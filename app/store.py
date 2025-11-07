import os
import re
import pandas as pd
from typing import List, Dict, Optional
from .config import settings
import chromadb
from chromadb.utils import embedding_functions


try:
    from langchain.embeddings import OpenAIEmbeddings
    from langchain.vectorstores import FAISS
    from langchain.schema import Document
except Exception:
    FAISS = None
    OpenAIEmbeddings = None
    Document = None


class PropertyStore:
    def __init__(self, csv_path: Optional[str] = None, mysql_url: Optional[str] = None):
        self.csv_path = csv_path or settings.PROPERTIES_CSV
        self.mysql_url = mysql_url or settings.MYSQL_URL
        self.use_mysql = os.getenv("USE_MYSQL", "false").lower() == "true"
        self.vector_enabled = os.getenv("USE_VECTOR", "true").lower() == "true"
        self.df = pd.DataFrame()
        self.vector_store = None
        self._load()


    def _load(self):
        print('CSV path '+ self.csv_path);
        print(os.path.exists(self.csv_path))
        #if self.csv_path and os.path.exists(self.csv_path):
        
        if self.csv_path:
            base_dir = os.path.dirname(__file__)   # current file’s directory
            csv_path = os.path.join(base_dir, "data", "properties.csv")
            self.df = pd.read_csv(csv_path)
        elif self.mysql_url:
            from sqlalchemy import create_engine
            engine = create_engine(self.mysql_url)
            self.df = pd.read_sql_table('properties', engine)
        else:
            self.df = pd.DataFrame(columns=['id','title','description','price','location','bedrooms','type','bathrooms','area','contact_email','contact_phone'])
        
        # Initialize Chroma Vector DB
        if self.vector_enabled:
            self._init_vector_db()
            
    def semantic_index(self, embedder=None):
        if FAISS is None or OpenAIEmbeddings is None:
            print('FAISS/langchain not installed; skipping semantic index')
        return
        texts = (self.df['title'].fillna('') + '\n' + self.df['description'].fillna('')).tolist()
        docs = [Document(page_content=t, metadata=self.df.iloc[i].to_dict()) for i, t in enumerate(texts)]
        embeddings = embedder or OpenAIEmbeddings()
        self.vector_store = FAISS.from_documents(docs, embeddings)

    def _init_vector_db(self):
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(
            name="real_estate_props",
            embedding_function=embedding_functions.DefaultEmbeddingFunction()
        )
        # Load data into vector DB
        #id,title,location,type,bhk,price,area_sqft,contact_person,phone,availability,images,youtube,description,whatsapp
        for idx, row in self.df.iterrows():
            doc_text = f"{row['title']} {row['location']}  {row['type']} {row['bhk']} {row['price']} {row['area_sqft']} {row['contact_person']} {row['phone']} {row['availability']}  {row['image']} {row['youtube']} {row['description']} {row['whatsapp']}"
            self.collection.add(
                ids=[str(row['id'])],
                documents=[doc_text],
                metadatas=[row.to_dict()]
            )
        print(f"[VectorDB] Loaded {len(self.df)} embeddings into Chroma")

    def semantic_search(self, query: str, top_k: int = 5):
        """Semantic vector search for user queries."""
        if not self.vector_enabled:
            return []
        results = self.collection.query(query_texts=[query], n_results=top_k)
        matches = []
        for meta in results["metadatas"][0]:
            matches.append(meta)
        print(f"[VectorDB] Found {len(matches)} semantic matches")
        return matches
    
    def search_filters(self, q: dict):
        df = self.df
        if 'location' in q and q['location']:
            df = df[df['location'].str.contains(q['location'], case=False, na=False)]
        if 'min_price' in q and q['min_price']:
            df = df[df['price'] >= q['min_price']]
        if 'max_price' in q and q['max_price']:
            df = df[df['price'] <= q['max_price']]
        if 'bedrooms' in q and q['bedrooms']:
            df = df[df['bedrooms'] >= q['bedrooms']]
        return df
    
    def _price_to_number(self, price_str: str) -> float:
        if not isinstance(price_str, str):
            return 0.0

        text = price_str.lower().replace(" ", "")
        if "cr" in text or "crore" in text:
            return float(text.lower().replace("crore", "").replace("cr", "").strip())* 100
        elif "lakh" in text:
            return float(text.lower().replace("lakh", "").replace("L", "").strip())
        try:
            return float(text)
        except:
            return 0.0
    
    def _filter_df(self, df, location=None, bhk=None, max_price=None, prop_type=None):
        result = df.copy()
        result_flag=False
        # Normalize column names
        result.columns = [c.strip().lower() for c in result.columns]
        print(result);
        print('Location Filter Result :')
        if location:
            result = result[result["location"].str.contains(fr"{location}", case=False, na=False, regex=True)]
            result_flag=True
            print(result)
        if bhk:
            try:
                result = result[result["bhk"] == int(bhk)]
                result_flag=True
                print('BHK Filter Result :');
                print(result)
            except:
                pass
        if prop_type:
            result = result[result["type"].str.contains(prop_type, case=False, na=False)]
            result_flag=True
            print('Type Filter Result :');
            print(result)
        if max_price:
            result["price_num"] = result["price"].apply(self._price_to_number)
            result = result[result["price_num"] <= float(max_price)]
            print('max price Filter Result :');
            result_flag=True
            print(max_price)
            print(result)
        
        if not result_flag:
            result = result.iloc[0:0]
    
        return result
    
    def search_properties(
        self,
        location: Optional[str] = None,
        bhk: Optional[int] = None,
        max_price: Optional[float] = None,
        prop_type: Optional[str] = None,
    ) -> List[Dict]:
        """Structured search with filters"""
        if self.use_mysql:
            cursor = self.conn.cursor(dictionary=True)
            query = "SELECT * FROM properties WHERE 1=1"
            params = []

            if location:
                query += " AND location LIKE %s"
                params.append(f"%{location}%")
            if bhk:
                query += " AND bhk = %s"
                params.append(bhk)
            if prop_type:
                query += " AND type LIKE %s"
                params.append(f"%{prop_type}%")
            if max_price:
                query += " AND price_value <= %s"
                params.append(max_price)

            cursor.execute(query, tuple(params))
            result = cursor.fetchall()
            cursor.close()
            print(f"[Store] Found {len(result)} properties from MySQL")
            return result

        else:
            result_df = self._filter_df(self.df, location, bhk, max_price, prop_type)
            if result_df is not None and not result_df.empty:
                print(f"[Store] Found {len(result_df)} properties from CSV")
            else:
                print(f"[Store] Found 0 properties from CSV")
            return result_df.to_dict(orient="records")
    
    
    def search(self, query: str) -> List[Dict]:
        """
        Free-text search — interprets user query like:
        '2BHK in Noida under 90 lakh' or 'villa in Gurugram below 2 crore'
        """
        query = query.lower()
        print('Query '+query)

        # Extract filters using regex
        bhk_match = re.search(r"(\d+)\s?bhk", query)
        bhk = int(bhk_match.group(1)) if bhk_match else None

        price_match = re.search(r"(\d+(\.\d+)?)\s?(lakh|crore|cr)", query)
        max_price = None
        if price_match:
            value, unit = price_match.group(1), price_match.group(3)
            max_price = float(value) * (100 if "cr" in unit or "crore" in unit else 1)

        # Try to extract location and type keywords
        possible_locations = [
            "noida", "gurgaon", "gurugram", "delhi", "mumbai", "pune", "bangalore", "greater noida"
        ]
        location = next((loc for loc in possible_locations if loc in query), None)

        prop_type = None
        if "villa" in query:
            prop_type = "villa"
        elif "flat" in query or "apartment" in query:
            prop_type = "apartment"
        elif "plot" in query:
            prop_type = "plot"

        print(f"[Store] Parsed query → location={location}, bhk={bhk}, price={max_price}, type={prop_type}")

        return self.search_properties(location, bhk, max_price, prop_type)
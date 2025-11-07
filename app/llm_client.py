import os
import json
import requests
import re
from .config import settings
from typing import List, Dict, Optional, Any


class GroqLllmClient:
    """Simple REST client for Groq Llama-3.3-like endpoints. Adapt to your server API."""

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        self.base_url = base_url or settings.LLM_API_URL
        self.api_key = api_key or settings.LLM_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
    def generate(self, prompt: str, max_tokens: int = 200, temperature: float = 0.7) -> dict:
        payload = {"prompt": prompt, "max_tokens": max_tokens, "temperature": temperature}
        data = {"model": "llama-3.3-70b-versatile","messages": [
            {"role": "system", "content": "You are a helpful real estate assistant."},
            {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        r = requests.post(self.base_url, json=data, headers=self.headers, timeout=30)
        r.raise_for_status()
        data = r.json()

        # expect data contains 'text' or similar — adapt based on your server
        #text = data.get("text") or data.get("output") or data.get("response")
        #if not text:
            # fallback to raw
            #return str(data)

        return data
    
    def generate_str(self, prompt: str, max_tokens: int = 200, temperature: float = 0.7) -> str:
        payload = {"prompt": prompt, "max_tokens": max_tokens, "temperature": temperature}
        data = {"model": "llama-3.3-70b-versatile","messages": [
            {"role": "system", "content": "You are a helpful real estate assistant."},
            {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        r = requests.post(self.base_url, json=data, headers=self.headers, timeout=30)
        r.raise_for_status()
        data = r.json()

        # expect data contains 'text' or similar — adapt based on your server
        text = data.get("text") or data.get("output") or data.get("response")
        if not text:
            # fallback to raw
            return str(data)

        return text

    # ---------------------------
    # 1️⃣ Core request handler
    # ---------------------------
    
    def _post(self, prompt: str) -> str:
        try:
            data = self.generate(prompt,200,0.7)
            print(data)
            # For OpenAI-like schema
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0].get("text", "").strip()
            # For Ollama / Groq with "response" field
            elif "response" in data:
                return data["response"].strip()
            else:
                return str(data)
        except Exception as e:
            print(f"[LLMClient] Error calling LLM API: {e}")
            return ""
    
    def extract_property_details(self, text: str) -> Dict[str, Any]:
        """
        Ask the LLM to extract property details from free text and return JSON-like dict.
        Attempts to parse JSON from the model; if parsing fails, falls back to regex.
        Returns keys: title, location, price, area, amenities (amenities as comma-separated string or list).
        """
        # few-shot prompt to improve structured JSON output
        prompt = f"""
You are an extraction assistant. Extract property listing fields from the user's text and return ONLY valid JSON.
Fields to extract (if present):
- title (e.g., "3BHK Apartment", "2BHK Flat")
- location (city/area)
- price (string, include units like 'Lakh' or 'Crore' if present)
- area (string, include units like 'sqft' if present)
- amenities (comma-separated string or list, e.g., "Lift, Parking")

Example 1:
Text: "I want to list my 2BHK flat in Sector 76 Noida, 950 sqft, price around 75 lakh, has parking and lift."
Output JSON:
{{
  "title": "2BHK Flat",
  "location": "Sector 76 Noida",
  "price": "75 lakh",
  "area": "950 sqft",
  "amenities": "Parking, Lift"
}}

Example 2:
Text: "Selling a 4BHK villa in Gurugram near Golf Course Road. Asking 2.1 Crore, 2200 sq ft, garden and pool."
Output JSON:
{{
  "title": "4BHK Villa",
  "location": "Gurugram, Golf Course Road",
  "price": "2.1 Crore",
  "area": "2200 sqft",
  "amenities": "Garden, Pool"
}}

Now extract from this text:
\"\"\"{text}\"\"\"

Return JSON only.
"""
        raw = self._post(prompt)

        # Try to parse model output as JSON
        try:
            # Some models may return additional text — try to extract the JSON substring first.
            # Find first '{' and last '}' to isolate JSON block
            start = raw.find('{')
            end = raw.rfind('}')
            if start != -1 and end != -1 and end > start:
                json_text = raw[start:end+1]
            else:
                json_text = raw

            parsed = json.loads(json_text)
            # Normalize keys/values: trim strings, convert lists to comma-separated strings
            normalized = {}
            for k, v in parsed.items():
                if isinstance(v, list):
                    normalized[k] = ", ".join([str(x).strip() for x in v if x])
                else:
                    normalized[k] = str(v).strip() if v is not None else v
            return normalized
        except Exception:
            # Fallback: simple regex-based extraction if LLM JSON parsing fails
            fallback = {}

            # title: try BHK pattern
            bhk_match = re.search(r'(\d+\s*bhk)', text, re.IGNORECASE)
            if bhk_match:
                fallback['title'] = bhk_match.group(1).upper().replace(" ", "")

            # location: look for "in <location>" or common city names (fallback)
            loc_match = re.search(r'in\s+([A-Za-z0-9\s\-\,]+?)(?:,|for|priced|price|asking|$)', text, re.IGNORECASE)
            if loc_match:
                fallback['location'] = loc_match.group(1).strip()

            # price
            price_match = re.search(r'(\d+(\.\d+)?\s*(lakh|crore|cr|rs|₹))', text, re.IGNORECASE)
            if price_match:
                fallback['price'] = price_match.group(1).strip()

            # area
            area_match = re.search(r'(\d{3,5}\s*(sqft|sq\.?ft|square\s*feet))', text, re.IGNORECASE)
            if area_match:
                fallback['area'] = area_match.group(1).strip()

            # amenities: common keywords
            amenities = []
            for amen in ['lift', 'parking', 'garden', 'pool', 'gym', 'security', 'balcony']:
                if re.search(r'\b' + re.escape(amen) + r'\b', text, re.IGNORECASE):
                    amenities.append(amen.capitalize())
            if amenities:
                fallback['amenities'] = ", ".join(sorted(set(amenities)))

            return fallback
    
    def summarize(self, properties: List[Dict]) -> str:
        """
        Summarizes a list of property dicts into a human-readable text using LLM.
        If LLM is unavailable, returns a manual summary.
        """
        if not properties:
            return "No matching properties found."

        # Convert property list into a readable summary prompt
        property_text = "\n".join([
            f"- {p.get('title', 'Property')} in {p.get('location', '')}, "
            f"{p.get('bhk', '')} BHK, Price: {p.get('price', '')}, Type: {p.get('type', '')}"
            for p in properties
        ])

        prompt = (
            "You are a real estate assistant. "
            "Summarize the following property listings for a client in a friendly, concise way.\n\n"
            f"Property List:\n{property_text}\n\n"
            "Provide a short summary highlighting the best options and their key features."
        )

        # Try to use remote LLM if available
        try:
            summary = self.generate_str(prompt)
            if summary and not summary.startswith("Sorry"):
                return summary
        except Exception as e:
            print(f"[LLM] Summarization fallback: {e}")

        # Fallback: simple text-based summary
        summary_lines = [
            f"🏠 {p.get('title', 'Property')} ({p.get('bhk', '?')} BHK, {p.get('type', 'N/A')}) "
            f"in {p.get('location', 'Unknown')} at {p.get('price', 'N/A')}"
            for p in properties
        ]
        return "Here are the top properties I found:\n" + "\n".join(summary_lines)

# convenience
client = GroqLllmClient()
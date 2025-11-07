"""
nlu_extractor.py — Hybrid NER + Regex + LLM Extraction
------------------------------------------------------
Extracts property details from natural language input.
"""

import re
import spacy
from typing import Dict, Any
from app.llm_client import GroqLllmClient


class HybridExtractor:
    def __init__(self):
        # Load SpaCy model (run once)
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # if not downloaded, auto download
            from spacy.cli import download
            download("en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")

        self.llm = GroqLllmClient()

    def extract(self, text: str) -> Dict[str, Any]:
        """
        Extract property details using NER + Regex + LLM hybrid.
        """
        doc = self.nlp(text)
        extracted = {}

        # --- Named Entity Recognition (NER)
        for ent in doc.ents:
            if ent.label_ in ["GPE", "LOC"]:
                extracted.setdefault("location", ent.text)
            elif ent.label_ in ["MONEY"]:
                extracted.setdefault("price", ent.text)
            elif ent.label_ in ["QUANTITY"]:
                extracted.setdefault("area", ent.text)

        # --- Regex-based fallback
        price_match = re.search(r"(\d+\.?\d*\s*(lakh|crore|rs|₹))", text, re.IGNORECASE)
        if price_match and "price" not in extracted:
            extracted["price"] = price_match.group(1)

        area_match = re.search(r"(\d{3,5}\s*(sqft|square feet|sq\.ft|sq ft))", text, re.IGNORECASE)
        if area_match and "area" not in extracted:
            extracted["area"] = area_match.group(1)

        bhk_match = re.search(r"(\d+\s*bhk)", text, re.IGNORECASE)
        if bhk_match:
            extracted["title"] = bhk_match.group(1).upper()

        amenities_match = re.findall(r"(parking|lift|gym|pool|garden|security)", text, re.IGNORECASE)
        if amenities_match:
            extracted["amenities"] = list(set([a.lower() for a in amenities_match]))

        # --- LLM-based structured extraction
        try:
            llm_result = self.llm.extract_property_details(text)
            for k, v in llm_result.items():
                if v and k not in extracted:
                    extracted[k] = v
        except Exception as e:
            print(f"[HybridExtractor] LLM extraction skipped due to: {e}")

        return extracted

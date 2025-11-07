# app/nlu.py
import re
from autocorrect import Speller
from typing import Dict

class NLUProcessor:
    """
    Performs basic Natural Language Understanding:
      - Spell correction & normalization
      - Intent classification
      - Entity extraction using regex
    """

    def __init__(self):
        self.spell = Speller(lang='en')

        # Simple keyword-based intent map
        self.intent_keywords = {
            "search_property": ["find", "show", "search", "available", "property", "flat", "plot", "villa","apartment"],
            "schedule_visit": ["visit", "book", "schedule", "see", "site", "appointment"],
            "contact_agent": ["contact", "call", "whatsapp", "email", "connect"],
            "price_query": ["price", "cost", "budget", "rate", "demand"],
        }

    def normalize(self, text: str) -> str:
        """Lowercase, remove extra spaces, correct spelling."""
        print('Input query '+text);
        text = text.lower().strip()
        text = re.sub(r"[^a-z0-9\s]", "", text)
        print('Query post normalize '+text)
        #corrected = " ".join([self.spell(word) for word in text.split()])
        #print('Normalized query '+corrected);
        #return corrected
        return text

    def classify_intent(self, text: str) -> str:
        """Classify intent based on keywords."""
        for intent, keywords in self.intent_keywords.items():
            if any(word in text for word in keywords):
                return intent
        #return "general_query"
        return "search_property"

    def extract_entities(self, text: str) -> Dict[str, str]:
        """Extract common real estate entities using regex patterns."""
        entities = {}
        # Example patterns
        price_match = re.search(r"(\d+(?:\.\d+)?\s*(?:lakh|cr|crore))", text)
        location_match = re.search(r"in\s+([a-z\s]+)", text)

        if price_match:
            entities["price"] = price_match.group(1)
        if location_match:
            entities["location"] = location_match.group(1).strip()
        return entities

    def process(self, text: str) -> Dict[str, any]:
        """End-to-end processing: normalize → classify → extract entities."""
        normalized = self.normalize(text)
        intent = self.classify_intent(normalized)
        entities = self.extract_entities(normalized)

        return {
            "original": text,
            "normalized": normalized,
            "intent": intent,
            "entities": entities
        }


# Example usage test
if __name__ == "__main__":
    nlu = NLUProcessor()
    query = "Can you show me flats in Noida under 1 cr?"
    print(nlu.process(query))

from app.store import PropertyStore
from app.llm_client import GroqLllmClient
from app.nlu import NLUProcessor
from app.notifier import Notifier
from app.scheduler import VisitScheduler
from app.stt import SpeechToText


class RealEstateAgent:
    def __init__(self):
        self.store = PropertyStore()
        self.llm = GroqLllmClient()
        self.nlu = NLUProcessor()
        self.notifier = Notifier()
        self.scheduler = VisitScheduler()
        self.stt = SpeechToText()

    async def handle_query(self, query: str):
        """Main pipeline for handling client text queries."""
        normalized_query = self.nlu.normalize(query)
        intent = self.nlu.classify_intent(normalized_query) 
        print('final intent '+intent)

        if intent == "search_property":
            properties = self.store.search(normalized_query)
            if not properties:
               properties = self.store.semantic_search(normalized_query)
            summarize = self.llm.summarize(properties)
            return {"properties":properties,"summarize":summarize}

        elif intent == "schedule_visit":
            result = self.scheduler.schedule_visit(normalized_query)
            return f"Visit scheduled: {result}"

        elif intent == "notify_advertiser":
            self.notifier.notify_advertiser(normalized_query)
            return "Advertiser notified successfully."

        else:
            return #self.llm.generate(normalized_query)

    def stt_to_text(self, audio_file: bytes) -> str:
        """Convert voice input to text using STT."""
        return self.stt.convert(audio_file)

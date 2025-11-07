"""
upload_agent.py — Real Estate Upload Agent
------------------------------------------
Handles property upload workflow:
 - Extract property fields from paragraph or voice input
 - Merge partial data across turns
 - Ask for missing details
 - Start upload & show progress
 - Reset session when user says "start over"
"""

import asyncio
from typing import Dict, Any
from app.nlu_extractor import HybridExtractor
from app.memory_manager import PropertyMemory
from app.store import PropertyStore
from app.llm_client import GroqLllmClient


class UploadAgent:
    def __init__(self):
        self.extractor = HybridExtractor()
        self.memory = PropertyMemory()
        self.store = PropertyStore()
        self.llm = GroqLllmClient()

        # Minimal required fields
        self.required_fields = ["title", "location", "price", "area", "amenities", "images"]

    # ------------------------------------------------------
    # INTENT HANDLERS
    # ------------------------------------------------------
    def detect_reset_intent(self, text: str) -> bool:
        """Detect if user wants to reset session"""
        reset_phrases = [
            "start over", "reset", "clear all", "forget it", "restart",
            "begin again", "new property", "delete previous", "discard"
        ]
        return any(p in text.lower() for p in reset_phrases)

    # ------------------------------------------------------
    # MAIN PROCESSOR
    # ------------------------------------------------------
    async def process_input(self, text: str, session_id: str) -> Dict[str, Any]:
        """
        Handle text or transcribed paragraph describing a property.
        Supports multi-turn completion via memory.
        """

        # 🔁 Check for reset intent
        if self.detect_reset_intent(text):
            self.memory.clear(session_id)
            return {
                "status": "reset",
                "message": "Previous property details cleared. Please start describing your property again."
            }

        # 🧩 Extract structured data
        extracted = self.extractor.extract(text)

        # 🧠 Merge with prior memory
        current_data = self.memory.get(session_id)
        merged = {**current_data, **extracted}
        self.memory.update(session_id, merged)

        # ✅ Check for completeness
        missing = self.check_missing_fields(merged)
        if missing:
            prompt = (
                f"I've captured the following details: {merged}. "
                f"Please provide the missing details: {', '.join(missing)}."
            )
            return {"status": "incomplete", "missing_fields": missing, "message": prompt}

        # ⚙️ All details present — start upload
        task = asyncio.create_task(self.upload_property(merged, session_id))
        return {
            "status": "uploading",
            "message": "All property details received. Upload process started.",
            "task_id": id(task)
        }

    # ------------------------------------------------------
    # FIELD VALIDATION
    # ------------------------------------------------------
    def check_missing_fields(self, details: Dict[str, Any]):
        """Find which required fields are missing or empty"""
        missing = []
        for field in self.required_fields:
            if field not in details or not details[field]:
                missing.append(field)
        return missing

    # ------------------------------------------------------
    # UPLOAD SIMULATION
    # ------------------------------------------------------
    async def upload_property(self, details: Dict[str, Any], session_id: str):
        """
        Simulate upload & progress tracking.
        Replace this logic with actual DB or API upload.
        """
        for progress in range(0, 101, 25):
            await asyncio.sleep(1)
            print(f"[Upload Progress] {progress}% - {details.get('title', 'Unknown Property')}")
        # Save property after completion
        self.store.save(details)
        # Clear memory post-success
        self.memory.clear(session_id)
        print("[Upload Completed] Property saved to database.")
        return {"status": "completed", "message": "Property uploaded successfully."}


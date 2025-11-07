"""
memory_manager.py — Property Memory using Redis
------------------------------------------------
Stores and retrieves property details across chat turns.
"""

import redis
import json
from typing import Dict, Any


class PropertyMemory:
    def __init__(self, host="localhost", port=6379, db=0):
        try:
            self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)
            self.redis.ping()
        except Exception as e:
            print(f"[Warning] Redis connection failed: {e}")
            self.redis = None

    def get(self, session_id: str) -> Dict[str, Any]:
        """Fetch saved property details for user session"""
        if not self.redis:
            return {}
        data = self.redis.get(session_id)
        return json.loads(data) if data else {}

    def update(self, session_id: str, new_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge new details into existing memory"""
        if not self.redis:
            return new_data
        current = self.get(session_id)
        current.update(new_data)
        self.redis.set(session_id, json.dumps(current))
        return current

    def clear(self, session_id: str):
        """Reset memory for given session"""
        if not self.redis:
            return
        self.redis.delete(session_id)
        print(f"[Memory] Cleared session: {session_id}")

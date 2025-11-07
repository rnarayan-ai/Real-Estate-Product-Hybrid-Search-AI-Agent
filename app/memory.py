import redis
import json
from .config import settings
import datetime


class MemoryStore:
def __init__(self, url: str = None):
url = url or settings.REDIS_URL
self.client = redis.from_url(url)


def add_interaction(self, user_id: str, message: str):
key = f'user:{user_id}:history'
item = json.dumps({'ts': datetime.datetime.utcnow().isoformat(), 'msg': message})
self.client.rpush(key, item)


def get_history(self, user_id: str, limit: int = 10):
key = f'user:{user_id}:history'
items = self.client.lrange(key, -limit, -1)
return [json.loads(x) for x in items]


memory = MemoryStore()
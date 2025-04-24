import redis
from config import REDIS_HOST, REDIS_PORT, REDIS_DB, MESSAGE_RETENTION

class Database:
    def __init__(self):
        self.redis = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True
        )

    def store_message(self, chat_id: int, message_id: int, user_id: int):
        """Store a message with TTL"""
        key = f"message:{user_id}:{chat_id}:{message_id}"
        self.redis.set(key, "1", ex=MESSAGE_RETENTION)

    def get_user_messages(self, user_id: int):
        """Get all messages for a user"""
        pattern = f"message:{user_id}:*"
        keys = self.redis.keys(pattern)
        messages = []
        
        for key in keys:
            # Extract chat_id and message_id from the key
            parts = key.split(':')
            if len(parts) == 4:
                chat_id = int(parts[2])
                message_id = int(parts[3])
                messages.append((chat_id, message_id))
        
        return messages

    def delete_user_messages(self, user_id: int):
        """Delete all messages for a user"""
        pattern = f"message:{user_id}:*"
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys) 
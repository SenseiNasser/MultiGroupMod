# database.py

import redis
import logging
from config import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_DB,
    REDIS_USER,     # Add username import
    REDIS_PASSWORD,
    REDIS_SSL,
    MESSAGE_RETENTION
)

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.redis = None
        # Validate Redis configuration
        if not all([REDIS_HOST, REDIS_PORT is not None, REDIS_USER, REDIS_PASSWORD]):
            logger.critical("FATAL: Missing essential Redis configuration (HOST, PORT, USER, PASSWORD)")
            return

        try:
            logger.info(f"Connecting to Redis: {REDIS_HOST}:{REDIS_PORT}, DB: {REDIS_DB}, SSL: {REDIS_SSL}")
            self.redis = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                username=REDIS_USER,     # Add username parameter
                password=REDIS_PASSWORD,
                ssl=REDIS_SSL,
                decode_responses=True,
                socket_timeout=15,
                socket_connect_timeout=15
            )
            # Test connection
            self.redis.ping()
            logger.info("Successfully connected to Redis")

        except redis.exceptions.AuthenticationError as e:
            logger.critical(f"Redis authentication failed. Error: {e}", exc_info=True)
            self.redis = None
        except redis.exceptions.ConnectionError as e:
            logger.critical(f"Redis connection failed. Error: {e}", exc_info=True)
            self.redis = None
        except redis.exceptions.TimeoutError as e:
            logger.critical(f"Redis connection timeout. Error: {e}", exc_info=True)
            self.redis = None
        except Exception as e:
            logger.critical(f"Unexpected Redis error: {e}", exc_info=True)
            self.redis = None


    def _check_connection(self):
        """Helper to check if Redis connection is valid before operations."""
        if self.redis is None:
            logger.error("Redis connection is not available (failed during initialization or missing config).")
            return False
        # Optional: Add a ping check here for resilience, but it adds latency
        # try:
        #     self.redis.ping()
        #     return True
        # except redis.exceptions.ConnectionError:
        #     logger.error("Redis connection lost.")
        #     # Maybe attempt reconnect here? Complex.
        #     return False
        return True # Assume connection is okay if it was initialized

    # --- Keep store_message, get_user_messages, delete_user_messages as before ---
    # --- but ensure they use self._check_connection() first ---

    def store_message(self, chat_id: int, message_id: int, user_id: int):
        """Store a message ID with TTL."""
        if not self._check_connection():
            logger.error("Database connection failed while storing message")
            return  # Add proper error handling

        try:
            key = f"message:{user_id}:{chat_id}:{message_id}"
            self.redis.set(key, "1", ex=MESSAGE_RETENTION)
            logger.debug(f"Stored Redis key: {key} with TTL {MESSAGE_RETENTION}s")
        except Exception as e:
            logger.error(f"Failed to store message key for user {user_id} in Redis: {e}", exc_info=True)

    def get_user_messages(self, user_id: int):
        """Get messages using scan_iter instead of keys"""
        if not self._check_connection():
            return []
    
        messages = []
        try:
            pattern = f"message:{user_id}:*"
            cursor = '0'
            while True:
                cursor, keys = self.redis.scan(cursor=cursor, match=pattern, count=100)
                for key in keys:
                    parts = key.split(':')
                    if len(parts) == 4:
                        try:
                            chat_id = int(parts[2])
                            message_id = int(parts[3])
                            messages.append((chat_id, message_id))
                        except (ValueError, IndexError):
                            logger.warning(f"Could not parse message key: {key}")
                    if cursor == 0:
                        break
            logger.debug(f"Found {len(messages)} messages via SCAN")
        except Exception as e:
            logger.error(f"Error scanning keys: {e}")
        return messages

    def delete_user_messages(self, user_id: int):
        """Delete all stored message keys for a user"""
        if not self._check_connection():
            return 0

        deleted_count = 0
        try:
            pattern = f"message:{user_id}:*"
            keys = self.redis.keys(pattern) # WARNING: KEYS can be slow
            if keys:
                deleted_count = self.redis.delete(*keys)
                logger.info(f"Deleted {deleted_count} Redis keys for user {user_id}.")
            else:
                logger.info(f"No Redis keys found to delete for user {user_id}.")
        except Exception as e:
             logger.error(f"Failed to delete user messages for user {user_id} from Redis: {e}", exc_info=True)
        return deleted_count
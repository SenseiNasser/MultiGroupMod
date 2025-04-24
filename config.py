import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
WEBHOOK_PORT = int(os.getenv('WEBHOOK_PORT', '8443'))

# Redis configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
REDIS_DB = int(os.getenv('REDIS_DB', '0'))

# Message retention period in seconds (7 days)
MESSAGE_RETENTION = 7 * 24 * 60 * 60

# Admin user IDs (comma-separated in .env)
ADMIN_IDS = set(map(int, os.getenv('ADMIN_IDS', '').split(','))) if os.getenv('ADMIN_IDS') else set()

# Group IDs (comma-separated in .env)
GROUP_IDS = set(map(int, os.getenv('GROUP_IDS', '').split(','))) if os.getenv('GROUP_IDS') else set() 
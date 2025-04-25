import asyncio
import logging
from flask import Flask, request, abort
from telegram import Update
import os


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s] %(message)s',
)
logger = logging.getLogger(__name__)

try:
    from bot import application as telegram_app
    logger.info("Successfully imported Telegram application")
except ImportError as e:
    logger.critical(f"Failed to import bot application: {e}")
    raise

flask_app = Flask(__name__)

@flask_app.route('/webhook', methods=['POST'])
def webhook():
    if not telegram_app:
        abort(503, "Service Unavailable")
    
    try:
        update_json = request.get_json(force=True)
        update = Update.de_json(update_json, telegram_app.bot)
        
        # Process update in async context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(telegram_app.process_update(update))
        loop.close()
        
    except Exception as e:
        logger.error(f"Error processing update: {e}")
    
    return 'OK', 200

application = flask_app
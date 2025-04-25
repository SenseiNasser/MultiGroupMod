import asyncio
import logging
from flask import Flask, request, abort
from telegram import Update


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s] %(message)s',
)
logger = logging.getLogger(__name__)

try:
    from bot import application as telegram_app
    logger.info("Successfully imported Telegram application")

    # Initialize the application
    async def initialize_app():
        """Initialize the PTB Application."""
        logger.info("Running application.initialize()...")
        await telegram_app.initialize()
        logger.info("Application initialized successfully.")

    # Run the async initialization function synchronously
    try:
        logger.info("Starting asyncio initialization run...")
        asyncio.run(initialize_app())
        logger.info("Asyncio initialization run completed.")
    except Exception as init_err:
        logger.critical(f"FATAL: asyncio.run(initialize_app) failed: {init_err}", exc_info=True)
        raise RuntimeError(f"Failed to initialize Telegram application: {init_err}") from init_err

except Exception as e:
    logger.critical(f"FATAL: Failed to import or initialize bot application in wsgi.py: {e}", exc_info=True)
    raise

flask_app = Flask(__name__)

@flask_app.route('/webhook', methods=['POST'])
def webhook():
    if telegram_app is None or not getattr(telegram_app, '_initialized', False):
        logger.error("Webhook received, but telegram_app object is None or not initialized!")
        abort(503, "Service Unavailable: Bot not ready.")

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

@flask_app.route('/')
def index():
    if telegram_app and getattr(telegram_app, '_initialized', False):
        return "Telegram Bot Web Service is running and Initialized.", 200
    elif telegram_app:
        return "Telegram Bot Web Service is running but Initializing or Failed.", 503
    else:
        return "Telegram Bot Web Service failed to load.", 500
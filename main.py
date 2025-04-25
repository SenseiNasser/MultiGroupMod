import logging
import asyncio
from fastapi import FastAPI, Request, Response, HTTPException
from telegram import Update
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s] %(message)s',
)
logger = logging.getLogger(__name__)
logger.info("--- FastAPI App File Loading ---")

try:
    from bot import application as telegram_app
    from bot import logger as bot_logger
    if telegram_app is None:
        raise RuntimeError("Imported telegram_app is None")
    logger.info("Telegram application imported.")

    # Initialize the application
    async def initialize_app():
        logger.info("Running application.initialize()...")
        await telegram_app.initialize()
        logger.info("Application initialized successfully.")

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("Starting asyncio initialization run via lifespan...")
        try:
            await initialize_app()
            logger.info("Asyncio initialization run completed via lifespan.")
        except Exception as init_err:
            logger.critical(f"FATAL: Lifespan initialization failed: {init_err}", exc_info=True)
            raise RuntimeError(f"Failed lifespan init: {init_err}") from init_err
        yield
        logger.info("Application shutting down, running cleanup...")

    app = FastAPI(lifespan=lifespan)
    logger.info("FastAPI app created.")

except Exception as e:
    logger.critical(f"FATAL: Failed to import or initialize application: {e}", exc_info=True)
    raise

@app.post("/webhook")
async def webhook(request: Request):
    if telegram_app is None or not getattr(telegram_app, '_initialized', False):
        logger.error("Webhook received, but telegram_app object is None or not initialized!")
        raise HTTPException(status_code=503, detail="Service Unavailable: Bot not ready.")

    try:
        update_json = await request.json()
        if not update_json:
            bot_logger.warning("Received empty or non-JSON data on webhook.")
            return Response(status_code=400, content="Bad Request")

        update = Update.de_json(update_json, telegram_app.bot)
        bot_logger.debug(f"Webhook processing Update ID: {update.update_id}")

        await telegram_app.process_update(update)
        bot_logger.debug(f"Finished processing update ID: {update.update_id}")

    except Exception as e:
        update_id_str = f"Update ID {update.update_id}" if update else "Unknown Update"
        bot_logger.error(f"Error processing update in webhook ({update_id_str}): {e}", exc_info=True)
    return Response(status_code=200, content="OK")

@app.get("/")
async def index():
    if telegram_app and getattr(telegram_app, '_initialized', False):
        return {"status": "OK", "message": "Telegram Bot Web Service is running and Initialized."}
    elif telegram_app:
        raise HTTPException(status_code=503, detail="Initializing or Failed")
    else:
        raise HTTPException(status_code=500, detail="Failed to load application")
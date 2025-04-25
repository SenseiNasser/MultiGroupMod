# config.py
import os
import logging
from dotenv import load_dotenv

# --- Load .env ---
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path, verbose=True)

logger = logging.getLogger(__name__)

# --- Essential Configuration ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    logger.critical("BOT_TOKEN not found!")
    raise ValueError("Missing BOT_TOKEN environment variable")

# --- Webhook Configuration ---
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
WEBHOOK_PORT = int(os.environ.get("WEBHOOK_PORT", 8443))

# --- Bot Permissions ---
ADMIN_IDS_STR = os.environ.get("ADMIN_IDS", "")
try:
    ADMIN_IDS = set(int(admin_id.strip()) for admin_id in ADMIN_IDS_STR.split(',') if admin_id.strip())
    logger.info(f"Loaded {len(ADMIN_IDS)} Admin IDs.")
except ValueError as e:
    logger.error(f"Invalid ADMIN_IDS format: {ADMIN_IDS_STR}. Error: {e}", exc_info=True)
    ADMIN_IDS = set()

GROUP_IDS_STR = os.environ.get("GROUP_IDS", "")
try:
    GROUP_IDS = set(int(group_id.strip()) for group_id in GROUP_IDS_STR.split(',') if group_id.strip())
    logger.info(f"Loaded {len(GROUP_IDS)} Group IDs.")
except ValueError as e:
    logger.error(f"Invalid GROUP_IDS format: {GROUP_IDS_STR}. Error: {e}", exc_info=True)
    GROUP_IDS = set()

# --- Database (Redis) Configuration ---
REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT_STR = os.environ.get("REDIS_PORT", "6379")
REDIS_DB_STR = os.environ.get("REDIS_DB", "0")
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")
REDIS_USER = os.environ.get("REDIS_USER")
REDIS_SSL_STR = os.environ.get("REDIS_SSL", "False")

# Validate Port
try:
    REDIS_PORT = int(REDIS_PORT_STR)
except (ValueError, TypeError):
    logger.error(f"Invalid REDIS_PORT value '{REDIS_PORT_STR}'. Must be an integer.", exc_info=True)
    REDIS_PORT = None

# Validate DB
try:
    REDIS_DB = int(REDIS_DB_STR)
except (ValueError, TypeError):
    logger.error(f"Invalid REDIS_DB value '{REDIS_DB_STR}'. Must be an integer.", exc_info=True)
    REDIS_DB = 0

# Validate Host
if not REDIS_HOST:
    logger.warning("REDIS_HOST not found in environment. Database connection will likely fail.")

# Validate Auth requirements
if REDIS_HOST and not REDIS_USER:
    logger.warning(f"REDIS_USER is not set for host {REDIS_HOST}. Authentication might fail.")
if REDIS_HOST and not REDIS_PASSWORD:
    logger.warning(f"REDIS_PASSWORD is not set for host {REDIS_HOST}. Authentication might fail.")

# Convert SSL String to Boolean
REDIS_SSL = REDIS_SSL_STR.lower() in ['true', '1', 't', 'y', 'yes']

# --- Message Retention ---
DEFAULT_RETENTION = 7 * 24 * 60 * 60
try:
    MESSAGE_RETENTION = int(os.environ.get("MESSAGE_RETENTION", DEFAULT_RETENTION))
    if MESSAGE_RETENTION <= 0:
        logger.warning(f"MESSAGE_RETENTION must be positive, using default: {DEFAULT_RETENTION}s")
        MESSAGE_RETENTION = DEFAULT_RETENTION
    else:
        logger.info(f"Message retention set to: {MESSAGE_RETENTION} seconds")
except ValueError:
    logger.error(f"Invalid MESSAGE_RETENTION value, using default: {DEFAULT_RETENTION}s", exc_info=True)
    MESSAGE_RETENTION = DEFAULT_RETENTION

# --- Log loaded Redis config ---
redis_log_host = REDIS_HOST or "Not Set"
redis_log_port = REDIS_PORT if REDIS_PORT is not None else "Invalid"
redis_log_db = REDIS_DB
redis_log_user_status = "Set" if REDIS_USER else "Not Set"
redis_log_pass_status = "Set" if REDIS_PASSWORD else "Not Set"
redis_log_ssl = REDIS_SSL
logger.info(f"Redis Config: Host={redis_log_host}, Port={redis_log_port}, DB={redis_log_db}, User={redis_log_user_status}, Password={redis_log_pass_status}, SSL={redis_log_ssl}")

logger.info("Configuration loaded.")
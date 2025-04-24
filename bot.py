import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN, WEBHOOK_URL, WEBHOOK_PORT, ADMIN_IDS, GROUP_IDS
from database import Database

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize database
db = Database()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text('Hi! I am your group moderation bot.')

async def store_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Store every message in the database."""
    if update.message:
        chat_id = update.message.chat_id
        message_id = update.message.message_id
        user_id = update.message.from_user.id
        
        # Store message in database
        db.store_message(chat_id, message_id, user_id)

async def get_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get user ID by replying to their message."""
    if not update.message.reply_to_message:
        await update.message.reply_text("Please reply to a user's message to get their ID.")
        return
    
    target_user = update.message.reply_to_message.from_user
    response = (
        f"User Information:\n"
        f"Name: {target_user.full_name}\n"
        f"Username: @{target_user.username if target_user.username else 'N/A'}\n"
        f"ID: {target_user.id}\n"
        f"Language: {target_user.language_code if target_user.language_code else 'N/A'}"
    )
    await update.message.reply_text(response)

async def check_user_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check which groups a user has joined."""
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("Please reply to a user's message to check their group memberships.")
        return
    
    target_user = update.message.reply_to_message.from_user
    target_id = target_user.id
    
    # Get all messages for this user to determine which groups they're in
    messages = db.get_user_messages(target_id)
    user_groups = set(chat_id for chat_id, _ in messages)
    
    response = [f"User {target_user.full_name} (ID: {target_id}) is in the following groups:"]
    
    for group_id in user_groups:
        try:
            chat = await context.bot.get_chat(group_id)
            response.append(f"- {chat.title} (ID: {group_id})")
        except Exception as e:
            logger.error(f"Error getting chat info for {group_id}: {e}")
            response.append(f"- Unknown Group (ID: {group_id})")
    
    if not user_groups:
        response = [f"User {target_user.full_name} (ID: {target_id}) is not found in any groups."]
    
    await update.message.reply_text("\n".join(response))

async def ban_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ban a user from all groups and delete their messages."""
    if update.effective_user.id not in ADMIN_IDS:
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("Please reply to a user's message to ban them.")
        return
    
    target_user = update.message.reply_to_message.from_user
    target_id = target_user.id
    
    # Get all messages for this user
    messages = db.get_user_messages(target_id)
    
    # Delete all messages
    for chat_id, message_id in messages:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception as e:
            logger.error(f"Error deleting message: {e}")
    
    # Ban user from all groups
    for group_id in GROUP_IDS:
        try:
            await context.bot.ban_chat_member(
                chat_id=group_id,
                user_id=target_id,
                revoke_messages=True
            )
        except Exception as e:
            logger.error(f"Error banning user in group {group_id}: {e}")
    
    # Delete stored messages from database
    db.delete_user_messages(target_id)
    
    await update.message.reply_text(
        f"User {target_user.full_name} (ID: {target_id}) has been banned from all groups "
        "and their messages have been deleted."
    )

def main():
    """Start the bot."""
    # Create the Application and pass it your bot's token
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("banall", ban_all))
    application.add_handler(CommandHandler("user_id", get_user_id))
    application.add_handler(CommandHandler("user_is_join", check_user_groups))
    application.add_handler(MessageHandler(filters.ALL, store_message))

    # Set up webhook
    application.run_webhook(
        listen="0.0.0.0",
        port=WEBHOOK_PORT,
        url_path=BOT_TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}"
    )

if __name__ == '__main__':
    main() 
# Telegram Group Moderation Bot

A powerful moderation bot that can manage multiple Telegram groups simultaneously, with features for banning users and deleting their messages across all groups.

## Features

- Webhook-based architecture for reliability
- Redis database for message storage with 7-day TTL
- Admin-only commands
- Cross-group user banning
- Message deletion across all groups
- Automatic message tracking
- User information lookup
- Group membership tracking

## Prerequisites

- Python 3.8+
- Redis server
- SSL-enabled domain or ngrok for development
- Telegram Bot Token (from @BotFather)

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with the following variables:
   ```
   BOT_TOKEN=your_bot_token
   WEBHOOK_URL=https://your-domain.com
   WEBHOOK_PORT=8443
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_DB=0
   ADMIN_IDS=123456789,987654321  # Comma-separated list of admin Telegram IDs
   GROUP_IDS=-1001234567890,-1009876543210  # Comma-separated list of group IDs
   ```

4. Start Redis server:
   ```bash
   redis-server
   ```

5. Run the bot:
   ```bash
   python bot.py
   ```

## Usage

1. Add the bot to all groups you want to manage
2. Make the bot an administrator in each group with the following permissions:
   - Delete messages
   - Ban users
   - Read messages

3. Commands:
   - `/start` - Basic bot information
   - `/banall` - Reply to a user's message with this command to ban them from all groups and delete their messages
   - `/user_id` - Reply to a user's message to get their detailed information (ID, username, name, language)
   - `/user_is_join` - Reply to a user's message to check which groups they have joined (admin only)

## Security

- All commands are restricted to admin users only
- Message data is automatically deleted after 7 days
- Webhook-based architecture ensures no message loss

## Notes

- The bot must be an administrator in all groups to function properly
- Make sure your webhook URL is accessible and has a valid SSL certificate
- For development, you can use ngrok to create a temporary HTTPS URL
- The `/user_is_join` command will only show groups where the user has sent messages that are still within the 7-day retention period 
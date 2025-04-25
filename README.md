# Telegram Group Moderation Bot

A powerful moderation bot that can manage multiple Telegram groups simultaneously, with features for banning users and deleting their messages across all groups.

## Features

- Webhook-based architecture for reliability (when deployed)
- Redis database backend for message storage with configurable TTL
- Admin-only commands
- Cross-group user banning
- Message deletion across all groups
- Automatic message tracking
- User information lookup
- Group membership tracking

## Prerequisites

- Python 3.8+
- Git
- Telegram Bot Token (from @BotFather)
- [Redis Server](https://redis.io/docs/getting-started/installation/) (Required only for local development)
- [Render Account](https://dashboard.render.com/) (Required for production deployment)
- [ngrok](https://ngrok.com/download) (Optional, for local webhook testing)

## Local Development Setup

These steps allow you to run the bot on your local machine for testing.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/SenseiNasser/telegram-group-moderation-bot.git
    cd telegram-group-moderation-bot
    ```

2.  **Set up a virtual environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Start a local Redis server:**
    *   Follow the Redis installation guide linked in Prerequisites.
    *   Run the server (often just `redis-server` in your terminal).

5.  **Create and configure a `.env` file:**
    *   Copy the example below into a new file named `.env` in the project root.
    *   **Fill in your actual `BOT_TOKEN`**.
    *   For `WEBHOOK_URL`, if you want to test webhooks locally, start `ngrok http 8000` (or another port) and use the `https://` URL ngrok provides. Otherwise, you can leave it blank or use a placeholder for local testing without webhooks.

    ```ini
    # .env file for LOCAL DEVELOPMENT

    BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE
    # Optional: Use ngrok for local webhook testing (e.g., https://xxxxx.ngrok.io)
    WEBHOOK_URL=
    WEBHOOK_PORT=8000 # Port Flask/Gunicorn will run on locally

    # --- Local Redis ---
    REDIS_HOST=localhost
    REDIS_PORT=6379
    REDIS_DB=0
    REDIS_PASSWORD= # Leave blank if your local Redis has no password
    REDIS_SSL=False

    MESSAGE_RETENTION=604800 # 7 days in seconds

    # --- Bot Permissions (Comma-separated Telegram User IDs) ---
    ADMIN_IDS=123456789,987654321
    GROUP_IDS=-1001234567890,-1009876543210 # Groups the bot should operate in
    ```

6.  **Run the bot locally:**
    *   Use Flask's built-in server (good for development):
        ```bash
        # Make sure your WSGI file is named wsgi.py and contains application = flask_app
        flask --app wsgi run --port 8000
        ```
    *   Or use Gunicorn (mimics production):
        ```bash
        gunicorn wsgi:application -b 127.0.0.1:8000 --reload
        ```

7.  **(Optional) Set Local Webhook:** If using ngrok and you want to test webhooks, send the `/setWebhook` command to Telegram using your ngrok URL. You usually only need to do this once.
    ```bash
    curl -F "url=https://YOUR_NG
    *   Once "Available", go to its "Connect" tab and find the **External Connection URL** (`rediss://...`). Note the **Hostname** and **Password**. Add `0.0.0.0/0` to the **Access Control** list on the "Info" tab.

3.  **Create Render Web Service:**
    *   Go to the Render Dashboard -> New + -> **Web Service**.
    *   Connect your GitHub repository.
    *   **Name:** e.g., `telegram-bot-service`
    *   **Region:** **Select the SAME region** as your Redis KV store.
    *   **Branch:** `master` (or your main branch).
    *   **Runtime:** Python 3.
    *   **Build Command:** `pip install --upgrade pip && pip install -r requirements.txt`
    *   **Start Command:** `gunicorn wsgi:application`
    *   **Plan:** Free.

4.  **Configure Environment Variables on Render:**
    *   Go to the **Environment** section for your *Web Service*.
    *   Add the following variables (using values from your bot token and the Render Redis details):

        ```ini
        # Render Environment Variables (NO .env file needed here!)

        BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
        ADMIN_IDS=123456789,987654321 # Your Telegram User ID(s)
        GROUP_IDS=-1001234567890,-100987654321 # Target Group ID(s)

        # Use details from your RENDER Redis KV Store (EXTERNAL URL)
        REDIS_HOST=YOUR_RENDER_KV_HOSTNAME # e.g., frankfurt-keyvalue.render.com
        REDIS_PORT=6379 # Or the port shown by Render
        REDIS_PASSWORD=YOUR_RENDER_KV_PASSWORD
        REDIS_DB=0
        REDIS_SSL=True # MUST be True for external connection

        MESSAGE_RETENTION=604800

        # WEBHOOK_URL will be set AFTER first deploy
        ```

5.  **Deploy and Set Webhook URL:**
    *   Click **"Create Web Service"**. Monitor the "Logs" tab for deployment progress.
    *   Once the first deploy is successful, copy the URL Render assigns to your service (e.g., `https://telegram-bot-service.onrender.com`).
    *   Go back to the **Environment** variables for the Web Service.
    *   Add/Update the `WEBHOOK_URL` variable with the copied URL:
        ```ini
        WEBHOOK_URL=https://telegram-bot-service.onrender.com
        ```
    *   Save the environment variables. This will trigger a re-deploy.

6.  **Set Telegram Webhook:**
    *   Wait for the re-deploy to finish.
    *   Open your local terminal (or a Render Shell for the web service) and run this `curl` command, replacing placeholders:
        ```bash
        curl -F "url=https://YOUR_APP_NAME.onrender.com/webhook" \
             https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook
        ```
        *   Replace `YOUR_APP_NAME.onrender.com` with your actual Render service URL.
        *   Replace `<YOUR_BOT_TOKEN>` with your bot's token.
    *   You should see `{"ok":true,"result":true,"description":"Webhook was set"}`.

## Usage

1.  Add the bot to all Telegram groups you want it to manage.
2.  Make the bot an **administrator** in each group with permissions to:
    *   Delete messages
    *   Ban users
3.  Available commands:
    *   `/start` - Basic bot information.
    *   `/banall` (Admin only) - Reply to a user's message to ban them from all configured groups and delete their recent messages stored by the bot.
    *   `/user_id` (Admin only) - Reply to a user's message to get their detailed information.
    *   `/user_is_join` (Admin only) - Reply to a user's message to check which configured groups they have recently sent messages in.

## Security

- Admin commands require the user's Telegram ID to be in the `ADMIN_IDS` list.
- Message data in Redis is automatically deleted after `MESSAGE_RETENTION` seconds (default 7 days).
- Render provides automatic HTTPS for the webhook URL.
- Consider adding a `secret_token` to your webhook setup for enhanced security (requires code changes and setting it in the `curl` command).

## Notes

- The bot must be an administrator in all groups listed in `GROUP_IDS` to function correctly (ban, delete messages).
- Environment variables on Render are used for production secrets, not the `.env` file.
- The `/user_is_join` command only shows groups where the user has sent messages that are still within the message retention period in Redis.
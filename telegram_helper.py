from telegram import Bot
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Initialize the Telegram bot 
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID") 
bot = Bot(token=bot_token)

def send_task_to_telegram(title, description):
    """
    Sends a task to the configured Telegram chat.
    """
    message = f"📝 *New Task Added!*\n\n*Title:* {title}\n*Description:* {description}"

    print(">> Sending to Telegram")
    print("Bot token:", bot_token)
    print("Chat ID:", chat_id)
    print("Message:", message)

    bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")

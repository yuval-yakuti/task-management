from telegram import Bot
from dotenv import load_dotenv
import os

load_dotenv()
print("Loaded token:", os.getenv("TELEGRAM_BOT_TOKEN"))
print("Current directory:", os.getcwd())

bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=bot_token)

updates = bot.get_updates()

for update in updates:
    print(f"Chat ID: {update.message.chat.id}")
    print(f"Username: {update.message.chat.username}")
    print(f"Text: {update.message.text}")

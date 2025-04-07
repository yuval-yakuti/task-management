from telegram import Bot
import os
from dotenv import load_dotenv

load_dotenv()

bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=bot_token)
bot.send_message(chat_id=chat_id, text="🚀 Test message from Voltify bot!")

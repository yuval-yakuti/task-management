import asyncio
from telegram import Bot
from telegram.constants import ParseMode
import os
from dotenv import load_dotenv

load_dotenv()

bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=bot_token)

async def main():
    updates = await bot.get_updates()
    for update in updates:
        print(f"Chat ID: {update.message.chat.id}")
        print(f"Username: {update.message.chat.username}")
        print(f"Full Name: {update.message.chat.full_name}")
        print("-----------")

if __name__ == "__main__":
    asyncio.run(main())

import asyncio
from telegram import Bot

async def main():
    bot = Bot(token="8010873044:AAEs9_mZ53Jazft6-v3UoiH7O-cr4xoBQng")
    updates = await bot.get_updates()
    for update in updates:
        print(update.message.chat.id)

if __name__ == "__main__":
    asyncio.run(main())

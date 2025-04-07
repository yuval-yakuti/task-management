import asyncio
from telegram import Bot

async def main():
    bot = Bot(token="8010873044:AAGl75si13FCyiXalOzoToSAxCixFQ4zXe8")
    updates = await bot.get_updates()
    for update in updates:
        print(update.message.chat.id)

if __name__ == "__main__":
    asyncio.run(main())

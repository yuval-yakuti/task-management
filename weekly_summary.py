import os
from pymongo import MongoClient
from telegram import Bot
from dotenv import load_dotenv
from datetime import datetime
from openai import OpenAI
from apscheduler.schedulers.background import BackgroundScheduler  # ← זה כאן!

# Load environment variables
load_dotenv()

# Set up OpenAI
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Set up Telegram
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")
bot = Bot(token=bot_token)

# Set up MongoDB
mongo_client = MongoClient(os.getenv("MONGO_URI"))
db = mongo_client["voltify_db"]
tasks_collection = db['tasks']

def generate_weekly_summary():
    # Step 1: Fetch all incomplete tasks from the DB
    tasks = list(tasks_collection.find({
        'completed': False
    }))

    if not tasks:
        return "🎉 You have no open tasks this week! Great job!"

    # Step 2: Build a prompt from the open tasks
    prompt = "Create a weekly summary based on the following open tasks:\n"
    for task in tasks:
        prompt += f"- {task.get('title', '')}: {task.get('description', '')}\n"

    # Step 3: Ask OpenAI to summarize
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant who creates smart weekly summaries for open tasks."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    summary = response.choices[0].message.content.strip()
    return summary

def send_weekly_summary():
    summary = generate_weekly_summary()
    message = f"🧠 *Weekly Smart Summary:*\n\n{summary}"
    bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")

# Schedule the summary every 30 seconds (for testing)
scheduler = BackgroundScheduler()
scheduler.add_job(send_weekly_summary, 'cron', day_of_week='sun', hour=8, minute=0)
scheduler.start()
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_task_description(title):
    prompt = f"Suggest a short description for this task: {title}"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    return response.choices[0].message.content.strip()


def analyze_task_description(description):
    prompt = (
        "Analyze the following task description and suggest:\n"
        "1. A suitable category (Work, Study, Personal, Other)\n"
        "2. An estimated time in minutes to complete the task.\n\n"
        f"Task: {description}\n\n"
        "Respond in JSON format like this:\n"
        "{\n"
        '  "category": "Study",\n'
        '  "estimated_time": 45\n'
        "}"
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You're a helpful assistant that categorizes tasks."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5
    )

    try:
        raw_content = response.choices[0].message.content
        print("🧠 AI Raw Response:\n", raw_content)
        result = json.loads(raw_content)
        return result.get("category"), result.get("estimated_time")
    except Exception as e:
        print("❌ Failed to parse AI response:", e)
        return None, None

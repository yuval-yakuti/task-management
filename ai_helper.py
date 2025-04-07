import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_task_category(description):
    prompt = f"Suggest a suitable category for the following task description:\n'{description}'\nCategory (one or two words):"
    
    # Function that returns a smart category by description 
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    return response.choices[0].message.content.strip()

# Function to generate a short task description using the title
def generate_task_description(title):
    prompt = f"Suggest a short description for a task titled: '{title}'"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()
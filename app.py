from flask import Flask
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()  #loading file .env

app = Flask(__name__)

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client.get_default_database()

@app.route('/')
def home():
    return "Connected to MongoDB!"

if __name__ == '__main__':
    app.run(debug=True)

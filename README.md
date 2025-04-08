# Voltify – Task Management App

This project is a personal web application for task management, built using **Python Flask** and connected to **MongoDB Atlas**.

It was created as part of a technical assignment and serves as the foundation for a smart, extendable task manager that can integrate with AI tools and messaging platforms.

---

## 🧠 Features
✅ User registration & login with password hashing and input validation
✅ Add, edit, delete, and mark tasks as completed
✅ Priority tagging and category filtering
✅ Estimated time & smart categorization using OpenAI
✅ Weekly smart summary sent via Telegram Bot
✅ AI-powered task description enhancement
✅ Responsive interface styled after Instagram's login
✅ Secure .env and production-ready structure

---

## 🎁 Bonus Features Implemented
✅ AWS EC2 Deployment with working external URL
✅ Secure .env and environment config separation
✅ Telegram notifications on task creation & completion
✅ Scheduled weekly summary using APScheduler + OpenAI
✅ Password validation and form input constraints
✅ Rate limiting with Flask-Limiter to prevent brute-force login
✅ Clean, styled login form with mobile responsiveness

---

## 🛠️ Technologies Used
- Python 3.8, Flask, MongoDB Atlas
- Jinja, HTML/CSS, JavaScript
- OpenAI API, Telegram Bot API
- python-dotenv, Flask-Limiter, APScheduler
- AWS EC2 for live deployment
- MongoDB Atlas (Cloud database)

---

## 🚀 Getting Started

### 1. Clone the repository:
```bash
git clone https://github.com/yuval-yakuti/task-management.git
cd task-management
```
### 2. Create a virtual environment and activate it:
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```
### 3. Install dependencies:
```bash
pip install -r requirements.txt
```
### 4. Create a `.env` file:
```bash
cp .env.example .env
```
### 5. Run the app:
```bash
python app.py
```
Visit `http://127.0.0.1:5000/` in your browser to verify.

🔐 .env.example
```bash
MONGO_URI=your_mongodb_uri_here
OPENAI_API_KEY=your_openai_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
```
---

## 🧑‍💻 Developer
Created by Yuval Yakuti, as part of the application process for the Co-Op program.

---

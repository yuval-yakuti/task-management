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

##Deployment
# Voltify Deployment Guide (AWS EC2)

This guide outlines the complete process of deploying the Voltify Flask application to an AWS EC2 instance.
---

## 1. Launching an EC2 Instance
1. Log in to your [AWS Console](https://console.aws.amazon.com/).
2. Navigate to **EC2** > **Instances** > **Launch Instance**.
3. Configure the instance:
   - **Name**: Voltify
   - **AMI**: Ubuntu Server 22.04 LTS
   - **Instance Type**: t2.micro (Free Tier eligible)
   - **Key Pair**: Create or select an existing `.pem` key file
   - **Security Group**: Allow inbound traffic on ports 22 (SSH), 80 (HTTP), and 5000 (for Flask development)
---

## 2. Connect to the EC2 Instance
```bash
chmod 400 path/to/your-key.pem
ssh -i path/to/your-key.pem ec2-user@<EC2_PUBLIC_IP>
```
---

## 3. Install Required Packages
```bash
sudo apt update && sudo apt install python3-pip python3-venv git -y
```
---

## 4. Clone the Project Repository
```bash
git clone https://github.com/yuval-yakuti/task-management.git
cd task-management
```
---

## 5. Set Up Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```
---

## 6. Install Python Dependencies
```bash
pip install -r requirements.txt
```
---

## 7. Create the .env File (Sensitive Credentials)
Since environment variables are not uploaded to GitHub for security reasons, create a `.env` file manually:
```bash
touch .env
nano .env
```
Paste the following content and replace with actual credentials:
```
MONGO_URI=your_mongodb_connection_string
OPENAI_API_KEY=your_openai_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```
Press `CTRL+O`, `Enter`, then `CTRL+X` to save and exit.
---

## 8. Run the Application
```bash
sudo FLASK_APP=app.py flask run --host=0.0.0.0 --port=80
```
You can now access the application in your browser:
```
http://<EC2_PUBLIC_IP>
```
---

## 9. Notes
- The `app.py` file uses environment variables from the `.env` file via `python-dotenv`.
- The weekly summary scheduler is integrated and starts automatically.
- Logs are written to `app.log` for monitoring purposes.
---

> ✅ Deployment complete. Your application is now live on AWS!

## 🧑‍💻 Developer
Created by Yuval Yakuti, as part of the application process for the Co-Op program.

---

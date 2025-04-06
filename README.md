# Voltify – Task Management App

This project is a personal web application for task management, built using **Python Flask** and connected to **MongoDB Atlas**.

It was created as part of a technical assignment and serves as the foundation for a smart, extendable task manager that can integrate with AI tools and messaging platforms.

---

## 🧠 Features (So Far)
- Flask server with routing and debug mode
- Cloud-based MongoDB connection
- Environment variables managed securely with `.env`
- Ready for future integrations (OpenAI, Telegram)

---

## 🛠️ Technologies Used
- Python 3.8
- Flask
- pymongo
- python-dotenv
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
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### 3. Install dependencies:
```bash
pip install -r requirements.txt
```

### 4. Create a `.env` file:
```
MONGO_URI=your_mongo_connection_string_here
```

### 5. Run the app:
```bash
python app.py
```
Visit `http://127.0.0.1:5000/` in your browser to verify.

---

## 📌 Notes
- The application is currently in development mode.
- MongoDB URI is managed through environment variables and not included in the repository.
- This README will be updated as new features are added (authentication, task logic, AI & Telegram integrations).

---

## 🧑‍💻 Developer
Created by Yuval Yakuti, as part of the application process for the Co-Op program.

---
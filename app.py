# --- Import required libraries ---
from flask import Flask, request, jsonify, render_template, session, redirect
import os
import logging
import re
from weekly_summary import scheduler  
from bson.objectid import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from ai_helper import generate_task_description, analyze_task_description
from telegram_helper import send_task_to_telegram
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS

# --- Load environment variables from .env file ---
load_dotenv()

# --- Logging Configuration ---
# This sets up logging to record application events into a file called 'app.log'
# Each log entry will include the timestamp, log level (INFO, WARNING, etc.), and the message
logging.basicConfig(
    level=logging.INFO,                  
    format='%(asctime)s - %(levelname)s - %(message)s',  
    filename='app.log',                   
    filemode='a'                           # Append mode: doesn't overwrite existing logs
)

# Configure basic logging
logging.basicConfig(
    filename='app.log',         # The log messages will be saved in this file
    level=logging.INFO,         
    format='%(asctime)s - %(levelname)s - %(message)s'  
)

# --- Initialize Flask app ---
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:5000"]}})
limiter = Limiter(get_remote_address, app=app)

# --- Secret key for managing user sessions ---
app.secret_key = os.getenv("SECRET_KEY", "dev_key_for_now")

# --- Connect to MongoDB using URI from .env ---
mongo_uri = os.getenv("MONGO_URI")
print("🔍 MONGO_URI =", os.getenv("MONGO_URI"))
mongo_client = MongoClient(os.getenv("MONGO_URI"))
db = mongo_client["voltify_db"]

# --- Homepage route: displays options to login or register ---
@app.route('/')
def home():
    return redirect('/login_form')

# --- User registration route using JSON ---
@app.route('/register', methods=['POST'])
def register():
    # Extract data from the incoming JSON request
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Check if username or password is missing
    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400

    # Access the users collection in the database
    users_collection = db['users']

    # Check if the username already exists
    existing_user = users_collection.find_one({'username': username})
    if existing_user:
        return jsonify({'error': 'Username already exists'}), 409

    # Hash the password and insert the new user into the database
    hashed_password = generate_password_hash(password)
    users_collection.insert_one({
        'username': username,
        'password': hashed_password
    })

    return jsonify({'message': 'User registered successfully'}), 201

# --- User login route using JSON ---
@app.route('/api/login', methods=['POST'])
@limiter.limit("5 per minute")
def login_api():
    # Extract data from the incoming JSON request
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Log the attempt
    logging.info(f"Login attempt for user: {username}")

    # Check if username or password is missing
    if not username or not password:
        logging.warning(f"Missing login fields. Username: {username}")
        return jsonify({'error': 'Missing username or password'}), 400

    users_collection = db['users']
    user = users_collection.find_one({'username': username})

    # If user not found or password incorrect
    if not user or not check_password_hash(user['password'], password):
        logging.warning(f"Failed login for user: {username}")
        return jsonify({'error': 'Invalid username or password'}), 401

    # If login is successful
    logging.info(f"Successful login for user: {username}")
    return jsonify({'message': 'Logged in successfully'}), 200

# --- Route for handling registration form submission ---
@app.route('/register_form', methods=['POST'])
def process_register_form():
    username = request.form.get('username')
    password = request.form.get('password')

    logging.info(f"Registration attempt for username: {username}")

    # Check for missing or invalid input
    if not username or not password:
        logging.warning("Registration failed: Missing fields.")
        return "Missing fields", 400

    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        logging.warning(f"Registration failed: Invalid username format - {username}")
        return "Username must contain only letters, numbers, and underscores.", 400

    if len(username) < 3 or len(username) > 20:
        logging.warning(f"Registration failed: Username length invalid - {username}")
        return "Username must be between 3 and 20 characters.", 400

    if len(password) < 6 or len(password) > 32:
        logging.warning(f"Registration failed: Password length invalid - {username}")
        return "Password must be between 6 and 32 characters.", 400

    users_collection = db['users']
    existing_user = users_collection.find_one({'username': username})
    if existing_user:
        logging.warning(f"Registration failed: Username already exists - {username}")
        return "Username already exists", 409

    hashed_password = generate_password_hash(password)
    users_collection.insert_one({
        'username': username,
        'password': hashed_password
    })

    logging.info(f"New user registered successfully: {username}")

    return """
        <h3>🎉 User registered successfully!</h3>
        <p><a href='/login_form'>Click here to login</a></p>
    """, 201

# --- Route for showing the login form (HTML) ---
@app.route('/login_form', methods=['GET'])
def show_login_form():
    return render_template('login_form.html')

# --- Route for handling login form submission ---
@app.route('/login_form', methods=['POST'])
@limiter.limit("5 per minute")
def process_login_form():
    username = request.form.get('username')
    password = request.form.get('password')

    # Check for missing fields
    if not username or not password:
        return "Missing fields", 400

    # Search for user in the database
    users_collection = db['users']
    user = users_collection.find_one({'username': username})

    # Validate user credentials
    if not user or not check_password_hash(user['password'], password):
        return "Invalid username or password", 401

    # Save the logged-in user in the session
    session['username'] = username
    return redirect('/tasks')

# --- Route for logging out the user ---
@app.route('/logout')
def logout():
    session.pop('username', None)
    return "Logged out!<br><a href='/login_form'>Login again</a>"

@app.route('/tasks', methods=['GET'])
def show_tasks():
    # Check if user is logged in
    if 'username' not in session:
        return "You must be logged in to view your tasks.<br><a href='/login_form'>Login</a>", 401

    username = session['username']
    category_filter = request.args.get('category')  # Get filter from query string

    # Build the query
    query = {'username': username}
    if category_filter:
        query['category'] = category_filter

    # Fetch filtered tasks from DB
    tasks_collection = db['tasks']
    user_tasks = list(tasks_collection.find(query).sort([
        ('completed', 1),
        ('created_at', 1)
    ]))

    # Pass selected category to the template for highlighting
    return render_template('tasks.html', username=username, tasks=user_tasks, selected_category=category_filter)

# --- Route for displaying the task creation form ---
@app.route('/add_task', methods=['GET'])
def show_add_task_form():
    if 'username' not in session:
        logging.warning("Unauthorized attempt to access add_task form")
        return "You must be logged in to add a task.", 401
    return render_template('add_task.html')

# --- Route for handling the task submission ---
@app.route('/add_task', methods=['POST'])
def add_task():
    if 'username' not in session:
        logging.warning("Unauthorized attempt to add a task")
        return "You must be logged in to add a task.", 401

    username = session['username']
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    priority = request.form.get('priority') == 'on'
    category = request.form.get('category', '').strip()
    estimated_time = request.form.get('estimated_time', '').strip()

    logging.info(f"User '{username}' is submitting a new task: {title}")

    # --- Input Validation ---
    if not title or len(title) < 2:
        logging.warning(f"Task submission by '{username}' failed: Title too short or missing")
        return "Title must be at least 2 characters.", 400

    if estimated_time:
        try:
            estimated_time = int(estimated_time)
            if estimated_time <= 0:
                logging.warning(f"Task submission by '{username}' failed: Non-positive estimated time")
                return "Estimated time must be a positive number.", 400
        except ValueError:
            logging.warning(f"Task submission by '{username}' failed: Invalid estimated time (not a number)")
            return "Estimated time must be a number.", 400
    else:
        estimated_time = None

    # --- AI-based Estimations if missing ---
    if not category or not estimated_time:
        logging.info(f"AI estimation triggered for task '{title}' by '{username}'")
        ai_category, ai_time = analyze_task_description(description or title)
        if not category:
            category = ai_category
        if not estimated_time:
            estimated_time = int(ai_time)

    task_data = {
        'username': username,
        'title': title,
        'description': description,
        'completed': False,
        'priority': priority,
        'category': category,
        'estimated_time': estimated_time,
        'created_at': datetime.utcnow()
    }

    # --- Save to DB ---
    tasks_collection = db['tasks']
    tasks_collection.insert_one(task_data)

    logging.info(f"Task successfully added by '{username}': {title}")

    send_task_to_telegram(title, description)
    logging.info(f"Telegram notification sent for task: {title}")

    return redirect('/tasks')

# --- Route for deleting a task by its ID ---
@app.route('/delete_task/<task_id>', methods=['POST'])
def delete_task(task_id):
    # Make sure the user is logged in
    if 'username' not in session:
        logging.warning("Unauthorized attempt to delete a task")
        return "You must be logged in to delete a task.", 401

    tasks_collection = db['tasks']
    
    # Attempt to find the task before deleting
    task = tasks_collection.find_one({
        '_id': ObjectId(task_id),
        'username': session['username']
    })

    if not task:
        logging.warning(f"Task with ID {task_id} not found or access denied for user {session['username']}")
        return "Task not found or access denied.", 404

    tasks_collection.delete_one({
        '_id': ObjectId(task_id),
        'username': session['username']
    })

    logging.info(f"Task '{task['title']}' deleted by user '{session['username']}'")

    # Redirect back to the task list
    return redirect('/tasks')

# --- Route for handling the task update ---
@app.route('/edit_task/<task_id>', methods=['POST'])
def update_task(task_id):
    if 'username' not in session:
        logging.warning("Unauthorized attempt to update a task")
        return "You must be logged in to update a task.", 401

    title = request.form.get('title')
    description = request.form.get('description')
    completed = request.form.get('completed') == 'on'
    priority = request.form.get('priority') == 'on'
    category = request.form.get('category')
    estimated_time = request.form.get('estimated_time')

    if estimated_time:
        try:
            estimated_time = int(estimated_time)
            if estimated_time <= 0:
                logging.warning(f"Invalid estimated time provided by user {session['username']}")
                return "Estimated time must be a positive number.", 400
        except ValueError:
            logging.warning(f"Non-numeric estimated time provided by user {session['username']}")
            return "Estimated time must be a number.", 400
    else:
        estimated_time = None

    if not title:
        logging.warning(f"User {session['username']} submitted a task without a title")
        return "Title is required.", 400

    tasks_collection = db['tasks']
    result = tasks_collection.update_one(
        {'_id': ObjectId(task_id), 'username': session['username']},
        {'$set': {
            'title': title,
            'description': description,
            'completed': completed,
            'priority': priority,
            'estimated_time': estimated_time,
            'category': category
        }}
    )

    if result.matched_count == 0:
        logging.warning(f"Task update failed. Task ID: {task_id} not found for user {session['username']}")
        return "Task not found or access denied.", 404

    logging.info(f"Task '{title}' updated by user '{session['username']}'")
    return redirect('/tasks')

# --- Route for updating the "completed" status of a task ---
@app.route('/update_task_status/<task_id>', methods=['POST'])
def update_task_status(task_id):
    # Make sure the user is logged in
    if 'username' not in session:
        logging.warning("Unauthorized attempt to update task status")
        return jsonify({'error': 'Unauthorized'}), 401

    # Get JSON data sent from the client
    data = request.get_json()
    completed = data.get('completed', False)

    tasks_collection = db['tasks']
    task = tasks_collection.find_one({'_id': ObjectId(task_id), 'username': session['username']})

    if not task:
        logging.warning(f"Task not found or access denied for task_id: {task_id}")
        return jsonify({'error': 'Task not found'}), 404

    # Update the "completed" field of the task
    tasks_collection.update_one(
        {'_id': ObjectId(task_id), 'username': session['username']},
        {'$set': {'completed': completed}}
    )

    status = "completed" if completed else "not completed"
    logging.info(f"Task '{task['title']}' marked as {status} by user '{session['username']}'")

    # 🔔 Send Telegram notification if task is marked as completed
    if completed:
        from telegram_helper import bot, chat_id
        message = f"✅ *Task Completed!*\n\n*Title:* {task['title']}\n*Description:* {task.get('description', '')}"
        try:
            bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")
            logging.info(f"Telegram notification sent for task completion: '{task['title']}'")
        except Exception as e:
            logging.error(f"Failed to send Telegram message: {e}")

    # Return a success message as JSON
    return jsonify({'message': 'Task status updated'}), 200

# --- Route to send a task to Telegram ---
@app.route('/send_to_telegram/<task_id>', methods=['POST'])
def send_to_telegram(task_id):
    # Ensure the user is logged in
    if 'username' not in session:
        return "Unauthorized", 401

    tasks_collection = db['tasks']
    
    # Find the task that belongs to the current user
    task = tasks_collection.find_one({
        '_id': ObjectId(task_id),
        'username': session['username']
    })

    if not task:
        return "Task not found or access denied", 404

    # Extract task details
    title = task.get('title', 'Untitled')
    description = task.get('description', '')

    # Debugging: print the task details
    print(f"Sending Task to Telegram: Title: {title}, Description: {description}")

    # Import and use the Telegram helper to send message
    from telegram_helper import send_task_to_telegram
    send_task_to_telegram(title, description)

    try:
        send_task_to_telegram(title, description)
        print("Task sent to Telegram successfully!")
    except Exception as e:
        print(f"Error sending task to Telegram: {e}")
        return f"Error sending task to Telegram: {e}", 500

    return redirect('/tasks')


# --- Route for handling AI suggestion based on a specific task ---
@app.route('/ask_ai/<task_id>', methods=['GET', 'POST'])
def ask_ai(task_id):
    # Check if the user is logged in
    if 'username' not in session:
        return "Unauthorized", 401

    tasks_collection = db['tasks']

    # Look up the task by ID and ensure it belongs to the logged-in user
    task = tasks_collection.find_one({
        '_id': ObjectId(task_id),
        'username': session['username']
    })

    # If task not found or doesn't belong to user
    if not task:
        return "Task not found or access denied", 404

    # Get the task title to send to GPT
    title = task.get('title', 'Untitled')

    # Use OpenAI to generate a helpful description based on the title
    suggestion = generate_task_description(title)

    # Show the AI's response in a simple page
    return render_template("ask_ai.html", task=task, ai_description=suggestion)

# --- Route to apply the AI suggestion to the task description ---
@app.route('/apply_ai_suggestion/<task_id>', methods=['POST'])
def apply_ai_suggestion(task_id):
    # Ensure the user is logged in
    if 'username' not in session:
        return "Unauthorized", 401

    tasks_collection = db['tasks']

    # Get the suggested description from the submitted form
    new_description = request.form.get('ai_description')

    if not new_description:
        return "Missing suggestion", 400

    # Update the task's description in the database
    result = tasks_collection.update_one(
        {'_id': ObjectId(task_id), 'username': session['username']},
        {'$set': {'description': new_description}}
    )

    if result.modified_count == 0:
        return "Update failed or not allowed", 400

    # Redirect the user back to the tasks page
    return redirect('/tasks')

# --- Run the app in development mode ---
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=50001)

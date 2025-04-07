# --- Import required libraries ---
from flask import Flask, request, jsonify, render_template, session, redirect
import os
from bson.objectid import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from ai_helper import generate_task_description 
from telegram_helper import send_task_to_telegram

# --- Load environment variables from .env file ---
load_dotenv()

# --- Initialize Flask app ---
app = Flask(__name__)

# --- Secret key for managing user sessions ---
app.secret_key = os.getenv("SECRET_KEY", "dev_key_for_now")

# --- Connect to MongoDB using URI from .env ---
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client.get_default_database()  # Database name comes from the URI

# --- Homepage route: displays options to login or register ---
@app.route('/')
def home():
    return render_template('auth_options.html')

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
@app.route('/login', methods=['POST'])
def login():
    # Extract data from the incoming JSON request
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Check if username or password is missing
    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400

    # Access the users collection in the database
    users_collection = db['users']

    # Find user by username
    user = users_collection.find_one({'username': username})
    if not user:
        return jsonify({'error': 'Invalid username or password'}), 401

    # Verify the password against the stored hash
    if not check_password_hash(user['password'], password):
        return jsonify({'error': 'Invalid username or password'}), 401

    # If everything matches, login is successful
    return jsonify({'message': 'Logged in successfully'}), 200

# --- Route for showing the registration form (HTML) ---
@app.route('/register_form', methods=['GET'])
def show_register_form():
    return render_template('register_form.html')

# --- Route for handling registration form submission ---
@app.route('/register_form', methods=['POST'])
def process_register_form():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return "Missing fields", 400

    users_collection = db['users']
    existing_user = users_collection.find_one({'username': username})
    if existing_user:
        return "Username already exists", 409

    hashed_password = generate_password_hash(password)
    users_collection.insert_one({
        'username': username,
        'password': hashed_password
    })

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
    tasks_collection = db['tasks']
    
    # Fetch only tasks that belong to the current user
    user_tasks = list(
    tasks_collection.find({'username': username})
    .sort([('completed', 1), ('created_at', 1)]))

    # Render the task page with the username and their tasks
    return render_template('tasks.html', username=username, tasks=user_tasks)

# --- Route for displaying the task creation form ---
@app.route('/add_task', methods=['GET'])
def show_add_task_form():
    if 'username' not in session:
        return "You must be logged in to add a task.", 401
    return render_template('add_task.html')

# --- Route for handling the task submission ---
@app.route('/add_task', methods=['POST'])
def add_task():
    if 'username' not in session:
        return "You must be logged in to add a task.", 401

    title = request.form.get('title')
    description = request.form.get('description')
    priority = request.form.get('priority') == 'on'
    category = request.form.get('category')  # New field from form


    if not title:
        return "Title is required.", 400

    tasks_collection = db['tasks']
    tasks_collection.insert_one({
    'username': session['username'],
    'title': title,
    'description': description,
    'completed': False,
    'priority': priority,
    'category': category,
    'created_at': datetime.utcnow()
    })
    
    print("✅ Inserted task:")
    print(tasks_collection.find_one({'title': title, 'username': session['username']}))

    send_task_to_telegram(title, description)

    # Redirect to task list after successful addition
    return redirect('/tasks')

# --- Route for deleting a task by its ID ---
@app.route('/delete_task/<task_id>', methods=['POST'])
def delete_task(task_id):
    # Make sure the user is logged in
    if 'username' not in session:
        return "You must be logged in to delete a task.", 401

    tasks_collection = db['tasks']
    
    # Delete the task only if it belongs to the logged-in user
    tasks_collection.delete_one({
        '_id': ObjectId(task_id),
        'username': session['username']
    })

    # Redirect back to the task list
    return redirect('/tasks')

# --- Route for showing the edit form for a specific task ---
@app.route('/edit_task/<task_id>', methods=['GET'])
def show_edit_task_form(task_id):
    if 'username' not in session:
        return "You must be logged in to edit a task.", 401

    tasks_collection = db['tasks']
    task = tasks_collection.find_one({
        '_id': ObjectId(task_id),
        'username': session['username']
    })

    if not task:
        return "Task not found or access denied.", 404

    return render_template('edit_task.html', task=task)

# --- Route for handling the task update ---
@app.route('/edit_task/<task_id>', methods=['POST'])
def update_task(task_id):
    if 'username' not in session:
        return "You must be logged in to update a task.", 401

    title = request.form.get('title')
    description = request.form.get('description')
    completed = request.form.get('completed') == 'on'
    priority = request.form.get('priority') == 'on'

    if not title:
        return "Title is required.", 400

    tasks_collection = db['tasks']
    result = tasks_collection.update_one(
        {'_id': ObjectId(task_id), 'username': session['username']},
        {'$set': {
            'title': title,
            'description': description,
            'completed': completed,
            'priority': priority
        }}
    )

    if result.matched_count == 0:
        return "Task not found or access denied.", 404

    return redirect('/tasks')

# --- Route for updating the "completed" status of a task ---
@app.route('/update_task_status/<task_id>', methods=['POST'])
def update_task_status(task_id):
    # Make sure the user is logged in
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    # Get JSON data sent from the client
    data = request.get_json()
    completed = data.get('completed', False)

    tasks_collection = db['tasks']

    # Update the "completed" field of the task if it belongs to the current user
    tasks_collection.update_one(
        {'_id': ObjectId(task_id), 'username': session['username']},
        {'$set': {'completed': completed}}
    )

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

    # Import and use the Telegram helper to send message
    from telegram_helper import send_task_to_telegram
    send_task_to_telegram(title, description)

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
    app.run(debug=True)

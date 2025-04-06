# --- Import required libraries ---
from flask import Flask, request, jsonify, render_template, session
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

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
    return f"Welcome, {username}!<br><a href='/logout'>Log out</a>"

# --- Route for logging out the user ---
@app.route('/logout')
def logout():
    session.pop('username', None)
    return "Logged out!<br><a href='/login_form'>Login again</a>"

# --- Route for handling registration form submission ---
@app.route('/register_form', methods=['POST'])
def process_register_form():
    username = request.form.get('username')
    password = request.form.get('password')

    # Check for missing fields
    if not username or not password:
        return "Missing fields", 400

    # Check if user already exists
    users_collection = db['users']
    existing_user = users_collection.find_one({'username': username})
    if existing_user:
        return "Username already exists", 409

    # Hash password and insert new user
    hashed_password = generate_password_hash(password)
    users_collection.insert_one({
        'username': username,
        'password': hashed_password
    })

    return "User registered successfully!<br><a href='/register_form'>Go back</a>", 201

# --- Run the app in development mode ---
if __name__ == '__main__':
    app.run(debug=True)

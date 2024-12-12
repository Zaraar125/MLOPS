from flask import Flask, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
import jwt
import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Update with your MongoDB URI if needed
# client = MongoClient("mongodb://admin:secret@mongodb:27017/")

db = client['auth_db']  # Use the database named 'auth_db'
users_collection = db['users']  # Use the collection named 'users'

# JWT Configuration
JWT_SECRET = 'your_jwt_secret'  # Keep this secret
JWT_EXPIRATION_DELTA = datetime.timedelta(hours=1)  # Token expiration time

@app.route('/')
def home():
    return redirect(url_for('register'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        security_answer = request.form['security_answer']
        
        if users_collection.find_one({"username": username}):
            flash("Username already exists, please choose another", "danger")
            return redirect(url_for('register'))

        # Store the user with a hashed password and hashed security answer
        users_collection.insert_one({
            'username': username,
            'password': generate_password_hash(password),
            'security_answer': generate_password_hash(security_answer)
        })
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = users_collection.find_one({"username": username})
        
        if user and check_password_hash(user['password'], password):
            # Create JWT token
            token = jwt.encode({
                'username': username,
                'exp': datetime.datetime.utcnow() + JWT_EXPIRATION_DELTA
            }, JWT_SECRET, algorithm='HS256')
            
            # Optionally, you can store the token in the session for easy access (not necessary)
            session['token'] = token

            flash("Login successful! You are now authenticated.", "success")
            return redirect(url_for('home'))
        
        flash("Invalid username or password", "danger")
    
    return render_template('login.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form['username']  # Get the username from the form
        security_answer = request.form['security_answer']
        
        # Find the user by username
        user = users_collection.find_one({"username": username})

        if user:
            # Check if the hashed security answer matches the input
            if check_password_hash(user['security_answer'], security_answer):
                session['verified_user'] = user['username']
                flash("Answer correct! Please enter your new password.", "success")
                return redirect(url_for('reset_password'))
            else:
                flash("Incorrect answer to the security question.", "danger")
        else:
            flash("Username not found.", "danger")
    
    return render_template('forgot_password.html')
@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        username = request.form['username']
        new_password = request.form['new_password']
        
        if username == session.get('verified_user'):
            users_collection.update_one(
                {"username": username},
                {"$set": {"password": generate_password_hash(new_password)}}
            )
            session.pop('verified_user', None)
            flash("Password updated successfully! Please log in.", "success")
            return redirect(url_for('login'))
        
        flash("Invalid username.", "danger")
    
    return render_template('reset_password.html')

# Example of a protected route
@app.route('/protected')
def protected():
    token = session.get('token')  # Or retrieve from Authorization header in a real scenario
    if not token:
        return "Access denied. No token provided.", 403
    
    try:
        # Decode the token to get the user information
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return f"Welcome {payload['username']}! This is a protected route."
    except jwt.ExpiredSignatureError:
        return "Token has expired. Please log in again.", 401
    except jwt.InvalidTokenError:
        return "Invalid token. Please log in again.", 401

if __name__ == '__main__':
    app.run(debug=True)

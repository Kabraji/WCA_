from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import re  # For regex validation

app = Flask(__name__)
app.secret_key = 'Pratham#123'  # Change this to a random secret key
app.config['MONGO_URI'] = 'mongodb://localhost:27017/chat_analyzer'  # Update with your MongoDB URI
mongo = PyMongo(app)

def is_valid_email(email):
    # Simple email regex check
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def is_valid_mobile(mobile):
    # Ensure the mobile number is exactly 10 digits
    return re.match(r"^[0-9]{10}$", mobile)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        mobile = request.form.get('mobile')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        # Server-side validation
        if not is_valid_email(email):
            flash('Invalid email format.')
            return redirect(url_for('register'))

        if not is_valid_mobile(mobile):
            flash('Mobile number must be exactly 10 digits.')
            return redirect(url_for('register'))

        if len(password) < 8:
            flash('Password must be at least 8 characters long.')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)

        # Check if the username or email already exists
        existing_user = mongo.db.USERS.find_one({'username': username})
        existing_email = mongo.db.USERS.find_one({'email': email})
        if existing_user:
            flash('Username already exists. Please choose a different one.')
            return redirect(url_for('register'))
        if existing_email:
            flash('Email already exists. Please use a different one.')
            return redirect(url_for('register'))

        # Insert the new user into the database
        mongo.db.USERS.insert_one({
            'name': name,
            'mobile': mobile,
            'email': email,
            'username': username,
            'password': hashed_password
        })
        flash('Registration successful! Please log in.')
        return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    user = mongo.db.USERS.find_one({'username': username})

    if user and check_password_hash(user['password'], password):
        session['username'] = username
        return redirect("http://localhost:8501")  # Change this to your Streamlit app's URL
    else:
        flash('Invalid username or password.')
        return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    else:
        return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)

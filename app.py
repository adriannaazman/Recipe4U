import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Correct path to database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "database", "user.db")


import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def create_db():
    db_path = os.path.join(BASE_DIR, "database", "user.db")
    if not os.path.exists(db_path):  # Only create if not already exists
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL
                    )''')
        conn.commit()
        conn.close()
        print("Database and users table created successfully!")
    else:
        print("Database already exists.")

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
            conn.commit()
            return redirect('/login')
        except sqlite3.IntegrityError:
            return "❌ Email already exists!"
        finally:
            conn.close()
    return render_template('register.html')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = c.fetchone()
        conn.close()

        if user:
            Flask("Login successful!", "success")
            return redirect(url_for('index'))
        else:
            Flask("Incorrect email or password.", "danger")
            return redirect(url_for('login'))
    return render_template('login.html')

# Forgot Password page
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        new_password = request.form['new_password']

        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        user = c.fetchone()

        if user:
            c.execute("UPDATE users SET password=? WHERE email=?", (new_password, email))
            conn.commit()
            Flask("Password updated successfully. Please log in.", "success")
            return redirect(url_for('login'))
        else:
            Flask("Email not found.", "danger")
            return redirect(url_for('forgot_password'))
        conn.close()
    return render_template('forgot_password.html')

if __name__ == '__main__':
    create_db()
    app.run(debug=True)
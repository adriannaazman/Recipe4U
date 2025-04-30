import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flash messages

# Correct path to database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "database", "user.db")

def create_db():
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()
        print("Database and users table created successfully!")
    else:
        print("Database already exists.")

@app.route('/')
def index():
    return render_template('index.html')

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
            flash("✅ Registered successfully! Please login.", "success")
            return redirect('/login')
        except sqlite3.IntegrityError:
            flash("❌ Email already exists!", "danger")
        finally:
            conn.close()
    return render_template('register.html')

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
            flash("✅ Login successful!", "success")
            session['user_name'] = user[1]
            return redirect('/home')
        else:
            flash("❌ Incorrect email or password.", "danger")
            return redirect('/login')
    return render_template('login.html')


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
            flash("✅ Password updated. Please log in.", "success")
            return redirect(url_for('login'))
        else:
            flash("❌ Email not found.", "danger")
            return redirect(url_for('forgot_password'))
        conn.close()
    return render_template('forgot_password.html')

@app.route('/home')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    create_db()
    app.run(debug=True)
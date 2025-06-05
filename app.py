import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "database", "main.db")

def create_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS ingredients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        option TEXT,
        quantity INTEGER DEFAULT 0
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS health_profile (
        user_id INTEGER,
        age INTEGER,
        weight REAL,
        height REAL,
        activity_level TEXT,
        PRIMARY KEY(user_id),
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    conn.commit()
    conn.close()

create_db()
print("✅ Database and tables created successfully.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                           (name, email, hashed_password))
            conn.commit()
            flash("✅ Registered successfully! Please login.", "success")
            return redirect(url_for('login'))
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
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            flash("✅ Login successful!", "success")
            return redirect(url_for('home'))
        else:
            flash("❌ Incorrect email or password.", "danger")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

@app.route('/home')
def home():
    if 'user_name' in session:
        return render_template('home.html', user=session['user_name'])
    else:
        flash("⚠️ Please login first.", "warning")
        return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        age = int(request.form['age'])
        weight = float(request.form['weight'])
        height = float(request.form['height'])
        activity = request.form['activity']

        # BMI Calculation
        bmi = round(weight / ((height / 100) ** 2), 2)

        if activity == 'low':
            calories = weight * 25
        elif activity == 'medium':
            calories = weight * 30
        else:
            calories = weight * 35

        return render_template('profile_result.html', bmi=bmi, calories=calories)

    return render_template('profile_form.html')

@app.route('/health_profile', methods=['GET', 'POST'])
def health_profile():
    if request.method == 'POST':
        age = request.form['age']
        weight = request.form['weight']
        height = request.form['height']
        activity_level = request.form['activity_level']

        # Save to DB
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO health_profile (user_id, age, weight, height, activity_level)
                          VALUES (?, ?, ?, ?, ?)''', (session['user_id'], age, weight, height, activity_level))
        conn.commit()
        conn.close()

        session['health_filled'] = True  # Mark as done
        return redirect(url_for('profile_result'))

    return render_template('health_profile.html')

@app.route('/profile_result')
def profile_result():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT age, weight, height, activity_level FROM health_profile WHERE user_id = ?', (session['user_id'],))
    data = cursor.fetchone()
    conn.close()

    if data:
        age, weight, height, activity_level = data
        weight = float(weight)
        height = float(height) / 100  # convert cm to m

        # Calculate BMI
        bmi = round(weight / (height ** 2), 2)

        # Estimate calories (simple formula)
        activity_factors = {
            'low': 30,
            'medium': 35,
            'high': 40
        }
        calories = round(weight * activity_factors.get(activity_level, 35))

        return render_template('profile_result.html', bmi=bmi, calories=calories)

    return "Health profile not found."

if __name__ == '__main__':
    app.run(debug=True)
import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = 'your_secret_key'  

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

        # ✅ Hash the password
        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            # ✅ Save hashed password
            cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, hashed_password))
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
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[3], password):  # index 3 = hashed password
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            flash("✅ Login successful!", "success")
            return redirect('/home')  # this is a route, not a file
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
<<<<<<< HEAD
    if 'user_name' in session:
        return render_template('home.html', user=session['user_name'])
    else:
        flash("⚠️ Please login first.", "warning")
        return redirect('/login')
    
@app.route('/ingredients')
def show_ingredients():
    conn = sqlite3.connect("database/ingredients.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ingredients")
    ingredients = cursor.fetchall()
    conn.close()
    return render_template("ingredients.html", ingredients=ingredients)




=======
    return render_template('home.html')
>>>>>>> d88ff83cc0e927385632b320e01ef010375a1f8b
@app.route('/logout')
def logout():
    return render_template('logout.html')


if __name__ == '__main__':
    create_db()
    app.run(debug=True)
import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from collections import defaultdict

app = Flask(__name__)  
app.secret_key = 'your_secret_key'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "database", "main.db")

#make sure database and tables are created
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
    cursor.execute('''CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recipe_id INTEGER,
        username TEXT,
        rating INTEGER,
        comment TEXT,
        timestamp TEXT
    )''')
    conn.commit()
    conn.close()

create_db()

#User database connection (main.db)
def get_user_db_connection():
    db_path = os.path.join(BASE_DIR, "database", "main.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/welcome')
def welcome():
    return render_template('index.html')

#ingredients form bar
@app.route('/', methods=['GET', 'POST'])
def index():
    recipes = []
    if request.method == 'POST':
        user_ingredients = [i.strip().lower() for i in request.form.get('ingredients', '').split(',')]
        min_match = int(request.form.get('min_match', 1))
        meal_type = request.form.get('meal_type', '')
        diet = request.form.get('diet', '')
        recipes = get_matching_recipes(user_ingredients, min_match, meal_type, diet)

    return render_template('indexupdate.html', recipes=recipes)

def get_db_connection():
    conn = sqlite3.connect('recipes_database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_matching_recipes(user_ingredients, min_match=1, meal_type='', diet=''):
    conn = get_db_connection()
    cursor = conn.cursor()

    like_clauses = [f"ingredients LIKE ?" for _ in user_ingredients]
    query_conditions = [f"({' OR '.join(like_clauses)})"]
    params = [f"%{ingredient}%" for ingredient in user_ingredients]

    #filters
    if meal_type:
        query_conditions.append("meal_type = ?")
        params.append(meal_type)
    if diet:
        query_conditions.append("diet = ?")
        params.append(diet)

    query = f"SELECT * FROM recipes WHERE {' AND '.join(query_conditions)}"
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()

#recipe rank
    enriched_recipes = []
    for recipe in results:
        recipe_ingredients = [ing.strip().lower() for ing in recipe['ingredients'].split(',')]
        matched = [ing for ing in user_ingredients if ing in recipe_ingredients]
        missing = [ing for ing in recipe_ingredients if ing not in user_ingredients]
        match_count = len(matched)
        missing_count = len(missing)

        if match_count >= min_match:
            enriched_recipes.append({
                'id': recipe['id'],
                'name': recipe['name'],
                'ingredients': recipe['ingredients'],
                'meal_type': recipe['meal_type'],
                'diet': recipe['diet'],
                'matches': match_count,
                'missing_count': missing_count,
                'missing_ingredients': missing,
                'steps': recipe['steps'],  
                'cooking_time': recipe['cooking_time'],
                'image_url': recipe['image_url']

            })

    #sort recipes by most matched ingredients with leasr missing ingredients
    conn = get_db_connection()
    cursor = conn.cursor()
    for recipe in enriched_recipes:
        cursor.execute('SELECT username, rating, comment, timestamp FROM comments WHERE recipe_id = ? ORDER BY timestamp DESC', (recipe['id'],))
        recipe['comments'] = cursor.fetchall()
    conn.close()

    enriched_recipes.sort(key=lambda r: (-r['matches'], r['missing_count']))
    return enriched_recipes

#meal plan generator
@app.route('/meal_plan', methods=['GET', 'POST'])
def meal_plan():
    weekly_plan = []
    if request.method == 'POST':
        user_ingredients = request.form.get('ingredients', '').lower().split(', ')
        num_days = int(request.form.get('num_days', 7))
        meal_slots = ['breakfast', 'lunch', 'dinner']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM recipes")
        all_recipes = cursor.fetchall()
        conn.close()

        from collections import defaultdict
        categorized_recipes = defaultdict(list)

        for recipe in all_recipes:
            recipe_ingredients = [ing.strip().lower() for ing in recipe['ingredients'].split(',')]
            matched = set(user_ingredients).intersection(recipe_ingredients)
            missing = set(recipe_ingredients) - set(user_ingredients)

            categorized_recipes[recipe['meal_type'].lower()].append({
                'name': recipe['name'],
                'ingredients': recipe_ingredients,
                'matched': list(matched),
                'missing': list(missing),
                'missing_count': len(missing),
                'match_count': len(matched),
                'diet': recipe['diet']
            })

        for meal in meal_slots:
            categorized_recipes[meal].sort(key=lambda x: (-x['match_count'], x['missing_count']))

        for day in range(1, num_days + 1):
            day_plan = {'day': f'Day {day}'}
            for meal in meal_slots:
                if categorized_recipes[meal]:
                    recipe = categorized_recipes[meal].pop(0)
                    day_plan[meal] = recipe
                else:
                    day_plan[meal] = None
            weekly_plan.append(day_plan)

    return render_template('meal_plan.html', weekly_plan=weekly_plan)

@app.route('/comment', methods=['POST'])
def submit_comment():
    if 'user_id' not in session:
        flash("⚠️ You must be logged in to comment.", "warning")
        return redirect(url_for('login'))

    recipe_id = request.form['recipe_id']
    username = session['user_name']  #this is take from session, not form
    rating = int(request.form['rating'])
    comment = request.form['comment']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO comments (recipe_id, username, rating, comment, timestamp) VALUES (?, ?, ?, ?, datetime("now"))',
        (recipe_id, username, rating, comment)
    )
    conn.commit()
    conn.close()

    flash("✅ Comment submitted successfully!", "success")
    return redirect('/')

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
            cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, hashed_password))
            conn.commit()
            flash("✅ Registered successfully! Please login.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("❌ Email already exists!", "danger")
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        new_password = request.form['new_password']
        hashed_password = generate_password_hash(new_password)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cursor.fetchone()

        if user:
            cursor.execute("UPDATE users SET password=? WHERE email=?", (hashed_password, email))
            conn.commit()
            conn.close()
            flash("✅ Password reset successful! Please log in with your new password.", "success")
            return redirect(url_for('login'))
        else:
            conn.close()
            flash("❌ Email not found in our records.", "danger")

    return render_template('forgot_password.html')

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
            return redirect(url_for('index'))
        else:
            flash("❌ Incorrect email or password.", "danger")
    return render_template('login.html')

@app.route('/delete_account', methods=['GET', 'POST'])
def delete_account():
    if 'user_id' not in session:
        flash("❌ Please log in to delete your account.", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_id = session['user_id']

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))

        cursor.execute("DELETE FROM health_profile WHERE user_id = ?", (user_id,))

        conn.commit()
        conn.close()

        session.clear()
        flash("✅ Your account has been deleted successfully.", "success")
        return redirect(url_for('register'))  
    return render_template('delete_account.html')

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

        bmi = round(weight / ((height / 100) ** 2), 2)
        calories = weight * (25 if activity == 'low' else 30 if activity == 'medium' else 35)

        return render_template('profile_result.html', bmi=bmi, calories=calories)
    return render_template('profile_form.html')

@app.route('/bmi', methods=['GET', 'POST'])
def bmi_calculator():
    bmi = None
    calories = None

    if request.method == 'POST':
        age = int(request.form['age'])
        weight = float(request.form['weight'])
        height = float(request.form['height'])
        activity = request.form['activity_level']

        bmi = round(weight / ((height / 100) ** 2), 2)
        calories = round(weight * {
            'sedentary': 25,
            'light': 30,
            'moderate': 35,
            'active': 40
        }.get(activity, 30))

    return render_template('health_profile.html', bmi=bmi, calories=calories)

if __name__ == '__main__':
    app.run(debug=True)
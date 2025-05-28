import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "database", "main.db")  # Main database

# Create tables (users, ingredients, saved_recipes)
def create_tables():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')

    # Create ingredients table
    c.execute('''
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            option TEXT,
            quantity INTEGER DEFAULT 0
        )
    ''')

    # Create saved_recipes table (to save recipes for users)
    c.execute('''
        CREATE TABLE IF NOT EXISTS saved_recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            recipe_name TEXT,
            ingredients TEXT,
            instructions TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()

create_tables()
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
        flash("⚠ Please login first.", "warning")
        return redirect(url_for('login'))

@app.route('/ingredients')
def show_ingredients():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM ingredients ORDER BY name")
    ingredients = c.fetchall()
    conn.close()
    return render_template("ingredients.html", ingredients=ingredients)

@app.route('/ingredients/<int:ingredient_id>')
def ingredient_detail(ingredient_id):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT * FROM ingredients WHERE id=?", (ingredient_id,))
    ingredient = c.fetchone()
    conn.close()

    if not ingredient:
        flash("Ingredient not found.", "danger")
        return redirect(url_for('show_ingredients'))

    return render_template('ingredient_detail.html', ingredient=ingredient)

@app.route('/add_ingredient', methods=['GET', 'POST'])
def add_ingredient():
    if 'user_name' not in session:
        flash("Please login to add ingredients.", "warning")
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name'].strip()
        quantity = request.form['quantity'].strip()
        option = request.form['option'].strip() if 'option' in request.form else None

        if not name or not quantity:
            flash("Please enter all fields.", "danger")
            return redirect(url_for('add_ingredient'))

        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO ingredients (name, option, quantity) VALUES (?, ?, ?)",
                      (name, option, quantity))
            conn.commit()
            flash(f"✅ Ingredient '{name}' added successfully!", "success")
            return redirect(url_for('show_ingredients'))
        except sqlite3.IntegrityError:
            flash("❌ Ingredient already exists!", "danger")
        finally:
            conn.close()

    return render_template('add_ingredient.html')

@app.route('/add_to_cart/<int:ingredient_id>')
def add_to_cart(ingredient_id):
    if 'cart' not in session:
        session['cart'] = {}

    cart = session['cart']

    if str(ingredient_id) in cart:
        cart[str(ingredient_id)] += 1
    else:
        cart[str(ingredient_id)] = 1

    session['cart'] = cart
    flash("🛒 Added to cart!", "success")
    return redirect(url_for('show_ingredients'))

@app.route('/cart')
def view_cart():
    if 'cart' not in session or len(session['cart']) == 0:
        flash("🛒 Cart is empty.", "info")
        return render_template('cart.html', cart_items=[], total=0)

    cart = session['cart']
    ids = tuple(int(k) for k in cart.keys())

    placeholders = ",".join("?" * len(ids))
    query = f"SELECT * FROM ingredients WHERE id IN ({placeholders})"

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(query, ids)
    ingredients = c.fetchall()
    conn.close()

    cart_items = []
    total_items = 0
    for ing in ingredients:
        quantity_in_cart = cart[str(ing[0])]
        
        # Ensure the length check for ing and assign quantity
        if len(ing) > 3:
            quantity = ing[3]
        else:
            quantity = 0  # or some default value
        
        cart_items.append({
            "id": ing[0],
            "name": ing[1],
            "option": ing[2] if ing[2] else "No option",
            "quantity": quantity,
            "count": quantity_in_cart
        })
        total_items += quantity_in_cart

    return render_template('cart.html', cart_items=cart_items, total=total_items)

@app.route('/recipe')
def recipe_page():
    recipes = [
        {
            'name': 'Chicken Lettuce Wrap',
            'ingredients': ['Chicken', 'Lettuce', 'Mayonnaise', 'Pepper', 'Cucumber'],
            'instructions': 'Mix all ingredients and wrap them in lettuce leaves. Enjoy!'
        },
        {
            'name': 'Chicken Salad',
            'ingredients': ['Chicken', 'Lettuce', 'Mayonnaise', 'Pepper', 'Cucumber'],
            'instructions': 'Combine all ingredients in a bowl and toss together.'
        }
    ]
    print(recipes)  # Check the contents of recipes
    return render_template('recipe.html', recipes=recipes)


@app.route('/clear_cart')
def clear_cart():
    session.pop('cart', None)  # Clear the cart from the session
    flash("🛒 Cart has been cleared.", "info")
    return redirect(url_for('view_cart'))


@app.route('/save_recipe', methods=['POST'])
def save_recipe():
    if 'user_id' not in session:
        flash("You need to log in to save a recipe.", "warning")
        return redirect(url_for('login_page'))

    user_id = session['user_id']
    recipe_name = request.form['recipe_name']
    ingredients = request.form['ingredients']
    instructions = request.form['instructions']

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        INSERT INTO saved_recipes (user_id, recipe_name, ingredients, instructions)
        VALUES (?, ?, ?, ?)
    ''', (user_id, recipe_name, ingredients, instructions))
    conn.commit()
    conn.close()

    flash("Recipe saved successfully!", "success")
    return redirect(url_for('recipe_page'))  # Redirect back to the recipe page

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
        conn = sqlite3.connect('main.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO health_profile (user_id, age, weight, height, activity_level)
            VALUES (?, ?, ?, ?, ?)
        ''', (session['user_id'], age, weight, height, activity_level))
        conn.commit()
        conn.close()

        session['health_filled'] = True  # Mark as done
        return redirect(url_for('profile_result'))


    return render_template('health_profile.html')

@app.route('/profile_result')
def profile_result():
    conn = sqlite3.connect('main.db')
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
    create_tables()
    app.run(debug=True)
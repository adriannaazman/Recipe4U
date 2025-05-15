from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import random

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('ingredients.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            content TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            score INTEGER NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            meal_type TEXT,
            diet TEXT,
            time INTEGER,
            steps INTEGER,
            url TEXT
        )
    ''')

    conn.commit()
    conn.close()

def difficulty_level(recipe):
    time = recipe.get("time") or 0
    steps = recipe.get("steps") or 0
    if time <= 15 and steps <= 5:
        return "easy"
    elif time <= 45 and steps <= 10:
        return "medium"
    else:
        return "hard"

@app.route("/", methods=["GET", "POST"])
def index():
    conn = get_db_connection()
    c = conn.cursor()

    c.execute("SELECT name FROM ingredients")
    ingredients = c.fetchall()
    user_ingredients = [row["name"].lower() for row in ingredients]

    c.execute("SELECT id, name, ingredients, meal_type, diet, time, steps, url FROM recipes")
    db_recipes = c.fetchall()

    recipes = []
    for r in db_recipes:
        ing_list = [i.strip().lower() for i in r["ingredients"].split(",")]
        recipes.append({
            "id": r["id"],
            "name": r["name"],
            "ingredients": ing_list,
            "meal_type": r["meal_type"],
            "diet": r["diet"],
            "time": r["time"],
            "steps": r["steps"],
            "url": r["url"]
        })

    filtered_recipes = recipes

    if request.method == "POST":
        meal_type_filter = request.form.get("meal_type", "").lower()
        diet_filter = request.form.get("diet", "").lower()
        difficulty_filter = request.form.get("difficulty", "").lower()
        min_match = int(request.form.get("min_match", 0))

        filtered_recipes = []
        for r in recipes:
            match_count = sum(1 for i in r["ingredients"] if i in user_ingredients)

            if meal_type_filter and r["meal_type"] and r["meal_type"].lower() != meal_type_filter:
                continue
            if diet_filter and r["diet"] and r["diet"].lower() != diet_filter:
                continue
            if difficulty_filter and difficulty_level(r) != difficulty_filter:
                continue
            if match_count < min_match:
                continue
            filtered_recipes.append(r)

        filtered_recipes.sort(key=lambda r: sum(1 for i in r["ingredients"] if i in user_ingredients), reverse=True)

    recipe_comments = {}
    recipe_ratings = {}

    for recipe in filtered_recipes:
        recipe_id = recipe["id"]
        c.execute("SELECT content FROM comments WHERE recipe_id = ?", (recipe_id,))
        comments = c.fetchall()
        recipe_comments[recipe_id] = [comment["content"] for comment in comments]

        c.execute("SELECT AVG(score) FROM ratings WHERE recipe_id = ?", (recipe_id,))
        avg = c.fetchone()[0]
        recipe_ratings[recipe_id] = round(avg, 1) if avg else "No ratings yet"

    conn.close()

    meal_plan = None
    if request.method == "POST" and filtered_recipes:
        meal_plan = generate_meal_plan(filtered_recipes)

    return render_template("indexupload.html",
                           ingredients=ingredients,
                           recipes=filtered_recipes,
                           meal_plan=meal_plan,
                           recipe_comments=recipe_comments,
                           recipe_ratings=recipe_ratings)

@app.route("/add", methods=["POST"])
def add():
    name = request.form["ingredient"].strip().lower()
    if not name:
        return redirect("/")

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO ingredients (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM ingredients WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

def generate_meal_plan(recipes):
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    meals = ["Breakfast", "Lunch", "Dinner"]
    plan = {}
    selected = random.sample(recipes * 3, min(21, len(recipes) * 3))

    i = 0
    for day in days:
        plan[day] = {}
        for meal in meals:
            plan[day][meal] = selected[i]["name"] if i < len(selected) else "No Recipe"
            i += 1
    return plan

@app.route("/comment/<int:recipe_id>", methods=["POST"])
def comment(recipe_id):
    content = request.form["content"]
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO comments (recipe_id, content) VALUES (?, ?)", (recipe_id, content))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/rate/<int:recipe_id>", methods=["POST"])
def rate(recipe_id):
    score = int(request.form["score"])
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO ratings (recipe_id, score) VALUES (?, ?)", (recipe_id, score))
    conn.commit()
    conn.close()
    return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)

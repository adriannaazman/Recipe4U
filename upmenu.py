from flask import Flask, render_template, request, redirect
import sqlite3
import random

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('ingredients.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

#mock recipes
recipes = [
    {"id": 1, "name": "Omelette", "ingredients": ["egg", "cheese"], "meal_type": "breakfast", "diet": "vegetarian", "time": 10, "steps": 2},
    {"id": 2, "name": "Tomato Pasta", "ingredients": ["tomato", "pasta"], "meal_type": "lunch", "diet": "vegan", "time": 20, "steps": 4},
    {"id": 3, "name": "Grilled Cheese", "ingredients": ["bread", "cheese"], "meal_type": "lunch", "diet": "vegetarian", "time": 15, "steps": 3},
    {"id": 4, "name": "Salad", "ingredients": ["lettuce", "tomato"], "meal_type": "dinner", "diet": "vegan", "time": 10, "steps": 2},
    {"id": 5, "name": "Smoothie", "ingredients": ["banana", "milk"], "meal_type": "breakfast", "diet": "vegetarian", "time": 5, "steps": 1},
    {"id": 6, "name": "Fried Rice", "ingredients": ["rice", "egg"], "meal_type": "dinner", "diet": "vegetarian", "time": 25, "steps": 5},
    {"id": 7, "name": "Pancakes", "ingredients": ["flour", "milk", "egg"], "meal_type": "breakfast", "diet": "vegetarian", "time": 20, "steps": 4},
]

@app.route("/", methods=["GET", "POST"])
def index():
    conn = sqlite3.connect("ingredients.db")
    c = conn.cursor()
    c.execute("SELECT id, name FROM ingredients")
    ingredients = c.fetchall()
    user_ingredients = [name.lower() for _, name in ingredients]
    conn.close()

    meal_plan = None

    matched_recipes = []
    for recipe in recipes:
        matched = sum(1 for i in recipe["ingredients"] if i in user_ingredients)
        total = len(recipe["ingredients"])
        missing = [i for i in recipe["ingredients"] if i not in user_ingredients]
        matched_recipes.append((recipe["name"], matched, total, missing))

    matched_recipes.sort(key=lambda x: x[1], reverse=True)

    if request.method == "POST":
        matching = [r for r in recipes if any(i in user_ingredients for i in r["ingredients"])]
        meal_plan = generate_meal_plan(matching)

    return render_template("indexup.html", ingredients=ingredients, meal_plan=meal_plan, matched_recipes=matched_recipes)

@app.route("/add", methods=["POST"])
def add():
    name = request.form["ingredient"]
    conn = sqlite3.connect("ingredients.db")
    c = conn.cursor()
    c.execute("INSERT INTO ingredients (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    conn = sqlite3.connect("ingredients.db")
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

if __name__ == "__main__":
    init_db()
    app.run(debug=True)

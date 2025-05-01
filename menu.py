from flask import Flask, render_template, request
import random

app = Flask(__name__)

# mock recipe database
recipes = [
    {"id": 1, "name": "Omelette", "ingredients": ["egg", "cheese"]},
    {"id": 2, "name": "Tomato Pasta", "ingredients": ["tomato", "pasta"]},
    {"id": 3, "name": "Grilled Cheese", "ingredients": ["bread", "cheese"]},
    {"id": 4, "name": "Salad", "ingredients": ["lettuce", "tomato"]},
    {"id": 5, "name": "Smoothie", "ingredients": ["banana", "milk"]},
    {"id": 6, "name": "Fried Rice", "ingredients": ["rice", "egg"]},
    {"id": 7, "name": "Pancakes", "ingredients": ["flour", "milk", "egg"]},
]

@app.route('/', methods=['GET', 'POST'])
def index():
    meal_plan = None
    if request.method == 'POST':
        user_ingredients = request.form.get('ingredients').lower().split(',')
        user_ingredients = [i.strip() for i in user_ingredients]

        matching = [r for r in recipes if any(i in r["ingredients"] for i in user_ingredients)]
        meal_plan = generate_meal_plan(matching)

    return render_template('index.html', meal_plan=meal_plan)

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

if __name__ == '__main__':
    app.run(debug=True)

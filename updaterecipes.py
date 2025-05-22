from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)  

#ingredients form bar
@app.route('/', methods=['GET', 'POST'])
def index():
    recipes = []
    if request.method == 'POST':
        user_ingredients = request.form.get('ingredients', '').lower().split(', ')
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
                'cooking_time': recipe['cooking_time']
            })

    #sort recipes by most matched ingredients with leasr missing ingredients
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

if __name__ == '__main__':
    app.run(debug=True)




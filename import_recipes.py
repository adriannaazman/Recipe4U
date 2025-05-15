import sqlite3
import csv
import ast

conn = sqlite3.connect('recipes.db')
c = conn.cursor()

with open('recipes.csv', 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        
        ingredients_raw = row['RecipeIngredientParts']
        try:
            ingredients_list = ast.literal_eval(ingredients_raw.replace('c(', '[').replace(')', ']'))
            ingredients = ', '.join(ingredients_list)
        except:
            ingredients = ingredients_raw  

        c.execute('''
            INSERT INTO recipes (id, name, description, ingredients, difficulty, meal_type, diet, prep_time, link)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            row['RecipeId'],
            row['Name'],
            row['Description'],
            ingredients,             
            "Medium",                
            row['RecipeCategory'],
            row['Keywords'],
            row['PrepTime'],
            row['Images']            
        ))

conn.commit()
conn.close()



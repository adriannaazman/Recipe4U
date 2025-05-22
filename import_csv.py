import sqlite3
import csv

conn = sqlite3.connect("recipes_database.db")
c = conn.cursor()

with open("recipes_full_steps.csv", newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        c.execute('''
            INSERT INTO recipes (name, ingredients, meal_type, diet, cooking_time, steps, image_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            row['name'],
            row['ingredients'],
            row['meal_type'],
            row['diet'],
            int(row['cooking_time']) if row['cooking_time'].isdigit() else 0,
            row['steps'],
            row['image_url']
        ))

conn.commit()
conn.close()
print("Recipes imported successfully.")






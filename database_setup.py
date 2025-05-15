import sqlite3

conn = sqlite3.connect('recipes.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY,
    name TEXT,
    author_id INTEGER,
    author_name TEXT,
    cook_time TEXT,
    prep_time TEXT,
    total_time TEXT,
    date_published TEXT,
    description TEXT,
    images TEXT,
    category TEXT,
    keywords TEXT,
    ingredient_quantities TEXT,
    ingredient_parts TEXT,
    rating REAL,
    review_count INTEGER,
    calories REAL,
    fat REAL,
    saturated_fat REAL,
    cholesterol REAL,
    sodium REAL,
    carbohydrate REAL,
    fiber REAL,
    sugar REAL,
    protein REAL,
    servings INTEGER,
    recipe_yield TEXT,
    instructions TEXT
)
''')

conn.commit()
conn.close()



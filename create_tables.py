import sqlite3

conn = sqlite3.connect('recipes_databases.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    ingredients TEXT NOT NULL,
    meal_type TEXT,
    diet TEXT,
    cooking_time INTEGER,
    steps TEXT,
    image_url TEXT
)
''')

# TODO: You can create other tables here too, like users, comments, etc.

print("Database and tables created successfully.")

conn.commit()
conn.close()


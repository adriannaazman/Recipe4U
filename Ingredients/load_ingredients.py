import sqlite3
import json
import os

# Path to main.db
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, '..', 'database', 'main.db')

# Connect to main.db
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Create table for ingredients
c.execute('''
    CREATE TABLE IF NOT EXISTS ingredients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        quantity INTEGER DEFAULT 0
    )
''')

# Load ingredients from JSON file
with open('Ingredients/ingredients.json', 'r') as f:
    data = json.load(f)

# Insert ingredients into ingredients.db
for item in data:
    name = item['name']
    option = ", ".join(item.get("option", []))  # Handle list as text

    try:
        c.execute("INSERT INTO ingredients (name, description) VALUES (?, ?)", (name, option))
    except sqlite3.IntegrityError:
        continue  # Skip duplicates if name already exists

conn.commit()
conn.close()

print("✅ Ingredients successfully saved into ingredients.db!")

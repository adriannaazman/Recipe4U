import sqlite3
import os

db_path = 'recipes.db'
print(f"Checking database at: {os.path.abspath(db_path)}")

# Connect to database
conn = sqlite3.connect(db_path)
c = conn.cursor()

# List all tables
print("Available tables in the database:")
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = c.fetchall()
print(tables)

# If 'recipes' exists, print column info
if ('recipes',) in tables:
    print("\n'recipes' table structure:")
    c.execute("PRAGMA table_info(recipes)")
    columns = c.fetchall()
    for col in columns:
        print(col)
else:
    print("\n'recipes' table not found.")

conn.close()


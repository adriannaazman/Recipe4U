# database/setup.py

import sqlite3
import os

# Make sure the database folder exists
if not os.path.exists("database"):
    os.makedirs("database")

# Path to main.db
db_path = os.path.join("database", "main.db")

def create_db():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Create users table
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
''')

    conn.commit()
    conn.close()
    print("✅ Database created successfully at", db_path)

# Run this script directly
if __name__ == "__main__":
    create_db()
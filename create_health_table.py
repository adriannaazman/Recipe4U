import sqlite3

conn = sqlite3.connect('main.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS health_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    age INTEGER,
    weight REAL,
    height REAL,
    activity_level TEXT
)
''')

conn.commit()
conn.close()
print("✅ health_profile table created successfully.")

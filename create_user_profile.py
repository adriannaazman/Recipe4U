import sqlite3

conn = sqlite3.connect('user.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_profile (
        user_id INTEGER PRIMARY KEY,
        age INTEGER,
        gender TEXT,
        height_cm REAL,
        weight_kg REAL,
        activity_level TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
''')

conn.commit()
conn.close()

print("✅ user_profile table created successfully.")
import sqlite3
import os  


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "database", "user.db")

conn = sqlite3.connect(db_path)
c = conn.cursor()

# View all users
c.execute("SELECT * FROM users")
users = c.fetchall()

for user in users:
    print(user)

conn.close()
import sqlite3

conn = sqlite3.connect('database/user.db')
c = conn.cursor()

c.execute("SELECT * FROM users")  # assuming your table is called users
rows = c.fetchall()

for row in rows:
    print(row)

conn.close()
import sqlite3

# Make sure this path matches your actual database file
conn = sqlite3.connect('user.db')  # Or your actual db_path
cursor = conn.cursor()

cursor.execute("DELETE FROM users")  # This deletes all users

conn.commit()
conn.close()

print("✅ Old users removed.")
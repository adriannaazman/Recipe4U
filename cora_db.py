import sqlite3

def create_comments_table():
    conn = sqlite3.connect('recipes_database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER,
            username TEXT,
            comment TEXT,
            rating INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(recipe_id) REFERENCES recipes(id)
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_comments_table()
    print("Comments table created.")

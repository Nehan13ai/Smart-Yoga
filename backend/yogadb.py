import sqlite3

def init_db():
    """Initializes the database and creates the users table if it doesn't exist."""
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        print("Database initialized and 'users' table is ready.")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    # This allows you to run 'python yogadb.py' from the terminal to create the DB
    init_db()
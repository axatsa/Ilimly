
import sqlite3
import logging

def setup_db():
    """
    Creates or updates the user_data database with the required schema.
    This function is safe to run multiple times - it will only create
    the table if it doesn't already exist.
    """
    try:
        # Connect to the SQLite database (creates it if it doesn't exist)
        conn = sqlite3.connect('user_data.db')
        cursor = conn.cursor()
        
        # Create the user_data table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_data (
            user_id INTEGER PRIMARY KEY,
            chosen_language TEXT(10) NOT NULL
        )
        ''')
        
        # Commit the changes and close the connection
        conn.commit()
        print("Database setup completed successfully!")
        
        # Log the number of existing users
        cursor.execute("SELECT COUNT(*) FROM user_data")
        user_count = cursor.fetchone()[0]
        print(f"Current number of users in database: {user_count}")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    setup_db()

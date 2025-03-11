
import sqlite3

def view_database():
    try:
        # Подключение к базе данных SQLite
        conn = sqlite3.connect('user_data.db')
        cursor = conn.cursor()
        
        # Получение всех записей из таблицы user_data
        cursor.execute("SELECT * FROM user_data")
        rows = cursor.fetchall()
        
        print("База данных user_data.db содержит следующие записи:")
        print("user_id | chosen_language")
        print("-" * 30)
        
        for row in rows:
            print(f"{row[0]} | {row[1]}")
        
        # Подсчет общего количества пользователей
        cursor.execute("SELECT COUNT(*) FROM user_data")
        count = cursor.fetchone()[0]
        print(f"\nВсего пользователей: {count}")
        
    except sqlite3.Error as e:
        print(f"Ошибка базы данных: {e}")
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    view_database()

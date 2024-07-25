import sqlite3
from datetime import datetime
import pandas as pd

# Путь к исходной базе данных
source_db_path = '/home/user/DB/serversgta5rp/Blackberry_roulette_data.db'
# Путь к новой базе данных
target_db_path = '/home/user/DB/serversgta5rp/New_roulette_data.db'
# Путь к CSV-файлу
csv_path = '/home/user/DB/serversgta5rp/New_roulette_data.csv'

# Функция для создания новой базы данных
def create_new_db():
    conn = sqlite3.connect(target_db_path)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS roulette_numbers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        number TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        hour INTEGER,
        minute INTEGER,
        day_of_week INTEGER,
        is_weekend INTEGER,
        username TEXT NOT NULL,
        session_id INTEGER
    );
    ''')
    conn.commit()
    conn.close()

# Функция для переноса данных из старой базы данных в новую
def transfer_data():
    source_conn = sqlite3.connect(source_db_path)
    source_cursor = source_conn.cursor()

    target_conn = sqlite3.connect(target_db_path)
    target_cursor = target_conn.cursor()

    # Перенос данных из старой базы данных
    source_cursor.execute('SELECT number, timestamp FROM roulette_numbers')
    rows = source_cursor.fetchall()

    data = []
    session_id_counter = 1

    for row in rows:
        number, timestamp = row
        dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        hour = dt.hour
        minute = dt.minute
        day_of_week = dt.weekday()
        is_weekend = 1 if day_of_week >= 5 else 0
        session_id = session_id_counter

        if len(data) > 0 and data[-1][1].split(" ")[0] != timestamp.split(" ")[0]:
            session_id_counter += 1
            session_id = session_id_counter

        data.append((number, timestamp, hour, minute, day_of_week, is_weekend, 'MrJin', session_id))

        target_cursor.execute('''
        INSERT INTO roulette_numbers (number, timestamp, hour, minute, day_of_week, is_weekend, username, session_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (number, timestamp, hour, minute, day_of_week, is_weekend, 'MrJin', session_id))

    target_conn.commit()
    source_conn.close()
    target_conn.close()

    return data

# Функция для экспорта данных в CSV
def export_to_csv(data):
    df = pd.DataFrame(data, columns=['number', 'timestamp', 'hour', 'minute', 'day_of_week', 'is_weekend', 'username', 'session_id'])
    df.to_csv(csv_path, index=False)

# Создание новой базы данных и перенос данных
create_new_db()
data = transfer_data()
export_to_csv(data)

print("База данных перенесена в новый файл и конвертирована в  CSV.")

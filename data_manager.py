import sqlite3
from datetime import datetime
import os
import pandas as pd

DATABASE_PATH = "/home/user/DB/serversgta5rp"

def connect_db(server_name):
    if server_name is None:
        raise ValueError("Server name must not be None")
    database_filename = f"{server_name}_roulette_data.db"
    absolute_path = os.path.join(DATABASE_PATH, database_filename)
    conn = sqlite3.connect(absolute_path)
    return conn

def create_tables(server_name):
    conn = connect_db(server_name)
    cursor = conn.cursor()
    try:
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS roulette_numbers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            hour INTEGER,
            minute INTEGER,
            day_of_week INTEGER,
            username TEXT DEFAULT 'AI'
        );
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS guessed_numbers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number TEXT NOT NULL,
            username TEXT NOT NULL,
            timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        ''')
        conn.commit()

        cursor.execute("PRAGMA table_info(roulette_numbers)")
        columns = [info[1] for info in cursor.fetchall()]
        if 'hour' not in columns:
            cursor.execute("ALTER TABLE roulette_numbers ADD COLUMN hour INTEGER")
        if 'minute' not in columns:
            cursor.execute("ALTER TABLE roulette_numbers ADD COLUMN minute INTEGER")
        if 'day_of_week' not in columns:
            cursor.execute("ALTER TABLE roulette_numbers ADD COLUMN day_of_week INTEGER")
        if 'username' not in columns:
            cursor.execute("ALTER TABLE roulette_numbers ADD COLUMN username TEXT DEFAULT 'AI'")
        conn.commit()
    except Exception as e:
        print(f"Ошибка при создании таблиц: {e}")
    finally:
        conn.close()

def insert_roulette_number(server_name, number, username='AI'):
    conn = connect_db(server_name)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    hour = datetime.now().hour
    minute = datetime.now().minute
    day_of_week = datetime.now().weekday()
    number_str = "00" if number == "00" else number
    cursor.execute('''
        INSERT INTO roulette_numbers (number, timestamp, hour, minute, day_of_week, username)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (number_str, timestamp, hour, minute, day_of_week, username))
    conn.commit()
    conn.close()

def get_all_numbers_with_timestamp(server_name):
    conn = connect_db(server_name)
    cursor = conn.cursor()
    cursor.execute('SELECT number, timestamp, hour, minute, day_of_week FROM roulette_numbers')
    numbers = cursor.fetchall()
    conn.close()
    return [{'number': n[0], 'timestamp': n[1], 'hour': n[2], 'minute': n[3], 'day_of_week': n[4]} for n in numbers]

def get_following_numbers(server_name, target_number):
    conn = connect_db(server_name)
    cursor = conn.cursor()
    cursor.execute('''
        WITH RankedNumbers AS (
            SELECT number, LEAD(number) OVER (ORDER BY id ASC) AS next_number
            FROM roulette_numbers
        )
        SELECT next_number FROM RankedNumbers
        WHERE number = ? AND next_number IS NOT NULL
    ''', (str(target_number),))
    numbers = cursor.fetchall()
    conn.close()
    filtered_numbers = [num[0] for num in numbers if num[0] is not None]

    if not filtered_numbers:
        return [], False
    return filtered_numbers, True

def get_guessed_history(server_name):
    conn = connect_db(server_name)
    cursor = conn.cursor()
    cursor.execute("SELECT number, username FROM guessed_numbers ORDER BY timestamp DESC LIMIT 5")
    history = cursor.fetchall()
    conn.close()
    return [{'number': row[0], 'predictor': row[1]} for row in history]

def add_guessed_number(server_name, number, username):
    conn = connect_db(server_name)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO guessed_numbers (number, username) VALUES (?, ?)", (number, username))
    cursor.execute("DELETE FROM guessed_numbers WHERE id NOT IN (SELECT id FROM guessed_numbers ORDER BY timestamp DESC LIMIT 5)")
    conn.commit()
    conn.close()

def cancel_and_get_previous_entry(server_name):
    try:
        conn = connect_db(server_name)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM roulette_numbers ORDER BY id DESC LIMIT 1')
        last_entry = cursor.fetchone()
        if last_entry:
            last_entry_id = last_entry[0]
            cursor.execute('SELECT number FROM roulette_numbers WHERE id < ? ORDER BY id DESC LIMIT 1', (last_entry_id,))
            previous_entry = cursor.fetchone()
            cursor.execute('DELETE FROM roulette_numbers WHERE id = ?', (last_entry_id,))
            conn.commit()
            if previous_entry:
                return True, previous_entry[0]
            else:
                return True, None
    except Exception as e:
        print(f"An error occurred: {e}")
        return False, None
    finally:
        cursor.close()
        conn.close()

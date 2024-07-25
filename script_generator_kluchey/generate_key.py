# Не запускать скрипт


import sqlite3
import random
import string

# Функция для генерации ключа
def generate_key():
    parts = []
    for _ in range(4):
        part = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
        parts.append(part)
    return '-'.join(parts)

# Создание базы данных и таблицы
db_path = '/home/user/DB/key/subscribe_key.db test'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS subscription_keys (
    id INTEGER PRIMARY KEY,
    key TEXT NOT NULL,
    duration_days INTEGER NOT NULL,
    is_activated INTEGER DEFAULT 0,
    user_name TEXT,
    activation_date TEXT
)
''')

# Словарь для количества ключей по срокам действия
durations = {
    1: 1000,
    7: 1000,
    14: 2500,
    30: 5500,
    60: 1000,
    90: 1000,
    180: 1000,
    365: 1000,
    -1: 50  # Вечные ключи
}

# Генерация и добавление ключей в базу данных
for days, count in durations.items():
    for _ in range(count):
        key = generate_key()
        # Для вечных ключей устанавливаем значение -1
        duration_days = 99999 if days == -1 else days
        cursor.execute('INSERT INTO subscription_keys (key, duration_days) VALUES (?, ?)', (key, duration_days))

conn.commit()
conn.close()
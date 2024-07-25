import sqlite3
import csv

# Путь к файлу базы данных
db_path = '/home/user/DB/key/subscribe_key.db'
# Определение пути к файлу CSV (такое же название, как у базы данных, но с расширением .csv)
csv_path = db_path.replace('.db', '.csv')

# Подключение к базе данных
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Выполнение запроса для выбора всех данных из таблицы
cursor.execute('SELECT * FROM subscription_keys')
rows = cursor.fetchall()

# Сохранение данных в файл CSV
with open(csv_path, 'w', newline='', encoding='utf-8') as csv_file:
    csv_writer = csv.writer(csv_file)
    # Обновляем заголовки столбцов согласно новой структуре
    csv_writer.writerow(['ID', 'Key', 'Duration Days', 'Is Activated', 'User Name', 'Activation Date'])
    # Запись данных
    csv_writer.writerows(rows)

# Закрытие соединения с базой данных
conn.close()

print(f'Данные успешно сохранены в файл: {csv_path}')
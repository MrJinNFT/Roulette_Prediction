import sqlite3
import pandas as pd
import os

DATABASE_PATH = "/home/user/DB/serversgta5rp"

def get_server_data(database_file):
    conn = sqlite3.connect(os.path.join(DATABASE_PATH, database_file))
    df = pd.read_sql_query("SELECT * FROM roulette_numbers", conn)
    conn.close()
    return df

def clean_data(df):
    df['timestamp'] = pd.to_datetime(df['timestamp'])  # Преобразование timestamp в datetime
    df['day_of_week'] = df['timestamp'].dt.dayofweek  # Добавление day_of_week на основе timestamp
    df['hour'] = df['timestamp'].dt.hour
    df['minute'] = df['timestamp'].dt.minute
    
    # Удаление строк с пропущенными значениями только в критически важных столбцах
    df.dropna(subset=['number', 'timestamp'], inplace=True)
    
    # Удаление дубликатов
    df.drop_duplicates(inplace=True)

    return df

def prepare_data(server_name):
    data = get_server_data(f"{server_name}_roulette_data.db")
    cleaned_data = clean_data(data)
    
    if cleaned_data.empty:
        print("Недостаточно данных для обработки.")
        return None
    else:
        cleaned_data_path = os.path.join('/home/user/DB/model/cleaned_data', f'{server_name}_cleaned_data.csv')
        os.makedirs(os.path.dirname(cleaned_data_path), exist_ok=True)
        cleaned_data.to_csv(cleaned_data_path, index=False)
        print(f"Очищенные данные сохранены в {cleaned_data_path}")
        return cleaned_data_path

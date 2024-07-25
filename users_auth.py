import sqlite3
from datetime import datetime, timedelta

DATABASE_SUBSCRIPTION_KEYS = "/home/user/DB/key/subscribe_key.db"

def get_db_connection(db_file):
    return sqlite3.connect(db_file)

def check_subscription(user_id):
    with get_db_connection(DATABASE_SUBSCRIPTION_KEYS) as conn:
        cur = conn.cursor()
        cur.execute('SELECT activation_date, duration_days FROM subscription_keys WHERE user_name = ? AND is_activated = 1 ORDER BY activation_date DESC LIMIT 1', 
                    (str(user_id),))
        result = cur.fetchone()
        if result:
            activation_date, duration_days = result
            activation_date = datetime.strptime(activation_date, "%Y-%m-%d %H:%M:%S")
            if datetime.now() <= activation_date + timedelta(days=duration_days):
                return True
        return False

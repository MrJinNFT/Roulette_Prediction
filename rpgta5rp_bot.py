import telebot
import sqlite3
from datetime import datetime, timedelta
from config import API_TOKEN, ADMIN_PASSWORD

bot = telebot.TeleBot(API_TOKEN)

DATABASE_SUBSCRIPTION_KEYS = "/home/user/DB/key/subscribe_key.db"

def get_db_connection(db_file):
    return sqlite3.connect(db_file)

# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    username = message.from_user.username if message.from_user.username else "друг"
    welcome_message = f"""
    <b>Привет, @{username}!</b>

    Я здесь, чтобы сделать твой опыт ещё лучше! Вот что я могу предложить:

    - 🔮 <b>/predict</b> - Предсказать в 1 клик: Нажми и узнай свою удачу!
    - 🔑 <b>/subscription</b> - Активировать подписку: Введи свой ключ подписки.
    - 📈 <b>/status</b> - Проверить статус и информацию о подписке.
    - ❓ <b>/help</b> - Получить информацию о командах.

    Не забудь подписаться на наш канал для получения последних обновлений и специальных предложений!
    """
    markup = telebot.types.InlineKeyboardMarkup()
    button_group = telebot.types.InlineKeyboardButton(text="Присоединиться к группе", url="https://t.me/+ivgTss3rnQQ2Nzgy")
    markup.add(button_group)
    bot.send_message(message.chat.id, welcome_message, reply_markup=markup, parse_mode='HTML')

# Команда /predict
@bot.message_handler(commands=['predict'])
def send_launch_button(message):
    try:
        user_id = message.from_user.id
        is_active, _, _, _ = check_subscription(user_id)
        if is_active:
            markup = telebot.types.InlineKeyboardMarkup()
            button = telebot.types.InlineKeyboardButton(
                text="Запустить приложение", 
                url="https://t.me/rpgta5rp_bot/roulette_prediction"
            )
            markup.add(button)
            bot.send_message(
                message.chat.id, 
                "Нажмите кнопку ниже, чтобы запустить приложение:",
                reply_markup=markup
            )
        else:
            bot.send_message(message.chat.id, "Ваша подписка истекла или не активирована. Используйте /subscription для активации.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Произошла ошибка: {str(e)}")

# Команда /subscription
@bot.message_handler(commands=['subscription'])
def handle_subscription(message):
    bot.send_message(message.chat.id, "Пожалуйста, отправьте ключ подписки для активации:")
    bot.register_next_step_handler(message, activate_subscription)

def activate_subscription(message):
    key = message.text
    user_id = message.from_user.id
    if activate_key(key, user_id):
        bot.send_message(message.chat.id, "Ключ активирован! Теперь вы можете использовать /predict для запуска приложения.")
    else:
        bot.send_message(message.chat.id, "Ключ недействителен или уже активирован.")

def activate_key(key, user_id):
    with get_db_connection(DATABASE_SUBSCRIPTION_KEYS) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM subscription_keys WHERE key = ? AND is_activated = 0', (key,))
        if cursor.fetchone():
            cursor.execute('UPDATE subscription_keys SET is_activated = 1, user_name = ?, activation_date = ? WHERE key = ?', (str(user_id), datetime.now().strftime('%Y-%m-%d %H:%M:%S'), key))
            conn.commit()
            return True
    return False

def check_subscription(user_id):
    with get_db_connection(DATABASE_SUBSCRIPTION_KEYS) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT key, activation_date, duration_days FROM subscription_keys WHERE user_name = ? AND is_activated = 1 ORDER BY activation_date DESC LIMIT 1', (str(user_id),))
        result = cursor.fetchone()
        if result:
            key, activation_date, duration_days = result
            activation_date = datetime.strptime(activation_date, '%Y-%m-%d %H:%M:%S')
            if datetime.now() <= activation_date + timedelta(days=duration_days):
                remaining_days = (activation_date + timedelta(days=duration_days) - datetime.now()).days
                return True, key, activation_date.strftime('%Y-%m-%d'), remaining_days
    return False, None, None, 0

# Команда /status
@bot.message_handler(commands=['status'])
def send_subscription_status(message):
    user_id = message.from_user.id
    is_active, key, activation_date, remaining_days = check_subscription(user_id)
    if is_active:
        bot.reply_to(message, f"Ваш ключ подписки: {key}\nАктивировано: {activation_date}\nОсталось дней подписки: {remaining_days}")
    else:
        bot.reply_to(message, "У вас нет активной подписки.")

# Команда /help
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
Команды:
/start - Приветственное сообщение.
/predict - Запустить приложение (только для активных подписок).
/subscription - Активировать подписку.
/status - Проверить статус подписки.
/help - Эта справка.
"""
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['admin'])
def admin_login(message):
    msg = bot.reply_to(message, "Введите пароль администратора:")
    bot.register_next_step_handler(msg, admin_password_check)

def admin_password_check(message):
    if message.text == ADMIN_PASSWORD:
        bot.send_message(message.chat.id, "Пароль верный. Вот список активированных ключей:")
        show_activated_keys(message)
        bot.send_message(message.chat.id, "Для аннулирования ключа отправьте его в формате: /revoke ключ")
    else:
        bot.send_message(message.chat.id, "Неверный пароль.")

def show_activated_keys(message):
    with get_db_connection(DATABASE_SUBSCRIPTION_KEYS) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT key, user_name, activation_date, duration_days FROM subscription_keys WHERE is_activated = 1 LIMIT 10')
        keys = cursor.fetchall()
        if keys:
            response = "Активированные ключи:\n"
            for key, user_name, activation_date, duration_days in keys:
                response += f"Ключ: {key}, Пользователь: {user_name}, Активация: {activation_date}, Срок: {duration_days} дней\n"
            bot.send_message(message.chat.id, response)
        else:
            bot.send_message(message.chat.id, "Активированных ключей нет.")

@bot.message_handler(commands=['revoke'])
def revoke_key(message):
    if not message.text.startswith("/revoke "):
        bot.send_message(message.chat.id, "Неверный формат команды. Используйте: /revoke ключ")
        return
    key_to_revoke = message.text.split(" ", 1)[1]
    with get_db_connection(DATABASE_SUBSCRIPTION_KEYS) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE subscription_keys SET is_activated = 0, user_name = NULL, activation_date = NULL WHERE key = ?', (key_to_revoke,))
        if cursor.rowcount > 0:
            conn.commit()
            bot.send_message(message.chat.id, f"Ключ {key_to_revoke} аннулирован и теперь доступен для активации.")
        else:
            bot.send_message(message.chat.id, "Ключ не найден или уже аннулирован.")

# Запуск бота
bot.polling()

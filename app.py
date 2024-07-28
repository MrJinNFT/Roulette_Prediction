import csv
from datetime import datetime
import os
import logging
from flask import Flask, request, jsonify, redirect, session, url_for, render_template
from prediction_engine import PredictionEngine
from data_manager import cancel_and_get_previous_entry, create_tables, insert_roulette_number, get_guessed_history, add_guessed_number

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Инициализация PredictionEngine
engine = PredictionEngine()

@app.route('/')
def index():
    logging.debug('Rendering index.html')
    return render_template('index.html', username=session.get('username', ''))

@app.route('/predicts')
def predicts():
    selected_server = request.args.get('server')
    username = request.args.get('username')
    if selected_server and username:
        create_tables(selected_server)
        logging.debug(f'Server: {selected_server}, Username: {username}')
        return render_template('predicts.html', server=selected_server, username=username)
    else:
        logging.debug('Redirecting to index')
        return redirect(url_for('index'))

@app.route('/predict', methods=['POST'])
def predict():
    selected_server = request.form.get('server')
    number = request.form.get('number')
    username = request.form.get('username')

    if not selected_server or not number or not username:
        logging.error('Missing required parameters')
        return jsonify({'error': 'Server name, number and username are required'}), 400

    try:
        predictions = engine.combined_predictions(selected_server, int(number))
        insert_roulette_number(selected_server, number, username)

        # Проверка на совпадение предсказанного числа с введенным числом
        for prediction in predictions['number_predictions']:
            if prediction['number'] == number:
                source = 'AI' if 'source' in prediction and prediction['source'] == 'AI' else 'User'
                add_guessed_number(selected_server, number, username, source)
                break

        guessed_history = get_guessed_history(selected_server)
        return jsonify(predictions=predictions, guessed_history=guessed_history)
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return jsonify({'error': str(e)}), 400
    
def log_guessed_number_to_file(number, username, server, source):
    log_filename = "guessed_numbers_log.csv"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, username, number, server, source])    

@app.route('/guessed', methods=['POST'])
def guessed():
    number = request.form.get('number')
    username = request.form.get('username')
    server = request.form.get('server')
    source = request.form.get('source', 'User')

    if not number or not username or not server:
        return jsonify({'error': 'Number, username and server are required'}), 400

    try:
        add_guessed_number(server, number, username, source)
        guessed_history = get_guessed_history(server)
        return jsonify(guessed_history)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/update_last_number', methods=['POST'])
def update_last_number():
    number = request.form.get('number')
    username = request.form.get('username')
    server = request.form.get('server')

    if not number or not username or not server:
        return jsonify({'error': 'Number, username, and server are required'}), 400

    try:
        insert_roulette_number(server, number, username)
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"An error occurred while updating the last number: {str(e)}")
        return jsonify({'error': str(e)}), 400

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/user_guide')
def user_guide():
    return render_template('user_guide.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/cancel_last_entry', methods=['POST'])
def cancel_last_entry():
    server_name = request.form.get('server')
    if not server_name:
        return jsonify({"status": "error", "message": "Необходимо указать сервер."})
    
    success, previous_number = cancel_and_get_previous_entry(server_name)
    if success:
        return jsonify({"status": "success", "previous_number": previous_number})
    else:
        return jsonify({"status": "error", "message": "Не удалось отменить последний ввод."})

@app.after_request
def add_header(response):
    response.cache_control.no_store = True
    response.cache_control.must_revalidate = True
    response.cache_control.max_age = 0
    response.expires = 0
    response.pragma = 'no-cache'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

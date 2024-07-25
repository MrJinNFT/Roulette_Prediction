import os
from flask import Flask, request, jsonify, redirect, url_for, render_template, session
from prediction_engine import PredictionEngine
from data_manager import cancel_and_get_previous_entry, create_tables, insert_number

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Инициализация PredictionEngine
engine = PredictionEngine()

@app.route('/')
def index():
    return render_template('index.html', username=session.get('username', ''))

@app.route('/predicts')
def predicts():
    selected_server = request.args.get('server')
    username = request.args.get('username')
    if selected_server:
        create_tables(selected_server)
        session['username'] = username
        return render_template('predicts.html', server=selected_server, username=username)
    else:
        return redirect(url_for('index'))

@app.route('/predict', methods=['POST'])
def predict():
    selected_server = request.form.get('server')
    number = request.form.get('number')
    username = request.form.get('username', 'AI')

    if not selected_server or not number:
        return jsonify({'error': 'Server name and number are required'}), 400

    try:
        predictions = engine.combined_predictions(selected_server, int(number))
        insert_number(selected_server, number, username)
        return jsonify(predictions=predictions)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
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

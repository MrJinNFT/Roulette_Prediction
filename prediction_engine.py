import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from collections import Counter
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import logging

# Импорт функций из data_manager
from data_manager import get_all_numbers_with_timestamp, get_following_numbers, insert_roulette_number

class PredictionEngine:
    def __init__(self):
        self.models = {}

    def train_model(self, server_name):
        data = self.prepare_data(server_name)
        X = data[['previous_number', 'hour', 'minute', 'day_of_week']].values
        y = data['current_number'].values

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        accuracy = accuracy_score(y_test, model.predict(X_test))
        logging.info(f"Accuracy for {server_name}: {accuracy}")

        self.models[server_name] = model

    def prepare_data(self, server_name):
        all_numbers = get_all_numbers_with_timestamp(server_name)
        data = {
            'previous_number': [],
            'current_number': [],
            'hour': [],
            'minute': [],
            'day_of_week': []
        }

        for i in range(1, len(all_numbers)):
            previous_number = all_numbers[i - 1]['number']
            current_number = all_numbers[i]['number']
            timestamp = pd.Timestamp(all_numbers[i]['timestamp'])
            data['previous_number'].append(previous_number)
            data['current_number'].append(current_number)
            data['hour'].append(timestamp.hour)
            data['minute'].append(timestamp.minute)
            data['day_of_week'].append(timestamp.dayofweek)

        return pd.DataFrame(data)

    def historical_predictions(self, server_name, current_number):
        all_numbers = get_all_numbers_with_timestamp(server_name)
        recent_numbers = [entry['number'] for entry in all_numbers if pd.Timestamp(entry['timestamp']) > (datetime.now() - timedelta(days=30))]
        following_numbers, data_sufficient = get_following_numbers(server_name, current_number)

        if not data_sufficient:
            return [{"number": "Мало данных для предсказания", "probability": "0%"}]

        total_counts = sum([count for number, count in Counter(following_numbers).items()])
        predictions = []

        if total_counts > 0:
            counter = Counter(following_numbers)
            most_common = [num for num, count in counter.most_common() if count >= 3]
            latest_numbers = list(dict.fromkeys(reversed(recent_numbers)))

            latest_predictions = [num for num in latest_numbers if following_numbers.count(num) >= 3][:3]
            most_common_predictions = [num for num in most_common if num not in latest_predictions][:3]

            combined_predictions = most_common_predictions + latest_predictions

            for num in combined_predictions:
                count = following_numbers.count(num)
                probability = round((count / total_counts) * 100, 2)
                prediction = {'number': num, 'probability': f"{probability}%"}

                if current_number == num:
                    prediction['dubl'] = True
                predictions.append(prediction)
        else:
            return [{"number": "Мало данных для предсказания", "probability": "0%"}]

        return predictions[:6]

    def combined_predictions(self, server_name, current_number):
        try:
            historical_predictions = self.historical_predictions(server_name, current_number)
            model_predictions = self.model_based_predictions(server_name, current_number)

            # Берем 3 предсказания от исторических данных и 3 от модели
            combined_predictions = historical_predictions[:3] + model_predictions[:3]

            # Логирование предсказаний
            logging.debug(f"Combined Predictions: {combined_predictions}")

            return combined_predictions
        except Exception as e:
            logging.error(f"An error occurred in combined_predictions: {str(e)}")
            return [{"number": "Error", "probability": "0%"}]

    def model_based_predictions(self, server_name, current_number):
        model = self.models.get(server_name)
        if not model:
            self.train_model(server_name)
            model = self.models[server_name]

        data = self.prepare_data_for_prediction(current_number)
        probabilities = model.predict_proba(data)[0]

        # Убедимся, что модель возвращает все вероятности от 0 до 36
        prediction_list = []
        for i in range(len(probabilities)):
            if i <= 36:  # Убедимся, что предсказанные числа в диапазоне 0-36
                prediction_list.append({
                    'number': str(i),  # Assuming class labels are numbers 0-36
                    'probability': f"{probabilities[i] * 100:.2f}%",
                    'source': 'AI'
                })

        # Логирование предсказаний модели
        logging.debug(f"Model Predictions: {prediction_list}")

        # Сортировка по вероятности и выбор топ-3 предсказаний
        prediction_list.sort(key=lambda x: float(x['probability'].strip('%')), reverse=True)
        return prediction_list[:3]

    def prepare_data_for_prediction(self, current_number):
        timestamp = pd.Timestamp.now()
        return np.array([[current_number, timestamp.hour, timestamp.minute, timestamp.dayofweek]])

    def update_with_latest_number(self, server_name, number, username='AI'):
        insert_roulette_number(server_name, number, username)

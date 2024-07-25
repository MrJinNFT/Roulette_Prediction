from collections import Counter
from data_manager import get_following_numbers, get_all_numbers, insert_roulette_number

class PredictionEngine:
    def __init__(self):
        self.predicted_numbers = []

    def historical_predictions(self, server_name, current_number):
        following_numbers, data_sufficient = get_following_numbers(server_name, current_number)
        all_numbers = get_all_numbers(server_name)

        if not data_sufficient:
            return [{"number": "Мало данных для предсказания", "probability": "0%"}]

        total_counts = sum([count for number, count in Counter(following_numbers).items()])
        predictions = []

        if total_counts > 0:
            counter = Counter(following_numbers)
            most_common = [num for num, count in counter.most_common() if count >= 3]
            latest_numbers = list(dict.fromkeys(reversed(all_numbers)))

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
            last_two_numbers = get_all_numbers(server_name)[-2:]

            filtered_predictions = [
                pred for pred in historical_predictions
                if not (pred['number'] == last_two_numbers[-1] and pred['number'] == last_two_numbers[-1])
            ]

            return filtered_predictions
        except Exception as e:
            print(f"An error occurred in combined_predictions: {str(e)}")
            return [{"number": "Error", "probability": "0%"}]

if __name__ == "__main__":
    print("Prediction Engine module")

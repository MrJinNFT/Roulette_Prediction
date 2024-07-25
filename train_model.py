import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from joblib import dump
import os

def load_data(file_path):
    return pd.read_csv(file_path)

def create_model():
    numeric_features = ['hour', 'minute', 'day_of_week', 'is_weekend', 'session_id']
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features)
        ]
    )
    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', XGBClassifier(random_state=42))
    ])
    return model

def train_model(data, server_name):
    X = data[['hour', 'minute', 'day_of_week', 'is_weekend', 'session_id']]
    y = data['number']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = create_model()

    param_distributions = {
        'classifier__n_estimators': [50, 100],
        'classifier__learning_rate': [0.01, 0.1],
        'classifier__max_depth': [3, 5]
    }

    randomized_search = RandomizedSearchCV(model, param_distributions, cv=2, n_iter=10, n_jobs=-1, verbose=2)
    randomized_search.fit(X_train, y_train)

    print("Лучшие параметры: ", randomized_search.best_params_)
    print("Лучшая точность: ", randomized_search.best_score_)

    best_model = randomized_search.best_estimator_
    print("Точность на тестовых данных: ", best_model.score(X_test, y_test))

    model_path = f'/home/user/DB/model/trained_model/{server_name}_trained_model.pkl'
    dump(best_model, model_path)
    print(f"Обученная модель сохранена в {model_path}")

    return best_model

def main(server_name):
    cleaned_data_path = f"/home/user/DB/model/cleaned_data/{server_name}_cleaned_data.csv"
    if os.path.exists(cleaned_data_path):
        data = load_data(cleaned_data_path)
        train_model(data, server_name)
    else:
        print(f"Файл очищенных данных {cleaned_data_path} не найден.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        print("Имя сервера не указано.")

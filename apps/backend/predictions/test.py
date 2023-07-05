import os
import pickle
import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.preprocessing.sequence import TimeseriesGenerator
from sklearn.preprocessing import MinMaxScaler
from apps.backend.database import Question, Tag
from apps import config
from datetime import datetime, timedelta
import matplotlib.pyplot as plt


# Fetch the data from the database
def get_data_from_db():
    config.initiate_connection()

    ten_days_ago = datetime.now() - timedelta(days=10)
    data = []

    for tag in Tag.objects().order_by('-tags_length')[:1]:
        tag_questions = Question.objects(tags=tag.tag_name, creation_date__lte=ten_days_ago)
        for question in tag_questions:
            data.append({
                "tag": tag.tag_name,
                "date": question.creation_date.date(),
            })

    data_df = pd.DataFrame(data)
    return data_df


# Prepare the data for LSTM model
def prepare_data_for_lstm(data_df):
    prepared_data = {}

    for tag in data_df['tag'].unique():
        tag_data = data_df[data_df['tag'] == tag].groupby('date').size()
        tag_data = tag_data.values.astype('float32').reshape(-1, 1)

        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(tag_data)

        prepared_data[tag] = (scaled_data, scaler)

    return prepared_data


# Train the LSTM model
def train_model_lstm(data, look_back=1):
    models = {}

    for tag, (tag_data, scaler) in data.items():
        train_size = int(len(tag_data) * 0.80)
        train, test = tag_data[0:train_size], tag_data[train_size:len(tag_data)]
        train_gen = TimeseriesGenerator(train, train, length=look_back, batch_size=1)

        model = Sequential()
        model.add(LSTM(4, input_shape=(1, look_back)))
        model.add(Dense(1))
        model.compile(loss='mean_squared_error', optimizer='adam')

        model.fit(train_gen, epochs=10, verbose=2)

        models[tag] = (model, scaler)

    return models


# Save the LSTM models
def save_models_lstm(models):
    dir_path = 'tag_question_count_prediction_lstm/'
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    for tag, (model, scaler) in models.items():
        with open(dir_path + f'{tag}_prediction_model_lstm.pkl', 'wb') as file:
            pickle.dump((model, scaler), file)


# Load the saved models and predict
def load_models_and_predict():
    dir_path = 'tag_question_count_prediction_lstm/'

    for tag in os.listdir(dir_path):
        with open(dir_path + tag, 'rb') as file:
            model, scaler = pickle.load(file)

            predictions = predict_for_next_days(model, scaler, days=30)
            predictions = scaler.inverse_transform(predictions)

            plt.figure(figsize=(8, 4))
            plt.plot(range(len(predictions)), predictions, label='Predicted')
            plt.legend(loc='upper right')
            plt.title(f'Predictions for {tag}')
            plt.show()


def predict_for_next_days(model, scaler, days=30, look_back=1):
    start_point = np.array([[[1]]])  # starting point for predictions
    predictions = []

    for _ in range(days):
        pred = model.predict(start_point)
        predictions.append(pred[0][0])
        start_point = np.array([[[pred[0][0]]]])

    return np.array(predictions).reshape(-1, 1)


try:
    data = get_data_from_db()
    prepared_data = prepare_data_for_lstm(data)
    models = train_model_lstm(prepared_data)
    save_models_lstm(models)

    for tag, (model, scaler) in models.items():
        forecast = predict_for_next_days(model, scaler, days=30)

        # Get actual data for last 10 days
        actual_data_list = []
        for i in range(10):
            day = datetime.now() - timedelta(days=10 - i)
            day_count = Question.objects(tags=tag, creation_date__gte=day,
                                         creation_date__lt=day + timedelta(days=1)).count()
            actual_data_list.append(day_count)

        # Check if forecast and actual_data_list are not empty
        if forecast.size != 0 and actual_data_list:
            # Plot actual data and forecast
            plt.figure(figsize=(10, 6))
            plt.plot(range(10), actual_data_list, marker='o', linestyle='-', color='b', label='Actual Data')
            plt.plot(range(30), forecast, marker='o', linestyle='-', color='r', label='Predictions')
            plt.title(f"Question count predictions for tag {tag}")
            plt.xlabel('Day')
            plt.ylabel('Question count')
            plt.legend()
            plt.show()
        else:
            print(f"No forecast or actual data available for tag {tag}")

except Exception as e:
    print(f"An error occurred: {e}")

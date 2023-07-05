import os
import pickle
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from apps.backend.database import Question, Tag
from apps import config
from datetime import datetime, timedelta
import matplotlib.pyplot as plt


def get_data_from_db():
    config.initiate_connection()

    ten_days_ago = datetime.now() - timedelta(days=10)
    data = []

    for tag in Tag.objects().order_by('-tags_length')[:2]:
        tag_questions = Question.objects(tags=tag.tag_name, creation_date__lte=ten_days_ago)
        for question in tag_questions:
            data.append({
                "tag": tag.tag_name,
                "date": question.creation_date.date(),
            })

    data_df = pd.DataFrame(data)
    return data_df


def prepare_data(data_df):
    data_df = data_df.groupby(['tag', 'date']).size().reset_index(name='counts')
    return data_df


def evaluate_arima_model(tag_data, order):
    try:
        model = ARIMA(tag_data['counts'], order=order)
        model_fit = model.fit()
        return model_fit.aic
    except:
        return float('inf')


def optimize_arima_model(tag_data):
    p_values = range(0, 3)
    d_values = range(0, 3)
    q_values = range(0, 3)
    order_list = [(p, d, q) for p in p_values for d in d_values for q in q_values]

    best_aic = float('inf')
    best_order = None
    for order in order_list:
        try:
            aic = evaluate_arima_model(tag_data, order)
            if aic < best_aic:
                best_aic, best_order = aic, order
        except:
            continue

    return best_order


def train_model(data_df):
    models = {}

    for tag in data_df['tag'].unique():
        tag_data = data_df[data_df['tag'] == tag].set_index('date')
        best_order = optimize_arima_model(tag_data)
        if best_order is not None:
            model = ARIMA(tag_data['counts'], order=best_order)
            model_fit = model.fit()
            print(model_fit.summary())
            models[tag] = model_fit
        else:
            print(f"Could not find a suitable ARIMA model for tag {tag}")

    return models


def save_models(models):
    dir_path = '../data_files/tag_question_count_prediction/'
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    for tag, model in models.items():
        with open(dir_path + f'{tag}_prediction_model.pkl', 'wb') as file:
            pickle.dump(model, file)


try:
    data = get_data_from_db()
    data = prepare_data(data)
    models = train_model(data)
    save_models(models)

    for tag in data['tag'].unique():
        model = models[tag]
        # Predict for the next 30 days
        forecast = model.forecast(steps=30)

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

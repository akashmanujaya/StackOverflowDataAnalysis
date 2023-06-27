import os
import pickle
import pandas as pd
from mongoengine import connect
from statsmodels.tsa.arima.model import ARIMA
from apps.backend.database import Tag, Question


def get_data_from_db():
    connect(db='stack_exchange_analysis', host='localhost', port=27017)

    tags = list(Tag.objects().order_by('-tags_length')[:10])
    data = []

    for tag in tags:
        tag_questions = Question.objects(tags=tag.tag_name)
        for question in tag_questions:
            data.append({
                "tag": tag.tag_name,
                "year": question.creation_date.year,
            })

    data_df = pd.DataFrame(data)
    return data_df


def prepare_data(data_df):
    data_df = data_df.groupby(['tag', 'year']).size().reset_index(name='counts')
    return data_df


def train_model(data_df):
    models = {}

    for tag in data_df['tag'].unique():
        tag_data = data_df[data_df['tag'] == tag].set_index('year')
        model = ARIMA(tag_data['counts'], order=(5, 1, 0))
        model_fit = model.fit()
        print(model_fit.summary())

        models[tag] = model_fit

    return models


def save_models(models):
    dir_path = 'tag_question_count_prediction/'
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

except Exception as e:
    print(f"An error occurred: {e}")

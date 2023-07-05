import json
import os
import pickle
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from apps.backend.database import Question, Tag
from apps import config
from datetime import datetime, timedelta
from dotenv import load_dotenv


class TagQuestionPredictor:
    def __init__(self):
        load_dotenv()

        # This gives you the relative path from environment variable
        self.data_file_path = os.getenv('DATA_FILE_PATH')
        config.initiate_connection()
        self.models_dir = os.path.join(self.data_file_path, 'tag_question_count_prediction')

    def get_data_from_db(self):
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

    def prepare_data(self, data_df):
        data_df = data_df.groupby(['tag', 'date']).size().reset_index(name='counts')
        return data_df

    def train_model(self, data_df):
        models = {}

        for tag in data_df['tag'].unique():
            tag_data = data_df[data_df['tag'] == tag].set_index('date')
            model = ARIMA(tag_data['counts'], order=(5, 1, 0))
            model_fit = model.fit()

            models[tag] = model_fit

        return models

    def save_models(self, models):
        if not os.path.exists(self.models_dir):
            os.makedirs(self.models_dir)

        for tag, model in models.items():
            with open(self.models_dir + f'/{tag}_prediction_model.pkl', 'wb') as file:
                pickle.dump(model, file)

    def get_actual_data(self, tag):
        actual_data_list = []
        for i in range(10):
            day = datetime.now() - timedelta(days=10 - i)
            day_count = Question.objects(tags=tag, creation_date__gte=day,
                                         creation_date__lt=day + timedelta(days=1)).count()
            actual_data_list.append(day_count)
        print(f"This is actual data list for tag {tag} and data is {actual_data_list}")
        return actual_data_list

    def predict_and_save(self):

        # Ensure the models directory exists
        if not os.path.exists(self.models_dir):
            print(f"No models directory found at {self.models_dir}")
            return

        # Initialize dictionary to store prediction results
        prediction_results = {}

        for model_file in os.listdir(self.models_dir):
            tag = os.path.splitext(model_file)[0].replace('_prediction_model', '')  # remove .pkl extension and '_prediction_model' to get the tag name
            with open(os.path.join(self.models_dir, model_file), 'rb') as file:
                model = pickle.load(file)
                forecast = [round(x) for x in model.forecast(steps=30)]
                actual_data = self.get_actual_data(tag)

                # Store in dictionary
                prediction_results[tag] = {
                    "forecast": forecast,
                    "actual_data": actual_data,
                }

        file_path = os.path.join(self.data_file_path, 'prediction_results.json')
        print(f"comes here and file path: {file_path}")
        # Save dictionary to JSON file
        with open(file_path, 'w') as file:
            json.dump(prediction_results, file)

    def run(self):
        try:
            # data = self.get_data_from_db()
            # data = self.prepare_data(data)
            # models = self.train_model(data)
            # self.save_models(models)

            # After saving models
            self.predict_and_save()
        except Exception as e:
            print(f"An error occurred: {e}")

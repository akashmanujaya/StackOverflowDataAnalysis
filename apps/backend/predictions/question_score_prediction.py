import pickle
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from apps.backend.database import Question
from apps import config


def get_data_from_db():
    # initiate database connection
    config.initiate_connection()

    data = []
    for question in Question.objects():
        question_dict = {
            "question_id": question.question_id,
            "title": question.title,
            "view_count": question.view_count,
            "answer_count": question.answer_count,
            "score": question.score,
            "question_length": question.question_length,
            "question_age": question.question_age,
            "time_since_last_edit": question.time_since_last_edit,
            "complexity_score": question.complexity_score
        }
        data.append(question_dict)

    data_df = pd.DataFrame(data)
    return data_df


def preprocess_data(data_df):
    # Handle missing values
    data_df = data_df.fillna(value={'time_since_last_edit': data_df['question_age']})

    # Convert boolean column to int
    # data_df['is_answered'] = data_df['is_answered'].astype(int)

    return data_df


def extract_features(data):
    vectorizer = TfidfVectorizer(min_df=0.1, max_df=0.9)
    tfidf = vectorizer.fit_transform(data['title'])
    tfidf_df = pd.DataFrame(tfidf.toarray(), columns=vectorizer.get_feature_names_out())
    data = pd.concat([data, tfidf_df], axis=1)
    data.drop(['title'], axis=1, inplace=True)
    return data


def train_model(data):
    try:
        # Separate predictors and target
        X = data.drop('score', axis=1)
        y = data['score']

        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train a random forest regressor
        rf = RandomForestRegressor(n_estimators=100, random_state=42)
        rf.fit(X_train, y_train)

        # Print the score of the fitted model
        print(f'Model Score: {rf.score(X_test, y_test)}')

        # Check current working directory
        print(f'Current working directory: {os.getcwd()}')

        # Save the model
        dir_path = os.path.join(os.getcwd())
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        model_path = os.path.join(dir_path, 'question_score_prediction_model.pkl')
        with open(model_path, 'wb') as file:
            pickle.dump(rf, file)

        print(f'Model saved to: {model_path}')

        return rf

    except Exception as e:
        print(f'An error occurred: {str(e)}')


try:
    # Load the data
    data = get_data_from_db()

    # Preprocess the data
    data = preprocess_data(data)

    # Extract features from the text
    data = extract_features(data)

    # Train the model
    train_model(data)

except Exception as e:
    print(f"An error occurred: {e}")

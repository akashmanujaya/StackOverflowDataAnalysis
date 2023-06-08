from apps.backend.crossvalidated_client import CrossValidatedClient
from apps.backend.stackoverflow_client import StackOverflowClient
from apps.backend.database_manager import DatabaseManager
from dotenv.main import load_dotenv
from datetime import datetime
import os

load_dotenv()


def fetch_data():
    # Initialize a DatabaseManager instance with your database credentials
    database_manager = DatabaseManager(
        os.environ['DB_USER'],
        os.environ['DB_PASSWORD'],
        os.environ['DB_HOST'],
        os.environ['DB_NAME']
    )

    # Create tables if they don't exist
    database_manager.create_tables()

    # Initialize a StackOverflowClient instance with the tags you're interested in
    stack_overflow_tags = ['python', 'data-science', 'machine-learning', 'deep-learning', 'neural-network',
                           'classification',
                           'keras', 'nlp', 'scikit-learn', 'tensorflow', 'time-series', 'regression', 'r',
                           'dataset',
                           'cnn', 'clustering', 'pandas', 'data-mining', 'predictive-modeling', 'lstm',
                           'statistics',
                           'feature-selection', 'data', 'random-forest', 'machine-learning-model',
                           'linear-regression',
                           'data-cleaning', 'rnn', 'image-classification', 'convolutional-neural-network',
                           'decision-trees',
                           'xgboost', 'logistic-regression', 'visualization', 'training', 'pytorch',
                           'data-science-model',
                           'feature-engineering', 'computer-vision', 'cross-validation', 'reinforcement-learning',
                           'svm',
                           'text-mining', 'multiclass-classification', 'class-imbalance', 'loss-function',
                           'preprocessing',
                           'optimization', 'recommender-system', 'word-embeddings', 'bigdata']

    cross_validated_tags = [
        'r',
        'regression',
        'machine-learning',
        'time-series',
        'probability',
        'hypothesis-testing',
        'distributions',
        'self-study',
        'neural-networks',
        'bayesian',
        'logistic',
        'mathematical-statistics',
        'classification',
        'correlation',
        'statistical-significance',
        'mixed-model',
        'normal-distribution',
        'multiple-regression',
        'python',
        'confidence-interval',
        'generalized-linear-model',
        'variance',
        'clustering',
        'forecasting',
        'clustering',
        'data-visualization',
        'cross-validation',
        'sampling',
        'p-value',
        'linear-model'
    ]

    stackoverflow_client = StackOverflowClient(
        stack_overflow_tags,

        os.environ['STACK_EXCHANGE_ACCESS_TOKEN'],
        os.environ['STACK_EXCHANGE_KEY']
    )

    crossvalidated_client = CrossValidatedClient(
        cross_validated_tags,
        os.environ['STACK_EXCHANGE_ACCESS_TOKEN'],
        os.environ['STACK_EXCHANGE_KEY']
    )

    # Fetch questions from the API and insert them into the database
    for items in stackoverflow_client.fetch_all_questions():
        for question in items:
            try:
                if question['score'] > 0 and 'owner' in question and 'user_id' in question['owner']:
                    database_manager.insert_user(question['owner'])
                    question['creation_date'] = datetime.utcfromtimestamp(question['creation_date']).strftime(
                        '%Y-%m-%d %H:%M:%S')
                    if 'last_edit_date' in question:
                        question['last_edit_date'] = datetime.utcfromtimestamp(question['last_edit_date']).strftime(
                            '%Y-%m-%d %H:%M:%S')
                    question['user_id'] = question['owner']['user_id']
                    question['source'] = 'stackoverflow'
                    database_manager.insert_question(question)
                    database_manager.insert_tags(question['question_id'], question['tags'])
            except Exception as ex:
                print(f"Error Occurred: {ex}")
                print(question)

    for items in crossvalidated_client.fetch_all_questions():
        for question in items:
            try:
                if question['score'] > 0 and 'owner' in question and 'user_id' in question['owner']:
                    database_manager.insert_user(question['owner'])
                    question['creation_date'] = datetime.utcfromtimestamp(question['creation_date']).strftime(
                        '%Y-%m-%d %H:%M:%S')
                    if 'last_edit_date' in question:
                        question['last_edit_date'] = datetime.utcfromtimestamp(question['last_edit_date']).strftime(
                            '%Y-%m-%d %H:%M:%S')
                    question['user_id'] = question['owner']['user_id']
                    question['source'] = 'crossvalidated'
                    database_manager.insert_question(question)
                    database_manager.insert_tags(question['question_id'], question['tags'])
            except Exception as ex:
                print(f"Error Occurred: {ex}")
                print(question)

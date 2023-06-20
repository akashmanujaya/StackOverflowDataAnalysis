from celery import Celery
from mongoengine import connect
from dotenv import load_dotenv
from apps.backend.clients.crossvalidated_client import CrossValidatedClient
from apps.backend.clients.stackoverflow_client import StackOverflowClient
from apps.backend.database_manager import DatabaseManager
from apps.backend.database import Tag, Question
from apps.backend.services.complexity_score import ComplexityAnalyzer
from datetime import datetime
import os
from urllib.parse import quote_plus

# Load .env file
load_dotenv()

# Replace these with your MongoDB settings
db_name = quote_plus(os.environ["MONGO_DB_NAME"])
username = quote_plus(os.environ["MONGO_DB_USER"])
password = quote_plus(os.environ["MONGO_DB_PASSWORD"])
host = os.environ["MONGO_DB_HOST"]

# Initialize Celery
celery_app = Celery(__name__, broker='pyamqp://guest@localhost//')

# Update tags length every hour
celery_app.conf.beat_schedule = {
    'fetch_data': {
        'task': 'apps.backend.services.tasks.fetch_data',
        'schedule': 60.0 * 60.0,
    },
}

connect(db=db_name, host=f'mongodb+srv://{username}:{password}@{host}/{db_name}?retryWrites=true&w=majority')


@celery_app.task(name="apps.backend.services.tasks.update_tags_length")
def update_tags_length():
    # Establish a connection to the MongoDB server
    # connect(db=db_name, host=f'mongodb+srv://{username}:{password}@{host}/{db_name}?retryWrites=true&w=majority')

    # Your original code
    tags = Tag.objects.all()
    for tag in tags:
        tag.tags_length = Question.objects(tags=tag).count()
        tag.save()


@celery_app.task(name="apps.backend.services.tasks.update_complexity_score")
def update_complexity_score():
    # Establish a connection to the MongoDB server
    # connect(db=db_name, host=f'mongodb+srv://{username}:{password}@{host}/{db_name}?retryWrites=true&w=majority')

    # Initialize a ComplexityAnalyzer instance
    complexity_analyzer = ComplexityAnalyzer()

    # Update complexity scores
    complexity_analyzer.update_question_complexity()


@celery_app.task(name="apps.backend.services.tasks.fetch_data")
def fetch_data():
    # Establish a connection to the MongoDB server
    # connect(db=db_name, host=f'mongodb+srv://{username}:{password}@{host}/{db_name}?retryWrites=true&w=majority')

    # Initialize a DatabaseManager instance with your database credentials
    db_manager = DatabaseManager()

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

    cross_validated_client = CrossValidatedClient(
        cross_validated_tags,
        os.environ['STACK_EXCHANGE_ACCESS_TOKEN'],
        os.environ['STACK_EXCHANGE_KEY']
    )

    for items in stackoverflow_client.fetch_all_questions():
        for question in items:
            try:
                if question['score'] > 0 and 'owner' in question and 'user_id' in question['owner']:
                    user = db_manager.insert_user(question['owner'])
                    question['creation_date'] = datetime.utcfromtimestamp(question['creation_date']).strftime(
                        '%Y-%m-%d %H:%M:%S')
                    if 'last_edit_date' in question:
                        question['last_edit_date'] = datetime.utcfromtimestamp(question['last_edit_date']).strftime(
                            '%Y-%m-%d %H:%M:%S')
                    question['user'] = user
                    question['source'] = 'stackoverflow'
                    tags = [db_manager.get_or_create_tag(tag) for tag in question['tags']]
                    db_manager.insert_question(question, tags)
            except Exception as ex:
                print(f"Error Occurred: {ex}")

    for items in cross_validated_client.fetch_all_questions():
        for question in items:
            try:
                if question['score'] > 0 and 'owner' in question and 'user_id' in question['owner']:
                    user = db_manager.insert_user(question['owner'])
                    question['creation_date'] = datetime.utcfromtimestamp(question['creation_date']).strftime(
                        '%Y-%m-%d %H:%M:%S')
                    if 'last_edit_date' in question:
                        question['last_edit_date'] = datetime.utcfromtimestamp(question['last_edit_date']).strftime(
                            '%Y-%m-%d %H:%M:%S')
                    question['user'] = user
                    question['source'] = 'crossvalidated'
                    tags = [db_manager.get_or_create_tag(tag) for tag in question['tags']]
                    db_manager.insert_question(question, tags)
            except Exception as ex:
                print(f"Error Occurred: {ex}")

    # Invoke update_tags_length when fetch_data finishes
    update_tags_length.delay()

    # Invoke update_complexity_score when update_tags_length finishes
    update_complexity_score.delay()

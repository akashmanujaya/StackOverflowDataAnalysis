from celery import Celery
from mongoengine import connect
from dotenv import load_dotenv
from apps.backend.clients.crossvalidated_client import CrossValidatedClient
from apps.backend.clients.stackoverflow_client import StackOverflowClient
from apps.backend.database_manager import DatabaseManager
from apps.backend.database import Tag, Question, User
from apps.backend.services.complexity_score import ComplexityAnalyzer
from datetime import datetime
import os
from urllib.parse import quote_plus
import json
import random
import numpy as np
from pandas import DataFrame
from scipy import stats

# Load .env file
load_dotenv()

# Replace these with your MongoDB settings
db_name = quote_plus(os.environ["MONGO_DB_NAME"])
username = quote_plus(os.environ["MONGO_DB_USER"])
password = quote_plus(os.environ["MONGO_DB_PASSWORD"])
host = os.environ["MONGO_DB_HOST"]

# This gives you the relative path from environment variable
data_file_path = os.getenv('DATA_FILE_PATH')

# Initialize Celery
celery_app = Celery(__name__, broker='pyamqp://guest@localhost//')

# Update tags length every hour
celery_app.conf.beat_schedule = {
    'fetch_data': {
        'task': 'apps.backend.services.tasks.fetch_data',
        'schedule': 60.0 * 60.0,
    },
}

# Establish a connection to the MongoDB server
# connect(db=db_name, host=f'mongodb+srv://{username}:{password}@{host}/{db_name}?retryWrites=true&w=majority')

connect(
    db=db_name,  # Replace with your database name
    host='localhost',  # Replace with your MongoDB server host
    port=27017,  # Replace with your MongoDB server port
    # username='your_username',  # Replace with your MongoDB username if required
    # password='your_password',  # Replace with your MongoDB password if required
)


@celery_app.task(name="apps.backend.services.tasks.update_tags_length")
def update_tags_length():
    # Your original code
    tags = Tag.objects.all()
    for tag in tags:
        tag.tags_length = Question.objects(tags=tag).count()
        tag.save()


@celery_app.task(name="apps.backend.services.tasks.update_complexity_score")
def update_complexity_score():
    # Initialize a ComplexityAnalyzer instance
    complexity_analyzer = ComplexityAnalyzer()

    # Update complexity scores
    complexity_analyzer.update_question_complexity()

    complexity_analyzer.save_complexity_score()


@celery_app.task(name="apps.backend.services.tasks.save_top_users")
def save_top_users():
    # Get top 5 users
    top_users = User.objects().order_by('-reputation')[:5]

    # Serialize the users
    serialized_users = [serialize_user(user) for user in top_users]

    # Ensure the directory exists
    os.makedirs(data_file_path, exist_ok=True)

    # Define the file path
    file_path = os.path.join(data_file_path, 'top_users.json')

    # Write the serialized data to the file
    with open(file_path, 'w') as file:
        file.write(json.dumps(serialized_users))


@celery_app.task(name="apps.backend.services.tasks.save_popular_tags")
def save_popular_tags():
    # Get top 10 tags
    top_tags = Tag.objects().order_by('-tags_length')[:10]

    # Serialize the tags
    serialized_tags = [tag.tag_name for tag in top_tags]

    # Define the file path
    file_path = os.path.join(data_file_path, 'popular_tags.json')

    # Write the serialized data to the file
    with open(file_path, 'w') as file:
        file.write(json.dumps(serialized_tags))


@celery_app.task(name="apps.backend.services.tasks.save_tags_and_data")
def save_tags_and_data():
    # Define a dictionary to store all the data
    all_data = {}

    # Get top 10 tags
    top_tags = Tag.objects().order_by('-tags_length')[:10]

    # Serialize the tags
    all_data['tags'] = [tag.tag_name for tag in top_tags]

    # Fetch data for each tag
    for tag_name in all_data['tags']:
        # Get the tag with tag_name
        tag = Tag.objects(tag_name=tag_name).first()

        # Find all questions related to the tag
        questions = Question.objects(tags=tag)

        # Prepare the data
        data = {}
        for question in questions:
            year = question.creation_date.year
            data[year] = data.get(year, 0) + 1

        # Sort the data by year and convert to the required format
        sorted_data = sorted(data.items(), key=lambda x: x[0])
        all_data[tag_name] = [(str(year), count) for year, count in sorted_data]

    # Define the file path
    file_path = os.path.join(data_file_path, 'tags_and_data.json')
    os.makedirs(data_file_path, exist_ok=True)

    # Write the serialized data to the file
    with open(file_path, 'w') as file:
        file.write(json.dumps(all_data))


@celery_app.task(name="apps.backend.services.tasks.save_tag_statistics")
def save_tag_statistics():
    # Get the top 10 tags
    top_tags = Tag.objects().order_by('-tags_length')[:10]

    # Prepare a list to store the tag data
    tag_data = []

    # Iterate through each tag
    for tag in top_tags:
        # Get all questions associated with this tag
        questions = Question.objects.filter(tags=tag)

        # Calculate mean, median and mode
        scores = [question.complexity_score for question in questions]
        mean = np.mean(scores)
        median = np.median(scores)
        mode = stats.mode(scores)[0][0] if scores else np.nan  # Take only the first mode

        # Append a new dictionary to tag_data
        tag_data.append({
            'tag': tag.tag_name,
            'mean': mean,
            'median': median,
            'mode': float(mode)  # make sure mode is float not numpy.float64
        })

    # Define the file path
    file_path = os.path.join(data_file_path, 'tags_statistics.json')
    os.makedirs(data_file_path, exist_ok=True)

    # Write the serialized data to the file
    with open(file_path, 'w') as file:
        file.write(json.dumps(tag_data))


@celery_app.task(name="apps.backend.services.tasks.save_score_complexity")
def save_score_complexity():
    data = list(Question.objects().only('score', 'complexity_score'))
    sample_size = min(1000, len(data))  # adjust this as needed
    sampled_data = random.sample(data, sample_size)
    response = [{'x': item.complexity_score, 'y': item.score} for item in sampled_data]
    # Define the file path
    file_path = os.path.join(data_file_path, 'score_complexity.json')
    os.makedirs(data_file_path, exist_ok=True)

    with open(file_path, 'w') as file:
        file.write(json.dumps(response))


@celery_app.task(name="apps.backend.services.tasks.save_complexity_quartile_over_time")
def save_complexity_quartile_over_time():
    questions = Question.objects.only('creation_date', 'complexity_score').all()

    # Create a DataFrame with creation_date and complexity_score
    df = DataFrame([{'date': question.creation_date, 'complexity': question.complexity_score}
                    for question in questions])

    # Drop rows where 'complexity' is NaN
    df = df.dropna(subset=['complexity'])

    # Convert creation_date to year format
    df['date'] = df['date'].apply(lambda x: x.strftime('%Y'))

    # Group by date and calculate quartiles
    df_grouped = df.groupby('date')['complexity']

    quartile_25 = df_grouped.apply(lambda x: np.percentile(x, 25)).tolist()
    quartile_50 = df_grouped.apply(lambda x: np.percentile(x, 50)).tolist()
    quartile_75 = df_grouped.apply(lambda x: np.percentile(x, 75)).tolist()

    dates = sorted(df['date'].unique().tolist())

    # Limit to last 10 years
    if len(dates) > 10:
        dates = dates[-10:]
        quartile_25 = quartile_25[-10:]
        quartile_50 = quartile_50[-10:]
        quartile_75 = quartile_75[-10:]

    data = {
        'dates': dates,
        'quartile_25': quartile_25,
        'quartile_50': quartile_50,
        'quartile_75': quartile_75
    }

    # Define the file path
    file_path = os.path.join(data_file_path, 'complexity_quartile_over_time.json')
    os.makedirs(data_file_path, exist_ok=True)

    # Write the serialized data to the file
    with open(file_path, 'w') as file:
        file.write(json.dumps(data))


@celery_app.task(name="apps.backend.services.tasks.save_top_questions")
def save_top_questions():
    # Get top 8 questions
    top_questions = Question.objects().order_by('-score')[:8]

    # Serialize the questions
    serialized_questions = [
        {
            'question_id': str(question.id),
            'title': question.title,
            'view_count': question.view_count,
            'user': serialize_user(question.user),
            'score': question.score,
            'link': question.link,
        } for question in top_questions
    ]

    # Define the file path
    file_path = os.path.join(data_file_path, 'top_questions.json')

    # Write the serialized data to the file
    with open(file_path, 'w') as file:
        file.write(json.dumps(serialized_questions))


def serialize_user(user):
    return {
        'user_id': str(user.id),
        'display_name': user.display_name,
        'profile_image': user.profile_image,
        'reputation': user.reputation,
        'link': user.link
    }


@celery_app.task(name="apps.backend.services.tasks.fetch_data")
def fetch_data():
    # Initialize a DatabaseManager instance with your database credentials
    db_manager = DatabaseManager()

    # Get the directory of the current script file
    current_dir = os.path.dirname(os.path.realpath(__file__))

    # Construct the full paths to your files
    stackoverflow_tags_path = os.path.join(current_dir, 'stackoverflow_tags.txt')
    cross_validated_tags_path = os.path.join(current_dir, 'cross_validated_tags.txt')

    # Read tags from text files
    with open(stackoverflow_tags_path, 'r') as file:
        stack_overflow_tags = [line.strip() for line in file.readlines()]

    with open(cross_validated_tags_path, 'r') as file:
        cross_validated_tags = [line.strip() for line in file.readlines()]

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

    # Invoke save_popular_tags when fetch_data finishes
    save_tags_and_data.delay()

    # Invoke save_score_complexity when fetch_data finishes
    save_score_complexity.delay()

    # Invoke save_complexity_quartile_over_time when fetch_data finishes
    save_complexity_quartile_over_time.delay()

    # Invoke save_tag_statistics when fetch_data finishes
    save_tag_statistics.delay()

    # Invoke save_top_users when fetch_data finishes
    save_top_users.delay()

    # Invoke save_top_questions when fetch_data finishes
    save_top_questions.delay()

    # Invoke update_tags_length when fetch_data finishes
    update_tags_length.delay()

    # Invoke update_complexity_score when update_tags_length finishes
    update_complexity_score.delay()

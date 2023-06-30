from celery import Celery
from dotenv import load_dotenv
from apps.backend.clients.crossvalidated_client import CrossValidatedClient
from apps.backend.clients.stackoverflow_client import StackOverflowClient
from apps.backend.database_manager import DatabaseManager
from apps.backend.database import Tag, Question, User
from apps.backend.services.complexity_score import ComplexityAnalyzer
# import datetime
from datetime import datetime
import os
from apps import config
import json
import random
import numpy as np
from pandas import DataFrame
from scipy import stats

# Load .env file
load_dotenv()

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
config.initiate_connection()

# Get the directory of the current script file
current_dir = os.path.dirname(os.path.realpath(__file__))

# Construct the full paths to your files
stackoverflow_tags_path = os.path.join(current_dir, 'stackoverflow_tags.txt')
cross_validated_tags_path = os.path.join(current_dir, 'cross_validated_tags.txt')


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
    top_tags = get_unique_tags()

    # Define the file path
    file_path = os.path.join(data_file_path, 'popular_tags.json')

    # Write the serialized data to the file
    with open(file_path, 'w') as file:
        file.write(json.dumps(top_tags))


@celery_app.task(name="apps.backend.services.tasks.save_tags_and_data")
def save_tags_and_data():
    # Define a dictionary to store all the data
    all_data = {}

    # Get tags
    tags = get_unique_tags()

    # Fetch data for each tag
    for tag in tags:
        # Find all questions related to the tag
        questions = Question.objects(tags=tag)

        # Prepare the data
        data = {}
        for question in questions:
            year = question.creation_date.year
            data[year] = data.get(year, 0) + 1

        # Sort the data by year and convert to the required format
        sorted_data = sorted(data.items(), key=lambda x: x[0])
        all_data[tag] = [(str(year), count) for year, count in sorted_data]

    # Define the file path
    file_path = os.path.join(data_file_path, 'tags_and_data.json')
    os.makedirs(data_file_path, exist_ok=True)

    # Write the serialized data to the file
    with open(file_path, 'w') as file:
        file.write(json.dumps(all_data))


@celery_app.task(name="apps.backend.services.tasks.save_tag_statistics")
def save_tag_statistics():
    # Get the top 10 tags
    tags = get_unique_tags()

    # Prepare a list to store the tag data
    tag_data = []

    # Iterate through each tag
    for tag in tags:
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


def get_unique_tags():
    tags = []

    with open(stackoverflow_tags_path, 'r') as file:
        tags += file.read().splitlines()

    with open(cross_validated_tags_path, 'r') as file:
        tags += file.read().splitlines()

    return list(set(tags))


# def calculate_tag_percentage(tag_name, year):
#     start_date = datetime.datetime(year, 1, 1)
#     end_date = datetime.datetime(year + 1, 1, 1)
#
#     # Get the tag object
#     tag = Tag.objects(tag_name=tag_name).first()
#
#     # Calculate the total number of questions in the year
#     total_questions = Question.objects(creation_date__gte=start_date, creation_date__lt=end_date).count()
#
#     # Calculate the total number of questions with the given tag in the year
#     tag_questions = Question.objects(creation_date__gte=start_date, creation_date__lt=end_date, tags=tag).count()
#
#     # Calculate the percentage (with two decimal points)
#     percentage = round((tag_questions / total_questions) * 100, 2)
#
#     return percentage
#
#
# @celery_app.task(name="apps.backend.services.tasks.save_tag_percentages")
# def save_tag_percentages():
#     # get current year
#     current_year = datetime.datetime.now().year
#
#     # get unique tags
#     tags = get_unique_tags()
#
#     tag_percentages = {}
#
#     # loop over each tag
#     for tag in tags:
#         tag_percentages[tag] = {}
#
#         # loop over last 10 years
#         for year in range(current_year - 9, current_year + 1):
#             # calculate percentage for each tag
#             percentage = calculate_tag_percentage(tag, year)
#
#             # add percentage to the tag dict
#             tag_percentages[tag][str(year)] = percentage
#
#     # Define the file path
#     file_path = os.path.join(data_file_path, 'tag_percentages.json')
#
#     # write the data to a json file
#     with open(file_path, 'w') as file:
#         file.write(json.dumps(tag_percentages))
#

def serialize_user(user):
    return {
        'user_id': str(user.id),
        'display_name': user.display_name,
        'profile_image': user.profile_image,
        'reputation': user.reputation,
        'link': user.link
    }


def calculate_question_age(creation_date):
    now = datetime.utcnow()  # this will now create a timezone naive datetime object
    age = (now - creation_date).total_seconds() / (60 * 60 * 24)  # convert to days
    return age


def calculate_time_since_last_edit(last_edit_date):
    if last_edit_date:  # if the question has been edited
        now = datetime.utcnow()
        time_since_last_edit = (now - last_edit_date).total_seconds() / (60 * 60 * 24)  # convert to days
    else:  # if the question has not been edited
        time_since_last_edit = None
    return time_since_last_edit


@celery_app.task(name="apps.backend.services.tasks.fetch_data")
def fetch_data():
    # Initialize a DatabaseManager instance with your database credentials
    db_manager = DatabaseManager()

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
                    question['question_length'] = len(question['body'])
                    question['question_age'] = calculate_question_age(question['creation_date'])
                    question['time_since_last_edit'] = calculate_time_since_last_edit(question['last_edit_date'])
                    tags = [db_manager.get_or_create_tag(tag) for tag in question['tags']]
                    db_manager.insert_question(question, tags)
            except Exception as ex:
                print(f"Error Occurred from fetch_data function: {ex}")

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
                    question['question_length'] = len(question['body'])
                    question['question_age'] = calculate_question_age(question['creation_date'])
                    question['time_since_last_edit'] = calculate_time_since_last_edit(question['last_edit_date'])
                    tags = [db_manager.get_or_create_tag(tag) for tag in question['tags']]
                    db_manager.insert_question(question, tags)
            except Exception as ex:
                print(f"Error Occurred from fetch_data function: {ex}")

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

    # Invoke update_complexity_score when update_tags_length finishes
    # save_tag_percentages.delay()

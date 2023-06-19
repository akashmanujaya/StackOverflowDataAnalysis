from flask import jsonify
from apps.backend.database import User, Question, Tag
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
from mongoengine import connect, disconnect

# Load .env file
load_dotenv()

# Replace these with your MongoDB settings
db_name = quote_plus(os.environ["MONGO_DB_NAME"])
username = quote_plus(os.environ["MONGO_DB_USER"])
password = quote_plus(os.environ["MONGO_DB_PASSWORD"])
host = os.environ["MONGO_DB_HOST"]


def handle_database_connection():
    disconnect()
    connect(db=db_name, host=f'mongodb+srv://{username}:{password}@{host}/{db_name}?retryWrites=true&w=majority')


def get_top_users():
    # handle_database_connection()

    # Get top 7 users based on reputation
    result = User.objects().order_by('-reputation')[:5]
    return [serialize_user(user) for user in result]


def serialize_user(user):
    return {
        'user_id': str(user.id),
        'display_name': user.display_name,
        'profile_image': user.profile_image,
        'reputation': user.reputation,
        'link': user.link
    }


def get_top_questions():
    # handle_database_connection()
    # Get top 7 questions based on score
    result = Question.objects().order_by('-score')[:8]
    return jsonify([
        {
            'question_id': str(question.id),
            'title': question.title,
            'view_count': question.view_count,
            'user': serialize_user(question.user),
            'score': question.score,
            'link': question.link,
        } for question in result
    ])


def get_popular_tags():
    # handle_database_connection()
    try:
        # Get top 10 tags based on the number of questions associated with them
        result = Tag.objects().order_by('-tags_length')[:10]
        return jsonify([tag.tag_name for tag in result])
    finally:
        pass  # No need to close the session when using MongoEngine


def get_tag_data(tag_name):
    # handle_database_connection()
    # Get the tag with tag_name
    tag = Tag.objects(tag_name=tag_name).first()

    # Check if tag exists
    if not tag:
        return jsonify([])

    # Find all questions related to the tag
    questions = Question.objects(tags=tag)

    # Prepare the data
    data = {}
    for question in questions:
        year = question.creation_date.year
        data[year] = data.get(year, 0) + 1

    # Sort the data by year and convert to the required format
    sorted_data = sorted(data.items(), key=lambda x: x[0])
    return jsonify([(str(year), count) for year, count in sorted_data])

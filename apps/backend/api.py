from flask import jsonify
from apps.backend.database import User, Question, Tag
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
from collections import Counter
import numpy as np

# Load .env file
load_dotenv()

# Replace these with your MongoDB settings
db_name = quote_plus(os.environ["MONGO_DB_NAME"])
username = quote_plus(os.environ["MONGO_DB_USER"])
password = quote_plus(os.environ["MONGO_DB_PASSWORD"])
host = os.environ["MONGO_DB_HOST"]


def get_top_users():
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
    try:
        # Get top 10 tags based on the number of questions associated with them
        result = Tag.objects().order_by('-tags_length')[:10]
        return jsonify([tag.tag_name for tag in result])
    finally:
        pass  # No need to close the session when using MongoEngine


def get_tag_data(tag_name):
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


def get_complexity_scores():
    scores = [item['complexity_score'] for item in Question.objects().only('complexity_score')]

    # Set up the bins for the histogram
    bins = np.linspace(0, 1, 11)  # create 10 equally spaced bins between 0 and 1
    bins_labels = ["{:.1f} - {:.1f}".format(bins[i], bins[i + 1]) for i in range(len(bins) - 1)]  # Create bin labels

    # Digitize the data (assign each score to a bin)
    digitized = np.digitize(scores, bins)

    # Count the number of scores in each bin
    frequency_counts = Counter(digitized)

    # Prepare the data for the chart
    chart_data = [{'x': bins_labels[i - 1], 'y': frequency_counts[i]} for i in range(1, len(bins))]

    return jsonify(chart_data)

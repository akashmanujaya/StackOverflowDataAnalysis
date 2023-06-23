from flask import jsonify
from apps.backend.database import User, Question, Tag
from dotenv import load_dotenv
import os
import json
from pandas import DataFrame
import numpy as np

load_dotenv()

data_file_path = os.getenv('DATA_FILE_PATH')


def get_complexity_quartile_over_time():
    # Define the file path
    file_path = os.path.join(data_file_path, 'complexity_quartile_over_time.json')

    # Check if the file exists
    if not os.path.isfile(file_path):
        return jsonify({'error': 'File not found'}), 404

    # Read the data from the file
    with open(file_path, 'r') as file:
        complexity_quartile_over_time = json.load(file)

    # Return the data
    return jsonify(complexity_quartile_over_time)


def get_tag_statistics():
    # Define the file path
    file_path = os.path.join(data_file_path, 'tags_statistics.json')

    # Check if the file exists
    if not os.path.isfile(file_path):
        return jsonify({'error': 'File not found'}), 404

    # Read the data from the file
    with open(file_path, 'r') as file:
        tags_statistics = json.load(file)

    # Return the data
    return jsonify(tags_statistics)


def get_top_users():
    # Define the file path
    file_path = os.path.join(data_file_path, 'top_users.json')

    # Check if the file exists
    if not os.path.isfile(file_path):
        return jsonify({'error': 'File not found'}), 404

    # Read the data from the file
    with open(file_path, 'r') as file:
        top_users = json.load(file)

    # Return the data
    return jsonify(top_users)


def get_top_questions():
    # Define the file path
    file_path = os.path.join(data_file_path, 'top_questions.json')

    # Check if the file exists
    if not os.path.isfile(file_path):
        return jsonify({'error': 'File not found'}), 404

    # Read the data from the file
    with open(file_path, 'r') as file:
        top_questions = json.load(file)

    # Return the data
    return jsonify(top_questions)


def get_popular_tags():
    try:
        # Define the file path
        file_path = os.path.join(data_file_path, 'tags_and_data.json')

        # Check if the file exists
        if not os.path.isfile(file_path):
            return jsonify({'error': 'File not found'}), 404

        # Read the data from the file
        with open(file_path, 'r') as file:
            all_data = json.load(file)

        # Return the tags
        return jsonify(all_data['tags'])
    except Exception as ex:
        return jsonify({'error': f'Something went wrong: {ex}'}), 500


def get_tag_data(tag_name):
    # Define the file path
    file_path = os.path.join(data_file_path, 'tags_and_data.json')

    # Check if the file exists
    if not os.path.isfile(file_path):
        return jsonify({'error': 'File not found'}), 404

    # Read the data from the file
    with open(file_path, 'r') as file:
        all_data = json.load(file)

    # Fetch the data for the requested tag
    if tag_name not in all_data:
        return jsonify({'error': 'No data for the given tag'}), 404

    # Return the data
    return jsonify(all_data[tag_name])


def get_complexity_scores():
    file_path = os.path.join(data_file_path, 'complexity_score.json')
    # Check if the file exists
    if not os.path.isfile(file_path):
        return jsonify({'error': 'File not found'}), 404

    # Read data from file
    with open(file_path, 'r') as file:
        chart_data = json.load(file)

    return jsonify(chart_data)


def get_score_complexity():
    file_path = os.path.join(data_file_path, 'score_complexity.json')
    # Check if the file exists
    if not os.path.isfile(file_path):
        return jsonify({'error': 'File not found'}), 404

    # Read data from file
    with open(file_path, 'r') as file:
        chart_data = json.load(file)

    return jsonify(chart_data)

import pickle
import pandas as pd
from flask import jsonify
from apps.backend.services.complexity_score import ComplexityAnalyzer
from dotenv import load_dotenv
import os
import json

load_dotenv()

data_file_path = os.getenv('DATA_FILE_PATH')
prediction_file_path = os.getenv('PREDICTIONS_FILE_PATH')


def get_prediction(tag_name):
    try:
        # Define the file path
        file_path = os.path.join(prediction_file_path, f'tag_question_count_prediction/{tag_name}_prediction_model.pkl')

        # Load the model
        with open(file_path, 'rb') as file:
            model = pickle.load(file)

        # Generate the years for next 5 years
        years = pd.date_range(start='2023', end='2028', freq='AS')

        # Predict for next 5 years
        prediction = model.predict(start=1, end=5)

        # Prepare the result
        result = dict(zip(map(str, years.year), prediction.tolist()))

        # Return the result
        return jsonify(result)
    except Exception as e:
        return str(e)


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


def get_calculated_com_score(text, tag_count=0):
    com_analyser = ComplexityAnalyzer()
    score = com_analyser.calculate_complexity(text, tag_count)
    return score


def get_tag_percentage(tags, start_year, end_year):
    try:
        # Define the file path
        file_path = os.path.join(data_file_path, 'tag_percentages.json')

        # Check if the file exists
        if not os.path.isfile(file_path):
            return {'error': 'File not found'}

        # Read the data from the file
        with open(file_path, 'r') as file:
            all_data = json.load(file)

        # Initialize response data
        response_data = []

        # Process all requested tags
        for tag_name in tags:
            # Check if the tag exists in the data
            if tag_name not in all_data:
                continue  # Skip this tag if it doesn't exist in the data

            # Filter the data for the current tag based on the year range
            tag_data = {year: value for year, value in all_data[tag_name].items()
                        if start_year <= int(year) <= end_year}

            # Add the current tag data to the response
            response_data.append({
                'tag': tag_name,
                'data': tag_data
            })

        # Return the data
        return response_data

    except Exception as ex:
        return {'error': f'Something went wrong: {ex}'}


def get_prediction_results():
    try:
        # Define the file path
        file_path = os.path.join(data_file_path, 'prediction_results.json')

        # Check if the file exists
        if not os.path.isfile(file_path):
            return jsonify({'error': 'File not found'}), 404

        # Read the data from the file
        with open(file_path, 'r') as file:
            prediction_results = json.load(file)

        # Return the data
        return jsonify(prediction_results)

    except Exception as e:
        return str(e)

def calculate_tag_coverage():
    try:
        # Define the file path
        file_path = os.path.join(data_file_path, 'tag_coverage.json')

        # Check if the file exists
        if not os.path.isfile(file_path):
            return jsonify({'error': 'File not found'}), 404

        # Read the data from the file
        with open(file_path, 'r') as file:
            tag_coverage = json.load(file)

        # Return the data
        return tag_coverage

    except Exception as ex:
        return jsonify({'error': f'Something went wrong: {ex}'}), 500


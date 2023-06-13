from flask import jsonify
from apps.backend.database import User, Question, Tag


def get_top_users():
    # Get top 7 users based on reputation
    result = User.objects().order_by('-reputation')[:5]
    return jsonify([
        {
            'user_id': str(user.id),
            'display_name': user.display_name,
            'profile_image': user.profile_image,
            'reputation': user.reputation,
            'link': user.link
        } for user in result
    ])


def get_top_questions():
    # Get top 7 questions based on score
    result = Question.objects().order_by('-score')[:8]
    return jsonify([
        {
            'question_id': str(question.id),
            'title': question.title,
            'view_count': question.view_count,
            'user': question.user,
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

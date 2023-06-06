# tag_service.py

from flask import jsonify
from sqlalchemy import text
from database import db


def get_popular_tags():
    try:
        sql = text("""
            SELECT Tags.tag_name
            FROM Tags
            JOIN QuestionTags ON Tags.tag_id = QuestionTags.tag_id
            GROUP BY Tags.tag_name
            ORDER BY COUNT(QuestionTags.question_id) DESC
            LIMIT 50
        """)
        result = db.session.execute(sql)
        db.session.commit()
        return jsonify([row[0] for row in result])
    finally:
        db.session.remove()


def get_tag_data(tag_name):
    sql = text(f"""
        SELECT YEAR(Questions.creation_date) AS year, COUNT(Questions.question_id) AS count
        FROM Questions
        JOIN QuestionTags ON Questions.question_id = QuestionTags.question_id
        JOIN Tags ON QuestionTags.tag_id = Tags.tag_id
        WHERE Tags.tag_name = :tag_name
        GROUP BY YEAR(Questions.creation_date)
        ORDER BY year
    """)
    result = db.session.execute(sql, {'tag_name': tag_name})  # Use db.session.execute() instead
    return jsonify([(str(row[0]), row[1]) for row in result])

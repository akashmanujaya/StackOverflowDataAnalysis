from apps.backend.database import Tag, Question, User
from mongoengine import connect
from datetime import datetime, timezone

connect(
    db='stack_exchange_analysis',  # Replace with your database name
    host='localhost',  # Replace with your MongoDB server host
    port=27017,  # Replace with your MongoDB server port
    # username='your_username',  # Replace with your MongoDB username if required
    # password='your_password',  # Replace with your MongoDB password if required
)


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


questions = Question.objects.all()

for question in questions:
    question_age = calculate_question_age(question.creation_date)
    time_since_last_edit = calculate_time_since_last_edit(question.last_edit_date)
    question.update(question_age=question_age, time_since_last_edit=time_since_last_edit)

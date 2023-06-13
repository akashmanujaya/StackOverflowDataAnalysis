from apps.backend.database import User, Question, Tag


class DatabaseManager:
    def __init__(self):
        pass

    def insert_user(self, user):
        user_instance = User.objects(user_id=user['user_id']).first()
        if user_instance:
            # Update existing user
            user_instance.update(
                reputation=user['reputation'],
                display_name=user['display_name'],
                profile_image=user['profile_image'],
                link=user['link']
            )
        else:
            # Insert new user
            user_instance = User(
                user_id=user['user_id'],
                reputation=user['reputation'],
                display_name=user['display_name'],
                profile_image=user['profile_image'],
                link=user['link']
            )
            user_instance.save()
        return user_instance  # Return the user instance

    def insert_question(self, question, tags):
        # Check if the question already exists
        question_instance = Question.objects(question_id=question['question_id']).first()

        if question_instance:
            # Update existing question
            question_instance.update(
                link=question['link'],
                title=question['title'],
                body=question['body'],
                is_answered=question['is_answered'],
                view_count=question['view_count'],
                answer_count=question['answer_count'],
                score=question['score'],
                creation_date=question['creation_date'],
                last_edit_date=question.get('last_edit_date'),
                source=question['source'],
                user=question['user'],
                tags=tags
            )
        else:
            # Insert new question
            question_instance = Question(
                question_id=question['question_id'],
                link=question['link'],
                title=question['title'],
                body=question['body'],
                is_answered=question['is_answered'],
                view_count=question['view_count'],
                answer_count=question['answer_count'],
                score=question['score'],
                creation_date=question['creation_date'],
                last_edit_date=question.get('last_edit_date'),
                source=question['source'],
                user=question['user'],
                tags=tags
            )
            question_instance.save()
        return question_instance  # Return the question instance

    def get_or_create_tag(self, tag_name):
        tag_instance = Tag.objects(tag_name=tag_name).first()
        if not tag_instance:
            # Insert new tag
            tag_instance = Tag(tag_name=tag_name)
            tag_instance.save()
        return tag_instance  # Return the tag instance

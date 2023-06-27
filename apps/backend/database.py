from flask_mongoengine import MongoEngine

db = MongoEngine()


class User(db.Document):
    user_id = db.IntField(primary_key=True)
    reputation = db.IntField(required=True)
    display_name = db.StringField(max_length=255, required=True)
    profile_image = db.StringField(max_length=1024)
    link = db.StringField(max_length=1024)


class Tag(db.Document):
    tag_name = db.StringField(max_length=255, primary_key=True)
    tags_length = db.IntField(default=0)

    def __str__(self):
        return self.tag_name


class Question(db.Document):
    question_id = db.IntField(primary_key=True)
    link = db.StringField(required=True)
    title = db.StringField(required=True)
    body = db.StringField()
    is_answered = db.BooleanField(required=True)
    view_count = db.IntField(required=True)
    answer_count = db.IntField(required=True)
    score = db.IntField(required=True)
    creation_date = db.DateTimeField(required=True)
    last_edit_date = db.DateTimeField()
    source = db.StringField(choices=('stackoverflow', 'crossvalidated'), required=True)
    user = db.ReferenceField(User)
    tags = db.ListField(db.ReferenceField(Tag))
    complexity_score = db.FloatField()
    question_length = db.IntField()
    question_age = db.FloatField()
    time_since_last_edit = db.FloatField()

    meta = {
        'indexes': ['tags']
    }

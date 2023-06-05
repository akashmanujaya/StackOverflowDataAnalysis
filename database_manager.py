import mysql.connector


class DatabaseManager:
    def __init__(self, username, password, host, database):
        self.connection = mysql.connector.connect(
            user=username,
            password=password,
            host=host,
            database=database
        )
        self.cursor = self.connection.cursor()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                user_id INT PRIMARY KEY,
                reputation INT NOT NULL,
                display_name VARCHAR(255) NOT NULL,
                profile_image VARCHAR(1024),
                link VARCHAR(1024)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Questions (
                question_id INT PRIMARY KEY,
                title TEXT NOT NULL,
                is_answered BOOLEAN NOT NULL,
                view_count INT NOT NULL,
                answer_count INT NOT NULL,
                score INT NOT NULL,
                creation_date DATETIME NOT NULL,
                last_edit_date DATETIME,
                source ENUM('stackoverflow', 'crossvalidated') NOT NULL,
                user_id INT,
                FOREIGN KEY(user_id) REFERENCES Users(user_id)
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Tags (
                tag_id INT AUTO_INCREMENT PRIMARY KEY,
                tag_name VARCHAR(255) UNIQUE NOT NULL
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS QuestionTags (
                id INT AUTO_INCREMENT PRIMARY KEY,
                question_id INT NOT NULL,
                tag_id INT NOT NULL,
                FOREIGN KEY(question_id) REFERENCES Questions(question_id),
                FOREIGN KEY(tag_id) REFERENCES Tags(tag_id),
                UNIQUE(question_id, tag_id)
            )
        """)

        self.connection.commit()

    def insert_user(self, user):
        insert_query = """
            INSERT IGNORE INTO Users (user_id, reputation, display_name, profile_image, link)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            reputation=VALUES(reputation),
            display_name=VALUES(display_name), profile_image=VALUES(profile_image), link=VALUES(link)
        """

        try:
            self.cursor.execute(insert_query, (
                user['user_id'], user['reputation'], user['display_name'], user['profile_image'],
                user['link']))
            self.connection.commit()
        except Exception as ex:
            print(f"Error insertions: {ex}")

    def insert_question(self, question):
        insert_query = """
            INSERT INTO Questions (question_id, title, is_answered, view_count, answer_count, score, creation_date, last_edit_date, source, user_id) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
            ON DUPLICATE KEY UPDATE 
            title=VALUES(title), is_answered=VALUES(is_answered), view_count=VALUES(view_count), 
            answer_count=VALUES(answer_count), score=VALUES(score), creation_date=VALUES(creation_date), 
            last_edit_date=VALUES(last_edit_date), source=VALUES(source), user_id=VALUES(user_id)
        """



        data_tuple = (
            question['question_id'],
            question['title'],
            question['is_answered'],
            question['view_count'],
            question['answer_count'],
            question['score'],
            question['creation_date'],
            question.get('last_edit_date', None),
            question['source'],
            question['user_id']
        )
        # use .get() with default value of None if 'last_edit_date' does not exist
        self.cursor.execute(insert_query, data_tuple)
        self.connection.commit()

    def get_or_create_tag(self, tag_name):
        select_query = "SELECT tag_id FROM Tags WHERE tag_name = %s"
        self.cursor.execute(select_query, (tag_name,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            insert_query = "INSERT IGNORE INTO Tags (tag_name) VALUES (%s)"
            self.cursor.execute(insert_query, (tag_name,))
            self.connection.commit()
            return self.cursor.lastrowid

    def insert_question_tag(self, question_id, tag_id):
        insert_query = "INSERT IGNORE INTO QuestionTags (question_id, tag_id) VALUES (%s, %s)"
        self.cursor.execute(insert_query, (question_id, tag_id))
        self.connection.commit()

    def insert_tags(self, question_id, tags):
        for tag_name in tags:
            tag_id = self.get_or_create_tag(tag_name)
            self.insert_question_tag(question_id, tag_id)

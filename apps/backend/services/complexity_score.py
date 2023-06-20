import os
from dotenv import load_dotenv
from mongoengine import connect
from pymongo import UpdateOne
from textblob import TextBlob
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import nltk
import string
import re
from urllib.parse import quote_plus
from textstat import flesch_kincaid_grade, polysyllabcount
from apps.backend.database import Question
from mongoengine.errors import OperationError

nltk.download('punkt')
nltk.download('stopwords')

load_dotenv()

# Replace these with your MongoDB settings
db_name = quote_plus(os.environ["MONGO_DB_NAME"])
username = quote_plus(os.environ["MONGO_DB_USER"])
password = quote_plus(os.environ["MONGO_DB_PASSWORD"])
host = os.environ["MONGO_DB_HOST"]


class ComplexityAnalyzer:
    stop_words = set(stopwords.words('english'))

    @staticmethod
    def normalize(value: float, max_value: float) -> float:
        """ Normalize a value to range between 0 and 1 """
        return value / max_value if max_value else 0

    def text_complexity(self, text: str, tags_count: int = 0) -> float:
        """ Calculate the complexity of a text """

        # Complexity based on the length of the text
        max_length = 7000  # Ideally, you should calculate this based on your data
        length_complexity = self.normalize(len(text), max_length)

        # Complexity based on the number of stop words
        words = word_tokenize(text.lower())
        stop_words_count = len([word for word in words if word in self.stop_words])
        stop_words_complexity = self.normalize(stop_words_count, len(words))

        # Complexity based on the number of punctuation marks
        punctuation_count = len([char for char in text if char in string.punctuation])
        punctuation_complexity = self.normalize(punctuation_count, len(text))

        # Complexity based on vocabulary richness
        vocabulary_richness = len(set(words)) / len(words) if words else 0

        # Complexity based on the number of sentences
        sentences = sent_tokenize(text)
        sentence_complexity = self.normalize(len(sentences), 50)  # 50 is an arbitrary max value for sentences

        # Complexity based on the sentiment of the text
        sentiment = TextBlob(text).sentiment
        sentiment_complexity = (1 - sentiment.polarity) / 2  # convert [-1, 1] to [0, 1]

        # Complexity based on the Flesch-Kincaid readability score
        fk_score = flesch_kincaid_grade(text)
        fk_complexity = self.normalize(fk_score, 20)  # 20 is an arbitrary max value for FK score

        # Complexity based on the polysyllabic words
        polysyllab_count = polysyllabcount(text)
        polysyllab_complexity = self.normalize(polysyllab_count, len(words))

        # Complexity based on the code snippets
        code_snippets_count = len(re.findall(r'```[^```]*```', text)) + len(
            re.findall(r'<code>(.*?)</code>', text, re.DOTALL))
        code_snippets_complexity = self.normalize(code_snippets_count,
                                                  10)  # 10 is an arbitrary max value for code snippets

        # Complexity based on the math formulas
        math_formulas_count = len(re.findall(r'\$[^$]*\$', text))
        math_formulas_complexity = self.normalize(math_formulas_count,
                                                  10)  # 10 is an arbitrary max value for math formulas

        # Complexity based on the tags count
        tags_complexity = self.normalize(tags_count, 5)  # 5 is an arbitrary max value for tags

        # Calculate total complexity
        total_complexity = (
                0.15 * length_complexity +
                0.05 * stop_words_complexity +
                0.05 * punctuation_complexity +
                0.15 * vocabulary_richness +
                0.05 * sentence_complexity +
                0.05 * sentiment_complexity +
                0.15 * fk_complexity +
                0.1 * polysyllab_complexity +
                0.1 * code_snippets_complexity +
                0.1 * math_formulas_complexity +
                0.05 * tags_complexity
        )

        return round(total_complexity, 4)

    def update_question_complexity(self, batch_size=1000):
        """ Update the complexity of all questions in the database """

        # Establish the connection
        connect(db=db_name, host=f'mongodb+srv://{username}:{password}@{host}/{db_name}?retryWrites=true&w=majority')

        try:
            questions = Question.objects(complexity_score__exists=False).no_cache()  # disable cache
            question_count = questions.count()

            for i in range(0, question_count, batch_size):
                question_batch = questions[i:i + batch_size]
                updates = []
                for question in question_batch:
                    complexity = self.text_complexity(question.body, len(question.tags))
                    updates.append(
                        UpdateOne({'_id': question.question_id}, {'$set': {'complexity_score': complexity}})
                    )

                if updates:
                    try:
                        Question._get_collection().bulk_write(updates, ordered=False)
                    except OperationError as oe:
                        print(f"An error occurred while updating question complexity: {oe}")

        except Exception as e:
            print(f"An error occurred while updating question complexity: {e}")

    def calculate_complexity(self, text: str, tags_count: int = 0):
        """ Calculate and return the complexity score for the provided text and tags count """
        return self.text_complexity(text, tags_count)

from database_manager import DatabaseManager
from stackoverflow_client import StackOverflowClient


def main():
    # Initialize a DatabaseManager instance with your database credentials
    database_manager = DatabaseManager('root', '', 'localhost', 'stack_overflow_analysis')

    # Create tables if they don't exist
    database_manager.create_tables()

    # Initialize a StackOverflowClient instance with the tags you're interested in
    tags = ['python', 'data-science', 'machine-learning', 'deep-learning', 'neural-network', 'classification',
            'keras', 'nlp', 'scikit-learn', 'tensorflow', 'time-series', 'regression', 'r', 'dataset',
            'cnn', 'clustering', 'pandas', 'data-mining', 'predictive-modeling', 'lstm', 'statistics',
            'feature-selection', 'data', 'random-forest', 'machine-learning-model', 'linear-regression',
            'data-cleaning', 'rnn', 'image-classification', 'convolutional-neural-network', 'decision-trees',
            'xgboost', 'logistic-regression', 'visualization', 'training', 'pytorch', 'data-science-model',
            'feature-engineering', 'computer-vision', 'cross-validation', 'reinforcement-learning', 'svm',
            'text-mining', 'multiclass-classification', 'class-imbalance', 'loss-function', 'preprocessing',
            'optimization', 'recommender-system', 'word-embeddings', 'bigdata']
    stackoverflow_client = StackOverflowClient(tags)

    # Fetch questions from the API and insert them into the database
    for items in stackoverflow_client.fetch_all_questions():
        for question in items:
            try:
                if question['score'] > 0 and 'owner' in question and 'user_id' in question['owner']:
                    database_manager.insert_user(question['owner'])
                    question['user_id'] = question['owner']['user_id']
                    question['source'] = 'stackoverflow'
                    database_manager.insert_question(question)
                    database_manager.insert_tags(question['question_id'], question['tags'])
            except Exception as ex:
                print(f"Error Occurred: {ex}")
                print(question)


if __name__ == "__main__":
    main()

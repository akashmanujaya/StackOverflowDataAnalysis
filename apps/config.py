import os
from decouple import config
from dotenv.main import load_dotenv
from mongoengine import connect, disconnect

load_dotenv()


class Config(object):
    basedir = os.path.abspath(os.path.dirname(__file__))

    # Set up the App SECRET_KEY
    SECRET_KEY = config('SECRET_KEY', default='S#perS3crEt_007')

    # MongoDB database
    MONGODB_SETTINGS = {
        'db': os.environ["MONGO_DB_NAME"],
        'host': os.environ["MONGO_DB_HOST"],
        'port': int(os.environ["MONGO_DB_PORT"]),
        # 'username': os.environ["MONGO_DB_USER"],
        # 'password': os.environ["MONGO_DB_PASSWORD"]
    }


class ProductionConfig(Config):
    DEBUG = False

    # Security
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600


class DebugConfig(Config):
    DEBUG = True


# Load all possible configurations
config_dict = {
    'Production': ProductionConfig,
    'Debug': DebugConfig
}


def initiate_connection():
    con = Config()
    mongodb_settings = con.MONGODB_SETTINGS

    disconnect()
    # connect(host=f"mongodb+srv://{mongodb_settings['username']}:{mongodb_settings['password']}@{mongodb_settings['host']}/{mongodb_settings['db']}?retryWrites=true&w=majority")
    connect(
        db=mongodb_settings['db'],  # Replace with your database name
        host='localhost',  # Replace with your MongoDB server host
        port=27017,  # Replace with your MongoDB server port
        # username='your_username',  # Replace with your MongoDB username if required
        # password='your_password',  # Replace with your MongoDB password if required
    )


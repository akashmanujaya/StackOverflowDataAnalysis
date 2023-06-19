import os
from decouple import config
from dotenv.main import load_dotenv

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
        'username': os.environ["MONGO_DB_USER"],
        'password': os.environ["MONGO_DB_PASSWORD"]
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

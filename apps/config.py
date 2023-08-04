import os
from decouple import config
from dotenv.main import load_dotenv
from mongoengine import connect, disconnect_all

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


def initiate_connection():
    con = Config()
    mongodb_settings = con.MONGODB_SETTINGS

    try:
        disconnect_all()
        connect(
            db=mongodb_settings['db'],
            host=mongodb_settings['host'],
            port=mongodb_settings['port'],
            # username=mongodb_settings['username'],
            # password=mongodb_settings['password'],
            # authentication_source=mongodb_settings['db'],
        )
    except Exception as ex:
        print(f"Error: {ex}")


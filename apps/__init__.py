from flask import Flask
from importlib import import_module
from apps.backend.database import db

from mongoengine import connect, disconnect


def register_blueprints(app):
    module = import_module('apps.home.routes')
    app.register_blueprint(module.blueprint)


def create_app(config):
    app = Flask(__name__)
    app.app_context().push()
    app.config.from_object(config)
    handle_database_connection(app.config['MONGODB_SETTINGS'])

    register_blueprints(app)
    return app


def handle_database_connection(mongodb_settings):
    disconnect()
    # connect(host=f"mongodb+srv://{mongodb_settings['username']}:{mongodb_settings['password']}@{mongodb_settings['host']}/{mongodb_settings['db']}?retryWrites=true&w=majority")
    connect(
        db=mongodb_settings['db'],  # Replace with your database name
        host='localhost',  # Replace with your MongoDB server host
        port=27017,  # Replace with your MongoDB server port
        # username='your_username',  # Replace with your MongoDB username if required
        # password='your_password',  # Replace with your MongoDB password if required
    )
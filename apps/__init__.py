from flask import Flask
from importlib import import_module
from apps.backend.database import db


def register_blueprints(app):
    module = import_module('apps.home.routes')
    app.register_blueprint(module.blueprint)


def create_app(config):
    app = Flask(__name__)
    app.app_context().push()
    app.config.from_object(config)
    db.init_app(app)
    register_blueprints(app)
    return app

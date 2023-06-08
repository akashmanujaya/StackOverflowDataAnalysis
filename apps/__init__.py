# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from importlib import import_module


db = SQLAlchemy()


def register_blueprints(app):
    module = import_module('apps.home.routes')
    app.register_blueprint(module.blueprint)


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    register_blueprints(app)
    return app

# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from flask import render_template, request
from jinja2 import TemplateNotFound
from apps.backend.tag_service import get_popular_tags, get_tag_data


@blueprint.route('/')
def index():
    return render_template('home/index.html', segment='index')


@blueprint.route('/api/tags')
def tags():
    return get_popular_tags()

@blueprint.route('/api/tags/<tag_name>')
def tag_data(tag_name):
    return get_tag_data(tag_name)

@blueprint.route('/<template>')
def route_template(template):
    try:

        if not template.endswith('.html'):
            pass

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):
    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None

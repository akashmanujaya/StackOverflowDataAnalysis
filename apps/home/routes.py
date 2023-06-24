from apps.home import blueprint
from flask import render_template, request
from jinja2 import TemplateNotFound
from apps.backend.api import *


@blueprint.route('/')
def index():
    return render_template('home/index.html', segment='index')


@blueprint.route('/complexity')
def complexity_score():
    return render_template('home/complexity.html', segment='complexity')


@blueprint.route('/api/complexity_scores')
def get_complexity_hist():
    return get_complexity_scores()


@blueprint.route('/api/score_complexity')
def get_score_vs_complexity():
    return get_score_complexity()


@blueprint.route('/api/tags')
def tags():
    return get_popular_tags()


@blueprint.route('/api/tags/<tag_name>')
def tag_data(tag_name):
    return get_tag_data(tag_name)


@blueprint.route('/api/complexity_quartile_over_time')
def complexity_quartile_over_time():
    return get_complexity_quartile_over_time()


@blueprint.route('/api/calculate_complexity_score', methods=['POST'])
def calculate_complexity_score():
    data = request.form['question']
    score = get_calculated_com_score(data)
    return jsonify({'score': score})


@blueprint.route('/api/tag_statistics')
def tag_statistics():
    return get_tag_statistics()


@blueprint.route('/api/top_users')
def top_users():
    return get_top_users()


@blueprint.route('/api/top_questions')
def top_questions():
    return get_top_questions()


# @blueprint.route('/<template>')
# def route_template(template):
#     try:
#         if not template.endswith('.html'):
#             pass
#
#         # Detect the current page
#         segment = get_segment(request)
#
#         # Serve the file (if exists) from app/templates/home/FILE.html
#         return render_template("home/" + template, segment=segment)
#
#     except TemplateNotFound:
#         return render_template('home/page-404.html'), 404
#
#     except:
#         return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(req):
    try:
        segment = req.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None

from datetime import datetime, timedelta

from apps.home import blueprint
from flask import render_template, request, current_app, make_response
from apps.backend.api import *


@blueprint.route('/')
def index():
    return render_template('home/index.html', segment='index')


@blueprint.route('/complexity')
def complexity_score():
    return render_template('home/complexity.html', segment='complexity')


@blueprint.route('/predictions')
def predictions():
    return render_template('home/predictions.html', segment='predictions')


@blueprint.route('/ngram')
def ngrqm():
    return render_template('home/ngram_viewer.html', segment='ngram')


@blueprint.route('/about-us')
def test():
    return render_template('home/about.html', segment='about')


@blueprint.route('/api/get_coverage')
def get_coverage():
    try:
        coverage_data = calculate_tag_coverage()

        if 'error' in coverage_data:
            return coverage_data, 500

        return jsonify(coverage_data)

    except Exception as ex:
        return jsonify({'error': f'Something went wrong: {ex}'}), 500


@blueprint.route('/api/get_summary')
def get_summary_cards_data():
    try:
        coverage_data = get_summary()

        if 'error' in coverage_data:
            return coverage_data, 500

        return jsonify(coverage_data)

    except Exception as ex:
        return jsonify({'error': f'Something went wrong: {ex}'}), 500


@blueprint.route('/api/tag_percentage')
def tag_percentage():
    try:
        tags = request.args.get('tags').split(',')
        start_year = int(request.args.get('start_year'))
        end_year = int(request.args.get('end_year'))

        response_data = get_tag_percentage(tags, start_year, end_year)

        if 'error' in response_data:
            return response_data, 500

        return jsonify(response_data)
    except Exception as ex:
        return jsonify({'error': f'Something went wrong: {ex}'}), 500


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
    question = request.form['question']
    tags_count = 0

    if request.form['tags']:
        # Parse the tags data from the AJAX request payload
        tags = json.loads(request.form['tags'])

        # Calculate the number of tags
        tags_count = len(tags)
    score = get_calculated_com_score(question, tags_count)
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


@blueprint.route('/api/tag_prediction/<tag_name>')
def tag_prediction(tag_name):
    return get_prediction(tag_name)


@blueprint.route('/api/prediction_results')
def prediction_results():
    try:
        return get_prediction_results()
    except Exception as ex:
        return jsonify({'error': f'Something went wrong: {ex}'}), 500


@blueprint.route('/sitemap.xml', methods=['GET'])
def sitemap():
    """Generate sitemap.xml. Makes a list of urls and date modified."""
    pages = []
    ten_days_ago = (datetime.now() - timedelta(days=7)).isoformat() + 'Z'  # 'Z' indicates UTC time
    # static pages
    for rule in current_app.url_map.iter_rules():
        if "GET" in rule.methods and len(rule.arguments) == 0:
            pages.append(
                [rule.rule, ten_days_ago]
            )

    sitemap_xml = render_template('sitemap_template.xml', pages=pages)
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"

    return response


@blueprint.app_errorhandler(403)
def forbidden(error):
    return render_template('home/errors/403.html'), 403


@blueprint.app_errorhandler(404)
def page_not_found(error):
    return render_template('home/errors/404.html'), 404


@blueprint.app_errorhandler(500)
def internal_server_error(error):
    return render_template('home/errors/500.html'), 500


# Helper - Extract current page name from request
def get_segment(req):
    try:
        segment = req.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None




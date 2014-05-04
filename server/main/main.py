# -*- coding: utf-8 -*-
from google.appengine.api import mail
from flaskext import wtf
import flask
from werkzeug.wsgi import DispatcherMiddleware
import config
import model
import util
from google.appengine.ext import ndb
from client_auth import mobile_api
from helpers import JSONEncoder



app = flask.Flask(__name__)
app.config.from_object(config)
app.jinja_env.line_statement_prefix = '#'
app.jinja_env.line_comment_prefix = '##'
app.jinja_env.globals.update(slugify=util.slugify)


import auth
import admin
import breeze_api



################################################################################
# Main page
################################################################################
@app.route('/')
def welcome():
    next_url = util.get_next_url()
    if flask.url_for('welcome') in next_url:
        next_url = flask.url_for('index')
    screenshots = [
        {
            'link': 'https://dl.dropboxusercontent.com/u/51908400/gcdc/landing-page/screenshots/Screenshots_topic.png',
            'title': 'Single Topic View',
            'img_src': 'https://dl.dropboxusercontent.com/u/51908400/gcdc/landing-page/screenshots/Screenshots_topic.png'
        }, {
            'link': 'https://dl.dropboxusercontent.com/u/51908400/gcdc/landing-page/screenshots/Screenshots_20131231_091351.png',
            'title': 'Follow Teams',
            'img_src': 'https://dl.dropboxusercontent.com/u/51908400/gcdc/landing-page/screenshots/Screenshots_20131231_091351.png'
        }, {
            'link': 'https://dl.dropboxusercontent.com/u/51908400/gcdc/landing-page/screenshots/Screenshots_friends.png',
            'title': 'View Friend and their teams from Google+',
            'img_src': 'https://dl.dropboxusercontent.com/u/51908400/gcdc/landing-page/screenshots/Screenshots_friends.png'
        }, {
            'link': 'https://dl.dropboxusercontent.com/u/51908400/gcdc/landing-page/screenshots/Screenshots_dashboard.png',
            'title': 'Dashboard',
            'img_src': 'https://dl.dropboxusercontent.com/u/51908400/gcdc/landing-page/screenshots/Screenshots_dashboard.png'
        },
    ]
    images = [
        {'bg': '/img/landing-page/background-imgaes/bg-2.jpg',
         'cs': '/img/landing-page/container-page/greenball2.png',
         'title':'The reason we love football'},
        {'bg': '/img/landing-page/background-imgaes/bg-3.jpg',
         'cs': '/img/landing-page/container-page/greenball6.png',
         'title': 'Soccer fans hangout'},
        {'bg': '/img/landing-page/background-imgaes/bg-4.jpg',
         'cs': '/img/landing-page/container-page/greenball3.png',
         'title':'Passionate fans on the loose'},
        {'bg': '/img/landing-page/background-imgaes/bg-5.jpg',
         'cs': '/img/landing-page/container-page/greenball5.png',
         'title':'All for the love of the game'},
    ]
    features = [
        {
            'icon': 'location-arrow',
            'name': 'Login Support',
            'content': 'Ability to login with either your regular Google Account or Facebook.'
        }, {
            'icon': 'thumbs-up',
            'name': 'Different teams',
            'content': 'Support for clubs and countries. Local leagues included for you to follow'
        }, {
            'icon': 'pencil',
            'name': 'Post Topics',
            'content': 'Freedom to post topics about teams that you follow. Topics can be edited anytime.'
        }, {
            'icon': 'cloud-download',
            'name': 'Soccer News',
            'content': 'Feeds on the latest update in Soccer are available.'
        }, {
            'icon': 'volume-up',
            'name': 'Share',
            'content': 'Share comments and posts on Google+ . Friends (Google+ login) using the app are shown'
        }, {
            'icon': 'mobile-phone',
            'name': 'Any device',
            'content': 'Optimized view for mobile devices with the same experience.'
        }
    ]
    facebook_signin_url = flask.url_for('signin_facebook', next=next_url)
    google_signin_url = flask.url_for('signin_google', next=next_url)
    google_plus_signin_url = flask.url_for('signin_google_plus', next=next_url)
    return flask.render_template('welcome3.html',
                                 html_class='welcome',
                                 facebook_signin_url=facebook_signin_url,
                                 google_signin_url=google_signin_url,
                                 images=images,
                                 features=features,
                                 screenshots=screenshots,
                                 google_plus_signin_url=google_plus_signin_url,
    )


################################################################################
# Sitemap stuff
################################################################################
@app.route('/sitemap.xml')
def sitemap():
    response = flask.make_response(flask.render_template(
        'sitemap.xml',
        host_url=flask.request.host_url[:-1],
        lastmod=config.CURRENT_VERSION_DATE.strftime('%Y-%m-%d'),
    ))
    response.headers['Content-Type'] = 'application/xml'
    return response


################################################################################
# Profile stuff
################################################################################
class ProfileUpdateForm(wtf.Form):
    name = wtf.TextField('Name',
                         [wtf.validators.required()], filters=[util.strip_filter],
    )
    email = wtf.TextField('Email',
                          [wtf.validators.optional(), wtf.validators.email()],
                          filters=[util.strip_filter],
    )


@app.route('/_s/profile/', endpoint='profile_service')
@app.route('/profile/', methods=['GET', 'POST'])
@auth.login_required
def profile():
    user_db = auth.current_user_db()
    form = ProfileUpdateForm(obj=user_db)

    if form.validate_on_submit():
        form.populate_obj(user_db)
        user_db.put()
        return flask.redirect(flask.url_for('welcome'))

    if flask.request.path.startswith('/_s/'):
        return util.jsonify_model_db(user_db)

    return flask.render_template(
        'profile.html',
        title='Profile',
        html_class='profile',
        form=form,
        user_db=user_db,
        has_json=True,
    )


################################################################################
# Feedback
################################################################################
class FeedbackForm(wtf.Form):
    subject = wtf.TextField('Subject',
                            [wtf.validators.required()], filters=[util.strip_filter],
    )
    message = wtf.TextAreaField('Message',
                                [wtf.validators.required()], filters=[util.strip_filter],
    )
    email = wtf.TextField('Email (optional)',
                          [wtf.validators.optional(), wtf.validators.email()],
                          filters=[util.strip_filter],
    )

@app.route('/feedback/', methods=['GET', 'POST'])
def feedback():
    if not config.CONFIG_DB.feedback_email:
        return flask.abort(418)

    form = FeedbackForm()
    if form.validate_on_submit():
        mail.send_mail(
            sender=config.CONFIG_DB.feedback_email,
            to=config.CONFIG_DB.feedback_email,
            subject='[%s] %s' % (
                config.CONFIG_DB.brand_name,
                form.subject.data,
            ),
            reply_to=form.email.data or config.CONFIG_DB.feedback_email,
            body='%s\n\n%s' % (form.message.data, form.email.data)
        )
        flask.flash('Thank you for your feedback!', category='success')
        return flask.redirect(flask.url_for('welcome'))
    if not form.errors and auth.current_user_id() > 0:
        form.email.data = auth.current_user_db().email

    return flask.render_template(
        'feedback.html',
        title='Feedback',
        html_class='feedback',
        form=form,
    )


################################################################################
# User Stuff
################################################################################
@app.route('/_s/user/', endpoint='user_list_service')
@app.route('/user/')
@auth.admin_required
def user_list():
    user_dbs, more_cursor = util.retrieve_dbs(
        model.User.query(),
        limit=util.param('limit', int),
        cursor=util.param('cursor'),
        order=util.param('order') or '-created',
        name=util.param('name'),
        admin=util.param('admin', bool),
        author=util.param('author', bool)
    )

    if flask.request.path.startswith('/_s/'):
        return util.jsonify_model_dbs(user_dbs, more_cursor)

    return flask.render_template(
        'user_list.html',
        html_class='user',
        title='User List',
        user_dbs=user_dbs,
        more_url=util.generate_more_url(more_cursor),
        has_json=True,
    )

################################################################################
# Error Handling
################################################################################
@app.errorhandler(400)  # Bad Request
@app.errorhandler(401)  # Unauthorized
@app.errorhandler(403)  # Forbidden
@app.errorhandler(404)  # Not Found
@app.errorhandler(405)  # Method Not Allowed
@app.errorhandler(410)  # Gone
@app.errorhandler(418)  # I'm a Teapot
@app.errorhandler(500)  # Internal Server Error
def error_handler(e):
    try:
        e.code
    except:
        class e(object):
            code = 500
            name = 'Internal Server Error'

    if flask.request.path.startswith('/_s/'):
        return util.jsonpify({
            'status': 'error',
            'error_code': e.code,
            'error_name': e.name.lower().replace(' ', '_'),
            'error_message': e.name,
        }), e.code

    return flask.render_template(
        'error.html',
        title='Error %d (%s)!!1' % (e.code, e.name),
        html_class='error-page',
        error=e,
    ), e.code


@app.route('/gteam/<string:name>')
def moment_team(name):
    team = model.Team.retrieve_one_by('name', name)
    followers = model.User.query(model.User.teams == team.key).fetch()

    return flask.render_template(
        'g+_templates/follow.html',
        team=team,
        count=len(followers),
    )

@app.route('/my-profile')
@auth.login_required
def my_profile():
    user=auth.current_user_db()
    return flask.render_template(
        'g+_templates/profile.html',
        user_db=user,
        comment_counts=len(user.comments),
        followers_count=len(user.teams),
    )


def initialize_channels():
    teams, temp = util.retrieve_dbs(model.Team.query())
    for team in teams:
        util.create_channel(team.name.replace(" ",""))

@app.route('/index')
@app.route('/index/')
@auth.login_required
def index():
    initialize_channels()
    return flask.render_template(
        'welcome2.html'
    )

@app.route('/xml-to-json/', methods=['GET'])
def xml_to_json():
    import xmltodict, json
    QUERY_URL = "http://greenfootball.org/?feed=rss2"
    import requests

    r = requests.get(QUERY_URL)
    return r.json

@app.route('/gtopic/<int:url>')
def moment_topic(url):
    key = ndb.Key('Topic',url)
    topic = key.get()
    return flask.render_template(
        'g+_templates/topics.html',
        topic=topic
    )


application = DispatcherMiddleware(app, {
    '/mobile':     mobile_api
})

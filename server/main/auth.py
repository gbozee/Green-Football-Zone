# -*- coding: utf-8 -*-

from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.api import urlfetch

import functools
import json
import re

import re
import unidecode
import flask
from flaskext import login
from flaskext import oauth
import time
from rauth.service import OAuth2Service

import util
import model
import config

from main import app




################################################################################
# Flaskext Login
################################################################################
login_manager = login.LoginManager()


class AnonymousUser(login.AnonymousUserMixin):
    id = 0
    admin = False
    name = 'Anonymous'
    user_db = None

    def key(self):
        return None


login_manager.anonymous_user = AnonymousUser


class FlaskUser(AnonymousUser):
    def __init__(self, user_db):
        self.user_db = user_db
        self.id = user_db.key.id()
        self.name = user_db.name
        self.admin = user_db.admin

    def key(self):
        return self.user_db.key.urlsafe()

    def get_id(self):
        return self.user_db.key.urlsafe()

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.user_db.active

    def is_anonymous(self):
        return False


@login_manager.user_loader
def load_user(key):
    user_db = ndb.Key(urlsafe=key).get()
    if user_db:
        return FlaskUser(user_db)
    return None


login_manager.init_app(app)


def current_user_id():
    return login.current_user.id


def current_user_key():
    return login.current_user.user_db.key if login.current_user.user_db else None


def current_user_db():
    return login.current_user.user_db


def is_logged_in():
    return login.current_user.id != 0


################################################################################
# Decorators
################################################################################
def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kws):
        if is_logged_in():
            return f(*args, **kws)
        if flask.request.path.startswith('/_s/'):
            return flask.abort(401)
        return flask.redirect(flask.url_for('welcome', next=flask.request.url))

    return decorated_function


def admin_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kws):
        if is_logged_in() and current_user_db().admin:
            return f(*args, **kws)
        if not is_logged_in() and flask.request.path.startswith('/_s/'):
            return flask.abort(401)
        if not is_logged_in():
            return flask.redirect(flask.url_for('welcome', next=flask.request.url))
        return flask.abort(403)

    return decorated_function


def author_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if is_logged_in() and current_user_db().author:
            return f(*args, **kwargs)
            #if flask.request.path.startswith('/_s/'):
        #    return flask.abort(401)

        return flask.redirect(flask.url_for('welcome', next=flask.request.url))

    return decorated_function


################################################################################
# Sign in stuff
################################################################################
@app.route('/login/')
@app.route('/signin/')
def signin():
    next_url = util.get_next_url()
    if flask.url_for('signin') in next_url:
        next_url = flask.url_for('welcome')
    facebook_signin_url = flask.url_for('signin_facebook', next=next_url)
    google_signin_url = flask.url_for('signin_google', next=next_url)
    google_plus_signin_url = flask.url_for('signin_google_plus', next=next_url)

    bitbucket_signin_url = flask.url_for('signin_bitbucket', next=next_url)
    dropbox_signin_url = flask.url_for('signin_dropbox', next=next_url)

    github_signin_url = flask.url_for('signin_github', next=next_url)

    linkedin_signin_url = flask.url_for('signin_linkedin', next=next_url)
    #twitter_signin_url = flask.url_for('signin_twitter', next=next_url)
    vk_signin_url = flask.url_for('signin_vk', next=next_url)
    windowslive_signin_url = flask.url_for('signin_windowslive', next=next_url)

    return flask.render_template(
        'signin.html',
        title='Please sign in',
        html_class='signin',
        bitbucket_signin_url=bitbucket_signin_url,
        dropbox_signin_url=dropbox_signin_url,
        facebook_signin_url=facebook_signin_url,
        github_signin_url=github_signin_url,
        google_signin_url=google_signin_url,
        google_plus_signin_url=google_plus_signin_url,
        linkedin_signin_url=linkedin_signin_url,
        #twitter_signin_url=twitter_signin_url,
        vk_signin_url=vk_signin_url,
        windowslive_signin_url=windowslive_signin_url,
        next_url=next_url,
    )


@app.route('/signout/')
def signout():
    login.logout_user()
    flask.flash(u'You have been signed out.')
    return flask.redirect(flask.url_for('welcome'))


################################################################################
# Google
################################################################################
@app.route('/signin/google/')
def signin_google():
    google_url = users.create_login_url(
        flask.url_for('google_authorized', next=util.get_next_url())
    )
    return flask.redirect(google_url)


@app.route('/_s/callback/google/authorized/')
def google_authorized():
    google_user = users.get_current_user()
    if google_user is None:
        flask.flash(u'You denied the request to sign in.')
        return flask.redirect(util.get_next_url())

    user_db = retrieve_user_from_google(google_user)
    return signin_user_db(user_db)


def retrieve_user_from_google(google_user):
    auth_id = 'federated_%s' % google_user.user_id()

    user_db = model.User.retrieve_one_by('email', google_user.email())
    if user_db:
        if auth_id not in user_db.auth_ids:
            user_db.auth_ids.append(auth_id)
            user_db.username = google_user.nickname()
        user_db.put()
        return user_db

    user_db = model.User.retrieve_one_by('auth_ids', auth_id)
    if user_db:
        if user_db.email == google_user.email():
            return user_db
        if not user_db.admin and users.is_current_user_admin():
            user_db.admin = True
            user_db.put()
        return user_db


    return create_user_db(
        auth_id,
        google_user.nickname().split('@')[0].replace('.', ' ').title(),
        google_user.nickname(),
        google_user.email(),
        admin=users.is_current_user_admin(),
    )


################################################################################
# Twitter
################################################################################
twitter_oauth = oauth.OAuth()

twitter = twitter_oauth.remote_app(
    'twitter',
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authorize',
    consumer_key=config.CONFIG_DB.twitter_consumer_key,
    consumer_secret=config.CONFIG_DB.twitter_consumer_secret,
)


@app.route('/_s/callback/twitter/oauth-authorized/')
@twitter.authorized_handler
def twitter_authorized(resp):
    if resp is None:
        flask.flash(u'You denied the request to sign in.')
        return flask.redirect(util.get_next_url())

    flask.session['oauth_token'] = (
        resp['oauth_token'],
        resp['oauth_token_secret'],
    )
    user_db = retrieve_user_from_twitter(resp)
    return signin_user_db(user_db)


@twitter.tokengetter
def get_twitter_token():
    return flask.session.get('oauth_token')


@app.route('/signin/twitter/')
def signin_twitter():
    flask.session.pop('oauth_token', None)
    try:
        return twitter.authorize(
            callback=flask.url_for('twitter_authorized', next=util.get_next_url()),
        )
    except:
        flask.flash(
            'Something went terribly wrong with Twitter sign in. Please try again.',
            category='danger',
        )
        return flask.redirect(flask.url_for('signin', next=util.get_next_url()))


def retrieve_user_from_twitter(response):
    auth_id = 'twitter_%s' % response['user_id']
    user_db = model.User.retrieve_one_by('auth_ids', auth_id)
    if user_db:
        return user_db

    return create_user_db(
        auth_id,
        response['screen_name'],
        response['screen_name'],
    )


################################################################################
# Facebook
################################################################################
facebook_oauth = oauth.OAuth()

facebook = facebook_oauth.remote_app(
    'facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=config.CONFIG_DB.facebook_app_id,
    consumer_secret=config.CONFIG_DB.facebook_app_secret,
    #consumer_key=config.CONFIG_DB.facebook_app_id,
    #consumer_secret=config.CONFIG_DB.facebook_app_secret,
    request_token_params={'scope': 'email'},
)


@app.route('/_s/callback/facebook/oauth-authorized/')
@facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            flask.request.args['error_reason'],
            flask.request.args['error_description']
        )
    flask.session['oauth_token'] = (resp['access_token'], '')
    me = facebook.get('/me')
    user_db = retrieve_user_from_facebook(me.data)
    return signin_user_db(user_db)


@facebook.tokengetter
def get_facebook_oauth_token():
    return flask.session.get('oauth_token')


@app.route('/signin/facebook/')
def signin_facebook():
    return facebook.authorize(callback=flask.url_for('facebook_authorized',
                                                     next=util.get_next_url(),
                                                     _external=True),
    )


def retrieve_user_from_facebook(response):
    print response
    auth_id = 'facebook_%s' % response['id']

    user_db = model.User.retrieve_one_by('email', response['email'])
    if user_db:
        if auth_id not in user_db.auth_ids:
            user_db.auth_ids.append(auth_id)
            return update_facebook_specific_information(user_db,
                                                 facebook_public_profile_url=response['link'],
                                                 facebook_username=response['username'],
            )
        else:
            return user_db
    user_db = model.User.retrieve_one_by('auth_ids', auth_id)
    if user_db:
        return user_db


    return create_user_db(
        auth_id,
        response['name'],
        response['username'] if 'username' in response else response['id'],
        response['email'],
        facebook_public_profile_url=response['link'],
        facebook_username=response['username'],
    )


################################################################################
# Bitbucket
################################################################################
bitbucket_oauth = oauth.OAuth()

bitbucket = bitbucket_oauth.remote_app(
    'bitbucket',
    base_url='https://api.bitbucket.org/1.0/',
    request_token_url='https://bitbucket.org/!api/1.0/oauth/request_token',
    access_token_url='https://bitbucket.org/!api/1.0/oauth/access_token',
    authorize_url='https://bitbucket.org/!api/1.0/oauth/authenticate',
    consumer_key=config.CONFIG_DB.bitbucket_key,
    consumer_secret=config.CONFIG_DB.bitbucket_secret,
)


@app.route('/_s/callback/bitbucket/oauth-authorized/')
@bitbucket.authorized_handler
def bitbucket_authorized(resp):
    if resp is None:
        return 'Access denied'
    flask.session['oauth_token'] = (
        resp['oauth_token'], resp['oauth_token_secret'])
    me = bitbucket.get('user')
    user_db = retrieve_user_from_bitbucket(me.data['user'])
    return signin_user_db(user_db)


@bitbucket.tokengetter
def get_bitbucket_oauth_token():
    return flask.session.get('oauth_token')


@app.route('/signin/bitbucket/')
def signin_bitbucket():
    flask.session['oauth_token'] = None
    return bitbucket.authorize(
        callback=flask.url_for('bitbucket_authorized',
                               next=util.get_next_url(),
                               _external=True,
        )
    )


def retrieve_user_from_bitbucket(response):
    auth_id = 'bitbucket_%s' % response['username']
    user_db = model.User.retrieve_one_by('auth_ids', auth_id)
    if user_db:
        return user_db
    if response['first_name'] or response['last_name']:
        name = ' '.join((response['first_name'], response['last_name'])).strip()
    else:
        name = response['username']
    return create_user_db(auth_id, name, response['username'])


###############################################################################
# Dropbox
###############################################################################
dropbox_oauth = oauth.OAuth()

dropbox = dropbox_oauth.remote_app(
    'dropbox',
    base_url='https://api.dropbox.com/1/',
    request_token_url=None,
    access_token_url='https://api.dropbox.com/1/oauth2/token',
    access_token_method='POST',
    access_token_params={'grant_type': 'authorization_code'},
    authorize_url='https://www.dropbox.com/1/oauth2/authorize',
    consumer_key=model.Config.get_master_db().dropbox_app_key,
    consumer_secret=model.Config.get_master_db().dropbox_app_secret,
)


@app.route('/_s/callback/dropbox/oauth-authorized/')
@dropbox.authorized_handler
def dropbox_authorized(resp):
    if resp is None:
        return 'Access denied: error=%s error_description=%s' % (
            flask.request.args['error'],
            flask.request.args['error_description'],
        )
    flask.session['oauth_token'] = (resp['access_token'], '')
    me = dropbox.get(
        'account/info',
        headers={'Authorization': 'Bearer %s' % resp['access_token']}
    )
    user_db = retrieve_user_from_dropbox(me.data)
    return signin_user_db(user_db)


@dropbox.tokengetter
def get_dropbox_oauth_token():
    return flask.session.get('oauth_token')


@app.route('/signin/dropbox/')
def signin_dropbox():
    flask.session['oauth_token'] = None
    return dropbox.authorize(
        callback=re.sub(r'^http:', 'https:',
                        flask.url_for('dropbox_authorized', _external=True)
        )
    )


def retrieve_user_from_dropbox(response):
    auth_id = 'dropbox_%s' % response['uid']
    user_db = model.User.retrieve_one_by('auth_ids', auth_id)
    if user_db:
        return user_db

    return create_user_db(
        auth_id,
        response['display_name'],
        unidecode.unidecode(response['display_name']),
    )


################################################################################
# GitHub
################################################################################
github_oauth = oauth.OAuth()

github = github_oauth.remote_app(
    'github',
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    consumer_key=config.CONFIG_DB.github_client_id,
    consumer_secret=config.CONFIG_DB.github_client_secret,
    request_token_params={'scope': 'user:email'},
)


@app.route('/_s/callback/github/oauth-authorized/')
@github.authorized_handler
def github_authorized(resp):
    if resp is None:
        return 'Access denied: error=%s' % flask.request.args['error']
    flask.session['oauth_token'] = (resp['access_token'], '')
    me = github.get('user')
    user_db = retrieve_user_from_github(me.data)
    return signin_user_db(user_db)


@github.tokengetter
def get_github_oauth_token():
    return flask.session.get('oauth_token')


@app.route('/signin/github/')
def signin_github():
    return github.authorize(
        callback=flask.url_for('github_authorized',
                               next=util.get_next_url(),
                               _external=True,
        )
    )


def retrieve_user_from_github(response):
    auth_id = 'github_%s' % str(response['id'])
    user_db = model.User.retrieve_one_by('auth_ids', auth_id)
    if user_db:
        return user_db
    return create_user_db(
        auth_id,
        response['name'] or response['login'],
        response['login'],
        response['email'] or '',
    )


################################################################################
# LinkedIn
################################################################################
linkedin_oauth = oauth.OAuth()

linkedin = linkedin_oauth.remote_app(
    'linkedin',
    base_url='https://api.linkedin.com/v1/',
    request_token_url=None,
    access_token_url='https://www.linkedin.com/uas/oauth2/accessToken',
    access_token_params={'grant_type': 'authorization_code'},
    access_token_method='POST',
    authorize_url='https://www.linkedin.com/uas/oauth2/authorization',
    consumer_key=config.CONFIG_DB.linkedin_api_key,
    consumer_secret=config.CONFIG_DB.linkedin_secret_key,
    request_token_params={
        'scope': 'r_basicprofile r_emailaddress',
        'state': util.uuid(),
    },
)


@app.route('/_s/callback/linkedin/oauth-authorized/')
@linkedin.authorized_handler
def linkedin_authorized(resp):
    if resp is None:
        return 'Access denied: error=%s error_description=%s' % (
            flask.request.args['error'],
            flask.request.args['error_description'],
        )
    flask.session['access_token'] = (resp['access_token'], '')
    fields = 'id,first-name,last-name,email-address'
    profile_url = '%speople/~:(%s)?oauth2_access_token=%s' % (
        linkedin.base_url, fields, resp['access_token'],
    )
    result = urlfetch.fetch(
        profile_url,
        headers={'x-li-format': 'json', 'Content-Type': 'application/json'}
    )
    try:
        content = flask.json.loads(result.content)
    except ValueError:
        return "Unknown error: invalid response from LinkedIn"
    if result.status_code != 200:
        return 'Unknown error: status=%s message=%s' % (
            content['status'], content['message'],
        )
    user_db = retrieve_user_from_linkedin(content)
    return signin_user_db(user_db)


@linkedin.tokengetter
def get_linkedin_oauth_token():
    return flask.session.get('access_token')


@app.route('/signin/linkedin/')
def signin_linkedin():
    flask.session['access_token'] = None
    return linkedin.authorize(
        callback=flask.url_for(
            'linkedin_authorized',
            next=util.get_next_url(),
            _external=True,
        ),
    )


def retrieve_user_from_linkedin(response):
    auth_id = 'linkedin_%s' % response['id']
    user_db = model.User.retrieve_one_by('auth_ids', auth_id)
    if user_db:
        return user_db
    full_name = ' '.join([response['firstName'], response['lastName']]).strip()
    return create_user_db(
        auth_id,
        full_name,
        response['emailAddress'] or unidecode.unidecode(full_name),
        response['emailAddress'],
    )


###############################################################################
# VK
###############################################################################
vk_oauth = oauth.OAuth()

vk = vk_oauth.remote_app(
    'vk',
    base_url='https://api.vk.com/',
    request_token_url=None,
    access_token_url='https://oauth.vk.com/access_token',
    authorize_url='https://oauth.vk.com/authorize',
    consumer_key=model.Config.get_master_db().vk_app_id,
    consumer_secret=model.Config.get_master_db().vk_app_secret,
)


@app.route('/_s/callback/vk/oauth-authorized/')
@vk.authorized_handler
def vk_authorized(resp):
    if resp is None:
        return 'Access denied: error=%s error_description=%s' % (
            flask.request.args['error'],
            flask.request.args['error_description'],
        )
    access_token = resp['access_token']
    flask.session['oauth_token'] = (access_token, '')
    me = vk.get('/method/getUserInfoEx', data={'access_token': access_token})
    user_db = retrieve_user_from_vk(me.data['response'])
    return signin_user_db(user_db)


@vk.tokengetter
def get_vk_oauth_token():
    return flask.session.get('oauth_token')


@app.route('/signin/vk/')
def signin_vk():
    return vk.authorize(
        callback=flask.url_for(
            'vk_authorized',
            scope='notify',
            next=util.get_next_url(),
            _external=True,
        )
    )


def retrieve_user_from_vk(response):
    auth_id = 'vk_%s' % response['user_id']
    user_db = model.User.retrieve_one_by('auth_ids', auth_id)
    if user_db:
        return user_db

    return create_user_db(
        auth_id,
        response['user_name'],
        unidecode.unidecode(response['user_name']),
    )


###############################################################################
# Windows Live
###############################################################################
windowslive_oauth = oauth.OAuth()

windowslive = windowslive_oauth.remote_app(
    'windowslive',
    base_url='https://apis.live.net/v5.0/',
    request_token_url=None,
    access_token_url='https://login.live.com/oauth20_token.srf',
    access_token_method='POST',
    access_token_params={'grant_type': 'authorization_code'},
    authorize_url='https://login.live.com/oauth20_authorize.srf',
    consumer_key=model.Config.get_master_db().windowslive_client_id,
    consumer_secret=model.Config.get_master_db().windowslive_client_secret,
    request_token_params={'scope': 'wl.emails'},
)


@app.route('/_s/callback/windowslive/oauth-authorized/')
@windowslive.authorized_handler
def windowslive_authorized(resp):
    if resp is None:
        return 'Access denied: error=%s error_description=%s' % (
            flask.request.args['error'],
            flask.request.args['error_description'],
        )
    flask.session['oauth_token'] = (resp['access_token'], '')
    me = windowslive.get(
        'me',
        data={'access_token': resp['access_token']},
        headers={'accept-encoding': 'identity'},
    ).data
    if me.get('error'):
        return 'Unknown error: error:%s error_description:%s' % (
            me['code'],
            me['message'],
        )
    user_db = retrieve_user_from_windowslive(me)
    return signin_user_db(user_db)


@windowslive.tokengetter
def get_windowslive_oauth_token():
    return flask.session.get('oauth_token')


@app.route('/signin/windowslive/')
def signin_windowslive():
    return windowslive.authorize(
        callback=flask.url_for(
            'windowslive_authorized',
            next=util.get_next_url(),
            _external=True,
        )
    )


def retrieve_user_from_windowslive(response):
    auth_id = 'windowslive_%s' % response['id']
    user_db = model.User.retrieve_one_by('auth_ids', auth_id)
    if user_db:
        return user_db
    email = response['emails']['preferred'] or response['emails']['account']
    return create_user_db(
        auth_id,
        response['name'] or '',
        email,
        email=email,
    )

################################################################################
# Google Plus
################################################################################
#google_plus_oauth = oauth.OAuth()
GOOGLE_API_URL = 'https://www.googleapis.com/oauth2/v2/'

GOOGLE_PLUS_API_URL = 'https://www.googleapis.com/plus/v1/'

client_id = config.CONFIG_DB.google_plus_consumer_id
client_secret = config.CONFIG_DB.google_plus_consumer_secret

google_plus = OAuth2Service(
    name='google_plus',
    client_id='183001439932.apps.googleusercontent.com',
    client_secret='n-Cns6XSpeepvDed1cHsM37p',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    base_url='None'
)





visible_actions = (' ').join([
    'https://schemas.google.com/AddActivity',
    'http://schemas.google.com/ReviewActivity',
    'http://schemas.google.com/CommentActivity'])

scope = (' ').join([
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/plus.login',
])


@app.route('/signin/google_plus/')
def signin_google_plus():
    redirect_uri = flask.url_for('authorized', _external=True)
    params = {
        'scope': scope,
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        #'redirect_uri': '',
        #'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
        'access_type': 'offline',
        'approval_prompt': 'force',
        'request_visible_actions': visible_actions
    }

    return flask.redirect(google_plus.get_authorize_url(**params))


@app.route('/oauth2callback')
def authorized():
    # check to make sure the user authorized the request
    if not 'code' in flask.request.args:
        flask.flash('You did not authorize the request')
        return flask.redirect(flask.url_for('welcome'))
    code = flask.request.args['code']

    # make a request for the access token credentials using code
    redirect_uri = flask.url_for('authorized', _external=True)
    #redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
    data = {
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri,
    }

    response = google_plus.get_raw_access_token(data=data)
    response = response.json()
    flask.session['oauth_token'] = (response['access_token'],
                                    response['refresh_token'],)
    print response

    user_db = retrieve_user_from_google_plus(response)
    return signin_user_db(user_db)


def retrieve_user_from_google_plus(response):
    expires_at = int(time.time()) + response['expires_in']
    try:
        refresh_token = response['refresh_token']
    except:
        refresh_token = None

    google_plus_auth = google_plus.get_session(token=response['access_token'])

    # the user object as returned by google
    result = google_plus_auth.get(GOOGLE_API_URL + 'userinfo').json()
    print result
    email = result['email']
    user_db = model.User.retrieve_one_by('email', email)
    auth_id = 'google_plus_%s' % result['id']
    if 'picture' in result:
        x = result['picture']
    else:
        x = ""
    if user_db:
        if auth_id in user_db.auth_ids:
            return user_db
        else:
            user_db.auth_ids.append(auth_id)

            return update_google_plus_specific_information(user_db,
                                                       google_plus_id=result['id'],
                                                       google_display_name=result['name'],
                                                       google_image_url=x,
                                                       google_public_profile_url=result['link'],
                                                       access_token=response['access_token'],
                                                       refresh_token=response['refresh_token'],
                                                       expires_at=expires_at)
    else:
        return create_user_db(auth_id,
                              result['name'],
                              result['name'],
                              result['email'],
                              google_plus_id=result['id'],
                              google_display_name=result['name'],
                              google_image_url=x,
                              google_public_profile_url=result['link'],
                              access_token=response['access_token'],
                              refresh_token=response['refresh_token'],
                              expires_at=expires_at
        )


################################################################################
# Helpers
################################################################################
def create_user_db(auth_id, name, username, email='', **params):
    username = re.sub(r'_+|-+|\s+', '.', username.split('@')[0].lower().strip())
    new_username = username
    n = 1
    while model.User.retrieve_one_by('username', new_username) is not None:
        new_username = '%s%d' % (username, n)
        n += 1

    user_db = model.User(
        name=name,
        email=email.lower(),
        username=new_username,
        auth_ids=[auth_id],
        **params
    )
    user_db.put()
    return user_db


def update_facebook_specific_information(user, **kwargs):
    for key in kwargs:
        try:
            setattr(user, key, kwargs[key])
        except:
            setattr(user, key, None)
    user.put()
    return user


def update_google_plus_specific_information(user, **kwargs):
    for key in kwargs:
        try:
            setattr(user, key, kwargs[key])
        except:
            setattr(user, key, None)
    user.put()
    return user


@ndb.toplevel
def signin_user_db(user_db):
    if not user_db:
        return flask.redirect(flask.url_for('welcome'))
    flask_user_db = FlaskUser(user_db)
    if login.login_user(flask_user_db):
        user_db.put_async()
        flask.flash('Hello %s, welcome to %s!!!' % (
            user_db.name, config.CONFIG_DB.brand_name,
        ), category='success')
        return flask.redirect(util.get_next_url())
    else:
        flask.flash('Sorry, but you could not sign in.', category='danger')
        return flask.redirect(flask.url_for('welcome'))


#def get_or_create_google_plus_user(google_id, access_token, expires_at, refresh_token, **params):
#    user = model.User.retrieve_one_by('username', google_id['name'])
#    if user is None:
#        user = current_user_db()
#        user.google_display_name = google_id['name']
#        user.google_plus_id = google_id['id']
#        if google_id.has_key('picture'):
#            user.google_public_profile_url = google_id['picture']
#        user.access_token = access_token
#        user.expires_at = expires_at
#        user.refresh_token = refresh_token
#
#    user.put()
#    return user
# -*- coding: utf-8 -*-
from flask import g

from google.appengine.ext import ndb
from uuid import uuid4
import os
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature
import util
import modelx


import flask_httpauth as httpauth
basic_auth = httpauth.HTTPBasicAuth()

@basic_auth.verify_password
def verify_password(email_or_token,password):
    # first try to authenticate by token
    user = User.verify_auth_token(email_or_token)
    if not user:
        return False
    g.user = user
    return True


# The timestamp of the currently deployed version
TIMESTAMP = long(os.environ.get('CURRENT_VERSION_ID').split('.')[1]) >> 28


class ReferenceProperty(ndb.KeyProperty):
    def _validate(self, value):
        if not isinstance(value, ndb.Model):
            raise TypeError('expected an ndb.Model, got %s' % repr(value))

    def _to_base_type(self, value):
        return value.key

    def _from_base_type(self, value):
        return value.get()


class Base(ndb.Model, modelx.BaseX):
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)
    version = ndb.IntegerProperty(default=TIMESTAMP)
    _PROPERTIES = {
        'key',
        'id',
        'version',
        'created',
        'modified',
    }


class Config(Base, modelx.ConfigX):
    analytics_id = ndb.StringProperty(default='')
    announcement_html = ndb.StringProperty(default='')
    announcement_type = ndb.StringProperty(default='info', choices=[
        'info', 'warning', 'success', 'danger',
    ])
    bitbucket_key = ndb.StringProperty(default='')
    bitbucket_secret = ndb.StringProperty(default='')
    brand_name = ndb.StringProperty(default='gae-init')
    dropbox_app_key = ndb.StringProperty(default='')
    dropbox_app_secret = ndb.StringProperty(default='')
    facebook_app_id = ndb.StringProperty(default='')
    facebook_app_secret = ndb.StringProperty(default='')
    feedback_email = ndb.StringProperty(default='')
    flask_secret_key = ndb.StringProperty(default=str(uuid4()).replace('-', ''))
    github_client_id = ndb.StringProperty(default='')
    github_client_secret = ndb.StringProperty(default='')
    linkedin_api_key = ndb.StringProperty(default='')
    linkedin_secret_key = ndb.StringProperty(default='')
    twitter_consumer_key = ndb.StringProperty(default='')
    twitter_consumer_secret = ndb.StringProperty(default='')
    vk_app_id = ndb.StringProperty(default='')
    vk_app_secret = ndb.StringProperty(default='')
    windowslive_client_id = ndb.StringProperty(default='')
    windowslive_client_secret = ndb.StringProperty(default='')
    google_plus_consumer_id = ndb.StringProperty(default='')
    google_plus_consumer_secret = ndb.StringProperty(default='')

    _PROPERTIES = Base._PROPERTIES.union({
        'analytics_id',
        'announcement_html',
        'announcement_type',
        'bitbucket_key',
        'bitbucket_secret',
        'brand_name',
        'dropbox_app_key',
        'dropbox_app_secret',
        'facebook_app_id',
        'facebook_app_secret',
        'feedback_email',
        'flask_secret_key',
        'github_client_id',
        'github_client_secret',
        'linkedin_api_key',
        'linkedin_secret_key',
        'twitter_consumer_key',
        'twitter_consumer_secret',
        'vk_app_id',
        'vk_app_secret',
        'windowslive_client_id',
        'windowslive_client_secret',
        'google_plus_consumer_id',
        'google_plus_consumer_secret',
    })
CLUB = 'club'
COUNTRY = 'country'
types = [CLUB,COUNTRY]
AFRICAN = 'african'
EUROPEAN = 'european'
continent_league = [EUROPEAN,AFRICAN,COUNTRY]


class League(Base, modelx.LeagueX):
    name = ndb.StringProperty(indexed=True, required=True)
    logo = ndb.StringProperty(required=True)
    type = ndb.StringProperty(choices=types, default=CLUB)
    info = ndb.StringProperty(default='')

    _PROPERTIES = Base._PROPERTIES.union({
        'name',
        'logo',
        'type',
        'info',
        'teams'
        'name_url'
    })

    @property
    def teams(self):
        teams_dbs, more_cursor = util.retrieve_dbs(
            Team.query(Team.league == self.key),
            limit=util.param('limit', int),
            cursor=util.param('cursor'),
            order=util.param('order'),
        )
        return teams_dbs


class Team(Base, modelx.TeamX):
    #league = ndb.KeyProperty(kind='League')
    league = ndb.KeyProperty(kind='League')
    c_league = ndb.StringProperty(choices=continent_league, default=EUROPEAN)
    type = ndb.StringProperty(choices=types, default=CLUB)
    position = ndb.IntegerProperty(default=0)
    name = ndb.StringProperty(indexed=True, required=True)
    logo = ndb.StringProperty(indexed=True, required=True)
    #topics = ndb.KeyProperty(kind='Topic', repeated=True)
    followers = ndb.KeyProperty(kind='User', repeated=True)
    coach = ndb.StringProperty(indexed=True)
    admin = ndb.KeyProperty(kind='User')
    follow_url = ndb.StringProperty(default="")
    monitor_likes = ndb.KeyProperty(kind='User', repeated=True)
    likes = ndb.IntegerProperty(default=0)
    dislikes = ndb.IntegerProperty(default=0)
    info = ndb.StringProperty(default='')


    _PROPERTIES = Base._PROPERTIES.union({
        'name',
        'logo',
        'c_league',
        'type',
        'admin',
        'coach',
        'info',
        #'followers'
        'topics',
        'name_url',
        'follow_url',
        #'all_topics'
    })

    @property
    def team_topics(self):
        #return Topic.query(Topic.team == self.key).fetch()
        topics, more_cursor = util.retrieve_dbs(
            Topic.query(Topic.team == self.key),
            limit=util.param('limit', int),
            cursor=util.param('cursor'),
            order=util.param('order'),
        )
        return topics


class DirectedUserToUserEdge(Base):
    """Represents friend links between GreenFootball users."""
    owner_user_id = ndb.IntegerProperty()
    friend_user_id = ndb.IntegerProperty()

config_file = "greenfootballzone4life"
class User(Base, modelx.UserX):
    name = ndb.StringProperty(indexed=True, required=True)
    username = ndb.StringProperty(indexed=True, required=True)
    email = ndb.StringProperty(indexed=True, default='')
    auth_ids = ndb.StringProperty(indexed=True, repeated=True)
    google_image_url = ndb.StringProperty(indexed=True, default='')

    active = ndb.BooleanProperty(default=True)
    admin = ndb.BooleanProperty(default=False)
    author = ndb.BooleanProperty(default=True)
    team_admin = ndb.BooleanProperty(default=False)
    teams = ndb.KeyProperty(kind='Team', repeated=True)
    comments = ndb.KeyProperty(repeated=True)
    facebook_id = ndb.StringProperty(indexed=True)
    facebook_username=ndb.StringProperty(indexed=True)

    google_plus_id = ndb.StringProperty(indexed=True)
    google_display_name = ndb.StringProperty(indexed=True, default='')
    google_public_profile_url = ndb.StringProperty(indexed=True, default='')
    facebook_public_profile_url = ndb.StringProperty(indexed=True, default='')
    access_token = ndb.StringProperty()
    refresh_token = ndb.StringProperty()
    expires_at = ndb.IntegerProperty()

    _PROPERTIES = Base._PROPERTIES.union({
        'active',
        'admin',
        'author',
        'team_admin',
        'auth_ids',
        'avatar_url',
        'email',
        'name',
        'username',
        'image_url',
        'gplus_login',
        'google_display_name',
        'facebook_login',
        'facebook_username',
        'google_public_profile_url',
        'facebook_public_profile_url',
        'google_image_url',
    })

    def generate_auth_token(self, expiration = 5*3600):
        s = Serializer(config_file, expires_in = expiration)
        return s.dumps({ 'id': self.email })

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(config_file)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user = User.retrieve_one_by('email',data['id'])
        return user

    def topics_authored(self):
        return Topic.query(Topic.author == self.key).fetch()
        #topics, more_cursor = util.retrieve_dbs(
        #    Topic.query(Topic.author == self),
        #    limit=util.param('limit', int),
        #    cursor=util.param('cursor'),
        #    order=util.param('order'),
        #)
        #return topics

    def team_administered(self):
        return Team.query(Team.administrator == self.key).fetch()
        #teams, more_cursor = util.retrieve_dbs(
        #    Team.query(Team.administrator == self),
        #    limit=util.param('limit', int),
        #    cursor=util.param('cursor'),
        #    order=util.param('order'),
        #)
        #return teams


    def get_friends(self):
        """Query the friends of the current user."""
        edges = DirectedUserToUserEdge.query(
            DirectedUserToUserEdge.owner_user_id == self.key.id())\
            .fetch(projection=[DirectedUserToUserEdge.friend_user_id])
        edge2 = [e.friend_user_id for e in edges]
        edge4 = list(set(edge2))
        print edge4
        #return [ndb.Key('User', edge.friend_user_id).get() for edge in
        #        edges]
        return [ndb.Key('User', edge).get() for edge in
                edge4]



class Topic(Base):
    title = ndb.StringProperty(indexed=True, required=True)
    body = ndb.StringProperty()
    votes = ndb.IntegerProperty(default=0)
    #replies = ndb.KeyProperty(repeated=True)
    team = ndb.KeyProperty(kind='Team')
    author = ndb.KeyProperty(kind='User')
    voters = ndb.KeyProperty(repeated=True)
    topic_url = ndb.StringProperty(default="")
    vote_url = ndb.StringProperty(default="")
    shared = ndb.BooleanProperty(default=False)
    second_team = ndb.KeyProperty(kind='Team')
    #team_name = ndb.StringProperty(indexed=True)
    #teams = ndb.KeyProperty(repeated=True)

    _PROPERTIES = Base._PROPERTIES.union({
        'title',
        'votes',
        'body',
        'topic_url',
        'vote_url',
        #'replies',
    })


class Reply(Base):
    topic = ndb.KeyProperty(kind=Topic)
    user = ndb.KeyProperty(kind=User)
    votes = ndb.IntegerProperty(default=0)
    voters = ndb.KeyProperty(repeated=True)
    body = ndb.StringProperty(indexed=True, required=True)

    _PROPERTIES = Base._PROPERTIES.union({
        #'topic',
        #'user',
        'votes',
        'body',
        })
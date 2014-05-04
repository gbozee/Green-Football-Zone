import json
import time

from google.appengine.ext import ndb

import auth
from flask_restful import Resource, Api, reqparse, fields, marshal, marshal_with
import model
from rauth.service import OAuth2Service


SCOPES = [
    'https://www.googleapis.com/auth/plus.login',
]

VISIBLE_ACTIONS = [
    'http://schemas.google.com/AddActivity',
    'http://schemas.google.com/ReviewActivity'
]

TOKEN_INFO_ENDPOINT = ('https://www.googleapis.com/oauth2/v1/tokeninfo' +
                       '?access_token=%s')
TOKEN_REVOKE_ENDPOINT = 'https://accounts.google.com/o/oauth2/revoke?token=%s'
GOOGLE_PLUS_API_URL = 'https://www.googleapis.com/plus/v1/'

GOOGLE_API_URL = 'https://www.googleapis.com/oauth2/v1/'

#
#def get_user_id(user):
#    if user.google_plus_id:
#        return user.google_plus_id
#    g_id_index = [i for i, s in enumerate(user.auth_ids) if 'federated' in s]
#    if len(g_id_index) == 1:
#        index = g_id_index[0]
#        return user.auth_ids[index].split('_')[1]


class GooglePlus():
    def __init__(self):
        self.user = GooglePlus.get_user()
        self.headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    def get_user(self):
        print self.user
        return self.user

    def get_user_profile(self):
        """Return the public Google+ profile data for the given user."""
        user = refresh(self.user)
        credentials = user.access_token
        google_plus_auth = auth.google_plus.get_session(token=credentials)
        response = google_plus_auth.get(GOOGLE_PLUS_API_URL + 'people/me').json()
        #response = google_plus_auth.get(GOOGLE_API_URL + 'userinfo?access_token='+credentials).json()
        return response

    def get_user_activity(self):
        credentials = self.get_user().access_token
        google_plus = auth.google_plus.get_session(token=credentials)
        response = google_plus.get(GOOGLE_PLUS_API_URL + 'people/me/activities/public').json()
        return response

    def get_user_moments(self):
        user = refresh(self.user)
        credentials = user.access_token
        google_plus_auth = auth.google_plus.get_session(token=credentials)
        response = google_plus_auth.get(GOOGLE_PLUS_API_URL + 'people/me/moments/vault').json()
        #response = google_plus_auth.get(GOOGLE_API_URL + 'userinfo?access_token='+credentials).json()
        return response

    def get_and_store_friends(self):
        """Query Google for the list of the user's friends that they've shared with
        our app, and then store those friends for later use.

        Args:
          user: User to get friends for.
        """
        #user_id = get_user_id(self.user)
        friends_list = model.DirectedUserToUserEdge.query(
            model.DirectedUserToUserEdge.owner_user_id == self.user.key.id()).fetch(keys_only=True)
        if len(friends_list) > 0:
            ndb.delete_multi(friends_list)
        google_plus_auth = auth.google_plus.get_session(token=self.user.access_token)
        friends = google_plus_auth.get(GOOGLE_PLUS_API_URL + 'people/me/people/visible').json()
        for google_friend in friends['items']:
            # Determine if the friend from Google is a user of our app
            friend = model.User.retrieve_one_by('google_plus_id',
                                                google_friend['id'])
            # Only store edges for friends who are users of our app
            if friend is not None:
                #[edge.key.delete() for edge in friends_list]
                edge = model.DirectedUserToUserEdge()
                edge.owner_user_id = self.user.key.id()
                edge.friend_user_id = friend.key.id()
                edge.put()
        return friends

    def add_topic_to_google_plus_activity(self,topic):
        """Creates an app activity in Google indicating that the given User has
        uploaded the given Photo.

        Args:
          user: Creator of Photo.
          photo: Photo itself.
        """
        if topic:
            activity = json.dumps({
                "type": "http://schemas.google.com/AddActivity",
                "target": {
                    "url": topic
                    #"url": 'https://developers.google.com/+/web/snippet/examples/movie'
                }
            })

            user = refresh(self.user)
            google_plus_auth = auth.google_plus.get_session(token=user.access_token)
            friends = google_plus_auth.post(GOOGLE_PLUS_API_URL + 'people/me/moments/vault',
                                            headers=self.headers, data=activity).json()
            return friends
        else:
            return []

    @staticmethod
    def get_user():
        user = auth.current_user_db()
        #if user.google_display_name == '':
        #    flask.flash('User is not known yet')
        #    return flask.redirect(flask.url_for('signin_google_plus'))
        #current = int(time.time())
        #remaining = user.expires_at - current
        #print "remaining=%d" % (remaining)
        #if remaining <= 0:
        #    result = refresh(user)
        #    return result
        return user


    def add_reply_to_google_plus_activity(self,url,reply, user2):
        """Add to the user's Google+ app activity that they replied to a post.

        Args:
          reply: user reply.
        """
        #title = reply.topic.get()
        #user_posted = reply.user.get().username
        if url:
            activity = json.dumps(
                {"type": "http://schemas.google.com/ReviewActivity",
                 "target": {
                     #"url": url
                     "url": 'https://developers.google.com/+/web/snippet/examples/movie'
                 },
                 "result": {
                     "type": "http://schema.org/Review",
                     "name": "Reply to " + url + " by " + user2,
                     #"url": title.topic_url,
                     "url": url,
                     #"url": 'https://developers.google.com/+/web/snippet/examples/movie',
                     #"text": reply.body,
                     "text": reply,
                 }})
            user = refresh(self.user)
            google_plus_auth = auth.google_plus.get_session(token=user.access_token)
            user_reply = google_plus_auth.post(GOOGLE_PLUS_API_URL + 'people/me/moments/vault',
                                               headers=self.headers, data=activity).json()
            return user_reply


    def vote_or_unvote_topic_on_google_plus_activity(self, topic, text):
        """diplaying voting alert on a topic on google+.

        Args:
          topic: topic voted on.
        """
        activity = json.dumps(
            {"type": "http://schemas.google.com/ReviewActivity",
             "target": {
                 #"url": topic.topic_url
                 "url": 'https://developers.google.com/+/web/snippet/examples/movie'
             },
             "result": {
                 "type": "http://schema.org/Review",
                 "name": text['title'],
                 #"url": topic.vote_url,
                 "url": 'https://developers.google.com/+/web/snippet/examples/movie',
                 "text": text['body'],
             }})
        user = refresh(self.user)
        google_plus_auth = auth.google_plus.get_session(token=user.access_token)
        vote = google_plus_auth.post(GOOGLE_PLUS_API_URL + 'people/me/moments/vault',
                                     headers=self.headers, data=activity).json()
        return vote

    def user_following_or_unfollowing_a_new_team(self, team, texts):
        """Add to the new team the  user is following to his/her Google+ app activity

        Args:
         team: the team being followed
       """

        activity = json.dumps(
            {"type": "http://schemas.google.com/ReviewActivity",
             "target": {
                 #"url": team.follow_url
                 "url": 'https://developers.google.com/+/web/snippet/examples/movie'
             },
             "result": {
                 "type": "http://schema.org/Review",
                 "name": texts['title'],
                 #"url": team.follow_url,
                 "url": 'https://developers.google.com/+/web/snippet/examples/movie',
                 "text": texts['body'],
             }})
        user = refresh(self.user)
        google_plus_auth = auth.google_plus.get_session(token=user.access_token)
        follow = google_plus_auth.post(GOOGLE_PLUS_API_URL + 'people/me/moments/vault',
                                       headers=self.headers, data=activity).json()
        return follow


def refresh(users):
    user = users
    response = auth.google_plus.get_raw_access_token(data={
        'refresh_token': user.refresh_token,
        'grant_type': 'refresh_token',
        'scope': 'https://www.googleapis.com/auth/plus.login',

    })
    response2 = response.json()
    print response2
    user.access_token = response2['access_token']
    user.expires_at = int(time.time()) + response2['expires_in']

    user.put()
    return user








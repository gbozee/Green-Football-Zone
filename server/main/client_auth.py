import json
from flask import request,abort, g, jsonify, Flask
from flask.views import MethodView
from google.appengine.api import memcache
from google.appengine.api.app_identity import app_identity
from model import basic_auth,User,Team, Topic
from google.appengine.ext import ndb
from main import util
import config
from helpers import JSONEncoder
from model import League,Team,User,Reply
from flask_restful import Resource, Api, reqparse, fields, marshal, marshal_with,abort

mobile_api = Flask(__name__)
mobile_api.config.from_object(config)
mobile_api.json_encoder = JSONEncoder

api = Api(mobile_api,catch_all_404s=True)


API_URL = '/v1.0/'

@mobile_api.route(API_URL+'connect', methods=['POST'])
def connect():
    data = json.loads(request.data)
    user_email = data.get('email')
    user = User.retrieve_one_by('email',user_email)
    if user:
        token = user.generate_auth_token()
        response = dict(token=token.decode('ascii'),new_user=False)
    else:
        user = User(name = data.get('name'),username = data.get('username'),
                    email = user_email)
        user.put()
        token = user.generate_auth_token()
        response = dict(token=token.decode('ascii'),new_user=True)
    return jsonify(response)

@mobile_api.route(API_URL+'api/token')
@basic_auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({ 'token': token.decode('ascii') })


@mobile_api.route(API_URL+'api/user')
@basic_auth.login_required
def get_username():
    return jsonify({ 'user': g.user.username })


def list_response(array, **kwargs):
    meta = {
        'count': len(array),
        'total': len(array)
    }
    if 'total' in kwargs and kwargs['total']:
        meta['total']= kwargs['total']
    if 'next' in kwargs and kwargs['next']:
        meta['next']=util.generate_more_url(kwargs['next'])
    if 'previous' in kwargs and kwargs['previous']:
        meta['previous']=util.generate_more_url(kwargs['previous'])
    data = {
        'results': array,
        'meta': meta
    }
    response = {
        'status': 'success',
        'data': data
    }
    if 'status' in kwargs and kwargs['status']:
        response['status'] = kwargs['status']
    return jsonify(response)

def single_response(result,status=None):
    response = {
        'status': status if status else 'success',
        'data': result
    }
    return jsonify(response)
def register_api(view, endpoint, url, pk='id', pk_type='int'):
    view_func = view.as_view(endpoint)
    mobile_api.add_url_rule(url, defaults={pk: None},
                     view_func=view_func, methods=['GET',])
    mobile_api.add_url_rule(url, view_func=view_func, methods=['POST',])
    mobile_api.add_url_rule('%s<%s:%s>' % (url, pk_type, pk), view_func=view_func,
                     methods=['GET', 'PUT', 'DELETE'])

def validate_post(params,req):
    if not req:
        abort(404)
    for value in params:
        if not value in req:
            abort(404)

class LeagueAPI(MethodView):
    def get(self, name):
        if name is None:
            leagues = League.query().fetch()
            return list_response(leagues)
        else:
            league = League.retrieve_one_by('name',name)
            return single_response(league)

    def post(self):
        # create a new user
        args = request.json
        new_league = League(
            parent=ndb.Key("League", args.get('league') or "*notitle"),
            name=args['name'].lower().title(),
            type=args.get('club') or 'club',
            info=args.get('info') or '',
            logo=args.get('logo')
        )
        new_league.put()
        # notification('leagues', 'league_created', league=result)
        return single_response(new_league,201)

register_api(LeagueAPI, 'league_api', API_URL+'leagues/', pk='name',pk_type='string')

class TeamAPI(MethodView):
    def get(self, name):
        if name is None:
            teams = util.retrieve_dbs()
            return list_response(teams)
        else:
            team = Team.retrieve_one_by('name',name)
            return single_response(team)

    def post(self):
        # create a new user
        args = request.data
        new_league = League(
            parent=ndb.Key("League", args['league'] or "*notitle"),
            name=args['name'].lower().title(),
            type=args['type'] or 'club',
            info=args['info'] or '',
            logo=args['logo']
        )
        new_league.put()
        # notification('leagues', 'league_created', league=result)
        return single_response(new_league,201)

    def put(self,name):
        pass

    def delete(self,name):
        pass

register_api(TeamAPI, 'team_api', API_URL+'teams/', pk='name',pk_type='string')


reply_field = {

    'body': fields.String,
    'votes': fields.Integer,
    'created': fields.String,
    'key': fields.String,
    'id':fields.Integer,
    'topic':fields.String,
    'by': fields.String,
    'user_url':fields.String,
    'team':fields.String,
    'team_name':fields.String,
}
simple_team_field = {
    'name': fields.String,
    'admin': fields.String,
    'c_league': fields.String,
    'type':fields.String,
    'created':fields.String,
    'logo': fields.String,
    'coach': fields.String,
    'info': fields.String,
    'league': fields.String,
    'key': fields.String,
    'follow_url':fields.String,
    'id': fields.Integer,
    # 'uri': fields.Url('teams3'),
    #'uri': fields.Url('league_team_url'),
    #'topic_url':fields.Url('team_topics1'),
    'followers_count': fields.Integer
}

class FollowTeamAPI(Resource):
    decorators = [basic_auth.login_required]
    def get(self,team_name):
        team = TeamRepo(team_name).team
        if team is None:
            abort(404)
        user_repo = UserRepo()
        user_object = user_repo.follow_team(team.key)
        cursor = None
        response = get_array_result_object(user_object,simple_team_field,status='followed')
        return response

api.add_resource(FollowTeamAPI, API_URL+'teams/<team_name>/follow', endpoint='follow_teams2.0')

class TopicListAPI(Resource):
    decorators = [basic_auth.login_required]
    def __init__(self):
        self.args = reqparse.RequestParser()
        self.args.add_argument('title', type=str, required=True, help="No title Provided", location='json'),
        self.args.add_argument('body', type=str, required=True, help="No body Provided", location='json'),
        self.args.add_argument('team', type=str, default='' ,location='json'),
        self.args.add_argument('second_team', type=str, default="", location='json'),
        #self.args.add_argument('root_url', type=str, help="No Root url Provided", location='json'),
        super(TopicListAPI, self).__init__()

    def get(self):
        topics,next = TopicRepo.get_all_topics_objects()
        response = get_array_result_object(topics, simple_topic_field, next=next)
        return response

    def post(self):
        args = self.args.parse_args()
        topic = TopicRepo.add_topic(args)
        response = marshal(topic, simple_topic_field)
        # topic_notification(response['team'], 'topic_added', topic=response)
        # topic_notification(response['second_team'], 'topic_added', topic=response)
        return get_single_result_object(response), 203


api.add_resource(TopicListAPI, API_URL + 'topics', endpoint='all_topicss12')

class TopicAPI(Resource):
    decorators = [basic_auth.login_required]
    def __init__(self):
        self.args = reqparse.RequestParser()

        self.args.add_argument('title', type=str, default="", help="", location='json'),
        self.args.add_argument('body', type=str, default="", help=" Provided", location='json'),
        self.args.add_argument('team', type=str, default='', location='json'),
        self.args.add_argument('second_team', type=str, default="", location='json'),
        super(TopicAPI, self).__init__()

    def get(self, topic_id):
        topic_repo = TopicRepo(topic_id)
        topic = topic_repo.topic
        if topic is None:
            abort(404)
        topic_model = topic_repo.fetch_topic_objects()
        response = marshal(topic_model, simple_topic_field)
        return get_single_result_object(response)

    def put(self, topic_id):
        args = self.args.parse_args()
        topic = TopicRepo(topic_id)
        topic_model = topic.update_topic(args)
        response = marshal(topic_model, simple_topic_field)
        # topic_notification(response['team'],'topic_updated',topic=response)
        # topic_notification(response['second_team'],'topic_updated',topic=response)
        return get_single_result_object(response)

    def delete(self, topic_id):
        topic = TopicRepo(topic_id)
        response = marshal(topic.fetch_topic_objects(), simple_topic_field)
        # topic_notification(response['team'], 'topic_deleted', topic=response)
        # topic_notification(response['second_team'], 'topic_deleted', topic=response)
        if topic.topic:
            topic.delete_topic()
        return {'result': True}


api.add_resource(TopicAPI, API_URL + 'topics/<int:topic_id>', endpoint='single_topic1',
                 methods=['GET','PUT','DELETE'])

class TopicRepliesAPI(Resource):
    decorators = [basic_auth.login_required]
    def __init__(self):
        self.args = reqparse.RequestParser()
        self.args.add_argument('body', type=str, required=True, help="No title Provided", location='json'),
        self.args.add_argument('reply_id', type=str, location='args'),
        self.user = UserRepo()
        super(TopicRepliesAPI, self).__init__()

    def get(self, topic_id):
        topic = TopicRepo(topic_id)
        if topic.topic is None:
            abort(404)
        replies, cursor = topic.get_replies_object()
        response = get_array_result_object(replies, reply_field,next=cursor)
        return response

    def post(self, topic_id):
        args = self.args.parse_args()
        args['user'] = self.user.get_user()
        #topic = ndb.Key('Topic',topic_id)
        topic = TopicRepo(topic_id)
        reply_object = topic.post_reply(args)
        response = marshal(reply_object, reply_field)
        # notification(response['team_name'].replace(" ",""), 'reply_added', reply=response,topic_id=topic_id)

        return get_single_result_object(response),201

api.add_resource(TopicRepliesAPI, API_URL + 'topics/<int:topic_id>/replies', endpoint='topic_replies')

class TopicVoteAPI(Resource):
    decorators = [basic_auth.login_required]
    def get(self,topic_id):
        topic_repo = TopicRepo(topic_id)
        topic = topic_repo.topic
        if topic is None:
            abort(404)
        topic_model = topic_repo.upvote(g.user)
        response = marshal(topic_model, simple_topic_field)
        # notification(response['team'].replace(" ",""), 'topic_upvote', topic=response)
        return get_single_result_object(response)

    def delete(self,topic_id):
        topic_repo = TopicRepo(topic_id)
        topic = topic_repo.topic
        if topic is None:
            abort(404)
        topic_model = topic_repo.downvote(g.user)
        response = marshal(topic_model, simple_topic_field)
        # notification(response['team'].replace(" ",""), 'topic_downvote', topic=response)
        return get_single_result_object(response)
#
api.add_resource(TopicVoteAPI, API_URL + 'topics/<int:topic_id>/vote', endpoint='topic_vote2')
#
class ReplyAPI(Resource):
    decorators = [basic_auth.login_required]
    def __init__(self):
        self.args = reqparse.RequestParser()
        self.args.add_argument('body', type=str, required=True, help="No body Provided", location='json'),
        self.user = UserRepo()
        super(ReplyAPI, self).__init__()

    def get(self,reply_id):
        reply = ReplyRepo(reply_id)
        print reply.reply
        if reply.reply is None:
            abort(404)
        #if validate_reply(reply.reply):
        reply_object = reply.get_reply_object()
        response = marshal(reply_object, reply_field)
        return response

    def put(self, reply_id):
        args = self.args.parse_args()
        reply = ReplyRepo(reply_id)
        reply_model = reply.update_reply(args)
        response = marshal(reply_model, reply_field)
        # notification(response['team_name'].replace(" ",""), 'reply_updated', reply=response, topic_id=response['topic_id'])
        return response, 203

    def delete(self, reply_id):
        reply = ndb.Key(urlsafe=reply_id)
        replied = reply.get()
        if replied:
            replied.key.delete()
        return {'result': True}
#
# api.add_resource(ReplyAPI, API_URL + 'replies/<string:reply_id>', endpoint='update_delete_reply2')
#
class ReplyVoteAPI(Resource):
    decorators = [basic_auth.login_required]
    def get(self, reply_id):
        reply_repo = ReplyRepo(reply_id)
        reply = reply_repo.reply
        if reply is None:
            abort(404)
        reply_model = reply_repo.upvote(g.user)
        response = marshal(reply_model, reply_field)
        return get_single_result_object(response)

    def delete(self, reply_id):
        reply_repo = ReplyRepo(reply_id)
        reply = reply_repo.reply
        if reply is None:
            abort(404)
        reply_model = reply_repo.downvote(g.user)
        response = marshal(reply_model, reply_field)
        return get_single_result_object(response)

api.add_resource(ReplyVoteAPI, API_URL + 'replies/<string:reply_id>/vote', endpoint='reply_vote3232')

class UserReplyListAPI(Resource):
    decorators = [basic_auth.login_required]
    def __init__(self):
        self.args = reqparse.RequestParser()
        self.args.add_argument('body', type=str, required=True, help="No title Provided", location='json'),
        self.args.add_argument('reply_id', type=str, location='args'),
        super(UserReplyListAPI, self).__init__()

    def get(self,):
        user = UserRepo()
        replies,next = user.get_replies_object()
        response = get_array_result_object(replies, reply_field,next=next)
        return response

api.add_resource(UserReplyListAPI, API_URL + 'me/comments', endpoint='replies_with_topic_edit22323')

class UserTeamsAPI(Resource):
    decorators = [basic_auth.login_required]
    def __init__(self):
         super(UserTeamsAPI, self).__init__()

    def get(self):
        user = UserRepo()
        if util.param('team_admin',bool):
            teams,next,previous,count = user.get_administered_teams_list()
        else:
            teams, next, previous, count = user.get_teams_object()
        response = get_array_result_object(teams, simple_team_field,next=next)
        return response

#
#
class UserTeamUnFollow(Resource):
    decorators = [basic_auth.login_required]
    def delete(self, team_name):
        team = Team.retrieve_one_by('name',team_name)
        #team = Team.get_by_id(team_id)
        print team
        if team is None:
            abort(404)
        user_repo = UserRepo()
        followed_teams = user_repo.unfollow_team(team.put())
        response = get_array_result_object(followed_teams,simple_team_field)
        return response

api.add_resource(UserTeamsAPI, API_URL+'my-teams', endpoint='user_teamswoeowhewheo')
api.add_resource(UserTeamUnFollow, API_URL+'my-teams/<string:team_name>', endpoint='user_teams_unfollow3223')
#
class UserTopicsAPI(Resource):
    decorators = [basic_auth.login_required]
    def __init__(self):
        self.user = g.user
        self.args = reqparse.RequestParser()
        super(UserTopicsAPI, self).__init__()

    def get(self):
        if util.param('author',bool):
            topics, next = get_authored_topics_object(self.user)
        else:
            topics, next= get_all_topics_from_followed_teams(self.user)
            print topics
        response = get_array_result_object(topics, simple_topic_field,next=next)
        return response

api.add_resource(UserTopicsAPI, API_URL + 'me/topics', endpoint='author_topics253232')
#
#
# simplest_user_field = {
#     'name': fields.String,
#     'author':fields.Boolean,
#     'admin': fields.Boolean,
#     'team_admin':fields.Boolean,
#     'username':fields.String,
#     'email':fields.String,
#     'avatar_url': fields.String,
#     'image_url':fields.String,
#     'key':fields.String,
#     'id':fields.Integer,
# }
#
class UserDetailsAPI(Resource):
    decorators = [basic_auth.login_required]
    def __init__(self):
        self.user = g.user
        self.args = reqparse.RequestParser()
        super(UserDetailsAPI, self).__init__()

    def get(self):
        user_db = get_user_object(self.user)
        return get_single_result_object(marshal(user_db, user_fields))
        #return {'user': marshal(user_db, simple_user_fields)}

    def put(self):
        user_object = update_info(self.user,request.json)
        return get_single_result_object(marshal(user_object, user_fields))

api.add_resource(UserDetailsAPI, API_URL + 'me/profile', endpoint='user_details24')
#
#
def get_teams_object(teams):
    teams_object = []
    for team in teams:
        if team:
            team_object = util.model_db_to_object(team)
            query = User.query(User.teams == team.key).fetch()
            league = team.league.get()
            if league:
                team_object['league'] = league.name
            team_object['followers_count'] = len(query)
            try:
                admin = team.admin.get()
                if admin:
                    team_object['admin'] = admin.username
            except:
                admin = None
            teams_object.append(team_object)

    return teams_object

def get_single_result_object(result,status=None):
    return {
        'status': status if status else 'success',
        'data': result

    }

def get_array_result_object(array, marshal_field,**kwargs):
    meta = {
        'count': len(array),
        'total': len(array)
    }
    if 'total' in kwargs and kwargs['total']:
        meta['total']= kwargs['total']
    if 'next' in kwargs and kwargs['next']:
        meta['next']=util.generate_more_url(kwargs['next'])
    if 'previous' in kwargs and kwargs['previous']:
        meta['previous']=util.generate_more_url(kwargs['previous'])
    data = {
        'results': map(lambda l: marshal(l, marshal_field), array),
        'meta': meta
    }
    response = {
        'status': 'success',
        'data': data
    }
    if 'status' in kwargs and kwargs['status']:
        response['status'] = kwargs['status']
    return response

simple_topic_field = {
    'title': fields.String,
    'author': fields.String,
    'created': fields.String,
    'votes': fields.Integer,
    'key': fields.String,
    'replies':fields.Integer,
    'body': fields.String,
    'id': fields.Integer,
    'second_team':fields.String,
    'second_team_url':fields.String,
    'topic_url': fields.String,
    'vote_url': fields.String,
    'team': fields.String,
    'team_url':fields.String,
    #'uri':fields.Url('single_topic1')
}
user_fields = {
        'admin':fields.Boolean,
        'author':fields.Boolean,
        'team_admin':fields.Boolean,
        'avatar_url':fields.String,
        'email':fields.String,
        'name':fields.String,
        'username':fields.String,
        'facebook_username':fields.String,
        'image_url':fields.String,
        'google_plus_id':fields.String,
        'google_display_name':fields.String,
        'facebook_login':fields.Boolean,
        'facebook_public_profile_url':fields.String,
        'key':fields.String,
        'id':fields.Integer
}
def update_info(user, args):
        for key in args:
            setattr(user, key, args[key])
        user.put()
        #return user
        return get_user_object(user)

def get_user_object(user):
    user_object = util.model_db_to_object(user)
    user_object['teams'] = get_teams_object(ndb.get_multi(user.teams))
    return user_object

def get_authored_topics_object(user):
    query = Topic.query(Topic.author == user.key)
    topics, next, = TopicRepo.get_all_topics_objects(query)
    return topics, next

def get_all_topics_from_followed_teams(user):
        key = user.username + '_team_topics_count'
        if len(user.teams) != 0:
            query = Topic.query(ndb.OR(Topic.team.IN(user.teams),
                                       Topic.second_team.IN(user.teams))).order(Topic._key)
            topics, next= TopicRepo.get_all_topics_objects(query)
        else:
            topics = []
            next = previous = None
        return topics, next

class TopicRepo(object):
    def __init__(self, url):
        self.topic = Topic.get_by_id(url)

    @classmethod
    def get_all_topics(cls, contains):
        topics = Topic.query().fetch()
        if contains:
            return map(lambda l: get_topic_with_reply(l), topics)
        return map(lambda l: get_topic_object(l), topics)


    def get_replies_object(self):
        query = Reply.query(Reply.topic == self.topic.key)
        replies, next = ReplyRepo.get_replies_object(query)
        return replies, next


    def get_topic(self):
        return self.topic

    def update_topic(self, topic):
        user = g.user
        for key in topic:
            if key == 'author':
                setattr(self.topic, key, user.key)
            elif key == 'team' or key == 'second_team':
                team = Team.query(Team.name == topic[key]).get()
                if team:
                    setattr(self.topic, key, team.key)
            else:
                setattr(self.topic, key, topic[key])
                #if topic['title']:
                #    self.topic.title = topic['title']
                #if topic['body']:
                #    self.topic.body = topic['body']
                #if topic['author']:
        saved_topic = self.topic.put().get()
        topic_model = util.model_db_to_object(saved_topic)
        if saved_topic.team:
            team3 = saved_topic.team.get()
            topic_model['team'] = team3.name
            topic_model['team_url'] = team3.logo

        topic_model['author'] = user.username
        #topic_model['replies'] = len(saved_topic.replies)
        if saved_topic.second_team:
            team3 = saved_topic.second_team.get()
            topic_model['second_team'] = team3.name
            topic_model['second_team_url'] = team3.logo
        # followed_topic_notification(self.topic,team_name=topic_model['team'])
        return topic_model

    def update_url(self, url):
        self.topic.topic_url = url['topic_url'] or ''
        self.topic.vote_url = url['vote_url'] or ''

        return self.topic.put()


    def delete_topic(self):
        team = self.topic.team
        if team:
        #if self.topic.key in team.topics:
        #    team.topics.remove(self.topic.key)
        #    team.put()
            key = team.get().name + '_count'
            if memcache.get('topics_count'):
                util.get_or_set_count_by_memcache('topics_count', increment=False)
            util.get_or_set_count_by_memcache(key, increment=False)
            #replies = self.topic.replies
            #ndb.delete_multi(replies)
        replies = Reply.query(Reply.topic == self.topic.key).fetch()
        if(len(replies)) > 0:
            for reply in replies:
                reply.key.delete()
        self.topic.key.delete()
        return True

    def upvote(self, user):
        upvote(self.topic, user)
        return self.fetch_topic_objects()

    def downvote(self, user):
        downvote(self.topic, user)
        return self.fetch_topic_objects()

    def has_voted(self, user):
        return user.key in self.topic.voters


    def post_reply(self, reply):
        user = g.user
        key = ndb.Key('Reply', self.topic.key.id())
        new_reply = Reply(
            parent=key,
            user=user.key,
            body=reply['body'],
            topic=self.topic.key,
        )
        new_reply.put()

        #self.topic.replies.append(new_reply_key)
        self.topic.put()

        #reply_new = new_reply_key.get()
        reply_object = util.model_db_to_object(new_reply)
        reply_object['by'] = user.username
        reply_object['topic'] = self.topic.title
        try:
            team = self.topic.team.get()
            reply_object['team'] = team.logo
            reply_object['team_name'] = team.name
        except:
            reply_object['team'] = None
            reply_object['team_name'] = None
        # followed_topic_notification(self.topic, reply=reply_object,topic=self.fetch_topic_objects())

        return reply_object

    @classmethod
    def get_all_topics_objects(cls,query=None):
        if query is None:
            query = Topic.query()
        topics, next = util.retrieve_dbs(
            query,
            limit=util.param('limit', int),
            cursor=util.param('cursor')
        )

        topics_object = get_topic_object(topics)
        return topics_object, next

    def fetch_topic_objects(self):
        topic_object = util.model_db_to_object(self.topic)
        replies = Reply.query(Reply.topic == self.topic.key).fetch()
        if replies:
            topic_object['replies'] = len(replies)
        topic_object['author'] = self.topic.author.get().username
        print self.topic.author

        if self.topic.team:
            team1 = self.topic.team.get()
            if team1:
                topic_object['team'] = team1.name
                topic_object['team_url'] = team1.logo
            else:
                self.topic.team = None
        if self.topic.second_team:
            team2 = self.topic.second_team.get()
            if team2:
                topic_object['second_team'] = team2.name
                topic_object['second_team_url'] = team2.logo
            else:
                self.topic.second_team = None
        self.topic.put()
        return topic_object

    @classmethod
    def add_topic(cls, args):
        topic = Topic()
        topic.author = g.user.key
        topic.title = args['title']
        topic.body = args['body']
        t = topic.put().get()

        # t.topic_url = server_url + '/gtopic/' + str(t.key.id())
        # t.vote_url = server_url + '/google_votes/' + str(t.key.id())
        t.put()
        tt = t
        if 'team' in args:
            if args['team'] is not "":
                team_value = args['team'].lower().title()
                tt = TeamRepo(team_value).post_topic(t)
        if 'second_team' in args:
            if args['second_team'] is not "":
                s_team_value = args['second_team'].lower().title()
                tt = TeamRepo(s_team_value).post_topic(t, attr='second_team')
        # followed_topic_notification(tt)
        obj = TopicRepo(tt.key.id())
        return obj.fetch_topic_objects()

def get_topic_object(topics):
    topics_object = []
    for topic in topics:
        topic_object = util.model_db_to_object(topic)
        try:
            replies = Reply.query(Reply.topic == topic.key).fetch()
            topic_object['replies'] = len(replies)
        except:
            topic_object['replies'] = 0
        author = topic.author.get()
        if author:
            topic_object['author'] = author.username
        try:
            team1 = topic.team.get()
            if team1:
                topic_object['team'] = team1.name
                topic_object['team_url'] = team1.logo
        except:
            team1 =None
        try:
            team2 = topic.second_team.get()
            if team2:
                topic_object['second_team'] = team2.name
                topic_object['second_team_url'] = team2.logo
        except:
            team2 = None
        topic.put()
        topics_object.append(topic_object)
    return topics_object

def get_topic_with_reply(topic):
    if topic is None:
        return {}
    else:
        return dict(
            id=topic.key.id(),
            title=topic.title,
            body=topic.body,
            team=dict(name=topic.team.get().name, logo=topic.team.get().logo),
            created=topic.created,
            author=getauthor(topic.author),
            votes=topic.vote,
            key=topic.key.urlsafe(),
            topic_url=topic.topic_url,
            vote_url=topic.vote_url,
            replies=map(lambda r: reply_model(r.get()), topic.replies)
        )

def getauthor(author):
    if author:
        if author.get() is None:
            return
        return author.get().username
    else:
        return None


def reply_model(reply):
    if reply is None: return
    return dict(
        id=reply.key.id(),
        body=reply.body,
        votes=reply.vote,
        created=reply.created,
        key=reply.key.urlsafe(),
        username=reply.user.get().username)

def upvote(obj, user):
    if not has_voted(obj, user):
        obj.votes += 1
        obj.voters.append(user.key)
        obj = obj.put()
    return obj


def downvote(obj, user):
    if has_voted(obj, user):
        obj.votes -= 1
        obj.voters.remove(user.key)
        obj = obj.put().get()
    return obj


def has_voted(obj, user):
    return user.key in obj.voters

server_url = app_identity.get_default_version_hostname()
class TeamRepo(object):
    def __init__(self, team_name):
        self.team = Team.retrieve_one_by('name', team_name)

    @classmethod
    def get_all_teams(cls):
        team = Team.query().fetch()
        if len(team) == 0:
            return []
        return team

    @classmethod
    def get_all_teams_object(cls, key, query=None):
        if query is None:
            query = Team.query()
        teams, next, previous, count = util.retrieve_dbs2(
            query,
            key,
            limit=util.param('limit', int),
            cursor=util.param('cursor'),
            order=util.param('order'),
        )
        teams_object = get_teams_object(teams)
        return teams_object, next, previous, count
        #teams = Team.query().fetch()
        #print teams
        #return map(lambda l: get_team_object(l), teams)

    @classmethod
    def get_team_obj(cls, team):
        team = get_team_object(team)
        if hasattr(team, 'followers'):
            team['followers_count'] = team.followers.length
        return team

    def get_team_object(self):
        if self.team.admin is None:
            admin = None
        else:
            admin = self.team.admin.get()
        team = util.model_db_to_object(self.team)
        team['followers_count'] = self.get_team_followers()
        if self.team.league.get() is not None:
            league = self.team.league.get()
            team['league'] = league.name
        if admin:
            team['admin'] = admin.username
        return team

    def get_team_followers(self):
        query = User.query(User.teams == self.team.key).fetch()
        return len(query)


    def get_topics_object(self):
        query = Topic.query(ndb.OR(Topic.team == self.team.key,
                                   Topic.second_team == self.team.key)).order(Topic._key)
        key_name = self.team.name + '_count'
        topics, next,= TopicRepo.get_all_topics_objects(query)
        return topics, next
        #return map(lambda t: get_topic_object(t.get()), self.team.topics)

    def get_team_with_topics(self):
        team = self.get_team_object()
        team['topics'] = self.get_topics_object()

        return team

    def get_followers_object(self):
        followers = ndb.get_multi(self.team.followers)
        #return map(lambda f: get_followers_model(f.get()), self.team.followers)

    def get_follow_result(self, user):
        return get_follow_result(user, self.team)


    def get_team(self):
        return self.team

    def update_team(self, team):
        self.team.type = team['type']
        if team['league'] is not '':
            league = League.retrieve_one_by('name', team['league'])
            if league:
                self.team.league = league.key
        if team['name'] is not '':
            self.team.name = team['name'].lower().title()
        if team['logo'] is not '':
            self.team.logo = team['logo']
        if team['coach'] is not '':
            self.team.coach = team['coach'] or ''
        if team['admin'] is not "":
            username = team['admin'].lower()
            admin = User.retrieve_one_by('username', username)
            if admin:
                self.team.admin = admin.key
        if team['info'] is not "":
            self.team.info = team['info']

        self.team.follow_url = server_url + '/gteam/' + self.team.name
        self.team.c_league = team['c_league']
        return self.team.put()

    def delete_team(self):
        if hasattr(self.team, 'followers'):
            users = self.team.followers
            for user in users:
                user.get().teams.remove(self.team.key)
                user.put()
        query = Team.query()
        util.get_or_set_count_by_memcache('team_count', query, increment=False)
        return self.team.key.delete()


    def get_topics(self):
        return self.team.topics

    def post_topic(self, topic, attr='team'):
        if type(topic) == Topic:
            setattr(topic, attr, self.team.key)
            return topic.put().get()
        author = g.user
        ancestor = ndb.Key('Topic', self.team.name or '*notitle')
        new_topic = Topic(
            title=topic['title'],
            body=topic['body'],
            author=author.key,
            team=self.team.key,
            #topic_url=topic['url']
        )
        topic_key = new_topic.put()
        key_name = self.team.name + '_count'
        util.get_or_set_count_by_memcache(key_name, increment=True)
        if memcache.get('topics_count'):
            util.get_or_set_count_by_memcache('topics_count', increment=True)

        #self.team.topics.append(topic_key)
        #self.team.put()
        new_topic = topic_key.get()
        topic_object = util.model_db_to_object(new_topic)
        topic_object['team'] = self.team.name
        topic_object['author'] = author.username
        #if topic['url']:
        #    new_topic.topic_url = 'http://' + topic['url'].netloc + '/gtopic/' + topic_key.urlsafe()
        #    new_topic.put()
        return topic_object

    def update_topic_url(self, topic, new_topic):
        if topic['topic_url']:
            new_topic.topic_url = topic['topic_url']
        if topic['vote_url']:
            new_topic.vote_url = topic['vote_url']
        new_topic.topic_url = server_url + '/gtopic/' + str(new_topic.key.id())
        new_topic.vote_url = server_url + '/google_votes/' + str(new_topic.key.id())
        return new_topic.put()


    def follow(self, user):
        self.team.followers.append(user.key)
        return self.team.put()


    def unfollow(self, user):
        self.team.followers.remove(user.key)
        return self.team.put()

    def isfollowing(self, user):
        if user.key not in self.team.followers:
            return False
        return True

    def like(self):
        self.team.likes += 1
        return self.team.put()

    def dislike(self):
        self.team.dislikes += 1
        return self.team.put()

def get_team_object(team):
    if team is None:
        return {}
    return dict(
        name=team.name,
        admin=getauthor(team.administrator),
        coach=team.coach,
        info=team.info,
        logo=team.logo,
        league=team.league.get().name,
        key=team.key.urlsafe(),
        id=team.key.id(), )

def get_follow_result(user, team):
    return dict(
        count=len(team.followers),
        button_class="" if user.key not in team.followers else "following",
        text="Follow" if user.key not in team.followers else "Following",
    )


class UserRepo(object):
    def __init__(self, user_id=None):
        if user_id is None:
            self.user = g.user
            print self.user
        else:
            self.user = ndb.Key('User', user_id).get()
            print self.user

    @classmethod
    def get_all_users(cls, key, query=None):
        if query is None:
            query = User.query()
        users, next, previous, count = util.retrieve_dbs2(
            query,
            key,
            refresh=util.param('refresh', bool),
            limit=util.param('limit', int),
            cursor=util.param('cursor'),
            admin=util.param('admin', bool),
            author=util.param('author', bool)
        )
        users_object = get_users_object(users)
        return users_object, next, previous, count
        #return map(lambda l: authors_model(l), users)

    def get_user(self):
        return self.user

    def post_comment(self, key):
        self.user.comments.append(key)
        return self.user.put()

    def follow_team(self, key):
        if key not in self.user.teams:
            self.user.teams.append(key)
        self.user.put()
        teams = ndb.get_multi(self.user.teams)
        return get_teams_object(teams)

    def unfollow_team(self, key):

        if len(self.user.teams) is not 0:
            if key in self.user.teams:
                self.user.teams.remove(key)
        self.user.put()
        teams = ndb.get_multi(self.user.teams)
        return get_teams_object(teams)

    def remove_comment(self, key):
        self.user.comments.remove(key)
        return self.user.put()

    def set_as_author(self):
        self.user.author = not self.user.author
        self.user.put()
        return authors_model(self.user)


    def get_user_object(self):
        user_object = util.model_db_to_object(self.user)
        user_object['teams'] = get_teams_object(ndb.get_multi(self.user.teams))
        return user_object

    def get_authored_topics_object(self):
        query = Topic.query(Topic.author == self.user.key)
        topics, next, = TopicRepo.get_all_topics_objects(query)
        return topics, next

    def get_all_topics_from_followed_teams(self):
        key = self.user.username + '_team_topics_count'
        if len(self.user.teams) != 0:
            query = Topic.query(ndb.OR(Topic.team.IN(self.user.teams),
                                       Topic.second_team.IN(self.user.teams))).order(Topic._key)
            topics, next= TopicRepo.get_all_topics_objects(query)
        else:
            topics = []
            next = previous = None
        return topics, next


    def get_user_teams_object(self):
        return map(lambda l: get_team_object(l.get()), self.user.teams)

    # def post_comment_on_google_plus(self, url, comment, user):
    #     g_plus = GooglePlus()
    #     result = g_plus.add_reply_to_google_plus_activity(url, comment, user)
    #     return result

    def get_administered_teams_list(self):
        query = Team.query(Team.admin == self.user.key)
        key = self.user.username + '_teams_count'
        return TeamRepo.get_all_teams_object(key, query)

    def get_user_comments(self):
        for reply in self.user.comments:
            if reply.get() is None:
                print reply.get()
                self.user.comments.remove(reply)
                self.user.put()
        if len(self.user.comments) == 0:
            return []
        return map(lambda l: user_reply_model(l.get()), self.user.comments)

    def get_teams_object(self):
        all_teams = []
        for key in self.user.teams:
            val = key.get()
            if val is None:
                self.user.teams.remove(key)
            else:
                all_teams.append(val)
        self.user.put()

        #teams = ndb.get_multi(self.user.teams)
        #for idx, val in enumerate(teams):
        #    if val is None:
        #        self.user.teams[idx].
        #    print idx, val
        nexturl = previous = None
        count = len(self.user.teams)
        return get_teams_object(all_teams), nexturl, previous, count

    def get_replies_object(self):
        query = Reply.query(Reply.user == self.user.key)
        key = self.user.username + '_replies_count'
        return ReplyRepo.get_replies_object(query)

    def update_info(self, args):
        for key in args:
            setattr(self.user, key, args[key])
        self.user.put()
        #return user
        return self.get_user_object()

    def toggle_author(self):
        self.user.author = not self.user.author
        self.user.put()
        return self.get_user_object()

    @classmethod
    def get_admin_users(cls):
        query = User.query(User.team_admin is True)
        return cls.get_all_users('admin_users', query)

    def toggle_admin(self):
        self.user.team_admin = not self.user.team_admin
        self.user.put()
        return self.get_user_object()

def user_reply_model(reply):
    if reply is None:
        return
    return dict(
        id=reply.key.id(),
        body=reply.body,
        topic=None if reply.topic.get() is None else get_topic_object(reply.topic.get()),
        votes=reply.vote,
        created=reply.created,
        key=reply.key.urlsafe(),
        username=reply.user.get().username)

def get_user_object(user):
    return dict(
        date_joined=user.created,
        email=user.email,
        username=user.username,
        avatar=user.avatar_url if user.google_public_profile_url is not "" else user.google_public_profile_url,
        comments_count=len(user.comments),
        key=user.key.urlsafe(),
        id=user.key.id(),
        author=user.author,
        token=user.access_token,
        signed_in=False if user.google_plus_id == "" else True,
        admin=user.admin,
        gplus_id=user.google_plus_id,
        gplus_display_name=user.google_display_name,
        gplus_friends=map(lambda l: (get_friends_model(l)), user.get_friends()),
    )

def get_friends_model(friend):
    return dict(
        name=friend.username,
        avatar=friend.avatar_url,
        image_url=friend.image_url,
        google_image_url=friend.google_image_url,
        google_public_profile_url=friend.google_public_profile_url,
    )

class ReplyRepo(object):
    def __init__(self, reply_id):
        if type(reply_id) is Reply:
            self.reply = reply_id
        else:
            self.reply = ndb.Key(urlsafe=reply_id).get()
            print self.reply
            print "hello"
            #self.reply = Reply.get_by_id(reply_id)

    def get_reply_object(self):
        reply_object = util.model_db_to_object(self.reply)
        reply_object['by'] = self.reply.user.get().username
        topic = self.reply.topic.get()
        if topic:
            reply_object['topic'] = topic.title
            reply_object['topic_id'] = topic.key.id()
            team = topic.team.get()
            if team:
                reply_object['team'] = team.logo
                reply_object['team_name'] = team.name
        return reply_object

    def get_reply(self):
        return self.reply.key


    def update_reply(self, args):
        self.reply.body = args['body']
        reply = self.reply.put()
        model = ReplyRepo(reply.get())
        return model.get_reply_object()

    def delete_reply(self):
        self.reply.key.delete()
        return True

    @classmethod
    def get_all_replies(cls):
        replies = Reply.query().fetch()
        return map(lambda l: reply_model(l), replies)

    @classmethod
    def get_replies_object(cls, query=None):
        if query is None:
            query = Reply.query()
        replies, next = util.retrieve_dbs(
            query,
            limit=util.param('limit', int),
            cursor=util.param('cursor'),
            order=util.param('order'),
        )
        replies_object = get_replies_object(replies)
        return replies_object, next

    def upvote(self, user):
        upvote(self.reply, user)
        return self.get_reply_object()

    def downvote(self, user):
        downvote(self.reply, user)
        return self.get_reply_object()

def get_replies_object(replies):
    obj = []
    for reply in replies:
        #if validate_reply(reply):
        reply_object = util.model_db_to_object(reply)
        topic = reply.topic.get()
        if topic:
            reply_object['topic'] = topic.title
            try:
                team = topic.team.get()
                if team:
                    reply_object['team'] = team.logo
            except:
                team = topic.second_team.get()
                if team:
                    reply_object['team'] = team.logo
        user = reply.user.get()
        if user:
            reply_object['by'] = user.username
            reply_object['user_url'] = user.avatar_url

        obj.append(reply_object)
        #else:
        #    reply.key.delete()
    return obj

def get_users_object(users):
    users_object = []
    for user in users:
        user_object = util.model_db_to_object(user)
        users_object.append(user_object)
    return users_object

def authors_model(author):
    return dict(
        name=author.username,
        author=author.author,
        id=author.key.id(),
    )
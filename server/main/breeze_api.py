from google.appengine.ext import ndb
from main import app, util
import auth
from flask_restful import Resource, Api, reqparse, fields, marshal, marshal_with,abort
from flask import request
from model import Team
from repo import LeagueRepo, TeamRepo, TopicRepo,UserRepo, ReplyRepo, notification, topic_notification


api = Api(app,catch_all_404s=True)

API_URL = '/api/v2.0/'


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
topic_team_field = {
    'name': fields.String,
    'logo': fields.String,
    'followers_count': fields.Integer,
}
topic_field = {
    'title': fields.String,
    'replies': fields.Nested(reply_field),
    'created': fields.String,
    'author': fields.String,
    'votes': fields.Integer,
    'key': fields.String,
    'body': fields.String,
    'id': fields.Integer,
    'topic_url': fields.String,
    'vote_url': fields.String,
    'team': fields.Nested(topic_team_field),
}

user_topic_field = {
    'title': fields.String,
    'created': fields.String,
    'author': fields.String,
    'votes': fields.Integer,
    'body': fields.String,
    'id': fields.Integer,
    'team': fields.Nested(topic_team_field),
}

simplest_team_fields = {
    'name': fields.String,
}

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

follow_fields = {
    'count': fields.Integer,
    'button_class': fields.String,
    'text': fields.String,
}
team_followers_fields = {
    'name': fields.String,
}
button_field = {
    "isfollowing": fields.String,
    "class": fields.String,
    "text": fields.String
}

team_fields = {
    'name': fields.String,
    'admin': fields.String,
    'logo': fields.String,
    'c_league':fields.String,
    'type':fields.String,
    'coach': fields.String,
    'topics': fields.Nested(simple_topic_field),
    'followers': fields.Nested(team_followers_fields),
    'league': fields.String,
    'key': fields.String,
    'info': fields.String,
    'uri': fields.Url('teams3'),
    'button': fields.Nested(button_field)
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
    'uri': fields.Url('teams3'),
    #'uri': fields.Url('league_team_url'),
    #'topic_url':fields.Url('team_topics1'),
    'followers_count': fields.Integer
}


league_fields = {
    'name': fields.String,
    'created':fields.String,
    'logo': fields.String,
    'type': fields.String,
    'key': fields.String,
    'id': fields.Integer,
    'info': fields.String,
    'uri': fields.Url('teams_with_league_edit2'),
    'name_url':fields.String,
}

user_teams = {
    'name': fields.String,
    'league': fields.String,
    'logo': fields.String,
    'key': fields.String,
}
user_reply_field = {
    'body': fields.String,
    'votes': fields.Integer,
    'created': fields.DateTime,
    'key': fields.String,
    'username': fields.String,
    'topic': fields.Nested(user_topic_field),
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
friends_fields = {
    'avatar_url': fields.String,
    'email': fields.String,
    'name': fields.String,
    'username': fields.String,
    'image_url': fields.String,
    'google_display_name':fields.String,
    'google_plus_id': fields.String,
    'key': fields.String,
    'id': fields.Integer,
    'teams':fields.Nested(simple_team_field),
    'topics_count':fields.Integer,
    'replies_count':fields.Integer
}

simple_user_fields = {
    'username': fields.String,
    'comments_count': fields.Integer,
    'date_joined': fields.DateTime,
    'avatar': fields.String,
    'key': fields.String,
    'id': fields.Integer,
    'author': fields.Boolean,
    'admin': fields.Boolean,
    'signed_in':fields.Boolean,
    'gplus_display_name':fields.String,
}

author_fields = {
    'username': fields.String,
    'teams': fields.Nested(simple_team_field),
    'comments': fields.Nested(user_reply_field),
    'id': fields.Integer,
    'topics': fields.Nested(topic_field),
    'teams_administered': fields.Nested(simple_team_field),
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
def get_single_result_object(result,status=None):
    return {
        'status': status if status else 'success',
        'data': result

    }


class LeagueListAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.args = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, required=True, help='No league name provided', location='json'),
        self.reqparse.add_argument('logo', type=str, default="", location='json')
        self.reqparse.add_argument('info', type=str, default="", location='json')
        self.reqparse.add_argument('type', type=str, default="club", location='json')
        self.args.add_argument('include_teams', type=bool, default=False, location='args')
        super(LeagueListAPI, self).__init__()


    def get(self):
        all_leagues,cursor = LeagueRepo.get_all_leagues_object()
        response = get_array_result_object(all_leagues,league_fields, next=cursor)
        return response


    def post(self):
        args = self.reqparse.parse_args()
        data = dict(name=args['name'], logo=args['logo'],
                    info=args['info'], league=args['name'],type=args['type'])
        league = LeagueRepo.create_league(data)
        result = marshal(league,league_fields)
        notification('leagues', 'league_created', league=result)
        return get_single_result_object(result), 201

class LeagueAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, default="", help='No league name provided', location='json'),
        self.reqparse.add_argument('logo', type=str, default="", location='json')
        self.reqparse.add_argument('info', type=str, default="", location='json')
        self.reqparse.add_argument('type', type=str, default="club", location='json')
        self.reqparse.add_argument('include_teams', type=bool, default=False, location='args')
        super(LeagueAPI, self).__init__()

    def get(self, name):
        league_repo = LeagueRepo(name)
        if league_repo.league is None:
            abort(404)
        league = league_repo.get_league_object()
        response = marshal(league, league_fields)
        return get_single_result_object(response)

    def put(self, name):
        args = self.reqparse.parse_args()
        league = LeagueRepo(name)
        if league.league is None:
            abort(404)
        data = dict(name=args['name'], logo=args['logo'],
                    info=args['info'],type=args['type'])
        league_key = league.update_league(data)
        league_model = util.model_db_to_object(league_key.get())
        response = marshal(league_model,league_fields)
        return get_single_result_object(response), 203

    def delete(self, name):
        league = LeagueRepo(name)
        if league.league is None:
            abort(404)
        return {"result": league.delete_league()}

api.add_resource(LeagueListAPI, API_URL + 'leagues', endpoint='leagues2')
api.add_resource(LeagueAPI, API_URL + 'leagues/<string:name>', endpoint='teams_with_league_edit2')
api.add_resource(LeagueAPI, API_URL + 'leagues/<int:name>', endpoint='teams_with_league_edit3')

LEAGUE_URL = API_URL+'leagues/<string:name>/'
class LeagueTeamListAPI(Resource):
    def __init__(self):
        self.args = reqparse.RequestParser()
        self.req = reqparse.RequestParser()
        self.req.add_argument('name', type=str, required=True, help='No team name provided', location='json'),
        self.req.add_argument('logo', type=str, required=True, location='json')
        self.req.add_argument('coach', type=str, location='json',default='')
        self.req.add_argument('admin', type=str, required=True, help="No User name provided", location='json')
        self.req.add_argument('c_league', type=str, default='european', help="No User name provided", location='json')
        self.req.add_argument('type',type=str,default='club', location='json')
        self.req.add_argument('info', type=str, default='', location='json')
        super(LeagueTeamListAPI, self).__init__()

    def get(self, name):
        league_repo = LeagueRepo(name)
        if league_repo.league is None:
            abort(404)
        teams,next,previous,count = league_repo.get_teams_object()
        response = get_array_result_object(teams,simple_team_field,next=next,previous=previous,total=count)
        return response

    def post(self,name):
        req = self.req.parse_args()
        league = LeagueRepo(name)
        if league.league is None:
            abort(404)
        team = league.create_team(req)
        response = marshal(team, simple_team_field)
        notification(name.replace(" ",""), 'team_created', team=response)
        return response,201
        #return {'team': marshal(team, simple_team_field)}, 201

api.add_resource(LeagueTeamListAPI, LEAGUE_URL+'teams', endpoint='league_teams_url')

class TeamListAPI(Resource):
    def get(self):
        teams,next,previous,count = TeamRepo.get_all_teams_object('team_count')
        response = get_array_result_object(teams, simple_team_field, next=next, previous=previous, total=count)
        return response

class TeamAPI(Resource):
    def __init__(self):
        self.args = reqparse.RequestParser()
        self.req = reqparse.RequestParser()
        self.req.add_argument('logo', type=str, default="", location='json')
        self.req.add_argument('name', type=str, default="", location='json')
        self.req.add_argument('coach', type=str, default="", location='json')
        self.req.add_argument('admin', type=str, default="", location='json')
        self.req.add_argument('league', type=str, default="", location='json')
        self.req.add_argument('c_league', type=str, default="european", location='json')
        self.req.add_argument('type', type=str, default="club", location='json')
        self.req.add_argument('info', type=str, default="", location='json')
        self.req.add_argument('follow_url', type=str, location='json')
        self.args.add_argument('include_topics', type=bool, default=False, location='args')
        super(TeamAPI, self).__init__()

    def get(self, name):
        team = TeamRepo(name)
        if team.team is None:
            abort(404)
        team_object = team.get_team_object()
        response = marshal(team_object,simple_team_field)
        return get_single_result_object(response)
        #return {'team': marshal(teams, simple_team_field)}

    def put(self, name):
        req = self.req.parse_args()
        team = TeamRepo(name)
        team.update_team(req)
        team_model = team.get_team_object()
        response = marshal(team_model, simple_team_field)
        notification(response['name'].replace(" ",""), 'team_updated', team=response)
        return get_single_result_object(response), 203
        #return {'team': marshal(team_model, simple_team_field)}, 201

    def delete(self, name):
        team = TeamRepo(name)
        response = marshal(team.get_team_object(),simple_team_field)
        notification(response['name'].replace(" ",""), 'team_deleted', team=response)
        team.delete_team()
        return {"result": True}

api.add_resource(TeamListAPI, API_URL + 'teams', endpoint='teams2')
api.add_resource(TeamAPI, API_URL + 'teams/<string:name>', methods=['GET','PUT','DELETE'], endpoint='teams3')

api.add_resource(TeamAPI, API_URL + 'teams/<int:name>', methods=['PUT'], endpoint='teams4')

class AdminTeamsList(Resource):
    def get(self,user):
        admin = UserRepo(user_id=user)
        if admin.user is None:
            abort(404)
        if admin.user.team_admin is False:
            abort(401)
        teams,next,previous,count = admin.get_administered_teams_list()
        response = get_array_result_object(teams, simple_team_field,next=next,previous=previous,total=count)
        return response

api.add_resource(AdminTeamsList,API_URL+'admins/<int:user>/teams',endpoint='admin_teams')

class FollowTeamAPI(Resource):
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

class TeamTopicListAPI(Resource):
    def __init__(self):
        self.args = reqparse.RequestParser()
        super(TeamTopicListAPI, self).__init__()

    def get(self, team_name):
        team = TeamRepo(team_name)
        topics,next = team.get_topics_object()
        response = get_array_result_object(topics,simple_topic_field,next=next)
        return response



class TopicListAPI(Resource):
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
        topic_notification(response['team'], 'topic_added', topic=response)
        topic_notification(response['second_team'], 'topic_added', topic=response)
        return get_single_result_object(response), 203


api.add_resource(TopicListAPI, API_URL + 'topics', endpoint='all_topicss1')


class TopicAPI(Resource):
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
        topic_notification(response['team'],'topic_updated',topic=response)
        topic_notification(response['second_team'],'topic_updated',topic=response)
        return get_single_result_object(response)

    def delete(self, topic_id):
        topic = TopicRepo(topic_id)
        response = marshal(topic.fetch_topic_objects(), simple_topic_field)
        topic_notification(response['team'], 'topic_deleted', topic=response)
        topic_notification(response['second_team'], 'topic_deleted', topic=response)
        if topic.topic:
            topic.delete_topic()
        return {'result': True}


api.add_resource(TeamTopicListAPI, API_URL + 'teams/<string:team_name>/topics', endpoint='team_topics1')
api.add_resource(TopicAPI, API_URL + 'topics/<int:topic_id>', endpoint='single_topic1',
                 methods=['GET','PUT','DELETE'])

class TopicRepliesAPI(Resource):
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
        notification(response['team_name'].replace(" ",""), 'reply_added', reply=response,topic_id=topic_id)

        return get_single_result_object(response),201

api.add_resource(TopicRepliesAPI, API_URL + 'topics/<int:topic_id>/replies', endpoint='topic_replies')

class TopicVoteAPI(Resource):
    def get(self,topic_id):
        topic_repo = TopicRepo(topic_id)
        topic = topic_repo.topic
        if topic is None:
            abort(404)
        topic_model = topic_repo.upvote(auth.current_user_db())
        response = marshal(topic_model, simple_topic_field)
        notification(response['team'].replace(" ",""), 'topic_upvote', topic=response)
        return get_single_result_object(response)

    def delete(self,topic_id):
        topic_repo = TopicRepo(topic_id)
        topic = topic_repo.topic
        if topic is None:
            abort(404)
        topic_model = topic_repo.downvote(auth.current_user_db())
        response = marshal(topic_model, simple_topic_field)
        notification(response['team'].replace(" ",""), 'topic_downvote', topic=response)
        return get_single_result_object(response)

api.add_resource(TopicVoteAPI, API_URL + 'topics/<int:topic_id>/vote', endpoint='topic_vote2')

class ReplyAPI(Resource):
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
        notification(response['team_name'].replace(" ",""), 'reply_updated', reply=response, topic_id=response['topic_id'])
        return response, 203

    def delete(self, reply_id):
        reply = ndb.Key(urlsafe=reply_id)
        replied = reply.get()
        if replied:
            replied.key.delete()
        return {'result': True}

api.add_resource(ReplyAPI, API_URL + 'replies/<string:reply_id>', endpoint='update_delete_reply2')

class ReplyVoteAPI(Resource):
    def get(self, reply_id):
        reply_repo = ReplyRepo(reply_id)
        reply = reply_repo.reply
        if reply is None:
            abort(404)
        reply_model = reply_repo.upvote(auth.current_user_db())
        response = marshal(reply_model, reply_field)
        return get_single_result_object(response)

    def delete(self, reply_id):
        reply_repo = ReplyRepo(reply_id)
        reply = reply_repo.reply
        if reply is None:
            abort(404)
        reply_model = reply_repo.downvote(auth.current_user_db())
        response = marshal(reply_model, reply_field)
        return get_single_result_object(response)

api.add_resource(ReplyVoteAPI, API_URL + 'replies/<string:reply_id>/vote', endpoint='reply_vote')

class UserReplyListAPI(Resource):
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

api.add_resource(UserReplyListAPI, API_URL + 'me/comments', endpoint='replies_with_topic_edit2')

class UserTeamsAPI(Resource):
    def get(self):
        user = UserRepo()
        if util.param('team_admin',bool):
            teams,next,previous,count = user.get_administered_teams_list()
        else:
            teams, next, previous, count = user.get_teams_object()
        response = get_array_result_object(teams, simple_team_field,next=next,previous=previous,total=count)
        return response



class UserTeamUnFollow(Resource):
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

api.add_resource(UserTeamsAPI, API_URL+'my-teams', endpoint='user_teams')
api.add_resource(UserTeamUnFollow, API_URL+'my-teams/<string:team_name>', endpoint='user_teams_unfollow')

class UserTopicsAPI(Resource):
    def get(self):
        author = UserRepo()
        if util.param('author',bool):
            topics, next = author.get_authored_topics_object()
        else:
            topics, next= author.get_all_topics_from_followed_teams()
            print topics
        response = get_array_result_object(topics, simple_topic_field,next=next)
        return response

api.add_resource(UserTopicsAPI, API_URL + 'me/topics', endpoint='author_topics2')


simplest_user_field = {
    'name': fields.String,
    'author':fields.Boolean,
    'admin': fields.Boolean,
    'team_admin':fields.Boolean,
    'username':fields.String,
    'email':fields.String,
    'avatar_url': fields.String,
    'image_url':fields.String,
    'key':fields.String,
    'id':fields.Integer,
}

class UserListAPI(Resource):
    def get(self):
        if util.param('team_admin',bool):
            users,next,previous,total = UserRepo.get_admin_users()
        else:
            users,next,previous,total = UserRepo.get_all_users('all_users_count')
        response = get_array_result_object(users,simplest_user_field,next=next,previous=previous,total=total)
        return response

api.add_resource(UserListAPI, API_URL + 'users', endpoint='all_the_users_in_gf')

#Assign Authors and Admin
class AuthorAPI(Resource):

    def get(self,user_id):
        user = UserRepo(user_id)
        if util.param('team_admin',bool):
            model = user.toggle_admin()
        else:
            model = user.toggle_author()
        return get_single_result_object(marshal(model,simplest_user_field))

    def post(self, user_id):
        user_repo = UserRepo(user_id)
        user = user_repo.update_info(request.json)
        print user
        user_model = UserRepo(user.key.id()).get_user_object()
        return get_single_result_object(marshal(user_model,simplest_user_field))


api.add_resource(AuthorAPI, API_URL + 'users/<int:user_id>',endpoint='assign_authors_admin')

class UserDetailsAPI(Resource):
    def __init__(self):
        self.user = UserRepo()
        self.args = reqparse.RequestParser()
        super(UserDetailsAPI, self).__init__()

    def get(self):
        user_repo = UserRepo()
        user_db = user_repo.get_user_object()
        return get_single_result_object(marshal(user_db, user_fields))
        #return {'user': marshal(user_db, simple_user_fields)}

    def put(self):
        user_object = self.user.update_info(request.json)
        return get_single_result_object(marshal(user_object, user_fields))

api.add_resource(UserDetailsAPI, API_URL + 'me/profile', endpoint='user_details2')


class GooglePlusFriends(Resource):
    def get(self):
        user = UserRepo()
        friends = user.get_friends_object()
        return get_array_result_object(friends,friends_fields)
        #return {'user': marshal(friends, friends_fields)}

api.add_resource(GooglePlusFriends, API_URL + 'me/friends', endpoint='google_plus_friends2')

class PostTopicOnGooglePlus(Resource):
    def get(self,id):
        user = UserRepo()
        topic = TopicRepo(id)
        result = user.post_topic_on_google_plus(topic.get_topic().topic_url)
        return result

api.add_resource(PostTopicOnGooglePlus, API_URL + 'post_g_topic/<int:id>', endpoint='post_g_topic')

class PostReplyOnTopic(Resource):
    def get(self,reply_key):
    #def get(self):
        user = UserRepo()
        reply = ReplyRepo(reply_key)
        reply_model = reply.reply

        result = user.post_comment_on_google_plus(reply_model.topic.get().title,
                                                  reply_model.body,user.get_user().username)
        return result

api.add_resource(PostReplyOnTopic, API_URL + 'post_g_reply/<string:reply_key>', endpoint='post_g_reply')


class FriendTeamsAPI(Resource):
    def get(self,id):
        user = UserRepo(id)
        teams,next,previous,count = user.get_teams_object()
        return get_array_result_object(teams,simple_team_field)

api.add_resource(FriendTeamsAPI,API_URL+'users/<int:id>/teams',endpoint='friends_teams')

class GooglePlusUsersFollowingTeamAPI(Resource):
    def get(self):
        pass

class UserTeams(Resource):
    def get(self,user_id):
        pass


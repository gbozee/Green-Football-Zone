from google.appengine.api import memcache
#from google.appengine.dist27 import urllib
from google.appengine.api import app_identity
from google.appengine.ext import ndb
import auth
from google_plus_api import GooglePlus
from model import User, League, Team, Topic, Reply
import util
from util import async


server_url = app_identity.get_default_version_hostname()
@async
def notification(team_name,event,**kwargs):
    notice = kwargs
    print notice
    util.create_channel(team_name,event,notice)
def topic_notification(team_name,event,**kwargs):
    if team_name:
        kwargs['team_name'] = team_name
        notification(team_name.replace(" ",""),event,**kwargs)



def followed_topic_notification(my_topic,**kwargs):
    if my_topic.team in auth.current_user_db().teams:
        if 'reply' in kwargs:
            notification('followed_teams','reply_added',**kwargs)
        else:
            notification('followed_teams', 'topic_added',**kwargs)


def get_leagues_object(leagues):
    leagues_object = []
    for league in leagues:
        league_object = util.model_db_to_object(league)
        print type(league_object['created'])
        #league_object = league.to_dict()
        #print league_object
        #teams = Team.query(Team.league == league.key).fetch()
        #teams_object = get_teams_object(teams)
        #league_object['teams'] = teams_object
        leagues_object.append(league_object)
    return leagues_object


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


class LeagueRepo(object):
    def __init__(self, name):
        if type(name) == int:
            self.league = ndb.Key('League',name).get()
        else:
            new_name = name.lower().title()
            self.league = League.retrieve_one_by('name', new_name)


    def get_league(self):
        return self.league

    def get_league_object(self):
        league_object = util.model_db_to_object(self.league)
        return league_object
        #return get_league_object(self.league)

    def get_league_with_teams_object(self):
        league = self.get_league_object()
        teams = Team.query(Team.league == self.league.key).fetch()
        league['teams'] = get_teams_object(teams)
        return league

    def get_teams_object(self):
        query = Team.query(Team.league == self.league.key)
        key_name = self.league.name + '_count'
        teams_object, next, previous, count = TeamRepo.get_all_teams_object(key_name, query)
        #teams, cursor = util.retrieve_dbs(
        #    Team.query(Team.league == self.league.key),
        #    limit=util.param('limit', int),
        #    cursor=util.param('cursor'),
        #    order=util.param('order'),
        #)
        #teams_object = get_teams_object(teams)
        return teams_object, next, previous, count

    def get_teams_from_league_object(self):
        return map(lambda l: get_team_object(l), self.league.teams)

    #@classmethod
    #def get_teams_from_league_object(cls, league):
    #    v = map(lambda l: get_team_object(l),league.teams)
    #    return map(lambda x: x['teams']=)


    @classmethod
    def get_all_leagues(cls):
        return League.query().get()


    @classmethod
    def get_all_leagues_object(cls, query=None):
        if query is None:
            query = League.query()
        leagues, next = util.retrieve_dbs(
            query,
            limit=util.param('limit', int),
            cursor=util.param('cursor'),
            order=util.param('order'),
            type=util.param('type')
        )

        leagues_object = get_leagues_object(leagues)
        #return map(lambda l: get_league_object(l), leagues),cursor
        return leagues_object, next

    @classmethod
    def get_all_leagues_with_teams_object(cls):
        leagues, cursor = util.retrieve_dbs(
            League.query(),
            limit=util.param('limit', int),
            cursor=util.param('cursor'),
            order=util.param('order'),
        )
        leagues_object = get_leagues_object(leagues)

        return leagues_object, cursor
        #if len(leagues)==0:
        #    return []
        #return map(lambda l: get_all_league_objects(l), leagues)

    @classmethod
    def create_league(cls, league):
        name = league['name'].lower().title()
        new_league = League(
            parent=ndb.Key("League", league['league'] or "*notitle"),
            name=name,
            type=league['type'] or 'club',
            info=league['info'],
            logo=league['logo']
        )
        key = new_league.put()
        league = key.get()
        model = util.model_db_to_object(league)
        util.get_or_set_count_by_memcache('league_count', League.query(), increment=True)
        return model


    def update_league(self, league):
        self.league.type = league['type']
        if league["name"] is not "":
            self.league.name = league['name']
        if league['logo'] is not "":
            self.league.logo = league['logo']
        if league['info'] is not "":
            self.league.info = league['info']


        return self.league.put()

    def delete_league(self):
        self.league.key.delete()
        util.get_or_set_count_by_memcache('league_count', League.query(), increment=False)
        return True

    def get_teams_(self, ):
        ancestor_key = ndb.Key("Team", self.league)
        return Team.query(ancestor=ancestor_key).fetch()

    def get_team_from_league(self, team):
        name = team.lower().title()
        return Team.query(Team.name == name, ancestor=self.league.key).get()

    def create_team(self, team):
        print team
        admin = User.retrieve_one_by('username', team['admin'].lower())
        team_name = team['name'].lower().title()
        new_team = Team(
            league=self.league.key,
            name=team_name,
            logo=team['logo'],
            c_league=team['c_league'],
            coach=team['coach'] or '',
            type=team['type'],
            admin=admin.key,
            info=team['info'] or '',
            follow_url=server_url + '/gteam/' + team_name
        )
        new_team.put()

        team_object = util.model_db_to_object(new_team)

        return team_object

    @classmethod
    def get_leagues_by_tyep(cls, type):
        query = League.query(League.type == type)
        return LeagueRepo.get_all_leagues_object(query=query)


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
        author = auth.current_user_db()
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
        user = auth.current_user_db()
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
        followed_topic_notification(self.topic,team_name=topic_model['team'])
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
        user = auth.current_user_db()
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
        followed_topic_notification(self.topic, reply=reply_object,topic=self.fetch_topic_objects())

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
        topic.author = auth.current_user_db().key
        topic.title = args['title']
        topic.body = args['body']
        t = topic.put().get()

        t.topic_url = server_url + '/gtopic/' + str(t.key.id())
        t.vote_url = server_url + '/google_votes/' + str(t.key.id())
        t.put()
        tt = t
        if 'team' in args:
            if args['team'] is not "":
                tt = TeamRepo(args['team']).post_topic(t)
        if 'second_team' in args:
            if args['second_team'] is not "":
                tt = TeamRepo(args['second_team']).post_topic(t, attr='second_team')
        followed_topic_notification(tt)
        obj = TopicRepo(tt.key.id())
        return obj.fetch_topic_objects()


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

#def validate_reply(reply):
#    if reply.topic:
#        if reply.topic.get():
#            return True
#    return False
    #return True if reply.topic and reply.topic.get() else False


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


def get_users_object(users):
    users_object = []
    for user in users:
        user_object = util.model_db_to_object(user)
        users_object.append(user_object)
    return users_object

def get_friends_object(users):
    users_object = []

    for user in users:
        reply_query = Reply.query(Reply.user == user.key)
        topic_query = Topic.query(Topic.author == user.key)
        user_object = util.model_db_to_object(user)
        user_teams = ndb.get_multi(user.teams)
        teams_object = get_teams_object(user_teams)
        user_object['teams'] = teams_object
        replies_count = len(ReplyRepo.get_replies_object(reply_query)[0])
        user_object['replies_count'] = replies_count
        topics_count = len(TopicRepo.get_all_topics_objects(topic_query)[0])
        user_object['topics_count'] = topics_count
        users_object.append(user_object)
    return users_object

class UserRepo(object):
    def __init__(self, user_id=None):
        if user_id is None:
            self.user = auth.current_user_db()
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

    def get_friends_object(self):
        g_plus = GooglePlus()
        g_plus.get_and_store_friends()
        friends_object = get_friends_object(self.user.get_friends())

        return friends_object

        #return map(lambda l: get_friends_model(l), self.user.get_friends())

    def post_topic_on_google_plus(self, url):
        g_plus = GooglePlus()
        result = g_plus.add_topic_to_google_plus_activity(url)
        return result


    def post_comment_on_google_plus(self, url, comment, user):
        g_plus = GooglePlus()
        result = g_plus.add_reply_to_google_plus_activity(url, comment, user)
        return result

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


def get_all_league_objects(league):
    return dict(name=league.name,
                info=league.info,
                logo=league.logo,
                id=league.key.id(),
                key=league.key.urlsafe(),
                teams=map(lambda l: get_team_object(l), league.teams))


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


def get_followers_model(team):
    return dict(name=team.username)


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


def is_following_button_model():
    return dict(
        isfollowing=True,
        button_class="following",
        text="Following")


def is_not_following_button_model():
    return dict(
        isfollowing=False,
        button_class="",
        button_text="Follow")


def get_follow_result(user, team):
    return dict(
        count=len(team.followers),
        button_class="" if user.key not in team.followers else "following",
        text="Follow" if user.key not in team.followers else "Following",
    )


def authors_model(author):
    return dict(
        name=author.username,
        author=author.author,
        id=author.key.id(),
    )
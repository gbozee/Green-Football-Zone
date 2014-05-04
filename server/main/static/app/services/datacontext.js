(function () {
    'use strict';
//Todo: Rearrange and refractor
    var serviceId = 'datacontext';
    angular.module('app').factory(serviceId,
//        ['$http', 'common', 'Conf','gfService', datacontext]);
        ['$http', 'common', 'Conf','$angularCacheFactory','userInfo',
            'LeagueService','TeamService',
             datacontext]);

    var storeMeta = {
        isLoaded: {
            user_teams_topics: false,
            author_topics: false,
            league_with_teams: false,
            teams: false,
            all_topics: false,
            loaded_locally: false,
            author_teams: false,
            friends: false,
            news:false,
            user_replies:false,
            all_users:false,
            followed_team:false,
            user_profile:false,
        }
    };
    var _friends = [];
    var _user_info = {};
    var _authored_topics = [];
    var news = [];

    function datacontext($http, common, Conf,$angularCacheFactory,userInfo,LeagueService,TeamService) {
        var $q = common.$q;
        var getLogFn = common.logger.getLogFn;
        var log = getLogFn(serviceId);
        var logError = getLogFn(serviceId, 'error');
        var logSuccess = getLogFn(serviceId, 'success');
        var primePromise;
        var _all_user_replies = [];
        var gfCache = $angularCacheFactory.get('gfCache');



        var service = {
//            getTopicByKey: getTopicByKey,
            getTeamTopics: getTeamTopics,
            getButtonClass: getButtonClass,
            getGooglePlusFriends: getGooglePlusFriends,
            prime: prime,
             unfollowTeam:unfollowTeam,
            toggleAdmin:toggleAdmin,
            deleteReply:deleteReply,
            //Admin functions

            getAuthors: toggleAdmin,
            hasGooglePlusToken: hasGooglePlusToken,
            getAllUsers:getAllUsers,
            getFeeds: getFeeds,
                        //User Details
            deleteTopic:deleteAuthoredTopic
        };

        return service;

        function getLeagues(refresh){
            var deferred = $q.defer(),
                leagueCache = $angularCacheFactory.get(gfCache);

            if(refresh){
                leagueCache.remove('all_leagues');
            }
            $http.get(Conf.apiBase+'leagues')

        }
        function unfollowTeam(team){
            var deferred = $q.defer()
            $http.get(Conf.apiBase+'me/teams/'+team+'/unfollow').then(function(data){
                console.log(data);
                deferred.resolve(data);
                log('Just Unfollowed '+team.name);
            });
            return deferred.promise;
        }



        function prime() {
            if (primePromise) return primePromise;
            primePromise = $q.all([userInfo.fetchUserDetails(),
                userInfo.getUserTeams(),userInfo.fetchUserReplies(),
                userInfo.refreshAuthoredTopics(),userInfo.refreshFollowedTopics(true),
//                    getFeeds(true),
                TeamService.getTeams(),LeagueService.getLeagues()])//            $q.all([getAllUserReplies(), getUserInfo(true), getLeagues(true),
//                    getUserTeamTopics(true), getAllTopics(true), getAllTeams(true),
//                    getGooglePlusFriends(true)
//                ])
                .then(extendMetadata())
                .then(success);
            return primePromise;

            function success() {
                log('Primed the data');
                console.log('Replies',_all_user_replies);
                console.log($angularCacheFactory.info());
            }

            function extendMetadata() {
            }
        }

        function getAllUsers(no){
            return userResource.getList({limit:no})
        }

        function getFeeds(refresh){
            if(_isNewsLoaded() && !refresh){
                return $q.when(news);
            }
            var requestUrl = 'http://ajax.googleapis.com/ajax/services/feed/load?v=1.0&callback=JSON_CALLBACK&num=50&q=' +
                encodeURIComponent('http://greenfootball.org/?feed=rss2');

            var deferred = $q.defer();
                $http.jsonp(requestUrl).then(function(res){
                log('Feed Recieved');
                deferred.resolve(res.data.responseData.feed.entries);
                _isNewsLoaded(true);
                news = res.data.responseData.feed.entries;
            });
            return deferred.promise;

        }

        function hasGooglePlusToken() {
            if (_user_info.token === '') {
                return false;
            }
            if (_user_info.token === null) {
                return false;
            }
            return $q.when(typeof (_user_info.token) !== 'undefined');

        }

        function toggleAdmin(user_id) {
            return userResource.uncached.one(user_id).get({team_admin:true});
        }



        function deleteAuthoredTopic(topic){
            var deferred = $q.defer();
            $http.delete(Conf.apiBase+'topics/'+topic.id).then(function(data){
                deferred.resolve(data);
            });
            return deferred.promise;
        }


        function deleteReply(reply){
            var deferred = $q.defer();
            $http.delete(Conf.apiBase+'replies/'+reply.key).then(function(data){
                deferred.resolve(data);
            });
            return deferred.promise;
        }



        function getButtonClass(team_name, forceRefresh) {
            var button = {}

            if (forceRefresh) {
                getTeamsFollowed(forceRefresh)
            }
            var team = _.find(_teams_following, {'name': team_name});
            console.log(team);
            if (typeof(team) !== 'undefined') {
                button.count = team.followers_count;
                button.button_class = "following";
                button.text = "Following";
            }
            else {
                button.button_class = "";
                button.count = 0;
                button.text = "Follow";
            }

            return $q.when(button);

        }

        function getTeamTopics(team_name,forceRefresh) {
            if(!forceRefresh){
                return teamResource.cached.one(team_name).customGETLIST('topics');
            }
            return teamResource.uncached.one(team_name).customGETLIST('topics');
        }


        function _queryFailed(error) {
            var msg = config.appErrorPrefix + 'Error retrieving data.' + error.message;
            logError(msg, error);
            throw error;
        }
        function getGooglePlusFriends(forceRefresh) {
            if (_isFriendsLoaded() && !forceRefresh) {
                return $q.when(_friends);
            }
            if(!_user_info.signed_in){
                return $q.when([])
            }
            var deferred = $q.defer();
            $http.get(Conf.apiBase + 'friends')
                .then(function (result) {
                    _friends = result.data.user;
                    _isFriendsLoaded(true);
                    log('Friends Recieved', _friends.length, 0);
                    deferred.resolve(_friends);

                }, function (error) {
                   logError('Could not recieve Friends');
                   deferred.reject(error);
                });
            return deferred.promise;
        }



//        Team related methods
//        Topic related methods
//        Replies related methods
        function _isTeamsLoaded(value){
            return _areItemsLoaded('teams',value);
        }

        function _isNewsLoaded(value){
            return _areItemsLoaded('news',value);
        }
        function _isFollowedTeamsLoaded(value){
            return _areItemsLoaded('followed_team',value);
        }
        function _isUserLoaded(value){
            return _areItemsLoaded('user_profile',value);
        }

        function _isAuthoredTopicsLoaded(value){
            return _areItemsLoaded('author_topics',value);
        }
        function _isFriendsLoaded(value) {
            return _areItemsLoaded('friends', value);
        }
        function _isRepliesLoaded(value){
            return _areItemsLoaded('user_replies',value);
        }
        function _isUserFollowedTeamTopics(value){
            return _areItemsLoaded('user_teams_topics',value)
        }

        function _areItemsLoaded(key, value) {
            if (value === undefined) {
                return storeMeta.isLoaded[key]; // get
            }
            return storeMeta.isLoaded[key] = value; // set
        }
    }
})();
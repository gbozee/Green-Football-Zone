angular.module('starter.services', ['restangular'])
  .config(['RestangularProvider', function (restangular) {

    restangular.setRestangularFields({
      id: "name",
      route: "restangularRoute",
      selfLink: "self.href",
      name: "name"
    });
    restangular.setRequestInterceptor(function (elem, operation) {
      if (operation === "remove") {
        return undefined;
      }
      return elem;
    });
    // Now let's configure the response extractor for each request
    restangular.setResponseExtractor(function (response, operation, what, url) {
      // This is a get for a list
      var newResponse;
      if (operation === "getList") {
        // Here we're returning an Array which has one special property metadata with our extra information
        newResponse = response.data.results;
        newResponse.metadata = response.data.meta;
      } else {
        // This is an element
        newResponse = response.data;
      }
      return newResponse;
    });
  }])
  .factory('GFRestangular',function(Restangular){
    return Restangular.withConfig(function (RestangularConfigurer) {
      RestangularConfigurer.setBaseUrl('/mobile/v1.0/api');
      RestangularConfigurer.setDefaultHeaders()
    });
  })

  .factory('authInterceptor', function ($rootScope, $q, $window) {
    return {
      request: function (config) {
        config.headers = config.headers || {};
        if ($window.sessionStorage.token) {
          config.headers.Authorization = 'Basic ' + $window.sessionStorage.token;
        }
        return config;
      },
      response: function (response) {
        if (response.status === 401) {
          // handle the case where the user is not authenticated
        }
        return response || $q.when(response);
      }
    };
  })
  .config(function ($httpProvider) {
    $httpProvider.interceptors.push('authInterceptor');
  })

.service('Team',function(datacontext,$http,$q,$timeout){
    var team = {};
    var topics = [];
    var Team = {};

    Team.getTeam = function(id){
      team = _.find(datacontext.teams(),{id:Number(id)});
      return team;
    };

    Team.getTopics = function(team){
      return datacontext.getTeamTopics(team);
    };

    Team.loadMoreTopics = function(){
      return datacontext.getTeamTopics(team,5);
    };

    return Team;
})

  .factory('Topic',function(Team,$http,$q,$timeout){
    var topic = {};
    var comments = [];

    var Topic = {};
    Topic.getTopic =  function(params){
      var deferred = $q.defer();
      var team = Team.getTeam(params.teamId);
      Team.getTopics(team).then(function(topics){
        var topic = _.find(topics,{id:Number(params.topicId)});
        deferred.resolve(topic);
      });
      return deferred.promise;
    };
    Topic.getComments = function(){
      var deferred = $q.defer();
      $http.get('http://localhost:3000/comments').success(function(data){
        comments = data;
        deferred.resolve(comments);
      });
      return deferred.promise;
    };
    Topic.createComment = function(comment){

    };
    Topic.loadMoreComments = function(){
      var deferred = $q.defer();
      $timeout(function() {
        deferred.resolve({
          body: "I agree with you before now but we have improved during the festive period and showed signs of the old Chelsea hence the 3 - 0 victory over Southampton away from home. I think things will fall in place as the season goes.",
          topic: "Chelsea under-performing",
          votes: 0,
          key: "ahlzfmdjZGMyMDEzLWdyZWVuLWZvb3RiYWxsciQLEgVSZXBseRiAgICA-OSuCQwLEgVSZXBseRiAgICAgICACgw",
          created: "2014-01-02T11:51:45.619150",
          team_name: null,
          team: "/img/clubs/premiership/chelsea.jpg",
          user_url: "//gravatar.com/avatar/c8c43b7ff1ae0391529fd23f95abb902?d=identicon&r=x",
          id: 2893222729292,
          by: "melliciousmel"
        });
      },2000);
      return deferred.promise;
    };
    return Topic;
  })

.factory('Topics',function(Topic,User){
    var topics = [];
    var Topics = {};
    Topics.getTopic = function(params){
      if(params.hasOwnProperty('teamId')){
        return Topic.getTopic(params);
      }
      return User.getTopic(params);
    };
    return Topics;
  })
.factory('datacontext',function($window,$http,$q,$timeout){
  var teams = 	$window.RESPONSE.teams;
  var followedTeams = $window.RESPONSE.followed_teams;
  var user = $window.RESPONSE.user;

	function getTeams(){
		return teams;
	}
  function isFollowing(team){
    var index = _.findIndex(followedTeams,{id:team.id});
    return index > -1;
  }
  function getTeam(id){
    return _.find(teams,{id:id});
  }

  function getTeamTopics(team,no_to_load){
    var deferred = $q.defer();
    if(no_to_load){
      $timeout(function() {
        deferred.resolve({
          body: "I will admit, I do not watch soccer like before but I don't know, it seems certain clubs are not as tough as they are hyped to be. Totenham Hotspurs is said to be a thorn in Arsenal 's flesh but really, Arsenal has dominated, winning 17 out of their 43 encounters. Is that how rivalry should be?",
          topic_url: "gcdc2013-green-football.appspot.com/gtopic/4977455852945408",
          second_team: "Arsenal",
          vote_url: "gcdc2013-green-football.appspot.com/google_votes/4977455852945408",
          second_team_url: "/img/clubs/premiership/arsenal.jpg",
          key: "ahlzfmdjZGMyMDEzLWdyZWVuLWZvb3RiYWxschILEgVUb3BpYxiAgICAhN_rCAw",
          replies: 3,
          id: 4977455852945408,
          votes: 0,
          title: "Can Totenham Hotspurs be referred to as a rival or competition to Arsenal this season?",
          author: "gbozee",
          created: "2014-01-04T10:14:57.635550",
          team_url: "/img/clubs/premiership/tottenham_hotspur.jpg",
          team: "Tottenham Hotspurs"
        });
      },2000);
      return deferred.promise;
    }
    $http.get('http://localhost:3000/topics').success(function(data){
      topics = data;
      deferred.resolve(topics);
    });
    return deferred.promise;
  }

  function followTeam(team){
    var deferred = $q.defer();
    $timeout(function(){
      deferred.resolve(team);
    },2000);

    return deferred.promise;
  }

  function getFollowedTeamTopics(){
    var topics = [];
    var deferred = $q.defer();
    $http.get('http://localhost:3000/topics').success(function(data){
      topics = data;
      deferred.resolve(topics);
    });
    return deferred.promise;
  }

    function getUserTeams(){
      var deferred = $q.defer();
      deferred.resolve(followedTeams);
      return deferred.promise;
    }

    function addNewTopic(topic){
      var deferred = $q.defer();
      deferred.resolve();
      return deferred.promise;
    }
    function updateTopic(topic){
      var deferred = $q.defer();
      deferred.resolve();
      return deferred.promise;
    }

    function deleteTopic(topic){
      var deferred = $q.defer();
      deferred.resolve();
      return deferred.promise;
    }

    function postComment(comment){
      var deferred = $q.defer();
      deferred.resolve();
      return deferred.promise;
    }

    function getProfile(){
      var deferred = $q.defer();
      deferred.resolve(user);
      return deferred.promise;
    }

    function fetchUserReplies(){
      var deferred = $q.defer();
      $http.get('http://localhost:3000/replies').success(function(data){
        deferred.resolve(data);
      });
      return deferred.promise;
    }
	return{
		teams:getTeams,
    isFollowing:isFollowing,
    getTeamById:getTeam,
    getTeamTopics:getTeamTopics,
    followTeam:followTeam,
    userTeamTopics:getFollowedTeamTopics,
    getUserTeams:getUserTeams,
    addTopic:addNewTopic,
    updateTopic:updateTopic,
    deleteTopic:deleteTopic,
    postReply:postComment,
    getProfile:getProfile,
    getUserReplies:fetchUserReplies
	};
});
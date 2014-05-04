angular.module('starter.services')
  .factory('User',function(datacontext,$q){
    var storeMeta = {
      isLoaded: {
        user_teams_topics: false,
        followed_team:false,
        user_profile:false
      }
    };
    var replies = [];
    var user = {};
    var teams = [];
    var followedTopics = [];
    var authored_topics = [];

    prime();

    function getUserTeams(refresh){
      if (_isFollowedTeamsLoaded() && !refresh) {
        return $q.when(teams);
      }
      var deferred = $q.defer();
      datacontext.getUserTeams().then(function(result){
        teams = result;
        _isUserFollowedTeamTopics(true);
        deferred.resolve(teams);
      });
      return deferred.promise;
    }

    function getProfile(refresh){
      if (_isUserLoaded() && !refresh) {
        return $q.when(user);
      }
      var deferred = $q.defer();
      datacontext.getProfile().then(function(profile){
        user = profile;
        _isUserLoaded(true);
        deferred.resolve(user);
      });
      return deferred.promise;
    }

    function getReplies(){
      var deferred = $q.defer();
      datacontext.getUserReplies().then(function(response){
        replies = response;
        deferred.resolve(replies);
      });
      return deferred.promise;
    }

    function prime(){
      return $q.all([getProfile(), getUserTeams(),getFollowedTopics(),getReplies()]);
    }
    function extendUser(){
      var deferred = $q.defer();
      prime().then(function(){
        _.extend(user,{teams:teams,topics:authored_topics,replies:replies});
        deferred.resolve(user);
      });
      return deferred.promise;
    }

    function getFollowedTopics(refresh){
      if (_isUserFollowedTeamTopics() && !refresh) {
        return $q.when(followedTopics);
      }
      var deferred = $q.defer();
      datacontext.userTeamTopics().then(function(response){
        followedTopics = response;
        _isUserFollowedTeamTopics(true);
        deferred.resolve(followedTopics);
      });
      return deferred.promise;
    }

    function getTopicFromFollowedTopics(params){
      var deferred = $q.defer();
      getFollowedTopics().then(function(){
        var topic = _.find(followedTopics,{id:Number(params.topicId)});
        console.log(topic);
        deferred.resolve(topic);
      });
      return deferred.promise;

    }

    function isFollowing(team){
      return _.findIndex(teams,{id:team.id}) > -1;
    }

    function unFollowTeam(team){
      var deferred = $q.defer();
//      datacontext.unfollowTeam(team).then(function(result){
        var index = _.findIndex(teams,{id:team.id});
        teams.splice(index,1);
//        getFollowedTopics().then(function(response){
          deferred.resolve(teams);
//        });
//      });
      return deferred.promise;
    }

    function followTeam(team){
      var deferred = $q.defer();
      datacontext.followTeam(team).then(function(result){
        teams.push(team);
        getFollowedTopics().then(function(response){
          deferred.resolve(team);
        });
      });
      return deferred.promise;
    }

    function deleteTopic(topic){
      var deferred = $q.defer();
      datacontext.deleteTopic(topic).then(function(data){
//            datacontext.deleteTopic(topic).then(function(data){
        var index = _.findIndex(authored_topics,{id:topic.id});
//                user.authored_topics.splice(index,1);
        authored_topics.splice(index,1);
        deferred.resolve(authored_topics);

      });
      return deferred.promise;
    }

    function addTopic(v_topic) {
      var deferred = $q.defer();
      datacontext.addTopic(v_topic)
        .then(function (topic) {
//                    user.authored_topics.push(topic);
          authored_topics.push(topic);
          deferred.resolve(authored_topics);

        });
      return deferred.promise;
    }

    function updateTopic(topic){
      var deferred = $q.defer();
      datacontext.updateTopic(topic).then(function(data){
        var index = _.findIndex(authored_topics,{id:topic.id})
        authored_topics[index]=data;
        deferred.resolve(data);

      });
      return deferred.promise;
    }


    function postReply (reply) {
      return datacontext.postReply(reply);
    }


    return {
      teams:getUserTeams,
      followTeam:followTeam,
      unfollowTeam:unFollowTeam,
      isFollowing:isFollowing,
      topics:getFollowedTopics,
      getTopic:getTopicFromFollowedTopics,
      addTopic:addTopic,
      deleteTopic:deleteTopic,
      updateTopic:updateTopic,
      postReply:postReply,
      getProfile:getProfile,
      getUserProfile:extendUser


    };

    function _isFollowedTeamsLoaded(value){
      return _areItemsLoaded('followed_team',value);
    }
    function _isUserLoaded(value){
      return _areItemsLoaded('user_profile',value);
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
  });
angular.module('starter.controllers', [])

.controller('AppCtrl', function($scope) {

})

  .controller('LoginCtrl', function ($scope, $location, OpenFB) {

    $scope.googleLogin = function(){

    }
    $scope.facebookLogin = function () {

      OpenFB.login('email,read_stream,publish_stream').then(
        function () {
          $location.path('/app/home');
        },
        function () {
          alert('OpenFB login failed');
        });
    };

  })
  .controller('HomeCtrl',function($scope,$state,User,$ionicLoading) {
    $scope.loadMore = function(){
    };

    $scope.findTeams = function(){
      $state.go('app.teams');
    };

    $scope.show = function() {
      $scope.loading = $ionicLoading.show({
        content: 'Loading feed...'
      });
    };
    $scope.hide = function(){
      $scope.loading.hide();
    };

    function loadTopics() {
      $scope.show();
      User.topics(true).then(function(topics){
        $scope.hide();
        $scope.topics = topics;
//        $scope.topics = [];
        $scope.$broadcast('scroll.refreshComplete');

      },function(failure) {
        $scope.hide();

      });
    }

    $scope.doRefresh = loadTopics;
    loadTopics();

  })
  .controller('AboutCtrl',function($scope,datacontext){

  })
.controller('ProfileCtrl',function($scope,$state,User){
    User.getUserProfile().then(function(profile){
      $scope.user = profile;
      $scope.teams = profile.teams;
    });

    $scope.unfollow = function(team){
      return User.unfollowTeam(team).then(function(data){
        $scope.teams = data;
      });
    };

    $scope.findTeams = function(){
      $state.go('app.teams');
    }
})
.controller('TeamsCtrl',function($scope,datacontext){
	  $scope.teams = datacontext.teams();

    $scope.isFollowing = function(team){
      return datacontext.isFollowing(team);
    }
})
.controller('TeamCtrl',function($scope,$stateParams,$ionicModal,Team,User){
    $scope.team = Team.getTeam($stateParams.teamId);
    $scope.topicsLoaded = false;
    console.log($scope.team);
    function getTopics(team){
      Team.getTopics(team).then(function(topics){
        $scope.topics = topics;
        $scope.topicsLoaded = true;
      });
    }
    getTopics($scope.team);

    $scope.isFollowing = function(team){
      return User.isFollowing(team);
    };
    $scope.loading = false;
    $scope.follow = function(team){
      $scope.loading = true;
      return User.followTeam(team).then(function(){
        $scope.loading = false;
      })
    };

    // Create and load the Modal
    $ionicModal.fromTemplateUrl('templates/new-topic.html', function(modal) {
      $scope.topicModal = modal;
    }, {
      scope: $scope,
      animation: 'slide-in-up'
    });

    // Called when the form is submitted
    $scope.createTopic = function(topic) {
      User.createTopic(topic).then(function(data){
        $scope.topics.push(data);
      });

      $scope.topicModal.hide();
      topic.title = "";
      topic.body = "";
    };

    // Open our new task modal
    $scope.newTopic = function() {
      $scope.topicModal.show();
    };

    // Close the new task modal
    $scope.closeNewTopic = function() {
      $scope.topicModal.hide();
    };


    $scope.doRefresh = function(){
      $scope.topicsLoaded = false;
      Team.getTopics($scope.team).then(function(topics){
        $scope.topics = topics;
        $scope.topicsLoaded = true;
        $scope.$broadcast('scroll.refreshComplete');
      });
    };

    $scope.loadMore = function() {
      $scope.topicsLoaded = false;
      Team.loadMoreTopics().then(function(topics){
        angular.forEach(topics,function(topic){
          $scope.topics.push(topic);
        });
        $scope.topicsLoaded = true;
        $scope.$broadcast('scroll.infiniteScrollComplete');
        //        $scope.$broadcast('scroll.refreshComplete');
      });
    }
})

.controller('TopicCtrl',function($scope,$stateParams,$ionicModal,Topic,Topics){
    $scope.commentLoaded = false;
  Topics.getTopic($stateParams).then(function(topic){
    $scope.topic = topic;
  });

  Topic.getComments($scope.topic).then(function(comments){
    $scope.comments = comments;
    $scope.commentLoaded = true;
  });

    // Create and load the Modal
    $ionicModal.fromTemplateUrl('templates/new-comment.html', function(modal) {
      $scope.commentModal = modal;
    }, {
      scope: $scope,
      animation: 'slide-in-up'
    });

    // Called when the form is submitted
    $scope.createComment = function(comment) {
      Topic.createComment(comment).then(function(data){
        $scope.comments.push(data);
      });

      $scope.commentModal.hide();
      comment.body = "";
    };

    // Open our new task modal
    $scope.newComment = function() {
      $scope.commentModal.show();
    };

    // Close the new task modal
    $scope.closeNewComment = function() {
      $scope.commentModal.hide();
    };

    $scope.doRefresh = function(){
      $scope.commentLoaded = false;
      Topic.getComments($scope.topic).then(function(comments){
        $scope.comments = comments;
        $scope.commentLoaded = true;
        $scope.$broadcast('scroll.refreshComplete');
      });
    };

    $scope.loadMore = function() {
      $scope.commentsLoaded = false;
      Topic.loadMoreComments().then(function(comments){
        angular.forEach(comments,function(comment){
          $scope.comments.push(comment);
        });
        $scope.commentsLoaded = true;
        $scope.$broadcast('scroll.infiniteScrollComplete');
        //        $scope.$broadcast('scroll.refreshComplete');
      });
      $scope.toggleBody = function(comment){
        if ($scope.isBodyShown(comment)) {
          $scope.shownComment = null;
        } else {
          $scope.shownComment = comment;
        }
      };
      $scope.isBodyShown = function(comment){
        return $scope.shownComment === comment;
      };
    }
});

// Ionic Starter App

// angular.module is a global place for creating, registering and retrieving Angular modules
// 'starter' is the name of this angular module example (also set in a <body> attribute in index.html)
// the 2nd parameter is an array of 'requires'
// 'starter.controllers' is found in controllers.js
angular.module('starter', ['ionic', 'starter.controllers','starter.services','openfb'])

.run(function($ionicPlatform,OpenFB,$rootScope,$state,$window) {
    OpenFB.init('486290954832181');
  $ionicPlatform.ready(function() {
    if(window.StatusBar) {
      // org.apache.cordova.statusbar required
      StatusBar.styleDefault();
    }
  });
    $rootScope.$on('$stateChangeStart', function(event, toState) {
      if (toState.name !== "app.login" && toState.name !== "app.logout" && !$window.sessionStorage['fbtoken']) {
        $state.go('app.login');
        event.preventDefault();
      }
    });

    $rootScope.$on('OAuthException', function() {
      $state.go('app.login');
    });
})

.config(function($stateProvider, $urlRouterProvider) {
  $stateProvider

    .state('app', {
      url: "/app",
      abstract: true,
      templateUrl: "templates/menu.html",
      controller: 'AppCtrl'
    })
    .state('app.login', {
      url: "/login",
      views: {
        'menuContent': {
          templateUrl: "templates/login.html",
          controller: "LoginCtrl"
        }
      }
    })

    .state('app.home', {
      url: "/home",
      views: {
        'menuContent' :{
          templateUrl: "templates/home.html",
          controller:"HomeCtrl"
        }
      }
    })

    .state('app.teams', {
      url: "/teams",
      views: {
        'menuContent' :{
          templateUrl: "templates/teams.html",
          controller:'TeamsCtrl'
        }
      }
    })
    .state('app.profile', {
      url: "/profile",
      views: {
        'menuContent' :{
          templateUrl: "templates/profile.html",
          controller:'ProfileCtrl'
        }
      }
    })

    .state('app.single_topic', {
      url: "/:teamId/topics/:topicId",
      views: {
        'menuContent' :{
          templateUrl: "templates/single_topic.html",
          controller: 'TopicCtrl'
        }
      }
    })
    .state('app.my_teams', {
      url: "/my-teams",
      views: {
        'menuContent' :{
          templateUrl: "templates/my-teams.html",
          controller: 'ProfileCtrl'
        }
      }
    })
    .state('app.single_user_topic', {
      url: "/topics/:topicId",
      views: {
        'menuContent' :{
          templateUrl: "templates/single_topic.html",
          controller: 'TopicCtrl'
        }
      }
    })
  .state('app.single_team', {
      url: "/teams/:teamId",
      views: {
        'menuContent' :{
          templateUrl: "templates/single_team.html",
          controller: 'TeamCtrl'
        }
      }
    })
    .state('app.about', {
      url: "/about",
      views: {
        'menuContent' :{
          templateUrl: "templates/about.html",
          controller: 'AboutCtrl'
        }
      }
    });
  // if none of the above states are matched, use this as the fallback
  $urlRouterProvider.otherwise('/app/home');
});


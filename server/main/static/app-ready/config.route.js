(function () {
  'use strict';
  var app = angular.module('app');
  app.constant('routes', getRoutes());
  app.config([
    '$routeProvider',
    'routes',
    routeConfigurator
  ]);
  function routeConfigurator($routeProvider, routes) {
    routes.forEach(function (r) {
      setRoute(r.url, r.config);
    });
    $routeProvider.otherwise({ redirectTo: '/' });
    function setRoute(url, definition) {
      definition.resolve = angular.extend(definition.resolve || {}, { prime: prime });
      $routeProvider.when(url, definition);
      return $routeProvider;
    }
  }
  prime.$inject = ['datacontext'];
  function prime(dc) {
    return dc.prime();
  }
  function getRoutes() {
    return [
      {
        url: '/',
        config: {
          templateUrl: '/p/app/dashboard/dashboard.html',
          title: 'dashboard',
          settings: {
            nav: 2,
            content: '<i class="icon-dashboard"></i> Dashboard'
          }
        }
      },
      {
        url: '/user-topics',
        config: {
          title: 'user-topics',
          templateUrl: '/p/app/user/topic.html',
          settings: {
            nav: 4,
            content: '<i class="glyphicon glyphicon-user"></i> My Followed Topics'
          }
        }
      },
      {
        url: '/admin',
        config: {
          title: 'admin',
          templateUrl: '/p/app/admin/admin.html',
          settings: {
            nav: 1,
            content: '<i class="icon-lock"></i>Admin'
          }
        }
      },
      {
        url: '/topic/:topic_id',
        config: {
          title: 'replies',
          templateUrl: '/p/app/user/single-topic.html',
          resolve: { set_team: set_team }
        }
      },
      {
        url: '/my-comments',
        config: {
          title: 'posted-comments',
          templateUrl: '/p/app/user/user-replies.html',
          settings: {
            nav: 5,
            content: '<i class="glyphicon glyphicon-comment"></i> Posted Replies'
          }
        }
      },
      {
        url: '/my-friends',
        config: {
          title: 'g+_friends',
          templateUrl: '/p/app/user/friends.html'
        }
      },
      {
        url: '/leagues',
        config: {
          title: 'leagues',
          templateUrl: '/p/app/gf/league.html',
          settings: {
            nav: 3,
            content: '<i class="icon-list"></i> Leagues'
          }
        }
      },
      {
        url: '/leagues/:league_name',
        config: {
          title: 'teams',
          templateUrl: '/p/app/gf/team.html'
        }
      },
      {
        url: '/teams/:team_name',
        config: {
          title: 'single-team',
          templateUrl: '/p/app/gf/single-team.html'
        }
      },
      {
        url: '/all-teams',
        config: {
          title: 'all-teams',
          templateUrl: '/p/app/gf/all_teams.html',
          settings: {}
        }
      },
      {
        url: '/teams/search/:search',
        config: {
          title: 'all-teams',
          templateUrl: '/p/app/gf/all_teams.html'
        }
      },
      {
        url: '/author',
        config: {
          title: 'author',
          templateUrl: '/p/app/user/author.html',
          settings: {
            nav: 6,
            content: '<i class="icon-list"></i> Authored Topics'
          }
        }
      },
      {
        url: '/author/create-topic/:create',
        config: {
          title: 'author',
          templateUrl: '/p/app/user/author.html'
        }
      },
      {
        url: '/update/:topic_id',
        config: {
          title: 'update-topic',
          templateUrl: '/p/app/user/update-topic.html'
        }
      },
      {
        url: '/add_topic',
        config: {
          title: 'add-topic',
          templateUrl: '/p/app/user/update-topic.html',
          resolve: { update_topic: set_add_topic }
        }
      },
      {
        url: '/league_update/:name',
        config: {
          title: 'update-league',
          templateUrl: '/p/app/admin/update-league.html',
          resolve: { update_topic: set_update_league }
        }
      },
      {
        url: '/add_league',
        config: {
          title: 'add-league',
          templateUrl: '/p/app/admin/create-league.html',
          resolve: { update_topic: set_add_league }
        }
      },
      {
        url: '/team_update/:name',
        config: {
          title: 'update-team',
          templateUrl: '/p/app/admin/update-team.html',
          resolve: { update_topic: set_update_team }
        }
      },
      {
        url: '/add_team',
        config: {
          title: 'add-team',
          templateUrl: '/p/app/admin/create-team.html',
          resolve: { update_topic: set_add_team }
        }
      },
      {
        url: '/update-reply/:key',
        config: {
          title: 'update-reply',
          templateUrl: '/p/app/user/update-reply.html'
        }
      },
      {
        url: '/notifications',
        config: {
          title: 'notifications',
          templateUrl: '/p/app/dashboard/notification.html'
        }
      }
    ];
  }
  single_topic.$inject = [
    'common',
    '$route',
    'datacontext'
  ];
  function single_topic(common, $route, datacontext) {
    var defer = common.$q.defer();
    datacontext.getTopicById($route.current.pathParams.topic_id).then(function (data) {
      defer.resolve(data);
    });
    return defer.promise;
  }
  set_update_topic.$inject = ['inhouse'];
  function set_update_topic(inhouse) {
    return inhouse.setTitle('Update Topic');
  }
  set_add_topic.$inject = ['inhouse'];
  function set_add_topic(inhouse) {
    return inhouse.setTitle('Add Topic');
  }
  set_update_league.$inject = ['inhouse'];
  function set_update_league(inhouse) {
    return inhouse.setLeagueTitle('Update League');
  }
  set_add_league.$inject = ['inhouse'];
  function set_add_league(inhouse) {
    return inhouse.setLeagueTitle('Add League');
  }
  set_update_team.$inject = ['inhouse'];
  function set_update_team(inhouse) {
    return inhouse.setTeamTitle('Update Team');
  }
  set_add_team.$inject = ['inhouse'];
  function set_add_team(inhouse) {
    return inhouse.setTeamTitle('Add Team');
  }
  set_team.$inject = [
    'ReplyService',
    '$route'
  ];
  function set_team(replyService, $route) {
    return replyService.getTopic($route.current.pathParams.topic_id).then(function (data) {
      replyService.setTeam(data.team.replace(/\s/g, '', $route.current.pathParams.topic_id));
    });
  }
}());
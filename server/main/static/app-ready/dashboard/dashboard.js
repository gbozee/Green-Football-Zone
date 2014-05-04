(function () {
  'use strict';
  var controllerId = 'dashboard';
  angular.module('app').controller(controllerId, [
    '$rootScope',
    'common',
    'gfService',
    'datacontext',
    'userInfo',
    'Conf',
    'Pusher',
    '$scope',
    dashboard
  ]);
  angular.module('app').controller('userTopics', [
    '$filter',
    'userInfo',
    '$scope',
    userTopicsCtrl
  ]);
  angular.module('app').controller('followedTeams', [
    'userInfo',
    followedTeamsCtrl
  ]);
  function userTopicsCtrl($filter, userInfo, $scope) {
    var ut = this;
    function topics(forceRefresh) {
      return userInfo.refreshFollowedTopics(forceRefresh).then(function (result) {
        ut.followedTopics = result;
        ut.followedTopics = $filter('orderBy')(ut.followedTopics, '-created');
        groupToPages();
      });
    }
    topics();
    $scope.$on('refresh:teams', function () {
      topics(true);
    });
    ut.currentPage = 0;
    ut.itemsPerPage = 2;
    function groupToPages() {
      ut.pagedItems = [];
      for (var i = 0; i < ut.followedTopics.length; i++) {
        if (i % ut.itemsPerPage === 0) {
          ut.pagedItems[Math.floor(i / ut.itemsPerPage)] = [ut.followedTopics[i]];
        } else {
          ut.pagedItems[Math.floor(i / ut.itemsPerPage)].push(ut.followedTopics[i]);
        }
      }
    }
    ut.range = function (start, end) {
      var ret = [];
      if (!end) {
        end = start;
        start = 0;
      }
      for (var i = start; i < end; i++) {
        ret.push(i);
      }
      return ret;
    };
    ut.prevPage = function () {
      console.log(ut.pagedItems);
      if (ut.currentPage > 0) {
        ut.currentPage--;
      }
    };
    ut.nextPage = function () {
      console.log(ut.pagedItems);
      if (ut.currentPage < ut.pagedItems.length - 1) {
        ut.currentPage++;
      }
    };
    ut.setPage = function (n) {
      ut.currentPage = n;
    };
  }
  function followedTeamsCtrl(userInfo) {
    var ft = this;
    ft.currentPage = 0;
    ft.followedTeams = userInfo.pagedTeams;
    ft.itemsPerPage = 6;
    ft.unfollowTeam = userInfo.unfollowTeam;
    ft.prevPage = function () {
      if (ft.currentPage > 0) {
        ft.currentPage--;
      }
    };
    ft.nextPage = function () {
      if (ft.currentPage < ft.followedTeams().length - 1) {
        ft.currentPage++;
      }
    };
    ft.setPage = function (n) {
      ft.currentPage = n;
    };
  }
  function dashboard($rootScope, common, gfService, datacontext, userInfo, Conf, Pusher, $scope) {
    var getLogFn = common.logger.getLogFn;
    var log = getLogFn(controllerId);
    var logError = getLogFn(controllerId, 'error');
    var myTeamResource = gfService.myTeamResource();
    var vm = this;
    vm.news = {
      title: 'GF News',
      description: ''
    };
    vm.gf_news = [];
    vm.friendsCount = userInfo.getFriends;
    vm.title = 'My Dashboard';
    vm.comments = userInfo.replies;
    vm.followedTeams = userInfo.teams;
    vm.feeds = datacontext.getFeeds();
    vm.refreshNews = refreshNews;
    vm.user = userInfo.user;
    vm.signedIn = userInfo.isSignedIn;
    vm.type = 'club';
    vm.clientId = Conf.clientId;
    vm.prefilltext = 'Argue on soccer related contents at Green Football';
    vm.adminTeams = [];
    vm.authoredTopics = [];
    vm.followed_topics = userInfo.followed_topics;
    vm.showPrevious = false;
    vm.showNext = true;
    vm.sortorder = '-votes';
    activate();
    Pusher.subscribe('followed_teams', 'topic_added', function (data) {
      log('New Topic Recieved');
      $scope.$broadcast('refresh:teams');
    });
    Pusher.subscribe('followed_teams', 'reply_added', function (msg) {
      log('Reply from ' + msg.reply.by);
      $rootScope.$broadcast('update:replies');
    });
    vm.setTeamType = function (value) {
      vm.type = value;
    };
    function followedTeams() {
      return _.filter(userInfo.teams(), { type: vm.type });
    }
    vm.friendsIsZero = function () {
      if (userInfo.getFriends().length == 0) {
      }
    };
    function refreshNews() {
      vm.feeds = datacontext.getFeeds(true);
      vm.feeds.then(function () {
        log('Feeds Refreshed');
      });
    }
    function activate() {
      var promises = [];
      common.activateController(promises, controllerId).then(function () {
        log('Activated Dashboard View');
      });
    }
    function getAdminTeams() {
      return myTeamResource.getList({ team_admin: true }).then(function (data) {
        vm.adminTeams = data;
      });
    }
    function getAuthoredTopics() {
      userInfo.getAuthoredTopics().then(function (data) {
        vm.authoredTopics = data;
      });
    }
    vm.currentPage = 0;
    vm.itemsPerPage = 2;
    vm.feeds.then(function (data) {
      console.log(data);
      vm.pagedItems = [];
      for (var i = 0; i < data.length; i++) {
        if (i % vm.itemsPerPage === 0) {
          vm.pagedItems[Math.floor(i / vm.itemsPerPage)] = [data[i]];
        } else {
          vm.pagedItems[Math.floor(i / vm.itemsPerPage)].push(data[i]);
        }
      }
    });
    vm.range = function (start, end) {
      var ret = [];
      if (!end) {
        end = start;
        start = 0;
      }
      for (var i = start; i < end; i++) {
        ret.push(i);
      }
      return ret;
    };
    vm.prevPage = function () {
      console.log(vm.pagedItems);
      if (vm.currentPage > 0) {
        vm.currentPage--;
      }
    };
    vm.nextPage = function () {
      console.log(vm.pagedItems);
      if (vm.currentPage < vm.pagedItems.length - 1) {
        vm.currentPage++;
      }
    };
    vm.setPage = function (n) {
      vm.currentPage = n;
    };
  }
}());
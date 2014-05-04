(function () {
  'use strict';
  var controllerId = 'admin';
  angular.module('app').controller(controllerId, [
    'common',
    'gfUtils',
    'adminService',
    'Pusher',
    admin
  ]);
  angular.module('app').directive('gfTeamList', [gfTeamListDirective]);
  angular.module('app').directive('gfLeagueList', [gfLeagueListDirective]);
  angular.module('app').directive('gfTableHeader', [gfTableHeader]);
  angular.module('app').directive('gfLeagueParginator', [gfLeagueParginator]);
  angular.module('app').service('gfUtils', [gfUtils]);
  angular.module('app').service('adminService', [
    'Restangular',
    '$angularCacheFactory',
    adminService
  ]);
  angular.module('app').directive('gfTable', [gfTable]);
  function adminService(Restangular, $angularCacheFactory) {
    var leagueResource = Restangular.all('leagues');
    var teamResource = Restangular.all('teams');
    var userResource = Restangular.all('users');
    var leagues = leagueResource.getList().$object;
    var teams = teamResource.getList().$object;
    var all_users = userResource.getList().$object;
    var authors = userResource.getList({ author: true }).$object;
    var itemsPerPage = 4;
    var admin = {};
    admin.leagues = function () {
      return leagues;
    };
    admin.teams = function () {
      return teams;
    };
    admin.authors = function () {
      return authors;
    };
    admin.users = function () {
      return all_users;
    };
    admin.addLeague = function (league) {
      return leagueResource.post(league).then(function (data) {
        leagues.push(data);
        return data;
      });
    };
    admin.getLeague = function (league) {
      var x = _.find(leagues, { id: league });
      console.log(x);
      return x;
    };
    admin.getTeams = function () {
      return teamResource.getList();
    };
    admin.getLeagues = function () {
      return leagueResource.getList();
    };
    admin.addTeam = function (team) {
      console.log(team.league);
      var teamToAdd = _.find(leagues, { name: team.league });
      console.log(teamToAdd);
      return teamToAdd.post('teams', team);
    };
    admin.assignRole = function (user, params) {
      return userResource.one(user.id).get(params).then(function (data) {
        console.log(user.id);
        console.log(all_users);
        var index = _.findIndex(all_users, { id: user.id });
        console.log(index);
        all_users[index] = data;
        return data;
      });
    };
    admin.updateLeague = function (league) {
      return leagueResource.one(league.name).customPUT(league).then(function (data) {
        var index = _.indexOf(leagues, { id: league.id });
        leagues[index] = data;
        console.log('Updated', data);
        return data;
      });
    };
    admin.updateTeam = function (team) {
      return teamResource.one(team.name).customPUT(team).then(function (data) {
        var index = _.indexOf(teams, { id: team.id });
        teams[index] = data;
        return data;
      });
    };
    admin.deleteLeague = function (league) {
      return leagueResource.one(league.name).remove().then(function (data) {
        var index = _.indexOf(leagues, { id: league.id });
        leagues.splice(index, 1);
        return groupByPage(leagues, itemsPerPage);
      });
    };
    admin.deleteTeam = function deleteTeam(team) {
      return teamResource.one(team.name).remove().then(function (data) {
        var index = _.indexOf(teams, { id: team.id });
        teams.splice(index, 1);
        return groupByPage(teams, itemsPerPage);
      });
    };
    function groupByPage(array, itemsPerPage) {
      var pagedItems = [];
      for (var i = 0; i < array.length; i++) {
        if (i % itemsPerPage === 0) {
          pagedItems[Math.floor(i / itemsPerPage)] = [array[i]];
        } else {
          pagedItems[Math.floor(i / itemsPerPage)].push(array[i]);
        }
      }
      return pagedItems;
    }
    admin.groupLeaguesByPage = function (val) {
      return groupByPage(leagues, 4);
    };
    admin.groupTeamsByPage = function (val) {
      return groupByPage(teams, 4);
    };
    admin.groupUsersByPage = function (val) {
      return groupByPage(all_users, 4);
    };
    admin.refresh = function () {
      return leagueResource.getList().then(function (data) {
        leagues = data;
        return leagues;
      }).then(function (data) {
        return teamResource.getList().then(function (data) {
          teams = data;
          return teams;
        });
      });
    };
    return admin;
  }
  function gfUtils() {
    function parseUri(str) {
      var o = parseUri.options, m = o.parser[o.strictMode ? 'strict' : 'loose'].exec(str), uri = {}, i = 14;
      while (i--)
        uri[o.key[i]] = m[i] || '';
      uri[o.q.name] = {};
      uri[o.key[12]].replace(o.q.parser, function ($0, $1, $2) {
        if ($1)
          uri[o.q.name][$1] = $2;
      });
      return uri;
    }
    ;
    function _extractUrl(url) {
      var params = parseUri(url);
      return {
        limit: params.queryKey.limit,
        cursor: decodeURIComponent(params.queryKey.cursor)
      };
    }
    parseUri.options = {
      strictMode: false,
      key: [
        'source',
        'protocol',
        'authority',
        'userInfo',
        'user',
        'password',
        'host',
        'port',
        'relative',
        'path',
        'directory',
        'file',
        'query',
        'anchor'
      ],
      q: {
        name: 'queryKey',
        parser: /(?:^|&)([^&=]*)=?([^&]*)/g
      },
      parser: {
        strict: /^(?:([^:\/?#]+):)?(?:\/\/((?:(([^:@]*)(?::([^:@]*))?)?@)?([^:\/?#]*)(?::(\d*))?))?((((?:[^?#\/]*\/)*)([^?#]*))(?:\?([^#]*))?(?:#(.*))?)/,
        loose: /^(?:(?![^:@]+:[^:@\/]*@)([^:\/?#.]+):)?(?:\/\/)?((?:(([^:@]*)(?::([^:@]*))?)?@)?([^:\/?#]*)(?::(\d*))?)(((\/(?:[^?#](?![^?#\/]*\.[^?#\/.]+(?:[?#]|$)))*\/?)?([^?#\/]*))(?:\?([^#]*))?(?:#(.*))?)/
      }
    };
    return { extractCursor: _extractUrl };
  }
  function gfLeagueParginator() {
    return {
      restrict: 'E',
      templateUrl: '/p/app/layout/league-parginator.html',
      scope: {
        items: '=',
        itemsPerPage: '@',
        query: '='
      },
      controller: 'parginationCtrl'
    };
  }
  function admin(common, gfUtils, adminService, Pusher) {
    var getLogFn = common.logger.getLogFn;
    var log = getLogFn(controllerId);
    var vm = this;
    vm.title = 'Admin';
    vm.assignAuthor = assignAuthor;
    vm.assignAdmin = assignAdmin;
    vm.deleteLeague = deleteLeague;
    vm.deleteTeam = deleteTeam;
    vm.currentFeedPage = 1;
    vm.refresh = adminService.refresh;
    vm.showPrevious = false;
    vm.showNext = true;
    vm.deleteLeague = deleteLeague;
    vm.deleteTeam = deleteTeam;
    vm.query = {};
    activate();
    function activate() {
      common.activateController([], controllerId).then(function () {
        log('Activated Admin View');
      });
    }
    Pusher.subscribe('leagues', 'league_created', function (message) {
      log(message.league.name + ' now available');
      vm.refresh();
    });
    function assignAuthor(author) {
      return adminService.assignRole(author);
    }
    function assignAdmin(author) {
      return adminService.assignRole(author, { team_admin: true });
    }
    vm.pagedItems = adminService.groupLeaguesByPage;
    vm.pagedTeamItems = adminService.groupTeamsByPage;
    vm.pagedUserItems = adminService.groupUsersByPage;
    vm.currentLeaguePage = 0;
    vm.currentTeamPage = 0;
    vm.currentUserPage = 0;
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
      if (vm.currentLeaguePage > 0) {
        vm.currentLeaguePage--;
      }
    };
    vm.nextPage = function (pagedItems) {
      console.log(pagedItems);
      if (vm.currentLeaguePage < pagedItems.length - 1) {
        vm.currentLeaguePage++;
      }
    };
    vm.setPage = function (n) {
      vm.currentLeaguePage = n;
    };
    vm.prevTeamPage = function () {
      if (vm.currentTeamPage > 0) {
        vm.currentTeamPage--;
      }
    };
    vm.nextTeamPage = function (pagedItems) {
      console.log(pagedItems);
      if (vm.currentTeamPage < pagedItems.length - 1) {
        vm.currentTeamPage++;
      }
    };
    vm.setTeamPage = function (n) {
      vm.currentTeamPage = n;
    };
    vm.prevUserPage = function () {
      if (vm.currentUserPage > 0) {
        vm.currentUserPage--;
      }
    };
    vm.nextUserPage = function (pagedItems) {
      console.log(pagedItems);
      if (vm.currentUserPage < pagedItems.length - 1) {
        vm.currentUserPage++;
      }
    };
    vm.setUserPage = function (n) {
      vm.currentUserPage = n;
    };
    function deleteLeague(league) {
      return adminService.deleteLeague(league).then(function (data) {
        log('League Deleted');
        vm.pagedItems = adminService.groupLeaguesByPage;
      });
    }
    function deleteTeam(team) {
      return adminService.deleteTeam(team).then(function (data) {
        log('Team Deleted');
        vm.pagedTeamItems = adminService.groupTeamsByPage;
      });
    }
  }
  function gfTeamListDirective() {
    return {
      restrict: 'A',
      template: '<tr data-ng-repeat="p in list">' + '<td><a href="#/team_update/{{ p.name }}">{{ p.name }}</a></td>' + '<td>{{ p.logo }}</td>' + '<td>{{ p.admin }}</td>' + '</tr>',
      scope: { list: '=' }
    };
  }
  function gfLeagueListDirective() {
    return {
      restrict: 'A',
      template: '<tr data-ng-repeat="p in list">' + '<td><a href="#/league_update/{{ $index }}">{{ p.name }}</a></td>' + '<td>{{ p.logo }}</td>' + '</tr>',
      scope: { list: '=' }
    };
  }
  function gfTableHeader() {
    return {
      restrict: 'A',
      template: '<th data-ng-repeat="head in header">{{head | capitalize}}</th>',
      scope: { header: '=' }
    };
  }
  function gfTable() {
    return {
      restrict: 'E',
      templateUrl: '/p/app/admin/admin-partials/admin-table.html',
      scope: {
        header: '=',
        title: '@',
        list: '=',
        team: '@',
        color: '@'
      }
    };
  }
}());
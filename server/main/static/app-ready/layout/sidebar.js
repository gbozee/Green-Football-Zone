(function () {
  'use strict';
  var controllerId = 'sidebar';
  angular.module('app').controller(controllerId, [
    '$location',
    '$route',
    'common',
    'config',
    'routes',
    'userInfo',
    sidebar
  ]);
  function sidebar($location, common, $route, config, routes, userInfo) {
    var vm = this;
    vm.isCurrent = isCurrent;
    var keyCodes = config.keyCodes;
    vm.search = search;
    vm.searchText = '';
    vm.user = userInfo.user;
    vm.isAdmin = isAdmin;
    vm.isAuthor = isAuthor;
    activate();
    function activate() {
      getNavRoutes();
    }
    function getNavRoutes() {
      vm.navRoutes = routes.filter(function (r) {
        return r.config.settings && r.config.settings.nav;
      }).sort(function (r1, r2) {
        return r1.config.settings.nav > r2.config.settings.nav;
      });
    }
    function isAdmin() {
      return userInfo.user().admin;
    }
    function isAuthor() {
      return userInfo.user().author;
    }
    function isCurrent(route) {
      if (!route.config.title || !$route.current || !$route.current.title) {
        return '';
      }
      var menuName = route.config.title;
      return $route.current.title.substr(0, menuName.length) === menuName ? 'current' : '';
    }
    function search($event) {
      if ($event.keyCode === keyCodes.esc) {
        vm.searchText = '';
        return;
      }
      if ($event.type === 'click' || $event.keyCode === keyCodes.enter) {
        var route = '/teams/search/';
        $location.path(route + vm.searchText);
      }
    }
  }
}());
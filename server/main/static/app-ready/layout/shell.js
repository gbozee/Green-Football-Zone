(function () {
  'use strict';
  var controllerId = 'shell';
  angular.module('app').controller(controllerId, [
    '$window',
    '$scope',
    '$location',
    '$rootScope',
    'common',
    'config',
    'userInfo',
    'GFAPI',
    'Conf',
    shell
  ]);
  function shell($window, $scope, $location, $rootScope, common, config, userInfo, GFAPI, Conf) {
    var vm = this;
    var logSuccess = common.logger.getLogFn(controllerId, 'success');
    var events = config.events;
    vm.busyMessage = 'Please wait ...';
    vm.isBusy = true;
    vm.hello = 'This is me';
    var keyCodes = config.keyCodes;
    vm.search = search;
    vm.searchText = '';
    vm.clientId = Conf.clientId;
    vm.spinnerOptions = {
      radius: 40,
      lines: 7,
      length: 0,
      width: 30,
      speed: 1.7,
      corners: 1,
      trail: 100,
      color: '#F58A00'
    };
    vm.data = userInfo;
    activate();
    function activate() {
      logSuccess('GF loaded!', null, true);
      common.activateController([], controllerId);
    }
    function toggleSpinner(on) {
      vm.isBusy = on;
    }
    $rootScope.$on('$routeChangeStart', function (event, next, current) {
      toggleSpinner(true);
    });
    $rootScope.$on(events.controllerActivateSuccess, function (data) {
      toggleSpinner(false);
    });
    $rootScope.$on(events.spinnerToggle, function (data) {
      toggleSpinner(data.show);
    });
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
    vm.userProfile = undefined;
    vm.hasUserProfile = false;
    vm.immediateFailed = false;
    $scope.$on('event:google-plus-signin-success', function (event, authResult) {
      vm.isSignedIn = true;
      console.log(authResult);
      userInfo.getCredentials(authResult);
    });
    $scope.$on('event:google-plus-signin-failure', function (event, authResult) {
      console.log(authResult);
    });
  }
}());
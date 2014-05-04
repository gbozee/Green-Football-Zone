(function () {
  'use strict';
  var controllerId = 'create_team';
  angular.module('app').controller(controllerId, [
    '$location',
    'common',
    'adminService',
    'gfTypeSupport',
    create_team
  ]);
  angular.module('app').controller('update_team', [
    'Restangular',
    '$routeParams',
    '$location',
    'common',
    'gfTypeSupport',
    update_team
  ]);
  function create_team($location, common, adminService, gfTypeSupport) {
    var getLogFn = common.logger.getLogFn;
    var log = getLogFn(controllerId);
    var vm = this;
    vm.title = 'Create Team';
    vm.team = {};
    vm.save = addTeam;
    vm.data = gfTypeSupport;
    activate();
    function activate() {
      var promises = [
          getLeagues(),
          getAuthors()
        ];
      common.activateController(promises, controllerId).then(function () {
        log('Activated Team Creation View');
      });
    }
    function getAuthors() {
      vm.authors = adminService.authors;
    }
    function getLeagues() {
      vm.leagues = adminService.leagues;
    }
    function addTeam() {
      console.log(vm.team);
      adminService.addTeam(vm.team).then(function (team) {
        console.log(team);
        $location.url('/admin');
      });
    }
  }
  function update_team(Restangular, $routeParams, $location, common, gfTypeSupport) {
    var teamResource = Restangular.all('teams');
    var getLogFn = common.logger.getLogFn;
    var log = getLogFn(controllerId);
    var vm = this;
    vm.title = 'Update Team';
    vm.save = updateTeam;
    vm.data = gfTypeSupport;
    activate();
    function activate() {
      var promises = [
          getTeam(),
          getLeagues(),
          getAuthors()
        ];
      common.activateController(promises, controllerId).then(function () {
        log('Activated Team Creation View');
      });
    }
    function getTeam() {
      teamResource.one($routeParams.name).get().then(function (data) {
        vm.team = data;
        console.log('GET TEAM', vm.team);
      });
    }
    function getAuthors() {
      vm.authors = Restangular.all('users').getList({ author: true }).$object;
    }
    function getLeagues() {
      vm.leagues = Restangular.all('leagues').getList().$object;
    }
    function updateTeam() {
      teamResource.one(vm.team.name).customPUT(vm.team).then(function (response) {
        console.log(response);
        $location.url('/admin');
      });
    }
  }
}());
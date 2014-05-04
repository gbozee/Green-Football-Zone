(function () {
    'use strict';
    var controllerId = 'create_league';
    angular.module('app').controller(controllerId, ['$location', 'common',
            'Restangular','gfTypeSupport', create_league])
        .controller('update_league',['$routeParams','$location',
            'common','Restangular','gfTypeSupport',update_league])


    function create_league($location, common, Restangular, gfTypeSupport) {
        var leagueResource = Restangular.all('leagues');
        var getLogFn = common.logger.getLogFn;
        var log = getLogFn(controllerId);

        var vm = this;
        vm.types = gfTypeSupport.types;
        vm.title = "Create League";
        vm.league = {};
        vm.save = addLeague;

        activate();

        function activate() {
            var promises = [];
            common.activateController(promises, controllerId)
        }

        function addLeague() {
            leagueResource.post(vm.league).then(function(result){
                console.log(result);
                $location.url('/admin');
            });
        }


    }
    function update_league($routeParams,$location,common,Restangular,gfTypeSupport){
        var leagueResource = Restangular.all('leagues');
        var getLogFn = common.logger.getLogFn;
        var log = getLogFn(controllerId);
        var vm = this;
        vm.types = gfTypeSupport.types;
        vm.title = "Update League";
        vm.league = {};
        vm.save = updateLeague;

        activate();

        function activate() {
            var promises = [getLeague()];
            common.activateController(promises, controllerId)
                .then(function () {
                    log('Admin View');
                });
        }
        function getLeague() {
//            vm.league = leagueResource.one($routeParams).get().$object;
            leagueResource.one($routeParams.name).get().
                then(function(data){
                    console.log(data);
                    vm.league = data;
                })

        }
        function updateLeague() {
            leagueResource.one($routeParams.name).customPUT(vm.league)
                .then(function(data){
//            vm.league.put().then(function(){
                log('League Updated')
                $location.url('/admin');
            });
        }
    }
})();
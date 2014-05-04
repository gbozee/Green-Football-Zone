(function () {
    'use strict';
    var controllerId = 'leagues';
    angular.module('app').controller(controllerId, ['$location','common','LeagueService','Pusher','ngProgress', Leagues]);
    angular.module('app').service('LeagueService', ['gfService','$q','$angularCacheFactory','$rootScope',LeagueService]);

    function LeagueService(gfService,$q,$angularCacheFactory,$rootScope){

        var leagueResource = gfService.leagueResource();
        var leagues = {};
        var leagueService = {};

        leagueService.getLeagues = function(){
            return leagueResource.getList().then(function(data){
                leagues.clubs = _.filter(data,{type:'club'});
                leagues.countries = _.filter(data,{type:'country'});
                return leagues;
            })
        };
        leagueService.refresh = function(){
            var myCache = $angularCacheFactory.get('gfCache');
            if(typeof myCache !== 'undefined' ){
                myCache.remove('/api/v2.0/leagues');
                $rootScope.$broadcast('refresh:teams');
            }
            return $q.when(true);
        }
        return leagueService;
    }

    function Leagues($location,common,LeagueService,Pusher,ngProgress) {
        var getLogFn = common.logger.getLogFn;
        var log = getLogFn(controllerId);
        ngProgress.height('10px');
        var vm = this;
        vm.title = 'Leagues';
        vm.refresh = refresh;
        vm.currentClubPage = 0;
        vm.currentCountryPage = 0;
        vm.itemsPerPage = 6;
        vm.club_leagues = [];
        vm.country_leagues = [];

        function paginateClubs(data){

                log(data.length + ' Club Leagues Loaded')
                vm.pagedClubItems = [];
                for (var i = 0; i < data.length; i++) {
                    if (i % vm.itemsPerPage === 0) {
                        vm.pagedClubItems[Math.floor(i / vm.itemsPerPage)] = [ data[i] ];
                    } else {
                        vm.pagedClubItems[Math.floor(i / vm.itemsPerPage)].push(data[i]);
                    }
                }
        }
        function paginateCountries(data){
            log(data.length + ' Club Leagues Loaded')
                vm.pagedCountryItems = [];
                for (var i = 0; i < data.length; i++) {
                    if (i % vm.itemsPerPage === 0) {
                        vm.pagedCountryItems[Math.floor(i / vm.itemsPerPage)] = [ data[i] ];
                    } else {
                        vm.pagedCountryItems[Math.floor(i / vm.itemsPerPage)].push(data[i]);
                    }
                }
        }

        activate();
        function getLeagues() {
//            return LeagueService.getLeagues().then(function(data){
            return LeagueService.getLeagues().then(function(data){
                console.log('Leagues',data);
                vm.club_leagues = data.clubs;
                vm.country_leagues = data.countries;
                paginateCountries(vm.country_leagues);
                paginateClubs(vm.club_leagues);
                ngProgress.complete();
            });
        }
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

        vm.prevClubPage = function () {
            console.log(vm.pagedClubItems);
            if (vm.currentClubPage > 0) {
                vm.currentClubPage--;
            }
        };

        vm.nextClubPage = function () {
            console.log(vm.pagedClubItems);
            if (vm.currentClubPage < vm.pagedClubItems.length - 1) {
                vm.currentClubPage++;
            }
        };
        Pusher.subscribe('leagues','league_created',function(message){
            log(message.league.name + ' now available');
            refresh();
        });
        vm.setClubPage = function (n) {
            vm.currentClubPage = n;
        };
        vm.previousCountryPage=function () {
            console.log(vm.pagedCountryItems);
            if (vm.currentCountryPage > 0) {
                vm.currentCountryPage--;
            }
        };
        vm.nextCountryPage = function () {
            console.log(vm.pagedCountryItems);
            if (vm.currentCountryPage < vm.pagedCountryItems.length - 1) {
                vm.currentCountryPage++;
            }
        };

        vm.setCountryPage = function (n) {
            vm.currentCountryPagePage = n;
        };

        function activate() {
            var promises = [
//                vm.leagues
                getLeagues()
            ];
            common.activateController(promises, controllerId)
                .then(function () {
                    log('Leagues Loaded');
                });
        }
        function refresh() {
            ngProgress.start();
            return LeagueService.refresh().then(function(){
                getLeagues();
            });

        }
    }

})();
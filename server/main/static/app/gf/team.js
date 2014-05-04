(function () {
    'use strict';
    var controllerId = 'teams';
    angular.module('app').controller(controllerId, ['$routeParams',
        'common', 'config','userInfo','TeamService','Pusher','$rootScope','ngProgress'
        , teams]);
    angular.module('app').service('TeamService',['gfService','$q','$angularCacheFactory','$rootScope',TeamService]);
    function TeamService(gfService,$q,$angularCacheFactory,$rootScope){
        var teamService = gfService.teamResource();
        var leagueService = gfService.leagueResource();

        var service = {};
        var teams = [];

        service.getTeams = function(){
            return teamService.getList().then(function(data){
                teams = data;
                return teams;
            })
        };

        service.getTeamFromLeagueLocal = function(league,refresh){
            if(refresh){
                this.refresh();
                return this.getTeamsFromLeague(league);
            }
            var team = _.where(teams,{league:league});
            console.log(team);
            return $q.when(team);

        };

        service.teams = function(refresh){
            if(refresh){
                this.refresh();
                return this.getTeams()}
            return $q.when(teams);
        };

        service.getLeague = function(league){
            return leagueService.one(league).get().$object;
        }
        service.getTeamsFromLeague = function (league){
           return leagueService.one(league).customGETLIST('teams')
               .then(function(data){
                   teams = data;
                   return teams;
               });
        }
        service.refresh = function(){
            var myCache = $angularCacheFactory.get('gfCache');
            myCache.remove(teams.getRequestedUrl().toString());
        }
        $rootScope.$on('refresh:teams',function(){
            service.teams(true);
        });
        return service;

    }
    function teams($routeParams, common, config,userInfo,TeamService,Pusher,$rootScope,ngProgress) {
        var getLogFn = common.logger.getLogFn;
        var log = getLogFn(controllerId);
        var logError = getLogFn(controllerId, 'error');

        var vm = this;
        vm.refresh = refresh;
        vm.league = TeamService.getLeague($routeParams.league_name);
//         vm.title = $routeParams.league_name;
         vm.currentPage = 0;
        vm.itemsPerPage = 6;
        ngProgress.height('10px');
        vm.following = isFollowing;
        vm.pagedItems = [];
        vm.teams = [];
        vm.filteredTeams = [];
        Pusher.subscribe($routeParams.league_name.replace(/\s/g,''),'team_created',function(message){
            log(message.team.name + ' now available');
            refresh();
        });
//        vm.teams = [];
        function getTeams(refresh){
//            TeamService.getTeamsFromLeague($routeParams.league_name).then(function(data){//
            TeamService.getTeamFromLeagueLocal($routeParams.league_name,refresh).then(function(data){//
               log('Teams Refreshed')
                vm.teams = data;
                vm.filteredTeams  = vm.teams;
                console.log(vm.teams);
                onPageLoaded();
                ngProgress.complete();
            });
        }

        function refresh() {
            ngProgress.start();
            getTeams(true);
        }

        function onPageLoaded(){
            vm.currentPage = 0;
            groupToPages();
        }

        function groupToPages(){

            for (var i = 0; i < vm.filteredTeams.length; i++) {
                if (i % vm.itemsPerPage === 0) {
                    vm.pagedItems[Math.floor(i / vm.itemsPerPage)] = [ vm.filteredTeams[i] ];
                } else {
                    vm.pagedItems[Math.floor(i / vm.itemsPerPage)].push(vm.filteredTeams[i]);
                }
            }
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

        var applyFilter = function () {
        };
        var keyCodes = config.keyCodes;
        vm.teamsSearch = $routeParams.search || '';
        vm.teamsFilter = teamFilter;
        vm.search = search;
        vm.followedTeams = userInfo.teams;
//        getTeamsFromLeague();
        activate();

        function activate() {
            common.activateController([getTeams(false)], controllerId)
                .then(function () {
                    applyFilter = common.createSearchThrottle(vm, 'teams');
                    if (vm.teamsSearch) {
                        applyFilter(true);
                    }

                    log('Activated Teams View');
                });
        }

        function isFollowing(teamName){
            return _.findIndex(userInfo.teams(),{name:teamName}) > -1;
        }

        vm.followTeam = function (a) {
            console.log(vm.following);

           ngProgress.start();
           return userInfo.followTeam(a).then(function(){
                ngProgress.complete();
           });
        }

        function search($event) {
            if ($event.keyCode === keyCodes.esc) {
                vm.teamsSearch = '';
                applyFilter(true);
            }
            else applyFilter();
                onPageLoaded()
        }

        function teamFilter(team) {
            var textContains = common.textContains;
            var searchText = vm.teamsSearch;
            var isMatch = searchText ?
                textContains(team.name, searchText)
               || textContains(team.type, searchText)
                    || textContains(team.league, searchText)
                    || textContains(team.c_league, searchText)
                    || textContains(team.coach,searchText)
                : true;
            return isMatch;

        }
    }
})();
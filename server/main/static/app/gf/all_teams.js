(function () {
    'use strict';
    var controllerId = 'all_teams';
    angular.module('app').controller(controllerId, ['$routeParams', 'common','TeamService', 'config',
        '$location','userInfo','ngProgress', all_teams]);

    function all_teams($routeParams, common,TeamService, config,$location,userInfo,ngProgress) {
//        var teamResource = gfService.teamResource();
        var getLogFn = common.logger.getLogFn;
        var log = getLogFn(controllerId);
        var logError = getLogFn(controllerId, 'error');
        var vm = this;
        ngProgress.height('10px');
        vm.title = 'All Teams';
        vm.teams = [];
        vm.filteredTeams= [];
        vm.refresh = refresh;
        var applyFilter = function () { };
        var keyCodes = config.keyCodes;
        vm.teamsSearch = $routeParams.search || '';
        vm.teamsFilter = teamFilter;
        vm.search = search;
         vm.currentPage = 0;
        vm.itemsPerPage = 6;
        vm.following = isFollowing;
        vm.navigateToTopics = navigateToTopics;
        vm.followTeam = followTeam;
        activate();

        function followTeam(){
            ngProgress.start();
            return userInfo.followTeam().then(function(){
                ngProgress.complete();
            })
        }
        function activate() {
            common.activateController([getAllTeams()], controllerId)
                .then(function () {
                    applyFilter = common.createSearchThrottle(vm, 'teams');
                    if (vm.teamsSearch) {
                        applyFilter(true);
                        onPageLoaded();
                    }
                    log('Activated All-Teams View');
                });
        }

        function getAllTeams(forceRefresh) {
            return TeamService.teams(forceRefresh)
                .then(function (data) {
                    log('All Teams '+data.length);
                    vm.teams = vm.filteredTeams = data;
                    applyFilter();
                    onPageLoaded();
                    ngProgress.complete();
                })
        }

        function refresh() {
            ngProgress.start();
            getAllTeams(true);

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


        function navigateToTopics(team_name){
            if (isFollowing(team_name)){
                $location.url('/teams/'+team_name);
            }else{
                logError('You are not Following '+ team_name);
            }
        }
        function onPageLoaded(){
            vm.currentPage = 0;
            groupToPages();
        }


        function groupToPages(){
            vm.pagedItems = [];
            for (var i = 0; i < vm.filteredTeams.length; i++) {
                if (i % vm.itemsPerPage === 0) {
                    vm.pagedItems[Math.floor(i / vm.itemsPerPage)] = [ vm.filteredTeams[i] ];
                } else {
                    vm.pagedItems[Math.floor(i / vm.itemsPerPage)].push(vm.filteredTeams[i]);
                }
            }
        }
        function isFollowing(teamName){
            return _.findIndex(userInfo.teams(),{name:teamName}) > -1;
        }
        //Todo: filter and sort teams
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
            if (vm.currentPage > 0) {
                vm.currentPage--;
            }
        };
        vm.nextPage = function () {
            if (vm.currentPage < vm.pagedItems.length - 1) {
                vm.currentPage++;
            }
        };

        vm.setPage = function (n) {
            vm.currentPage = n;
        };
    }
})();
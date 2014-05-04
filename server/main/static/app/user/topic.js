(function () {
    'use strict';
    var controllerId = 'topics';
    angular.module('app').controller(controllerId, ['common', 'config', '$filter',
        'inhouse','userInfo','Pusher','ngProgress', topics]);

    function topics(common, config, $filter, inhouse,userInfo,Pusher,ngProgress) {
        var getLogFn = common.logger.getLogFn;
        ngProgress.height('10px');
        var log = getLogFn(controllerId);

        var vm = this;
        vm.title = 'User Topics';

        vm.topics = [];
        vm.filteredTopics = [];

         vm.currentPage = 0;
         vm.itemsPerPage = 5;
        vm.refresh = refresh;
        var keyCodes = config.keyCodes;
        vm.topicsSearch = '';
        vm.topicsFilter = topicsFilter;
        vm.search = search;
        vm.date = setDate;
        var applyFilter = function () {
        };

        activate();

        function activate() {
            common.activateController([getUserTopics(true)], controllerId)
                .then(function () {
                    applyFilter = common.createSearchThrottle(vm, 'topics');
                    if (vm.topicsSearch) {
                        applyFilter(true);
                    }
                    log('Activated Admin View');
                });
        }
        Pusher.subscribe('followed_teams','topic_added',function(){
            ngProgress.reset();
            refresh();
        });
        function getUserTopics(forceRefresh) {
            userInfo.refreshFollowedTopics(forceRefresh).then(function(data){
                vm.topics = data;
                vm.topics = $filter('orderBy')(vm.topics,'-created');
                vm.filteredTopics = vm.topics;
                onPageLoaded();
                ngProgress.complete();
            });

//            return datacontext.getUserTeamTopics(forceRefresh)
//                .then(function (data) {
////                    return vm.sessions = vm.filteredSessions = data;
//                    return vm.topics = vm.filteredTopics = data;
//                });
        }


        function refresh() {
//            userInfo.refreshFollowedTopics().
//                then(function(data){
//                  vm.topics = data.followedTopics;
//                  vm.filteredTopics = vm.topics;
//            })
            ngProgress.start();
            getUserTopics(true);
        }

        function search($event) {
            if ($event.keyCode === keyCodes.esc) {
                vm.replySearch = '';
                applyFilter(true)
            }
            else applyFilter();
             onPageLoaded();
        }

        function topicsFilter(topic) {
            var textContains = common.textContains;
            var searchText = vm.topicsSearch;
            var isMatch = searchText ?
                textContains(topic.body, searchText)
                    || textContains(topic.author, searchText)
                    || textContains(topic.team, searchText)
                    || textContains(topic.title, searchText)
                : true;
            return isMatch;

        }
        function setDate(date) {
            return moment.utc(date).format('ddd hh:mm a');
        }

        function groupToPages(){
            vm.pagedItems = [];
            for (var i = 0; i < vm.filteredTopics.length; i++) {
                if (i % vm.itemsPerPage === 0) {
                    vm.pagedItems[Math.floor(i / vm.itemsPerPage)] = [ vm.filteredTopics[i] ];
                } else {
                    vm.pagedItems[Math.floor(i / vm.itemsPerPage)].push(vm.filteredTopics[i]);
                }
            }
        }

        function onPageLoaded(){
            vm.currentPage = 0;
            groupToPages();
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
})();
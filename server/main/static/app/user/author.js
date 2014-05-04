(function () {
    'use strict';
    var controllerId = 'author';
    angular.module('app').controller(controllerId, ['bootstrap.dialog','config', '$filter', '$routeParams', '$location',
        'userInfo', 'common', 'inhouse','ngProgress', author]);
    angular.module('app').controller('userDetails', ['common', 'gfService', 'userInfo', userDetails]);
    angular.module('app').filter('characters', [charactersFilter]);
    angular.module('app').filter('words', [wordsFilter]);


    function charactersFilter() {
        return function (input, chars, breakOnWord) {
            if (isNaN(chars)) return input;
            if (chars <= 0) return '';
            if (input && input.length >= chars) {
                input = input.substring(0, chars);

                if (!breakOnWord) {
                    var lastspace = input.lastIndexOf(' ');
                    //get last space
                    if (lastspace !== -1) {
                        input = input.substr(0, lastspace);
                    }
                } else {
                    while (input.charAt(input.length - 1) == ' ') {
                        input = input.substr(0, input.length - 1);
                    }
                }
                return input + '...';
            }
            return input;
        };
    }

    function wordsFilter() {
        return function (input, words) {
            if (isNaN(words)) return input;
            if (words <= 0) return '';
            if (input) {
                var inputWords = input.split(/\s+/);
                if (inputWords.length > words) {
                    input = inputWords.slice(0, words).join(' ') + '...';
                }
            }
            return input;
        };
    }


    function userDetails(common, gfService) {
        var myResource = gfService.myResource();
        var getLogFn = common.logger.getLogFn;
        var log = getLogFn('userReplies');
        var logError = getLogFn('userReplies', 'error');

        var uc = this;
        uc.user = {};

        function getUserDetails() {
            return myResource.customGET('profile').then(function (data) {
                uc.user = data;
                log('Welcome ' + uc.user.username);
            })
        }

        getUserDetails();
        activate();

        function activate() {
            common.activateController([getUserDetails()], 'userDetails')
                .then(function () {
                    log('Activated Authors View');
                });
        }

//
    }

    function author(bsDialog,config, $filter, $routeParams, $location, userInfo, common, inhouse,ngProgress) {
        var getLogFn = common.logger.getLogFn;
        var log = getLogFn(controllerId);
        var keyCodes = config.keyCodes;
        var vm = this;
        ngProgress.height("10px");
        vm.addtitle = "";
        vm.canCreate = $routeParams.create || false;
        vm.updatable = false;
        vm.topics = [];
        vm.topic = {};
        vm.refresh = refresh;
        vm.addTopic = addTopic;
        vm.reset = resetTopic;
        vm.updateTopic = updateTopic;
        vm.deleteTopic = deleteTopic;
        vm.doneCreating = doneCreating;
        vm.query = {};
        vm.signedIn = userInfo.isSignedIn;

        vm.search = search;
        vm.teams = [];
        vm.activateCreate = activateCreate;
        vm.close = closingUpdate;
        vm.currentPage = 0;
        vm.itemsPerPage = 5;
        vm.editTopic = editTopic;
        vm.topicsSearch = $routeParams.search || '';
        vm.topicsFilter = topicsFilter;

        vm.followedTeams = userInfo.teams;
        vm.filteredTopics = [];
        var applyFilter = function () {
        };

        function editTopic() {
            ngProgress.complete();
            ngProgress.start();
            return userInfo.updateTopic(vm.topic).then(function () {
                ngProgress.complete();
                vm.updatable = false;
                getAuthoredTopics(true);
                vm.topic = {};
            })
        }

        activate();

        function activate() {
            common.activateController([getAuthoredTopics(true)], controllerId)
                .then(function () {
                    applyFilter = common.createSearchThrottle(vm, 'topics');

                    log('Activated Authors View');
                });
        }

        function updateTopic(topic) {
            vm.updatable = true;
            vm.canCreate = false;
            vm.topic = topic;
        }

        function getAuthoredTopics(forceRefresh) {
            return userInfo.getAuthoredTopics(forceRefresh).then(function (data) {
                console.log(data);
                vm.topics = data;
                vm.topics = $filter('orderBy')(vm.topics, '-created');
                vm.filteredTopics = vm.topics;
                onPageLoaded();
                ngProgress.complete();
                log('Authored Topics Recieved')
            });
        }

//        var teamResource = gfService.teamResource();

        function groupToPages() {
            vm.pagedItems = [];
            for (var i = 0; i < vm.filteredTopics.length; i++) {
                if (i % vm.itemsPerPage === 0) {
                    vm.pagedItems[Math.floor(i / vm.itemsPerPage)] = [ vm.filteredTopics[i] ];
                } else {
                    vm.pagedItems[Math.floor(i / vm.itemsPerPage)].push(vm.filteredTopics[i]);
                }
            }
        }

        function onPageLoaded() {
            vm.currentPage = 0;
            groupToPages();
        }

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
        vm.setPage = function (n) {
            vm.currentPage = n;
        };

        function closingUpdate() {
            vm.canUpdate = false;
        }

        function refresh() {
            ngProgress.start();
            return userInfo.refreshAuthoredTopics().then(function (data) {
                getAuthoredTopics();
            })
        }

        function activateCreate() {
            vm.canCreate = true;
            vm.updatable = false;
        }

        function resetTopic(){
            vm.topic = {};
            return;
        }
        function addTopic($event) {
            if ($event.keyCode === keyCodes.esc) {
                return resetTopic();
            }
            if ($event.type === 'click' || $event.keyCode === keyCodes.enter) {
                ngProgress.complete();
                ngProgress.start();
                return userInfo.addTopic(vm.topic)
                    .then(function (topic) {
                        log('Topic Added');
                        getAuthoredTopics();
                        vm.topic = {};
                        doneCreating();

                    });
            }

        }

        function doneCreating() {
            vm.canCreate = false;
        }

        vm.doneUpdating = function () {
            vm.updatable = false;
        }

        function deleteTopic(topic) {
//            return bsDialog.deleteDialog('Topic').then(confirmDelete);
//            function confirmDelete(topic) {
                ngProgress.start();
                return userInfo.deleteTopic(topic)
                    .then(function () {
                        ngProgress.complete();
                        log('Topic Deleted');
                        getAuthoredTopics();
                    });
//            }
        }

        function search($event) {
            if ($event.keyCode === keyCodes.esc) {
                vm.topicsSearch = '';
                applyFilter(true);
            }
            else applyFilter();
            onPageLoaded()
        }

        function topicsFilter(topic) {
            var textContains = common.textContains;
            var searchText = vm.topicsSearch;
            var isMatch = searchText ?
                textContains(topic.title, searchText)
                    || textContains(topic.body, searchText)
                    || textContains(topic.team, searchText)
                    || textContains(topic.second_team, searchText)
                : true;
            return isMatch;

        }
    }
})();
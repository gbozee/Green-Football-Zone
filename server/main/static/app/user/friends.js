//Todo: get all friends from google plus along with their teams
// and only show replies if they are following the same team as you
(function () {
    'use strict';
    var controllerId = 'friends';
    angular.module('app').controller(controllerId, [
        'userInfo', 'common', friends]);

    function friends(userInfo, common) {
        var getLogFn = common.logger.getLogFn;
        var log = getLogFn(controllerId);

        var vm = this;

        vm.title = 'Friends on Google+ Using Green Football';

        vm.friends = [];
        vm.refresh = refresh;
        activate();

        function activate() {
            common.activateController([getFriends()], controllerId)
                .then(function () {
                    log('Activated Friends View');
                });
        }

        function getFriends(forceRefresh) {
            vm.friends = userInfo.getFriends;
        }

        function refresh() {
            getFriends(true);
        }


        vm.currentPage = 0;
        vm.itemsPerPage = 6;
        vm.pagedItems = userInfo.pagedFriends;

        vm.prevPage = function () {
            if (vm.currentPage > 0) {
                vm.currentPage--;
            }
        };
        vm.nextPage = function () {
            if (vm.currentPage < vm.pagedItems().length - 1) {
                vm.currentPage++;
            }
        };

        vm.setPage = function (n) {
            vm.currentPage = n;
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
    }
})();
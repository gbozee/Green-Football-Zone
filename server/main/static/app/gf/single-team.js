(function () {
    'use strict';
    var controllerId = 'team';
    angular.module('app').controller(controllerId, ['$filter','$routeParams', 'common', 'TopicService','Conf',
        'userInfo','Pusher','$rootScope','ngProgress', team]);
    angular.module('app').controller('gfFollowController', ['common','$http', '$scope','userInfo','ngProgress', gfFollowCtrl]);
    angular.module('app').service('TopicService', ['gfService','$angularCacheFactory','$rootScope', TopicService]);

    function TopicService(gfService,$angularCacheFactory,$rootScope){
        var teamService = gfService.teamResource();

        var service = {};
        var topics = [];

        service.getTeam = function(name){
            return teamService.one(name).get().$object;
        };
        service.getTopicsForTeam = function (team){
           return teamService.one(team).customGETLIST('topics')
               .then(function(data){
                   topics = data;
                   return topics;
               });
        }
        service.refresh = function(){
            var myCache = $angularCacheFactory.get('gfCache');
            myCache.remove(topics.getRequestedUrl().toString());
            $rootScope.$broadcast('followed:topics');
        }
        return service;

    }
    function gfFollowCtrl(common,$http, $scope,userInfo,ngProgress) {
        var getLogFn = common.logger.getLogFn;
        var log = getLogFn('gfFollowCtrl');
        ngProgress.height('10px');
        var logError = getLogFn('gfFollowCtrl', 'error');

            $scope.following =  _.findIndex(userInfo.user.teams,{name:$scope.teamToFollow.name}) > -1;
//        };

        $scope.followTeam = function () {
            console.log($scope.following);
            ngProgress.start();
           userInfo.followTeam($scope.teamToFollow) .then(function(){
               ngProgress.complete();
                });
        };

    }

    function team($filter,$routeParams, common, TopicService,Conf, userInfo,Pusher,$rootScope,ngProgress) {

        var getLogFn = common.logger.getLogFn;
        var log = getLogFn(controllerId);
        var logError = getLogFn(controllerId, 'error');
        ngProgress.height('10px');
        var vm = this;
        vm.title = 'Team';
        vm.clientId = Conf.clientId;
        vm.team ={};
        vm.unfollowTeam = userInfo.unfollowTeam;
//        vm.team = {};
        vm.topics = [];
        vm.button = {};
        vm.followButton = followButton;
        vm.followHover = followHover;
        vm.unFollowHover = unfollowHover;
        vm.followedTeams = [];
        vm.number = 20;
        vm.following = isFollowing;
        vm.followTeam = followTeam;
        vm.refresh = refresh;
        vm.voteNotify = voteNotify;
        vm.signedIn = userInfo.isSignedIn;
        function isFollowing(){
            return _.findIndex(userInfo.teams(),{name:vm.team.name}) > -1;
        }
        function voteNotify(){
            return logError('You can only vote in the topic Page Sorry!!');
        }

        function followTeam(team){
            ngProgress.start();
            return userInfo.followTeam(team).then(function(){
                ngProgress.complete();
            });
        }
        function refresh(){
            ngProgress.start();
            TopicService.refresh();
            return userInfo.refreshFollowedTopics().then(function(){
                getTeamTopics();
            });
        }

        activate();

        function activate() {
            common.activateController([getTeam(),getTeamTopics()], controllerId)
                .then(function () {

                });
        };
        function topic_notification(teamName,data,action){
            var message = {
                link:'teams/'+teamName,
                body:data.topic.title + '    '+ action+' for '+teamName
            }
            $rootScope.$broadcast('notification',message);
        }
        Pusher.subscribe($routeParams.team_name.replace(/\s/g,''),'topic_added',function(data){
            topic_notification(data.team_name,data, 'created');
            log('New Topic for '+data.team_name);
            ngProgress.reset();
            refresh();
        });
        Pusher.subscribe($routeParams.team_name.replace(/\s/g,''),'topic_updated',function(data){
            topic_notification(data.team_name,data,'updated');
            log(data.topic.title +' Updated');
            ngProgress.reset();
            refresh();
        });
        Pusher.subscribe($routeParams.team_name.replace(/\s/g,''),'topic_deleted',function(data){
            log(data.topic.title +' Deleted');
            ngProgress.reset();
            refresh();
        });
        function getTeamTopics(){
//            vm.topics = userInfo;
            TopicService.getTopicsForTeam($routeParams.team_name).then(function(data){
                vm.topics = data;
                vm.topics = $filter('orderBy')(vm.topics,'-created');
                onPageLoaded();
                ngProgress.complete();
                log('Topics Recieved');
            });
        };
        function getTeam() {
            vm.team = TopicService.getTeam($routeParams.team_name)
        }

//        function getButtonClass() {
//            return teamResource.getButtonClass($routeParams.team_name)
//                .then(function (data) {
//                    vm.button = data;
//                })
//        }
        function followButton() {
            button.count = team.followers_count;
            button.button_class = "following";
            button.text = "Following";

            button.button_class = "";
            button.count = 0;
            button.text = "Follow";
            var button = angular.element('input.followButton');
            if (button.hasClass('following')) {
                return teamResource.unfollowTeam(vm.team)
                    .then(function (result) {
                        vm.button = result;
                        vm.button.button_class = '';
                        button.removeClass('following');
                        button.removeClass('unfollow');
                        vm.button.text = 'Follow';
//                    button.text('Follow');
                    });
            } else {
                return teamResource.followTeam(vm.team)
                    .then(function (result) {
                        vm.button = result;
                        vm.button.button_class = '';
                        button.addClass('following');
                        vm.button.text = 'Following';
//                        button.text('Following');
                    })
            }
        }

        function followHover() {
            var button = angular.element('input.followButton');
            if (button.hasClass('following')) {
                button.addClass('unfollow');
                button.text('Unfollow');
            }
//        };
        }

        function unfollowHover() {
            var button = angular.element('input.followButton');
            if (button.hasClass('following')) {
                button.removeClass('unfollow');
                button.text('Following');
            }
        }

        //Paging of the page
         vm.currentPage = 0;
        vm.itemsPerPage = 5;
        function groupToPages(){
            vm.pagedItems = [];
            for (var i = 0; i < vm.topics.length; i++) {
                if (i % vm.itemsPerPage === 0) {
                    vm.pagedItems[Math.floor(i / vm.itemsPerPage)] = [ vm.topics[i] ];
                } else {
                    vm.pagedItems[Math.floor(i / vm.itemsPerPage)].push(vm.topics[i]);
                }
            }
        }
        function onPageLoaded(){
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

    }
})();
(function () {
  'use strict';
  var controllerId = 'topic';
  angular.module('app').controller(controllerId, [
    '$filter',
    '$routeParams',
    'common',
    'config',
    'ReplyService',
    'userInfo',
    'Conf',
    'Pusher',
    'ngProgress',
    topic
  ]);
  angular.module('app').service('ReplyService', [
    'gfService',
    '$angularCacheFactory',
    '$rootScope',
    ReplyService
  ]);
  function ReplyService(gfService, $angularCacheFactory, $rootScope) {
    var topicService = gfService.topicResource();
    var service = {};
    var replies = [];
    var teamName;
    var topicId;
    service.getTopicId = function () {
      return topicId;
    };
    service.getTopic = function (name) {
      return topicService.one(name).get();
    };
    service.setTeam = function (team, topic_id) {
      topicId = topic_id;
      teamName = team;
      console.log('REPLY_TEAM ', teamName);
    };
    service.getTeam = function () {
      console.log(teamName);
      return teamName;
    };
    service.getRepliesForTopic = function (team) {
      return topicService.one(team).all('replies').getList().then(function (data) {
        replies = data;
        return replies;
      });
    };
    service.reply_notification = function (link, data) {
      var message = {
          link: '/topic/' + link,
          body: 'Reply from ' + data.reply.by
        };
      $rootScope.$broadcast('notification', message);
    };
    service.refresh = function () {
      var myCache = $angularCacheFactory.get('gfCache');
      myCache.remove(replies.getRequestedUrl().toString());
    };
    $rootScope.$on('refresh:replies', function () {
      this.refresh();
    });
    return service;
  }
  function topic($filter, $routeParams, common, config, ReplyService, userInfo, Conf, Pusher, ngProgress) {
    var getLogFn = common.logger.getLogFn;
    var log = getLogFn(controllerId);
    ngProgress.height('10px');
    var vm = this;
    var keyCodes = config.keyCodes;
    vm.clientId = Conf.clientId;
    vm.title = 'Single Topic View';
    vm.topic = {};
    vm.addReply = addReply;
    vm.newReply = {};
    vm.voteCount = 0;
    vm.upVote = upVoteTopic;
    vm.downVote = downVoteTopic;
    vm.refresh = refresh;
    vm.sortorder = '-created';
    vm.replies = [];
    vm.signedIn = userInfo.isSignedIn;
    activate();
    console.log('GGGGG', ReplyService.getTeam());
    function activate() {
      common.activateController([
        getTopic(),
        getReplies()
      ], controllerId).then(function () {
        log('Activated Topic View');
      });
    }
    Pusher.subscribe(ReplyService.getTeam(), 'reply_added', function (data) {
      log('Incoming Reply');
      ReplyService.reply_notification(data.topic_id, data);
      console.log(data);
      ngProgress.reset();
      refresh(vm.currentPage);
    });
    Pusher.subscribe(ReplyService.getTeam(), 'reply_updated', function (data) {
      log('Updated Reply from ', data.reply.by);
      ReplyService.reply_notification(data.topic_id, data);
      ngProgress.reset();
      refresh(vm.currentPage);
    });
    function getTopic() {
      return ReplyService.getTopic($routeParams.topic_id).then(function (data) {
        console.log(data);
        vm.topic = data;
        vm.voteCount = vm.topic.votes;
        log(vm.topic.title + ' Loaded');
      });
    }
    function getReplies(pageNo) {
      return ReplyService.getRepliesForTopic($routeParams.topic_id).then(function (data) {
        vm.replies = data;
        vm.replies = $filter('orderBy')(vm.replies, 'created');
        if (pageNo) {
          onPageLoaded(pageNo);
        } else {
          onPageLoaded();
        }
        ngProgress.complete();
      });
    }
    function addReply($event) {
      if ($event.keyCode === keyCodes.esc) {
        vm.newReply = {};
        return;
      }
      if ($event.type === 'click' || $event.keyCode === keyCodes.enter) {
        vm.newReply.created = Date.now();
        ngProgress.complete();
        ngProgress.start();
        return userInfo.addReply(vm.topic, vm.newReply).then(function (reply) {
          reply.user_url = userInfo.user().avatar_url;
          vm.replies.push(reply);
          log('Reply added');
          vm.newReply = {};
          onPageLoaded(vm.currentPage);
          ngProgress.complete();
        });
      }
    }
    function upVoteTopic() {
      ngProgress.complete();
      ngProgress.start();
      return vm.topic.customGET('vote').then(function (data) {
        userInfo.insertTopicIfFollowing(data);
        vm.voteCount = data.votes;
        log('Voted');
        ngProgress.complete();
      });
    }
    function downVoteTopic() {
      ngProgress.complete();
      ngProgress.start();
      return vm.topic.customDELETE('vote').then(function (data) {
        userInfo.insertTopicIfFollowing(data);
        vm.voteCount = data.votes;
        log('down voted');
        ngProgress.complete();
      });
    }
    function refresh(pageNo) {
      ngProgress.complete();
      ngProgress.start();
      ReplyService.refresh();
      getReplies(pageNo);
    }
    vm.currentPage = 0;
    vm.itemsPerPage = 5;
    function groupToPages() {
      vm.pagedItems = [];
      for (var i = 0; i < vm.replies.length; i++) {
        if (i % vm.itemsPerPage === 0) {
          vm.pagedItems[Math.floor(i / vm.itemsPerPage)] = [vm.replies[i]];
        } else {
          vm.pagedItems[Math.floor(i / vm.itemsPerPage)].push(vm.replies[i]);
        }
      }
      vm.currentPage = vm.pagedItems.length - 1;
    }
    function onPageLoaded(no) {
      groupToPages();
      if (no) {
        vm.currentPage = no;
      }
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
}());
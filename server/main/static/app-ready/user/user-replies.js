(function () {
  'use strict';
  var controllerId = 'user_replies';
  angular.module('app').controller(controllerId, [
    '$filter',
    '$routeParams',
    'common',
    'config',
    'userInfo',
    user_replies
  ]);
  angular.module('app').factory('userInfo', [
    '$rootScope',
    'common',
    '$filter',
    'Restangular',
    '$q',
    'ngProgress',
    userInfo
  ]);
  function userInfo($rootScope, common, $filter, Restangular, $q, ngProgress) {
    var getLogFn = common.logger.getLogFn;
    var log = getLogFn('userInfo');
    var logError = getLogFn('userInfo', 'error');
    var myResource = Restangular.all('me');
    var teamResource = Restangular.all('teams');
    var topicResource = Restangular.all('topics');
    var replyResource = Restangular.all('replies');
    var userResource = Restangular.all('users');
    var myTeamResource = Restangular.all('my-teams');
    var loaded = false;
    var replyLoaded = false;
    var authoredLoaded = false;
    var authored_topics = [];
    var replies = [];
    var teams = [];
    var myfriends = [];
    var followed_topics = [];
    var authResult = {};
    var user = {};
    var g_plusProfile = {};
    var itemsPerPage = 6;
    var userService = {};
    var isSignedIn = false;
    var credentials = {};
    userService.getCredentials = function (authResult) {
      isSignedIn = true;
      console.log(authResult);
      credentials = authResult;
      user.access_token = authResult.access_token;
      gapi.client.load('plus', 'v1', loadProfile);
    };
    function getProfileInformation() {
      var request = gapi.client.plus.people.get({ 'userId': 'me' });
      request.execute(loadProfileCallback);
    }
    function insertMoments(topic, reply) {
      var moment = {
          'type': 'http://schemas.google.com/ReviewActivity',
          'target': { 'url': 'https://developers.google.com/+/web/snippet/examples/movie' },
          'result': {
            'type': 'http://schema.org/Movie',
            'name': 'Night of the Living Dead',
            'url': 'https://developers.google.com/+/web/snippet/examples/movie',
            'text': 'It is amazingly effective at whatever it is that it is supposed to do.',
            'reviewRating': {
              'type': 'http://schema.org/Rating',
              'ratingValue': '100',
              'bestRating': '100',
              'worstRating': '0'
            }
          }
        };
      var request = gapi.client.request({
          'path': 'plus/v1/people/me/moments/vault',
          'method': 'POST',
          'body': JSON.stringify(moment)
        });
      request.execute(function (result) {
        console.log(result);
      });
    }
    function loadProfile() {
      getProfileInformation();
    }
    function loadProfileCallback(obj) {
      if (obj.displayName !== null || obj.displayName !== undefined) {
        user.google_display_name = obj.displayName;
      }
      if (obj.image.url !== null || obj.image.url !== undefined) {
        user.gplus_image_url = obj.image.url;
      }
      if (obj.url !== null || obj.url !== undefined) {
        user.gplus_profile = obj.url;
      }
      console.log(obj);
      var params = {
          access_token: user.access_token,
          google_plus_id: obj.id,
          google_image_url: obj.image.url,
          google_display_name: obj.displayName
        };
      myResource.customPUT(params, 'profile').then(function (data) {
        console.log(data);
        log('Details upgraded from G+');
        return myResource.customGETLIST('friends').then(function (friends) {
          console.log(friends);
          log('Friends in G+ on GF recieved ', friends.length);
          myfriends = friends;
        }, function (error) {
          console.log(error);
        });
      }, function (error) {
        console.log(error);
      });
    }
    userService.isSignedIn = function () {
      return isSignedIn;
    };
    userService.fetchUserDetails = function () {
      var deferred = $q.defer();
      myResource.customGET('profile').then(function (data) {
        user = data;
        deferred.resolve(user);
        return data;
      }, function (error) {
        console.log(error);
        logError('Connection Timed out when recieving friends');
      });
      return deferred.promise;
    };
    userService.getFriends = function () {
      return myfriends;
    };
    userService.getUserTeams = function () {
      return myTeamResource.getList().then(function (data) {
        user.teams = data;
        teams = data;
        console.log(data);
        loaded = true;
        return data;
      });
    };
    userService.fetchUserReplies = function () {
      return myResource.customGETLIST('comments').then(function (data) {
        replies = data;
        replyLoaded = true;
        return replies;
      });
    };
    userService.fetchFollowedTeamTopics = function () {
      return myResource.customGETLIST('topics').then(function (data) {
        followed_topics = data;
        console.log('Followed Topcis ', followed_topics);
        return data;
      });
    };
    userService.insertTopicIfFollowing = function (topic) {
      var index = _.findIndex(followed_topics, { id: topic.id });
      console.log(index);
      if (index > -1) {
        followed_topics[index] = topic;
      }
    };
    userService.replies = function () {
      return replies;
    };
    userService.teams = function () {
      return teams;
    };
    userService.followTeam = function (team) {
      var deferred = $q.defer();
      teamResource.one(team.name).customGET('follow').then(function (data) {
        console.log(data);
        teams.push(team);
        log('Followed Team ', team.name);
        return teams;
      }).then(function () {
        myResource.customGETLIST('topics').then(function (data) {
          followed_topics = data;
          log('Refreshed Followed Topics');
          deferred.resolve(user);
        });
      });
      return deferred.promise;
    };
    userService.followed_topics = function (refresh) {
      return followed_topics;
    };
    function AuthoredTopics() {
      return $q.when(authored_topics);
    }
    ;
    userService.getAuthoredTopics = AuthoredTopics;
    userService.refreshAuthoredTopics = function () {
      return myResource.customGETLIST('topics', { author: true }).then(function (data) {
        authored_topics = data;
        authoredLoaded = true;
        return data;
      });
    };
    userService.pagedTeams = function () {
      var pagedItems = [];
      for (var i = 0; i < teams.length; i++) {
        if (i % itemsPerPage === 0) {
          pagedItems[Math.floor(i / itemsPerPage)] = [teams[i]];
        } else {
          pagedItems[Math.floor(i / itemsPerPage)].push(teams[i]);
        }
      }
      return pagedItems;
    };
    userService.pagedFriends = function () {
      var pagedItems = [];
      for (var i = 0; i < myfriends.length; i++) {
        if (i % itemsPerPage === 0) {
          pagedItems[Math.floor(i / itemsPerPage)] = [myfriends[i]];
        } else {
          pagedItems[Math.floor(i / itemsPerPage)].push(myfriends[i]);
        }
      }
      console.log('Paged Friends ', pagedItems);
      return pagedItems;
    };
    function pageTopics() {
      var pagedItems = [];
      var topics = $filter('orderBy')(user.authored_topics, '-created');
      for (var i = 0; i < topics.length; i++) {
        if (i % itemsPerPage === 0) {
          pagedItems[Math.floor(i / itemsPerPage)] = [topics[i]];
        } else {
          pagedItems[Math.floor(i / itemsPerPage)].push(topics[i]);
        }
      }
      return pagedItems;
    }
    userService.deleteTopic = function (topic) {
      var deferred = $q.defer();
      topicResource.one(topic.id).remove().then(function (data) {
        var index = _.findIndex(authored_topics, { id: topic.id });
        authored_topics.splice(index, 1);
        log('Topic Deleted');
        deferred.resolve(authored_topics);
      });
      return deferred.promise;
    };
    userService.addTopic = function (v_topic) {
      var deferred = $q.defer();
      topicResource.post(v_topic).then(function (topic) {
        authored_topics.push(topic);
        log('Topic Added');
        deferred.resolve(authored_topics);
      });
      return deferred.promise;
    };
    userService.refreshFollowedTopics = function (refresh) {
      if (refresh) {
        var deferred = $q.defer();
        myResource.customGETLIST('topics').then(function (data) {
          followed_topics = data;
          deferred.resolve(followed_topics);
          log('Topics Refreshed ', followed_topics.length);
        });
        return deferred.promise;
      } else {
        return $q.when(followed_topics);
      }
    };
    userService.unfollowTeam = function (team) {
      var deferred = $q.defer();
      myTeamResource.one(team.name).remove().then(function (data) {
        var index = _.findIndex(teams, { id: team.id });
        teams.splice(index, 1);
        log('UnFollowed ', team.name);
        return user;
      }).then(function () {
        myResource.customGETLIST('topics').then(function (data) {
          followed_topics = data;
          log('Topics Refreshed ', followed_topics.length);
          deferred.resolve(user);
        });
      });
      return deferred.promise;
    };
    userService.addReply = function (topic, reply) {
      var deferred = $q.defer();
      topicResource.one(topic.id).post('replies', reply).then(function (reply) {
        replies.push(reply);
        deferred.resolve(reply);
      });
      return deferred.promise;
    };
    userService.deleteReply = function (reply) {
      var deferred = $q.defer();
      replyResource.one(reply.key).remove().then(function () {
        var index = _.findIndex(replies, { id: reply.id });
        replies.splice(index, 1);
        deferred.resolve();
      });
      return deferred.promise;
    };
    userService.updateReply = function (reply) {
      var deferred = $q.defer();
      replyResource.one(reply.key).customPUT(reply).then(function () {
        var index = _.findIndex(replies, { id: reply.id });
        replies[index] = reply;
        log('Reply Updated');
        deferred.resolve(reply);
      });
      return deferred.promise;
    };
    userService.filterTopicByTeam = function (team) {
      return _.filter(followed_topics, function (topic) {
        return topic.team === team.name || topic.second_team === team.name;
      });
    };
    userService.user = function () {
      user.countries = _.filter(teams, { type: 'country' });
      user.clubs = _.filter(teams, { type: 'club' });
      user.followed_topics = followed_topics;
      user.teams = teams;
      user.authored_topics = authored_topics;
      user.replies = replies;
      return user;
    };
    userService.getTopic = function (params) {
      return topicResource.one(params).get();
    };
    userService.updateTopic = function (topic) {
      var deferred = $q.defer();
      topicResource.one(topic.id).customPUT(topic).then(function (data) {
        var index = _.findIndex(authored_topics, { id: topic.id });
        authored_topics[index] = data;
        console.log('Success updated Topic', data);
        deferred.resolve(data);
      });
      return deferred.promise;
    };
    $rootScope.$on('followed:topics', function () {
      userService.refreshFollowedTopics(true);
    });
    return userService;
  }
  function user_replies($filter, $routeParams, common, config, userInfo) {
    var getLogFn = common.logger.getLogFn;
    var log = getLogFn(controllerId);
    var applyFilter = function () {
    };
    var vm = this;
    vm.title = 'All User Comments';
    vm.replies = [];
    var keyCodes = config.keyCodes;
    vm.replySearch = '';
    vm.repliesFilter = replyFilter;
    vm.search = search;
    vm.filteredReplies = [];
    vm.date = setDate;
    vm.refresh = refresh;
    vm.updatable = false;
    vm.open = open;
    vm.deleteReply = deleteReply;
    vm.editReply = editReply;
    vm.reply = {};
    vm.itemsPerPage = 6;
    vm.currentPage = 0;
    vm.refresh = activate();
    function activate() {
      common.activateController([getAllReplies(true)], controllerId).then(function () {
        applyFilter = common.createSearchThrottle(vm, 'replies');
        if (vm.replySearch) {
          applyFilter(true);
        }
        log('Activated User Replies View');
      });
    }
    function getAllReplies(refresh) {
      vm.replies = userInfo.replies();
      vm.replies = $filter('orderBy')(vm.replies, '-created');
      vm.filteredReplies = vm.replies;
      onPageLoaded();
    }
    function search($event) {
      if ($event.keyCode === keyCodes.esc) {
        vm.replySearch = '';
        applyFilter(true);
      } else
        applyFilter();
    }
    function replyFilter(reply) {
      var textContains = common.textContains;
      var searchText = vm.replySearch;
      var isMatch = searchText ? textContains(reply.body, searchText) || textContains(reply.topic, searchText) || textContains(reply.body, searchText) || textContains(reply.created, searchText) || textContains(reply.votes, searchText) : true;
      return isMatch;
    }
    function setDate(value) {
      return moment.utc(value).format('ddd hh:mm a');
    }
    function refresh() {
      return userInfo.fetchUserReplies().then(function (data) {
        getAllReplies(true);
      });
    }
    function deleteReply(reply) {
      return userInfo.deleteReply(reply).then(function () {
        log('Deleted');
        getAllReplies();
      });
    }
    function open(course) {
      vm.reply = course;
      vm.updatable = true;
    }
    function editReply() {
      userInfo.updateReply(vm.reply).then(function () {
        vm.updatable = false;
        getAllReplies();
      });
    }
    function groupToPages() {
      vm.pagedItems = [];
      for (var i = 0; i < vm.filteredReplies.length; i++) {
        if (i % vm.itemsPerPage === 0) {
          vm.pagedItems[Math.floor(i / vm.itemsPerPage)] = [vm.filteredReplies[i]];
        } else {
          vm.pagedItems[Math.floor(i / vm.itemsPerPage)].push(vm.filteredReplies[i]);
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
  }
}());
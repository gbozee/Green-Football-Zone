(function () {
  'use strict';
  angular.module('app').factory('Pusher', [
    '$rootScope',
    'PusherService',
    pusher
  ]);
  angular.module('app').filter('capitalize', [capitalize]);
  angular.module('app').service('gfTypeSupport', [gfTypeSupport]);
  angular.module('app').service('gfService', [
    'CachedRestangular',
    gfService
  ]);
  angular.module('app').factory('CachedRestangular', [
    'Restangular',
    '$angularCacheFactory',
    CachedRestangular
  ]);
  function pusher($rootScope, PusherService) {
    return {
      subscribe: function (channel, eventName, cb) {
        PusherService.then(function (pusher) {
          pusher.subscribe(channel).bind(eventName, function (data) {
            if (cb)
              cb(data);
            $rootScope.$broadcast(channel + ':' + eventName, data);
            $rootScope.$digest();
          });
        });
      }
    };
  }
  function gfCacheFactory($angularCacheFactory) {
    $angularCacheFactory('myNewCache', {
      capacity: 1000,
      maxAge: 300000,
      deleteOnExpire: 'aggressive',
      recycleFreq: 60000,
      cacheFlushInterval: 3600000,
      verifyIntegrity: true
    });
  }
  function CachedRestangular(Restangular, $angularCacheFactory) {
    var cache;
    return Restangular.withConfig(function (RestangularConfigurer) {
      cache = $angularCacheFactory('gfCache', {
        maxAge: 900000,
        cacheFlushInterval: 3600000,
        deleteOnExpire: 'aggressive',
        storageMode: 'localStorage',
        capacity: 100
      });
      RestangularConfigurer.setDefaultHttpFields({ cache: cache });
    });
  }
  function gfTypeSupport() {
    var types = [
        'club',
        'country'
      ];
    var c_leagues = [
        'european',
        'african',
        'country'
      ];
    return {
      types: types,
      c_leagues: c_leagues
    };
  }
  function capitalize() {
    return function (input, scope) {
      return input.substring(0, 1).toUpperCase() + input.substring(1);
    };
  }
  function gfService(CachedRestangular) {
    var service = {};
    service.leagueResource = function () {
      return CachedRestangular.all('leagues');
    };
    service.teamResource = function () {
      return CachedRestangular.all('teams');
    };
    service.myResource = function () {
      return CachedRestangular.all('me');
    };
    service.userResource = function () {
      return CachedRestangular.all('users');
    };
    service.topicResource = function () {
      return CachedRestangular.all('topics');
    };
    service.replyResource = function () {
      return CachedRestangular.all('replies');
    };
    service.myTeamResource = function () {
      return CachedRestangular.all('my-teams');
    };
    return service;
  }
}());
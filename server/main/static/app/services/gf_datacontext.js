(function () {
    'use strict';
//Todo: Rearrange and refractor

    angular.module('app').factory('Pusher', ['$rootScope','PusherService',pusher]);
    angular.module('app').filter('capitalize', [capitalize]);
    angular.module('app').service('gfTypeSupport', [gfTypeSupport]);
    angular.module('app').service('gfService',['CachedRestangular',gfService])
    angular.module('app').factory('CachedRestangular', ['Restangular','$angularCacheFactory', CachedRestangular]);

//    angular.module('app').service('gfCacheFactory',['$angularCacheFactory',gfCacheFactory]);


    function pusher($rootScope, PusherService) {
        return {
            subscribe: function (channel, eventName, cb) {
                PusherService.then(function (pusher) {
                    pusher.subscribe(channel)
                        .bind(eventName, function (data) {
                            if (cb) cb(data);
                            $rootScope
                                .$broadcast(channel + ':' + eventName, data);
                            $rootScope.$digest();
                        })
                })
            }
        }
    }

    function gfCacheFactory($angularCacheFactory){
        $angularCacheFactory('myNewCache', {

        // This cache can hold 1000 items
        capacity: 1000,

        // Items added to this cache expire after 15 minutes
        maxAge: 300000,

        // Items will be actively deleted when they expire
        deleteOnExpire: 'aggressive',

        // This cache will check for expired items every minute
        recycleFreq: 60000,

        // This cache will clear itself every hour
        cacheFlushInterval: 3600000,

        // This cache will sync itself with localStorage
//        storageMode: 'localStorage',

//        // Custom implementation of localStorage
//        storageImpl: myLocalStoragePolyfill,

        // Full synchronization with localStorage on every operation
        verifyIntegrity: true

        // This callback is executed when the item specified by "key" expires.
        // At this point you could retrieve a fresh value for "key"
        // from the server and re-insert it into the cache.
//        onExpire: function (key, value) {
//
//        }
     });

    }

    function CachedRestangular(Restangular,$angularCacheFactory) {
        var cache;
        return Restangular.withConfig(function (RestangularConfigurer) {
            cache = $angularCacheFactory('gfCache', {
                    maxAge: 900000, // Items added to this cache expire after 15 minutes.
                    cacheFlushInterval: 3600000, // This cache will clear itself every hour.
                    deleteOnExpire: 'aggressive', // Items will be deleted from this cache right when they expire.
                    storageMode: 'localStorage',
                    capacity: 100
                 });
            RestangularConfigurer.setDefaultHttpFields({cache:cache});
//            RestangularConfigurer.setResponseInterceptor(function(response,operation){
//                if (operation === 'put' || operation === 'post' || operation === 'delete') {
//                       cache.removeAll();
//                }
//                return response;
//            });
//            RestangularConfigurer.setResponseExtractor(function (response, operation, what, url) {
//                // This is a get for a list
//                var newResponse = response;
//                if (angular.isArray(response)) {
//                    angular.forEach(newResponse, function (value, key) {
////                        newResponse[key].originalElement = angular.copy(value);
//                        newResponse.originalElement[key] = angular.copy(value);
//                    });
//                } else {
//                    newResponse.originalElement = angular.copy(response);
//                }
//
//                return newResponse;
//            });
        });
    }


    function gfTypeSupport() {
        var types = ['club', 'country'];
        var c_leagues = ['european', 'african', 'country'];
        return{
            types: types,
            c_leagues: c_leagues
        }


    }
    function capitalize() {
        return function (input, scope) {
            return input.substring(0, 1).toUpperCase() + input.substring(1);
        }
    }

    function gfService(CachedRestangular){
    var service = {};

    service.leagueResource = function(){
        return CachedRestangular.all('leagues');
    }

    service.teamResource = function(){
        return CachedRestangular.all('teams');
    }
    service.myResource = function(){
        return CachedRestangular.all('me');
    }
    service.userResource = function(){
        return CachedRestangular.all('users')
    }
    service.topicResource = function(){
        return CachedRestangular.all('topics');
    }
    service.replyResource = function(){
        return CachedRestangular.all('replies');
    }

    service.myTeamResource = function(){
        return CachedRestangular.all('my-teams');
    }

    return service;
}

})();


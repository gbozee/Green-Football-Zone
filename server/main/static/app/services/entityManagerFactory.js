(function () {
    'use strict';

    var serviceId = 'Conf';
    angular.module('app').factory(serviceId, ['$location', 'config', serverConfig]);
    angular.module('app').factory('GFAPI',['Conf','$http',googlePlusGF])

    function serverConfig($location, config) {

        function getRootUrl() {
            var rootUrl = $location.protocol() + '://' + $location.host();
            if ($location.port())
                rootUrl += ':' + $location.port();
            return rootUrl;
        }
        var serviceName = config.remoteServiceName;

        var provider = {
            'clientId': '183001439932',
//            'clientId': '183001439932.apps.googleusercontent.com',
            'apiBase': serviceName,
            'rootUrl': getRootUrl(),
            'scopes': 'https://www.googleapis.com/auth/plus.login ',
            'requestvisibleactions': 'http://schemas.google.com/AddActivity ' +
                'http://schemas.google.com/ReviewActivity',
            'cookiepolicy': 'single_host_origin'
        };

        return provider;
    }
    function googlePlusGF(Conf,$http){
        return {
        signIn: function(authResult) {
          return $http.post(Conf.apiBase + 'connect', authResult);
        },
        verify:function(authResult){
            return $http.post(Conf.apiBase+'verify',authResult);
        },
//        votePhoto: function(photoId) {
//          return $http.put(Conf.apiBase + 'votes',
//              {'photoId': photoId});
//        },
//        getThemes: function() {
//          return $http.get(Conf.apiBase + 'themes');
//        },
//        getUploadUrl: function() {
//          return $http.post(Conf.apiBase + 'images');
//        },
//        getAllPhotosByTheme: function(themeId) {
//          return $http.get(Conf.apiBase + 'photos',
//              {params: {'themeId': themeId}});
//        },
//        getPhoto: function(photoId) {
//          return $http.get(Conf.apiBase + 'photos', {params:
//              {'photoId': photoId}});
//        },
//        getUserPhotosByTheme: function(themeId) {
//          return $http.get(Conf.apiBase + 'photos', {params:
//              {'themeId': themeId, 'userId': 'me'}});
//        },
        getFriends: function () {
          return $http.get(Conf.apiBase + 'friends');
        },
//        getFriendsPhotosByTheme: function(themeId) {
//          return $http.get(Conf.apiBase + 'photos', {params:
//              {'themeId': themeId, 'userId': 'me', 'friends': 'true'}});
//        },
//        deletePhoto: function(photoId) {
//          return $http.delete(Conf.apiBase + 'photos', {params:
//              {'photoId': photoId}});
//        },
        disconnect: function() {
          return $http.post(Conf.apiBase + 'disconnect');
        }
      };
    }
})();
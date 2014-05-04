(function () {
  'use strict';
  var serviceId = 'Conf';
  angular.module('app').factory(serviceId, [
    '$location',
    'config',
    serverConfig
  ]);
  angular.module('app').factory('GFAPI', [
    'Conf',
    '$http',
    googlePlusGF
  ]);
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
        'apiBase': serviceName,
        'rootUrl': getRootUrl(),
        'scopes': 'https://www.googleapis.com/auth/plus.login ',
        'requestvisibleactions': 'http://schemas.google.com/AddActivity ' + 'http://schemas.google.com/ReviewActivity',
        'cookiepolicy': 'single_host_origin'
      };
    return provider;
  }
  function googlePlusGF(Conf, $http) {
    return {
      signIn: function (authResult) {
        return $http.post(Conf.apiBase + 'connect', authResult);
      },
      verify: function (authResult) {
        return $http.post(Conf.apiBase + 'verify', authResult);
      },
      getFriends: function () {
        return $http.get(Conf.apiBase + 'friends');
      },
      disconnect: function () {
        return $http.post(Conf.apiBase + 'disconnect');
      }
    };
  }
}());
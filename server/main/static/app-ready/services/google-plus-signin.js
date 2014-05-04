'use strict';
angular.module('directive.g+signin', []).directive('googlePlusShare', function () {
  return {
    restrict: 'E',
    template: '<span id="myBtn">' + '<span class="icon">&nbsp;</span>' + '<span>{{text}}</span></span>',
    transclude: true,
    replace: true,
    link: function (scope, element, attrs) {
      scope.text = attrs.text;
      attrs.$set('class', 'dissolve-animation demo g-interactivepost');
      attrs.$set('data-prefilltext', attrs.prefilltext);
      attrs.$set('data-calltoactionlabel', attrs.calltoactionlabel);
      attrs.$set('data-clientid', attrs.clientid + '.apps.googleusercontent.com');
      attrs.$set('data-contenturl', attrs.contenturl);
      attrs.$set('data-calltoactionurl', attrs.contenturl);
      var defaults = {
          contentdeeplinkid: '',
          cookiepolicy: 'single_host_origin',
          calltoactiondeeplinkid: ''
        };
      angular.forEach(Object.getOwnPropertyNames(defaults), function (propName) {
        if (!attrs.hasOwnProperty('data-' + propName)) {
          attrs.$set('data-' + propName, defaults[propName]);
        }
      });
      (function () {
        var po = document.createElement('script');
        po.type = 'text/javascript';
        po.async = true;
        po.src = 'https://apis.google.com/js/client:plusone.js';
        var s = document.getElementsByTagName('script')[0];
        s.parentNode.insertBefore(po, s);
      }());
    }
  };
}).directive('googleRegularShare', function () {
  return {
    restrict: 'E',
    template: '<div class="g-plus" data-action="share"></div>',
    replace: true,
    link: function (scope, element, attrs) {
      (function () {
        var po = document.createElement('script');
        po.type = 'text/javascript';
        po.async = true;
        po.src = 'https://apis.google.com/js/client:plusone.js';
        var s = document.getElementsByTagName('script')[0];
        s.parentNode.insertBefore(po, s);
      }());
    }
  };
}).directive('googlePlusSignin', function () {
  return {
    restrict: 'E',
    template: '<span></span>',
    replace: true,
    link: function (scope, element, attrs) {
      attrs.$set('class', 'g-signin');
      attrs.$set('data-clientid', attrs.clientid + '.apps.googleusercontent.com');
      var defaults = {
          callback: 'signinCallback',
          cookiepolicy: 'none',
          requestvisibleactions: 'http://schemas.google.com/AddActivity http://schemas.google.com/ReviewActivity',
          scope: 'https://www.googleapis.com/auth/plus.login https://www.googleapis.com/auth/userinfo.email',
          width: 'medium',
          redirecturi: 'postmessage',
          'theme': 'dark',
          accesstype: 'offline'
        };
      angular.forEach(Object.getOwnPropertyNames(defaults), function (propName) {
        if (!attrs.hasOwnProperty('data-' + propName)) {
          attrs.$set('data-' + propName, defaults[propName]);
        }
      });
      (function () {
        var po = document.createElement('script');
        po.type = 'text/javascript';
        po.async = true;
        po.src = 'https://apis.google.com/js/client:plusone.js';
        var s = document.getElementsByTagName('script')[0];
        s.parentNode.insertBefore(po, s);
      }());
    }
  };
}).run([
  '$window',
  '$rootScope',
  function ($window, $rootScope) {
    $window.signinCallback = function (authResult) {
      if (authResult && authResult.access_token) {
        $rootScope.$broadcast('event:google-plus-signin-success', authResult);
      } else {
        $rootScope.$broadcast('event:google-plus-signin-failure', authResult);
      }
    };
  }
]);
angular.module('app.pusher', []).provider('PusherService', function () {
  var _scriptUrl = '//js.pusher.com/2.1/pusher.min.js', _scriptId = 'pusher-sdk', _token = '', _initOptions = {};
  this.setOptions = function (opts) {
    _initOptions = opts || _initOptions;
    return this;
  };
  this.setToken = function (token) {
    _token = token || _token;
    return this;
  };
  function createScript($document, callback, success) {
    var scriptTag = $document.createElement('script');
    scriptTag.type = 'text/javascript';
    scriptTag.async = true;
    scriptTag.id = _scriptId;
    scriptTag.src = _scriptUrl;
    scriptTag.onreadystatechange = function () {
      if (this.readyState == 'complete') {
        callback();
      }
    };
    scriptTag.onload = callback;
    var s = $document.getElementsByTagName('body')[0];
    s.appendChild(scriptTag);
  }
  this.$get = [
    '$document',
    '$timeout',
    '$q',
    '$rootScope',
    '$window',
    function ($document, $timeout, $q, $rootScope, $window) {
      var deferred = $q.defer(), socket, _pusher;
      function onSuccess() {
        _pusher = new $window.Pusher(_token, _initOptions);
      }
      var onScriptLoad = function (callback) {
        onSuccess();
        $timeout(function () {
          deferred.resolve(_pusher);
        });
      };
      createScript($document[0], onScriptLoad);
      return deferred.promise;
    }
  ];
});
'use strict';

/*
 * angular-google-plus-directive v0.0.1
 * ♡ CopyHeart 2013 by Jerad Bitner http://jeradbitner.com
 * Copying is an act of love. Please copy.
 */

angular.module('directive.g+signin', [])
    .directive('googlePlusShare', function () {
        return{
            restrict: 'E',
            template: '<span id="myBtn">' +
                '<span class="icon">&nbsp;</span>' +
                '<span>{{text}}</span></span>',
            transclude: true,
            replace: true,
            link: function (scope, element, attrs) {
                scope.text = attrs.text;
                // Set class.
                attrs.$set('class', 'dissolve-animation demo g-interactivepost');
                attrs.$set('data-prefilltext', attrs.prefilltext);
                attrs.$set('data-calltoactionlabel', attrs.calltoactionlabel);
                attrs.$set('data-clientid', attrs.clientid + '.apps.googleusercontent.com');
                attrs.$set('data-contenturl', attrs.contenturl);
                attrs.$set('data-calltoactionurl', attrs.contenturl);

                // Some default values, based on prior versions of this directive
                var defaults = {
//                    contenturl: 'http://gcdc2013-green-football.appspot.com',
                    contentdeeplinkid: '',
                    cookiepolicy: 'single_host_origin',
                    calltoactiondeeplinkid: ''
                };

                // Provide default values if not explicitly set
                angular.forEach(Object.getOwnPropertyNames(defaults), function (propName) {
                    if (!attrs.hasOwnProperty('data-' + propName)) {
                        attrs.$set('data-' + propName, defaults[propName]);
                    }
                });

                // Asynchronously load the G+ SDK.
                (function () {
                    var po = document.createElement('script');
                    po.type = 'text/javascript';
                    po.async = true;
                    po.src = 'https://apis.google.com/js/client:plusone.js';
                    var s = document.getElementsByTagName('script')[0];
                    s.parentNode.insertBefore(po, s);
                })();
            }
        }
    })
    .directive('googleRegularShare', function () {
        return{
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
                })();
            }
        };
    })
    .directive('googlePlusSignin',function () {
        return {
            restrict: 'E',
            template: '<span></span>',
            replace: true,
            link: function (scope, element, attrs) {

                // Set class.
                attrs.$set('class', 'g-signin');

                attrs.$set('data-clientid', attrs.clientid + '.apps.googleusercontent.com');

                // Some default values, based on prior versions of this directive
                var defaults = {
                    callback: 'signinCallback',
                    cookiepolicy: 'none',
//        cookiepolicy: 'single_host_origin',
                    requestvisibleactions: 'http://schemas.google.com/AddActivity http://schemas.google.com/ReviewActivity',
                    scope: 'https://www.googleapis.com/auth/plus.login https://www.googleapis.com/auth/userinfo.email',
                    width: 'medium',
                    redirecturi: "postmessage",
                    'theme': 'dark',
//        'approvalprompt':'force',
                    accesstype: 'offline'
                };

                // Provide default values if not explicitly set
                angular.forEach(Object.getOwnPropertyNames(defaults), function (propName) {
                    if (!attrs.hasOwnProperty('data-' + propName)) {
                        attrs.$set('data-' + propName, defaults[propName]);
                    }
                });

                // Asynchronously load the G+ SDK.
                (function () {
                    var po = document.createElement('script');
                    po.type = 'text/javascript';
                    po.async = true;
                    po.src = 'https://apis.google.com/js/client:plusone.js';
                    var s = document.getElementsByTagName('script')[0];
                    s.parentNode.insertBefore(po, s);
                })();
            }
        };
    }).run(['$window', '$rootScope', function ($window, $rootScope) {
        $window.signinCallback = function (authResult) {
            if (authResult && authResult.access_token) {
                $rootScope.$broadcast('event:google-plus-signin-success', authResult);
            }
            else {
                $rootScope.$broadcast('event:google-plus-signin-failure', authResult);
            }
        };
    }]);
angular.module('app.pusher', [])
    .provider('PusherService', function () {
        var _scriptUrl = '//js.pusher.com/2.1/pusher.min.js'
            , _scriptId = 'pusher-sdk'
            , _token = ''
            , _initOptions = {};

        this.setOptions = function (opts) {
            _initOptions = opts || _initOptions;
            return this;
        }

        this.setToken = function (token) {
            _token = token || _token;
            return this;
        }

        // Create a script tag with moment as the source
        // and call our onScriptLoad callback when it
        // has been loaded
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
            }
            // Set the callback to be run
            // after the scriptTag has loaded
            scriptTag.onload = callback;
            // Attach the script tag to the document body
            var s = $document
                .getElementsByTagName('body')[0];
            s.appendChild(scriptTag);
        }

        this.$get = ['$document', '$timeout', '$q', '$rootScope', '$window',
            function ($document, $timeout, $q, $rootScope, $window) {
                var deferred = $q.defer(),
                    socket,
                    _pusher;

                function onSuccess() {
                    // Executed when the SDK is loaded
                    _pusher = new $window.Pusher(_token, _initOptions);
                }

                // Load client in the browser
                // which will get called after the script
                // tag has been loaded
                var onScriptLoad = function (callback) {
                    onSuccess();
                    $timeout(function () {
                        // Resolve the deferred promise
                        // as the FB object on the window
                        deferred.resolve(_pusher);
                    });
                };

                // Kick it off and get Pushing
                createScript($document[0], onScriptLoad);
                return deferred.promise;
            }]
    });



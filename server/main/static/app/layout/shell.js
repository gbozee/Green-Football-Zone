(function () {
    'use strict';

    var controllerId = 'shell';
    angular.module('app').controller(controllerId,
        ['$window', '$scope', '$location', '$rootScope', 'common', 'config', 'userInfo', 'GFAPI', 'Conf', shell]);

    function shell($window, $scope, $location, $rootScope, common, config, userInfo, GFAPI, Conf) {
        var vm = this;
        var logSuccess = common.logger.getLogFn(controllerId, 'success');
        var events = config.events;
//        vm.signedIn = datacontext.isSignedIn();
//        vm.image = datacontext.getUserImage();
//        vm.isSignedIn = isSignedIn();
        vm.busyMessage = 'Please wait ...';
        vm.isBusy = true;
        vm.hello = "This is me";
        var keyCodes = config.keyCodes;
        vm.search = search;
        vm.searchText = '';
        vm.clientId = Conf.clientId;

        vm.spinnerOptions = {
            radius: 40,
            lines: 7,
            length: 0,
            width: 30,
            speed: 1.7,
            corners: 1.0,
            trail: 100,
            color: '#F58A00'
        };
        vm.data = userInfo;

        activate();

        function activate() {
            logSuccess('GF loaded!', null, true);
            common.activateController([], controllerId);

        }


//        function signedIn() {
//            return datacontext.hasGooglePlusToken()
//                .then(function (data) {
//                    vm.signedIn = data;
//                })
//        }

        function toggleSpinner(on) {
            vm.isBusy = on;
        }


        $rootScope.$on('$routeChangeStart',
            function (event, next, current) {
                toggleSpinner(true);
            }
        );

        $rootScope.$on(events.controllerActivateSuccess,
            function (data) {
                toggleSpinner(false);
            }
        );

        $rootScope.$on(events.spinnerToggle,
            function (data) {
                toggleSpinner(data.show);
            }
        );

        function search($event) {
            if ($event.keyCode === keyCodes.esc) {
                vm.searchText = '';
                return;
            }
            if ($event.type === 'click' || $event.keyCode === keyCodes.enter) {
                var route = '/teams/search/';
                $location.path(route + vm.searchText);
            }
        }

        // signIn
        vm.userProfile = undefined;
        vm.hasUserProfile = false;

        vm.immediateFailed = false;

//        vm.disconnect = function () {
//            GFAPI.disconnect().then(function () {
//                vm.userProfile = undefined;
//                vm.hasUserProfile = false;
//                vm.isSignedIn = false;
//                vm.immediateFailed = true;
//
//            });
//        }
//
//
//        vm.getFriends = function () {
//            GFAPI.getFriends().then(function (response) {
//                vm.friends = response.data;
////              vm.getFriendsPhotos();
//            })
//        }
//
//
//        vm.signedIn = function (profile) {
//            vm.isSignedIn = true;
//            vm.userProfile = profile;
//            vm.hasUserProfile = true;
////
//            vm.signIn = function (authResult) {
//                $scope.$apply(function () {
//                    vm.processAuth(authResult);
//                });
//            }
//        }
//
//        vm.processAuth = function (authResult) {
//            vm.immediateFailed = true;
//            if (vm.isSignedIn) {
//                return 0;
//            }
//            if (authResult['access_token']) {
//                vm.immediateFailed = false;
//                console.log(authResult);
//                // Successfully authorized, create session
////              GFAPI.signIn(authResult).then(function(response) {
////                $scope.signedIn(response.data);
//
////              });
//            } else if (authResult['error']) {
//                if (authResult['error'] == 'immediate_failed') {
//                    vm.immediateFailed = true;
//                } else {
//                    console.log('Error:' + authResult['error']);
//                }
//            }
//        }
//
//        vm.renderSignIn = function () {
//            $window.gapi.signin.render('myGsignin', {
//                'callback': vm.signIn,
//                'clientid': Conf.clientId,
//                'requestvisibleactions': Conf.requestvisibleactions,
//                'scope': Conf.scopes,
////              'apppackagename': Conf.apppackagename,
//                'theme': 'dark',
//                'cookiepolicy': Conf.cookiepolicy,
//                'accesstype': 'offline'
//            });
//        }

        $scope.$on('event:google-plus-signin-success', function (event,authResult) {
    // Send login to server or save into cookie
            vm.isSignedIn = true;
            console.log(authResult);
            userInfo.getCredentials(authResult);
          });
          $scope.$on('event:google-plus-signin-failure', function (event,authResult) {
            // Auth failure or signout detected
              console.log(authResult);
          });



    }



})();
(function () {
    'use strict';

    var app = angular.module('app', [
        // Angular modules 
        'ngAnimate',        // animations
        'ngRoute',          // routing
        'ngSanitize',       // sanitizes html bindings (ex: sidebar.js)
        'ngResource',       // resourceModule
        'ngTouch',          // touch mobile Devices
        'restangular',      //Restangular

        // Custom modules 
        'common',           // common functions, logger, spinner
        'common.bootstrap', // bootstrap dialog wrapper functions

        // 3rd Party Modules
        'ui.bootstrap',   // ui-bootstra'fundoo.services'   // for modal
        'jmdobry.angular-cache', // angular-cache
        'directive.g+signin', //Google plus sign in directive
        'app.pusher', //Pusher
        'ngProgress' //ngProgress
//        'FacebookPluginDirectives', //Facebook social icon directives
    ]);

    'use strict';

    // Factory name is handy for logging
    var serviceId = 'routemediator';

    // Define the factory on the module.
    // Inject the dependencies.
    // Point to the factory definition function.
    angular.module('app')
        .factory(serviceId,
            ['$location', '$rootScope', 'config', 'logger', routemediator]);
    //Todo: fix the routemediator
    function routemediator($location, $rootScope, config, logger) {
        // Define the functions and properties to reveal.
        var handleRouteChangeError = false;
        var service = {
            setRoutingHandlers: setRoutingHandlers,
            updateDoctitle: updateDocTitle
        };

        return service;

        function setRoutingHandlers() {
            updateDocTitle();
            handleRoutingErrors();
        }

        function handleRoutingErrors() {
            $rootScope.$on('$routeChangeError',
                function (event, current, previous, rejection) {
                    if (handleRouteChangeError) {
                        return;
                    }
                    handleRouteChangeError = true;
                    var msg = 'Error routing: ' + (current && current.name)
                        + '. ' + (rejection.msg || '');
                    logger.logWarning(msg, current, serviceId, true);
                    $location.path('/');
                });
        }

        function updateDocTitle() {
            $rootScope.$on('$routeChangeSuccess',
                function (event, current, previous) {
                    handleRouteChangeError = false;
                    var title = config.docTitle + ' ' + (current.title || '');
                    $rootScope.title = title;
                });
        }
    }

//    Handle routing errors and success events
    app.run(['$route', 'routemediator'
        , function ($route, routemediator) {
        // Include $route to kick start the router.
        routemediator.updateDoctitle();
    }]);
})();
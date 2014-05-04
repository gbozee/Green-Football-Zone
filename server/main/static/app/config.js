(function () {
    'use strict';

    var app = angular.module('app');

    // Configure Toastr
    toastr.options.timeOut = 4000;
    toastr.options.positionClass = 'toast-bottom-right';

    // For use with the HotTowel-Angular-Breeze add-on that uses Breeze
    var remoteServiceName = '/api/v2.0/';

    var events = {
        controllerActivateSuccess: 'controller.activateSuccess',
        spinnerToggle: 'spinner.toggle'
    };
    var imageSettings = {
        imageBasePath: '/img/',
        unknownPersonImageSource: 'team-icon.png'
    };

    var keyCodes = {
        backspace: 8,
        tab: 9,
        enter: 13,
        esc: 27,
        space: 32,
        pageup: 33,
        pagedown: 34,
        end: 35,
        home: 36,
        left: 37,
        up: 38,
        right: 39,
        down: 40,
        insert: 45,
        del: 46
    };

    var config = {
        appErrorPrefix: '[GF Error] ', //Configure the exceptionHandler decorator
        docTitle: 'GF: ',
        events: events,
        keyCodes: keyCodes,
        remoteServiceName: remoteServiceName,
        version: '2.0.0',
        imageSettings: imageSettings
    };

    app.value('config', config);

    app.config(['$logProvider', function ($logProvider) {
        // turn debugging off/on (no info or warn)
        if ($logProvider.debugEnabled) {
            $logProvider.debugEnabled(true);
        }
    }]);

    //#region Configure the common services via commonConfig
    app.config(['commonConfigProvider', function (cfg) {
        cfg.config.controllerActivateSuccessEvent = config.events.controllerActivateSuccess;
        cfg.config.spinnerToggleEvent = config.events.spinnerToggle;
    }]);
    //#endregion
    app.config(['PusherServiceProvider',function(PusherServiceProvider){
        PusherServiceProvider
            .setToken('7a3da06e97f015d45d27')
            .setOptions({});
    }]);
    app.config(['RestangularProvider', function (restangular) {
        restangular.setBaseUrl('/api/v2.0')
        restangular.setRestangularFields({
            id: "name",
            route: "restangularRoute",
            selfLink: "self.href",
            name: "name"
        });
        restangular.setRequestInterceptor(function (elem, operation) {
            if (operation === "remove") {
                return undefined;
            }
            return elem;
        });
        // Now let's configure the response extractor for each request
        restangular.setResponseExtractor(function (response, operation, what, url) {
            // This is a get for a list
            var newResponse;
            if (operation === "getList") {
                // Here we're returning an Array which has one special property metadata with our extra information
                newResponse = response.data.results;
                newResponse.metadata = response.data.meta;
            } else {
                // This is an element
                newResponse = response.data;
            }
            return newResponse;
        });
    }]);
//    app.config(['$angularCacheFactoryProvider', function ($angularCacheFactoryProvider) {
//        $angularCacheFactoryProvider.setCacheDefaults({
//            maxAge: 3600000,
//            deleteOnExpire: 'aggressive'
//        });
//
//    }])
})();


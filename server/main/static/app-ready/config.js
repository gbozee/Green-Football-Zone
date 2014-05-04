(function () {
  'use strict';
  var app = angular.module('app');
  toastr.options.timeOut = 4000;
  toastr.options.positionClass = 'toast-bottom-right';
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
      appErrorPrefix: '[GF Error] ',
      docTitle: 'GF: ',
      events: events,
      keyCodes: keyCodes,
      remoteServiceName: remoteServiceName,
      version: '2.0.0',
      imageSettings: imageSettings
    };
  app.value('config', config);
  app.config([
    '$logProvider',
    function ($logProvider) {
      if ($logProvider.debugEnabled) {
        $logProvider.debugEnabled(true);
      }
    }
  ]);
  app.config([
    'commonConfigProvider',
    function (cfg) {
      cfg.config.controllerActivateSuccessEvent = config.events.controllerActivateSuccess;
      cfg.config.spinnerToggleEvent = config.events.spinnerToggle;
    }
  ]);
  app.config([
    'PusherServiceProvider',
    function (PusherServiceProvider) {
      PusherServiceProvider.setToken('7a3da06e97f015d45d27').setOptions({});
    }
  ]);
  app.config([
    'RestangularProvider',
    function (restangular) {
      restangular.setBaseUrl('/api/v2.0');
      restangular.setRestangularFields({
        id: 'name',
        route: 'restangularRoute',
        selfLink: 'self.href',
        name: 'name'
      });
      restangular.setRequestInterceptor(function (elem, operation) {
        if (operation === 'remove') {
          return undefined;
        }
        return elem;
      });
      restangular.setResponseExtractor(function (response, operation, what, url) {
        var newResponse;
        if (operation === 'getList') {
          newResponse = response.data.results;
          newResponse.metadata = response.data.meta;
        } else {
          newResponse = response.data;
        }
        return newResponse;
      });
    }
  ]);
}());
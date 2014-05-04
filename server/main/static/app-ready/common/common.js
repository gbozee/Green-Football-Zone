(function () {
  'use strict';
  var commonModule = angular.module('common', []);
  commonModule.provider('commonConfig', function () {
    this.config = {};
    this.$get = function () {
      return { config: this.config };
    };
  });
  commonModule.factory('common', [
    '$q',
    '$rootScope',
    '$timeout',
    'commonConfig',
    'logger',
    common
  ]);
  function common($q, $rootScope, $timeout, commonConfig, logger) {
    var throttles = {};
    var service = {
        $broadcast: $broadcast,
        $q: $q,
        $timeout: $timeout,
        activateController: activateController,
        createSearchThrottle: createSearchThrottle,
        debouncedThrottle: debouncedThrottle,
        isNumber: isNumber,
        logger: logger,
        textContains: textContains
      };
    return service;
    function activateController(promises, controllerId) {
      return $q.all(promises).then(function (eventArgs) {
        var data = { controllerId: controllerId };
        $broadcast(commonConfig.config.controllerActivateSuccessEvent, data);
      });
    }
    function $broadcast() {
      return $rootScope.$broadcast.apply($rootScope, arguments);
    }
    function createSearchThrottle(viewmodel, list, filteredList, filter, delay) {
      console.log(viewmodel);
      delay = +delay || 300;
      if (!filteredList) {
        filteredList = 'filtered' + list[0].toUpperCase() + list.substr(1).toLowerCase();
        filter = list + 'Filter';
      }
      var filterFn = function () {
        viewmodel[filteredList] = viewmodel[list].filter(function (item) {
          return viewmodel[filter](item);
        });
      };
      return function () {
        var filterInputTimeout;
        return function (searchNow) {
          if (filterInputTimeout) {
            $timeout.cancel(filterInputTimeout);
            filterInputTimeout = null;
          }
          if (searchNow || !delay) {
            filterFn();
          } else {
            filterInputTimeout = $timeout(filterFn, delay);
          }
        };
      }();
    }
    function debouncedThrottle(key, callback, delay, immediate) {
      var defaultDelay = 1000;
      delay = delay || defaultDelay;
      if (throttles[key]) {
        $timeout.cancel(throttles[key]);
        throttles[key] = undefined;
      }
      if (immediate) {
        callback();
      } else {
        throttles[key] = $timeout(callback, delay);
      }
    }
    function isNumber(val) {
      return /^[-]?\d+$/.test(val);
    }
    function textContains(text, searchText) {
      return text && -1 !== text.toLowerCase().indexOf(searchText.toLowerCase());
    }
  }
}());
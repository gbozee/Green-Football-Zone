(function () {
  'use strict';
  var app = angular.module('app');
  app.directive('ccSidebar', [
    '$window',
    function ($window) {
      var directive = {
          link: link,
          restrict: 'A'
        };
      var $win = $($window);
      return directive;
      function link(scope, element, attrs) {
        var $sidebarInner = element.find('.sidebar-inner');
        var $dropdownElement = element.find('.sidebar-dropdown a');
        element.addClass('sidebar');
        $win.resize(resize);
        $dropdownElement.click(dropdown);
        function resize() {
          $win.width() >= 765 ? $sidebarInner.slideDown(350) : $sidebarInner.slideUp(350);
        }
        function dropdown(e) {
          var dropClass = 'dropy';
          e.preventDefault();
          if (!$dropdownElement.hasClass(dropClass)) {
            hideAllSidebars();
            $sidebarInner.slideDown(350);
            $dropdownElement.addClass(dropClass);
          } else if ($dropdownElement.hasClass(dropClass)) {
            $dropdownElement.removeClass(dropClass);
            $sidebarInner.slideUp(350);
          }
          function hideAllSidebars() {
            $sidebarInner.slideUp(350);
            $('.sidebar-dropdown a').removeClass(dropClass);
          }
        }
      }
    }
  ]);
  app.directive('ccWidgetClose', function () {
    var directive = {
        link: link,
        template: '<i class="icon-remove"></i>',
        restrict: 'A'
      };
    return directive;
    function link(scope, element, attrs) {
      attrs.$set('href', '#');
      attrs.$set('wclose');
      element.click(close);
      function close(e) {
        e.preventDefault();
        element.parent().parent().parent().hide(100);
      }
    }
  });
  app.directive('ccSlideBoxClose', function () {
    var directive = {
        link: link,
        template: '<i class="icon-remove"></i>',
        restrict: 'A'
      };
    return directive;
    function link(scope, element, attrs) {
      attrs.$set('href', '#');
      attrs.$set('sclose');
      element.click(close);
      function close(e) {
        e.preventDefault();
        element.parent().parent().parent().hide(100);
      }
    }
  });
  app.directive('ccWidgetMinimize', function () {
    var directive = {
        link: link,
        template: '<i class="icon-chevron-up"></i>',
        restrict: 'A'
      };
    return directive;
    function link(scope, element, attrs) {
      attrs.$set('href', '#');
      attrs.$set('wminimize');
      element.click(minimize);
      function minimize(e) {
        e.preventDefault();
        var $wcontent = element.parent().parent().next('.widget-content');
        var iElement = element.children('i');
        if ($wcontent.is(':visible')) {
          iElement.removeClass('icon-chevron-up');
          iElement.addClass('icon-chevron-down');
        } else {
          iElement.removeClass('icon-chevron-down');
          iElement.addClass('icon-chevron-up');
        }
        $wcontent.toggle(500);
      }
    }
  });
  app.directive('ccSlideBoxMinimize', function () {
    var directive = {
        link: link,
        template: '<i class="icon-chevron-up"></i>',
        restrict: 'A'
      };
    return directive;
    function link(scope, element, attrs) {
      attrs.$set('href', '#');
      attrs.$set('sminimize');
      element.click(minimize);
      function minimize(e) {
        e.preventDefault();
        var $wcontent = element.parent().parent().next('.widget-content');
        var iElement = element.children('i');
        if ($wcontent.is(':visible')) {
          iElement.removeClass('icon-chevron-up');
          iElement.addClass('icon-chevron-down');
        } else {
          iElement.removeClass('icon-chevron-down');
          iElement.addClass('icon-chevron-up');
        }
        $wcontent.toggle(500);
      }
    }
  });
  app.directive('ccScrollToTop', [
    '$window',
    function ($window) {
      var directive = {
          link: link,
          template: '<a href="#"><i class="icon-chevron-up"></i></a>',
          restrict: 'A'
        };
      return directive;
      function link(scope, element, attrs) {
        var $win = $($window);
        element.addClass('totop');
        $win.scroll(toggleIcon);
        element.find('a').click(function (e) {
          e.preventDefault();
          $('body').animate({ scrollTop: 0 }, 500);
        });
        function toggleIcon() {
          $win.scrollTop() > 300 ? element.slideDown() : element.slideUp();
        }
      }
    }
  ]);
  app.directive('ccSpinner', [
    '$window',
    function ($window) {
      var directive = {
          link: link,
          restrict: 'A'
        };
      return directive;
      function link(scope, element, attrs) {
        scope.spinner = null;
        scope.$watch(attrs.ccSpinner, function (options) {
          if (scope.spinner) {
            scope.spinner.stop();
          }
          scope.spinner = new $window.Spinner(options);
          scope.spinner.spin(element[0]);
        }, true);
      }
    }
  ]);
  app.directive('ccImgPerson', [
    'config',
    function (config) {
      var basePath = config.imageSettings.imageBasePath;
      var unknownImage = config.imageSettings.unknownPersonImageSource;
      var directive = {
          link: link,
          restrict: 'A'
        };
      return directive;
      function link(scope, element, attrs) {
        attrs.$observe('ccImgPerson', function (value) {
          value = basePath + (value || unknownImage);
          attrs.$set('src', value);
        });
      }
    }
  ]);
  app.directive('ccWidgetHeader', function () {
    var directive = {
        link: link,
        scope: {
          'title': '@',
          'subtitle': '@',
          'rightText': '@',
          'allowCollapse': '@'
        },
        templateUrl: '/p/app/layout/widgetheader.html',
        restrict: 'A'
      };
    return directive;
    function link(scope, element, attrs) {
      attrs.$set('class', 'widget-head');
    }
  });
  app.directive('upvote', function () {
    return {
      restrict: 'E',
      templateUrl: '/p/app/layout/upvote.html',
      scope: {
        count: '@',
        upvote: '&',
        downvote: '&'
      }
    };
  });
  app.directive('gfPageHeading', function () {
    return {
      restrict: 'E',
      templateUrl: '/p/app/layout/Page-heading.html',
      scope: {
        title: '@',
        subtitle: '@'
      }
    };
  });
  app.directive('gfPager', function () {
    return {
      restrict: 'E',
      templateUrl: '/p/app/layout/gf-pager.html',
      scope: {
        showPrevious: '=',
        showNext: '=',
        next: '&',
        previous: '&'
      }
    };
  });
  app.directive('gfFollowTeam', function () {
    return {
      restrict: 'E',
      replace: true,
      template: '<div class="gf-follow-button">' + '<span ng-show="following" class="label label-info">Following</span>' + '<button class="btn btn-info btn-lg" style= "width: 160px" ng-hide="following" rel=6 ng-click="followTeam()">Follow</button>' + '</div>',
      scope: { teamToFollow: '=' },
      controller: 'gfFollowController'
    };
  });
  app.directive('ngReallyClick', function () {
    return {
      restrict: 'A',
      link: function (scope, element, attrs) {
        element.bind('click', function () {
          var message = attrs.ngReallyMessage;
          if (message && confirm(message)) {
            scope.$apply(attrs.ngReallyClick);
          }
        });
      }
    };
  });
}());
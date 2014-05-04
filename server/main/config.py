# -*- coding: utf-8 -*-

import os
try:
  # This part is surrounded in try/except because the this config.py file is
  # also used in the run.py script which is used to compile/minify the client
  # side files (*.less, *.coffee, *.js) and is not aware of the GAE
  import model
  from datetime import datetime
  CONFIG_DB = model.Config.get_master_db()
  SECRET_KEY = CONFIG_DB.flask_secret_key.encode('ascii')
  CURRENT_VERSION_ID = os.environ.get('CURRENT_VERSION_ID')
  CURRENT_VERSION_NAME = CURRENT_VERSION_ID.split('.')[0]
  CURRENT_VERSION_TIMESTAMP = long(CURRENT_VERSION_ID.split('.')[1]) >> 28
  CURRENT_VERSION_DATE = datetime.fromtimestamp(CURRENT_VERSION_TIMESTAMP)
except:
  pass

PRODUCTION = os.environ.get('SERVER_SOFTWARE', '').startswith('Google App Engine')
DEVELOPMENT = not PRODUCTION
DEBUG = DEVELOPMENT

DEFAULT_DB_LIMIT = 64

################################################################################
# Client modules, also used by the run.py script.
################################################################################
STYLES = [
    'src/style/style.less',
    'src/style/gf-style.less',
    'src/style/external.less',
    'src/style/theme.less',
    'src/style/widgets.less',

  ]

SCRIPTS_MODULES = [
    'libs',
    #'scripts',
    'landing',
    'gf',
    'common',
    'others',
    #'angular',
    #'angular-route',
    #'angular-sanitize',
    #'ui_bootstrap',
    'ui-view',
    #'routemediator'
  ]

SCRIPTS = {
    'libs': [
        'src/lib/jquery.js',
        'src/lib/nprogress.js',
        'src/lib/moment.js',
        'src/lib/bootstrap/js/alert.js',
        'src/lib/bootstrap/js/button.js',
        'src/lib/bootstrap/js/collapse.js',
        'src/lib/bootstrap/js/dropdown.js',
        'src/lib/bootstrap/js/tooltip.js',
        'src/lib/bootstrap/js/transition.js',
        'src/lib/bootstrap/js/tab.js',
        'src/lib/bootstrap/js/scrollspy.js',
        'src/lib/bootstrap/js/popover.js',
        'src/lib/bootstrap/js/modal.js',
        'src/lib/bootstrap/js/carousel.js',
        'src/lib/bootstrap/js/affix.js',
      ],
    'landing':[
        'landing/js/jquery.magnific-popup.min.js',
        'landing/js/main.js',
        'landing/js/polyfills.js',
        'landing/js/validation.js',
    ],
    #'scripts': [
    #    'src/script/common/util.coffee',
    #    'src/script/common/service.coffee',
    #    'src/script/site/app-ready.coffee',
    #    'src/script/site/profile.coffee',
    #    'src/script/site/admin.coffee',
    #],
    'angular':[
        "scripts/angular.min.js",
        "scripts/angular-sanitize.min.js",
        "scripts/angular-route.min.js",
        "scripts/angular-animate.min.js",
        "scripts/angular-cache.min.js",
        "scripts/angular-resource.min.js",
        "scripts/bower_components/angular-touch/angular-touch.min.js",
        "scripts/restangular.min.js",
        "scripts/bower_components/ngprogress/build/ngProgress.min.js"
    ],
    'ui_bootstrap':[
        "scripts/ui-bootstrap-tpls-0.7.0.min.js"
    ],
    'ui-view':[
        "scripts/spin.min.js",
        "scripts/toastr.min.js",

    ],

    'others':[
        "scripts/lodash.min.js",
        "scripts/jquery.prettyPhoto.js",
        "scripts/bootstrap-switch.min.js",
        "scripts/moment.min.js",
        "scripts/q.min.js",
    ],
    'common':[
        "app-ready/common/common.js",
        "app-ready/common/logger.js",
        "app-ready/common/spinner.js",
        "app-ready/common/bootstrap/bootstrap.dialog.js",
    ],
    #'routemediator':[
    #
    #],
    'gf':[
        "app-ready/app.js",
        "app-ready/config.js",
        "app-ready/config.exceptionHandler.js",
        "app-ready/config.route.js",
        "app-ready/services/datacontext.js",
        "app-ready/services/inhouse.js",
        "app-ready/services/directives.js",
        "app-ready/services/entityManagerFactory.js",
        "app-ready/services/gf_datacontext.js",
        "app-ready/services/routemediator.js",

        "app-ready/dashboard/dashboard.js",
        "app-ready/dashboard/notification.js",
        "app-ready/admin/admin.js",
        "app-ready/admin/create-league.js",
        "app-ready/admin/create-team.js",
        "app-ready/user/topic.js",
        "app-ready/user/single-topic.js",
        "app-ready/user/user-replies.js",
        "app-ready/user/friends.js",
        "app-ready/user/author.js",
        "app-ready/layout/shell.js",
        "app-ready/layout/sidebar.js",
        "app-ready/gf/league.js",
        "app-ready/gf/all_teams.js",
        "app-ready/gf/team.js",
        "app-ready/gf/single-team.js",
        "app-ready/services/google-plus-signin.js",
        #"app-ready/services/facebookPluginDirectives.js"
    ],
    #
  }

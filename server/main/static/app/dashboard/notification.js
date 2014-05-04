(function () {
    'use strict';
    var controllerId = 'notifier';
    angular.module('app').controller(controllerId, ['common', '$location','gfNotifier'
        , notifiers]);
    angular.module('app').service('gfNotifier',['$rootScope',gfNotifier]);

    function gfNotifier($rootScope){
        var notifies = [];

        $rootScope.$on('notification',function(event,data){
            notifies.push(data);
        });
        $rootScope.$on('notification:delete',function(evt,data){
            removeNotices(data);
        })
        function getNotices(){
            return notifies;
        }
        function removeNotices($index){
            notifies.splice($index,1);
        }
        function removeAll(){
            notifies = [];
        }
        return {
            notices:getNotices,
            deleteNotices:removeAll,
            removeNotification:removeNotices,

        }
    }

    function notifiers(common,$location,gfNotifier) {
        var getLogFn = common.logger.getLogFn;
        var log = getLogFn(controllerId);
        var logError = getLogFn(controllerId, 'error');

        var nf = this;
        nf.navigate = navigate;
        nf.notifications = gfNotifier.notices;
        nf.clear = gfNotifier.deleteNotices;
        nf.deleteNotice = gfNotifier.removeNotification;

        function navigate(link,$index){
            $location.path(link);
            gfNotifier.removeNotification($index);
        }


        activate();


        function activate() {
            var promises = [

            ];
            common.activateController(promises, controllerId)
                .then(function () {

                });
        }

    }
})();
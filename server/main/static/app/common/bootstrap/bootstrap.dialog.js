(function () {
    'use strict';

    var bootstrapModule = angular.module('common.bootstrap', ['ui.bootstrap']);

    bootstrapModule.factory('bootstrap.dialog', ['$modal', '$templateCache', modalDialog]);

    function modalDialog($modal, $templateCache) {
        var service = {
            deleteDialog: deleteDialog,
            confirmationDialog: confirmationDialog
        };

//        $templateCache.put('/dialogs/whatsyourname.html',
//            '<div class="modal"><div class="modal-dialog">'+
//                '<div class="modal-content">'+
//                '<div class="modal-header">'+
//                '<h4 class="modal-title"><span class="glyphicon glyphicon-star">'+
//                '</span> User\'s Name</h4></div><div class="modal-body">'+
//                '<ng-form name="nameDialog" novalidate role="form"><div class="form-group input-group-lg" ng-class="{true: \'has-error\'}[nameDialog.username.$dirty && nameDialog.username.$invalid]"><label class="control-label" for="username">Name:</label><input type="text" class="form-control" name="username" id="username" ng-model="user.name" ng-keyup="hitEnter($event)" required><span class="help-block">Enter your full name, first &amp; last.</span></div></ng-form></div><div class="modal-footer"><button type="button" class="btn btn-default" ng-click="cancel()">Cancel</button><button type="button" class="btn btn-primary" ng-click="save()" ng-disabled="(nameDialog.$dirty && nameDialog.$invalid) || nameDialog.$pristine">Save</button></div></div></div></div>');
//    )

        $templateCache.put('modalDialog.tpl.html',
            '<div class="modal">'+
                '<div class="modal-dialog">'+
                    '<div class="modal-content">' +
                    '    <div class="modal-header">' +
                    '        <button type="button" class="close" data-dismiss="modal" aria-hidden="true" data-ng-click="cancel()">&times;</button>' +
                    '        <h3 class="modal-title">{{title}}</h3>' +
                    '    </div>' +
                    '    <div class="modal-body">' +
                    '        <p>{{message}}</p>' +
                    '    </div>' +
                    '    <div class="modal-footer">' +
                    '        <button class="btn btn-primary" data-ng-click="ok()">{{okText}}</button>' +
                    '        <button class="btn btn-info" data-ng-click="cancel()">{{cancelText}}</button>' +
                    '    </div>' +
                    '</div>'+
                '</div>'+
            '</div>');

        return service;

        function deleteDialog(itemName) {
            var title = 'Confirm Delete';
            itemName = itemName || 'item';
            var msg = 'Delete ' + itemName + '?';

            return confirmationDialog(title, msg);
        }

        function confirmationDialog(title, msg, okText, cancelText) {

            var modalOptions = {
                templateUrl: 'modalDialog.tpl.html',
                controller: ModalInstance,
                keyboard: true,
                resolve: {
                    options: function () {
                        return {
                            title: title,
                            message: msg,
                            okText: okText,
                            cancelText: cancelText
                        };
                    }
                }
            };

            return $modal.open(modalOptions).result;
        }
    }

    var ModalInstance = ['$scope', '$modalInstance', 'options',
        function ($scope, $modalInstance, options) {
            $scope.title = options.title || 'Title';
            $scope.message = options.message || '';
            $scope.okText = options.okText || 'OK';
            $scope.cancelText = options.cancelText || 'Cancel';
            $scope.ok = function () {
                $modalInstance.close('ok');
            };
            $scope.cancel = function () {
                $modalInstance.dismiss('cancel');
            };
        }];
})();
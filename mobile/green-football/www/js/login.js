angular.module('starter.login', ['openfb'])
  .factory('GFService',function(OpenFB,$q,$window,$http){
    return{
      getUser:function(){
        var deferred = $q.defer();
        OpenFB.get('/me').success(function (user) {
          console
          deferred.resolve(user);
        });
        return deferred.promise;
      },
      getToken:function(user){
        var defer = $q.defer;
        $http.post('',user).success(function (data, status, headers, config) {
          $window.sessionStorage.token = data.token;
          $scope.message = 'Welcome';
        })
          .error(function (data, status, headers, config) {
            // Erase the token if the user fails to log in
            delete $window.sessionStorage.token;

          })
      }
    }
  })

.controller('LoginCtrl', function ($scope, $location, OpenFB) {

  $scope.facebookLogin = function () {

    OpenFB.login('email,read_stream,publish_stream').then(
      function () {
        $location.path('/app/person/me/feed');
      },
      function () {
        alert('OpenFB login failed');
      });
  };

})
(function () {
    'use strict';
    var serviceId = 'gfResource';
    angular.module('app').factory(serviceId,
        ['$http', 'Conf', gfResource]);

    function gfResource($http,Conf){

        return function(collectionName){
            var collectionUrl = Conf.apiBase+collectionName;

            var Resource = function(data){
                angular.extend(this,data);
            };
            Resource.query = function(params){
                return $http.get(collectionUrl,
                    {params:angular.extend({q:JSON.stringify({} || params)})
                    }).then(function(response){
                        var result = [];
                        angular.forEach(response.data,function(value,key){
                            result[key]= new Resource(value);
                        });
                        return result;
                    });
            };

            Resource.save = function(data){
                return $http.post(collectionUrl,data)
                    .then(function(response){
                        return new Resource(data);
                    });
            };
            Resource.prototype.$save = function(data){
                return Resource.save(this);
            };

            Resource.remove = function(data){
                return $http.delete(collectionUrl)
                    .then(function(response){
                        return new Resource(data);
                    });
            };

            Resource.prototype.$remove = function(data){
                return Resource.remove(this);
            };

            //Other CRUD methods go here
//            Resource.prototype.$id = function(){
//                return getId(this)
//            }

            return Resource;
        }

    }


})();
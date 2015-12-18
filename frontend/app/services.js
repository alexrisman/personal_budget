(function() {
    var DTapi = function($http) {

        var servers = {'local': 'http://127.0.0.1:5000', 'production': 'http://52.11.236.0:8000'};
        var server_url = servers.production;

        var factory = {};
        factory.tweetData = function(params) {
            return $http.get(server_url+'/tweets/'+ params);
        };
        return factory;
    };

    DTapi.$inject = ['$http'];
    angular.module('myApp').factory('DTapi', DTapi);

}());
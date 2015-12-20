(function() {
    var DTapi = function($http) {

        var servers = {'local': 'http://127.0.0.1:5000', 'production': 'http://54.201.129.190:8000'};
        var server_url = servers.local;

        var factory = {};
        factory.countData = function() {
            return $http.get(server_url+'/counters/');
        };
        factory.tweetData = function(params) {
            return $http.get(server_url+'/tweets/'+ params);
        };
        return factory;
    };

    DTapi.$inject = ['$http'];
    angular.module('myApp').factory('DTapi', DTapi);

}());

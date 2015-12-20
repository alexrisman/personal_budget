(function() {

    var vizController = function ($scope, $filter, DTapi) {
        $scope.clicked = {};
        $scope.timeslider = {
        			min: 0,
                    model_min: 0,
                    model_max: 20,
        			max: 20
        		};
        $scope.params = {};

        $scope.data = null;

        $scope.init = function () {
            DTapi.tweetData('0&0')
                .success(function(response){
                    $scope.timeslider.max = response[0];
                    $scope.getCounts();
                    $scope.getTweets();
                });
        };

        $scope.getCounts = function () {
            DTapi.countData()
                .success(function(response){
                    $scope.numtweets = response['tweetcnt'];
                    $scope.numdeals = response['dealcnt'];
                });
        };

        $scope.getTweets = function () {
            DTapi.tweetData(($scope.timeslider.model_min).toString()+'&'+($scope.timeslider.model_max).toString())
                .success(function(response){
                    $scope.tweets = response[1];
                });
        };

        $scope.init();

    };

    vizController.$inject = ['$scope', '$filter', 'DTapi'];
    angular.module('myApp').controller('vizController', vizController);
}());

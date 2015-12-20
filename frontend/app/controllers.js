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
        $scope.stackingOpts = [
            { label: 'Absolute', value: 'normal', axislabel:'Tweets' },
            { label: 'Percentage', value: 'percent', axislabel:'Percent' }
          ];
        $scope.stacking = $scope.stackingOpts[1];

        $scope.data = null;

        $scope.init = function () {
            DTapi.tweetData('0&0')
                .success(function(response){
                    $scope.timeslider.max = response[0];
                    $scope.getTweets();
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

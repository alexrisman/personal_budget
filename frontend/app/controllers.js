(function() {

    var vizController = function ($scope, $filter, DTapi) {
        $scope.clicked = {};
        $scope.timeslider = {
        			min: 1429999200000,
                    model_min: 1429999200000,
                    model_max: 1430046000000,
        			max: 1430046000000
        		};
        $scope.params = {};
        $scope.stackingOpts = [
            { label: 'Absolute', value: 'normal', axislabel:'Tweets' },
            { label: 'Percentage', value: 'percent', axislabel:'Percent' }
          ];
        $scope.stacking = $scope.stackingOpts[1];

        $scope.data = null;

        $scope.init = function () {
            DTapi.tweetData(10)
                .success(function(response){
                    $scope.tweets = response;
                });
        };

        $scope.init();

    };

    vizController.$inject = ['$scope', '$filter', 'DTapi'];
    angular.module('myApp').controller('vizController', vizController);
}());
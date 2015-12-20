(function() {

    var vizController = function ($scope, $filter, DTapi) {
        $scope.clicked = {};
        $scope.timeslider = {
        			min: 0,
                    model_min: 0,
                    model_max: 100,
        			max: 100
        		};
        $scope.params = {};
        $scope.stackingOpts = [
            { label: 'Absolute', value: 'normal', axislabel:'Tweets' },
            { label: 'Percentage', value: 'percent', axislabel:'Percent' }
          ];
        $scope.stacking = $scope.stackingOpts[1];

        $scope.data = null;

        $scope.init = function () {
            DTapi.tweetData(15)
                .success(function(response){
                    $scope.tweets = response;
                });
        };

        $scope.init();

    };

    vizController.$inject = ['$scope', '$filter', 'DTapi'];
    angular.module('myApp').controller('vizController', vizController);
}());

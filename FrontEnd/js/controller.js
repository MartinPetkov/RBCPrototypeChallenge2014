var atmapper = angular.module("ATMapper", ["leaflet-directive"]);

atmapper.controller('ATMapperCtrl', function ($scope, leafletData) {
    $scope.center = {
      lat: 43.7044,
      lng: -79.7331,
      zoom: 12
    };

    $scope.defaults = {
      minZoom: $scope.center.zoom,
      zoomControl: false
    };

    $scope.maxbounds = {
      northEast: {
        lat: 43.81718852149039,
        lng: -79.89189147949219
      },
      southWest: {
        lat: 43.60923380393405,
        lng: -79.5952606201
      }
    };

    $scope.drawing = false;
    $scope.draw_button_name = "Start Drawing";

    $scope.paths = {};

    $scope.paths.draw = {
      color: 'teal',
      weight: 4,
      latlngs: [
        { lat: 0, lng: 0 },
        { lat: 0, lng: 0 },
        { lat: 0, lng: 0 },
        { lat: 0, lng: 0 }
      ]
    };

    leafletData.getMap().then(function(map) {
      var down = false;

      map.on('mousedown', function(e){
        if($scope.drawing) {
          $scope.paths.draw.latlngs[0] = e.latlng;
          $scope.paths.draw.latlngs[1] = e.latlng;
          $scope.paths.draw.latlngs[2] = e.latlng;
          $scope.paths.draw.latlngs[3] = e.latlng;

          down = true;
        }
      });

      map.on('mouseup', function(e){
        if($scope.drawing) {
          down = false;
        }
      });

      map.on('mousemove', function(e){
        if($scope.drawing) {
          if(down) { 
            $scope.paths.draw.latlngs[1] = angular.copy(e.latlng);
            $scope.paths.draw.latlngs[2] = angular.copy(e.latlng);
            $scope.paths.draw.latlngs[3] = angular.copy(e.latlng);

            var c1 = angular.copy($scope.paths.draw.latlngs[0]);
            var c2 = angular.copy($scope.paths.draw.latlngs[1]);
            var delta = { x: (c2.lat - c1.lat)/2.0, y: (c2.lng - c1.lng)/2.0};
            console.log(delta);

            $scope.paths.draw.latlngs[2].lat += delta.y;
            $scope.paths.draw.latlngs[2].lng -= delta.x;

            $scope.paths.draw.latlngs[3].lat -= delta.y;
            $scope.paths.draw.latlngs[3].lng += delta.x;





          }
        }
      });

    });

    $scope.draw = function(){
      $scope.drawing = !$scope.drawing;
      leafletData.getMap().then(function(map) {
        if($scope.drawing){
          map.dragging.disable();
          map.touchZoom.disable();
          map.doubleClickZoom.disable();
          map.scrollWheelZoom.disable();
          map.boxZoom.disable();
          $scope.draw_button_name = "Cancel";

        } else {
          map.dragging.enable();
          map.touchZoom.enable();
          map.doubleClickZoom.enable();
          map.scrollWheelZoom.enable();
          map.boxZoom.enable();
          map.keyboard.enable();
          $scope.draw_button_name = "Start Drawing";

          $scope.paths.draw.latlngs = [
            { lat: 0, lng: 0 },
            { lat: 0, lng: 0 },
            { lat: 0, lng: 0 },
            { lat: 0, lng: 0 }
          ];
        }
      });
    }


    // $scope.paths = {
    //   p1: {
    //     color: '#008000',
    //     weight: 8,
    //     latlngs: [
    //       { lat: $scope.center.lat-0.01, lng: $scope.center.lng+0.01 },
    //       { lat: $scope.center.lat-0.01, lng: $scope.center.lng-0.01 },
    //       { lat: $scope.center.lat+0.01, lng: $scope.center.lng-0.01 },
    //       { lat: $scope.center.lat+0.01, lng: $scope.center.lng+0.01 },
    //       { lat: $scope.center.lat-0.01, lng: $scope.center.lng+0.01 }
    //     ],
    //   }
    // };
});
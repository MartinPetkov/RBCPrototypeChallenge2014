var ULYSSES = angular.module("ULYSSES", ["ngRoute", "leaflet-directive"]);

function create_cord(v){
  return {lat: v.lat, lon: v.lng};
}

Math.seed = function(s) {
    Math.random = function() {
        s = Math.sin(s) * 10000; return s - Math.floor(s);
    }
};

ULYSSES.config(['$httpProvider', function($httpProvider) {
        $httpProvider.defaults.useXDomain = true;
        // delete $httpProvider.defaults.headers.common['X-Requested-With'];
    }
]);

ULYSSES.config(['$routeProvider',
  function($routeProvider) {
    $routeProvider.
      when('/', {
        templateUrl: 'partials/index.html',
        controller: 'IndexCtrl'
      }).
      when('/results', {
        templateUrl: 'partials/results.html',
        controller: 'ResultsCtrl'
      }).
      otherwise({
        redirectTo: '/'
      });
  }
]);

ULYSSES.service('searchService', function($http) {
  var promise = {

  };

  var reset = function(){

  }

  var doSearch = function(data) {
      promise = $http({
        method: 'POST',
        url: 'http://192.168.158.241:1236/ATMapper/clusters/',
        data: data
      });
  }

  var getSearch = function(){
      return promise;
  }

  return {
    doSearch: doSearch,
    getSearch: getSearch
  };

});

ULYSSES.controller('ResultsCtrl', function ($scope, leafletData, searchService) {

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

  $scope.markers = {};
  $scope.loaded = false;
  searchService.getSearch().success(function(data){

    data.clusters.forEach(function(cluster){
      cluster.ATMs.forEach(function(atm){
        var hash = "";
        var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
        Math.seed(cluster.cluster_id);

        for( var i=0; i < 3; i++ )
            hash += possible.charAt(Math.floor(Math.random() * possible.length));


        img = "data:image/gif;base64,R0lGODlhHwAyAKEAAP"+hash+"wAAAP///////yH5BAEKAAIALAAAAAAfADIAAAKwlI8Sy5sPTZszRgay3oDZ03Bi1ljYiHbOc6aolyzuvILBjNey2752Srm9AhJgUDgi7kTH3iaUbCI5UKZ0uKResdijcfrcRsHh4JdcrkYVNPU6izNK0HHtrw5EwPGa2pxvF0MX53cHWKgHqPKx1/ahMGj1WFSHCNEoOfnHQ6S5Kef5mRkq+kSqh2bpSaa6CtbqanrKggQbWts5K7ioS8vbG9MBfCk8LJhrbJMcs8zsWQAAOw=="

        $scope.markers["id_"+String(atm.atm_id)] = {
          lat: atm.lat,
          lng: atm.lon,
          focus: false,
          draggable: false,
          message: atm.address + '<br />' + atm.owner,
          icon: {
            iconUrl: img,
            shadowUrl: '',
            iconSize:     [25, 40],
            shadowSize:   [0, 0],
            iconAnchor:   [12, 40],
            shadowAnchor: [4, 62]
          }
        };
      });
    });

    console.log($scope.markers);

    $scope.loaded = true;
  }).error(function(){
    alert("ERROR");
  });

  // $scope.markers = {
  //   osloMarker: {
  //     lat: 59.91,
  //     lng: 10.75,
  //     message: "I want to travel here!",
  //     focus: true,
  //     draggable: false
  //   }
  // };
});

ULYSSES.controller('IndexCtrl', function ($scope, $location, leafletData, searchService) {
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
  $scope.draw_button_name = "Define Region";

  $scope.paths = {};

  $scope.paths.draw = {
    color: '#408289',
    weight: 4,
    latlngs: [
      { lat: 0, lng: 0 },
      { lat: 0, lng: 0 },
      { lat: 0, lng: 0 },
      { lat: 0, lng: 0 },
      { lat: 0, lng: 0 }
    ],
    mouse_start: { lat: 0, lng: 0 }
  };

  leafletData.getMap().then(function(map) {
    var down = false;

    map.on('mousedown', function(e){
      if($scope.drawing) {
        $scope.paths.draw.mouse_start = e.latlng;
        $scope.paths.draw.latlngs[0] = e.latlng;
        $scope.paths.draw.latlngs[1] = e.latlng;
        $scope.paths.draw.latlngs[2] = e.latlng;
        $scope.paths.draw.latlngs[3] = e.latlng;
        $scope.paths.draw.latlngs[4] = e.latlng;
        down = true;
      }
    });

    map.on('mouseup', function(e){
      if($scope.drawing) {
        down = false;
        var senddata = {
          NE: create_cord($scope.paths.draw.latlngs[0]),
          NW: create_cord($scope.paths.draw.latlngs[1]),
          SW: create_cord($scope.paths.draw.latlngs[3]),
          SE: create_cord($scope.paths.draw.latlngs[2])
        }
        searchService.doSearch(senddata);
        $location.path("/results");
      }
    });

    map.on('mousemove', function(e){
      if($scope.drawing) {
        if(down) { 
          $scope.paths.draw.latlngs[0] = angular.copy($scope.paths.draw.mouse_start);
          $scope.paths.draw.latlngs[1] = angular.copy($scope.paths.draw.mouse_start);
          $scope.paths.draw.latlngs[2] = angular.copy(e.latlng);
          $scope.paths.draw.latlngs[3] = angular.copy(e.latlng);

          var c1 = e.latlng;
          var c2 = $scope.paths.draw.mouse_start;
          var delta = { x: (c2.lat - c1.lat)/2.0, y: (c2.lng - c1.lng)/2.0};

          $scope.paths.draw.latlngs[0].lat += delta.y;
          $scope.paths.draw.latlngs[0].lng -= delta.x;

          $scope.paths.draw.latlngs[1].lat -= delta.y;
          $scope.paths.draw.latlngs[1].lng += delta.x;

          $scope.paths.draw.latlngs[2].lat -= delta.y;
          $scope.paths.draw.latlngs[2].lng += delta.x;

          $scope.paths.draw.latlngs[3].lat += delta.y;
          $scope.paths.draw.latlngs[3].lng -= delta.x;

          $scope.paths.draw.latlngs[4] = $scope.paths.draw.latlngs[0];



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
        $scope.draw_button_name = "Define Region";

        $scope.paths.draw.latlngs = [
          { lat: 0, lng: 0 },
          { lat: 0, lng: 0 },
          { lat: 0, lng: 0 },
          { lat: 0, lng: 0 },
          { lat: 0, lng: 0 }
        ];

        $scope.paths.draw.mouse_start = { lat: 0, lng: 0 };
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
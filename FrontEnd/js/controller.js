var ULYSSES = angular.module("ULYSSES", ["ngRoute", "leaflet-directive"]);

function create_cord(v){
  return {lat: v.lat, lon: v.lng};
}

Math.seed = function(s) {
    Math.random = function() {
        s = Math.sin(s) * 10000; return s - Math.floor(s);
    }
};

function HSVtoRGB(h, s, v) {
    var r, g, b, i, f, p, q, t;
    if (h && s === undefined && v === undefined) {
        s = h.s, v = h.v, h = h.h;
    }
    i = Math.floor(h * 6);
    f = h * 6 - i;
    p = v * (1 - s);
    q = v * (1 - f * s);
    t = v * (1 - (1 - f) * s);
    switch (i % 6) {
        case 0: r = v, g = t, b = p; break;
        case 1: r = q, g = v, b = p; break;
        case 2: r = p, g = v, b = t; break;
        case 3: r = p, g = q, b = v; break;
        case 4: r = t, g = p, b = v; break;
        case 5: r = v, g = p, b = q; break;
    }
    return {
        r: Math.floor(r * 255),
        g: Math.floor(g * 255),
        b: Math.floor(b * 255)
    };
}

function gen_color(seed) {
  Math.seed(seed);
  return HSVtoRGB(Math.random()*360000, Math.random(), 1);
}

function merge_options(obj1,obj2){
    var obj3 = {};
    for (var attrname in obj1) { obj3[attrname] = obj1[attrname]; }
    for (var attrname in obj2) { obj3[attrname] = obj2[attrname]; }
    return obj3;
}

function generate_image(base, colors) {
  var b64 = atob(base).split("");

  b64[13] = String.fromCharCode(colors.r);
  b64[14] = String.fromCharCode(colors.g);
  b64[15] = String.fromCharCode(colors.b);

  return "data:image/gif;base64," + btoa(b64.join(""));
}

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

ULYSSES.service('searchService', function($http,$location) {
  var promise = {
    success: function(){
      $location.path("/");
      return this;
    },
    error: function(){
      $location.path("/");
    }
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

ULYSSES.controller('ResultsCtrl', function ($scope, $timeout, leafletData, searchService) {
  $scope.predicate = '-score';

  $scope.center = {
    lat: 43.7044,
    lng: -79.7331,
    zoom: 12
  };

  $scope.defaults = {
    minZoom: 12,
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
    console.log(data);

    $timeout(function(){
      leafletData.getMap().then(function(map) {
        var r = data.region;
        map.fitBounds([
          [r.NW.lat, r.NW.lon],
          [r.NE.lat, r.NE.lon],
          [r.SE.lat, r.SE.lon],
          [r.SW.lat, r.SW.lon]
        ]);
      });
    }, 500);


    $scope.clusters = data.clusters.sort(function(a,b) {
      if (a.score < b.score)
         return 1;
      if (a.score > b.score)
        return -1;
      return 0;
    });

    data.clusters.forEach(function(cluster, cluster_index, cluster_arry){
      cluster.colors = gen_color(cluster.cluster_id);
      cluster.color = function(){
        var mainstring = "#"
        if(cluster.colors.r < 16) {
          mainstring += "0"; 
        }
        mainstring += cluster.colors.r.toString(16);
        if(cluster.colors.g < 16) {
          mainstring += "0"; 
        }
        mainstring += cluster.colors.g.toString(16);
        if(cluster.colors.b < 16) {
          mainstring += "0"; 
        }
        mainstring += cluster.colors.b.toString(16);

        return mainstring;
      }();


      var pin_img = generate_image("R0lGODlhHwAyAKEAAP///wAAAP///////yH5BAEKAAIALAAAAAAfADIAAAKwlI8Sy5sPTZszRgay3oDZ03Bi1ljYiHbOc6aolyzuvILBjNey2752Srm9AhJgUDgi7kTH3iaUbCI5UKZ0uKResdijcfrcRsHh4JdcrkYVNPU6izNK0HHtrw5EwPGa2pxvF0MX53cHWKgHqPKx1/ahMGj1WFSHCNEoOfnHQ6S5Kef5mRkq+kSqh2bpSaa6CtbqanrKggQbWts5K7ioS8vbG9MBfCk8LJhrbJMcs8zsWQAAOw==", cluster.colors);

      var dotbase = "R0lGODlhHwAdAKEAAP///wAAAP///////yH5BAEKAAIALAAAAAAfAB0AAAJzlI8Sy5sPTZszRgay3oDZ03Bi1ljYiHbOc6aolyzuvILBjNey2752Srm9AhJgUDgi7kTH3iaUbCI5UKZ0uKResdhjtxv8RptDhTHsU0y1E6NkbYVTEVlcNCa3q1h1PQyfd2bi1PXxFkhSY6gmpbhIF7RYAAA7";
      var last = (cluster_index == cluster_arry.length-1);
      var first = (cluster_index == 0);
      if(last && !first){
        dotbase = "R0lGODlhIAAfAKEBAP///wAAAAAAAAAAACH5BAEKAAIALAAAAAAgAB8AAAKElINoy30ZWAI0OTerEoF6fS3I50UjCV4nmqGp1LmaXEZiTK+5rcvt3nMpcDRAUPgoKkkbDnHps92gO9WTapRirstm6FgNwaheMVio/XKL5caZnZ5imfE31GsnS9fMe1L5E8XRZcJXMggnl4MoOLYI1ubUyBX5x3SDYyHmlFkGEWcGwVAAADs=";
      }
      if(first && !last) {
        dotbase = "R0lGODlhIAAfAKECAP///wAAALVPT7VPTyH5BAEKAAIALAAAAAAgAB8AAAJ9lI8Zke1/AgAM2ifp3WpWvi2TBl6ZV5ojmTriuLTuisod/dnGCefuAgwCaR6hkUdMKnHDpTMZE7yez2gESWX+sFQgpJmlWL9cqM8yXY5D5dXa1O6l4u5Sukg8k5n3N4ZnhANy4nVFyPFSiNDkpyCh6Pio19G4+Mg22QBpUAAAOw==";
      }
      var dot_img = generate_image(dotbase, cluster.colors);



      var cluster_message = function(){
        var main_message = "";

        var good_reasons = [];
        var bad_reasons = [];

        cluster.Reasons.forEach(function(reason) {
          //fuck you guys lmao
          var reason_text = reason.reason_text;
          if(reason.alignment == "B") {
            bad_reasons.push(reason.reason_text);
          } else {
            good_reasons.push(reason.reason_text);
          }
        });

        main_message += "<b>Pros</b><br/>";
        main_message += good_reasons.join("<br/>");

        main_message += "<br/>";
        main_message += "<br/>";
        main_message += "<b>Cons</b><br/>";
        main_message += bad_reasons.join("<br/>");

        return main_message;
      }();
      
      $scope.markers["id_"+String(cluster.cluster_id)] = {
        lat: cluster.midpoint_lat,
        lng: cluster.midpoint_lon,
        focus: false,
        draggable: false,
        message: cluster_message,
        bl_group: "clusters",
        icon: {
          iconUrl: dot_img,
          shadowUrl: '',
          iconSize:     [25, 25],
          shadowSize:   [0, 0],
          iconAnchor:   [12, 12],
          shadowAnchor: [4, 62]
        }
      };

      cluster.view = function(){
        $scope.center.lat = cluster.midpoint_lat;
        $scope.center.lng = cluster.midpoint_lon;
        $scope.center.zoom = 16;
        $timeout(function(){
        $scope.markers["id_"+String(cluster.cluster_id)].focus = true;
        }, 30);
      }
      
      cluster.ATMs.forEach(function(atm){
        var message = atm.address + '<br />' + atm.owner + "<br/>";
        message += "Transactions/Month: " + atm.trans_per_month + "<br/>";
        if(atm.owner == "RBC") {
          message = '<img class="pull-right" src="./assets/rbc_smallest.png" />' + message;
        }

        $scope.markers["id_"+String(atm.atm_id)] = {
          lat: atm.lat,
          lng: atm.lon,
          focus: false,
          draggable: false,
          message: message,
          bl_group: "atms",
          icon: {
            iconUrl: pin_img,
            shadowUrl: '',
            iconSize:     [25, 40],
            shadowSize:   [0, 0],
            iconAnchor:   [12, 40],
            shadowAnchor: [4, 62]
          }
        };
      });
    });

    $scope.loaded = true;

    window.dispatchEvent(new Event('resize'));
  }).error(function(){
    alert("ERROR");
  });

});

ULYSSES.controller('IndexCtrl', function ($scope, $location, $timeout, leafletData, searchService) {
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

  $scope.advanced = false;
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

  $scope.advanced_settings ={};

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
        if($scope.advanced){
          senddata = merge_options(senddata, $scope.advanced_settings);
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
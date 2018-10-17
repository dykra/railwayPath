let railwaySize = 1000;
require([
  "esri/views/MapView",
  "esri/Map",
  "esri/widgets/Sketch/SketchViewModel",
  "esri/Graphic",
  "esri/layers/GraphicsLayer",
  "esri/layers/MapImageLayer",
  "esri/layers/FeatureLayer",
  "esri/geometry/Polygon"
], function (
  MapView, Map,
  SketchViewModel, Graphic, GraphicsLayer,
  FeatureLayer, MapImageLayer,
  Polygon
) {

  let editGraphic;

  // m.test();

  // GraphicsLayer to hold graphics created via sketch view model
  const graphicsLayer = new GraphicsLayer({
    id: "tempGraphics"
  });

  let map = new Map({
    basemap: "gray",
    layers: [graphicsLayer]
  });
  console.log(map);

  // map.add(railwayPathLayer);

  // console.log(railwayPathLayer);

  const view = new MapView({
    container: "viewDiv",
    map: map,
    zoom: 3
  });

  const pointSymbol = {
    type: "simple-marker", // autocasts as new SimpleMarkerSymbol()
    style: "square",
    color: "#8A2BE2",
    size: "16px",
    outline: { // autocasts as new SimpleLineSymbol()
      color: [255, 255, 255],
      width: 3
    }
  };

  const polylineSymbol = {
    type: "simple-line", // autocasts as new SimpleLineSymbol()
    color: "#8A2BE2",
    width: "4",
    style: "dash"
  };

  const polygonSymbol = {
    type: "simple-fill", // autocasts as new SimpleFillSymbol()
    color: "rgba(138,43,226, 0.8)",
    style: "solid",
    outline: {
      color: "white",
      width: 1
    }
  };

  view.when(function () {
    // create a new sketch view model
    const sketchViewModel = new SketchViewModel({
      view,
      layer: graphicsLayer,
      pointSymbol,
      polylineSymbol,
      polygonSymbol
    });

    setUpClickHandler();

    // Listen to create-complete event to add a newly created graphic to view
    sketchViewModel.on("create-complete", addGraphic);

    // Listen the sketchViewModel's update-complete and update-cancel events
    sketchViewModel.on("update-complete", updateGraphic);
    sketchViewModel.on("update-cancel", updateGraphic);

    // Listen the sketchViewModel's events to draw polygon around line
    sketchViewModel.on("create-complete", addRailwayPolygon);
    sketchViewModel.on("update-complete", updateRailwayPolygon);
    sketchViewModel.on("update-cancel", updateRailwayPolygon);

    // called when sketchViewModel's create-complete event is fired.
    function addGraphic(event) {
      console.log(event);
      // Create a new graphic and set its geometry to
      // `create-complete` event geometry.
      const graphic = new Graphic({
        geometry: event.geometry,
        symbol: sketchViewModel.graphic.symbol
      });
      graphicsLayer.add(graphic);
    }

    // Runs when sketchViewModel's update-complete or update-cancel
    // events are fired.
    function updateGraphic(event) {
      // Create a new graphic and set its geometry event.geometry
      var graphic = new Graphic({
        geometry: event.geometry,
        symbol: editGraphic.symbol
      });
      graphicsLayer.add(graphic);

      // set the editGraphic to null update is complete or cancelled.
      editGraphic = null;
    }

    // set up logic to handle geometry update and reflect the update on "graphicsLayer"
    function setUpClickHandler() {
      view.on("click", function (event) {
        view.hitTest(event).then(function (response) {
          var results = response.results;
          if (results.length > 0) {
            for (var i = 0; i < results.length; i++) {
              // Check if we're already editing a graphic
              if (!editGraphic && results[i].graphic.layer.id === "tempGraphics") {
                // Save a reference to the graphic we intend to update
                editGraphic = results[i].graphic;

                // Remove the graphic from the GraphicsLayer
                // Sketch will handle displaying the graphic while being updated
                graphicsLayer.remove(editGraphic);
                sketchViewModel.update(editGraphic);
                break;
              }
            }
          }
        });
      });
    }

    // activate the sketch to create a point
    var drawPointButton = document.getElementById("pointButton");
    drawPointButton.onclick = function () {
      // set the sketch to create a point geometry
      sketchViewModel.create("point");
      setActiveButton(this);
    };

    // activate the sketch to create a polyline
    var drawLineButton = document.getElementById("polylineButton");
    drawLineButton.onclick = function () {
      // set the sketch to create a polyline geometry
      sketchViewModel.create("polyline");
      setActiveButton(this);
    };

    // activate the sketch to create a polygon
    var drawPolygonButton = document.getElementById("polygonButton");
    drawPolygonButton.onclick = function () {
      // set the sketch to create a polygon geometry
      console.log(sketchViewModel.create("polygon"));
      setActiveButton(this);
    };

    // activate the sketch to create a rectangle
    var drawRectangleButton = document.getElementById(
      "rectangleButton");
    drawRectangleButton.onclick = function () {
      // set the sketch to create a polygon geometry
      sketchViewModel.create("rectangle");
      setActiveButton(this);
    };

    // activate the sketch to create a circle
    var drawCircleButton = document.getElementById("circleButton");
    drawCircleButton.onclick = function () {
      // set the sketch to create a polygon geometry
      sketchViewModel.create("circle");
      setActiveButton(this);
    };

    // reset button
    document.getElementById("resetBtn").onclick = function () {
      sketchViewModel.reset();
      graphicsLayer.removeAll();
      setActiveButton();
    };

    function setActiveButton(selectedButton) {
      // focus the view to activate keyboard shortcuts for sketching
      view.focus();
      var elements = document.getElementsByClassName("active");
      for (var i = 0; i < elements.length; i++) {
        elements[i].classList.remove("active");
      }
      if (selectedButton) {
        selectedButton.classList.add("active");
      }
    }

    /**
     * RLWGeneratePolygon
     */
    function addRailwayPolygon(event){
      // console.log(event.geometry);
      // console.log(sketchViewModel.graphic.symbol);
      // console.log(sketchViewModel);
      const ring = [getPolygonPointsFromPolylinePoints(event.geometry.paths[0])];
      const polygon = new Polygon({
        hasZ: true,
        hasM: true,
        rings: ring,
        spatialReference: { wkid: 102100 }
      });
      const graphic = new Graphic({
        geometry: polygon,
        symbol: polygonSymbol
      });
      graphicsLayer.add(graphic);

    }

    function updateRailwayPolygon(event){

    }

    function getPolygonPointsFromPolylinePoints(points){
      if(points.length<2){
        return null;
      }
      let rings = [];
      for(let i=0;i<2*points.length+1;i++){
        rings.push([]);
      }
      for(let i=0;i<points.length;i++){
        let polygonPoints;
        if(i===0){
          polygonPoints = getEdgePolygonPoints(points[i],points[i+1],points[i],railwaySize);
          rings[2*points.length]=polygonPoints.first;
          rings[1]=polygonPoints.second;
          rings[0]=polygonPoints.first;
          continue;
        } else
        if(i===points.length-1){
          polygonPoints = getEdgePolygonPoints(points[i-1],points[i],points[i],railwaySize);
        } else {
          polygonPoints = getCenterPolygonPoints(points[i-1], points[i], points[i+1], railwaySize);
        }
        rings[1+i]=polygonPoints.second;
        rings[2*points.length-i]=polygonPoints.first;
      }
      return rings;
    }

    function getEdgePolygonPoints(firstPoint, secondPoint, edgePoint , distance){
      let scaledVector = scaleVectorToDistance([secondPoint[0]-firstPoint[0],secondPoint[1]-firstPoint[1]],distance);
      let points = {first:[], second:[]};

      points.first=[edgePoint[0] - scaledVector[1],edgePoint[1] + scaledVector[0]];
      points.second=[edgePoint[0] + scaledVector[1],edgePoint[1] - scaledVector[0]];

      return points;
    }

    function getCenterPolygonPoints(A, B, C, distance){
      let vectorBC = [C[0]-B[0],C[1]-B[1]];
      let vectorBA = [A[0]-B[0],A[1]-B[1]];
      let vector = [vectorBA[0]+vectorBC[0],vectorBA[1]+vectorBC[1]];
      let points = {first:[], second:[]};
      let sinusSign = (vectorBC[0]*vectorBA[1]-vectorBC[1]*vectorBA[0]);
      if(sinusSign<0){
        vector[0] = -vector[0];
        vector[1] = -vector[1];
      }
      if(vector[0]===0 && vector[1] ===0){
        points = getEdgePolygonPoints(B,C,distance);
      } else{
        vector = scaleVectorToDistance(vector, distance);
        points.first = [B[0] + vector[0], B[1] +vector[1]];
        points.second = [B[0] - vector[0], B[1] - vector[1]];
      }
      return points;
    }

    function scaleVectorToDistance(vector, distance){
      let vectorLength = Math.sqrt(Math.pow(vector[0],2) + Math.pow(vector[1],2));
      return [vector[0]*distance/vectorLength,vector[1]*distance/vectorLength];
    }


  });
});


function include(url){
  fetch(url)
    .then(
      function(response) {
        if (response.status !== 200) {
          console.log('Function import error. Status Code: ' +
            response.status);
          return;
        }

        // Examine the text in the response
        response.text().then(function(data) {
          return new Function("return " + data)();
        });
      }
    )
    .catch(function(err) {
      console.log('Fetch Error :-S', err);
    });
}

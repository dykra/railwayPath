let railwaySize = 100;
let minimalRadius = 500;
require([
  "esri/views/MapView",
  "esri/Map",
  "esri/widgets/Sketch/SketchViewModel",
  "esri/Graphic",
  "esri/layers/GraphicsLayer",
  "esri/layers/MapImageLayer",
  "esri/layers/FeatureLayer",
  "esri/geometry/Polygon",
  "esri/geometry/Polyline"
], function (
  MapView, Map,
  SketchViewModel, Graphic, GraphicsLayer,
  FeatureLayer, MapImageLayer,
  Polygon, Polyline
) {

  let editGraphic;
  let polygonEditGraphic;
  let polygonStack = [];
  let id = 0;

  // m.test();

  // GraphicsLayer to hold graphics created via sketch view model
  const graphicsLayer = new GraphicsLayer({
    id: "drawGraphic"
  });

  const tempLayer = new GraphicsLayer({
    id: "tempGraphic"
  });

  const errorLayer = new GraphicsLayer({
    id: "errorGraphic"
  });

  let map = new Map({
    basemap: "gray",
    layers: [tempLayer, errorLayer, graphicsLayer]
  });

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


  const polylineErrorSymbol = {
    type: "simple-line", // autocasts as new SimpleLineSymbol()
    color: "#FF0000",
    width: "5",
    style: "solid"
  };

  const polygonSymbol = {
    type: "simple-fill", // autocasts as new SimpleFillSymbol()
    color: "#999900",
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
      // console.log(event);
      // Create a new graphic and set its geometry to
      // `create-complete` event geometry.
      const graphic = new Graphic({
        geometry: event.geometry,
        symbol: sketchViewModel.graphic.symbol,
        graphicId: id++
      });
      polygonEditGraphic = graphic;
      graphicsLayer.add(graphic);
    }

    // Runs when sketchViewModel's update-complete or update-cancel
    // events are fired.
    function updateGraphic(event) {
      // Create a new graphic and set its geometry event.geometry
      var graphic = new Graphic({
        geometry: event.geometry,
        symbol: editGraphic.symbol,
        graphicId: editGraphic.graphicId
      });
      graphicsLayer.add(graphic);
      editGraphic = null
    }

    // set up logic to handle geometry update and reflect the update on "graphicsLayer"
    function setUpClickHandler() {
      view.on("click", function (event) {
        view.hitTest(event).then(function (response) {
          var results = response.results;
          if (results.length > 0) {
            for (var i = 0; i < results.length; i++) {
              // Check if we're already editing a graphic
              if (!editGraphic && results[i].graphic.layer.id === "drawGraphic") {
                // Save a reference to the graphic we intend to update
                editGraphic = results[i].graphic;
                polygonEditGraphic = results[i].graphic;


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
    function addRailwayPolygon(event) {
      // console.log(event.geometry);
      // console.log(sketchViewModel.graphic.symbol);
      // console.log(sketchViewModel);
      if (event.geometry.type !== "polyline") {
        return;
      }
      getImpossibleSegment(event.geometry);
      const ring = [getPolygonPointsFromPolylinePoints(event.geometry.paths[0])];
      const polygon = new Polygon({
        hasZ: true,
        hasM: true,
        rings: ring,
        spatialReference: {wkid: 102100}
      });
      const graphic = new Graphic({
        geometry: polygon,
        symbol: polygonSymbol
      });
      tempLayer.add(graphic);
      polygonStack[polygonEditGraphic.graphicId] = graphic;

    }

    function updateRailwayPolygon(event) {
      if (event.geometry.type !== "polyline") {
        return;
      }
      getImpossibleSegment(event.geometry);
      let oldPolygon = polygonStack[polygonEditGraphic.graphicId];
      // console.log(oldPolygon);
      polygonStack[polygonEditGraphic.graphicId] = null;
      tempLayer.remove(oldPolygon);
      addRailwayPolygon(event);
    }

    function getPolygonPointsFromPolylinePoints(points) {
      if (points.length < 2) {
        return null;
      }
      let rings = [];
      for (let i = 0; i < 2 * points.length + 1; i++) {
        rings.push([]);
      }
      for (let i = 0; i < points.length; i++) {
        let polygonPoints;
        if (i === 0) {
          polygonPoints = getEdgePolygonPoints(points[i], points[i + 1], points[i], railwaySize);
          rings[2 * points.length] = polygonPoints.first;
          rings[1] = polygonPoints.second;
          rings[0] = polygonPoints.first;
          continue;
        } else if (i === points.length - 1) {
          polygonPoints = getEdgePolygonPoints(points[i - 1], points[i], points[i], railwaySize);
        } else {
          polygonPoints = getCenterPolygonPoints(points[i - 1], points[i], points[i + 1], railwaySize);
        }
        rings[1 + i] = polygonPoints.second;
        rings[2 * points.length - i] = polygonPoints.first;
      }
      return rings;
    }

    function getEdgePolygonPoints(firstPoint, secondPoint, edgePoint, distance) {
      let scaledVector = scaleVectorToDistance([secondPoint[0] - firstPoint[0], secondPoint[1] - firstPoint[1]], distance);
      let points = {first: [], second: []};

      points.first = [edgePoint[0] - scaledVector[1], edgePoint[1] + scaledVector[0]];
      points.second = [edgePoint[0] + scaledVector[1], edgePoint[1] - scaledVector[0]];

      return points;
    }

    function getCenterPolygonPoints(A, B, C, distance) {
      let vectorBC = scaleVectorToDistance([C[0] - B[0], C[1] - B[1]], distance);
      let vectorBA = scaleVectorToDistance([A[0] - B[0], A[1] - B[1]], distance);
      let vector = [vectorBA[0] + vectorBC[0], vectorBA[1] + vectorBC[1]];
      let points = {first: [], second: []};
      let sinusSign = (vectorBC[0] * vectorBA[1] - vectorBC[1] * vectorBA[0]);
      if (sinusSign < 0) {
        vector[0] = -vector[0];
        vector[1] = -vector[1];
      }
      if (vector[0] === 0 && vector[1] === 0) {
        points = getEdgePolygonPoints(B, C, B, distance);
      } else {
        vector = scaleVectorToDistance(vector, distance);
        points.first = [B[0] + vector[0], B[1] + vector[1]];
        points.second = [B[0] - vector[0], B[1] - vector[1]];
      }
      return points;
    }

    function scaleVectorToDistance(vector, distance) {
      let vectorLength = Math.sqrt(Math.pow(vector[0], 2) + Math.pow(vector[1], 2));
      return [vector[0] * distance / vectorLength, vector[1] * distance / vectorLength];
    }

    /**
     * RLWValidatePolyline
     *
     *
     *
     *
     *
     */

    function getImpossibleSegment(polyline) {
      errorLayer.removeAll();
      if (polyline.type !== "polyline") {
        return;
      }
      let segment = getSegmentWithInValidRadius(polyline);
      if (segment != null) {


        let graphic = new Graphic({
          geometry: segment,
          symbol: polylineErrorSymbol
        });
        errorLayer.add(graphic);
      }
    }


    // function that checks if the line have good curve radius
    function getSegmentWithInValidRadius(polyline) {
      if (polyline.paths[0].length < 3) {
        return null;
      }

      let paths = polyline.paths[0];
      // console.log(paths);
      for(let i=0;i<paths.length-2;i++){
        const radius = calculateCircuscribedCircleRadius(paths[i],paths[i+1],paths[i+2]);
        console.log(radius);
        if(radius<minimalRadius){
          let points = [paths[i],paths[i+1],paths[i+2]];
          return createPolylineFromPoints(points);
        }
      }
      return null;
    }

    function calculateCircuscribedCircleRadius(A, B, C) {
      let O = calculateCenterOfCircuscribedCircle(A, B, C);

      //TODO: remove debug logging
      // console.log({"name": "A", "x": A[0], "y": A[1], "A": A});
      // console.log({"name": "B", "x": B[0], "y": B[1], "B": B});
      // console.log({"name": "C", "x": C[0], "y": C[1], "C": C});
      // console.log({"name": "O", "x": O[0], "y": O[1], "O": O});
      // console.log(view.spatialReference);
      // return getDistanceFromLatLonInM(A,O);
      return Math.sqrt(Math.pow(A[0] - O[0], 2) + Math.pow(A[1] - O[1], 2));
    }

    // function that calculate center of circle for further validation
    function calculateCenterOfCircuscribedCircle(A, B, C) {
      // I have no idea how to write it more human readable, so in case of bug rewrite whole function
      let point = [];
      // console.log({A:A,B:B,C:C});
      point[0] = (-(A[0] * (A[0] - B[0]) / (2 * (A[1] - B[1])))
        - B[0] * (A[0] - B[0]) / (2 * (A[1] - B[1])) + B[0] * (B[0] - C[0])
        / (2 * (B[1] - C[1])) + C[0] * (B[0] - C[0]) / (2 * (B[1] - C[1]))
        - A[1] / 2 + C[1] / 2) / ((B[0] - C[0]) / (B[1] - C[1]) - (A[0] - B[0]) / (A[1] - B[1]));

      point[1] = (A[0] - B[0]) / (B[1] - A[1]) * (point[0] - (A[0] + B[0]) / 2) + (A[1] + B[1]) / 2;
      return point;
    }


    function createPolylineFromPoints(points) {
      return new Polyline({
        type: "polyline",
        spatialReference: view.spatialReference,
        hasZ: false,
        paths: [points]
      });
    }

    function getSegment(polyline, points = 3, startPoint = 0) {
      const line = polyline.clone();

      let paths = [];

      if (line.paths[0].length < startPoint+points) return line;

      for (let i = startPoint; i <= startPoint+points; i++) {
        paths.push([line.getPoint(0, i)]);
      }

      return createPolylineFromPoints(paths);
    }


  });
});


function include(url) {
  fetch(url)
    .then(
      function (response) {
        if (response.status !== 200) {
          console.log('Function import error. Status Code: ' +
            response.status);
          return;
        }

        // Examine the text in the response
        response.text().then(function (data) {
          return new Function("return " + data)();
        });
      }
    )
    .catch(function (err) {
      console.log('Fetch Error :-S', err);
    });
}

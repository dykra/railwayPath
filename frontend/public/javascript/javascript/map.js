import 'esri/views/MapView';
import 'esri/Map';
import "esri/Map";
import "esri/widgets/Sketch/SketchViewModel";
import "esri/Graphic";
import "esri/layers/GraphicsLayer";
import "dojo/domReady!javascript/map";
import "esri/geometry/Polyline";

test();

let editGraphic;
let minimalRadius = 1000.0;

// GraphicsLayer to hold graphics created via sketch view model
const graphicsLayer = new GraphicsLayer({
  id: "tempGraphics"
});

const map = new Map({
  // basemap: "topo-vector",
  basemap: "dark-gray",
  layers: [graphicsLayer]
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

const polygonSymbol = {
  type: "simple-fill", // autocasts as new SimpleFillSymbol()
  color: "rgba(138,43,226, 0.8)",
  style: "solid",
  outline: {
    color: "white",
    width: 1
  }
};

function createPolylineFromPoints(points) {
  return new Polyline({
    type: "polyline",
    spatialReference: view.spatialReference,
    hasZ: false,
    paths: [points]
  });
}

function getLastSegment(polyline, points = 3) {
  const line = polyline.clone();

  let paths = [];

  if (line.paths[0].length < points) return line;

  for (let i = 1; i <= points; i++) {
    paths.push([line.getPoint(0, line.paths[0].length - i)]);
  }

  return createPolylineFromPoints(paths);
}

// function that calculate center of circle for further validation
function calculateCenterOfCircuscribedCircle(A, B, C) {
  // I have no idea how to write it more human readable, so in case of bug rewrite whole function
  let point = A.clone;
  point.x = (-(A.x * (A.x - B.x) / (2 * (A.y - B.y))) - B.x * (A.x - B.x) / (2 * (A.y - B.y)) + B.x * (B.x - C.x) / (2 * (B.y - C.y)) + C.x * (B.x - C.x) / (2 * (B.y - C.y)) - A.y / 2 + C.y / 2) / ((B.x - C.x) / (B.y - C.y) - (A.x - B.x) / (A.y - B.y));
  point.y = (A.x - B.x) / (B.y - A.y) * (point.x - (A.x + B.x) / 2) + (A.y + B.y) / 2;
  return point;
}

function calculateCircuscribedCircleRadius(A, B, C) {
  let O = calculateCenterOfCircuscribedCircle(A, B, C);

  //TODO: remove debug logging
  console.log({ "name": "A", "x": A.x, "y": A.y, "A": A });
  console.log({ "name": "B", "x": B.x, "y": B.y, "B": B });
  console.log({ "name": "C", "x": C.x, "y": C.y, "C": C });
  console.log({ "name": "O", "x": O.x, "y": O.y, "O": O });
  console.log(view.spatialReference);
  // return getDistanceFromLatLonInM(A,O);
  return Math.sqrt(Math.pow(A.x - O.x, 2) + Math.pow(A.y - O.y, 2));
}

// function that checks if the line have good curve radius
function isRadiusValid(polyline) {
  if (polyline.paths[0].length < 3) {
    return false;
  }

  //get the last segment from the polyline that is being drawn
  let lastSegment = getLastSegment(polyline, 3);

  const A = lastSegment.paths[0][0][0][0];
  const B = lastSegment.paths[0][0][1][0];
  const C = lastSegment.paths[0][0][2][0];

  const radius = calculateCircuscribedCircleRadius(A, B, C);

  // returns true if the line intersects itself, false otherwise
  console.log(radius);
  return radius <= minimalRadius;
}

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

  // called when sketchViewModel's create-complete event is fired.
  function addGraphic(event) {
    // Create a new graphic and set its geometry to
    // `create-complete` event geometry.
    let graphic = new Graphic({
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
    window.sketchModel = sketchViewModel;
    console.log(sketchViewModel);
    setActiveButton(this);
  };

  // activate the sketch to create a polygon
  var drawPolygonButton = document.getElementById("polygonButton");
  drawPolygonButton.onclick = function () {
    // set the sketch to create a polygon geometry
    sketchViewModel.create("polygon");
    setActiveButton(this);
  };

  // activate the sketch to create a rectangle
  var drawRectangleButton = document.getElementById("rectangleButton");
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
});
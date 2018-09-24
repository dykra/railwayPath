require([
  "esri/Map",
  "esri/views/MapView",
  "esri/views/2d/draw/Draw",
  "esri/Graphic",
  "esri/geometry/Polyline",
  "esri/geometry/geometryEngine",

  "dojo/domReady!public/javascript/map"
], function (
  Map, MapView,
  Draw, Graphic,
  Polyline, geometryEngine
) {
  var map = new Map({
    basemap: "gray"
  });

  var view = new MapView({
    container: "viewDiv",
    map: map,
    zoom: 16,
    center: [18.06, 59.34]
  });

  // add the button for the draw tool
  view.ui.add("line-button", "top-left");

  view.when(function (event) {
    var draw = new Draw({
      view: view
    });

    // ********************
    // draw polyline button
    // ********************
    var drawLineButton = document.getElementById("line-button");
    drawLineButton.onclick = function () {
      view.graphics.removeAll();
      enableCreateLine(draw, view);
    }
  });

  function enableCreateLine(draw, view) {
    // creates and returns an instance of PolyLineDrawAction
    // can only draw a line by clicking on the map
    var action = draw.create("polyline", {
      mode: "click"
    });

    // focus the view to activate keyboard shortcuts for sketching
    view.focus();

    // listen to vertex-add event on the polyline draw action
    action.on("vertex-add", updateVertices);

    // listen to vertex-remove event on the polyline draw action
    action.on("vertex-remove", updateVertices);

    // listen to cursor-update event on the polyline draw action
    action.on("cursor-update", createGraphic);

    // listen to draw-complete event on the polyline draw action
    action.on("draw-complete", updateVertices);

  }

  // This function is called from the "vertex-add" and "vertex-remove"
  // events. Checks if the last vertex is making the line intersect itself.
  function updateVertices(event) {
    // create a polyline from returned vertices
    let result = createGraphic(event);

    // if the last vertex is making the line intersects itself,
    // prevent "vertex-add" or "vertex-remove" from firing
    if (result.selfIntersects) {
      event.preventDefault();
    }
  }

  // create a new graphic presenting the polyline that is being drawn on the view
  function createGraphic(event) {
    let vertices = event.vertices;
    view.graphics.removeAll();

    // a graphic representing the polyline that is being drawn
    let graphic = new Graphic({
      geometry: new Polyline({
        paths: vertices,
        spatialReference: view.spatialReference
      }),
      symbol: {
        type: "simple-line", // autocasts as new SimpleFillSymbol
        color: [4, 90, 141],
        width: 4,
        cap: "round",
        join: "round"
      }
    });

    // check the polyline intersects itself.
    let intersectingFeature = getIntersectingFeature(graphic.geometry);

    // Add a new graphic for the intersecting segment.
    if (intersectingFeature) {
      view.graphics.addMany([graphic, intersectingFeature]);
    }
    // Just add the graphic representing the polyline if no intersection
    else {
      view.graphics.add(graphic);
    }

    // return the graphic and intersectingSegment
    return {
      graphic: graphic,
      selfIntersects: intersectingFeature
    }
  }

  // function that checks if the line intersects itself
  function isSelfIntersecting(polyline) {
    if (polyline.paths[0].length < 3) {
      return false
    }
    let line = polyline.clone();

    //get the last segment from the polyline that is being drawn
    let lastSegment = getLastSegment(polyline);
    line.removePoint(0, line.paths[0].length - 1);


    // returns true if the line intersects itself, false otherwise
    return geometryEngine.crosses(lastSegment, line);
  }

  // Checks if the line intersects itself. If yes, changes the last
  // segment's symbol giving a visual feedback to the user.
  function getIntersectingFeature(polyline) {
    window.xd1=polyline;
    window.xd2=geometryEngine;
    if (isSelfIntersecting(polyline)) {
      return new Graphic({
        geometry: getLastSegment(polyline),
        symbol: {
          type: "simple-line", // autocasts as new SimpleLineSymbol
          style: "short-dot",
          width: 3.5,
          color: "yellow"
        }
      });
    }
    return null;
  }

  // Get the last segment of the polyline that is being drawn
  function getLastSegment(polyline) {
    let line = polyline.clone();
    let lastXYPoint = line.getPoint(0, line.paths[0].length - 1);
    let existingLineFinalPoint = line.getPoint(0, line.paths[0].length - 2);

    return new Polyline({
      spatialReference: view.spatialReference,
      hasZ: false,
      paths: [
        [
          [existingLineFinalPoint.x, existingLineFinalPoint.y],
          [lastXYPoint.x, lastXYPoint.y]
        ]
      ]
    });
  }
});
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

  const minimalRadius = 1000.0;


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

  //TODO: refactor
  // function that checks if the line intersects itself
  function isSelfIntersecting(polyline) {
    if (polyline.paths[0].length < 3) {
      return false
    }


    let line = polyline.clone();

    //get the last segment from the polyline that is being drawn
    let lastSegment = getLastSegment(polyline, 3);

    const A = lastSegment.paths[0][0];
    const B = lastSegment.paths[0][1];
    const C = lastSegment.paths[0][2];
    const area = Math.abs(((B.x-A.x)*(C.y-A.y))-((B.y-A.y)*(C.x-A.x)))/2;
    const perimeter = (Math.sqrt(Math.pow(A.x-B.x, 2)+Math.pow(A.y-B.y, 2)))*(Math.sqrt(Math.pow(B.x-C.x, 2)+Math.pow(B.y-C.y, 2)))*(Math.sqrt(Math.pow(C.x-A.x, 2)+Math.pow(C.y-A.y, 2)));
    const radius = perimeter/(4*area);
    console.log({radius,perimeter,area});


    // returns true if the line intersects itself, false otherwise
    return radius<=minimalRadius;
  }

  // Checks if the line intersects itself. If yes, changes the last
  // segment's symbol giving a visual feedback to the user.
  function getIntersectingFeature(polyline) {
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
  function getLastSegment(polyline, points = 3) {
    const line = polyline.clone();

    let paths = [];

    if(line.paths[0].length<points)
      return line;

    for(let i=1;i<=points;i++){
      paths.push(line.getPoint(0, line.paths[0].length-i));
    }

    return {
      type: "polyline",
      spatialReference: view.spatialReference,
      hasZ: false,
      paths: [
        paths
      ]
    };
  }
});

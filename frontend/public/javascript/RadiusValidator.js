import { getLastSegment } from "../utils/PolylineUtilities";
let minimalRadius = 1000.0;

// function that checks if the line have good curve radius
export function isRadiusValid(polyline) {
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

// function that calculate center of circle for further validation
function calculateCenterOfCircuscribedCircle(A, B, C) {
  // I have no idea how to write it more human readable, so in case of bug rewrite whole function
  let point = A.clone;
  point.x = (-(A.x * (A.x - B.x) / (2 * (A.y - B.y))) - B.x * (A.x - B.x) / (2 * (A.y - B.y)) + B.x * (B.x - C.x) / (2 * (B.y - C.y)) + C.x * (B.x - C.x) / (2 * (B.y - C.y)) - A.y / 2 + C.y / 2) / ((B.x - C.x) / (B.y - C.y) - (A.x - B.x) / (A.y - B.y));
  point.y = (A.x - B.x) / (B.y - A.y) * (point.x - (A.x + B.x) / 2) + (A.y + B.y) / 2;
  return point;
}
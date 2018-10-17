
export function createPolylineFromPoints(points) {
  return new Polyline({
    type: "polyline",
    spatialReference: view.spatialReference,
    hasZ: false,
    paths: [points]
  });
}

export function getLastSegment(polyline, points = 3) {
  const line = polyline.clone();

  let paths = [];

  if (line.paths[0].length < points) return line;

  for (let i = 1; i <= points; i++) {
    paths.push([line.getPoint(0, line.paths[0].length - i)]);
  }

  return createPolylineFromPoints(paths);
}
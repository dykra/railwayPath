
export function getImpossibleSegment(polyline) {
  if (polyline.type !== "polyline") {
    return null;
  }
  if (isRadiusValid(polyline)) {
    return new Graphic({
      geometry: getLastSegment(polyline, 2),
      symbol: {
        type: "simple-line",
        style: "short-dot",
        width: 4,
        color: "yellow"
      }
    });
  }
  return null;
}
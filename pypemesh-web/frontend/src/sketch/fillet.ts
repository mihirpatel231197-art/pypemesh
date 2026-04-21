// 2D fillet — blend two lines meeting at a shared point with a tangent arc.
// Returns a polyline approximation that can be treated as sketch geometry
// or fed into extrusion.

export interface FilletResult {
  /** Arc center */
  center: [number, number];
  /** First tangent point (on line from A to corner) */
  t1: [number, number];
  /** Second tangent point (on line from B to corner) */
  t2: [number, number];
  /** Discretised polyline for rendering */
  points: [number, number][];
  /** Arc radius actually used (may be smaller than requested if lines are short) */
  radius: number;
}


/**
 * Fillet the corner at 'corner' between points 'A' and 'B' with given radius.
 * All positions in 2D. Returns tangent points + discretised arc.
 */
export function filletCorner(
  A: [number, number],
  corner: [number, number],
  B: [number, number],
  requestedRadius: number,
  segments = 16,
): FilletResult | null {
  const v1x = A[0] - corner[0], v1y = A[1] - corner[1];
  const v2x = B[0] - corner[0], v2y = B[1] - corner[1];
  const l1 = Math.hypot(v1x, v1y);
  const l2 = Math.hypot(v2x, v2y);
  if (l1 === 0 || l2 === 0) return null;

  const u1x = v1x / l1, u1y = v1y / l1;
  const u2x = v2x / l2, u2y = v2y / l2;

  const cosAngle = u1x * u2x + u1y * u2y;
  const halfAngle = Math.acos(Math.max(-1, Math.min(1, cosAngle))) / 2;
  if (halfAngle < 1e-6 || halfAngle > Math.PI / 2 - 1e-6) return null;

  // Distance from corner to tangent point
  const tanDist = requestedRadius / Math.tan(halfAngle);
  const dist = Math.min(tanDist, l1 * 0.95, l2 * 0.95);
  const radius = dist * Math.tan(halfAngle);

  const t1: [number, number] = [corner[0] + u1x * dist, corner[1] + u1y * dist];
  const t2: [number, number] = [corner[0] + u2x * dist, corner[1] + u2y * dist];

  // Arc center is along the bisector, offset by radius/sin(halfAngle)
  const bx = (u1x + u2x) / 2;
  const by = (u1y + u2y) / 2;
  const bLen = Math.hypot(bx, by);
  if (bLen === 0) return null;
  const bUnit: [number, number] = [bx / bLen, by / bLen];
  const centerDist = radius / Math.sin(halfAngle);
  const center: [number, number] = [
    corner[0] + bUnit[0] * centerDist,
    corner[1] + bUnit[1] * centerDist,
  ];

  // Discretise arc from t1 to t2 around center
  const a1 = Math.atan2(t1[1] - center[1], t1[0] - center[0]);
  const a2 = Math.atan2(t2[1] - center[1], t2[0] - center[0]);
  let sweep = a2 - a1;
  // Take shortest sweep
  while (sweep > Math.PI) sweep -= 2 * Math.PI;
  while (sweep < -Math.PI) sweep += 2 * Math.PI;

  const points: [number, number][] = [];
  for (let i = 0; i <= segments; i++) {
    const theta = a1 + sweep * (i / segments);
    points.push([
      center[0] + radius * Math.cos(theta),
      center[1] + radius * Math.sin(theta),
    ]);
  }

  return { center, t1, t2, points, radius };
}

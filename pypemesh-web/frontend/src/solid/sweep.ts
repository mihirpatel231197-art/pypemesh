// Sweep geometry — follow a centerline path to create pipe solid bodies.
// Uses THREE.TubeGeometry which extrudes a circular cross-section along a curve.
// Works perfectly for pipe-stress centerlines, giving "real pipe" solid visuals.

import * as THREE from "three";


/**
 * Build a sweep geometry following the centerline from 'from' to 'to'.
 * Radius is the pipe outer radius [m].
 */
export function pipeSweep(
  from: [number, number, number],
  to: [number, number, number],
  radius: number,
  segments = 20,
  radialSegments = 16,
): THREE.TubeGeometry {
  const curve = new THREE.LineCurve3(
    new THREE.Vector3(...from),
    new THREE.Vector3(...to),
  );
  return new THREE.TubeGeometry(curve, segments, radius, radialSegments, false);
}


/**
 * Sweep a pipe along a smooth centerline passing through intermediate points.
 * Use THREE.CatmullRomCurve3 for gentle curves — ideal for visualising routed
 * pipe systems with blended elbows.
 */
export function pipeSweepCurve(
  points: [number, number, number][],
  radius: number,
  segments = 64,
  radialSegments = 16,
  closed = false,
): THREE.TubeGeometry {
  const vectors = points.map((p) => new THREE.Vector3(...p));
  const curve = new THREE.CatmullRomCurve3(vectors, closed, "catmullrom", 0.5);
  return new THREE.TubeGeometry(curve, segments, radius, radialSegments, closed);
}


/**
 * Build a sweep along a quarter-arc between two tangent points — for elbow
 * solid visualisation with proper Karman bend radius.
 */
export function elbowSweep(
  center: [number, number, number],
  axis: [number, number, number],   // normal to the bend plane
  startTangent: [number, number, number],
  bendRadius: number,
  radius: number,
  bendAngleRad: number = Math.PI / 2,
  segments = 32,
  radialSegments = 16,
): THREE.TubeGeometry {
  const c = new THREE.Vector3(...center);
  const up = new THREE.Vector3(...axis).normalize();
  const t0 = new THREE.Vector3(...startTangent).normalize();
  const radialDir = new THREE.Vector3().crossVectors(up, t0).normalize().multiplyScalar(bendRadius);

  const points: THREE.Vector3[] = [];
  for (let i = 0; i <= segments; i++) {
    const theta = bendAngleRad * (i / segments);
    const r = new THREE.Vector3().copy(radialDir).applyAxisAngle(up, theta);
    const p = new THREE.Vector3().addVectors(c, r);
    points.push(p);
  }

  const curve = new THREE.CatmullRomCurve3(points);
  return new THREE.TubeGeometry(curve, segments, radius, radialSegments, false);
}

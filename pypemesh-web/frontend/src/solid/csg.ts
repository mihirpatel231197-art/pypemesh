// CSG (Constructive Solid Geometry) operations via three-bvh-csg.
// Union / subtract / intersect between Three.js meshes.

import * as THREE from "three";
import { Brush, Evaluator, ADDITION, SUBTRACTION, INTERSECTION } from "three-bvh-csg";


export type CSGOp = "union" | "subtract" | "intersect";


export function csg(a: THREE.Mesh, b: THREE.Mesh, op: CSGOp): THREE.Mesh {
  const brushA = new Brush(a.geometry, a.material as THREE.Material);
  brushA.position.copy(a.position);
  brushA.rotation.copy(a.rotation);
  brushA.scale.copy(a.scale);
  brushA.updateMatrixWorld();

  const brushB = new Brush(b.geometry, b.material as THREE.Material);
  brushB.position.copy(b.position);
  brushB.rotation.copy(b.rotation);
  brushB.scale.copy(b.scale);
  brushB.updateMatrixWorld();

  const evaluator = new Evaluator();
  const opConst = op === "union" ? ADDITION
                : op === "subtract" ? SUBTRACTION
                : INTERSECTION;

  const result = evaluator.evaluate(brushA, brushB, opConst);
  return result as unknown as THREE.Mesh;
}


/** Convenience: create a primitive solid mesh at a position with optional rotation. */
export function makeBox(
  size: [number, number, number],
  position: [number, number, number] = [0, 0, 0],
  color = "#60a5fa",
): THREE.Mesh {
  const geom = new THREE.BoxGeometry(...size);
  const mat = new THREE.MeshStandardMaterial({ color, metalness: 0.3, roughness: 0.5 });
  const mesh = new THREE.Mesh(geom, mat);
  mesh.position.set(...position);
  return mesh;
}


export function makeCylinder(
  radius: number,
  height: number,
  position: [number, number, number] = [0, 0, 0],
  color = "#60a5fa",
): THREE.Mesh {
  const geom = new THREE.CylinderGeometry(radius, radius, height, 32);
  const mat = new THREE.MeshStandardMaterial({ color, metalness: 0.4, roughness: 0.5 });
  const mesh = new THREE.Mesh(geom, mat);
  mesh.position.set(...position);
  return mesh;
}


export function makeSphere(
  radius: number,
  position: [number, number, number] = [0, 0, 0],
  color = "#60a5fa",
): THREE.Mesh {
  const geom = new THREE.SphereGeometry(radius, 32, 32);
  const mat = new THREE.MeshStandardMaterial({ color, metalness: 0.4, roughness: 0.5 });
  const mesh = new THREE.Mesh(geom, mat);
  mesh.position.set(...position);
  return mesh;
}


export function makeTorus(
  radius: number,
  tube: number,
  position: [number, number, number] = [0, 0, 0],
  color = "#60a5fa",
): THREE.Mesh {
  const geom = new THREE.TorusGeometry(radius, tube, 16, 32);
  const mat = new THREE.MeshStandardMaterial({ color, metalness: 0.4, roughness: 0.5 });
  const mesh = new THREE.Mesh(geom, mat);
  mesh.position.set(...position);
  return mesh;
}

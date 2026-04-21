// Smoke-test the 2D constraint solver and fillet routines.
// Exported as self-check functions callable from the browser console:
//   window.pypemeshTests.runAll()

import { solveSketch, type Constraint, type Point2D } from "./constraints";
import { filletCorner } from "./fillet";


export function test_constraint_distance(): boolean {
  const points: Point2D[] = [
    { id: "A", x: 0, y: 0, fixed: true },
    { id: "B", x: 1, y: 0 },
  ];
  const constraints: Constraint[] = [
    { kind: "fixed", point: "A" },
    { kind: "distance", a: "A", b: "B", value: 5 },
  ];
  const r = solveSketch(points, [], constraints);
  const B = r.points.find((p) => p.id === "B")!;
  const dist = Math.hypot(B.x, B.y);
  return Math.abs(dist - 5) < 1e-5 && r.converged;
}


export function test_constraint_horizontal(): boolean {
  const points: Point2D[] = [
    { id: "A", x: 0, y: 0, fixed: true },
    { id: "B", x: 5, y: 3 },
  ];
  const constraints: Constraint[] = [
    { kind: "fixed", point: "A" },
    { kind: "horizontal", a: "A", b: "B" },
  ];
  const r = solveSketch(points, [], constraints);
  const B = r.points.find((p) => p.id === "B")!;
  return Math.abs(B.y) < 1e-5 && r.converged;
}


export function test_fillet_right_angle(): boolean {
  // Right-angle corner at origin with lines to (1,0) and (0,1), fillet radius 0.2
  const f = filletCorner([1, 0], [0, 0], [0, 1], 0.2);
  if (!f) return false;
  // Tangent points should be at (0.2, 0) and (0, 0.2)
  return Math.abs(f.t1[0] - 0.2) < 1e-3
      && Math.abs(f.t1[1]) < 1e-3
      && Math.abs(f.t2[0]) < 1e-3
      && Math.abs(f.t2[1] - 0.2) < 1e-3;
}


export function runAll(): { passed: number; failed: number; results: Record<string, boolean> } {
  const tests: Record<string, () => boolean> = {
    distance: test_constraint_distance,
    horizontal: test_constraint_horizontal,
    fillet_right_angle: test_fillet_right_angle,
  };
  const results: Record<string, boolean> = {};
  let passed = 0, failed = 0;
  for (const [name, fn] of Object.entries(tests)) {
    try {
      const ok = fn();
      results[name] = ok;
      if (ok) passed++; else failed++;
    } catch {
      results[name] = false; failed++;
    }
  }
  return { passed, failed, results };
}


// Expose to the window for browser-console debugging
if (typeof window !== "undefined") {
  (window as any).pypemeshTests = { runAll, test_constraint_distance, test_constraint_horizontal, test_fillet_right_angle };
}

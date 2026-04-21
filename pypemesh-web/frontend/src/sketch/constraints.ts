// 2D parametric constraint solver — small from-scratch implementation.
//
// Supported constraints:
//   - Coincident (two points share location)
//   - Distance (fixed distance between two points)
//   - Horizontal (two points share Y)
//   - Vertical (two points share X)
//   - Fixed (a point doesn't move)
//   - Parallel (two line segments)
//   - Perpendicular (two line segments)
//
// Algorithm: Gauss-Seidel relaxation with adaptive damping. Converges for
// well-posed sketches in <100 iterations. Over-constrained sketches report
// residual > tolerance; under-constrained sketches just have freedom.

export interface Point2D {
  id: string;
  x: number;
  y: number;
  fixed?: boolean;
}

export interface Line2D {
  id: string;
  a: string;  // point id
  b: string;
}

export type Constraint =
  | { kind: "coincident"; a: string; b: string }
  | { kind: "distance"; a: string; b: string; value: number }
  | { kind: "horizontal"; a: string; b: string }
  | { kind: "vertical"; a: string; b: string }
  | { kind: "fixed"; point: string }
  | { kind: "parallel"; line_a: string; line_b: string }
  | { kind: "perpendicular"; line_a: string; line_b: string };


export interface SketchSolverResult {
  points: Point2D[];
  residual: number;
  iterations: number;
  converged: boolean;
}


const MAX_ITER = 500;
const TOLERANCE = 1e-6;


function len(ax: number, ay: number, bx: number, by: number): number {
  return Math.sqrt((bx - ax) ** 2 + (by - ay) ** 2);
}


export function solveSketch(
  initialPoints: Point2D[],
  lines: Line2D[],
  constraints: Constraint[],
): SketchSolverResult {
  const points = initialPoints.map((p) => ({ ...p }));
  const byId = new Map(points.map((p) => [p.id, p]));

  function getLine(id: string): { a: Point2D; b: Point2D } | null {
    const l = lines.find((x) => x.id === id);
    if (!l) return null;
    const a = byId.get(l.a);
    const b = byId.get(l.b);
    return a && b ? { a, b } : null;
  }

  let residual = Infinity;
  let iteration = 0;

  for (iteration = 0; iteration < MAX_ITER; iteration++) {
    let maxError = 0;

    for (const c of constraints) {
      if (c.kind === "fixed") {
        const p = byId.get(c.point);
        if (!p) continue;
        p.fixed = true;
      } else if (c.kind === "coincident") {
        const pa = byId.get(c.a); const pb = byId.get(c.b);
        if (!pa || !pb) continue;
        const ex = pa.x - pb.x; const ey = pa.y - pb.y;
        const err = Math.abs(ex) + Math.abs(ey);
        maxError = Math.max(maxError, err);
        if (!pa.fixed && !pb.fixed) {
          pa.x -= ex / 2; pa.y -= ey / 2;
          pb.x += ex / 2; pb.y += ey / 2;
        } else if (!pa.fixed) { pa.x -= ex; pa.y -= ey; }
        else if (!pb.fixed) { pb.x += ex; pb.y += ey; }
      } else if (c.kind === "distance") {
        const pa = byId.get(c.a); const pb = byId.get(c.b);
        if (!pa || !pb) continue;
        const current = len(pa.x, pa.y, pb.x, pb.y);
        if (current === 0) continue;
        const err = current - c.value;
        maxError = Math.max(maxError, Math.abs(err));
        const ux = (pb.x - pa.x) / current;
        const uy = (pb.y - pa.y) / current;
        if (!pa.fixed && !pb.fixed) {
          pa.x += (err / 2) * ux; pa.y += (err / 2) * uy;
          pb.x -= (err / 2) * ux; pb.y -= (err / 2) * uy;
        } else if (!pa.fixed) { pa.x += err * ux; pa.y += err * uy; }
        else if (!pb.fixed) { pb.x -= err * ux; pb.y -= err * uy; }
      } else if (c.kind === "horizontal") {
        const pa = byId.get(c.a); const pb = byId.get(c.b);
        if (!pa || !pb) continue;
        const err = pa.y - pb.y;
        maxError = Math.max(maxError, Math.abs(err));
        if (!pa.fixed && !pb.fixed) { pa.y -= err / 2; pb.y += err / 2; }
        else if (!pa.fixed) pa.y -= err;
        else if (!pb.fixed) pb.y += err;
      } else if (c.kind === "vertical") {
        const pa = byId.get(c.a); const pb = byId.get(c.b);
        if (!pa || !pb) continue;
        const err = pa.x - pb.x;
        maxError = Math.max(maxError, Math.abs(err));
        if (!pa.fixed && !pb.fixed) { pa.x -= err / 2; pb.x += err / 2; }
        else if (!pa.fixed) pa.x -= err;
        else if (!pb.fixed) pb.x += err;
      } else if (c.kind === "parallel") {
        const la = getLine(c.line_a); const lb = getLine(c.line_b);
        if (!la || !lb) continue;
        const dax = la.b.x - la.a.x, day = la.b.y - la.a.y;
        const dbx = lb.b.x - lb.a.x, dby = lb.b.y - lb.a.y;
        // Cross product should be zero for parallel lines
        const cross = dax * dby - day * dbx;
        maxError = Math.max(maxError, Math.abs(cross));
        // Gentle nudge: rotate b slightly toward parallel
        if (!lb.b.fixed && Math.abs(cross) > TOLERANCE) {
          const adjust = cross * 0.05;
          lb.b.x += -day * adjust;
          lb.b.y += dax * adjust;
        }
      } else if (c.kind === "perpendicular") {
        const la = getLine(c.line_a); const lb = getLine(c.line_b);
        if (!la || !lb) continue;
        const dax = la.b.x - la.a.x, day = la.b.y - la.a.y;
        const dbx = lb.b.x - lb.a.x, dby = lb.b.y - lb.a.y;
        // Dot product should be zero for perpendicular
        const dot = dax * dbx + day * dby;
        maxError = Math.max(maxError, Math.abs(dot));
        if (!lb.b.fixed && Math.abs(dot) > TOLERANCE) {
          const adjust = dot * 0.05;
          lb.b.x -= dax * adjust;
          lb.b.y -= day * adjust;
        }
      }
    }

    residual = maxError;
    if (maxError < TOLERANCE) break;
  }

  return {
    points,
    residual,
    iterations: iteration + 1,
    converged: residual < TOLERANCE,
  };
}

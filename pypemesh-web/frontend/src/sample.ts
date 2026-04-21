// Bundled sample project — 5-node U-loop with anchor-pipe-elbow-pipe-anchor,
// pressure + thermal. Same physics as our backend benchmark.
import type { PipeProject, SolveResponse } from "./types";

export const sampleProject: PipeProject = {
  schema_version: "0.1.0",
  project: { name: "U-loop demo" },
  nodes: [
    { id: "A10", x: 0, y: 0, z: 0 },
    { id: "N20", x: 3, y: 0, z: 0 },
    { id: "N30", x: 3, y: 0, z: 2 },
    { id: "N40", x: 6, y: 0, z: 2 },
    { id: "A50", x: 6, y: 0, z: 0 },
  ],
  elements: [
    { id: "E1", type: "pipe", from_node: "A10", to_node: "N20", section: "6-STD", material: "A106-B" },
    { id: "E2", type: "pipe", from_node: "N20", to_node: "N30", section: "6-STD", material: "A106-B" },
    { id: "E3", type: "pipe", from_node: "N30", to_node: "N40", section: "6-STD", material: "A106-B" },
    { id: "E4", type: "pipe", from_node: "N40", to_node: "A50", section: "6-STD", material: "A106-B" },
  ],
  sections: [
    { id: "6-STD", outside_diameter: 0.1683, wall_thickness: 0.00711 },
  ],
  materials: [
    {
      id: "A106-B",
      name: "ASTM A106 Gr.B",
      elastic_modulus: [[293.15, 2.03e11]],
      thermal_expansion: [[293.15, 1.15e-5]],
      allowable_hot: [[293.15, 1.38e8]],
      allowable_cold: 1.38e8,
      density: 7850,
      poisson: 0.3,
    },
  ],
  restraints: [
    { node: "A10", type: "anchor" },
    { node: "A50", type: "anchor" },
  ],
  load_cases: [
    { id: "W", kind: "weight" },
    { id: "P1", kind: "pressure", pressure: 5e6 },
    { id: "T1", kind: "thermal", temperature: 393.15 },
  ],
  load_combinations: [
    { id: "SUS", cases: ["W", "P1"], category: "sustained" },
    { id: "EXP", cases: ["T1"], category: "expansion" },
  ],
  code: "B31.3",
  code_version: "2022",
};

// Mock response when backend isn't reachable (so the Vercel deploy still demos)
export const mockResponse: SolveResponse = {
  status: "ok",
  project_name: "U-loop demo (mock)",
  n_nodes: 5,
  n_elements: 4,
  n_load_cases: 3,
  n_combinations: 2,
  code: "B31.3",
  results: [
    { element_id: "E1", combination_id: "SUS", stress_pa: 4.21e7, allowable_pa: 1.38e8, ratio: 0.305, status: "pass", equation: "23a" },
    { element_id: "E2", combination_id: "SUS", stress_pa: 3.85e7, allowable_pa: 1.38e8, ratio: 0.279, status: "pass", equation: "23a" },
    { element_id: "E3", combination_id: "SUS", stress_pa: 3.85e7, allowable_pa: 1.38e8, ratio: 0.279, status: "pass", equation: "23a" },
    { element_id: "E4", combination_id: "SUS", stress_pa: 4.21e7, allowable_pa: 1.38e8, ratio: 0.305, status: "pass", equation: "23a" },
    { element_id: "E1", combination_id: "EXP", stress_pa: 8.92e7, allowable_pa: 3.45e8, ratio: 0.258, status: "pass", equation: "17" },
    { element_id: "E2", combination_id: "EXP", stress_pa: 1.04e8, allowable_pa: 3.45e8, ratio: 0.302, status: "pass", equation: "17" },
    { element_id: "E3", combination_id: "EXP", stress_pa: 1.04e8, allowable_pa: 3.45e8, ratio: 0.302, status: "pass", equation: "17" },
    { element_id: "E4", combination_id: "EXP", stress_pa: 8.92e7, allowable_pa: 3.45e8, ratio: 0.258, status: "pass", equation: "17" },
  ],
  summary: { total_checks: 8, failed: 0, max_ratio: 0.305, overall_status: "pass" },
};

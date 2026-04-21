// Bundled sample projects — multiple realistic piping models for the demo.
import type { PipeProject, SolveResponse } from "./types";

const STD_SECTION = { id: "6-STD", outside_diameter: 0.1683, wall_thickness: 0.00711 };
const LARGE_SECTION = { id: "10-STD", outside_diameter: 0.273, wall_thickness: 0.00927 };

const A106B = {
  id: "A106-B",
  name: "ASTM A106 Gr.B",
  elastic_modulus: [[293.15, 2.03e11]] as [number, number][],
  thermal_expansion: [[293.15, 1.15e-5]] as [number, number][],
  allowable_hot: [[293.15, 1.38e8]] as [number, number][],
  allowable_cold: 1.38e8,
  density: 7850,
  poisson: 0.3,
};

// 1) U-loop: classic thermal expansion absorber with two anchors
export const uLoopProject: PipeProject = {
  schema_version: "0.1.0",
  project: { name: "U-loop thermal expansion" },
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
  sections: [STD_SECTION],
  materials: [A106B],
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
  code: "B31.3", code_version: "2022",
};

// 2) Cantilever with thermal — single anchor, free thermal growth
export const cantileverProject: PipeProject = {
  schema_version: "0.1.0",
  project: { name: "Cantilever thermal growth" },
  nodes: [
    { id: "A10", x: 0, y: 0, z: 0 },
    { id: "N20", x: 5, y: 0, z: 0 },
  ],
  elements: [
    { id: "E1", type: "pipe", from_node: "A10", to_node: "N20", section: "6-STD", material: "A106-B" },
  ],
  sections: [STD_SECTION],
  materials: [A106B],
  restraints: [{ node: "A10", type: "anchor" }],
  load_cases: [
    { id: "W", kind: "weight" },
    { id: "P1", kind: "pressure", pressure: 5e6 },
    { id: "T1", kind: "thermal", temperature: 423.15 },
  ],
  load_combinations: [
    { id: "SUS", cases: ["W", "P1"], category: "sustained" },
    { id: "EXP", cases: ["T1"], category: "expansion" },
  ],
  code: "B31.3", code_version: "2022",
};

// 3) Pump discharge — vertical pipe with anchors top + bottom
export const pumpDischargeProject: PipeProject = {
  schema_version: "0.1.0",
  project: { name: "Pump discharge riser" },
  nodes: [
    { id: "A10", x: 0, y: 0, z: 0 },
    { id: "N20", x: 0, y: 0, z: 2 },
    { id: "N30", x: 2, y: 0, z: 2 },
    { id: "N40", x: 2, y: 0, z: 4 },
    { id: "A50", x: 2, y: 0, z: 6 },
  ],
  elements: [
    { id: "E1", type: "pipe", from_node: "A10", to_node: "N20", section: "10-STD", material: "A106-B" },
    { id: "E2", type: "pipe", from_node: "N20", to_node: "N30", section: "10-STD", material: "A106-B" },
    { id: "E3", type: "pipe", from_node: "N30", to_node: "N40", section: "6-STD", material: "A106-B" },
    { id: "E4", type: "pipe", from_node: "N40", to_node: "A50", section: "6-STD", material: "A106-B" },
  ],
  sections: [STD_SECTION, LARGE_SECTION],
  materials: [A106B],
  restraints: [
    { node: "A10", type: "anchor" },
    { node: "A50", type: "anchor" },
  ],
  load_cases: [
    { id: "W", kind: "weight" },
    { id: "P1", kind: "pressure", pressure: 8e6 },
    { id: "T1", kind: "thermal", temperature: 363.15 },
  ],
  load_combinations: [
    { id: "SUS", cases: ["W", "P1"], category: "sustained" },
    { id: "EXP", cases: ["T1"], category: "expansion" },
  ],
  code: "B31.3", code_version: "2022",
};

// 4) Long horizontal run with intermediate support
export const longRunProject: PipeProject = {
  schema_version: "0.1.0",
  project: { name: "Long horizontal run" },
  nodes: [
    { id: "A10", x: 0, y: 0, z: 0 },
    { id: "N20", x: 3, y: 0, z: 0 },
    { id: "N30", x: 6, y: 0, z: 0 },
    { id: "N40", x: 9, y: 0, z: 0 },
    { id: "A50", x: 12, y: 0, z: 0 },
  ],
  elements: [
    { id: "E1", type: "pipe", from_node: "A10", to_node: "N20", section: "6-STD", material: "A106-B" },
    { id: "E2", type: "pipe", from_node: "N20", to_node: "N30", section: "6-STD", material: "A106-B" },
    { id: "E3", type: "pipe", from_node: "N30", to_node: "N40", section: "6-STD", material: "A106-B" },
    { id: "E4", type: "pipe", from_node: "N40", to_node: "A50", section: "6-STD", material: "A106-B" },
  ],
  sections: [STD_SECTION],
  materials: [A106B],
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
  code: "B31.3", code_version: "2022",
};

export const SAMPLE_PROJECTS: { id: string; label: string; project: PipeProject }[] = [
  { id: "u-loop", label: "U-loop (thermal expansion absorber)", project: uLoopProject },
  { id: "cantilever", label: "Cantilever (free thermal growth)", project: cantileverProject },
  { id: "pump-discharge", label: "Pump discharge riser", project: pumpDischargeProject },
  { id: "long-run", label: "Long horizontal run", project: longRunProject },
];

export const sampleProject = uLoopProject;  // back-compat default

// Mock response when backend isn't reachable
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

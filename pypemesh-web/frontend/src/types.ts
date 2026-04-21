// pypemesh project schema, mirrors pypemesh_core.solver.model

export type ElementType =
  | "pipe"
  | "elbow"
  | "tee"
  | "reducer"
  | "rigid"
  | "spring"
  | "expansion_joint";

export type RestraintType =
  | "anchor"
  | "guide"
  | "rest"
  | "limit_stop"
  | "spring_hanger"
  | "snubber";

export type LoadKind =
  | "weight"
  | "thermal"
  | "pressure"
  | "wind"
  | "seismic"
  | "user";

export interface PipeNode {
  id: string;
  x: number;
  y: number;
  z: number;
}

export interface PipeElement {
  id: string;
  type: ElementType;
  from_node: string;
  to_node: string;
  section: string;
  material: string;
  bend_radius?: number | null;
  branch_section?: string | null;
}

export interface PipeSection {
  id: string;
  outside_diameter: number;
  wall_thickness: number;
  corrosion_allowance?: number;
  insulation_thickness?: number;
  insulation_density?: number;
}

export interface PipeMaterial {
  id: string;
  name: string;
  elastic_modulus: [number, number][];
  thermal_expansion: [number, number][];
  allowable_hot: [number, number][];
  allowable_cold: number;
  density: number;
  poisson?: number;
}

export interface PipeRestraint {
  node: string;
  type: RestraintType;
  dx?: boolean; dy?: boolean; dz?: boolean;
  rx?: boolean; ry?: boolean; rz?: boolean;
  stiffness?: [number, number, number];
  gap?: number | null;
  friction?: number;
}

export interface PipeLoadCase {
  id: string;
  kind: LoadKind;
  scale?: number;
  temperature?: number | null;
  pressure?: number | null;
  direction?: [number, number, number] | null;
}

export interface PipeLoadCombination {
  id: string;
  cases: string[];
  category: string;
  scales?: number[];
}

export interface PipeProject {
  schema_version: string;
  project: { name: string };
  nodes: PipeNode[];
  elements: PipeElement[];
  sections: PipeSection[];
  materials: PipeMaterial[];
  restraints: PipeRestraint[];
  load_cases: PipeLoadCase[];
  load_combinations: PipeLoadCombination[];
  code: string;
  code_version: string;
}

export interface SolveResult {
  element_id: string;
  combination_id: string;
  stress_pa: number;
  allowable_pa: number;
  ratio: number;
  status: "pass" | "fail";
  equation: string;
}

export interface SolveResponse {
  status: string;
  project_name: string;
  n_nodes: number;
  n_elements: number;
  n_load_cases: number;
  n_combinations: number;
  code: string;
  results: SolveResult[];
  summary: {
    total_checks: number;
    failed: number;
    max_ratio: number;
    overall_status: "pass" | "fail";
  };
}

export interface ModesResponse {
  status: string;
  project_name: string;
  n_modes: number;
  frequencies_hz: number[];
  angular_frequencies: number[];
  periods_s: number[];
}

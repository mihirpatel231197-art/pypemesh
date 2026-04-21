// Dimension + measurement + equipment annotation types.
// These are view-layer data kept alongside the project in the store.

export interface Dimension {
  id: string;
  from_node: string;
  to_node: string;
}

export interface Equipment {
  id: string;
  type: "tank" | "pump" | "vessel" | "valve-box";
  anchor_node: string;       // node where the equipment attaches
  size_x: number;             // bounding box sizes [m]
  size_y: number;
  size_z: number;
  label?: string;
}

export interface SketchState {
  plane: "XY" | "XZ" | "YZ" | null;
  elevation: number;          // offset from origin on the plane's normal
  points: [number, number][]; // 2D points in the sketch plane
}

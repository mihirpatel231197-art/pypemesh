// Central store — Zustand with undo/redo history.
// Every mutation goes through a named action that is recorded in `past` so
// Cmd-Z undoes exactly one user action.

import { create } from "zustand";
import { immer } from "zustand/middleware/immer";
import type {
  PipeElement,
  PipeLoadCase,
  PipeLoadCombination,
  PipeMaterial,
  PipeNode,
  PipeProject,
  PipeRestraint,
  PipeSection,
} from "../types";
import type { Dimension, Equipment, SketchState } from "./annotations";

export type Tool =
  | "select"
  | "add-node"
  | "connect-pipe"
  | "connect-elbow"
  | "add-restraint"
  | "delete"
  | "dimension"
  | "measure"
  | "sketch";

export type Mode = "design" | "analysis";

interface ProjectStore {
  project: PipeProject;
  past: PipeProject[];
  future: PipeProject[];

  // View-layer annotations (not saved to project JSON yet)
  dimensions: Dimension[];
  equipment: Equipment[];
  sketch: SketchState;
  measurement: { from: [number, number, number]; to: [number, number, number] } | null;
  cursorPosition: [number, number, number] | null;

  mode: Mode;
  tool: Tool;
  selectedNodeIds: string[];
  selectedElementIds: string[];
  snapGridSize: number;
  snapToNodes: boolean;
  snapRadius: number;           // meters
  orthoMode: boolean;
  pendingConnectFrom: string | null; // node id while connecting
  pendingDimFrom: string | null;     // node id while placing dimension
  pendingMeasureFrom: [number, number, number] | null;

  // meta actions
  setProject: (p: PipeProject) => void;
  setMode: (m: Mode) => void;
  setTool: (t: Tool) => void;
  setSnapGrid: (n: number) => void;
  toggleOrtho: () => void;
  selectNode: (id: string | null, additive?: boolean) => void;
  selectElement: (id: string | null, additive?: boolean) => void;
  setPendingConnect: (id: string | null) => void;
  clearSelection: () => void;

  // undo/redo
  undo: () => void;
  redo: () => void;

  // mutations (each pushes history)
  addNode: (x: number, y: number, z: number, id?: string) => string;
  updateNode: (id: string, patch: Partial<PipeNode>) => void;
  deleteNode: (id: string) => void;

  addElement: (fromNode: string, toNode: string, type?: PipeElement["type"]) => string;
  updateElement: (id: string, patch: Partial<PipeElement>) => void;
  deleteElement: (id: string) => void;

  addRestraint: (nodeId: string, type?: PipeRestraint["type"]) => void;
  removeRestraint: (nodeId: string) => void;

  addMaterial: (m: PipeMaterial) => void;
  addSection: (s: PipeSection) => void;

  addLoadCase: (lc: PipeLoadCase) => void;
  updateLoadCase: (id: string, patch: Partial<PipeLoadCase>) => void;
  removeLoadCase: (id: string) => void;

  addLoadCombination: (c: PipeLoadCombination) => void;
  updateLoadCombination: (id: string, patch: Partial<PipeLoadCombination>) => void;
  removeLoadCombination: (id: string) => void;

  // Annotation / measurement actions
  addDimension: (fromNode: string, toNode: string) => void;
  removeDimension: (id: string) => void;
  setPendingDimFrom: (id: string | null) => void;

  addEquipment: (type: Equipment["type"], nodeId: string,
                 size?: [number, number, number], label?: string) => void;
  updateEquipment: (id: string, patch: Partial<Equipment>) => void;
  removeEquipment: (id: string) => void;

  setMeasurement: (m: ProjectStore["measurement"]) => void;
  setPendingMeasure: (p: [number, number, number] | null) => void;

  setSketchPlane: (plane: SketchState["plane"]) => void;
  setSketchElevation: (v: number) => void;
  addSketchPoint: (pt: [number, number]) => void;
  clearSketch: () => void;
  extrudeSketch: (direction: [number, number, number], length: number) => void;

  setCursorPosition: (p: [number, number, number] | null) => void;

  toggleSnapNodes: () => void;

  // Convenience: place node by direction+length from a reference
  placeNodeByLength: (fromNode: string | null, direction: "+X" | "-X" | "+Y" | "-Y" | "+Z" | "-Z",
                     length: number, createPipe?: boolean) => string | null;

  // Command-line dispatch (from CommandLine component)
  runCommand: (cmd: string) => { ok: boolean; message: string };
}

const EMPTY_PROJECT: PipeProject = {
  schema_version: "0.1.0",
  project: { name: "Untitled" },
  nodes: [],
  elements: [],
  sections: [],
  materials: [],
  restraints: [],
  load_cases: [{ id: "W", kind: "weight" }],
  load_combinations: [{ id: "SUS", cases: ["W"], category: "sustained" }],
  code: "B31.3",
  code_version: "2022",
};

const HISTORY_LIMIT = 200;

function deepClone<T>(v: T): T {
  // JSON-based clone — handles immer drafts (which structuredClone can't)
  return JSON.parse(JSON.stringify(v)) as T;
}

function pushHistory(past: PipeProject[], project: PipeProject): PipeProject[] {
  const next = [...past, deepClone(project)];
  return next.length > HISTORY_LIMIT ? next.slice(next.length - HISTORY_LIMIT) : next;
}

function nextId(prefix: string, existing: Set<string>): string {
  let i = existing.size + 1;
  let candidate = `${prefix}${i * 10}`;
  while (existing.has(candidate)) {
    i += 1;
    candidate = `${prefix}${i * 10}`;
  }
  return candidate;
}

function snapValue(v: number, grid: number): number {
  if (grid <= 0) return v;
  return Math.round(v / grid) * grid;
}

export const useProjectStore = create<ProjectStore>()(
  immer((set, get) => ({
    project: EMPTY_PROJECT,
    past: [],
    future: [],

    dimensions: [],
    equipment: [],
    sketch: { plane: null, elevation: 0, points: [] },
    measurement: null,
    cursorPosition: null,

    mode: "design",
    tool: "select",
    selectedNodeIds: [],
    selectedElementIds: [],
    snapGridSize: 0.5,
    snapToNodes: true,
    snapRadius: 0.25,
    orthoMode: true,
    pendingConnectFrom: null,
    pendingDimFrom: null,
    pendingMeasureFrom: null,

    setProject: (p) =>
      set((s) => {
        s.past = pushHistory(s.past, s.project);
        s.future = [];
        s.project = p;
        s.selectedNodeIds = [];
        s.selectedElementIds = [];
        s.pendingConnectFrom = null;
      }),

    setMode: (m) => set((s) => { s.mode = m; }),
    setTool: (t) => set((s) => {
      s.tool = t;
      s.pendingConnectFrom = null;
      s.pendingDimFrom = null;
      s.pendingMeasureFrom = null;
    }),
    setSnapGrid: (n) => set((s) => { s.snapGridSize = n; }),
    toggleOrtho: () => set((s) => { s.orthoMode = !s.orthoMode; }),
    toggleSnapNodes: () => set((s) => { s.snapToNodes = !s.snapToNodes; }),
    setCursorPosition: (p) => set((s) => { s.cursorPosition = p; }),
    setPendingDimFrom: (id) => set((s) => { s.pendingDimFrom = id; }),
    setPendingMeasure: (p) => set((s) => { s.pendingMeasureFrom = p; }),
    setMeasurement: (m) => set((s) => { s.measurement = m; }),

    addDimension: (fromNode, toNode) => set((s) => {
      const existing = new Set(s.dimensions.map((d) => d.id));
      let n = 1;
      let id = `D${n}`;
      while (existing.has(id)) { n += 1; id = `D${n}`; }
      s.dimensions.push({ id, from_node: fromNode, to_node: toNode });
    }),
    removeDimension: (id) => set((s) => {
      s.dimensions = s.dimensions.filter((d) => d.id !== id);
    }),

    addEquipment: (type, nodeId, size = [1.2, 1.2, 1.2], label) => set((s) => {
      const existing = new Set(s.equipment.map((e) => e.id));
      let n = 1;
      let id = `EQ${n}`;
      while (existing.has(id)) { n += 1; id = `EQ${n}`; }
      s.equipment.push({
        id, type, anchor_node: nodeId,
        size_x: size[0], size_y: size[1], size_z: size[2],
        label,
      });
    }),
    updateEquipment: (id, patch) => set((s) => {
      const eq = s.equipment.find((e) => e.id === id);
      if (eq) Object.assign(eq, patch);
    }),
    removeEquipment: (id) => set((s) => {
      s.equipment = s.equipment.filter((e) => e.id !== id);
    }),

    setSketchPlane: (plane) => set((s) => { s.sketch.plane = plane; s.sketch.points = []; }),
    setSketchElevation: (v) => set((s) => { s.sketch.elevation = v; }),
    addSketchPoint: (pt) => set((s) => { s.sketch.points.push(pt); }),
    clearSketch: () => set((s) => { s.sketch.points = []; }),
    extrudeSketch: (direction, length) => {
      const sk = get().sketch;
      if (!sk.plane || sk.points.length < 2) return;
      const grid = get().snapGridSize;
      set((s) => {
        s.past = pushHistory(s.past, s.project);
        s.future = [];
        // For each sketch point, create a node at the plane elevation, then
        // connect consecutive nodes with pipes.
        const newIds: string[] = [];
        for (const [a, b] of sk.points) {
          let x = 0, y = 0, z = 0;
          if (sk.plane === "XY") { x = a; y = b; z = sk.elevation; }
          else if (sk.plane === "XZ") { x = a; y = sk.elevation; z = b; }
          else { y = a; z = b; x = sk.elevation; }
          const existing = new Set(s.project.nodes.map((n) => n.id));
          const id = nextId("N", existing);
          s.project.nodes.push({
            id,
            x: snapValue(x, grid),
            y: snapValue(y, grid),
            z: snapValue(z, grid),
          });
          newIds.push(id);
        }
        for (let i = 0; i < newIds.length - 1; i++) {
          const elemExisting = new Set(s.project.elements.map((e) => e.id));
          const eid = nextId("E", elemExisting);
          s.project.elements.push({
            id: eid, type: "pipe",
            from_node: newIds[i], to_node: newIds[i + 1],
            section: s.project.sections[0]?.id ?? "default-section",
            material: s.project.materials[0]?.id ?? "default-material",
            bend_radius: null,
          });
        }
        // Optionally extrude: add extra segment in direction
        if (length > 0 && newIds.length > 0) {
          const lastNode = s.project.nodes.find((n) => n.id === newIds[newIds.length - 1])!;
          const extId = nextId("N", new Set(s.project.nodes.map((n) => n.id)));
          s.project.nodes.push({
            id: extId,
            x: lastNode.x + direction[0] * length,
            y: lastNode.y + direction[1] * length,
            z: lastNode.z + direction[2] * length,
          });
          s.project.elements.push({
            id: nextId("E", new Set(s.project.elements.map((e) => e.id))),
            type: "pipe",
            from_node: newIds[newIds.length - 1], to_node: extId,
            section: s.project.sections[0]?.id ?? "default-section",
            material: s.project.materials[0]?.id ?? "default-material",
            bend_radius: null,
          });
        }
        s.sketch.points = [];
      });
    },

    placeNodeByLength: (fromNode, direction, length, createPipe = true) => {
      let sourceCoord: [number, number, number] = [0, 0, 0];
      const state = get();
      if (fromNode) {
        const n = state.project.nodes.find((x) => x.id === fromNode);
        if (n) sourceCoord = [n.x, n.y, n.z];
        else return null;
      } else if (state.selectedNodeIds.length === 1) {
        const n = state.project.nodes.find((x) => x.id === state.selectedNodeIds[0]);
        if (n) { sourceCoord = [n.x, n.y, n.z]; fromNode = n.id; }
      }
      const delta: [number, number, number] =
        direction === "+X" ? [length, 0, 0] :
        direction === "-X" ? [-length, 0, 0] :
        direction === "+Y" ? [0, length, 0] :
        direction === "-Y" ? [0, -length, 0] :
        direction === "+Z" ? [0, 0, length] : [0, 0, -length];
      const newNodeId = state.addNode(
        sourceCoord[0] + delta[0],
        sourceCoord[1] + delta[1],
        sourceCoord[2] + delta[2],
      );
      if (fromNode && createPipe) {
        state.addElement(fromNode, newNodeId, "pipe");
      }
      return newNodeId;
    },

    runCommand: (cmdline) => {
      const parts = cmdline.trim().split(/\s+/);
      const cmd = (parts[0] || "").toLowerCase();
      const state = get();
      try {
        if (cmd === "node") {
          // node X Y Z
          const [x, y, z] = parts.slice(1).map((p) => parseFloat(p.replace(",", "")));
          if (Number.isNaN(x) || Number.isNaN(y) || Number.isNaN(z)) {
            return { ok: false, message: "Usage: node X Y Z" };
          }
          const id = state.addNode(x, y, z);
          return { ok: true, message: `Created node ${id}` };
        }
        if (cmd === "pipe" || cmd === "elbow" || cmd === "tee") {
          const [a, b] = parts.slice(1);
          if (!a || !b) return { ok: false, message: `Usage: ${cmd} FROM TO` };
          const nodes = new Set(state.project.nodes.map((n) => n.id));
          if (!nodes.has(a) || !nodes.has(b)) {
            return { ok: false, message: `Unknown node(s): ${a}, ${b}` };
          }
          const t: PipeElement["type"] = cmd === "pipe" ? "pipe" : cmd === "elbow" ? "elbow" : "tee";
          const id = state.addElement(a, b, t);
          return { ok: true, message: `Created element ${id}` };
        }
        if (cmd === "anchor") {
          const nid = parts[1];
          if (!nid) return { ok: false, message: "Usage: anchor NODE_ID" };
          state.addRestraint(nid, "anchor");
          return { ok: true, message: `Anchored ${nid}` };
        }
        if (cmd === "dim" || cmd === "dimension") {
          const [a, b] = parts.slice(1);
          if (!a || !b) return { ok: false, message: "Usage: dim FROM TO" };
          state.addDimension(a, b);
          return { ok: true, message: `Dimension ${a} → ${b}` };
        }
        if (cmd === "measure") {
          const [a, b] = parts.slice(1);
          if (!a || !b) return { ok: false, message: "Usage: measure FROM TO" };
          const nA = state.project.nodes.find((n) => n.id === a);
          const nB = state.project.nodes.find((n) => n.id === b);
          if (!nA || !nB) return { ok: false, message: "Unknown node(s)" };
          const d = Math.sqrt(
            (nA.x - nB.x) ** 2 + (nA.y - nB.y) ** 2 + (nA.z - nB.z) ** 2,
          );
          return { ok: true, message: `${a}→${b}: ${d.toFixed(4)} m` };
        }
        if (cmd === "ext" || cmd === "extrude") {
          // extrude DIRECTION LENGTH [from_node]
          const dir = parts[1] as "+X" | "-X" | "+Y" | "-Y" | "+Z" | "-Z";
          const len = parseFloat(parts[2]);
          const from = parts[3] ?? null;
          if (!dir || Number.isNaN(len)) {
            return { ok: false, message: "Usage: extrude +X|-X|+Y|-Y|+Z|-Z LENGTH [from]" };
          }
          const newId = state.placeNodeByLength(from, dir, len);
          return newId
            ? { ok: true, message: `Extruded ${len} m along ${dir} → node ${newId}` }
            : { ok: false, message: "No source node" };
        }
        if (cmd === "delete" || cmd === "del") {
          const id = parts[1];
          if (!id) return { ok: false, message: "Usage: delete ID" };
          const isNode = state.project.nodes.find((n) => n.id === id);
          const isElem = state.project.elements.find((e) => e.id === id);
          if (isNode) { state.deleteNode(id); return { ok: true, message: `Deleted node ${id}` }; }
          if (isElem) { state.deleteElement(id); return { ok: true, message: `Deleted element ${id}` }; }
          return { ok: false, message: `Not found: ${id}` };
        }
        if (cmd === "select") {
          const id = parts[1];
          if (!id) return { ok: false, message: "Usage: select ID" };
          const isNode = state.project.nodes.find((n) => n.id === id);
          const isElem = state.project.elements.find((e) => e.id === id);
          if (isNode) { state.selectNode(id); return { ok: true, message: `Selected node ${id}` }; }
          if (isElem) { state.selectElement(id); return { ok: true, message: `Selected element ${id}` }; }
          return { ok: false, message: `Not found: ${id}` };
        }
        if (cmd === "clear") {
          state.clearSelection();
          return { ok: true, message: "Selection cleared" };
        }
        if (cmd === "help" || cmd === "?") {
          return { ok: true, message:
            "Commands: node X Y Z · pipe|elbow|tee A B · anchor N · dim A B · measure A B · extrude +X 3.0 · delete ID · select ID · clear" };
        }
        return { ok: false, message: `Unknown command: ${cmd}. Type 'help'.` };
      } catch (e) {
        return { ok: false, message: `Error: ${(e as Error).message}` };
      }
    },

    selectNode: (id, additive = false) => set((s) => {
      if (id === null) {
        s.selectedNodeIds = [];
        return;
      }
      if (additive) {
        if (!s.selectedNodeIds.includes(id)) s.selectedNodeIds.push(id);
      } else {
        s.selectedNodeIds = [id];
        s.selectedElementIds = [];
      }
    }),

    selectElement: (id, additive = false) => set((s) => {
      if (id === null) {
        s.selectedElementIds = [];
        return;
      }
      if (additive) {
        if (!s.selectedElementIds.includes(id)) s.selectedElementIds.push(id);
      } else {
        s.selectedElementIds = [id];
        s.selectedNodeIds = [];
      }
    }),

    setPendingConnect: (id) => set((s) => { s.pendingConnectFrom = id; }),
    clearSelection: () => set((s) => {
      s.selectedNodeIds = [];
      s.selectedElementIds = [];
      s.pendingConnectFrom = null;
    }),

    undo: () => set((s) => {
      const prev = s.past.pop();
      if (prev) {
        s.future.push(deepClone(s.project));
        s.project = prev;
        s.selectedNodeIds = [];
        s.selectedElementIds = [];
        s.pendingConnectFrom = null;
      }
    }),

    redo: () => set((s) => {
      const next = s.future.pop();
      if (next) {
        s.past.push(deepClone(s.project));
        s.project = next;
      }
    }),

    addNode: (x, y, z, id) => {
      const existing = new Set(get().project.nodes.map((n) => n.id));
      const nodeId = id ?? nextId("N", existing);
      const grid = get().snapGridSize;
      set((s) => {
        s.past = pushHistory(s.past, s.project);
        s.future = [];
        s.project.nodes.push({
          id: nodeId,
          x: snapValue(x, grid),
          y: snapValue(y, grid),
          z: snapValue(z, grid),
        });
      });
      return nodeId;
    },

    updateNode: (id, patch) => set((s) => {
      s.past = pushHistory(s.past, s.project);
      s.future = [];
      const n = s.project.nodes.find((n) => n.id === id);
      if (n) Object.assign(n, patch);
    }),

    deleteNode: (id) => set((s) => {
      s.past = pushHistory(s.past, s.project);
      s.future = [];
      s.project.nodes = s.project.nodes.filter((n) => n.id !== id);
      // Remove elements that reference this node
      s.project.elements = s.project.elements.filter(
        (e) => e.from_node !== id && e.to_node !== id,
      );
      s.project.restraints = s.project.restraints.filter((r) => r.node !== id);
      s.selectedNodeIds = s.selectedNodeIds.filter((nid) => nid !== id);
    }),

    addElement: (fromNode, toNode, type = "pipe") => {
      const existing = new Set(get().project.elements.map((e) => e.id));
      const id = nextId("E", existing);
      set((s) => {
        s.past = pushHistory(s.past, s.project);
        s.future = [];
        // Default to first section/material if any
        const sectionId = s.project.sections[0]?.id ?? "default-section";
        const materialId = s.project.materials[0]?.id ?? "default-material";
        s.project.elements.push({
          id,
          type,
          from_node: fromNode,
          to_node: toNode,
          section: sectionId,
          material: materialId,
          bend_radius: type === "elbow" ? 0.228 : null,
        });
      });
      return id;
    },

    updateElement: (id, patch) => set((s) => {
      s.past = pushHistory(s.past, s.project);
      s.future = [];
      const e = s.project.elements.find((e) => e.id === id);
      if (e) Object.assign(e, patch);
    }),

    deleteElement: (id) => set((s) => {
      s.past = pushHistory(s.past, s.project);
      s.future = [];
      s.project.elements = s.project.elements.filter((e) => e.id !== id);
      s.selectedElementIds = s.selectedElementIds.filter((eid) => eid !== id);
    }),

    addRestraint: (nodeId, type = "anchor") => set((s) => {
      s.past = pushHistory(s.past, s.project);
      s.future = [];
      // Replace existing restraint at this node, if any
      s.project.restraints = s.project.restraints.filter((r) => r.node !== nodeId);
      s.project.restraints.push({ node: nodeId, type });
    }),

    removeRestraint: (nodeId) => set((s) => {
      s.past = pushHistory(s.past, s.project);
      s.future = [];
      s.project.restraints = s.project.restraints.filter((r) => r.node !== nodeId);
    }),

    addMaterial: (m) => set((s) => {
      s.past = pushHistory(s.past, s.project);
      s.future = [];
      if (!s.project.materials.find((x) => x.id === m.id)) {
        s.project.materials.push(m);
      }
    }),

    addSection: (sec) => set((s) => {
      s.past = pushHistory(s.past, s.project);
      s.future = [];
      if (!s.project.sections.find((x) => x.id === sec.id)) {
        s.project.sections.push(sec);
      }
    }),

    addLoadCase: (lc) => set((s) => {
      s.past = pushHistory(s.past, s.project);
      s.future = [];
      s.project.load_cases.push(lc);
    }),

    updateLoadCase: (id, patch) => set((s) => {
      s.past = pushHistory(s.past, s.project);
      s.future = [];
      const lc = s.project.load_cases.find((l) => l.id === id);
      if (lc) Object.assign(lc, patch);
    }),

    removeLoadCase: (id) => set((s) => {
      s.past = pushHistory(s.past, s.project);
      s.future = [];
      s.project.load_cases = s.project.load_cases.filter((l) => l.id !== id);
      for (const c of s.project.load_combinations) {
        c.cases = c.cases.filter((cid) => cid !== id);
      }
    }),

    addLoadCombination: (c) => set((s) => {
      s.past = pushHistory(s.past, s.project);
      s.future = [];
      s.project.load_combinations.push(c);
    }),

    updateLoadCombination: (id, patch) => set((s) => {
      s.past = pushHistory(s.past, s.project);
      s.future = [];
      const c = s.project.load_combinations.find((x) => x.id === id);
      if (c) Object.assign(c, patch);
    }),

    removeLoadCombination: (id) => set((s) => {
      s.past = pushHistory(s.past, s.project);
      s.future = [];
      s.project.load_combinations = s.project.load_combinations.filter((c) => c.id !== id);
    }),
  })),
);

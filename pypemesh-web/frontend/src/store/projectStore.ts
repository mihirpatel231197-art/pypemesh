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

export type Tool =
  | "select"
  | "add-node"
  | "connect-pipe"
  | "connect-elbow"
  | "add-restraint"
  | "delete";

export type Mode = "design" | "analysis";

interface ProjectStore {
  project: PipeProject;
  past: PipeProject[];
  future: PipeProject[];

  mode: Mode;
  tool: Tool;
  selectedNodeIds: string[];
  selectedElementIds: string[];
  snapGridSize: number;
  orthoMode: boolean;
  pendingConnectFrom: string | null; // node id while connecting

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

    mode: "design",
    tool: "select",
    selectedNodeIds: [],
    selectedElementIds: [],
    snapGridSize: 0.5,
    orthoMode: true,
    pendingConnectFrom: null,

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
    setTool: (t) => set((s) => { s.tool = t; s.pendingConnectFrom = null; }),
    setSnapGrid: (n) => set((s) => { s.snapGridSize = n; }),
    toggleOrtho: () => set((s) => { s.orthoMode = !s.orthoMode; }),

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

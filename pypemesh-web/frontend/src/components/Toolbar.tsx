import { useState } from "react";
import { useProjectStore, type Tool } from "../store/projectStore";
import { NumericNodeDialog, PlaceByLengthDialog, SketchDialog } from "./NumericInput";

const TOOLS: { id: Tool; label: string; hint: string }[] = [
  { id: "select", label: "◈ Select", hint: "Click to select (S)" },
  { id: "add-node", label: "＋ Node", hint: "Click in space to place node (N)" },
  { id: "connect-pipe", label: "― Pipe", hint: "Click node A → click node B (P)" },
  { id: "connect-elbow", label: "⌒ Elbow", hint: "Click node A → click node B (E)" },
  { id: "add-restraint", label: "⊥ Anchor", hint: "Click node to anchor (A)" },
  { id: "dimension", label: "↔ Dim", hint: "Click two nodes to dimension" },
  { id: "measure", label: "📏 Measure", hint: "Click two points for distance" },
  { id: "delete", label: "✕ Delete", hint: "Click node or element to delete (D)" },
];

export function Toolbar() {
  const mode = useProjectStore((s) => s.mode);
  const setMode = useProjectStore((s) => s.setMode);
  const tool = useProjectStore((s) => s.tool);
  const setTool = useProjectStore((s) => s.setTool);
  const undo = useProjectStore((s) => s.undo);
  const redo = useProjectStore((s) => s.redo);
  const past = useProjectStore((s) => s.past.length);
  const future = useProjectStore((s) => s.future.length);
  const snap = useProjectStore((s) => s.snapGridSize);
  const setSnap = useProjectStore((s) => s.setSnapGrid);
  const ortho = useProjectStore((s) => s.orthoMode);
  const toggleOrtho = useProjectStore((s) => s.toggleOrtho);
  const snapNodes = useProjectStore((s) => s.snapToNodes);
  const toggleSnapNodes = useProjectStore((s) => s.toggleSnapNodes);
  const selectedNodeIds = useProjectStore((s) => s.selectedNodeIds);
  const addEquipment = useProjectStore((s) => s.addEquipment);

  const [numericOpen, setNumericOpen] = useState(false);
  const [placeByLengthOpen, setPlaceByLengthOpen] = useState(false);
  const [sketchOpen, setSketchOpen] = useState(false);

  const selectedNode = selectedNodeIds.length === 1 ? selectedNodeIds[0] : null;

  return (
    <>
      <NumericNodeDialog open={numericOpen} onClose={() => setNumericOpen(false)} />
      <PlaceByLengthDialog open={placeByLengthOpen} onClose={() => setPlaceByLengthOpen(false)} fromNode={selectedNode} />
      <SketchDialog open={sketchOpen} onClose={() => setSketchOpen(false)} />

      <div className="toolbar">
        <div className="toolbar-group mode-toggle">
          <button
            className={`mode-btn ${mode === "design" ? "active" : ""}`}
            onClick={() => setMode("design")}
          >✎ Design</button>
          <button
            className={`mode-btn ${mode === "analysis" ? "active" : ""}`}
            onClick={() => setMode("analysis")}
          >⚡ Analyze</button>
        </div>

        {mode === "design" && (
          <>
            <div className="toolbar-group">
              {TOOLS.map((t) => (
                <button
                  key={t.id}
                  className={`tool-btn ${tool === t.id ? "active" : ""}`}
                  onClick={() => setTool(t.id)}
                  title={t.hint}
                >{t.label}</button>
              ))}
            </div>

            <div className="toolbar-group">
              <button className="tool-btn" onClick={() => setNumericOpen(true)} title="Place node numerically (X/Y/Z)">
                ⌨ XYZ
              </button>
              <button className="tool-btn" onClick={() => setPlaceByLengthOpen(true)}
                      title="Place node by direction + length from selected node">
                ⇢ +length
              </button>
              <button className="tool-btn" onClick={() => setSketchOpen(true)} title="2D sketch → pipe route">
                ✏ Sketch
              </button>
            </div>

            <div className="toolbar-group">
              <label className="toolbar-label">Equipment</label>
              <button className="tool-btn"
                      disabled={!selectedNode}
                      onClick={() => selectedNode && addEquipment("tank", selectedNode, [1.5, 2, 1.5], "Tank")}>
                🫙 Tank
              </button>
              <button className="tool-btn"
                      disabled={!selectedNode}
                      onClick={() => selectedNode && addEquipment("pump", selectedNode, [0.8, 0.6, 0.8], "Pump")}>
                ⚙ Pump
              </button>
              <button className="tool-btn"
                      disabled={!selectedNode}
                      onClick={() => selectedNode && addEquipment("vessel", selectedNode, [1, 2.5, 1], "Vessel")}>
                ⚫ Vessel
              </button>
            </div>

            <div className="toolbar-group">
              <label className="toolbar-label">Snap</label>
              <select
                value={snap}
                onChange={(e) => setSnap(parseFloat(e.target.value))}
                className="toolbar-select"
              >
                <option value={0}>off</option>
                <option value={0.1}>0.1 m</option>
                <option value={0.25}>0.25 m</option>
                <option value={0.5}>0.5 m</option>
                <option value={1}>1 m</option>
              </select>
              <button className={`tool-btn ${snapNodes ? "active" : ""}`}
                      onClick={toggleSnapNodes}
                      title="Snap cursor to nearby nodes">
                ⊙ Node snap
              </button>
              <button className={`tool-btn ${ortho ? "active" : ""}`}
                      onClick={toggleOrtho}
                      title="Ortho mode — constrain to X/Y/Z axes">
                ⊕ Ortho
              </button>
            </div>
          </>
        )}

        <div className="toolbar-spacer" />

        <div className="toolbar-group">
          <button className="tool-btn" onClick={undo} disabled={past === 0} title="Undo (Cmd-Z)">
            ↶ {past}
          </button>
          <button className="tool-btn" onClick={redo} disabled={future === 0} title="Redo (Cmd-Shift-Z)">
            ↷ {future}
          </button>
        </div>
      </div>
    </>
  );
}

// Modal dialogs for numeric node placement and place-by-length.

import { useEffect, useRef, useState } from "react";
import { useProjectStore } from "../store/projectStore";


export function NumericNodeDialog({ open, onClose }: { open: boolean; onClose: () => void }) {
  const addNode = useProjectStore((s) => s.addNode);
  const [x, setX] = useState("0");
  const [y, setY] = useState("0");
  const [z, setZ] = useState("0");
  const firstInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (open) setTimeout(() => firstInputRef.current?.focus(), 50);
  }, [open]);

  if (!open) return null;

  function submit(e?: React.FormEvent) {
    e?.preventDefault();
    const nx = parseFloat(x), ny = parseFloat(y), nz = parseFloat(z);
    if (!Number.isNaN(nx) && !Number.isNaN(ny) && !Number.isNaN(nz)) {
      addNode(nx, ny, nz);
      setX("0"); setY("0"); setZ("0");
      onClose();
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <form className="modal-card" onClick={(e) => e.stopPropagation()} onSubmit={submit}>
        <h3>Place node</h3>
        <div className="modal-field">
          <label>X [m]</label>
          <input ref={firstInputRef} value={x} onChange={(e) => setX(e.target.value)} type="number" step="0.1" />
        </div>
        <div className="modal-field">
          <label>Y [m]</label>
          <input value={y} onChange={(e) => setY(e.target.value)} type="number" step="0.1" />
        </div>
        <div className="modal-field">
          <label>Z [m]</label>
          <input value={z} onChange={(e) => setZ(e.target.value)} type="number" step="0.1" />
        </div>
        <div className="modal-actions">
          <button type="button" onClick={onClose}>Cancel</button>
          <button type="submit" className="primary">Place</button>
        </div>
      </form>
    </div>
  );
}


export function PlaceByLengthDialog({ open, onClose, fromNode }: {
  open: boolean; onClose: () => void; fromNode: string | null;
}) {
  const placeNodeByLength = useProjectStore((s) => s.placeNodeByLength);
  const [direction, setDirection] = useState<"+X" | "-X" | "+Y" | "-Y" | "+Z" | "-Z">("+X");
  const [length, setLength] = useState("1.0");
  const [createPipe, setCreatePipe] = useState(true);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (open) setTimeout(() => inputRef.current?.focus(), 50);
  }, [open]);

  if (!open) return null;

  function submit(e?: React.FormEvent) {
    e?.preventDefault();
    const len = parseFloat(length);
    if (!Number.isNaN(len)) {
      placeNodeByLength(fromNode, direction, len, createPipe);
      setLength("1.0");
      onClose();
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <form className="modal-card" onClick={(e) => e.stopPropagation()} onSubmit={submit}>
        <h3>Place by direction + length</h3>
        <p className="modal-hint">
          {fromNode ? `From: ${fromNode}` : "No reference node (will place at origin + offset)"}
        </p>
        <div className="modal-field">
          <label>Direction</label>
          <div className="direction-grid">
            {(["+X", "-X", "+Y", "-Y", "+Z", "-Z"] as const).map((d) => (
              <button
                key={d}
                type="button"
                className={`dir-btn ${direction === d ? "active" : ""}`}
                onClick={() => setDirection(d)}
              >
                {d}
              </button>
            ))}
          </div>
        </div>
        <div className="modal-field">
          <label>Length [m]</label>
          <input ref={inputRef} value={length} onChange={(e) => setLength(e.target.value)} type="number" step="0.1" />
        </div>
        <div className="modal-field">
          <label>
            <input type="checkbox" checked={createPipe} onChange={(e) => setCreatePipe(e.target.checked)} />
            Auto-connect with pipe
          </label>
        </div>
        <div className="modal-actions">
          <button type="button" onClick={onClose}>Cancel</button>
          <button type="submit" className="primary">Place</button>
        </div>
      </form>
    </div>
  );
}


export function SketchDialog({ open, onClose }: { open: boolean; onClose: () => void }) {
  const sketch = useProjectStore((s) => s.sketch);
  const setSketchPlane = useProjectStore((s) => s.setSketchPlane);
  const setSketchElevation = useProjectStore((s) => s.setSketchElevation);
  const clearSketch = useProjectStore((s) => s.clearSketch);
  const extrudeSketch = useProjectStore((s) => s.extrudeSketch);

  const [direction, setDirection] = useState<"+X" | "-X" | "+Y" | "-Y" | "+Z" | "-Z">("+Z");
  const [length, setLength] = useState("0");

  if (!open) return null;

  function finish() {
    const len = parseFloat(length) || 0;
    const dir: [number, number, number] =
      direction === "+X" ? [1, 0, 0] : direction === "-X" ? [-1, 0, 0] :
      direction === "+Y" ? [0, 1, 0] : direction === "-Y" ? [0, -1, 0] :
      direction === "+Z" ? [0, 0, 1] : [0, 0, -1];
    extrudeSketch(dir, len);
    onClose();
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <h3>2D Sketch → Pipe Route</h3>
        <p className="modal-hint">
          Pick a plane, click in the viewport to add points, then extrude.
        </p>
        <div className="modal-field">
          <label>Plane</label>
          <div className="direction-grid">
            {(["XY", "XZ", "YZ"] as const).map((p) => (
              <button
                key={p} type="button"
                className={`dir-btn ${sketch.plane === p ? "active" : ""}`}
                onClick={() => setSketchPlane(p)}
              >
                {p}
              </button>
            ))}
          </div>
        </div>
        <div className="modal-field">
          <label>Elevation [m]</label>
          <input
            type="number" step="0.1"
            value={sketch.elevation}
            onChange={(e) => setSketchElevation(parseFloat(e.target.value) || 0)}
          />
        </div>
        <div className="modal-field">
          <label>Points</label>
          <span className="modal-hint">{sketch.points.length} placed</span>
        </div>
        <div className="modal-field">
          <label>Extrude</label>
          <div className="direction-grid">
            {(["+X", "-X", "+Y", "-Y", "+Z", "-Z"] as const).map((d) => (
              <button
                key={d} type="button"
                className={`dir-btn ${direction === d ? "active" : ""}`}
                onClick={() => setDirection(d)}
              >
                {d}
              </button>
            ))}
          </div>
        </div>
        <div className="modal-field">
          <label>Length [m]</label>
          <input value={length} type="number" step="0.1" onChange={(e) => setLength(e.target.value)} />
        </div>
        <div className="modal-actions">
          <button type="button" onClick={clearSketch}>Clear points</button>
          <button type="button" onClick={onClose}>Cancel</button>
          <button type="button" className="primary" onClick={finish}>Create pipe route</button>
        </div>
      </div>
    </div>
  );
}

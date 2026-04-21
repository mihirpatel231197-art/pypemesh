import { useProjectStore } from "../store/projectStore";

const TOOL_LABEL: Record<string, string> = {
  "select": "Select",
  "add-node": "Add node",
  "connect-pipe": "Connect pipe",
  "connect-elbow": "Connect elbow",
  "add-restraint": "Add anchor",
  "delete": "Delete",
  "dimension": "Dimension",
  "measure": "Measure",
  "sketch": "Sketch",
};

export function StatusBar() {
  const tool = useProjectStore((s) => s.tool);
  const mode = useProjectStore((s) => s.mode);
  const cursor = useProjectStore((s) => s.cursorPosition);
  const snapGrid = useProjectStore((s) => s.snapGridSize);
  const snapNodes = useProjectStore((s) => s.snapToNodes);
  const project = useProjectStore((s) => s.project);
  const selectedNodes = useProjectStore((s) => s.selectedNodeIds);
  const selectedElements = useProjectStore((s) => s.selectedElementIds);
  const measurement = useProjectStore((s) => s.measurement);

  const measureDistance = measurement
    ? Math.sqrt(
        (measurement.from[0] - measurement.to[0]) ** 2 +
        (measurement.from[1] - measurement.to[1]) ** 2 +
        (measurement.from[2] - measurement.to[2]) ** 2,
      )
    : null;

  return (
    <div className="status-bar">
      <div className="sb-section">
        <span className="sb-label">Mode</span>
        <span className="sb-value">{mode}</span>
      </div>
      <div className="sb-section">
        <span className="sb-label">Tool</span>
        <span className="sb-value">{TOOL_LABEL[tool] ?? tool}</span>
      </div>
      <div className="sb-section">
        <span className="sb-label">Cursor</span>
        <span className="sb-value mono">
          {cursor
            ? `X ${cursor[0].toFixed(3)}  Y ${cursor[1].toFixed(3)}  Z ${cursor[2].toFixed(3)} m`
            : "—"}
        </span>
      </div>
      <div className="sb-section">
        <span className="sb-label">Snap</span>
        <span className="sb-value">{snapGrid > 0 ? `${snapGrid} m` : "off"} · nodes {snapNodes ? "on" : "off"}</span>
      </div>
      {measureDistance !== null && (
        <div className="sb-section sb-measure">
          <span className="sb-label">Δ</span>
          <span className="sb-value mono">{measureDistance.toFixed(4)} m</span>
        </div>
      )}
      <div className="sb-spacer" />
      <div className="sb-section">
        <span className="sb-label">Selection</span>
        <span className="sb-value">
          {selectedNodes.length + selectedElements.length > 0
            ? `${selectedNodes.length}N, ${selectedElements.length}E`
            : "—"}
        </span>
      </div>
      <div className="sb-section">
        <span className="sb-label">Model</span>
        <span className="sb-value">
          {project.nodes.length} nodes · {project.elements.length} elements
        </span>
      </div>
    </div>
  );
}

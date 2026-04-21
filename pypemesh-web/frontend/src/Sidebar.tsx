import type { PipeProject, SolveResponse } from "./types";

interface Props {
  project: PipeProject;
  selectedNode: string | null;
  selectedElement: string | null;
  onSelectNode: (id: string) => void;
  onSelectElement: (id: string) => void;
  results: SolveResponse | null;
  resultCombo: string | null;
  onSelectCombo: (id: string | null) => void;
  solving: boolean;
  onSolve: () => void;
}

function fmt(v: number, digits = 3): string {
  if (Math.abs(v) >= 1e6) return (v / 1e6).toFixed(digits) + " MPa";
  if (Math.abs(v) >= 1e3) return (v / 1e3).toFixed(digits) + " kPa";
  return v.toFixed(digits) + " Pa";
}

export function Sidebar({
  project,
  selectedNode,
  selectedElement,
  onSelectNode,
  onSelectElement,
  results,
  resultCombo,
  onSelectCombo,
  solving,
  onSolve,
}: Props) {
  const restraintIndex = Object.fromEntries(project.restraints.map((r) => [r.node, r]));
  const node = selectedNode ? project.nodes.find((n) => n.id === selectedNode) : null;
  const element = selectedElement ? project.elements.find((e) => e.id === selectedElement) : null;

  // Per-combo summary
  const combos = project.load_combinations;

  // Selected element's results across combinations
  const elementResults = results && element
    ? results.results.filter((r) => r.element_id === element.id)
    : [];

  return (
    <aside className="sidebar">
      <section>
        <h3>Project</h3>
        <div className="kv"><span>Name</span><b>{project.project.name}</b></div>
        <div className="kv"><span>Code</span><b>{project.code} {project.code_version}</b></div>
        <div className="kv"><span>Nodes</span><b>{project.nodes.length}</b></div>
        <div className="kv"><span>Elements</span><b>{project.elements.length}</b></div>
        <div className="kv"><span>Combinations</span><b>{combos.length}</b></div>
      </section>

      <section>
        <h3>Run analysis</h3>
        <button className="btn-primary" onClick={onSolve} disabled={solving}>
          {solving ? "Solving…" : "Run B31.3 check"}
        </button>
        {results && (
          <div className="summary">
            <div className={`status-pill ${results.summary.overall_status}`}>
              {results.summary.overall_status.toUpperCase()}
            </div>
            <div className="kv"><span>Checks</span><b>{results.summary.total_checks}</b></div>
            <div className="kv"><span>Failed</span><b>{results.summary.failed}</b></div>
            <div className="kv"><span>Max ratio</span><b>{results.summary.max_ratio.toFixed(3)}</b></div>
          </div>
        )}
      </section>

      {results && combos.length > 0 && (
        <section>
          <h3>Color by combination</h3>
          <div className="combo-buttons">
            <button
              className={`combo-btn ${resultCombo === null ? "active" : ""}`}
              onClick={() => onSelectCombo(null)}
            >
              none
            </button>
            {combos.map((c) => (
              <button
                key={c.id}
                className={`combo-btn ${resultCombo === c.id ? "active" : ""}`}
                onClick={() => onSelectCombo(c.id)}
              >
                {c.id} ({c.category})
              </button>
            ))}
          </div>
        </section>
      )}

      <section>
        <h3>Model tree</h3>
        <div className="tree">
          <div className="tree-group">
            <div className="tree-label">Nodes</div>
            {project.nodes.map((n) => {
              const r = restraintIndex[n.id];
              const cls = `tree-item ${selectedNode === n.id ? "selected" : ""}`;
              return (
                <div key={n.id} className={cls} onClick={() => onSelectNode(n.id)}>
                  <span className={`dot ${r ? "anchor" : "node"}`} />
                  {n.id}
                  {r && <span className="suffix">{r.type}</span>}
                </div>
              );
            })}
          </div>
          <div className="tree-group">
            <div className="tree-label">Elements</div>
            {project.elements.map((e) => (
              <div
                key={e.id}
                className={`tree-item ${selectedElement === e.id ? "selected" : ""}`}
                onClick={() => onSelectElement(e.id)}
              >
                <span className="dot pipe" />
                {e.id}
                <span className="suffix">{e.type} · {e.from_node}→{e.to_node}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {(node || element) && (
        <section>
          <h3>Properties</h3>
          {node && (
            <>
              <div className="kv"><span>Node</span><b>{node.id}</b></div>
              <div className="kv"><span>x</span><b>{node.x.toFixed(3)} m</b></div>
              <div className="kv"><span>y</span><b>{node.y.toFixed(3)} m</b></div>
              <div className="kv"><span>z</span><b>{node.z.toFixed(3)} m</b></div>
              {restraintIndex[node.id] && (
                <div className="kv"><span>Restraint</span><b>{restraintIndex[node.id].type}</b></div>
              )}
            </>
          )}
          {element && (
            <>
              <div className="kv"><span>Element</span><b>{element.id}</b></div>
              <div className="kv"><span>Type</span><b>{element.type}</b></div>
              <div className="kv"><span>From → To</span><b>{element.from_node} → {element.to_node}</b></div>
              <div className="kv"><span>Section</span><b>{element.section}</b></div>
              <div className="kv"><span>Material</span><b>{element.material}</b></div>
              {elementResults.length > 0 && (
                <div className="results-table">
                  <div className="results-header">Code check results</div>
                  {elementResults.map((r) => (
                    <div key={r.combination_id} className="result-row">
                      <div className="result-combo">
                        <b>{r.combination_id}</b>
                        <span className="eq">eq {r.equation}</span>
                      </div>
                      <div className="result-vals">
                        <span>{fmt(r.stress_pa, 1)}</span>
                        <span className="sep">/</span>
                        <span>{fmt(r.allowable_pa, 0)}</span>
                      </div>
                      <div className={`ratio ${r.status}`}>{(r.ratio * 100).toFixed(1)}%</div>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
        </section>
      )}
    </aside>
  );
}

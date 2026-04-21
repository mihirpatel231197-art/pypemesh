import type { PipeProject, SolveResponse } from "./types";

interface Props {
  project: PipeProject;
  results: SolveResponse | null;
}

export function Spreadsheet({ project, results }: Props) {
  const resultIndex: Record<string, { ratio: number; status: string }[]> = {};
  if (results) {
    for (const r of results.results) {
      resultIndex[r.element_id] = resultIndex[r.element_id] ?? [];
      resultIndex[r.element_id].push({ ratio: r.ratio, status: r.status });
    }
  }

  const restraintIndex = new Map(project.restraints.map((r) => [r.node, r]));

  return (
    <div className="spreadsheet">
      <div className="ss-section">
        <h4>Nodes ({project.nodes.length})</h4>
        <table className="ss-table">
          <thead>
            <tr>
              <th>ID</th><th>X [m]</th><th>Y [m]</th><th>Z [m]</th><th>Restraint</th>
            </tr>
          </thead>
          <tbody>
            {project.nodes.map((n) => {
              const r = restraintIndex.get(n.id);
              return (
                <tr key={n.id}>
                  <td className="mono">{n.id}</td>
                  <td className="mono right">{n.x.toFixed(3)}</td>
                  <td className="mono right">{n.y.toFixed(3)}</td>
                  <td className="mono right">{n.z.toFixed(3)}</td>
                  <td>{r ? <span className="badge-r">{r.type}</span> : ""}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="ss-section">
        <h4>Elements ({project.elements.length})</h4>
        <table className="ss-table">
          <thead>
            <tr>
              <th>ID</th><th>Type</th><th>From</th><th>To</th>
              <th>Section</th><th>Material</th>
              <th>Max ratio</th>
            </tr>
          </thead>
          <tbody>
            {project.elements.map((e) => {
              const rs = resultIndex[e.id] ?? [];
              const maxR = rs.length ? Math.max(...rs.map((r) => r.ratio)) : null;
              const hasFail = rs.some((r) => r.status === "fail");
              return (
                <tr key={e.id}>
                  <td className="mono">{e.id}</td>
                  <td>{e.type}</td>
                  <td className="mono">{e.from_node}</td>
                  <td className="mono">{e.to_node}</td>
                  <td className="mono">{e.section}</td>
                  <td className="mono">{e.material}</td>
                  <td className={`mono right ${hasFail ? "fail" : "pass"}`}>
                    {maxR !== null ? (maxR * 100).toFixed(1) + "%" : "—"}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="ss-section">
        <h4>Sections ({project.sections.length})</h4>
        <table className="ss-table">
          <thead>
            <tr><th>ID</th><th>OD [mm]</th><th>Wall [mm]</th></tr>
          </thead>
          <tbody>
            {project.sections.map((s) => (
              <tr key={s.id}>
                <td className="mono">{s.id}</td>
                <td className="mono right">{(s.outside_diameter * 1000).toFixed(2)}</td>
                <td className="mono right">{(s.wall_thickness * 1000).toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="ss-section">
        <h4>Load cases ({project.load_cases.length})</h4>
        <table className="ss-table">
          <thead>
            <tr><th>ID</th><th>Kind</th><th>Value</th></tr>
          </thead>
          <tbody>
            {project.load_cases.map((lc) => (
              <tr key={lc.id}>
                <td className="mono">{lc.id}</td>
                <td>{lc.kind}</td>
                <td className="mono right">
                  {lc.pressure !== null && lc.pressure !== undefined
                    ? `${(lc.pressure / 1e5).toFixed(1)} bar`
                    : lc.temperature !== null && lc.temperature !== undefined
                    ? `${(lc.temperature - 273.15).toFixed(1)} °C`
                    : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="ss-section">
        <h4>Load combinations ({project.load_combinations.length})</h4>
        <table className="ss-table">
          <thead>
            <tr><th>ID</th><th>Category</th><th>Cases</th></tr>
          </thead>
          <tbody>
            {project.load_combinations.map((c) => (
              <tr key={c.id}>
                <td className="mono">{c.id}</td>
                <td>{c.category}</td>
                <td className="mono">{c.cases.join(" + ")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {results && (
        <div className="ss-section">
          <h4>Results ({results.results.length} checks)</h4>
          <table className="ss-table">
            <thead>
              <tr>
                <th>Element</th><th>Combo</th><th>Eq</th>
                <th>Stress [MPa]</th><th>Allow [MPa]</th>
                <th>Ratio</th><th>Status</th>
              </tr>
            </thead>
            <tbody>
              {results.results.map((r, i) => (
                <tr key={i}>
                  <td className="mono">{r.element_id}</td>
                  <td className="mono">{r.combination_id}</td>
                  <td className="mono">{r.equation}</td>
                  <td className="mono right">{(r.stress_pa / 1e6).toFixed(2)}</td>
                  <td className="mono right">{(r.allowable_pa / 1e6).toFixed(2)}</td>
                  <td className="mono right">{(r.ratio * 100).toFixed(1)}%</td>
                  <td className={r.status === "pass" ? "pass" : "fail"}>
                    {r.status.toUpperCase()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

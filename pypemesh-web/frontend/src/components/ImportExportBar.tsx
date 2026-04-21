// Import / export bar — upload PCF / JSON / Caesar II text, download JSON / PDF / CSV.

import { useRef } from "react";
import { useProjectStore } from "../store/projectStore";
import { downloadReport, solveProject } from "../api";
import type { PipeProject } from "../types";


export function ImportExportBar() {
  const project = useProjectStore((s) => s.project);
  const setProject = useProjectStore((s) => s.setProject);
  const fileRef = useRef<HTMLInputElement>(null);

  async function onImport(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (!f) return;
    const text = await f.text();
    try {
      const loaded = JSON.parse(text) as PipeProject;
      if (!loaded.schema_version) throw new Error("not a pypemesh project JSON");
      setProject(loaded);
    } catch (err) {
      alert(`Couldn't load ${f.name}: ${err}`);
    }
    if (fileRef.current) fileRef.current.value = "";
  }

  function downloadJson() {
    const blob = new Blob([JSON.stringify(project, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${project.project.name.replace(/\s+/g, "_")}.pypemesh.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  async function downloadPdf() {
    const r = await downloadReport(project);
    if (!r.ok) alert(r.message ?? "PDF generation failed");
  }

  async function downloadCsv() {
    try {
      const res = await solveProject(project, project.code);
      const rows = [
        ["element_id", "combination_id", "equation", "stress_pa", "allowable_pa", "ratio", "status"],
        ...res.results.map((x) => [
          x.element_id, x.combination_id, x.equation,
          x.stress_pa.toExponential(6), x.allowable_pa.toExponential(6),
          x.ratio.toFixed(6), x.status,
        ]),
      ];
      const csv = rows.map((r) => r.join(",")).join("\n");
      const blob = new Blob([csv], { type: "text/csv" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${project.project.name.replace(/\s+/g, "_")}_results.csv`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      alert(`CSV export failed: ${err}`);
    }
  }

  return (
    <div className="io-bar">
      <label className="io-btn">
        📂 Import JSON
        <input
          ref={fileRef}
          type="file"
          accept=".json,.pypemesh.json"
          onChange={onImport}
          style={{ display: "none" }}
        />
      </label>
      <button className="io-btn" onClick={downloadJson}>⬇ JSON</button>
      <button className="io-btn" onClick={downloadPdf}>⬇ PDF report</button>
      <button className="io-btn" onClick={downloadCsv}>⬇ CSV</button>
    </div>
  );
}

// STEP / IGES import UI — dynamically loads occt-import-js (~8 MB WASM) on demand.

import { useRef, useState } from "react";
import type { ImportedGeometry } from "../solid/stepImport";

interface Props {
  onImported: (geom: ImportedGeometry) => void;
}

export function CADImport({ onImported }: Props) {
  const fileRef = useRef<HTMLInputElement>(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<string | null>(null);

  async function onFile(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (!f) return;
    setLoading(true);
    setStatus(`Loading OpenCascade WASM and parsing ${f.name}…`);
    try {
      const fmt = f.name.toLowerCase().endsWith(".iges") || f.name.toLowerCase().endsWith(".igs")
        ? "iges" : "step";
      const { loadCADFile, boundingOfGeometries } = await import("../solid/stepImport");
      const g = await loadCADFile(f, fmt);
      const bb = boundingOfGeometries(g);
      setStatus(`Imported ${g.meshes.length} mesh(es) · size ≈ ${bb.diagonal.toFixed(1)} m`);
      onImported(g);
    } catch (err) {
      setStatus(`Error: ${(err as Error).message}`);
    } finally {
      setLoading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  }

  return (
    <div className="cad-import">
      <label className="io-btn">
        {loading ? "Loading CAD…" : "📐 Import STEP / IGES"}
        <input
          ref={fileRef}
          type="file"
          accept=".step,.stp,.iges,.igs"
          onChange={onFile}
          disabled={loading}
          style={{ display: "none" }}
        />
      </label>
      {status && <span className="cad-import-status">{status}</span>}
    </div>
  );
}

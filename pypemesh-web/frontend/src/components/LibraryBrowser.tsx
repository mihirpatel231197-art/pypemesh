// Library browser — sidebar tabs for Materials, Sections, Fittings.
// Click an entry to add it to the current project.

import { useState } from "react";
import { useProjectStore } from "../store/projectStore";
import { MATERIAL_CATALOG, SECTION_CATALOG } from "../data/catalog";

type Tab = "materials" | "sections" | "fittings";

export function LibraryBrowser() {
  const [tab, setTab] = useState<Tab>("sections");
  const project = useProjectStore((s) => s.project);
  const addMaterial = useProjectStore((s) => s.addMaterial);
  const addSection = useProjectStore((s) => s.addSection);
  const [search, setSearch] = useState("");

  const projectMaterialIds = new Set(project.materials.map((m) => m.id));
  const projectSectionIds = new Set(project.sections.map((s) => s.id));

  const filteredMaterials = MATERIAL_CATALOG.filter((m) =>
    m.id.toLowerCase().includes(search.toLowerCase()) ||
    m.name.toLowerCase().includes(search.toLowerCase()),
  );
  const filteredSections = SECTION_CATALOG.filter((s) =>
    s.id.toLowerCase().includes(search.toLowerCase()),
  );

  return (
    <div className="library-panel">
      <div className="library-tabs">
        <button className={`lib-tab ${tab === "sections" ? "active" : ""}`} onClick={() => setTab("sections")}>
          Sections
        </button>
        <button className={`lib-tab ${tab === "materials" ? "active" : ""}`} onClick={() => setTab("materials")}>
          Materials
        </button>
        <button className={`lib-tab ${tab === "fittings" ? "active" : ""}`} onClick={() => setTab("fittings")}>
          Fittings
        </button>
      </div>

      <input
        type="search"
        placeholder="Search…"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="library-search"
      />

      <div className="library-list">
        {tab === "sections" && filteredSections.map((s) => (
          <div key={s.id} className="library-item">
            <div>
              <div className="lib-name">{s.id}</div>
              <div className="lib-meta">OD {(s.outside_diameter * 1000).toFixed(1)}mm · wall {(s.wall_thickness * 1000).toFixed(2)}mm</div>
            </div>
            <button
              disabled={projectSectionIds.has(s.id)}
              onClick={() => addSection(s)}
              className="lib-add-btn"
            >
              {projectSectionIds.has(s.id) ? "✓ added" : "+ add"}
            </button>
          </div>
        ))}

        {tab === "materials" && filteredMaterials.map((m) => (
          <div key={m.id} className="library-item">
            <div>
              <div className="lib-name">{m.id}</div>
              <div className="lib-meta">{m.name}</div>
            </div>
            <button
              disabled={projectMaterialIds.has(m.id)}
              onClick={() => addMaterial(m)}
              className="lib-add-btn"
            >
              {projectMaterialIds.has(m.id) ? "✓ added" : "+ add"}
            </button>
          </div>
        ))}

        {tab === "fittings" && (
          <div className="library-empty">
            <p>Standard fittings per ASME B16.9:</p>
            <ul>
              <li>LR elbow (1.5·Do)</li>
              <li>SR elbow (1·Do)</li>
              <li>3D / 5D elbows</li>
              <li>Straight + reducing tees</li>
              <li>Concentric + eccentric reducers</li>
              <li>B16.5 flanges (class 150/300/600/900/1500/2500)</li>
            </ul>
            <p className="hint">
              Pick an element in the 3D view → set its type to Elbow / Tee / Reducer → set bend radius.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

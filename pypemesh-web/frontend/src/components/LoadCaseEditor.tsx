// Load case + combination editor.

import { useProjectStore } from "../store/projectStore";
import type { LoadKind } from "../types";

export function LoadCaseEditor() {
  const project = useProjectStore((s) => s.project);
  const addLoadCase = useProjectStore((s) => s.addLoadCase);
  const updateLoadCase = useProjectStore((s) => s.updateLoadCase);
  const removeLoadCase = useProjectStore((s) => s.removeLoadCase);
  const addLoadCombination = useProjectStore((s) => s.addLoadCombination);
  const updateLoadCombination = useProjectStore((s) => s.updateLoadCombination);
  const removeLoadCombination = useProjectStore((s) => s.removeLoadCombination);

  function addLC(kind: LoadKind) {
    const existingIds = new Set(project.load_cases.map((l) => l.id));
    let i = 1;
    const prefix = kind === "weight" ? "W"
                 : kind === "pressure" ? "P"
                 : kind === "thermal" ? "T"
                 : kind === "wind" ? "WIN"
                 : "U";
    while (existingIds.has(`${prefix}${i}`)) i += 1;
    const id = `${prefix}${i}`;
    addLoadCase({
      id, kind,
      pressure: kind === "pressure" ? 5e6 : null,
      temperature: kind === "thermal" ? 393.15 : null,
    });
  }

  function addCombo(category: "sustained" | "occasional" | "expansion") {
    const existingIds = new Set(project.load_combinations.map((c) => c.id));
    const prefixMap = { sustained: "SUS", occasional: "OCC", expansion: "EXP" };
    let base = prefixMap[category];
    let id = base;
    let i = 2;
    while (existingIds.has(id)) {
      id = `${base}${i}`; i += 1;
    }
    addLoadCombination({ id, cases: [], category });
  }

  return (
    <div className="load-editor">
      <div className="load-section">
        <div className="load-header">
          <h4>Load cases</h4>
          <div className="load-header-btns">
            <button onClick={() => addLC("weight")}>+ Weight</button>
            <button onClick={() => addLC("pressure")}>+ Pressure</button>
            <button onClick={() => addLC("thermal")}>+ Thermal</button>
          </div>
        </div>
        {project.load_cases.map((lc) => (
          <div key={lc.id} className="load-row">
            <input
              className="load-id"
              value={lc.id}
              onChange={(e) => updateLoadCase(lc.id, { id: e.target.value })}
            />
            <span className="load-kind">{lc.kind}</span>
            {lc.kind === "pressure" && (
              <div className="load-val">
                <input
                  type="number"
                  value={(lc.pressure ?? 0) / 1e5}
                  step={1}
                  onChange={(e) => updateLoadCase(lc.id, {
                    pressure: (parseFloat(e.target.value) || 0) * 1e5,
                  })}
                />
                <span>bar</span>
              </div>
            )}
            {lc.kind === "thermal" && (
              <div className="load-val">
                <input
                  type="number"
                  value={(lc.temperature ?? 293.15) - 273.15}
                  step={5}
                  onChange={(e) => updateLoadCase(lc.id, {
                    temperature: (parseFloat(e.target.value) || 20) + 273.15,
                  })}
                />
                <span>°C</span>
              </div>
            )}
            <button className="remove" onClick={() => removeLoadCase(lc.id)}>×</button>
          </div>
        ))}
      </div>

      <div className="load-section">
        <div className="load-header">
          <h4>Combinations</h4>
          <div className="load-header-btns">
            <button onClick={() => addCombo("sustained")}>+ SUS</button>
            <button onClick={() => addCombo("occasional")}>+ OCC</button>
            <button onClick={() => addCombo("expansion")}>+ EXP</button>
          </div>
        </div>
        {project.load_combinations.map((c) => (
          <div key={c.id} className="load-row combo">
            <input
              className="load-id"
              value={c.id}
              onChange={(e) => updateLoadCombination(c.id, { id: e.target.value })}
            />
            <select
              value={c.category}
              onChange={(e) => updateLoadCombination(c.id, { category: e.target.value })}
            >
              <option value="sustained">sustained</option>
              <option value="occasional">occasional</option>
              <option value="expansion">expansion</option>
              <option value="operating">operating</option>
            </select>
            <div className="combo-cases">
              {project.load_cases.map((lc) => {
                const included = c.cases.includes(lc.id);
                return (
                  <button
                    key={lc.id}
                    className={`case-chip ${included ? "active" : ""}`}
                    onClick={() => updateLoadCombination(c.id, {
                      cases: included
                        ? c.cases.filter((x) => x !== lc.id)
                        : [...c.cases, lc.id],
                    })}
                  >
                    {lc.id}
                  </button>
                );
              })}
            </div>
            <button className="remove" onClick={() => removeLoadCombination(c.id)}>×</button>
          </div>
        ))}
      </div>
    </div>
  );
}

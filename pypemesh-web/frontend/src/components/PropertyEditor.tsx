// Inline property editor for the selected node(s) or element(s).

import { useProjectStore } from "../store/projectStore";

function NumberField({ label, value, onChange, step = 0.1, unit }: {
  label: string; value: number; onChange: (v: number) => void;
  step?: number; unit?: string;
}) {
  return (
    <div className="prop-field">
      <label>{label}</label>
      <div className="prop-input-unit">
        <input
          type="number"
          value={value}
          step={step}
          onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
        />
        {unit && <span className="unit">{unit}</span>}
      </div>
    </div>
  );
}

function SelectField({ label, value, options, onChange }: {
  label: string; value: string;
  options: { value: string; label: string }[];
  onChange: (v: string) => void;
}) {
  return (
    <div className="prop-field">
      <label>{label}</label>
      <select value={value} onChange={(e) => onChange(e.target.value)}>
        {options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
    </div>
  );
}

export function PropertyEditor() {
  const project = useProjectStore((s) => s.project);
  const selectedNodeIds = useProjectStore((s) => s.selectedNodeIds);
  const selectedElementIds = useProjectStore((s) => s.selectedElementIds);
  const updateNode = useProjectStore((s) => s.updateNode);
  const updateElement = useProjectStore((s) => s.updateElement);
  const deleteNode = useProjectStore((s) => s.deleteNode);
  const deleteElement = useProjectStore((s) => s.deleteElement);
  const addRestraint = useProjectStore((s) => s.addRestraint);
  const removeRestraint = useProjectStore((s) => s.removeRestraint);

  if (selectedNodeIds.length === 1) {
    const n = project.nodes.find((x) => x.id === selectedNodeIds[0]);
    if (!n) return null;
    const restraint = project.restraints.find((r) => r.node === n.id);
    return (
      <div className="property-editor">
        <h4>Node {n.id}</h4>
        <NumberField label="x" value={n.x} unit="m" onChange={(v) => updateNode(n.id, { x: v })} />
        <NumberField label="y" value={n.y} unit="m" onChange={(v) => updateNode(n.id, { y: v })} />
        <NumberField label="z" value={n.z} unit="m" onChange={(v) => updateNode(n.id, { z: v })} />
        <div className="prop-field">
          <label>Restraint</label>
          <div style={{ display: "flex", gap: 6 }}>
            <select
              value={restraint?.type ?? "none"}
              onChange={(e) => {
                const v = e.target.value;
                if (v === "none") removeRestraint(n.id);
                else addRestraint(n.id, v as any);
              }}
              style={{ flex: 1 }}
            >
              <option value="none">(free)</option>
              <option value="anchor">Anchor</option>
              <option value="guide">Guide</option>
              <option value="rest">Rest</option>
              <option value="limit_stop">Limit stop</option>
              <option value="spring_hanger">Spring hanger</option>
              <option value="snubber">Snubber</option>
            </select>
          </div>
        </div>
        <button className="danger" onClick={() => deleteNode(n.id)}>Delete node</button>
      </div>
    );
  }

  if (selectedElementIds.length === 1) {
    const e = project.elements.find((x) => x.id === selectedElementIds[0]);
    if (!e) return null;
    const sectionOptions = project.sections.map((s) => ({ value: s.id, label: s.id }));
    const materialOptions = project.materials.map((m) => ({ value: m.id, label: m.id }));
    return (
      <div className="property-editor">
        <h4>Element {e.id}</h4>
        <div className="prop-field">
          <label>From → To</label>
          <span className="mono">{e.from_node} → {e.to_node}</span>
        </div>
        <SelectField
          label="Type"
          value={e.type}
          options={[
            { value: "pipe", label: "Pipe" },
            { value: "elbow", label: "Elbow" },
            { value: "tee", label: "Tee" },
            { value: "reducer", label: "Reducer" },
            { value: "rigid", label: "Rigid" },
            { value: "spring", label: "Spring" },
          ]}
          onChange={(v) => updateElement(e.id, { type: v as any })}
        />
        <SelectField
          label="Section"
          value={e.section}
          options={sectionOptions.length ? sectionOptions : [{ value: e.section, label: e.section }]}
          onChange={(v) => updateElement(e.id, { section: v })}
        />
        <SelectField
          label="Material"
          value={e.material}
          options={materialOptions.length ? materialOptions : [{ value: e.material, label: e.material }]}
          onChange={(v) => updateElement(e.id, { material: v })}
        />
        {e.type === "elbow" && (
          <NumberField
            label="Bend radius"
            value={e.bend_radius ?? 0.228}
            step={0.01}
            unit="m"
            onChange={(v) => updateElement(e.id, { bend_radius: v })}
          />
        )}
        <button className="danger" onClick={() => deleteElement(e.id)}>Delete element</button>
      </div>
    );
  }

  return (
    <div className="property-editor empty">
      <p>Select a node or element to edit its properties.</p>
      <p className="hint">
        Or pick a tool from the toolbar to create new geometry.
      </p>
    </div>
  );
}

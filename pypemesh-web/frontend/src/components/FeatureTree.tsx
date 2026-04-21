// Hierarchical view of the model — nodes, elements, restraints, load cases,
// dimensions, equipment. Click any item to select it.

import { useState } from "react";
import { useProjectStore } from "../store/projectStore";


function Group({ title, count, children, defaultOpen = true }: {
  title: string; count: number; children: React.ReactNode; defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="ft-group">
      <div className="ft-group-header" onClick={() => setOpen((v) => !v)}>
        <span className="ft-chevron">{open ? "▾" : "▸"}</span>
        <span className="ft-group-title">{title}</span>
        <span className="ft-group-count">{count}</span>
      </div>
      {open && <div className="ft-group-body">{children}</div>}
    </div>
  );
}


export function FeatureTree() {
  const project = useProjectStore((s) => s.project);
  const dimensions = useProjectStore((s) => s.dimensions);
  const equipment = useProjectStore((s) => s.equipment);
  const selectedNodeIds = useProjectStore((s) => s.selectedNodeIds);
  const selectedElementIds = useProjectStore((s) => s.selectedElementIds);
  const selectNode = useProjectStore((s) => s.selectNode);
  const selectElement = useProjectStore((s) => s.selectElement);
  const removeDimension = useProjectStore((s) => s.removeDimension);
  const removeEquipment = useProjectStore((s) => s.removeEquipment);

  const restraintByNode = new Map(project.restraints.map((r) => [r.node, r]));

  return (
    <div className="feature-tree">
      <Group title="Nodes" count={project.nodes.length}>
        {project.nodes.map((n) => {
          const r = restraintByNode.get(n.id);
          return (
            <div
              key={n.id}
              className={`ft-item ${selectedNodeIds.includes(n.id) ? "selected" : ""}`}
              onClick={() => selectNode(n.id)}
            >
              <span className={`ft-dot ${r ? "anchor" : "node"}`} />
              <span className="ft-name">{n.id}</span>
              <span className="ft-meta">
                ({n.x.toFixed(2)}, {n.y.toFixed(2)}, {n.z.toFixed(2)})
              </span>
              {r && <span className="ft-tag">{r.type}</span>}
            </div>
          );
        })}
      </Group>

      <Group title="Elements" count={project.elements.length}>
        {project.elements.map((e) => (
          <div
            key={e.id}
            className={`ft-item ${selectedElementIds.includes(e.id) ? "selected" : ""}`}
            onClick={() => selectElement(e.id)}
          >
            <span className={`ft-dot elem ${e.type}`} />
            <span className="ft-name">{e.id}</span>
            <span className="ft-meta">
              {e.type} · {e.from_node}→{e.to_node}
            </span>
          </div>
        ))}
      </Group>

      <Group title="Sections" count={project.sections.length}>
        {project.sections.map((s) => (
          <div key={s.id} className="ft-item">
            <span className="ft-dot section" />
            <span className="ft-name">{s.id}</span>
            <span className="ft-meta">{(s.outside_diameter * 1000).toFixed(1)}×{(s.wall_thickness * 1000).toFixed(2)} mm</span>
          </div>
        ))}
      </Group>

      <Group title="Materials" count={project.materials.length}>
        {project.materials.map((m) => (
          <div key={m.id} className="ft-item">
            <span className="ft-dot material" />
            <span className="ft-name">{m.id}</span>
          </div>
        ))}
      </Group>

      <Group title="Restraints" count={project.restraints.length} defaultOpen={false}>
        {project.restraints.map((r, i) => (
          <div key={i} className="ft-item" onClick={() => selectNode(r.node)}>
            <span className="ft-dot anchor" />
            <span className="ft-name">{r.node}</span>
            <span className="ft-tag">{r.type}</span>
          </div>
        ))}
      </Group>

      <Group title="Load cases" count={project.load_cases.length} defaultOpen={false}>
        {project.load_cases.map((lc) => (
          <div key={lc.id} className="ft-item">
            <span className="ft-dot load" />
            <span className="ft-name">{lc.id}</span>
            <span className="ft-meta">{lc.kind}</span>
          </div>
        ))}
      </Group>

      <Group title="Combinations" count={project.load_combinations.length} defaultOpen={false}>
        {project.load_combinations.map((c) => (
          <div key={c.id} className="ft-item">
            <span className="ft-dot combo" />
            <span className="ft-name">{c.id}</span>
            <span className="ft-meta">{c.category} · {c.cases.join("+")}</span>
          </div>
        ))}
      </Group>

      <Group title="Dimensions" count={dimensions.length} defaultOpen={false}>
        {dimensions.map((d) => (
          <div key={d.id} className="ft-item">
            <span className="ft-dot dim" />
            <span className="ft-name">{d.id}</span>
            <span className="ft-meta">{d.from_node} → {d.to_node}</span>
            <button className="ft-delete" onClick={(e) => { e.stopPropagation(); removeDimension(d.id); }}>×</button>
          </div>
        ))}
      </Group>

      <Group title="Equipment" count={equipment.length} defaultOpen={false}>
        {equipment.map((eq) => (
          <div key={eq.id} className="ft-item">
            <span className="ft-dot equip" />
            <span className="ft-name">{eq.id}</span>
            <span className="ft-meta">{eq.type} @ {eq.anchor_node}</span>
            <button className="ft-delete" onClick={(e) => { e.stopPropagation(); removeEquipment(eq.id); }}>×</button>
          </div>
        ))}
      </Group>
    </div>
  );
}

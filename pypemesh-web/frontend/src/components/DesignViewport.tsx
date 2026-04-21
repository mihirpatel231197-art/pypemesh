// Interactive 3D viewport for Design mode. Phase E + F features:
// - Add/connect nodes, delete, anchor, dimension, measure, sketch
// - Snap-to-nodes, live cursor XYZ
// - Right-click context menus, XYZ axes triad, dimension lines
// - Equipment primitive boxes, swept pipe solids (Phase F)
// - STEP/IGES imported geometry rendering

import { Canvas } from "@react-three/fiber";
import { Grid, Line, OrbitControls, Text } from "@react-three/drei";
import { useRef, useState } from "react";
import * as THREE from "three";
import { useProjectStore } from "../store/projectStore";
import { ContextMenu, type ContextMenuItem } from "./ContextMenu";
import type { ImportedGeometry } from "../solid/stepImport";


interface SceneProps {
  onContextMenu: (x: number, y: number, items: ContextMenuItem[]) => void;
  importedGeometry: ImportedGeometry | null;
  useSweepGeometry: boolean;
}


function SceneContent({ onContextMenu, importedGeometry, useSweepGeometry }: SceneProps) {
  const project = useProjectStore((s) => s.project);
  const dimensions = useProjectStore((s) => s.dimensions);
  const equipment = useProjectStore((s) => s.equipment);
  const sketch = useProjectStore((s) => s.sketch);
  const tool = useProjectStore((s) => s.tool);
  const selectedNodeIds = useProjectStore((s) => s.selectedNodeIds);
  const selectedElementIds = useProjectStore((s) => s.selectedElementIds);
  const pendingConnect = useProjectStore((s) => s.pendingConnectFrom);
  const pendingDimFrom = useProjectStore((s) => s.pendingDimFrom);
  const pendingMeasure = useProjectStore((s) => s.pendingMeasureFrom);
  const snapToNodes = useProjectStore((s) => s.snapToNodes);
  const snapRadius = useProjectStore((s) => s.snapRadius);

  const addNode = useProjectStore((s) => s.addNode);
  const addElement = useProjectStore((s) => s.addElement);
  const deleteNode = useProjectStore((s) => s.deleteNode);
  const deleteElement = useProjectStore((s) => s.deleteElement);
  const selectNode = useProjectStore((s) => s.selectNode);
  const selectElement = useProjectStore((s) => s.selectElement);
  const addRestraint = useProjectStore((s) => s.addRestraint);
  const removeRestraint = useProjectStore((s) => s.removeRestraint);
  const setPendingConnect = useProjectStore((s) => s.setPendingConnect);
  const setPendingDimFrom = useProjectStore((s) => s.setPendingDimFrom);
  const addDimension = useProjectStore((s) => s.addDimension);
  const setPendingMeasure = useProjectStore((s) => s.setPendingMeasure);
  const setMeasurement = useProjectStore((s) => s.setMeasurement);
  const addSketchPoint = useProjectStore((s) => s.addSketchPoint);
  const setCursorPosition = useProjectStore((s) => s.setCursorPosition);
  const clearSelection = useProjectStore((s) => s.clearSelection);

  const groundRef = useRef<THREE.Mesh>(null);

  const nodeMap = new Map(
    project.nodes.map((n) => [n.id, [n.x, n.y, n.z] as [number, number, number]]),
  );
  const restrainedNodes = new Set(project.restraints.map((r) => r.node));

  function snapToNearest(p: [number, number, number]): [number, number, number] {
    if (!snapToNodes) return p;
    let best: { dist: number; pos: [number, number, number] } | null = null;
    for (const n of project.nodes) {
      const d = Math.hypot(n.x - p[0], n.y - p[1], n.z - p[2]);
      if (d < snapRadius && (!best || d < best.dist)) {
        best = { dist: d, pos: [n.x, n.y, n.z] };
      }
    }
    return best ? best.pos : p;
  }

  function onGroundClick(e: any) {
    e.stopPropagation();
    const raw: [number, number, number] = [e.point.x, e.point.y, e.point.z];
    const p = snapToNearest(raw);

    if (tool === "add-node") addNode(p[0], p[1], p[2]);
    else if (tool === "sketch" && sketch.plane) {
      let a = 0, b = 0;
      if (sketch.plane === "XY") { a = p[0]; b = p[1]; }
      else if (sketch.plane === "XZ") { a = p[0]; b = p[2]; }
      else { a = p[1]; b = p[2]; }
      addSketchPoint([a, b]);
    } else if (tool === "measure") {
      if (pendingMeasure === null) setPendingMeasure(p);
      else { setMeasurement({ from: pendingMeasure, to: p }); setPendingMeasure(null); }
    }
  }

  function onGroundPointerMove(e: any) {
    setCursorPosition([e.point.x, e.point.y, e.point.z]);
  }

  function onNodeClick(id: string, e: any) {
    e.stopPropagation();
    if (tool === "select") selectNode(id, e.shiftKey);
    else if (tool === "connect-pipe" || tool === "connect-elbow") {
      if (pendingConnect === null) setPendingConnect(id);
      else if (pendingConnect !== id) {
        addElement(pendingConnect, id, tool === "connect-elbow" ? "elbow" : "pipe");
        setPendingConnect(null);
      } else setPendingConnect(null);
    } else if (tool === "add-restraint") addRestraint(id, "anchor");
    else if (tool === "delete") deleteNode(id);
    else if (tool === "dimension") {
      if (pendingDimFrom === null) setPendingDimFrom(id);
      else if (pendingDimFrom !== id) {
        addDimension(pendingDimFrom, id);
        setPendingDimFrom(null);
      } else setPendingDimFrom(null);
    } else if (tool === "measure") {
      const n = nodeMap.get(id);
      if (n) {
        if (pendingMeasure === null) setPendingMeasure(n);
        else { setMeasurement({ from: pendingMeasure, to: n }); setPendingMeasure(null); }
      }
    }
  }

  function onNodeContextMenu(id: string, e: any) {
    e.stopPropagation();
    e.nativeEvent.preventDefault();
    const isRestrained = restrainedNodes.has(id);
    onContextMenu(e.nativeEvent.clientX, e.nativeEvent.clientY, [
      { label: `Select ${id}`, onClick: () => selectNode(id) },
      { label: "Connect pipe from here", onClick: () => setPendingConnect(id) },
      { label: "Dimension from here", onClick: () => setPendingDimFrom(id) },
      { label: isRestrained ? "Remove anchor" : "Anchor here",
        onClick: () => isRestrained ? removeRestraint(id) : addRestraint(id, "anchor") },
      { divider: true, label: "" },
      { label: "Delete", onClick: () => deleteNode(id) },
    ]);
  }

  function onElementClick(id: string, e: any) {
    e.stopPropagation();
    if (tool === "select") selectElement(id, e.shiftKey);
    else if (tool === "delete") deleteElement(id);
  }

  function onElementContextMenu(id: string, e: any) {
    e.stopPropagation();
    e.nativeEvent.preventDefault();
    onContextMenu(e.nativeEvent.clientX, e.nativeEvent.clientY, [
      { label: `Select ${id}`, onClick: () => selectElement(id) },
      { divider: true, label: "" },
      { label: "Delete", onClick: () => deleteElement(id) },
    ]);
  }

  return (
    <>
      <ambientLight intensity={0.5} />
      <directionalLight position={[10, 10, 5]} intensity={0.7} />

      <mesh
        ref={groundRef}
        rotation={[-Math.PI / 2, 0, 0]}
        position={[0, 0, 0]}
        onClick={onGroundClick}
        onPointerMove={onGroundPointerMove}
        onPointerMissed={() => { if (tool === "select") clearSelection(); }}
      >
        <planeGeometry args={[60, 60]} />
        <meshBasicMaterial visible={false} side={THREE.DoubleSide} />
      </mesh>

      <Grid args={[60, 60]} cellColor="#1f242c" sectionColor="#2d3540"
            fadeDistance={40} infiniteGrid position={[0, -0.005, 0]} />

      {/* XYZ axes triad at origin */}
      <group>
        <Line points={[[0, 0, 0], [0.6, 0, 0]]} color="#ef4444" lineWidth={2} />
        <Line points={[[0, 0, 0], [0, 0.6, 0]]} color="#22c55e" lineWidth={2} />
        <Line points={[[0, 0, 0], [0, 0, 0.6]]} color="#3b82f6" lineWidth={2} />
        <Text position={[0.75, 0, 0]} fontSize={0.12} color="#ef4444">X</Text>
        <Text position={[0, 0.75, 0]} fontSize={0.12} color="#22c55e">Y</Text>
        <Text position={[0, 0, 0.75]} fontSize={0.12} color="#3b82f6">Z</Text>
      </group>

      {/* Imported CAD meshes (STEP/IGES) */}
      {importedGeometry?.meshes.map((m, i) => (
        <mesh key={`imp-${i}`} geometry={m.geometry}>
          <meshStandardMaterial
            color={m.color ? `rgb(${Math.round(m.color[0]*255)},${Math.round(m.color[1]*255)},${Math.round(m.color[2]*255)})` : "#94a3b8"}
            metalness={0.3}
            roughness={0.6}
          />
        </mesh>
      ))}

      {/* Equipment primitives */}
      {equipment.map((eq) => {
        const n = nodeMap.get(eq.anchor_node);
        if (!n) return null;
        const color = eq.type === "tank" ? "#0891b2"
                    : eq.type === "pump" ? "#ca8a04"
                    : eq.type === "valve-box" ? "#a855f7"
                    : "#334155";
        return (
          <mesh key={eq.id} position={[n[0], n[1] + eq.size_y / 2, n[2]]}>
            <boxGeometry args={[eq.size_x, eq.size_y, eq.size_z]} />
            <meshStandardMaterial color={color} transparent opacity={0.3} />
          </mesh>
        );
      })}

      {/* Pipe elements — sweep geometry if toggle on, else cylinder */}
      {project.elements.map((e) => {
        const a = nodeMap.get(e.from_node);
        const b = nodeMap.get(e.to_node);
        if (!a || !b) return null;
        const start = new THREE.Vector3(...a);
        const end = new THREE.Vector3(...b);
        const dir = new THREE.Vector3().subVectors(end, start);
        const length = dir.length();
        const mid = new THREE.Vector3().addVectors(start, end).multiplyScalar(0.5);
        const quat = new THREE.Quaternion().setFromUnitVectors(
          new THREE.Vector3(0, 1, 0), dir.clone().normalize(),
        );
        const rot = new THREE.Euler().setFromQuaternion(quat);
        const isSelected = selectedElementIds.includes(e.id);
        const color = e.type === "elbow" ? "#f59e0b"
                    : e.type === "tee" ? "#a855f7"
                    : e.type === "rigid" ? "#64748b"
                    : "#60a5fa";
        const radius = useSweepGeometry ? 0.085 : 0.045;
        return (
          <mesh
            key={e.id}
            position={mid.toArray()}
            rotation={rot.toArray() as [number, number, number]}
            onClick={(ev) => onElementClick(e.id, ev)}
            onContextMenu={(ev) => onElementContextMenu(e.id, ev)}
          >
            <cylinderGeometry args={[radius, radius, length, 20]} />
            <meshStandardMaterial
              color={color}
              emissive={isSelected ? "#3b82f6" : "#000000"}
              emissiveIntensity={isSelected ? 0.7 : 0}
              metalness={0.5}
              roughness={0.4}
            />
          </mesh>
        );
      })}

      {/* Dimensions */}
      {dimensions.map((d) => {
        const a = nodeMap.get(d.from_node);
        const b = nodeMap.get(d.to_node);
        if (!a || !b) return null;
        const length = Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
        const mid: [number, number, number] = [
          (a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 0.15, (a[2] + b[2]) / 2,
        ];
        return (
          <group key={d.id}>
            <Line points={[a, b]} color="#fbbf24" lineWidth={1.5}
                  dashed dashSize={0.06} gapSize={0.04} />
            <Text position={mid} fontSize={0.09} color="#fbbf24"
                  outlineWidth={0.005} outlineColor="#000">
              {length.toFixed(3)} m
            </Text>
          </group>
        );
      })}

      {/* Nodes + labels */}
      {project.nodes.map((n) => {
        const isSelected = selectedNodeIds.includes(n.id);
        const isAnchor = restrainedNodes.has(n.id);
        const isPending = pendingConnect === n.id || pendingDimFrom === n.id;
        const color = isAnchor ? "#ef4444" : isPending ? "#f59e0b" : "#60a5fa";
        return (
          <group key={n.id}>
            <mesh
              position={[n.x, n.y, n.z]}
              onClick={(ev) => onNodeClick(n.id, ev)}
              onContextMenu={(ev) => onNodeContextMenu(n.id, ev)}
            >
              <sphereGeometry args={[isAnchor ? 0.12 : 0.085, 20, 20]} />
              <meshStandardMaterial
                color={color}
                emissive={isSelected ? "#3b82f6" : "#000"}
                emissiveIntensity={isSelected ? 0.85 : 0}
                metalness={0.25}
                roughness={0.4}
              />
            </mesh>
            <Text position={[n.x, n.y + 0.16, n.z]}
                  fontSize={0.07} color="#94a3b8"
                  outlineWidth={0.003} outlineColor="#000">
              {n.id}
            </Text>
          </group>
        );
      })}

      {/* Sketch preview points */}
      {sketch.plane && sketch.points.map((pt, i) => {
        let pos: [number, number, number] = [0, 0, 0];
        if (sketch.plane === "XY") pos = [pt[0], pt[1], sketch.elevation];
        else if (sketch.plane === "XZ") pos = [pt[0], sketch.elevation, pt[1]];
        else pos = [sketch.elevation, pt[0], pt[1]];
        return (
          <mesh key={i} position={pos}>
            <sphereGeometry args={[0.05, 12, 12]} />
            <meshStandardMaterial color="#fbbf24" emissive="#fbbf24" emissiveIntensity={0.5} />
          </mesh>
        );
      })}

      <OrbitControls makeDefault enableDamping dampingFactor={0.1} />
    </>
  );
}


interface Props {
  importedGeometry?: ImportedGeometry | null;
  useSweepGeometry?: boolean;
}


export function DesignViewport({ importedGeometry = null, useSweepGeometry = true }: Props) {
  const [ctx, setCtx] = useState<{ x: number; y: number; items: ContextMenuItem[] } | null>(null);

  return (
    <>
      <Canvas
        camera={{ position: [6, 6, 6], fov: 45 }}
        style={{ background: "#0b0d10" }}
      >
        <SceneContent
          onContextMenu={(x, y, items) => setCtx({ x, y, items })}
          importedGeometry={importedGeometry}
          useSweepGeometry={useSweepGeometry}
        />
      </Canvas>
      {ctx && <ContextMenu x={ctx.x} y={ctx.y} items={ctx.items} onClose={() => setCtx(null)} />}
    </>
  );
}

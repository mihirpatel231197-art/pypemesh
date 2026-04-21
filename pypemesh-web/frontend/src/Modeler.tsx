import { Canvas } from "@react-three/fiber";
import { OrbitControls, Grid } from "@react-three/drei";
import { useMemo } from "react";
import * as THREE from "three";
import type { PipeProject, SolveResponse } from "./types";

interface Props {
  project: PipeProject;
  selectedNode: string | null;
  selectedElement: string | null;
  onSelectNode: (id: string | null) => void;
  onSelectElement: (id: string | null) => void;
  results: SolveResponse | null;
  resultCombo: string | null;
}

function stressColor(ratio: number): string {
  // green → amber → red
  if (ratio < 0.5) return "#4ade80";
  if (ratio < 0.8) return "#facc15";
  if (ratio < 1.0) return "#fb923c";
  return "#ef4444";
}

export function Modeler({
  project,
  selectedNode,
  selectedElement,
  onSelectNode,
  onSelectElement,
  results,
  resultCombo,
}: Props) {
  const nodeIndex = useMemo(() => {
    const m: Record<string, [number, number, number]> = {};
    project.nodes.forEach((n) => (m[n.id] = [n.x, n.y, n.z]));
    return m;
  }, [project.nodes]);

  // Compute element ratios for current combination
  const elementRatio = useMemo(() => {
    const m: Record<string, number> = {};
    if (!results || !resultCombo) return m;
    results.results
      .filter((r) => r.combination_id === resultCombo)
      .forEach((r) => (m[r.element_id] = r.ratio));
    return m;
  }, [results, resultCombo]);

  const restrainedNodes = useMemo(
    () => new Set(project.restraints.map((r) => r.node)),
    [project.restraints],
  );

  return (
    <Canvas
      camera={{ position: [4, 4, 8], fov: 45 }}
      style={{ background: "#0b0d10" }}
      onPointerMissed={() => {
        onSelectNode(null);
        onSelectElement(null);
      }}
    >
      <ambientLight intensity={0.5} />
      <directionalLight position={[10, 10, 5]} intensity={0.7} />
      <Grid
        args={[20, 20]}
        cellColor="#1f242c"
        sectionColor="#2d3540"
        fadeDistance={40}
        infiniteGrid
        position={[0, -0.01, 0]}
      />
      <OrbitControls makeDefault enableDamping dampingFactor={0.1} />

      {/* Elements as cylinders between nodes */}
      {project.elements.map((e) => {
        const a = nodeIndex[e.from_node];
        const b = nodeIndex[e.to_node];
        if (!a || !b) return null;
        const start = new THREE.Vector3(...a);
        const end = new THREE.Vector3(...b);
        const dir = new THREE.Vector3().subVectors(end, start);
        const length = dir.length();
        const mid = new THREE.Vector3().addVectors(start, end).multiplyScalar(0.5);
        const quat = new THREE.Quaternion().setFromUnitVectors(
          new THREE.Vector3(0, 1, 0),
          dir.clone().normalize(),
        );
        const rotation = new THREE.Euler().setFromQuaternion(quat);
        const radius = 0.04;
        const ratio = elementRatio[e.id];
        const color = ratio !== undefined ? stressColor(ratio) : "#6b7280";
        const isSelected = e.id === selectedElement;

        return (
          <mesh
            key={e.id}
            position={mid.toArray()}
            rotation={rotation.toArray() as [number, number, number]}
            onClick={(ev) => {
              ev.stopPropagation();
              onSelectElement(e.id);
              onSelectNode(null);
            }}
          >
            <cylinderGeometry args={[radius, radius, length, 16]} />
            <meshStandardMaterial
              color={color}
              emissive={isSelected ? "#3b82f6" : "#000000"}
              emissiveIntensity={isSelected ? 0.6 : 0}
              metalness={0.4}
              roughness={0.5}
            />
          </mesh>
        );
      })}

      {/* Nodes as spheres */}
      {project.nodes.map((n) => {
        const isSelected = n.id === selectedNode;
        const isAnchor = restrainedNodes.has(n.id);
        const color = isAnchor ? "#ef4444" : "#60a5fa";
        return (
          <mesh
            key={n.id}
            position={[n.x, n.y, n.z]}
            onClick={(ev) => {
              ev.stopPropagation();
              onSelectNode(n.id);
              onSelectElement(null);
            }}
          >
            <sphereGeometry args={[isAnchor ? 0.1 : 0.07, 24, 24]} />
            <meshStandardMaterial
              color={color}
              emissive={isSelected ? "#3b82f6" : "#000"}
              emissiveIntensity={isSelected ? 0.8 : 0}
              metalness={0.2}
              roughness={0.4}
            />
          </mesh>
        );
      })}
    </Canvas>
  );
}

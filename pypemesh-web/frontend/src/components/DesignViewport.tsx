// Interactive 3D viewport for Design mode. Click to place nodes, connect
// nodes to make pipes/elbows, click to select, delete, anchor.

import { Canvas } from "@react-three/fiber";
import { Grid, OrbitControls } from "@react-three/drei";
import { useRef } from "react";
import * as THREE from "three";
import { useProjectStore } from "../store/projectStore";


function SceneContent() {
  const project = useProjectStore((s) => s.project);
  const tool = useProjectStore((s) => s.tool);
  const selectedNodeIds = useProjectStore((s) => s.selectedNodeIds);
  const selectedElementIds = useProjectStore((s) => s.selectedElementIds);
  const pendingConnect = useProjectStore((s) => s.pendingConnectFrom);

  const addNode = useProjectStore((s) => s.addNode);
  const addElement = useProjectStore((s) => s.addElement);
  const deleteNode = useProjectStore((s) => s.deleteNode);
  const deleteElement = useProjectStore((s) => s.deleteElement);
  const selectNode = useProjectStore((s) => s.selectNode);
  const selectElement = useProjectStore((s) => s.selectElement);
  const addRestraint = useProjectStore((s) => s.addRestraint);
  const setPendingConnect = useProjectStore((s) => s.setPendingConnect);
  const clearSelection = useProjectStore((s) => s.clearSelection);

  const groundRef = useRef<THREE.Mesh>(null);

  function onGroundClick(e: any) {
    if (tool !== "add-node") return;
    e.stopPropagation();
    // Get 3D point from click
    const [x, y, z] = [e.point.x, e.point.y, e.point.z];
    addNode(x, y, z);
  }

  function onNodeClick(id: string, e: any) {
    e.stopPropagation();
    if (tool === "select") {
      selectNode(id, e.shiftKey);
    } else if (tool === "connect-pipe" || tool === "connect-elbow") {
      if (pendingConnect === null) {
        setPendingConnect(id);
      } else if (pendingConnect !== id) {
        const elemType = tool === "connect-elbow" ? "elbow" : "pipe";
        addElement(pendingConnect, id, elemType);
        setPendingConnect(null);
      } else {
        setPendingConnect(null);
      }
    } else if (tool === "add-restraint") {
      addRestraint(id, "anchor");
    } else if (tool === "delete") {
      deleteNode(id);
    }
  }

  function onElementClick(id: string, e: any) {
    e.stopPropagation();
    if (tool === "select") {
      selectElement(id, e.shiftKey);
    } else if (tool === "delete") {
      deleteElement(id);
    }
  }

  const restrainedNodes = new Set(project.restraints.map((r) => r.node));
  const nodeMap = new Map(project.nodes.map((n) => [n.id, [n.x, n.y, n.z] as [number, number, number]]));

  return (
    <>
      <ambientLight intensity={0.5} />
      <directionalLight position={[10, 10, 5]} intensity={0.7} />

      {/* Clickable ground plane for adding nodes */}
      <mesh
        ref={groundRef}
        rotation={[-Math.PI / 2, 0, 0]}
        position={[0, 0, 0]}
        onClick={onGroundClick}
        onPointerMissed={() => {
          if (tool === "select") clearSelection();
        }}
      >
        <planeGeometry args={[50, 50]} />
        <meshBasicMaterial visible={false} side={THREE.DoubleSide} />
      </mesh>

      <Grid args={[50, 50]} cellColor="#1f242c" sectionColor="#2d3540"
            fadeDistance={40} infiniteGrid position={[0, -0.01, 0]} />

      {/* Elements */}
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
        return (
          <mesh
            key={e.id}
            position={mid.toArray()}
            rotation={rot.toArray() as [number, number, number]}
            onClick={(ev) => onElementClick(e.id, ev)}
          >
            <cylinderGeometry args={[0.045, 0.045, length, 16]} />
            <meshStandardMaterial
              color={color}
              emissive={isSelected ? "#3b82f6" : "#000000"}
              emissiveIntensity={isSelected ? 0.7 : 0}
              metalness={0.4}
              roughness={0.5}
            />
          </mesh>
        );
      })}

      {/* Nodes */}
      {project.nodes.map((n) => {
        const isSelected = selectedNodeIds.includes(n.id);
        const isAnchor = restrainedNodes.has(n.id);
        const isPendingConnect = pendingConnect === n.id;
        const color = isAnchor ? "#ef4444" : isPendingConnect ? "#f59e0b" : "#60a5fa";
        return (
          <mesh
            key={n.id}
            position={[n.x, n.y, n.z]}
            onClick={(ev) => onNodeClick(n.id, ev)}
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
        );
      })}

      <OrbitControls makeDefault enableDamping dampingFactor={0.1} />
    </>
  );
}


export function DesignViewport() {
  return (
    <Canvas
      camera={{ position: [6, 6, 6], fov: 45 }}
      style={{ background: "#0b0d10" }}
    >
      <SceneContent />
    </Canvas>
  );
}

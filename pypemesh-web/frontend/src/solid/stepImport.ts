// STEP / IGES import via occt-import-js (OpenCascade compiled to WebAssembly).
// Dynamically imported so the ~8 MB WASM is only loaded when the user opens
// a CAD file — initial page load stays lightweight.

import * as THREE from "three";


export interface ImportedGeometry {
  meshes: {
    name: string;
    geometry: THREE.BufferGeometry;
    color?: [number, number, number, number];  // RGBA 0-1
  }[];
}


/**
 * Read a STEP or IGES file into Three.js BufferGeometries.
 * The first call triggers a dynamic import of occt-import-js (~8 MB WASM).
 */
export async function loadCADFile(
  file: File,
  format: "step" | "iges" = "step",
): Promise<ImportedGeometry> {
  // Dynamic import keeps the main bundle light
  const occt = await import("occt-import-js");
  const occtInstance = await (occt.default ?? occt)();

  const arrayBuffer = await file.arrayBuffer();
  const bytes = new Uint8Array(arrayBuffer);

  const result = format === "step"
    ? occtInstance.ReadStepFile(bytes, null)
    : occtInstance.ReadIgesFile(bytes, null);

  if (!result.success) {
    throw new Error("Failed to parse CAD file");
  }

  const meshes = result.meshes.map((m: any) => {
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute(
      "position",
      new THREE.Float32BufferAttribute(m.attributes.position.array, 3),
    );
    if (m.attributes.normal) {
      geometry.setAttribute(
        "normal",
        new THREE.Float32BufferAttribute(m.attributes.normal.array, 3),
      );
    }
    if (m.index) {
      geometry.setIndex(new THREE.Uint32BufferAttribute(m.index.array, 1));
    }
    geometry.computeBoundingBox();
    return {
      name: m.name || "Imported",
      geometry,
      color: m.color,
    };
  });

  return { meshes };
}


/**
 * Compute the bounding-box center and diagonal of imported geometries —
 * useful for auto-framing the camera after import.
 */
export function boundingOfGeometries(g: ImportedGeometry): {
  center: THREE.Vector3;
  diagonal: number;
} {
  const box = new THREE.Box3();
  for (const m of g.meshes) {
    const gb = m.geometry.boundingBox;
    if (gb) box.union(gb);
  }
  const center = new THREE.Vector3();
  const size = new THREE.Vector3();
  box.getCenter(center);
  box.getSize(size);
  return { center, diagonal: size.length() };
}

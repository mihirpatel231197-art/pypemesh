// Client-side catalogs — material + section entries for the library browser.
// Mirrors pypemesh-core's ALL_MATERIALS and B36.10 schedules (trimmed for bundle size).

import type { PipeMaterial, PipeSection } from "../types";

function material(
  id: string, name: string,
  E_room: number, alpha_room: number,
  Sh_room: number, Sc: number,
  density: number, poisson = 0.3,
): PipeMaterial {
  return {
    id, name,
    elastic_modulus: [[293.15, E_room]],
    thermal_expansion: [[293.15, alpha_room]],
    allowable_hot: [[293.15, Sh_room]],
    allowable_cold: Sc,
    density,
    poisson,
  };
}

export const MATERIAL_CATALOG: PipeMaterial[] = [
  // Carbon
  material("A106-B", "ASTM A106 Gr.B (Carbon Steel)", 2.03e11, 1.15e-5, 1.38e8, 1.38e8, 7850),
  material("A53-B", "ASTM A53 Gr.B (Welded CS)", 2.03e11, 1.15e-5, 1.17e8, 1.17e8, 7850),
  material("A333-6", "ASTM A333 Gr.6 (Low-temp CS)", 2.03e11, 1.15e-5, 1.38e8, 1.38e8, 7850),
  material("A671-CC70", "ASTM A671 Gr.CC70 (High-strength CS)", 2.03e11, 1.15e-5, 1.59e8, 1.59e8, 7850),
  material("A350-LF2", "ASTM A350 Gr.LF2 (Low-temp forging)", 2.03e11, 1.12e-5, 1.38e8, 1.38e8, 7850),
  material("A420-WPL6", "ASTM A420 Gr.WPL6 (Low-temp fitting)", 2.03e11, 1.12e-5, 1.38e8, 1.38e8, 7850),
  // Stainless
  material("A312-TP304", "ASTM A312 TP304", 1.95e11, 1.60e-5, 1.38e8, 1.38e8, 7900),
  material("A312-TP316L", "ASTM A312 TP316L", 1.95e11, 1.59e-5, 1.15e8, 1.15e8, 7950),
  material("A312-TP316", "ASTM A312 TP316", 1.95e11, 1.59e-5, 1.38e8, 1.38e8, 7950),
  material("A312-TP321", "ASTM A312 TP321 (Ti-stabilized)", 1.95e11, 1.60e-5, 1.38e8, 1.38e8, 7900),
  material("A312-TP347", "ASTM A312 TP347 (Nb-stabilized)", 1.95e11, 1.60e-5, 1.38e8, 1.38e8, 7960),
  material("A312-TP310", "ASTM A312 TP310 (Heat-resistant)", 1.96e11, 1.44e-5, 1.38e8, 1.38e8, 7900),
  material("A312-TP309", "ASTM A312 TP309 (Heat-resistant)", 1.96e11, 1.49e-5, 1.38e8, 1.38e8, 7900),
  material("A312-TP317", "ASTM A312 TP317 (High-Mo)", 1.95e11, 1.60e-5, 1.38e8, 1.38e8, 7950),
  material("A312-TP904L", "ASTM A312 TP904L (Chloride-resistant)", 1.95e11, 1.58e-5, 1.72e8, 1.72e8, 7950),
  // Low-alloy
  material("A335-P11", "A335 P11 (1¼Cr-½Mo)", 2.04e11, 1.10e-5, 1.38e8, 1.38e8, 7850),
  material("A335-P22", "A335 P22 (2¼Cr-1Mo)", 2.04e11, 1.10e-5, 1.38e8, 1.38e8, 7850),
  material("A335-P91", "A335 P91 (9Cr-1Mo-V)", 2.18e11, 1.04e-5, 2.00e8, 2.00e8, 7800),
  material("A335-P5", "A335 P5 (5Cr-½Mo)", 2.04e11, 1.10e-5, 1.38e8, 1.38e8, 7850),
  material("A335-P9", "A335 P9 (9Cr-1Mo)", 2.18e11, 1.04e-5, 1.65e8, 1.65e8, 7800),
  material("A335-P92", "A335 P92 (9Cr-2W advanced)", 2.18e11, 1.04e-5, 2.75e8, 2.75e8, 7800),
  // Pipeline
  material("API-5L-X65", "API 5L Gr.X65 (Pipeline)", 2.03e11, 1.15e-5, 2.51e8, 2.51e8, 7850),
  material("API-5L-X70", "API 5L Gr.X70 (Pipeline)", 2.03e11, 1.15e-5, 2.84e8, 2.84e8, 7850),
  material("API-5L-X80", "API 5L Gr.X80 (Pipeline)", 2.03e11, 1.15e-5, 3.20e8, 3.20e8, 7850),
  material("API-5L-X100", "API 5L Gr.X100 (Pipeline)", 2.03e11, 1.15e-5, 4.35e8, 4.35e8, 7850),
  // Duplex
  material("A789-S31803", "Duplex 2205 (S31803)", 1.94e11, 1.30e-5, 2.41e8, 2.41e8, 7800),
  material("A790-S32750", "Super Duplex 2507 (S32750)", 1.95e11, 1.30e-5, 3.10e8, 3.10e8, 7800),
  // Nickel
  material("B444-N06625", "Inconel 625", 2.07e11, 1.28e-5, 2.75e8, 2.75e8, 8440),
  material("B167-N06600", "Inconel 600", 2.07e11, 1.33e-5, 2.07e8, 2.07e8, 8420),
  material("B407-N08800", "Incoloy 800", 1.96e11, 1.44e-5, 1.52e8, 1.52e8, 7940),
  material("B407-N08810", "Incoloy 800H", 1.96e11, 1.44e-5, 1.52e8, 1.52e8, 7940),
  material("B622-N10276", "Hastelloy C-276", 2.05e11, 1.12e-5, 2.83e8, 2.83e8, 8890),
  // Copper
  material("B88-K", "B88 Type K Copper", 1.17e11, 1.70e-5, 4.14e7, 4.14e7, 8940, 0.34),
  material("B88-L", "B88 Type L Copper", 1.17e11, 1.70e-5, 4.14e7, 4.14e7, 8940, 0.34),
  material("B88-M", "B88 Type M Copper (thin-wall)", 1.17e11, 1.70e-5, 4.14e7, 4.14e7, 8940, 0.34),
  material("B111-C70600", "90-10 Cu-Ni (seawater)", 1.38e11, 1.71e-5, 6.9e7, 6.9e7, 8900, 0.33),
  // Aluminum
  material("AL-6061", "Aluminum 6061-T6", 6.9e10, 2.36e-5, 8.27e7, 8.27e7, 2700, 0.33),
  material("AL-6063", "Aluminum 6063-T6", 6.9e10, 2.34e-5, 5.86e7, 5.86e7, 2700, 0.33),
  material("AL-3003", "Aluminum 3003-H14", 6.9e10, 2.32e-5, 5.5e7, 5.5e7, 2730, 0.33),
  material("AL-5052", "Aluminum 5052-H32 (marine)", 6.9e10, 2.38e-5, 9.6e7, 9.6e7, 2680, 0.33),
  // Titanium
  material("TI-GR2", "Titanium Grade 2", 1.03e11, 8.6e-6, 9.3e7, 9.3e7, 4510, 0.34),
  material("TI-GR7", "Titanium Grade 7 (Ti-0.2Pd)", 1.03e11, 8.6e-6, 9.6e7, 9.6e7, 4510, 0.34),
  material("TI-6AL-4V", "Titanium 6Al-4V", 1.14e11, 8.6e-6, 2.41e8, 2.41e8, 4430, 0.34),
  // Plastics + composites
  material("HDPE-PE100", "HDPE PE100", 9e8, 1.4e-4, 6.3e6, 6.3e6, 950, 0.45),
  material("PVC-SCH80", "PVC SCH 80", 3.1e9, 5.4e-5, 1.38e7, 1.38e7, 1400, 0.4),
  material("CPVC", "CPVC (hot-water, chemical)", 3.1e9, 6.3e-5, 1.38e7, 1.38e7, 1550, 0.4),
  material("PP-H", "Polypropylene Homopolymer", 1.4e9, 1.5e-4, 8.3e6, 8.3e6, 910, 0.42),
  material("PVDF", "PVDF (Teflon-like)", 1.4e9, 1.3e-4, 2e7, 2e7, 1780, 0.4),
  material("PTFE", "PTFE (Teflon)", 5e8, 1.2e-4, 1.5e7, 1.5e7, 2200, 0.46),
  material("GRE", "Glass-Reinforced Epoxy", 2.1e10, 1.8e-5, 1.3e8, 1.3e8, 1900, 0.28),
];


function section(id: string, od_mm: number, wall_mm: number): PipeSection {
  return { id, outside_diameter: od_mm / 1000, wall_thickness: wall_mm / 1000 };
}

// Trimmed B36.10 schedule catalog — common sizes only
export const SECTION_CATALOG: PipeSection[] = [
  section("NPS-1/2-SCH40", 21.3, 2.77),
  section("NPS-3/4-SCH40", 26.7, 2.87),
  section("NPS-1-SCH40", 33.4, 3.38),
  section("NPS-1-1/2-SCH40", 48.3, 3.68),
  section("NPS-2-SCH40", 60.3, 3.91),
  section("NPS-3-SCH40", 88.9, 5.49),
  section("NPS-4-SCH40", 114.3, 6.02),
  section("NPS-6-SCH40", 168.3, 7.11),
  section("NPS-8-SCH40", 219.1, 8.18),
  section("NPS-10-SCH40", 273.1, 9.27),
  section("NPS-12-SCH40", 323.9, 10.31),
  section("NPS-16-SCH40", 406.4, 12.70),
  section("NPS-20-SCH40", 508.0, 15.09),
  section("NPS-24-SCH40", 609.6, 17.48),
  section("NPS-6-SCH80", 168.3, 10.97),
  section("NPS-8-SCH80", 219.1, 12.70),
  section("NPS-12-SCH80", 323.9, 17.48),
  section("NPS-6-SCH160", 168.3, 18.26),
  section("NPS-8-SCH160", 219.1, 23.01),
  section("NPS-4-XXS", 114.3, 17.12),
  section("NPS-6-XXS", 168.3, 21.95),
  section("NPS-3-STD", 88.9, 5.49),
  section("NPS-4-STD", 114.3, 6.02),
  section("NPS-6-STD", 168.3, 7.11),
];

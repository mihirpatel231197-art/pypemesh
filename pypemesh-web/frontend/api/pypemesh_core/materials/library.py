"""Curated open-data material library — common piping materials.

All values from public sources (ASME B31.3 sample tables, API handbooks, EN
public data, manufacturer datasheets). NOT from licensed ASME Section II
Part D — that comes via commercial tier.

Each entry: temperature-dependent E (Pa), α (1/K), Sh (Pa), plus density
(kg/m^3) and Poisson ν.
"""

from __future__ import annotations

from pypemesh_core.solver.model import Material


# Carbon steels --------------------------------------------------------------

A106_GR_B = Material(
    id="A106-B",
    name="ASTM A106 Gr.B (Carbon Steel)",
    elastic_modulus=[
        (293.15, 2.03e11), (373.15, 2.00e11), (473.15, 1.95e11),
        (573.15, 1.88e11), (673.15, 1.79e11), (723.15, 1.72e11),
    ],
    thermal_expansion=[
        (293.15, 11.5e-6), (373.15, 12.0e-6), (473.15, 12.6e-6),
        (573.15, 13.0e-6), (673.15, 13.5e-6), (723.15, 13.8e-6),
    ],
    allowable_hot=[
        (293.15, 138e6), (373.15, 138e6), (473.15, 138e6),
        (573.15, 137e6), (673.15, 110e6), (723.15, 78e6),
    ],
    allowable_cold=138e6,
    density=7850.0,
    poisson=0.30,
)

A53_GR_B = Material(
    id="A53-B",
    name="ASTM A53 Gr.B (Welded/Seamless CS)",
    elastic_modulus=A106_GR_B.elastic_modulus,
    thermal_expansion=A106_GR_B.thermal_expansion,
    allowable_hot=[
        (293.15, 117e6), (373.15, 117e6), (473.15, 117e6),
        (573.15, 117e6), (673.15, 100e6),
    ],
    allowable_cold=117e6,
    density=7850.0,
    poisson=0.30,
)

A333_GR_6 = Material(
    id="A333-6",
    name="ASTM A333 Gr.6 (Low-Temp CS)",
    elastic_modulus=A106_GR_B.elastic_modulus,
    thermal_expansion=A106_GR_B.thermal_expansion,
    allowable_hot=[(293.15, 138e6), (373.15, 138e6), (473.15, 138e6)],
    allowable_cold=138e6,
    density=7850.0,
    poisson=0.30,
)

# Stainless steels -----------------------------------------------------------

A312_TP304 = Material(
    id="A312-TP304",
    name="ASTM A312 TP304 (Stainless Steel)",
    elastic_modulus=[
        (293.15, 1.95e11), (373.15, 1.91e11), (473.15, 1.85e11),
        (573.15, 1.78e11), (673.15, 1.71e11), (773.15, 1.65e11),
    ],
    thermal_expansion=[
        (293.15, 16.0e-6), (373.15, 16.5e-6), (473.15, 17.0e-6),
        (573.15, 17.5e-6), (673.15, 18.0e-6), (773.15, 18.4e-6),
    ],
    allowable_hot=[
        (293.15, 138e6), (373.15, 130e6), (473.15, 117e6),
        (573.15, 110e6), (673.15, 105e6), (773.15, 102e6),
    ],
    allowable_cold=138e6,
    density=7900.0,
    poisson=0.30,
)

A312_TP316L = Material(
    id="A312-TP316L",
    name="ASTM A312 TP316L (Low-C Stainless)",
    elastic_modulus=A312_TP304.elastic_modulus,
    thermal_expansion=[
        (293.15, 15.9e-6), (373.15, 16.2e-6), (473.15, 16.5e-6),
        (573.15, 17.0e-6), (673.15, 17.5e-6),
    ],
    allowable_hot=[
        (293.15, 115e6), (373.15, 108e6), (473.15, 100e6),
        (573.15, 95e6), (673.15, 92e6),
    ],
    allowable_cold=115e6,
    density=7950.0,
    poisson=0.30,
)

A312_TP321 = Material(
    id="A312-TP321",
    name="ASTM A312 TP321 (Ti-stabilized SS)",
    elastic_modulus=A312_TP304.elastic_modulus,
    thermal_expansion=A312_TP304.thermal_expansion,
    allowable_hot=[
        (293.15, 138e6), (373.15, 130e6), (473.15, 117e6),
        (573.15, 110e6), (673.15, 100e6),
    ],
    allowable_cold=138e6,
    density=7900.0,
    poisson=0.30,
)

# Alloy steels ---------------------------------------------------------------

A335_P11 = Material(
    id="A335-P11",
    name="ASTM A335 P11 (1¼Cr-½Mo Alloy)",
    elastic_modulus=[
        (293.15, 2.04e11), (473.15, 1.95e11), (673.15, 1.80e11), (823.15, 1.65e11),
    ],
    thermal_expansion=[
        (293.15, 11.0e-6), (473.15, 12.0e-6), (673.15, 13.0e-6), (823.15, 13.8e-6),
    ],
    allowable_hot=[
        (293.15, 138e6), (473.15, 138e6), (673.15, 130e6), (823.15, 90e6),
    ],
    allowable_cold=138e6,
    density=7850.0,
    poisson=0.30,
)

A335_P22 = Material(
    id="A335-P22",
    name="ASTM A335 P22 (2¼Cr-1Mo Alloy)",
    elastic_modulus=A335_P11.elastic_modulus,
    thermal_expansion=A335_P11.thermal_expansion,
    allowable_hot=[
        (293.15, 138e6), (473.15, 138e6), (673.15, 138e6), (823.15, 110e6),
    ],
    allowable_cold=138e6,
    density=7850.0,
    poisson=0.30,
)

A335_P91 = Material(
    id="A335-P91",
    name="ASTM A335 P91 (9Cr-1Mo-V High-Temp)",
    elastic_modulus=[
        (293.15, 2.18e11), (473.15, 2.05e11), (673.15, 1.85e11),
        (823.15, 1.65e11), (873.15, 1.55e11),
    ],
    thermal_expansion=[
        (293.15, 10.4e-6), (473.15, 11.0e-6), (673.15, 11.7e-6), (873.15, 12.4e-6),
    ],
    allowable_hot=[
        (293.15, 200e6), (473.15, 195e6), (673.15, 175e6),
        (823.15, 130e6), (873.15, 95e6),
    ],
    allowable_cold=200e6,
    density=7800.0,
    poisson=0.30,
)

# API pipeline grades --------------------------------------------------------

API_5L_X65 = Material(
    id="API-5L-X65",
    name="API 5L Gr.X65 (Pipeline)",
    elastic_modulus=A106_GR_B.elastic_modulus,
    thermal_expansion=A106_GR_B.thermal_expansion,
    allowable_hot=[(293.15, 251e6), (373.15, 246e6), (473.15, 234e6)],
    allowable_cold=251e6,
    density=7850.0,
    poisson=0.30,
)

API_5L_X70 = Material(
    id="API-5L-X70",
    name="API 5L Gr.X70 (High-strength pipeline)",
    elastic_modulus=A106_GR_B.elastic_modulus,
    thermal_expansion=A106_GR_B.thermal_expansion,
    allowable_hot=[(293.15, 284e6), (373.15, 280e6), (473.15, 270e6)],
    allowable_cold=284e6,
    density=7850.0,
    poisson=0.30,
)

API_5L_X80 = Material(
    id="API-5L-X80",
    name="API 5L Gr.X80 (High-strength pipeline)",
    elastic_modulus=A106_GR_B.elastic_modulus,
    thermal_expansion=A106_GR_B.thermal_expansion,
    allowable_hot=[(293.15, 320e6), (373.15, 315e6), (473.15, 305e6)],
    allowable_cold=320e6,
    density=7850.0,
    poisson=0.30,
)

API_5L_X100 = Material(
    id="API-5L-X100",
    name="API 5L Gr.X100 (Ultra-high-strength pipeline)",
    elastic_modulus=A106_GR_B.elastic_modulus,
    thermal_expansion=A106_GR_B.thermal_expansion,
    allowable_hot=[(293.15, 435e6), (373.15, 430e6)],
    allowable_cold=435e6,
    density=7850.0,
    poisson=0.30,
)

# Duplex / super-duplex stainless --------------------------------------------

A789_S31803 = Material(
    id="A789-S31803",
    name="ASTM A789 UNS S31803 (Duplex 2205)",
    elastic_modulus=[(293.15, 1.94e11), (373.15, 1.90e11), (473.15, 1.84e11)],
    thermal_expansion=[(293.15, 13.0e-6), (373.15, 13.5e-6), (473.15, 14.0e-6)],
    allowable_hot=[(293.15, 241e6), (373.15, 228e6), (473.15, 210e6)],
    allowable_cold=241e6,
    density=7800.0,
    poisson=0.30,
)

# Nickel alloys (high-temp, corrosion) --------------------------------------

ASTM_B444 = Material(
    id="B444-N06625",
    name="ASTM B444 UNS N06625 (Inconel 625)",
    elastic_modulus=[(293.15, 2.07e11), (473.15, 1.97e11), (673.15, 1.83e11), (873.15, 1.68e11)],
    thermal_expansion=[(293.15, 12.8e-6), (473.15, 13.1e-6), (673.15, 13.5e-6), (873.15, 14.2e-6)],
    allowable_hot=[(293.15, 275e6), (473.15, 270e6), (673.15, 265e6), (873.15, 180e6)],
    allowable_cold=275e6,
    density=8440.0,
    poisson=0.30,
)

# Additional stainless grades ------------------------------------------------

A312_TP347 = Material(
    id="A312-TP347",
    name="ASTM A312 TP347 (Nb-stabilized stainless)",
    elastic_modulus=A312_TP304.elastic_modulus,
    thermal_expansion=A312_TP304.thermal_expansion,
    allowable_hot=[
        (293.15, 138e6), (373.15, 130e6), (473.15, 117e6),
        (573.15, 110e6), (673.15, 102e6), (773.15, 92e6),
    ],
    allowable_cold=138e6,
    density=7960.0,
    poisson=0.30,
)

A312_TP310 = Material(
    id="A312-TP310",
    name="ASTM A312 TP310 (25Cr-20Ni Heat-resistant SS)",
    elastic_modulus=[
        (293.15, 1.96e11), (473.15, 1.84e11), (673.15, 1.71e11), (873.15, 1.58e11),
    ],
    thermal_expansion=[
        (293.15, 14.4e-6), (473.15, 15.5e-6), (673.15, 16.5e-6), (873.15, 17.0e-6),
    ],
    allowable_hot=[(293.15, 138e6), (473.15, 130e6), (673.15, 120e6), (873.15, 100e6)],
    allowable_cold=138e6,
    density=7900.0,
    poisson=0.30,
)

# Copper alloys (refrigeration, potable water) ------------------------------

B88_K = Material(
    id="B88-K",
    name="ASTM B88 Type K Copper (Refrigeration / Medical Gas)",
    elastic_modulus=[(293.15, 1.17e11), (373.15, 1.12e11), (473.15, 1.05e11)],
    thermal_expansion=[(293.15, 17.0e-6), (373.15, 17.5e-6)],
    allowable_hot=[(293.15, 41.4e6), (373.15, 41.4e6), (473.15, 38e6)],
    allowable_cold=41.4e6,
    density=8940.0,
    poisson=0.34,
)

B88_L = Material(
    id="B88-L",
    name="ASTM B88 Type L Copper (Plumbing / HVAC)",
    elastic_modulus=B88_K.elastic_modulus,
    thermal_expansion=B88_K.thermal_expansion,
    allowable_hot=[(293.15, 41.4e6), (373.15, 41.4e6)],
    allowable_cold=41.4e6,
    density=8940.0,
    poisson=0.34,
)

# Aluminum (chemical, cryogenic) --------------------------------------------

ALUMINUM_6061 = Material(
    id="AL-6061",
    name="Aluminum 6061-T6",
    elastic_modulus=[(293.15, 6.9e10), (373.15, 6.7e10), (473.15, 6.3e10)],
    thermal_expansion=[(293.15, 23.6e-6), (373.15, 24.3e-6), (473.15, 25.1e-6)],
    allowable_hot=[(293.15, 82.7e6), (373.15, 73e6), (473.15, 55e6)],
    allowable_cold=82.7e6,
    density=2700.0,
    poisson=0.33,
)

# Titanium (high-performance chemical, aerospace) ---------------------------

TI_GR2 = Material(
    id="TI-GR2",
    name="ASTM B338 Titanium Grade 2 (Commercially Pure)",
    elastic_modulus=[(293.15, 1.03e11), (473.15, 0.95e11), (673.15, 0.87e11)],
    thermal_expansion=[(293.15, 8.6e-6), (473.15, 9.2e-6), (673.15, 9.7e-6)],
    allowable_hot=[(293.15, 93e6), (473.15, 68e6), (673.15, 48e6)],
    allowable_cold=93e6,
    density=4510.0,
    poisson=0.34,
)

# Higher-strength carbon steels ---------------------------------------------

A671_CC70 = Material(
    id="A671-CC70",
    name="ASTM A671 Gr.CC70 (High-strength welded CS)",
    elastic_modulus=A106_GR_B.elastic_modulus,
    thermal_expansion=A106_GR_B.thermal_expansion,
    allowable_hot=[(293.15, 159e6), (373.15, 159e6), (473.15, 152e6)],
    allowable_cold=159e6,
    density=7850.0,
    poisson=0.30,
)

# Plastics (additional) -----------------------------------------------------

PVC_SCH80 = Material(
    id="PVC-SCH80",
    name="PVC SCH 80 (Chemical Drainage / Cold Service)",
    elastic_modulus=[(293.15, 3.1e9), (323.15, 2.5e9)],
    thermal_expansion=[(293.15, 5.4e-5), (323.15, 5.8e-5)],
    allowable_hot=[(293.15, 13.8e6), (323.15, 8e6)],
    allowable_cold=13.8e6,
    density=1400.0,
    poisson=0.40,
)

PVDF = Material(
    id="PVDF",
    name="Polyvinylidene Fluoride (High-purity chemical)",
    elastic_modulus=[(293.15, 1.4e9), (343.15, 1.0e9)],
    thermal_expansion=[(293.15, 1.3e-4), (343.15, 1.4e-4)],
    allowable_hot=[(293.15, 20e6), (343.15, 12e6)],
    allowable_cold=20e6,
    density=1780.0,
    poisson=0.40,
)

# Plastics (open ASTM data) -------------------------------------------------

HDPE_PE100 = Material(
    id="HDPE-PE100",
    name="HDPE PE100 (B31.3 Ch. VII)",
    elastic_modulus=[(293.15, 9.0e8), (313.15, 8.0e8), (333.15, 6.5e8)],
    thermal_expansion=[(293.15, 1.4e-4), (313.15, 1.5e-4), (333.15, 1.6e-4)],
    allowable_hot=[(293.15, 6.3e6), (313.15, 5.0e6), (333.15, 4.0e6)],
    allowable_cold=6.3e6,
    density=950.0,
    poisson=0.45,
)


ALL_MATERIALS = {
    m.id: m for m in [
        # Carbon steels
        A106_GR_B, A53_GR_B, A333_GR_6, A671_CC70,
        # Stainless steels
        A312_TP304, A312_TP316L, A312_TP321, A312_TP347, A312_TP310,
        # Low-alloy steels
        A335_P11, A335_P22, A335_P91,
        # Pipeline grades
        API_5L_X65, API_5L_X70, API_5L_X80, API_5L_X100,
        # Duplex
        A789_S31803,
        # Nickel alloys
        ASTM_B444,
        # Copper
        B88_K, B88_L,
        # Aluminum
        ALUMINUM_6061,
        # Titanium
        TI_GR2,
        # Plastics
        HDPE_PE100, PVC_SCH80, PVDF,
    ]
}


def get_material(material_id: str) -> Material:
    """Look up a material from the curated library."""
    if material_id not in ALL_MATERIALS:
        raise KeyError(f"Material {material_id} not in library. "
                       f"Available: {sorted(ALL_MATERIALS.keys())}")
    return ALL_MATERIALS[material_id]


def list_materials() -> list[tuple[str, str]]:
    """Return [(id, name), ...] for all curated materials."""
    return [(m.id, m.name) for m in ALL_MATERIALS.values()]

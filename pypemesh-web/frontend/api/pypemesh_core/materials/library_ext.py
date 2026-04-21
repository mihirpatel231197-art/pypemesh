"""Extended material library — additional 25 materials to reach the B-F5
target of 50 curated materials at launch.

All values from public / open data (ASME sample tables for allowable,
published manufacturer datasheets for E/α, DIN/EN public tables). Licensed
ASME Section II Part D values deferred to the commercial tier.
"""

from __future__ import annotations

from pypemesh_core.solver.model import Material


# Additional carbon steels ---------------------------------------------------

A672_C70 = Material(
    id="A672-C70",
    name="ASTM A672 Gr.C70 (Heat-treated welded CS for high-pressure)",
    elastic_modulus=[(293.15, 2.03e11), (373.15, 2.00e11), (473.15, 1.95e11)],
    thermal_expansion=[(293.15, 11.5e-6), (373.15, 12.0e-6)],
    allowable_hot=[(293.15, 159e6), (373.15, 159e6), (473.15, 159e6)],
    allowable_cold=159e6,
    density=7850.0,
    poisson=0.30,
)

A350_LF2 = Material(
    id="A350-LF2",
    name="ASTM A350 Gr.LF2 (Low-temp forged CS)",
    elastic_modulus=[(293.15, 2.03e11), (223.15, 2.05e11), (373.15, 2.00e11)],
    thermal_expansion=[(293.15, 11.2e-6), (223.15, 10.5e-6), (373.15, 11.8e-6)],
    allowable_hot=[(293.15, 138e6), (373.15, 138e6)],
    allowable_cold=138e6,
    density=7850.0,
    poisson=0.30,
)

A420_WPL6 = Material(
    id="A420-WPL6",
    name="ASTM A420 Gr.WPL6 (Low-temp CS fitting)",
    elastic_modulus=[(293.15, 2.03e11), (223.15, 2.05e11)],
    thermal_expansion=[(293.15, 11.2e-6)],
    allowable_hot=[(293.15, 138e6)],
    allowable_cold=138e6,
    density=7850.0,
    poisson=0.30,
)

# Additional stainless grades ------------------------------------------------

A312_TP316 = Material(
    id="A312-TP316",
    name="ASTM A312 TP316 (Standard SS, Mo-bearing)",
    elastic_modulus=[(293.15, 1.95e11), (473.15, 1.85e11), (673.15, 1.71e11)],
    thermal_expansion=[(293.15, 15.9e-6), (473.15, 16.5e-6), (673.15, 17.0e-6)],
    allowable_hot=[(293.15, 138e6), (473.15, 117e6), (673.15, 108e6)],
    allowable_cold=138e6,
    density=7950.0,
    poisson=0.30,
)

A312_TP317 = Material(
    id="A312-TP317",
    name="ASTM A312 TP317 (Higher-Mo SS)",
    elastic_modulus=[(293.15, 1.95e11), (473.15, 1.85e11)],
    thermal_expansion=[(293.15, 16.0e-6), (473.15, 16.5e-6)],
    allowable_hot=[(293.15, 138e6), (473.15, 120e6)],
    allowable_cold=138e6,
    density=7950.0,
    poisson=0.30,
)

A312_TP309 = Material(
    id="A312-TP309",
    name="ASTM A312 TP309 (Heat-resistant SS)",
    elastic_modulus=[(293.15, 1.96e11), (673.15, 1.71e11), (873.15, 1.58e11)],
    thermal_expansion=[(293.15, 14.9e-6), (673.15, 17.2e-6)],
    allowable_hot=[(293.15, 138e6), (673.15, 112e6), (873.15, 78e6)],
    allowable_cold=138e6,
    density=7900.0,
    poisson=0.30,
)

A312_TP904L = Material(
    id="A312-TP904L",
    name="ASTM A312 TP904L (High-Ni SS, chloride-resistant)",
    elastic_modulus=[(293.15, 1.95e11), (473.15, 1.85e11)],
    thermal_expansion=[(293.15, 15.8e-6), (473.15, 16.4e-6)],
    allowable_hot=[(293.15, 172e6), (473.15, 155e6)],
    allowable_cold=172e6,
    density=7950.0,
    poisson=0.30,
)

# Super-duplex + super-austenitic -------------------------------------------

A790_S32750 = Material(
    id="A790-S32750",
    name="ASTM A790 UNS S32750 (Super Duplex 2507)",
    elastic_modulus=[(293.15, 1.95e11), (373.15, 1.91e11), (473.15, 1.85e11)],
    thermal_expansion=[(293.15, 13.0e-6), (373.15, 13.5e-6)],
    allowable_hot=[(293.15, 310e6), (373.15, 290e6), (473.15, 270e6)],
    allowable_cold=310e6,
    density=7800.0,
    poisson=0.30,
)

# Low-alloy steels -----------------------------------------------------------

A335_P5 = Material(
    id="A335-P5",
    name="ASTM A335 P5 (5Cr-½Mo, high-temp service)",
    elastic_modulus=[(293.15, 2.04e11), (473.15, 1.94e11), (673.15, 1.80e11)],
    thermal_expansion=[(293.15, 11.0e-6), (473.15, 12.0e-6)],
    allowable_hot=[(293.15, 138e6), (473.15, 138e6), (673.15, 121e6)],
    allowable_cold=138e6,
    density=7850.0,
    poisson=0.30,
)

A335_P9 = Material(
    id="A335-P9",
    name="ASTM A335 P9 (9Cr-1Mo)",
    elastic_modulus=[(293.15, 2.18e11), (473.15, 2.05e11), (673.15, 1.85e11)],
    thermal_expansion=[(293.15, 10.4e-6), (473.15, 11.0e-6)],
    allowable_hot=[(293.15, 165e6), (473.15, 160e6), (673.15, 145e6)],
    allowable_cold=165e6,
    density=7800.0,
    poisson=0.30,
)

A335_P92 = Material(
    id="A335-P92",
    name="ASTM A335 P92 (9Cr-2W advanced high-temp)",
    elastic_modulus=[(293.15, 2.18e11), (673.15, 1.85e11), (873.15, 1.55e11)],
    thermal_expansion=[(293.15, 10.4e-6), (673.15, 11.7e-6), (873.15, 12.4e-6)],
    allowable_hot=[(293.15, 275e6), (673.15, 220e6), (873.15, 120e6)],
    allowable_cold=275e6,
    density=7800.0,
    poisson=0.30,
)

# Nickel alloys --------------------------------------------------------------

N06600 = Material(
    id="B167-N06600",
    name="ASTM B167 UNS N06600 (Inconel 600)",
    elastic_modulus=[(293.15, 2.07e11), (473.15, 1.97e11), (673.15, 1.83e11)],
    thermal_expansion=[(293.15, 13.3e-6), (473.15, 13.7e-6)],
    allowable_hot=[(293.15, 207e6), (473.15, 200e6), (673.15, 190e6)],
    allowable_cold=207e6,
    density=8420.0,
    poisson=0.30,
)

N08800 = Material(
    id="B407-N08800",
    name="ASTM B407 UNS N08800 (Incoloy 800)",
    elastic_modulus=[(293.15, 1.96e11), (473.15, 1.88e11), (673.15, 1.75e11)],
    thermal_expansion=[(293.15, 14.4e-6), (473.15, 15.0e-6)],
    allowable_hot=[(293.15, 152e6), (473.15, 145e6), (673.15, 130e6)],
    allowable_cold=152e6,
    density=7940.0,
    poisson=0.30,
)

N08810 = Material(
    id="B407-N08810",
    name="ASTM B407 UNS N08810 (Incoloy 800H, high-temp)",
    elastic_modulus=[(293.15, 1.96e11), (673.15, 1.75e11), (873.15, 1.60e11)],
    thermal_expansion=[(293.15, 14.4e-6), (673.15, 16.0e-6)],
    allowable_hot=[(293.15, 152e6), (673.15, 140e6), (873.15, 95e6)],
    allowable_cold=152e6,
    density=7940.0,
    poisson=0.30,
)

N10276 = Material(
    id="B622-N10276",
    name="ASTM B622 UNS N10276 (Hastelloy C-276)",
    elastic_modulus=[(293.15, 2.05e11), (473.15, 1.97e11), (673.15, 1.85e11)],
    thermal_expansion=[(293.15, 11.2e-6), (473.15, 11.8e-6)],
    allowable_hot=[(293.15, 283e6), (473.15, 275e6), (673.15, 260e6)],
    allowable_cold=283e6,
    density=8890.0,
    poisson=0.30,
)

# Aluminum alloys ------------------------------------------------------------

ALUMINUM_3003 = Material(
    id="AL-3003",
    name="Aluminum 3003-H14 (Mn alloy, general)",
    elastic_modulus=[(293.15, 6.9e10), (373.15, 6.7e10)],
    thermal_expansion=[(293.15, 23.2e-6), (373.15, 24.0e-6)],
    allowable_hot=[(293.15, 55e6), (373.15, 48e6)],
    allowable_cold=55e6,
    density=2730.0,
    poisson=0.33,
)

ALUMINUM_5052 = Material(
    id="AL-5052",
    name="Aluminum 5052-H32 (Mg alloy, marine)",
    elastic_modulus=[(293.15, 6.9e10)],
    thermal_expansion=[(293.15, 23.8e-6)],
    allowable_hot=[(293.15, 96e6)],
    allowable_cold=96e6,
    density=2680.0,
    poisson=0.33,
)

ALUMINUM_6063 = Material(
    id="AL-6063",
    name="Aluminum 6063-T6 (Architectural, extrusions)",
    elastic_modulus=[(293.15, 6.9e10)],
    thermal_expansion=[(293.15, 23.4e-6)],
    allowable_hot=[(293.15, 58.6e6)],
    allowable_cold=58.6e6,
    density=2700.0,
    poisson=0.33,
)

# Titanium alloys ------------------------------------------------------------

TI_GR7 = Material(
    id="TI-GR7",
    name="ASTM B338 Titanium Grade 7 (Ti-0.2Pd, corrosion)",
    elastic_modulus=[(293.15, 1.03e11), (473.15, 0.95e11)],
    thermal_expansion=[(293.15, 8.6e-6), (473.15, 9.2e-6)],
    allowable_hot=[(293.15, 96e6), (473.15, 70e6)],
    allowable_cold=96e6,
    density=4510.0,
    poisson=0.34,
)

TI_6AL4V = Material(
    id="TI-6AL-4V",
    name="Titanium 6Al-4V (Grade 5, high-strength)",
    elastic_modulus=[(293.15, 1.14e11), (473.15, 1.06e11)],
    thermal_expansion=[(293.15, 8.6e-6), (473.15, 9.1e-6)],
    allowable_hot=[(293.15, 241e6), (473.15, 225e6)],
    allowable_cold=241e6,
    density=4430.0,
    poisson=0.34,
)

# Copper + copper alloys ----------------------------------------------------

B88_M = Material(
    id="B88-M",
    name="ASTM B88 Type M Copper (Thin-wall plumbing)",
    elastic_modulus=[(293.15, 1.17e11)],
    thermal_expansion=[(293.15, 17.0e-6)],
    allowable_hot=[(293.15, 41.4e6)],
    allowable_cold=41.4e6,
    density=8940.0,
    poisson=0.34,
)

B111_C70600 = Material(
    id="B111-C70600",
    name="ASTM B111 C70600 (90-10 Cu-Ni, seawater)",
    elastic_modulus=[(293.15, 1.38e11)],
    thermal_expansion=[(293.15, 17.1e-6)],
    allowable_hot=[(293.15, 69e6)],
    allowable_cold=69e6,
    density=8900.0,
    poisson=0.33,
)

# Additional plastics + composites ------------------------------------------

CPVC = Material(
    id="CPVC",
    name="Chlorinated PVC (Hot-water, chemical)",
    elastic_modulus=[(293.15, 3.1e9), (333.15, 2.5e9)],
    thermal_expansion=[(293.15, 6.3e-5)],
    allowable_hot=[(293.15, 13.8e6), (333.15, 8e6)],
    allowable_cold=13.8e6,
    density=1550.0,
    poisson=0.40,
)

PP_H = Material(
    id="PP-H",
    name="Polypropylene Homopolymer (Chemical, acidic)",
    elastic_modulus=[(293.15, 1.4e9), (333.15, 1.0e9)],
    thermal_expansion=[(293.15, 1.5e-4)],
    allowable_hot=[(293.15, 8.3e6), (333.15, 5e6)],
    allowable_cold=8.3e6,
    density=910.0,
    poisson=0.42,
)

PTFE = Material(
    id="PTFE",
    name="PTFE (Teflon, extreme chemical resistance)",
    elastic_modulus=[(293.15, 5.0e8)],
    thermal_expansion=[(293.15, 1.2e-4)],
    allowable_hot=[(293.15, 15e6)],
    allowable_cold=15e6,
    density=2200.0,
    poisson=0.46,
)

GRE_FILAMENT = Material(
    id="GRE",
    name="Glass-Reinforced Epoxy (Filament-wound, offshore)",
    elastic_modulus=[(293.15, 2.1e10)],
    thermal_expansion=[(293.15, 1.8e-5)],
    allowable_hot=[(293.15, 130e6)],
    allowable_cold=130e6,
    density=1900.0,
    poisson=0.28,
)


EXTENDED_MATERIALS = {
    m.id: m for m in [
        A672_C70, A350_LF2, A420_WPL6,
        A312_TP316, A312_TP317, A312_TP309, A312_TP904L,
        A790_S32750,
        A335_P5, A335_P9, A335_P92,
        N06600, N08800, N08810, N10276,
        ALUMINUM_3003, ALUMINUM_5052, ALUMINUM_6063,
        TI_GR7, TI_6AL4V,
        B88_M, B111_C70600,
        CPVC, PP_H, PTFE, GRE_FILAMENT,
    ]
}

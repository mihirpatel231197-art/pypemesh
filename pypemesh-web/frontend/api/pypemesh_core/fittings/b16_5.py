"""ASME B16.5 — Pipe Flanges and Flanged Fittings — simplified dimensions.

Provides raised-face flange outside diameter and thickness per pressure
class (150, 300, 600, 900, 1500, 2500). Used for mass/weight modelling in
pipe stress analysis.

Reference: ASME B16.5-2020. Values from public standard, simplified.
"""

from __future__ import annotations


# Simplified flange outer diameter (mm) by class and NPS. RF (raised face).
# Weight can be estimated from OD, thickness, and pipe bore.
# Not exhaustive — covers NPS 1" through 24" for primary classes.
# Reference: ASME B16.5 public tables.
FLANGE_OD_MM: dict[tuple[int, str], float] = {
    # (class, nps) → flange OD mm
    (150, "NPS-1"):    108,  (150, "NPS-2"):   152,  (150, "NPS-3"):   190,
    (150, "NPS-4"):    229,  (150, "NPS-6"):   279,  (150, "NPS-8"):   343,
    (150, "NPS-10"):   406,  (150, "NPS-12"):  483,  (150, "NPS-16"):  597,
    (150, "NPS-20"):   699,  (150, "NPS-24"):  813,
    (300, "NPS-1"):    124,  (300, "NPS-2"):   165,  (300, "NPS-3"):   210,
    (300, "NPS-4"):    254,  (300, "NPS-6"):   318,  (300, "NPS-8"):   381,
    (300, "NPS-10"):   445,  (300, "NPS-12"):  521,  (300, "NPS-16"):  648,
    (300, "NPS-20"):   775,  (300, "NPS-24"):  915,
    (600, "NPS-2"):    165,  (600, "NPS-4"):   273,  (600, "NPS-6"):   356,
    (600, "NPS-8"):    419,  (600, "NPS-12"):  559,  (600, "NPS-16"):  705,
    (900, "NPS-4"):    292,  (900, "NPS-8"):   470,  (900, "NPS-12"):  610,
    (1500, "NPS-4"):   311,  (1500, "NPS-6"):  394,  (1500, "NPS-8"):  483,
    (2500, "NPS-4"):   357,  (2500, "NPS-6"):  483,  (2500, "NPS-8"):  552,
}

# Approximate flange thickness (mm)
FLANGE_THICK_MM: dict[tuple[int, str], float] = {
    (150, "NPS-6"):  24,  (150, "NPS-12"):  32,
    (300, "NPS-6"):  32,  (300, "NPS-12"):  44,
    (600, "NPS-6"):  38,  (600, "NPS-12"):  57,
    (900, "NPS-8"):  51,  (900, "NPS-12"):  76,
    (1500, "NPS-8"): 57,  (1500, "NPS-12"): 83,
}


def flange_outside_diameter(pressure_class: int, nps: str) -> float:
    """Flange OD in meters."""
    key = (pressure_class, nps)
    if key not in FLANGE_OD_MM:
        raise KeyError(f"No flange OD data for class {pressure_class} {nps}")
    return FLANGE_OD_MM[key] / 1000.0


def flange_thickness(pressure_class: int, nps: str) -> float:
    """Flange thickness in meters (approximate, for weight calc)."""
    key = (pressure_class, nps)
    if key not in FLANGE_THICK_MM:
        raise KeyError(f"No flange thickness data for class {pressure_class} {nps}")
    return FLANGE_THICK_MM[key] / 1000.0

"""ASME B16.9 — Factory-Made Wrought Butt-Welding Fittings — dimensions.

Provides bend radii and branch-length dimensions for standard butt-welded
fittings: elbows (SR / LR / 3D / 5D), tees (straight / reducing), reducers
(concentric / eccentric), caps, crosses.

For elbows, bend radius is the most commonly used parameter in stress
analysis (feeds the Karman flexibility calc and B31J SIF lookup).

Reference: ASME B16.9-2022. Values from public standard.
"""

from __future__ import annotations

from pypemesh_core.fittings.b36_10 import B36_10_TABLE


def elbow_bend_radius(nps: str, radius_class: str = "LR") -> float:
    """Standard bend radius for a butt-welded elbow per B16.9.

    Args:
        nps: Nominal pipe size (e.g. "NPS-6")
        radius_class: "SR" (short radius, = 1·NPS), "LR" (long radius, = 1.5·NPS),
                      "3D" (= 3·OD), "5D" (= 5·OD)

    Returns:
        Bend radius in meters.
    """
    if nps not in B36_10_TABLE:
        raise KeyError(f"Unknown NPS: {nps}")
    od_mm = B36_10_TABLE[nps][0]

    if radius_class == "SR":
        # Short radius: R = 1·NPS (nominal, in inches). Use OD as approx.
        return od_mm / 1000.0
    if radius_class == "LR":
        return 1.5 * od_mm / 1000.0
    if radius_class == "3D":
        return 3.0 * od_mm / 1000.0
    if radius_class == "5D":
        return 5.0 * od_mm / 1000.0
    raise ValueError(f"Unknown radius class: {radius_class}. Use SR/LR/3D/5D.")


# Simplified tee center-to-end lengths (mm) per B16.9, NPS range 1 through 24
# Reference values — full table available in the B16.9 standard.
TEE_C_TO_END_MM = {
    "NPS-1":    (38, 38),      # run / branch
    "NPS-2":    (64, 64),
    "NPS-3":    (86, 86),
    "NPS-4":    (105, 105),
    "NPS-6":    (143, 143),
    "NPS-8":    (178, 178),
    "NPS-10":   (216, 216),
    "NPS-12":   (254, 254),
    "NPS-14":   (279, 279),
    "NPS-16":   (305, 305),
    "NPS-18":   (343, 343),
    "NPS-20":   (381, 381),
    "NPS-24":   (432, 432),
}


def tee_dimensions(nps: str) -> tuple[float, float]:
    """Returns (run_length, branch_length) in meters for a B16.9 straight tee."""
    if nps not in TEE_C_TO_END_MM:
        raise KeyError(f"No TEE dimensions for {nps}")
    run_mm, br_mm = TEE_C_TO_END_MM[nps]
    return run_mm / 1000.0, br_mm / 1000.0

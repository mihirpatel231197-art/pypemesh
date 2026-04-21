"""Markl-based fatigue life prediction.

Markl's 1952 fatigue tests produced the empirical S-N relationship:

    i · S = C · N^(-0.2)

where:
- i = Stress Intensification Factor (from B31J)
- S = nominal bending stress range [Pa]
- N = cycles to failure
- C = material constant (245,000 psi ≈ 1.689 GPa for carbon steel)

Given applied stress range and SIF, solve for allowable cycles. Conversely,
given service cycles, compute the allowable stress range. Miner's rule
combines multiple stress ranges.

Reference: Markl, A.R.C. (1952). Fatigue Tests of Piping Components.
Trans. ASME 74, 287–303. ASME B31.3 Appendix D.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isinf
from typing import Literal


# Material constant C (Pa) — upper-bound envelope of Markl's data
MATERIAL_C: dict[str, float] = {
    "carbon_steel":      1.689e9,  # 245,000 psi
    "low_alloy":         1.689e9,
    "stainless_steel":   1.834e9,  # 266,000 psi (TP304/TP316 higher)
    "copper":            0.800e9,
    "aluminum":          0.600e9,
}

# B31.3 cycle factor f — multiplies SA for high cycle counts (§302.3.5)
# N ≤ 7000 → f=1.0; decreases with N per Table 302.3.5
def b31_3_cycle_factor(N: float) -> float:
    if N <= 7000:
        return 1.0
    if N <= 14_000:
        return 0.9
    if N <= 22_000:
        return 0.8
    if N <= 45_000:
        return 0.7
    if N <= 100_000:
        return 0.6
    if N <= 200_000:
        return 0.5
    if N <= 700_000:
        return 0.4
    if N <= 2_000_000:
        return 0.3
    return 0.2  # capped per §302.3.5


@dataclass
class FatigueRange:
    """A cyclic stress range to be accumulated."""

    name: str
    stress_range_pa: float
    sif: float
    n_cycles: float
    material_class: str = "carbon_steel"


def markl_allowable_cycles(
    stress_range_pa: float, sif: float, material_class: str = "carbon_steel"
) -> float:
    """Invert Markl's equation: N = (C / (i·S))^5."""
    effective = sif * stress_range_pa
    if effective <= 0:
        return float("inf")
    C = MATERIAL_C.get(material_class, MATERIAL_C["carbon_steel"])
    return (C / effective) ** 5


def markl_allowable_stress(
    n_cycles: float, sif: float, material_class: str = "carbon_steel"
) -> float:
    """Solve for S given a target life N: S = C / (i · N^0.2)."""
    if n_cycles <= 0 or sif <= 0:
        return float("inf")
    C = MATERIAL_C.get(material_class, MATERIAL_C["carbon_steel"])
    return C / (sif * (n_cycles ** 0.2))


def cumulative_damage(ranges: list[FatigueRange]) -> float:
    """Miner's rule: D = Σ n_i / N_i. D ≥ 1.0 means fatigue failure expected."""
    D = 0.0
    for r in ranges:
        N_allow = markl_allowable_cycles(r.stress_range_pa, r.sif, r.material_class)
        if not isinf(N_allow):
            D += r.n_cycles / N_allow
    return D

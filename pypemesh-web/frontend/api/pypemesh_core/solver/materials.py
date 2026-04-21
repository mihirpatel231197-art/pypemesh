"""Material property interpolation.

Linear interpolation between tabulated (T, value) points. SI units throughout —
temperatures in Kelvin, modulus in Pa, expansion in 1/K.
See docs/theory/PIPE_MECHANICS.md §2.4.
"""

from __future__ import annotations

from pypemesh_core.solver.model import Material


def _interpolate(table: list[tuple[float, float]], T: float) -> float:
    """Linear interpolation. Clamps to endpoints outside the table range."""
    if not table:
        raise ValueError("Empty property table")
    if len(table) == 1:
        return table[0][1]
    sorted_table = sorted(table, key=lambda pt: pt[0])
    if T <= sorted_table[0][0]:
        return sorted_table[0][1]
    if T >= sorted_table[-1][0]:
        return sorted_table[-1][1]
    for i in range(len(sorted_table) - 1):
        T0, v0 = sorted_table[i]
        T1, v1 = sorted_table[i + 1]
        if T0 <= T <= T1:
            return v0 + (v1 - v0) * (T - T0) / (T1 - T0)
    return sorted_table[-1][1]  # unreachable


def elastic_modulus_at(material: Material, T: float) -> float:
    """E(T) [Pa]."""
    return _interpolate(material.elastic_modulus, T)


def thermal_expansion_at(material: Material, T: float) -> float:
    """α(T) [1/K] — instantaneous coefficient."""
    return _interpolate(material.thermal_expansion, T)


def thermal_strain(material: Material, T_install: float, T_operate: float) -> float:
    """Thermal strain ε = ∫α dT, approximated as α_avg · ΔT.

    For more accurate work, use mean coefficient between install and operate
    temperatures (standard ASME approach).
    """
    alpha_install = thermal_expansion_at(material, T_install)
    alpha_operate = thermal_expansion_at(material, T_operate)
    alpha_mean = 0.5 * (alpha_install + alpha_operate)
    return alpha_mean * (T_operate - T_install)


def allowable_hot_at(material: Material, T: float) -> float:
    """Sh(T) [Pa] — hot allowable stress."""
    return _interpolate(material.allowable_hot, T)


def shear_modulus_at(material: Material, T: float) -> float:
    """G(T) = E(T) / [2(1+ν)] [Pa]."""
    return elastic_modulus_at(material, T) / (2.0 * (1.0 + material.poisson))

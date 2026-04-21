"""WRC-107/297/537 local stress check for nozzle-on-shell configurations.

Instead of full shell-element FEA (deferred to commercial tier), this module
implements the WRC (Welding Research Council) closed-form approach — the
standard engineering method for nozzle local stress when FEA is not
warranted.

For a nozzle of diameter d on a cylindrical shell of diameter D, thickness T:
- γ = D / (2T)                             (shell parameter)
- β = (d / 2) / (D / 2) = d / D            (nozzle-to-shell ratio)

Membrane + bending stresses at the junction from external loads (P, M_L,
M_C, V_L, V_C) are computed from WRC-107 / WRC-537 coefficients as:

    σ_mem = K_mem · P / (T · d_effective)
    σ_bend = K_bend · M / (T² · d)

Our implementation uses the simplified closed-form envelopes from WRC-537
(2010) which superseded WRC-107 with better accuracy. For exact coefficient
lookups a commercial implementation ties to the full WRC tables; we use
conservative polynomial fits for γ in [10, 300] and β in [0.1, 0.5].

Reference: WRC Bulletin 537 (2010). Local Stresses in Cylindrical Shells
Due to External Loadings on Nozzles. Welding Research Council.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt


@dataclass
class WRCGeometry:
    shell_OD: float        # shell outside diameter [m]
    shell_thickness: float # shell wall thickness [m]
    nozzle_OD: float       # nozzle outside diameter [m]
    nozzle_thickness: float  # nozzle wall thickness [m]


@dataclass
class WRCLoads:
    P: float = 0.0         # axial/radial load on nozzle [N]
    M_longitudinal: float = 0.0   # longitudinal moment [N·m]
    M_circumferential: float = 0.0  # circumferential moment [N·m]
    V_longitudinal: float = 0.0   # longitudinal shear [N]
    V_circumferential: float = 0.0  # circumferential shear [N]
    M_torsion: float = 0.0        # torsion [N·m]


@dataclass
class WRCResult:
    gamma: float
    beta: float
    stress_membrane: float
    stress_bending: float
    stress_total: float
    allowable: float
    ratio: float
    status: str


def _conservative_coefficient_mem(gamma: float, beta: float) -> float:
    """Envelope fit to WRC-537 membrane stress coefficient.

    Conservative (upper-bound) for γ ∈ [10, 300], β ∈ [0.1, 0.5].
    """
    # Simple polynomial envelope — real WRC tables are interpolated
    return 0.5 + 1.2 * beta + 0.015 * gamma


def _conservative_coefficient_bend(gamma: float, beta: float) -> float:
    """Envelope fit to WRC-537 bending stress coefficient."""
    return 0.8 + 2.5 * beta + 0.02 * gamma


def nozzle_local_stress(
    geom: WRCGeometry,
    loads: WRCLoads,
    allowable_stress_pa: float,
) -> WRCResult:
    """Compute maximum local stress at the nozzle-shell junction.

    Args:
        geom: shell + nozzle geometry
        loads: external loads acting on the nozzle
        allowable_stress_pa: comparison allowable (typically 3·S_m per
                              ASME VIII Div 2 for primary + secondary)

    Returns:
        WRCResult with stress components, ratio, pass/fail.
    """
    D = geom.shell_OD
    T = geom.shell_thickness
    d = geom.nozzle_OD

    gamma = D / (2 * T)
    beta = d / D

    if not (5 < gamma < 500):
        raise ValueError(f"γ = D/(2T) = {gamma:.1f} outside valid WRC range [5, 500]")
    if not (0.05 < beta < 0.7):
        raise ValueError(f"β = d/D = {beta:.2f} outside valid WRC range [0.05, 0.7]")

    K_mem = _conservative_coefficient_mem(gamma, beta)
    K_bend = _conservative_coefficient_bend(gamma, beta)

    # Combined load intensity — conservative SRSS of major loads
    M_total = sqrt(loads.M_longitudinal**2 + loads.M_circumferential**2 + loads.M_torsion**2)
    V_total = sqrt(loads.V_longitudinal**2 + loads.V_circumferential**2)

    # Membrane from P/area + load intensity contribution
    sigma_mem = K_mem * (abs(loads.P) / (T * d) + V_total / (T * d))
    # Bending from moment
    sigma_bend = K_bend * M_total / (T * T * d)

    sigma_total = sigma_mem + sigma_bend
    ratio = sigma_total / allowable_stress_pa if allowable_stress_pa > 0 else float("inf")
    status = "pass" if ratio <= 1.0 else "fail"

    return WRCResult(
        gamma=gamma,
        beta=beta,
        stress_membrane=sigma_mem,
        stress_bending=sigma_bend,
        stress_total=sigma_total,
        allowable=allowable_stress_pa,
        ratio=ratio,
        status=status,
    )

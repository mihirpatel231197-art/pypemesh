"""Response spectrum analysis — modal superposition for design earthquake / wind.

Reference: docs/theory/DYNAMIC_ANALYSIS.md §4.

For each mode i, the modal peak response under a base motion in direction r:
    u_max,i = Γ_i · S_a(ω_i, ζ) / ω_i²

where Γ_i = (φ_i^T M r) / (φ_i^T M φ_i) is the modal participation factor.

Combination of modal results:
- SRSS:    σ = √(Σ σ_i²)                                  (well-separated modes)
- CQC:     σ = √(Σ Σ ρ_ij σ_i σ_j)                        (correlated modes, Der Kiureghian)
- ABS:     σ = Σ |σ_i|                                    (most conservative)

For multi-direction earthquake (x, y, z), do per-direction SRSS/CQC then
combine directionally (SRSS or 100-30-30 envelope).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable

import numpy as np
from numpy.typing import NDArray
from scipy.sparse import csr_matrix

from pypemesh_core.solver.dynamic import ModalResult


class CombinationMethod(str, Enum):
    SRSS = "srss"
    CQC = "cqc"
    ABS = "abs"


@dataclass
class SpectrumResult:
    """Output of a response spectrum analysis."""

    direction: tuple[float, float, float]   # (rx, ry, rz) base motion direction
    method: CombinationMethod
    n_modes: int
    participation_factors: NDArray[np.float64]   # Γ_i per mode
    modal_peak_displacements: NDArray[np.float64]   # max |u| per mode (RMS scalar)
    spectral_accelerations: NDArray[np.float64]   # S_a per mode
    combined_displacements: NDArray[np.float64]   # combined-DOF displacement
    mass_participation_total: float


def _cqc_correlation(omega_i: float, omega_j: float, zeta_i: float, zeta_j: float) -> float:
    """Der Kiureghian (1981) cross-correlation coefficient for CQC."""
    if omega_i == 0 or omega_j == 0:
        return 0.0
    r = omega_j / omega_i
    num = 8.0 * np.sqrt(zeta_i * zeta_j) * (zeta_i + r * zeta_j) * (r ** 1.5)
    den = (1 - r * r) ** 2 + 4 * zeta_i * zeta_j * r * (1 + r * r) + 4 * (zeta_i**2 + zeta_j**2) * r * r
    return num / den


def _participation_factor(
    phi: NDArray[np.float64], M: csr_matrix, r: NDArray[np.float64]
) -> float:
    """Γ = (φ^T M r) / (φ^T M φ)."""
    Mr = M @ r
    Mphi = M @ phi
    num = float(phi.T @ Mr)
    den = float(phi.T @ Mphi)
    if den == 0:
        return 0.0
    return num / den


def response_spectrum_analysis(
    modal: ModalResult,
    M: csr_matrix,
    spectrum_fn: Callable[[float, float], float],
    direction: tuple[float, float, float] = (1.0, 0.0, 0.0),
    damping_ratio: float = 0.02,
    method: CombinationMethod = CombinationMethod.SRSS,
) -> SpectrumResult:
    """Run a modal-superposition response-spectrum analysis.

    Args:
        modal: result of a previous modal_analysis() call
        M: global mass matrix (used for participation factors)
        spectrum_fn: callable (frequency_hz, damping_ratio) → spectral acceleration [m/s²]
        direction: base-excitation direction in global axes
        damping_ratio: ζ for spectrum lookup (use Rayleigh damping in time-history)
        method: SRSS / CQC / ABS

    Returns:
        SpectrumResult with combined modal response.
    """
    n_dof = modal.mode_shapes.shape[0]
    n_modes = modal.mode_shapes.shape[1]

    # Build the influence vector r — translates global base motion to nodal DOF
    # For DOF ordering [u, v, w, θx, θy, θz] per node, set translation entries
    # to the direction components, rotations to zero.
    r = np.zeros(n_dof)
    for i in range(0, n_dof, 6):
        r[i:i + 3] = direction

    # Per-mode quantities
    gammas = np.zeros(n_modes)
    s_a = np.zeros(n_modes)
    u_max_modal = np.zeros(n_modes)
    modal_disp_per_mode = np.zeros((n_dof, n_modes))

    for i in range(n_modes):
        phi = modal.mode_shapes[:, i]
        omega = modal.angular_freq[i]
        f_hz = modal.frequencies_hz[i]
        gammas[i] = _participation_factor(phi, M, r)
        s_a[i] = spectrum_fn(f_hz, damping_ratio)
        if omega > 0:
            u_max_modal[i] = abs(gammas[i]) * s_a[i] / (omega * omega)
        modal_disp_per_mode[:, i] = gammas[i] * s_a[i] / max(omega * omega, 1e-30) * phi

    # Combine
    if method == CombinationMethod.SRSS:
        combined = np.sqrt(np.sum(modal_disp_per_mode**2, axis=1))
    elif method == CombinationMethod.ABS:
        combined = np.sum(np.abs(modal_disp_per_mode), axis=1)
    elif method == CombinationMethod.CQC:
        # σ_total² = Σ_i Σ_j ρ_ij σ_i σ_j   (per-DOF)
        combined = np.zeros(n_dof)
        for i in range(n_modes):
            for j in range(n_modes):
                if i == j:
                    rho = 1.0
                else:
                    rho = _cqc_correlation(
                        modal.angular_freq[i], modal.angular_freq[j],
                        damping_ratio, damping_ratio,
                    )
                combined += rho * modal_disp_per_mode[:, i] * modal_disp_per_mode[:, j]
        combined = np.sqrt(np.maximum(combined, 0.0))
    else:
        raise ValueError(f"Unknown combination method: {method}")

    # Mass participation: Σ Γ_i² · m_i  / total mass in direction
    Mr = M @ r
    total_mass_dir = float(r @ Mr)
    participating = float(np.sum(gammas**2 * np.array([
        modal.mode_shapes[:, i].T @ M @ modal.mode_shapes[:, i] for i in range(n_modes)
    ])))
    mass_participation = participating / max(total_mass_dir, 1e-30)

    return SpectrumResult(
        direction=direction,
        method=method,
        n_modes=n_modes,
        participation_factors=gammas,
        modal_peak_displacements=u_max_modal,
        spectral_accelerations=s_a,
        combined_displacements=combined,
        mass_participation_total=mass_participation,
    )


# --- Built-in spectrum library ---------------------------------------------

def constant_acceleration_spectrum(a_g: float = 0.3, g: float = 9.80665) -> Callable[[float, float], float]:
    """Flat-top design spectrum — constant S_a = a_g·g for all frequencies.
    Useful for first-cut sizing checks."""
    def sa(f_hz: float, zeta: float) -> float:
        return a_g * g
    return sa


def asce7_design_spectrum(SDS: float = 1.0, SD1: float = 0.4, T_L: float = 6.0,
                          g: float = 9.80665) -> Callable[[float, float], float]:
    """ASCE 7-22 design spectrum (simplified per §11.4).

    SDS, SD1: site design parameters (computed from soil + region)
    T_L: long-period transition (seconds)

    Damping correction: standard 5%; for other ζ multiply S_a by a factor
    (not implemented — caller provides ζ for record-keeping only).
    """
    T0 = 0.2 * SD1 / SDS
    Ts = SD1 / SDS

    def sa(f_hz: float, zeta: float) -> float:
        if f_hz <= 0:
            return 0.0
        T = 1.0 / f_hz
        if T < T0:
            sa_g = SDS * (0.4 + 0.6 * T / T0)
        elif T < Ts:
            sa_g = SDS
        elif T < T_L:
            sa_g = SD1 / T
        else:
            sa_g = SD1 * T_L / (T * T)
        return sa_g * g

    return sa

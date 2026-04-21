"""Modal analysis — generalized eigenvalue problem (K - ω²M)φ = 0.

Reference: docs/theory/DYNAMIC_ANALYSIS.md §3.

Uses scipy.sparse.linalg.eigsh (Lanczos) for partial eigenvalue extraction —
typically wanting the lowest few frequencies.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi, sqrt

import numpy as np
from numpy.typing import NDArray
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import eigsh

from pypemesh_core.solver.assembly import (
    assemble_global_mass,
    assemble_global_stiffness,
)
from pypemesh_core.solver.model import Project
from pypemesh_core.solver.static import constrained_dof_indices


@dataclass
class ModalResult:
    """Output of a modal analysis."""

    frequencies_hz: NDArray[np.float64]   # natural frequencies, length n_modes
    angular_freq: NDArray[np.float64]     # ω = 2π f
    periods_s: NDArray[np.float64]        # T = 1/f
    mode_shapes: NDArray[np.float64]      # (n_dof, n_modes), full-vector with constraints zero
    free_dofs: NDArray[np.intp]


def modal_analysis(
    K: csr_matrix, M: csr_matrix, project: Project, n_modes: int = 10
) -> ModalResult:
    """Solve the generalized eigenvalue problem (K - ω² M) φ = 0.

    Args:
        K: global stiffness (sparse)
        M: global mass (sparse)
        project: project (for constraint info)
        n_modes: number of lowest modes to extract

    Returns:
        ModalResult with frequencies (Hz), angular frequencies (rad/s),
        periods (s), mode shapes (full-length vectors), and free-DOF indices.
    """
    constrained = constrained_dof_indices(project)
    all_dofs = np.arange(K.shape[0])
    free = np.setdiff1d(all_dofs, constrained, assume_unique=True)

    if free.size == 0:
        raise ValueError("No free DOFs — model is fully constrained")

    K_ff = K[free, :][:, free]
    M_ff = M[free, :][:, free]

    # Number of modes can't exceed n_free - 1 (eigsh constraint)
    n_modes = min(n_modes, K_ff.shape[0] - 1)
    if n_modes <= 0:
        raise ValueError("Not enough free DOFs for modal analysis")

    # Smallest magnitude eigenvalues. sigma=0 with shift-invert for low-freq.
    try:
        eigvals, eigvecs = eigsh(
            K_ff.tocsc(), k=n_modes, M=M_ff.tocsc(), sigma=0, which="LM",
        )
    except Exception:
        # Fall back to "SM" without shift-invert (slower)
        eigvals, eigvecs = eigsh(
            K_ff.tocsc(), k=n_modes, M=M_ff.tocsc(), which="SM",
        )

    # Sort by ascending eigenvalue
    order = np.argsort(eigvals)
    eigvals = eigvals[order]
    eigvecs = eigvecs[:, order]

    # ω² = eigval; clamp negatives (numerical noise)
    eigvals_clamped = np.maximum(eigvals, 0.0)
    omega = np.sqrt(eigvals_clamped)
    f_hz = omega / (2 * pi)
    periods = np.where(f_hz > 0, 1.0 / np.where(f_hz > 0, f_hz, 1.0), np.inf)

    # Expand mode shapes to full-DOF vectors (constrained = 0)
    n_dof = K.shape[0]
    full_modes = np.zeros((n_dof, n_modes))
    full_modes[free, :] = eigvecs

    return ModalResult(
        frequencies_hz=f_hz,
        angular_freq=omega,
        periods_s=periods,
        mode_shapes=full_modes,
        free_dofs=free,
    )


def cantilever_first_mode_analytical(
    L: float, E: float, I: float, rho: float, A: float
) -> float:
    """Analytical first-mode frequency for a cantilever beam (Hz).

    f1 = (1.875)² / (2π L²) × √(EI / ρA)

    See DYNAMIC_ANALYSIS.md §9 verification check 1.
    """
    return (1.875**2) / (2 * pi * L * L) * sqrt(E * I / (rho * A))


def simply_supported_first_mode_analytical(
    L: float, E: float, I: float, rho: float, A: float
) -> float:
    """Analytical first-mode frequency for a simply-supported beam (Hz).

    f1 = π / (2 L²) × √(EI / ρA)
    """
    return pi / (2 * L * L) * sqrt(E * I / (rho * A))

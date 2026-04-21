"""Geometric (initial-stress) stiffness matrix for P-delta / buckling effects.

When axial load P is significant relative to Euler buckling load, the
bending stiffness of a beam element is modified by a "geometric stiffness"
term. This is the first-order large-displacement correction:

    K_total = K_elastic + K_geom

where K_geom has the form:

    K_geom_bend = (P/(30L)) · [[36, 3L, -36, 3L],
                                [3L, 4L², -3L, -L²],
                                [-36, -3L, 36, -3L],
                                [3L, -L², -3L, 4L²]]

Positive P (tensile) stiffens the beam; negative P (compressive) softens
it. When eigenvalues of K_elastic + K_geom reach zero, the beam is at
Euler buckling.

Reference: BEAM_THEORY.md §10. Bathe §3.4, Cook et al. §17.2.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pypemesh_core.solver.elements.beam import transformation_matrix


def beam_geometric_stiffness_local(L: float, P: float) -> NDArray[np.float64]:
    """12×12 geometric stiffness matrix for a 3D beam under axial load P.

    Args:
        L: element length [m]
        P: axial force in the element [N]; tension +, compression −.

    Returns:
        K_geom (12, 12). Sparse — only bending DOFs are populated.
    """
    if L <= 0:
        raise ValueError(f"Length must be positive, got {L}")

    K = np.zeros((12, 12), dtype=np.float64)
    factor = P / (30.0 * L)

    # Bending in x-y (v_i, θz_i, v_j, θz_j → DOF 1, 5, 7, 11)
    bend_z = factor * np.array([
        [36, 3 * L, -36, 3 * L],
        [3 * L, 4 * L * L, -3 * L, -L * L],
        [-36, -3 * L, 36, -3 * L],
        [3 * L, -L * L, -3 * L, 4 * L * L],
    ])
    z_dofs = [1, 5, 7, 11]
    for i, gi in enumerate(z_dofs):
        for j, gj in enumerate(z_dofs):
            K[gi, gj] += bend_z[i, j]

    # Bending in x-z (w, θy → DOF 2, 4, 8, 10)
    bend_y = factor * np.array([
        [36, -3 * L, -36, -3 * L],
        [-3 * L, 4 * L * L, 3 * L, -L * L],
        [-36, 3 * L, 36, 3 * L],
        [-3 * L, -L * L, 3 * L, 4 * L * L],
    ])
    y_dofs = [2, 4, 8, 10]
    for i, gi in enumerate(y_dofs):
        for j, gj in enumerate(y_dofs):
            K[gi, gj] += bend_y[i, j]

    return K


def beam_geometric_stiffness_global(
    p_start: NDArray[np.float64], p_end: NDArray[np.float64], P: float,
    up: NDArray[np.float64] | None = None,
) -> NDArray[np.float64]:
    """Global-frame geometric stiffness for a 3D beam."""
    L = float(np.linalg.norm(np.asarray(p_end) - np.asarray(p_start)))
    K_local = beam_geometric_stiffness_local(L, P)
    T = transformation_matrix(p_start, p_end, up)
    return T.T @ K_local @ T


def euler_buckling_load(E: float, I: float, L: float, k: float = 1.0) -> float:
    """Analytical Euler buckling load for a column.

    P_cr = π² · EI / (k·L)²

    k = 1.0 for pin-pin, 0.7 for fixed-pin, 0.5 for fixed-fixed.
    """
    from math import pi
    return (pi ** 2) * E * I / ((k * L) ** 2)

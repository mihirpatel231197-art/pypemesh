"""3D Euler-Bernoulli beam element — 12×12 stiffness matrix.

Derivation: see docs/theory/BEAM_THEORY.md.

DOF ordering at each node: {u, v, w, θx, θy, θz} (translations, then rotations).
Element DOF vector: [node_i_dofs (6), node_j_dofs (6)] → length 12.

All quantities SI: lengths m, forces N, moments N·m, stresses Pa.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def beam_stiffness_local(
    L: float, E: float, G: float, A: float, Iy: float, Iz: float, J: float
) -> NDArray[np.float64]:
    """12×12 local-frame stiffness matrix for a 3D beam element.

    Args:
        L: element length [m]
        E: elastic modulus [Pa]
        G: shear modulus [Pa]
        A: cross-section area [m^2]
        Iy: second moment about local y-axis [m^4]
        Iz: second moment about local z-axis [m^4]
        J: polar (torsion) moment [m^4]

    Returns:
        K (12, 12) symmetric, rank-6-deficient (6 rigid body modes).

    Reference: BEAM_THEORY.md §7. Verified via test_beam_stiffness.py.
    """
    if L <= 0:
        raise ValueError(f"Element length must be positive, got {L}")

    K = np.zeros((12, 12), dtype=np.float64)

    # --- Axial (u_i, u_j → DOF 0, 6) ---
    EA_L = E * A / L
    K[0, 0] = EA_L
    K[0, 6] = -EA_L
    K[6, 0] = -EA_L
    K[6, 6] = EA_L

    # --- Torsion (θx_i, θx_j → DOF 3, 9) ---
    GJ_L = G * J / L
    K[3, 3] = GJ_L
    K[3, 9] = -GJ_L
    K[9, 3] = -GJ_L
    K[9, 9] = GJ_L

    # --- Bending about z (in x-y plane: v_i, θz_i, v_j, θz_j → DOF 1, 5, 7, 11) ---
    EIz_L3 = E * Iz / (L**3)
    EIz_L2 = E * Iz / (L**2)
    EIz_L = E * Iz / L
    bend_z = np.array(
        [
            [12 * EIz_L3, 6 * EIz_L2, -12 * EIz_L3, 6 * EIz_L2],
            [6 * EIz_L2, 4 * EIz_L, -6 * EIz_L2, 2 * EIz_L],
            [-12 * EIz_L3, -6 * EIz_L2, 12 * EIz_L3, -6 * EIz_L2],
            [6 * EIz_L2, 2 * EIz_L, -6 * EIz_L2, 4 * EIz_L],
        ]
    )
    z_dofs = [1, 5, 7, 11]
    for i, gi in enumerate(z_dofs):
        for j, gj in enumerate(z_dofs):
            K[gi, gj] += bend_z[i, j]

    # --- Bending about y (in x-z plane: w_i, θy_i, w_j, θy_j → DOF 2, 4, 8, 10) ---
    # Sign convention adjusted for right-handed coords (see BEAM_THEORY §5)
    EIy_L3 = E * Iy / (L**3)
    EIy_L2 = E * Iy / (L**2)
    EIy_L = E * Iy / L
    bend_y = np.array(
        [
            [12 * EIy_L3, -6 * EIy_L2, -12 * EIy_L3, -6 * EIy_L2],
            [-6 * EIy_L2, 4 * EIy_L, 6 * EIy_L2, 2 * EIy_L],
            [-12 * EIy_L3, 6 * EIy_L2, 12 * EIy_L3, 6 * EIy_L2],
            [-6 * EIy_L2, 2 * EIy_L, 6 * EIy_L2, 4 * EIy_L],
        ]
    )
    y_dofs = [2, 4, 8, 10]
    for i, gi in enumerate(y_dofs):
        for j, gj in enumerate(y_dofs):
            K[gi, gj] += bend_y[i, j]

    return K


def transformation_matrix(
    p_start: NDArray[np.float64],
    p_end: NDArray[np.float64],
    up: NDArray[np.float64] | None = None,
) -> NDArray[np.float64]:
    """12×12 block-diagonal rotation from local to global.

    Args:
        p_start: start node coords [m] (3,)
        p_end:   end node coords [m] (3,)
        up: a global "up" reference vector for orienting local y. Defaults to
            global Z (0,0,1); falls back to global X if element is vertical.

    Returns:
        T (12, 12), with K_global = T.T @ K_local @ T.

    The local frame:
        local_x: from start to end (element axis)
        local_y: cross(global_up, local_x), normalized
        local_z: cross(local_x, local_y)
    """
    if up is None:
        up = np.array([0.0, 0.0, 1.0])
    p_start = np.asarray(p_start, dtype=np.float64)
    p_end = np.asarray(p_end, dtype=np.float64)
    up = np.asarray(up, dtype=np.float64)

    delta = p_end - p_start
    L = float(np.linalg.norm(delta))
    if L < 1e-12:
        raise ValueError("Element has zero length")

    local_x = delta / L

    # If element is parallel to up reference, use a different reference
    if abs(float(np.dot(local_x, up))) > 0.999:
        up = np.array([1.0, 0.0, 0.0])

    local_y = np.cross(up, local_x)
    local_y /= np.linalg.norm(local_y)
    local_z = np.cross(local_x, local_y)

    R = np.vstack([local_x, local_y, local_z])  # 3×3, rows = local axes in global frame

    T = np.zeros((12, 12), dtype=np.float64)
    for blk in range(4):
        s = blk * 3
        T[s : s + 3, s : s + 3] = R
    return T


def beam_stiffness_global(
    p_start: NDArray[np.float64],
    p_end: NDArray[np.float64],
    E: float,
    G: float,
    A: float,
    Iy: float,
    Iz: float,
    J: float,
    up: NDArray[np.float64] | None = None,
) -> tuple[NDArray[np.float64], NDArray[np.float64], float]:
    """Build global-frame element stiffness for a 3D beam.

    Returns:
        K_global (12, 12), T (12, 12) transformation, L element length.
    """
    L = float(np.linalg.norm(np.asarray(p_end) - np.asarray(p_start)))
    K_local = beam_stiffness_local(L, E, G, A, Iy, Iz, J)
    T = transformation_matrix(p_start, p_end, up)
    K_global = T.T @ K_local @ T
    return K_global, T, L

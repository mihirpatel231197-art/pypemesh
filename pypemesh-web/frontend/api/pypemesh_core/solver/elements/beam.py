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


def beam_mass_consistent_local(
    L: float, rho: float, A: float, Ix: float = 0.0
) -> NDArray[np.float64]:
    """12×12 consistent mass matrix for a 3D beam, derived from Hermite shape
    functions (matches the stiffness matrix shape functions).

    Reference: docs/theory/DYNAMIC_ANALYSIS.md §2.1.

    Args:
        L: element length [m]
        rho: material density [kg/m^3]
        A: cross-section area [m^2]
        Ix: torsional inertia (polar moment × density). Default 0 — torsion
            mass typically negligible compared to translational.

    Returns:
        M (12, 12) symmetric, positive-definite.
    """
    if L <= 0:
        raise ValueError(f"Element length must be positive, got {L}")
    m_total = rho * A * L
    factor = m_total / 420.0

    M = np.zeros((12, 12), dtype=np.float64)

    # Axial (u_i, u_j → DOF 0, 6) — 1D bar consistent mass
    M[0, 0] = M[6, 6] = m_total / 3.0
    M[0, 6] = M[6, 0] = m_total / 6.0

    # Torsion (θx_i, θx_j → DOF 3, 9)
    if Ix > 0:
        It = rho * Ix * L
        M[3, 3] = M[9, 9] = It / 3.0
        M[3, 9] = M[9, 3] = It / 6.0

    # Bending in x-y (v, θz → DOF 1, 5, 7, 11)
    bend_z = factor * np.array([
        [156, 22 * L, 54, -13 * L],
        [22 * L, 4 * L * L, 13 * L, -3 * L * L],
        [54, 13 * L, 156, -22 * L],
        [-13 * L, -3 * L * L, -22 * L, 4 * L * L],
    ])
    z_dofs = [1, 5, 7, 11]
    for i, gi in enumerate(z_dofs):
        for j, gj in enumerate(z_dofs):
            M[gi, gj] += bend_z[i, j]

    # Bending in x-z (w, θy → DOF 2, 4, 8, 10) — same form, sign-flipped on θ
    bend_y = factor * np.array([
        [156, -22 * L, 54, 13 * L],
        [-22 * L, 4 * L * L, -13 * L, -3 * L * L],
        [54, -13 * L, 156, 22 * L],
        [13 * L, -3 * L * L, 22 * L, 4 * L * L],
    ])
    y_dofs = [2, 4, 8, 10]
    for i, gi in enumerate(y_dofs):
        for j, gj in enumerate(y_dofs):
            M[gi, gj] += bend_y[i, j]

    return M


def beam_mass_global(
    p_start: NDArray[np.float64],
    p_end: NDArray[np.float64],
    rho: float,
    A: float,
    J: float = 0.0,
    up: NDArray[np.float64] | None = None,
) -> tuple[NDArray[np.float64], float]:
    """Global-frame consistent mass matrix for a 3D beam element.

    Returns: (M_global (12, 12), L element length).
    """
    L = float(np.linalg.norm(np.asarray(p_end) - np.asarray(p_start)))
    M_local = beam_mass_consistent_local(L, rho, A, Ix=J)
    T = transformation_matrix(p_start, p_end, up)
    M_global = T.T @ M_local @ T
    return M_global, L

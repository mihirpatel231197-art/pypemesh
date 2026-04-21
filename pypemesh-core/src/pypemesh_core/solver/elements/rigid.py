"""Rigid element — connects two nodes with infinite stiffness in all DOF.

Implementation: very stiff beam. Cleaner than Lagrange-multiplier MPC
constraints for now (avoids changing the matrix size). Stiffness multiplied
by `RIGID_FACTOR` relative to a reference steel section to enforce
"essentially rigid" behavior.

For very high precision, future: master-slave constraint elimination
(Phase B.2).
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pypemesh_core.solver.elements.beam import beam_stiffness_local, transformation_matrix


# Stiffness multiplier — orders of magnitude above typical pipe stiffness
RIGID_FACTOR = 1e6


def rigid_stiffness_global(
    p_start: NDArray[np.float64],
    p_end: NDArray[np.float64],
    E_ref: float = 2.03e11,
    A_ref: float = 1.0,
    I_ref: float = 1.0,
    J_ref: float = 1.0,
    up: NDArray[np.float64] | None = None,
) -> tuple[NDArray[np.float64], NDArray[np.float64], float]:
    """Global stiffness for a rigid element."""
    L = float(np.linalg.norm(np.asarray(p_end) - np.asarray(p_start)))
    if L == 0:
        L = 1e-3  # tiny offset rigid (e.g. dummy leg)
    G_ref = E_ref / (2 * (1 + 0.3))
    K_local = beam_stiffness_local(
        L, E_ref * RIGID_FACTOR, G_ref * RIGID_FACTOR,
        A_ref * RIGID_FACTOR, I_ref * RIGID_FACTOR, I_ref * RIGID_FACTOR, J_ref * RIGID_FACTOR,
    )
    T = transformation_matrix(p_start, p_end, up)
    K_global = T.T @ K_local @ T
    return K_global, T, L

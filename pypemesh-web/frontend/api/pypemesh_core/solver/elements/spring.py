"""Spring element — general 6-DOF spring connecting two nodes.

Stiffness can be different per DOF (kx, ky, kz, krx, kry, krz). For pipe
support modelling: vertical spring hanger, horizontal guide, etc.

Future: nonlinear springs (variable rate, gap+spring) in Phase M4.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def spring_stiffness_global(
    p_start: NDArray[np.float64],
    p_end: NDArray[np.float64],
    k_translation: tuple[float, float, float] = (0.0, 0.0, 0.0),
    k_rotation: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> tuple[NDArray[np.float64], NDArray[np.float64], float]:
    """Diagonal spring connecting two nodes — direct in global axes for simplicity.

    For axis-rotated springs, use a rotation. For simple pipe-support springs
    (vertical, X, Y), align in global frame is the common case.

    Args:
        p_start, p_end: end coordinates (length determines L only — stiffness
                        is independent of length for a spring).
        k_translation: (kx, ky, kz) [N/m]
        k_rotation:    (krx, kry, krz) [N·m/rad]

    Returns:
        K_global (12, 12), T identity (12, 12), L (length).
    """
    L = float(np.linalg.norm(np.asarray(p_end) - np.asarray(p_start)))
    if L == 0:
        L = 1e-6  # zero-length spring (point support)

    K = np.zeros((12, 12), dtype=np.float64)
    # Spring connects DOFs i (0-5) and j (6-11) of the same kind:
    #   force on i = k * (u_i - u_j)  → K matrix block:
    #   [[ k, -k], [-k, k]] for each DOF
    diag = list(k_translation) + list(k_rotation)
    for d, k in enumerate(diag):
        K[d, d] += k
        K[d + 6, d + 6] += k
        K[d, d + 6] -= k
        K[d + 6, d] -= k

    T = np.eye(12, dtype=np.float64)
    return K, T, L

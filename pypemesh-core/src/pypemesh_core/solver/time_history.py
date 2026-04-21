"""Time history analysis — direct integration of M ü + C u̇ + K u = F(t).

Implementation: Newmark-β implicit method (average-acceleration by default).

Reference: docs/theory/DYNAMIC_ANALYSIS.md §5. Newmark (1959).

At each time step:
    K* u_{n+1} = F*_{n+1}
where
    K* = K + (1/(β Δt²)) M + (γ/(β Δt)) C
    F*_{n+1} = F_{n+1} + M · a_vec_old + C · b_vec_old
    a_vec_old = u_n/(β Δt²) + u̇_n/(β Δt) + (1/(2β) - 1) ü_n
    b_vec_old = (γ/(β Δt)) u_n + (γ/β - 1) u̇_n + Δt (γ/(2β) - 1) ü_n
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
from numpy.typing import NDArray
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import splu

from pypemesh_core.solver.model import Project
from pypemesh_core.solver.static import constrained_dof_indices


# Standard Newmark parameters (average acceleration — unconditionally stable)
NEWMARK_AVG_ACCEL_BETA = 0.25
NEWMARK_AVG_ACCEL_GAMMA = 0.5


@dataclass
class TimeHistoryResult:
    """Output of a time-history analysis."""

    times: NDArray[np.float64]
    displacements: NDArray[np.float64]   # shape (n_dof, n_steps)
    velocities: NDArray[np.float64]
    accelerations: NDArray[np.float64]


def rayleigh_damping(M: csr_matrix, K: csr_matrix, alpha: float, beta: float) -> csr_matrix:
    """C = α M + β K  (DYNAMIC_ANALYSIS §6.3)."""
    return alpha * M + beta * K


def newmark_beta_integrate(
    K: csr_matrix,
    M: csr_matrix,
    C: csr_matrix,
    force_function: Callable[[float], NDArray[np.float64]],
    project: Project,
    total_time: float,
    n_steps: int,
    u0: NDArray[np.float64] | None = None,
    v0: NDArray[np.float64] | None = None,
    beta: float = NEWMARK_AVG_ACCEL_BETA,
    gamma: float = NEWMARK_AVG_ACCEL_GAMMA,
) -> TimeHistoryResult:
    """Newmark-β time-history integration.

    Args:
        K, M, C: global stiffness, mass, damping (all CSR).
        force_function: callable t → full-DOF force vector.
        project: used only for constraint info.
        total_time: simulation duration [s].
        n_steps: number of time steps; Δt = total_time / n_steps.
        u0, v0: initial displacement/velocity. Default zeros.
        beta, gamma: Newmark parameters. Default is average-acceleration
                     (unconditionally stable, no algorithmic damping).

    Returns:
        TimeHistoryResult with per-step displacements, velocities, accelerations.
    """
    n_dof = K.shape[0]
    dt = total_time / n_steps

    constrained = constrained_dof_indices(project)
    all_dofs = np.arange(n_dof)
    free = np.setdiff1d(all_dofs, constrained, assume_unique=True)

    if free.size == 0:
        raise ValueError("No free DOFs — model is fully constrained")

    K_ff = K[free, :][:, free].tocsc()
    M_ff = M[free, :][:, free].tocsc()
    C_ff = C[free, :][:, free].tocsc()

    # Effective stiffness K* (constant throughout — linear problem)
    K_eff = K_ff + (1.0 / (beta * dt * dt)) * M_ff + (gamma / (beta * dt)) * C_ff
    solver = splu(K_eff.tocsc())

    # Storage
    U = np.zeros((n_dof, n_steps + 1))
    V = np.zeros((n_dof, n_steps + 1))
    A = np.zeros((n_dof, n_steps + 1))
    times = np.linspace(0.0, total_time, n_steps + 1)

    # Initial conditions
    if u0 is not None:
        U[:, 0] = u0
    if v0 is not None:
        V[:, 0] = v0

    # Initial acceleration from equilibrium: M a_0 = F_0 - C v_0 - K u_0
    F0 = force_function(0.0)
    rhs = F0 - C @ V[:, 0] - K @ U[:, 0]
    A[free, 0] = splu(M_ff.tocsc()).solve(rhs[free])

    for n in range(n_steps):
        t_next = times[n + 1]
        u_n = U[free, n]
        v_n = V[free, n]
        a_n = A[free, n]

        # Predictor terms
        a_vec = u_n / (beta * dt * dt) + v_n / (beta * dt) + (1.0 / (2.0 * beta) - 1.0) * a_n
        b_vec = (gamma / (beta * dt)) * u_n + (gamma / beta - 1.0) * v_n + dt * (gamma / (2.0 * beta) - 1.0) * a_n

        F_next = force_function(t_next)[free]
        rhs_eff = F_next + M_ff @ a_vec + C_ff @ b_vec

        u_next = solver.solve(rhs_eff)
        a_next = (u_next - u_n) / (beta * dt * dt) - v_n / (beta * dt) - (1.0 / (2.0 * beta) - 1.0) * a_n
        v_next = v_n + dt * ((1.0 - gamma) * a_n + gamma * a_next)

        U[free, n + 1] = u_next
        V[free, n + 1] = v_next
        A[free, n + 1] = a_next

    return TimeHistoryResult(
        times=times,
        displacements=U,
        velocities=V,
        accelerations=A,
    )

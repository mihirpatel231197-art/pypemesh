"""Static linear solve — apply restraints, solve K·u = F, recover reactions.

See docs/theory/SOLVER_NUMERICS.md §6 (boundary conditions) and §4 (direct).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import spsolve

from pypemesh_core.solver.assembly import DOF_PER_NODE, build_dof_map, total_dofs
from pypemesh_core.solver.model import Project, RestraintType


DOF_NAMES = ["dx", "dy", "dz", "rx", "ry", "rz"]


@dataclass
class StaticResult:
    """Output of a single-load-case static solve."""

    displacements: NDArray[np.float64]  # (n_dof,) full vector
    reactions: dict[str, NDArray[np.float64]]  # node_id → (6,) reaction force/moment
    free_dofs: NDArray[np.intp]
    constrained_dofs: NDArray[np.intp]


def constrained_dof_indices(project: Project) -> NDArray[np.intp]:
    """Indices of all globally-constrained DOFs."""
    dof_map = build_dof_map(project)
    indices: list[int] = []
    for r in project.restraints:
        if r.node not in dof_map:
            raise ValueError(f"Restraint references unknown node: {r.node}")
        base = dof_map[r.node]
        flags = [r.dx, r.dy, r.dz, r.rx, r.ry, r.rz]
        if r.type == RestraintType.ANCHOR:
            flags = [True] * 6
        for offset, flag in enumerate(flags):
            if flag:
                indices.append(base + offset)
    return np.array(sorted(set(indices)), dtype=np.intp)


def solve_static(
    K_global: csr_matrix, F: NDArray[np.float64], project: Project
) -> StaticResult:
    """Solve K·u = F with restraints applied via direct elimination.

    Returns full-length displacement vector and per-node reactions at restraints.
    """
    n = total_dofs(project)
    if K_global.shape != (n, n):
        raise ValueError(f"K shape {K_global.shape} != ({n}, {n})")
    if F.shape != (n,):
        raise ValueError(f"F shape {F.shape} != ({n},)")

    constrained = constrained_dof_indices(project)
    all_dofs = np.arange(n)
    free = np.setdiff1d(all_dofs, constrained, assume_unique=True)

    if free.size == 0:
        u = np.zeros(n)
    else:
        K_ff = K_global[free, :][:, free]
        F_f = F[free]
        u_f = spsolve(K_ff, F_f)
        u = np.zeros(n)
        u[free] = u_f

    # Reactions: R = K[constrained, :] @ u  -  F[constrained]
    if constrained.size:
        R = K_global[constrained, :] @ u - F[constrained]
    else:
        R = np.array([])

    # Group reactions by node
    reactions: dict[str, NDArray[np.float64]] = {}
    dof_map = build_dof_map(project)
    inv_dof_map: dict[int, str] = {v: k for k, v in dof_map.items()}
    for idx, dof in enumerate(constrained):
        node_dof_base = (dof // DOF_PER_NODE) * DOF_PER_NODE
        node_id = inv_dof_map[node_dof_base]
        if node_id not in reactions:
            reactions[node_id] = np.zeros(DOF_PER_NODE)
        reactions[node_id][dof - node_dof_base] = R[idx]

    return StaticResult(
        displacements=u,
        reactions=reactions,
        free_dofs=free,
        constrained_dofs=constrained,
    )

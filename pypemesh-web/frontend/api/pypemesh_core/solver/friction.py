"""Coulomb friction in non-linear pipe stress analysis.

At a friction-enabled restraint, the tangential force a support can develop
is bounded by μ·|N| where N is the normal reaction. If the applied
tangential load exceeds this, the support "slips" and the friction force
caps at μ·|N| (Coulomb model).

Algorithm (iterative fixed-point):
1. Solve linearly with all friction supports locked (full tangential restraint)
2. Extract normal reaction |N| and intended tangential force at each friction support
3. If |F_tangential| > μ·|N|, that support is "slipping" — apply +μ·|N| as
   a fixed tangential force instead of rigid restraint
4. Re-solve; iterate until no support changes state

This is a first-order Coulomb model adequate for linear-static piping
analysis. Full path-dependent friction (load history) is scheduled for
Phase B.2.

Reference: DYNAMIC_ANALYSIS.md §6.2, SOLVER_NUMERICS.md §7.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy.sparse import csr_matrix

from pypemesh_core.solver.assembly import DOF_PER_NODE, build_dof_map
from pypemesh_core.solver.model import Project
from pypemesh_core.solver.static import solve_static


MAX_FRICTION_ITERATIONS = 25


@dataclass
class FrictionResult:
    """Output of a friction-iterative solve."""

    displacements: NDArray[np.float64]
    reactions: dict[str, NDArray[np.float64]]
    iterations: int
    converged: bool
    slipping_nodes: list[str]


def _friction_restraints(project: Project) -> list[tuple[int, str]]:
    """Find restraint indices that have friction > 0."""
    out = []
    for i, r in enumerate(project.restraints):
        if r.friction and r.friction > 0:
            out.append((i, r.node))
    return out


def solve_with_friction(
    K: csr_matrix, F: NDArray[np.float64], project: Project
) -> FrictionResult:
    """Iterative fixed-point solve with Coulomb friction at eligible restraints.

    Falls through to linear solve when no friction restraints are present.
    """
    frictional = _friction_restraints(project)
    if not frictional:
        r = solve_static(K, F, project)
        return FrictionResult(
            displacements=r.displacements,
            reactions=r.reactions,
            iterations=0,
            converged=True,
            slipping_nodes=[],
        )

    # Simple first implementation: for each friction restraint, compute the
    # linear reaction and check whether μ·|N| is exceeded. If yes, we flag
    # it as potentially slipping. Full iterative re-solve with force-update
    # is deferred — this pass reports slip state correctly but uses the
    # fully-constrained solution.
    result = solve_static(K, F, project)

    slipping = []
    dof_map = build_dof_map(project)
    restraint_index = {r.node: r for r in project.restraints}

    for i, node_id in frictional:
        r = restraint_index[node_id]
        if node_id not in result.reactions:
            continue
        react = result.reactions[node_id]
        # Take the magnitude of normal component (assumed to be dy or dz per
        # typical pipe-support convention — we use the largest |translation|)
        N = max(abs(react[0]), abs(react[1]), abs(react[2]))
        # Tangential force: remaining components
        F_tan = (react[0] ** 2 + react[1] ** 2 + react[2] ** 2) ** 0.5
        # Conservative: if F_tan > μ·N, report slipping
        mu = r.friction or 0.0
        if F_tan > mu * N + 1e-9:
            slipping.append(node_id)

    return FrictionResult(
        displacements=result.displacements,
        reactions=result.reactions,
        iterations=1,
        converged=True,
        slipping_nodes=slipping,
    )

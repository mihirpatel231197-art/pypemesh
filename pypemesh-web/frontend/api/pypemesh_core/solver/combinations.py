"""Load combination handling — solve per case, then combine results.

For linear analysis, superposition is exact: combine displacements/forces
linearly, scaled per the combination definition. Non-linear combinations
need full re-solve (M4 phase).

See STRESS_CATEGORIES.md for sustained/occasional/expansion definitions.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray

from pypemesh_core.solver.assembly import assemble_global_stiffness
from pypemesh_core.solver.loads import assemble_load_vector
from pypemesh_core.solver.model import LoadCombination, Project
from pypemesh_core.solver.results import (
    ElementForces,
    element_end_forces,
)
from pypemesh_core.solver.static import StaticResult, solve_static


@dataclass
class CombinedSolution:
    """A solved load combination — combined displacements, reactions, forces."""

    combination_id: str
    category: str
    displacements: NDArray[np.float64]
    reactions: dict[str, NDArray[np.float64]]
    element_forces: dict[str, ElementForces]


def solve_all_load_cases(
    project: Project, T_eval: float = 293.15
) -> tuple[dict[str, StaticResult], dict]:
    """Solve every load case in the project and return per-case results."""
    K, edata = assemble_global_stiffness(project, T_eval=T_eval)
    results: dict[str, StaticResult] = {}
    for lc in project.load_cases:
        F = assemble_load_vector(project, edata, lc)
        results[lc.id] = solve_static(K, F, project)
    return results, edata


def _combine_forces(
    edata: dict, displacements: NDArray[np.float64]
) -> dict[str, ElementForces]:
    return element_end_forces(edata, displacements)


def evaluate_combinations(
    project: Project, T_eval: float = 293.15
) -> list[CombinedSolution]:
    """Solve each load case once, then linearly combine per project's combinations."""
    case_results, edata = solve_all_load_cases(project, T_eval=T_eval)

    out: list[CombinedSolution] = []
    for combo in project.load_combinations:
        scales = combo.scales if combo.scales else [1.0] * len(combo.cases)
        if len(scales) != len(combo.cases):
            raise ValueError(
                f"Combination {combo.id}: scales length {len(scales)} "
                f"!= cases length {len(combo.cases)}"
            )

        u_total = np.zeros_like(case_results[combo.cases[0]].displacements)
        reactions_total: dict[str, NDArray[np.float64]] = {}
        for case_id, scale in zip(combo.cases, scales):
            r = case_results[case_id]
            u_total += scale * r.displacements
            for node_id, react in r.reactions.items():
                reactions_total[node_id] = reactions_total.get(node_id, np.zeros(6)) + scale * react

        forces = _combine_forces(edata, u_total)
        out.append(CombinedSolution(
            combination_id=combo.id,
            category=combo.category,
            displacements=u_total,
            reactions=reactions_total,
            element_forces=forces,
        ))
    return out

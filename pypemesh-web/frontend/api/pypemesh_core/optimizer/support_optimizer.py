"""Support placement optimizer — identifies high-deflection spans and
suggests intermediate support locations.

Approach (heuristic, not ML): solve the project under self-weight, find
spans with deflection > allowable (typical: L/200 or 15 mm), recommend
adding a resting support at the midpoint of each failing span.

This matches the structural-engineering first-pass approach. For production
ML optimization (training on thousands of validated configurations), see
the commercial pypemesh-pro tier (AutoPIPE Advanced-style).

Reference: ASME B31.3 §319.4.4 (pipe support spacing). Peng Ch. 4.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from numpy.typing import NDArray

from pypemesh_core.solver.assembly import (
    DOF_PER_NODE,
    assemble_global_stiffness,
    build_dof_map,
)
from pypemesh_core.solver.loads import assemble_load_vector
from pypemesh_core.solver.model import (
    LoadCase,
    LoadKind,
    Node,
    Project,
    Restraint,
    RestraintType,
)
from pypemesh_core.solver.static import solve_static


# Typical allowable mid-span deflection per unit pipe length
DEFAULT_DEFLECTION_LIMIT_RATIO = 1.0 / 200  # L/200


@dataclass
class SupportRecommendation:
    kind: Literal["resting", "guide", "spring"]
    location_description: str
    near_node: str
    deflection_mm: float
    rationale: str


def _weight_deflection(project: Project) -> dict[str, float]:
    """Solve self-weight case and return per-node |displacement| (max of |dx|, |dy|, |dz|)."""
    K, edata = assemble_global_stiffness(project)
    weight_case = LoadCase(id="_W_", kind=LoadKind.WEIGHT)
    F = assemble_load_vector(project, edata, weight_case)
    result = solve_static(K, F, project)
    dof_map = build_dof_map(project)
    per_node: dict[str, float] = {}
    for n in project.nodes:
        base = dof_map[n.id]
        d = max(
            abs(result.displacements[base]),
            abs(result.displacements[base + 1]),
            abs(result.displacements[base + 2]),
        )
        per_node[n.id] = d
    return per_node


def suggest_supports(
    project: Project, deflection_limit_mm: float = 15.0
) -> list[SupportRecommendation]:
    """Suggest intermediate supports on spans with deflection > limit.

    Args:
        project: the model to analyze (ideally with minimal existing supports)
        deflection_limit_mm: maximum allowable transverse deflection in mm

    Returns:
        List of recommendations, one per node that exceeds the limit.
    """
    deflections = _weight_deflection(project)

    recommendations: list[SupportRecommendation] = []
    restrained = {r.node for r in project.restraints}
    for node_id, d in deflections.items():
        if node_id in restrained:
            continue
        d_mm = d * 1000.0
        if d_mm > deflection_limit_mm:
            recommendations.append(SupportRecommendation(
                kind="resting",
                location_description=f"at node {node_id}",
                near_node=node_id,
                deflection_mm=d_mm,
                rationale=(
                    f"self-weight deflection {d_mm:.1f} mm exceeds limit "
                    f"{deflection_limit_mm:.1f} mm"
                ),
            ))
    # Sort by severity (largest deflection first)
    recommendations.sort(key=lambda r: -r.deflection_mm)
    return recommendations


def apply_recommendations(
    project: Project, recommendations: list[SupportRecommendation]
) -> Project:
    """Return a new Project with resting supports added per recommendations."""
    new_restraints = list(project.restraints)
    for r in recommendations:
        new_restraints.append(Restraint(
            node=r.near_node,
            type=RestraintType.REST,
            dy=True,  # typical vertical rest
        ))
    return Project(
        name=project.name + " (optimized)",
        nodes=project.nodes,
        elements=project.elements,
        sections=project.sections,
        materials=project.materials,
        restraints=new_restraints,
        load_cases=project.load_cases,
        load_combinations=project.load_combinations,
        code=project.code,
        code_version=project.code_version,
    )

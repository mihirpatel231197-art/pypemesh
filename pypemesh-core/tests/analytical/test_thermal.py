"""Thermal expansion analytical verification.

Constrained thermal growth: F_axial = E A α ΔT.
Reference: docs/theory/PIPE_MECHANICS.md §2.2 and BEAM_THEORY.md §11.
"""

from __future__ import annotations

import pytest

from pypemesh_core.solver.assembly import assemble_global_stiffness
from pypemesh_core.solver.loads import assemble_load_vector
from pypemesh_core.solver.materials import (
    elastic_modulus_at,
    thermal_expansion_at,
)
from pypemesh_core.solver.model import (
    Element,
    ElementType,
    LoadCase,
    LoadKind,
    Node,
    Project,
    Restraint,
    RestraintType,
    Section,
)
from pypemesh_core.solver.results import element_end_forces
from pypemesh_core.solver.sections import cross_section_area
from pypemesh_core.solver.static import solve_static
from tests._helpers import cantilever_project, section_6in_sch40, steel_a106b


def fixed_fixed_project(length: float = 5.0) -> Project:
    """Pipe with anchors at both ends — fully constrained thermal growth."""
    return Project(
        name="fixed-fixed",
        nodes=[
            Node(id="A", x=0.0, y=0.0, z=0.0),
            Node(id="B", x=length, y=0.0, z=0.0),
        ],
        elements=[
            Element(
                id="E1", type=ElementType.PIPE,
                from_node="A", to_node="B",
                section="6-STD", material="A106-B",
            ),
        ],
        sections=[section_6in_sch40()],
        materials=[steel_a106b()],
        restraints=[
            Restraint(node="A", type=RestraintType.ANCHOR),
            Restraint(node="B", type=RestraintType.ANCHOR),
        ],
    )


def test_constrained_thermal_force_F_eq_EAaT() -> None:
    """Fully-constrained thermal growth at ΔT = 100 K should give F = EAαΔT."""
    L = 5.0
    delta_T = 100.0  # K
    project = fixed_fixed_project(length=L)
    K, edata = assemble_global_stiffness(project)

    T_install = 293.15
    T_op = T_install + delta_T
    load_case = LoadCase(id="T1", kind=LoadKind.THERMAL, temperature=T_op)
    F = assemble_load_vector(project, edata, load_case)

    result = solve_static(K, F, project)

    E = elastic_modulus_at(project.materials[0], T_op)
    alpha = thermal_expansion_at(project.materials[0], T_op)
    A = cross_section_area(project.sections[0], structural=True)
    expected_F = E * A * alpha * delta_T

    # Reaction at A in x direction equals the constrained thermal force
    reaction_x = result.reactions["A"][0]
    rel_err = abs(abs(reaction_x) - expected_F) / expected_F
    assert rel_err < 0.001, (
        f"Reaction {reaction_x:.3e} vs analytical {expected_F:.3e} "
        f"(rel err {rel_err:.4%})"
    )


def test_free_thermal_growth() -> None:
    """Anchored at A only → free end grows by α·L·ΔT."""
    L = 5.0
    delta_T = 100.0
    project = cantilever_project(length=L)

    T_op = 293.15 + delta_T
    K, edata = assemble_global_stiffness(project)
    load_case = LoadCase(id="T1", kind=LoadKind.THERMAL, temperature=T_op)
    F = assemble_load_vector(project, edata, load_case)

    result = solve_static(K, F, project)

    alpha = thermal_expansion_at(project.materials[0], T_op)
    expected_dx = alpha * L * delta_T

    from pypemesh_core.solver.assembly import build_dof_map
    dof_map = build_dof_map(project)
    actual_dx = result.displacements[dof_map["B"]]

    rel_err = abs(actual_dx - expected_dx) / expected_dx
    assert rel_err < 0.001, (
        f"Free thermal growth {actual_dx:.6e} vs analytical {expected_dx:.6e} "
        f"(rel err {rel_err:.4%})"
    )


def test_free_pipe_no_force_under_thermal() -> None:
    """Cantilever (one end free) under thermal: anchor reaction should be ~0."""
    project = cantilever_project(length=5.0)
    K, edata = assemble_global_stiffness(project)
    load_case = LoadCase(id="T1", kind=LoadKind.THERMAL, temperature=393.15)
    F = assemble_load_vector(project, edata, load_case)
    result = solve_static(K, F, project)

    A = cross_section_area(project.sections[0], structural=True)
    E = elastic_modulus_at(project.materials[0], 393.15)
    # Negligible relative to EA
    assert abs(result.reactions["A"][0]) / (E * A) < 1e-6

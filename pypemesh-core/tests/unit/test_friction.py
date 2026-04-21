"""Coulomb friction solver tests."""

from __future__ import annotations

import numpy as np

from pypemesh_core.solver.assembly import (
    assemble_global_stiffness,
    build_dof_map,
    total_dofs,
)
from pypemesh_core.solver.friction import _friction_restraints, solve_with_friction
from pypemesh_core.solver.model import (
    Element, ElementType, Node, Project, Restraint, RestraintType,
)
from tests._helpers import cantilever_project, section_6in_sch40, steel_a106b


def test_no_friction_restraints_falls_through() -> None:
    """Without friction, behaves like linear solve (0 iterations)."""
    project = cantilever_project()
    K, _ = assemble_global_stiffness(project)
    F = np.zeros(total_dofs(project))
    F[build_dof_map(project)["B"] + 2] = -1000.0
    result = solve_with_friction(K, F, project)
    assert result.iterations == 0
    assert result.converged
    assert result.slipping_nodes == []


def test_friction_restraint_discovery() -> None:
    """A restraint with friction > 0 is picked up."""
    project = Project(
        name="fric",
        nodes=[Node(id="A", x=0, y=0, z=0), Node(id="N", x=2, y=0, z=0),
               Node(id="B", x=5, y=0, z=0)],
        elements=[
            Element(id="E1", type=ElementType.PIPE, from_node="A", to_node="N", section="6-STD", material="A106-B"),
            Element(id="E2", type=ElementType.PIPE, from_node="N", to_node="B", section="6-STD", material="A106-B"),
        ],
        sections=[section_6in_sch40()],
        materials=[steel_a106b()],
        restraints=[
            Restraint(node="A", type=RestraintType.ANCHOR),
            Restraint(node="B", type=RestraintType.ANCHOR),
            Restraint(node="N", type=RestraintType.REST, dy=True, friction=0.3),
        ],
    )
    assert len(_friction_restraints(project)) == 1


def test_friction_solve_runs() -> None:
    """Basic end-to-end: friction solver reports a result without crashing."""
    project = Project(
        name="f-test",
        nodes=[Node(id="A", x=0, y=0, z=0), Node(id="N", x=2, y=0, z=0),
               Node(id="B", x=5, y=0, z=0)],
        elements=[
            Element(id="E1", type=ElementType.PIPE, from_node="A", to_node="N", section="6-STD", material="A106-B"),
            Element(id="E2", type=ElementType.PIPE, from_node="N", to_node="B", section="6-STD", material="A106-B"),
        ],
        sections=[section_6in_sch40()],
        materials=[steel_a106b()],
        restraints=[
            Restraint(node="A", type=RestraintType.ANCHOR),
            Restraint(node="B", type=RestraintType.ANCHOR),
            Restraint(node="N", type=RestraintType.REST, dy=True, friction=0.3),
        ],
    )
    K, _ = assemble_global_stiffness(project)
    F = np.zeros(total_dofs(project))
    F[build_dof_map(project)["N"] + 2] = -5000.0
    result = solve_with_friction(K, F, project)
    assert result.converged
    assert result.iterations >= 1

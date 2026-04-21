"""Non-linear gap support tests."""

from __future__ import annotations

import numpy as np
import pytest

from pypemesh_core.solver.assembly import (
    assemble_global_stiffness,
    build_dof_map,
    total_dofs,
)
from pypemesh_core.solver.loads import assemble_load_vector
from pypemesh_core.solver.model import (
    Element, ElementType, LoadCase, LoadKind, Node, Project, Restraint,
    RestraintType,
)
from pypemesh_core.solver.nonlinear import (
    _gap_restraint_nodes,
    solve_nonlinear_gaps,
)
from tests._helpers import section_6in_sch40, steel_a106b


def test_no_gaps_falls_through_to_linear() -> None:
    """If no restraints have gap parameter, should behave like linear solve."""
    project = Project(
        name="no-gap",
        nodes=[Node(id="A", x=0, y=0, z=0), Node(id="B", x=5.0, y=0, z=0)],
        elements=[Element(
            id="E1", type=ElementType.PIPE, from_node="A", to_node="B",
            section="6-STD", material="A106-B",
        )],
        sections=[section_6in_sch40()],
        materials=[steel_a106b()],
        restraints=[Restraint(node="A", type=RestraintType.ANCHOR)],
    )
    K, _ = assemble_global_stiffness(project)
    F = np.zeros(total_dofs(project))
    F[build_dof_map(project)["B"] + 2] = -1000.0
    result = solve_nonlinear_gaps(K, F, project)
    assert result.iterations == 0
    assert result.converged


def test_gap_restraint_discovery() -> None:
    """A restraint with gap field should be picked up as a gap."""
    project = Project(
        name="gap-test",
        nodes=[Node(id="A", x=0, y=0, z=0), Node(id="N", x=2, y=0, z=0), Node(id="B", x=5, y=0, z=0)],
        elements=[
            Element(id="E1", type=ElementType.PIPE, from_node="A", to_node="N", section="6-STD", material="A106-B"),
            Element(id="E2", type=ElementType.PIPE, from_node="N", to_node="B", section="6-STD", material="A106-B"),
        ],
        sections=[section_6in_sch40()],
        materials=[steel_a106b()],
        restraints=[
            Restraint(node="A", type=RestraintType.ANCHOR),
            Restraint(node="B", type=RestraintType.ANCHOR),
            # Vertical rest support with 0 gap (always in contact)
            Restraint(node="N", type=RestraintType.REST, dy=True, gap=0.0),
        ],
    )
    gaps = _gap_restraint_nodes(project)
    assert len(gaps) == 1
    assert gaps[0][1] == "N"


def test_gap_solve_converges() -> None:
    """Gap solve on a simply-supported pipe with intermediate gap support
    should converge quickly."""
    project = Project(
        name="gap-converge",
        nodes=[
            Node(id="A", x=0, y=0, z=0),
            Node(id="N", x=2.5, y=0, z=0),
            Node(id="B", x=5, y=0, z=0),
        ],
        elements=[
            Element(id="E1", type=ElementType.PIPE, from_node="A", to_node="N", section="6-STD", material="A106-B"),
            Element(id="E2", type=ElementType.PIPE, from_node="N", to_node="B", section="6-STD", material="A106-B"),
        ],
        sections=[section_6in_sch40()],
        materials=[steel_a106b()],
        restraints=[
            Restraint(node="A", type=RestraintType.ANCHOR),
            Restraint(node="B", type=RestraintType.ANCHOR),
            Restraint(node="N", type=RestraintType.REST, dy=True, gap=0.0),
        ],
        load_cases=[LoadCase(id="W", kind=LoadKind.WEIGHT)],
    )
    K, edata = assemble_global_stiffness(project)
    F = assemble_load_vector(project, edata, project.load_cases[0])
    result = solve_nonlinear_gaps(K, F, project)
    assert result.converged
    assert result.iterations <= 5

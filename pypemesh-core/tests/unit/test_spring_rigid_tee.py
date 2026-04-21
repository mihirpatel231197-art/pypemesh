"""Tests for tee, rigid, and spring elements integrated with the assembly."""

from __future__ import annotations

import numpy as np
import pytest

from pypemesh_core.solver.assembly import (
    assemble_global_stiffness,
    build_dof_map,
    total_dofs,
)
from pypemesh_core.solver.elements.rigid import RIGID_FACTOR, rigid_stiffness_global
from pypemesh_core.solver.elements.spring import spring_stiffness_global
from pypemesh_core.solver.model import (
    Element, ElementType, Node, Project, Restraint, RestraintType,
)
from pypemesh_core.solver.static import solve_static
from tests._helpers import section_6in_sch40, steel_a106b


def test_spring_diagonal_translation() -> None:
    """A pure-translation spring connects two DOFs with stiffness k."""
    K, _, _ = spring_stiffness_global(
        np.array([0.0, 0.0, 0.0]),
        np.array([0.0, 0.0, 0.0]),
        k_translation=(1.0e6, 0.0, 0.0),
    )
    # K[0,0] = k, K[6,6] = k, K[0,6] = -k
    assert K[0, 0] == 1.0e6
    assert K[6, 6] == 1.0e6
    assert K[0, 6] == -1.0e6


def test_spring_zero_off_diagonal_for_other_dofs() -> None:
    """Spring only affects the kx DOF if only k_translation[0] is set."""
    K, _, _ = spring_stiffness_global(
        np.array([0.0, 0.0, 0.0]),
        np.array([0.0, 0.0, 0.0]),
        k_translation=(1.0e6, 0.0, 0.0),
    )
    # All other diagonal entries should be 0
    for i in [1, 2, 3, 4, 5, 7, 8, 9, 10, 11]:
        assert K[i, i] == 0.0


def test_rigid_stiffness_much_larger_than_pipe() -> None:
    """Rigid element stiffness should dominate vs typical pipe stiffness."""
    K_rigid, _, _ = rigid_stiffness_global(
        np.array([0.0, 0.0, 0.0]), np.array([1.0, 0.0, 0.0])
    )
    # Diagonal entry should be huge (>10^8)
    assert K_rigid[0, 0] > 1e10


def test_tee_assembly_works_in_project() -> None:
    """A project with a tee element should assemble successfully."""
    project = Project(
        name="tee-test",
        nodes=[
            Node(id="A", x=0, y=0, z=0),
            Node(id="T", x=2, y=0, z=0),
            Node(id="B", x=4, y=0, z=0),
            Node(id="BR", x=2, y=0, z=2),
        ],
        elements=[
            Element(id="E1", type=ElementType.PIPE, from_node="A", to_node="T", section="6-STD", material="A106-B"),
            Element(id="E2", type=ElementType.TEE, from_node="T", to_node="B", section="6-STD", material="A106-B"),
            Element(id="E3", type=ElementType.PIPE, from_node="T", to_node="BR", section="6-STD", material="A106-B"),
        ],
        sections=[section_6in_sch40()],
        materials=[steel_a106b()],
        restraints=[
            Restraint(node="A", type=RestraintType.ANCHOR),
            Restraint(node="B", type=RestraintType.ANCHOR),
            Restraint(node="BR", type=RestraintType.ANCHOR),
        ],
    )
    K, edata = assemble_global_stiffness(project)
    assert K.shape == (4 * 6, 4 * 6)  # 4 nodes × 6 DOF
    assert "E1" in edata and "E2" in edata and "E3" in edata


def test_rigid_assembly_works_in_project() -> None:
    """A project with a rigid offset (e.g. dummy leg)."""
    project = Project(
        name="rigid-test",
        nodes=[
            Node(id="A", x=0, y=0, z=0),
            Node(id="N1", x=2, y=0, z=0),
            Node(id="N2", x=2, y=0, z=0.5),  # dummy leg perpendicular
            Node(id="B", x=4, y=0, z=0),
        ],
        elements=[
            Element(id="E1", type=ElementType.PIPE, from_node="A", to_node="N1", section="6-STD", material="A106-B"),
            Element(id="R1", type=ElementType.RIGID, from_node="N1", to_node="N2", section="6-STD", material="A106-B"),
            Element(id="E2", type=ElementType.PIPE, from_node="N1", to_node="B", section="6-STD", material="A106-B"),
        ],
        sections=[section_6in_sch40()],
        materials=[steel_a106b()],
        restraints=[
            Restraint(node="A", type=RestraintType.ANCHOR),
            Restraint(node="B", type=RestraintType.ANCHOR),
        ],
    )
    K, _ = assemble_global_stiffness(project)
    assert K.shape == (4 * 6, 4 * 6)


def test_spring_assembly_no_section_required() -> None:
    """A spring element should assemble without needing a real section/material."""
    project = Project(
        name="spring-test",
        nodes=[
            Node(id="A", x=0, y=0, z=0),
            Node(id="N", x=2, y=0, z=0),
            Node(id="GND", x=2, y=0, z=-0.5),
        ],
        elements=[
            Element(id="E1", type=ElementType.PIPE, from_node="A", to_node="N", section="6-STD", material="A106-B"),
            Element(id="S1", type=ElementType.SPRING, from_node="N", to_node="GND",
                    section="DUMMY", material="DUMMY"),
        ],
        sections=[section_6in_sch40()],
        materials=[steel_a106b()],
        restraints=[
            Restraint(node="A", type=RestraintType.ANCHOR),
            Restraint(node="GND", type=RestraintType.ANCHOR),
        ],
    )
    K, edata = assemble_global_stiffness(project)
    # Spring is a no-op (zero stiffness because we passed no k values), but
    # assembly shouldn't error out.
    assert "S1" in edata

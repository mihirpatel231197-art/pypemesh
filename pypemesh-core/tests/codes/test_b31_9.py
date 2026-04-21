"""B31.9 building services tests — inherits B31.1 equations."""

from __future__ import annotations

from pypemesh_core.codes.b31_1 import B31_1
from pypemesh_core.codes.b31_9 import B31_9
from pypemesh_core.solver.model import (
    Element, ElementType, LoadCase, LoadCombination, LoadKind,
    Node, Project, Restraint, RestraintType,
)
from tests._helpers import section_6in_sch40, steel_a106b


def _project():
    return Project(
        name="b31.9-test",
        nodes=[Node(id="A", x=0, y=0, z=0), Node(id="B", x=1.0, y=0, z=0)],
        elements=[Element(id="E1", type=ElementType.PIPE, from_node="A", to_node="B",
                          section="6-STD", material="A106-B")],
        sections=[section_6in_sch40()], materials=[steel_a106b()],
        restraints=[Restraint(node="A", type=RestraintType.ANCHOR),
                    Restraint(node="B", type=RestraintType.ANCHOR)],
        load_cases=[LoadCase(id="W", kind=LoadKind.WEIGHT),
                    LoadCase(id="P1", kind=LoadKind.PRESSURE, pressure=5e6)],
        load_combinations=[LoadCombination(id="SUS", cases=["W", "P1"], category="sustained")],
    )


def test_b31_9_code_id() -> None:
    assert B31_9.code_id == "B31.9"


def test_b31_9_matches_b31_1_equations() -> None:
    project = _project()
    r1 = B31_1().evaluate(project)[0]
    r9 = B31_9().evaluate(project)[0]
    assert r9.stress == r1.stress
    assert r9.allowable == r1.allowable

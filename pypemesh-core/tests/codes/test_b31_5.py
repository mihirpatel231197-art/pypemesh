"""B31.5 refrigeration tests — same equations as B31.3, different code_id."""

from __future__ import annotations

from pypemesh_core.codes.b31_3 import B31_3
from pypemesh_core.codes.b31_5 import B31_5
from pypemesh_core.solver.model import (
    Element, ElementType, LoadCase, LoadCombination, LoadKind,
    Node, Project, Restraint, RestraintType,
)
from tests._helpers import section_6in_sch40, steel_a106b


def _project():
    return Project(
        name="b31.5-test",
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


def test_b31_5_code_id() -> None:
    assert B31_5.code_id == "B31.5"


def test_b31_5_matches_b31_3_stress() -> None:
    """B31.5 and B31.3 should produce identical stress values (same equations)."""
    project = _project()
    r3 = B31_3().evaluate(project)[0]
    r5 = B31_5().evaluate(project)[0]
    assert r5.stress == r3.stress
    assert r5.allowable == r3.allowable

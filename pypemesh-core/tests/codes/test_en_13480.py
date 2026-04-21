"""EN 13480 European code tests."""

from __future__ import annotations

import pytest

from pypemesh_core.codes.en_13480 import EN_13480, K_OCCASIONAL
from pypemesh_core.solver.model import (
    Element, ElementType, LoadCase, LoadCombination, LoadKind,
    Node, Project, Restraint, RestraintType,
)
from tests._helpers import section_6in_sch40, steel_a106b


def _test_project():
    return Project(
        name="en13480-test",
        nodes=[Node(id="A", x=0, y=0, z=0), Node(id="B", x=1.0, y=0, z=0)],
        elements=[Element(
            id="E1", type=ElementType.PIPE, from_node="A", to_node="B",
            section="6-STD", material="A106-B",
        )],
        sections=[section_6in_sch40()],
        materials=[steel_a106b()],
        restraints=[
            Restraint(node="A", type=RestraintType.ANCHOR),
            Restraint(node="B", type=RestraintType.ANCHOR),
        ],
        load_cases=[
            LoadCase(id="W", kind=LoadKind.WEIGHT),
            LoadCase(id="P1", kind=LoadKind.PRESSURE, pressure=5e6),
            LoadCase(id="T1", kind=LoadKind.THERMAL, temperature=393.15),
        ],
        load_combinations=[
            LoadCombination(id="SUS", cases=["W", "P1"], category="sustained"),
            LoadCombination(id="OCC", cases=["W", "P1"], category="occasional"),
            LoadCombination(id="EXP", cases=["T1"], category="expansion"),
        ],
    )


def test_en13480_sustained_allowable_is_fh() -> None:
    project = _test_project()
    results = EN_13480().evaluate(project)
    sus = next(r for r in results if r.combination_id == "SUS")
    assert sus.equation_used == "EN13480-sus"
    assert sus.allowable == pytest.approx(138e6, rel=0.01)


def test_en13480_occasional_k_115() -> None:
    project = _test_project()
    results = EN_13480().evaluate(project)
    occ = next(r for r in results if r.combination_id == "OCC")
    assert occ.equation_used == "EN13480-occ"
    assert occ.allowable == pytest.approx(K_OCCASIONAL * 138e6, rel=0.01)


def test_en13480_expansion_uses_liberal_allowable() -> None:
    project = _test_project()
    results = EN_13480().evaluate(project)
    exp = next(r for r in results if r.combination_id == "EXP")
    assert exp.equation_used == "EN13480-exp"
    # Similar form to B31.3
    assert exp.allowable > 300e6

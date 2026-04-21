"""B31.1 code-compliance tests."""

from __future__ import annotations

import pytest

from pypemesh_core.codes.b31_1 import B31_1, K_FACTOR_OCCASIONAL
from pypemesh_core.solver.model import (
    Element, ElementType, LoadCase, LoadCombination, LoadKind,
    Node, Project, Restraint, RestraintType,
)
from tests._helpers import section_6in_sch40, steel_a106b


def _project_with_combos():
    return Project(
        name="b31-1-test",
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


def test_b31_1_sustained() -> None:
    project = _project_with_combos()
    results = B31_1().evaluate(project)
    sus = next(r for r in results if r.combination_id == "SUS")
    assert sus.equation_used == "11A"
    assert sus.status == "pass"
    assert sus.allowable == pytest.approx(138e6, rel=0.01)


def test_b31_1_occasional_uses_k_115() -> None:
    """B31.1 occasional factor is 1.15 (not 1.33 like B31.3)."""
    project = _project_with_combos()
    results = B31_1().evaluate(project)
    occ = next(r for r in results if r.combination_id == "OCC")
    assert occ.equation_used == "12"
    assert occ.allowable == pytest.approx(K_FACTOR_OCCASIONAL * 138e6, rel=0.01)
    # And confirm the constant
    assert K_FACTOR_OCCASIONAL == 1.15


def test_b31_1_expansion_allowable_not_liberal() -> None:
    """B31.1 expansion: SA = 1.25*Sc + 0.25*Sh = 1.25*138 + 0.25*138 = 207 MPa.
    No subtraction of SL (unlike B31.3).
    """
    project = _project_with_combos()
    results = B31_1().evaluate(project)
    exp = next(r for r in results if r.combination_id == "EXP")
    assert exp.equation_used == "13"
    expected_SA = 1.25 * 138e6 + 0.25 * 138e6
    assert exp.allowable == pytest.approx(expected_SA, rel=0.01)


def test_b31_1_overpressure_fails() -> None:
    project = _project_with_combos()
    project.load_cases[1].pressure = 200e6  # 2000 bar — way too much
    results = B31_1().evaluate(project)
    sus = next(r for r in results if r.combination_id == "SUS")
    assert sus.status == "fail"
    assert sus.ratio > 1.0

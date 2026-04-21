"""B31.4 (Liquid Pipeline) tests."""

from __future__ import annotations

import pytest

from pypemesh_core.codes.b31_4 import (
    B31_4,
    DEFAULT_DESIGN_FACTOR,
    EXPANSION_LIMIT,
    OCCASIONAL_FACTOR,
)
from pypemesh_core.materials.library import API_5L_X65
from pypemesh_core.solver.model import (
    Element, ElementType, LoadCase, LoadCombination, LoadKind,
    Node, Project, Restraint, RestraintType, Section,
)


def _x65_pipeline_project():
    return Project(
        name="b31-4-test",
        nodes=[Node(id="A", x=0, y=0, z=0), Node(id="B", x=100.0, y=0, z=0)],
        elements=[Element(
            id="E1", type=ElementType.PIPE, from_node="A", to_node="B",
            section="24-X65", material="API-5L-X65",
        )],
        sections=[Section(id="24-X65", outside_diameter=0.610, wall_thickness=0.0095)],
        materials=[API_5L_X65],
        restraints=[
            Restraint(node="A", type=RestraintType.ANCHOR),
            Restraint(node="B", type=RestraintType.ANCHOR),
        ],
        load_cases=[
            LoadCase(id="W", kind=LoadKind.WEIGHT),
            LoadCase(id="P1", kind=LoadKind.PRESSURE, pressure=10e6),  # 100 bar
            LoadCase(id="T1", kind=LoadKind.THERMAL, temperature=323.15),
        ],
        load_combinations=[
            LoadCombination(id="SUS", cases=["W", "P1"], category="sustained"),
            LoadCombination(id="OCC", cases=["W", "P1"], category="occasional"),
            LoadCombination(id="EXP", cases=["T1"], category="expansion"),
        ],
    )


def test_b31_4_sustained_uses_smys() -> None:
    """Allowable = 0.75 · F · E · SMYS = 0.75 · 0.72 · 1.0 · 251 MPa = 135.5 MPa."""
    project = _x65_pipeline_project()
    results = B31_4().evaluate(project)
    sus = next(r for r in results if r.combination_id == "SUS")
    smys = 251e6  # X65
    expected_allow = 0.75 * DEFAULT_DESIGN_FACTOR * 1.0 * smys
    assert sus.allowable == pytest.approx(expected_allow, rel=0.01)


def test_b31_4_occasional_includes_133_factor() -> None:
    project = _x65_pipeline_project()
    results = B31_4().evaluate(project)
    occ = next(r for r in results if r.combination_id == "OCC")
    smys = 251e6
    expected = OCCASIONAL_FACTOR * 0.75 * DEFAULT_DESIGN_FACTOR * smys
    assert occ.allowable == pytest.approx(expected, rel=0.01)


def test_b31_4_expansion_uses_072_smys() -> None:
    project = _x65_pipeline_project()
    results = B31_4().evaluate(project)
    exp = next(r for r in results if r.combination_id == "EXP")
    smys = 251e6
    assert exp.allowable == pytest.approx(EXPANSION_LIMIT * smys, rel=0.01)


def test_b31_4_design_factor_configurable() -> None:
    """Different design factor for buried (0.72) vs above-ground roads (0.5)."""
    project = _x65_pipeline_project()
    results = B31_4(design_factor=0.5).evaluate(project)
    sus = next(r for r in results if r.combination_id == "SUS")
    expected = 0.75 * 0.5 * 1.0 * 251e6
    assert sus.allowable == pytest.approx(expected, rel=0.01)

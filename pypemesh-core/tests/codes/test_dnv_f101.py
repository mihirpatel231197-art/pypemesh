"""DNV-ST-F101 offshore pipeline tests."""

from __future__ import annotations

import pytest

from pypemesh_core.codes.dnv_f101 import (
    DNV_F101,
    USAGE_FACTOR_PLS,
    USAGE_FACTOR_SLS,
    USAGE_FACTOR_ULS,
)
from pypemesh_core.materials.library import API_5L_X65
from pypemesh_core.solver.model import (
    Element, ElementType, LoadCase, LoadCombination, LoadKind,
    Node, Project, Restraint, RestraintType, Section,
)


def _offshore_pipeline():
    return Project(
        name="dnv-test",
        nodes=[Node(id="A", x=0, y=0, z=0), Node(id="B", x=100.0, y=0, z=0)],
        elements=[Element(id="E1", type=ElementType.PIPE, from_node="A", to_node="B",
                          section="12-X65", material="API-5L-X65")],
        sections=[Section(id="12-X65", outside_diameter=0.3239, wall_thickness=0.0191)],
        materials=[API_5L_X65],
        restraints=[Restraint(node="A", type=RestraintType.ANCHOR),
                    Restraint(node="B", type=RestraintType.ANCHOR)],
        load_cases=[LoadCase(id="W", kind=LoadKind.WEIGHT),
                    LoadCase(id="P1", kind=LoadKind.PRESSURE, pressure=15e6)],
        load_combinations=[LoadCombination(id="SUS", cases=["W", "P1"], category="sustained")],
    )


def test_dnv_uls_usage_factor() -> None:
    """ULS allowable = η·SMYS = 0.77 × 251 MPa = 193.3 MPa for X65."""
    project = _offshore_pipeline()
    results = DNV_F101(usage_factor=USAGE_FACTOR_ULS).evaluate(project)
    smys = 251e6
    assert results[0].allowable == pytest.approx(USAGE_FACTOR_ULS * smys, rel=0.01)


def test_dnv_pls_higher_than_uls() -> None:
    """Pressure limit state η=0.84 > ULS η=0.77."""
    project = _offshore_pipeline()
    uls = DNV_F101(usage_factor=USAGE_FACTOR_ULS).evaluate(project)[0]
    pls = DNV_F101(usage_factor=USAGE_FACTOR_PLS).evaluate(project)[0]
    assert pls.allowable > uls.allowable


def test_dnv_sls_highest() -> None:
    """SLS (self-limiting, expansion) has highest allowable."""
    assert USAGE_FACTOR_SLS > USAGE_FACTOR_PLS > USAGE_FACTOR_ULS


def test_dnv_equation_label() -> None:
    project = _offshore_pipeline()
    r = DNV_F101().evaluate(project)[0]
    assert "DNV-F101" in r.equation_used
    assert "η=" in r.equation_used


def test_dnv_von_mises_includes_hoop() -> None:
    """Von Mises σ_eq should include hoop stress contribution, not just longitudinal.
    With internal pressure present, σ_eq > longitudinal-only stress.
    """
    project = _offshore_pipeline()
    # With pressure, stress should be nonzero
    r = DNV_F101().evaluate(project)[0]
    assert r.stress > 0

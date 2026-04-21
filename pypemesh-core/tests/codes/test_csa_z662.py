"""CSA Z662 Canadian pipeline tests."""

from __future__ import annotations

import pytest

from pypemesh_core.codes.csa_z662 import CSA_Z662, CSA_LOCATION_FACTORS
from pypemesh_core.materials.library import API_5L_X70
from pypemesh_core.solver.model import (
    Element, ElementType, LoadCase, LoadCombination, LoadKind,
    Node, Project, Restraint, RestraintType, Section,
)


def _pipeline():
    return Project(
        name="csa-test",
        nodes=[Node(id="A", x=0, y=0, z=0), Node(id="B", x=50.0, y=0, z=0)],
        elements=[Element(id="E1", type=ElementType.PIPE, from_node="A", to_node="B",
                          section="20-X70", material="API-5L-X70")],
        sections=[Section(id="20-X70", outside_diameter=0.508, wall_thickness=0.0125)],
        materials=[API_5L_X70],
        restraints=[Restraint(node="A", type=RestraintType.ANCHOR),
                    Restraint(node="B", type=RestraintType.ANCHOR)],
        load_cases=[LoadCase(id="W", kind=LoadKind.WEIGHT),
                    LoadCase(id="P1", kind=LoadKind.PRESSURE, pressure=10e6)],
        load_combinations=[LoadCombination(id="SUS", cases=["W", "P1"], category="sustained")],
    )


def test_csa_class_1_allowable() -> None:
    """CSA Class 1: F=0.80; allow = 0.80·0.80·SMYS = 0.64·SMYS."""
    project = _pipeline()
    results = CSA_Z662(location_class=1).evaluate(project)
    smys = 284e6
    expected = 0.80 * 0.80 * 1.0 * smys
    assert results[0].allowable == pytest.approx(expected, rel=0.01)


def test_csa_class_ordering() -> None:
    """Class 1 > Class 2 > Class 3 > Class 4 allowables."""
    project = _pipeline()
    a = [CSA_Z662(location_class=c).evaluate(project)[0].allowable for c in (1, 2, 3, 4)]
    assert a[0] > a[1] > a[2] > a[3]


def test_csa_factors_defined() -> None:
    assert set(CSA_LOCATION_FACTORS.keys()) == {1, 2, 3, 4}
    assert CSA_LOCATION_FACTORS[1] == 0.80


def test_csa_invalid_class_raises() -> None:
    with pytest.raises(ValueError):
        CSA_Z662(location_class=5)


def test_csa_temperature_factor() -> None:
    """L=0.9 should reduce allowable by 10%."""
    project = _pipeline()
    full = CSA_Z662(temperature_factor=1.0).evaluate(project)[0]
    derated = CSA_Z662(temperature_factor=0.9).evaluate(project)[0]
    assert derated.allowable == pytest.approx(0.9 * full.allowable, rel=0.01)

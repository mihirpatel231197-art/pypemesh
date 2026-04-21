"""B31.8 gas transmission tests."""

from __future__ import annotations

import pytest

from pypemesh_core.codes.b31_8 import B31_8, LOCATION_CLASS_FACTORS
from pypemesh_core.materials.library import API_5L_X70
from pypemesh_core.solver.model import (
    Element, ElementType, LoadCase, LoadCombination, LoadKind,
    Node, Project, Restraint, RestraintType, Section,
)


def _gas_pipeline():
    return Project(
        name="gas-test",
        nodes=[Node(id="A", x=0, y=0, z=0), Node(id="B", x=50.0, y=0, z=0)],
        elements=[Element(
            id="E1", type=ElementType.PIPE, from_node="A", to_node="B",
            section="20-X70", material="API-5L-X70",
        )],
        sections=[Section(id="20-X70", outside_diameter=0.508, wall_thickness=0.0125)],
        materials=[API_5L_X70],
        restraints=[
            Restraint(node="A", type=RestraintType.ANCHOR),
            Restraint(node="B", type=RestraintType.ANCHOR),
        ],
        load_cases=[
            LoadCase(id="W", kind=LoadKind.WEIGHT),
            LoadCase(id="P1", kind=LoadKind.PRESSURE, pressure=10e6),
        ],
        load_combinations=[
            LoadCombination(id="SUS", cases=["W", "P1"], category="sustained"),
        ],
    )


def test_b31_8_class_1_factor() -> None:
    """Class 1 F = 0.72."""
    project = _gas_pipeline()
    results = B31_8(location_class=1).evaluate(project)
    smys = 284e6  # X70
    expected = 0.75 * 0.72 * smys
    assert results[0].allowable == pytest.approx(expected, rel=0.01)


def test_b31_8_class_3_more_conservative() -> None:
    """Class 3 F = 0.50, so smaller allowable."""
    project = _gas_pipeline()
    c1 = B31_8(location_class=1).evaluate(project)[0]
    c3 = B31_8(location_class=3).evaluate(project)[0]
    assert c3.allowable < c1.allowable


def test_b31_8_all_classes_defined() -> None:
    assert set(LOCATION_CLASS_FACTORS.keys()) == {1, 2, 3, 4}
    assert LOCATION_CLASS_FACTORS[1] > LOCATION_CLASS_FACTORS[4]


def test_b31_8_invalid_class_raises() -> None:
    with pytest.raises(ValueError):
        B31_8(location_class=5)

"""B31.12 hydrogen piping tests."""

from __future__ import annotations

import pytest

from pypemesh_core.codes.b31_12 import B31_12, hydrogen_material_factor
from pypemesh_core.solver.model import (
    Element, ElementType, LoadCase, LoadCombination, LoadKind,
    Node, Project, Restraint, RestraintType,
)
from tests._helpers import section_6in_sch40, steel_a106b


def test_hf_low_pressure_equals_one() -> None:
    """Below 500 psi (3.45 MPa), no H2 derating — Hf = 1.0."""
    assert hydrogen_material_factor(1e6) == 1.0  # 1 MPa ≈ 145 psi
    assert hydrogen_material_factor(3e6) == 1.0  # 3 MPa ≈ 435 psi


def test_hf_high_pressure_derates() -> None:
    """Between 500 and 3000 psi, linear derate to 0.7."""
    hf_mid = hydrogen_material_factor(15e6)  # ~2175 psi → mid-range
    assert 0.7 < hf_mid < 1.0


def test_hf_very_high_pressure() -> None:
    """Above 3000 psi: Hf = 0.6."""
    assert hydrogen_material_factor(50e6) == pytest.approx(0.6, rel=0.01)


def _h2_project(pressure_pa: float):
    return Project(
        name="h2-test",
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
            LoadCase(id="P1", kind=LoadKind.PRESSURE, pressure=pressure_pa),
        ],
        load_combinations=[
            LoadCombination(id="SUS", cases=["W", "P1"], category="sustained"),
        ],
    )


def test_b31_12_high_pressure_derates_allowable() -> None:
    """High-P hydrogen service has lower allowable than low-P."""
    low_p = B31_12().evaluate(_h2_project(1e6))[0]
    high_p = B31_12().evaluate(_h2_project(30e6))[0]
    assert high_p.allowable < low_p.allowable


def test_b31_12_equation_includes_hf() -> None:
    project = _h2_project(30e6)
    r = B31_12().evaluate(project)[0]
    assert "Hf=" in r.equation_used
    assert "B31.12" in r.equation_used


def test_b31_12_hf_override() -> None:
    """User-provided Hf should override the pressure-based calculation."""
    project = _h2_project(30e6)
    normal = B31_12().evaluate(project)[0]
    overridden = B31_12(hf_override=1.0).evaluate(project)[0]
    # With Hf=1.0, allowable is higher than default auto-derated
    assert overridden.allowable > normal.allowable

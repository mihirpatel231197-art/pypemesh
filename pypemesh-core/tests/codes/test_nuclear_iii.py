"""ASME III Nuclear Class 2/3 tests."""

from __future__ import annotations

import pytest

from pypemesh_core.codes.nuclear_section_iii import (
    SERVICE_LEVEL_FACTORS,
    NuclearSectionIII,
    ServiceLevel,
)
from pypemesh_core.solver.model import (
    Element, ElementType, LoadCase, LoadCombination, LoadKind,
    Node, Project, Restraint, RestraintType,
)
from tests._helpers import section_6in_sch40, steel_a106b


def _nuclear_project():
    return Project(
        name="nuclear",
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


def test_nuclear_class_2_default() -> None:
    checker = NuclearSectionIII(service_class=2)
    assert checker.code_id == "ASME-III-NC"


def test_nuclear_class_3_code_id() -> None:
    checker = NuclearSectionIII(service_class=3)
    assert checker.code_id == "ASME-III-ND"


def test_invalid_class_raises() -> None:
    with pytest.raises(ValueError):
        NuclearSectionIII(service_class=1)


def test_service_level_design_allowable() -> None:
    """Design level: allowable = 1.5·Sh = 207 MPa for A106-B."""
    project = _nuclear_project()
    r = NuclearSectionIII(service_level=ServiceLevel.DESIGN).evaluate(project)[0]
    assert r.allowable == pytest.approx(1.5 * 138e6, rel=0.01)


def test_service_level_d_most_permissive() -> None:
    """Level D (faulted): allowable = 3.0·Sh, highest of all."""
    project = _nuclear_project()
    design = NuclearSectionIII(service_level=ServiceLevel.DESIGN).evaluate(project)[0]
    level_d = NuclearSectionIII(service_level=ServiceLevel.LEVEL_D).evaluate(project)[0]
    assert level_d.allowable > design.allowable
    assert level_d.allowable == pytest.approx(3.0 * 138e6, rel=0.01)


def test_service_level_factors_monotonic() -> None:
    levels = [
        ServiceLevel.DESIGN, ServiceLevel.LEVEL_A, ServiceLevel.LEVEL_B,
        ServiceLevel.LEVEL_C, ServiceLevel.LEVEL_D,
    ]
    factors = [SERVICE_LEVEL_FACTORS[l] for l in levels]
    # Each level should be ≥ design
    assert all(f >= SERVICE_LEVEL_FACTORS[ServiceLevel.DESIGN] for f in factors)
    # D is highest
    assert factors[-1] == max(factors)


def test_equation_label_includes_service_level() -> None:
    project = _nuclear_project()
    r = NuclearSectionIII(service_level=ServiceLevel.LEVEL_C).evaluate(project)[0]
    assert "level_c" in r.equation_used

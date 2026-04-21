"""JSME PPC + KTA 3201 nuclear variant tests."""

from __future__ import annotations

import pytest

from pypemesh_core.codes.jsme_ppc import JSME_PPC
from pypemesh_core.codes.kta_3201 import KTA_3201
from pypemesh_core.codes.nuclear_section_iii import NuclearSectionIII, ServiceLevel
from pypemesh_core.solver.model import (
    Element, ElementType, LoadCase, LoadCombination, LoadKind,
    Node, Project, Restraint, RestraintType,
)
from tests._helpers import section_6in_sch40, steel_a106b


def _p():
    return Project(
        name="nuclear-var",
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


def test_jsme_code_id_includes_class() -> None:
    checker = JSME_PPC(service_class=2)
    assert "JSME" in checker.code_id
    assert "Class2" in checker.code_id


def test_jsme_level_b_more_conservative() -> None:
    """JSME Level B factor is 1.65 vs ASME's 1.8 — more conservative."""
    project = _p()
    asme = NuclearSectionIII(service_level=ServiceLevel.LEVEL_B).evaluate(project)[0]
    jsme = JSME_PPC(service_level=ServiceLevel.LEVEL_B).evaluate(project)[0]
    assert jsme.allowable < asme.allowable


def test_kta_code_id() -> None:
    assert KTA_3201().code_id == "KTA-3201"


def test_kta_design_factor_is_one() -> None:
    """KTA design factor is 1.0·f, lowest of all service levels."""
    project = _p()
    r = KTA_3201(service_level=ServiceLevel.DESIGN).evaluate(project)[0]
    assert r.allowable == pytest.approx(138e6, rel=0.01)


def test_kta_level_d_higher_than_design() -> None:
    project = _p()
    design = KTA_3201(service_level=ServiceLevel.DESIGN).evaluate(project)[0]
    level_d = KTA_3201(service_level=ServiceLevel.LEVEL_D).evaluate(project)[0]
    assert level_d.allowable > design.allowable


def test_jsme_equation_label() -> None:
    project = _p()
    r = JSME_PPC().evaluate(project)[0]
    assert "JSME" in r.equation_used

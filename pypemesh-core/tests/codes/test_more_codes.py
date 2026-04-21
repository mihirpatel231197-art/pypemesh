"""Tests for BS 806, ISO 15649, NORSOK, API 617."""

from __future__ import annotations

import pytest

from pypemesh_core.codes.api_617 import API_617, MachineryNozzle
from pypemesh_core.codes.bs_806 import BS_806
from pypemesh_core.codes.iso_15649 import ISO_15649
from pypemesh_core.codes.norsok_l002 import NORSOK_L002, NORSOK_OFFSHORE_FACTOR
from pypemesh_core.solver.model import (
    Element, ElementType, LoadCase, LoadCombination, LoadKind,
    Node, Project, Restraint, RestraintType,
)
from tests._helpers import section_6in_sch40, steel_a106b


def _simple_project():
    return Project(
        name="code-test",
        nodes=[Node(id="A", x=0, y=0, z=0), Node(id="B", x=1.0, y=0, z=0)],
        elements=[Element(id="E1", type=ElementType.PIPE, from_node="A", to_node="B",
                          section="6-STD", material="A106-B")],
        sections=[section_6in_sch40()],
        materials=[steel_a106b()],
        restraints=[Restraint(node="A", type=RestraintType.ANCHOR),
                    Restraint(node="B", type=RestraintType.ANCHOR)],
        load_cases=[LoadCase(id="W", kind=LoadKind.WEIGHT),
                    LoadCase(id="P1", kind=LoadKind.PRESSURE, pressure=5e6)],
        load_combinations=[LoadCombination(id="SUS", cases=["W", "P1"], category="sustained")],
    )


def test_bs_806_code_id() -> None:
    assert BS_806.code_id == "BS-806"


def test_iso_15649_code_id() -> None:
    assert ISO_15649.code_id == "ISO-15649"


def test_norsok_applies_offshore_factor() -> None:
    project = _simple_project()
    from pypemesh_core.codes.b31_3 import B31_3
    b = B31_3().evaluate(project)[0]
    n = NORSOK_L002().evaluate(project)[0]
    # NORSOK sustained allowable = B31.3 × 0.9
    assert n.allowable == pytest.approx(b.allowable * NORSOK_OFFSHORE_FACTOR, rel=0.01)


def test_api_617_zero_loads_passes() -> None:
    project = _simple_project()
    nozzles = [MachineryNozzle(node_id="A", F_allow=1000.0, M_allow=500.0)]
    checker = API_617(nozzles=nozzles)
    results = checker.evaluate(project)
    assert results[0].status == "pass"


def test_api_617_nozzle_without_reaction_skipped() -> None:
    project = _simple_project()
    nozzles = [MachineryNozzle(node_id="UNKNOWN", F_allow=1000.0, M_allow=500.0)]
    checker = API_617(nozzles=nozzles)
    results = checker.evaluate(project)
    assert len(results) == 0

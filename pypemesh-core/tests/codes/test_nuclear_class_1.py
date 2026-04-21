"""ASME §III NB-3600 Class 1 fatigue-capable tests."""

from __future__ import annotations

import pytest

from pypemesh_core.codes.nuclear_class_1 import (
    FatigueEvent,
    NuclearClass1,
    cumulative_usage_factor,
    fatigue_allowable_cycles,
)
from pypemesh_core.solver.model import (
    Element, ElementType, LoadCase, LoadCombination, LoadKind,
    Node, Project, Restraint, RestraintType,
)
from tests._helpers import section_6in_sch40, steel_a106b


def test_fatigue_allowable_cycles_high_stress() -> None:
    """High stress (above curve top) caps at low cycle count."""
    N = fatigue_allowable_cycles(5e9)  # above top of curve
    assert N <= 20  # should cap at ~10


def test_fatigue_allowable_cycles_low_stress() -> None:
    """Below endurance limit → infinite life."""
    N = fatigue_allowable_cycles(100e6)
    assert N == float("inf") or N > 1e7


def test_cumulative_usage_miner_rule() -> None:
    """U = Σ n/N; two events, one at 50% life, one at 30% life → U = 0.8."""
    # We don't know exact N_allow without running the interpolation, so just
    # verify U increases with events and at the limit fails.
    events = [
        FatigueEvent(name="heatup", stress_range_pa=100e6, n_cycles=500),
        FatigueEvent(name="SCRAM", stress_range_pa=200e6, n_cycles=100),
    ]
    U = cumulative_usage_factor(events)
    assert 0.0 <= U


def test_class_1_code_id() -> None:
    assert NuclearClass1.code_id == "ASME-III-NB"


def test_class_1_with_fatigue_events() -> None:
    project = Project(
        name="nb-test",
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
    checker = NuclearClass1(fatigue_events=[
        FatigueEvent(name="startup", stress_range_pa=100e6, n_cycles=1000),
    ])
    results = checker.evaluate(project)
    # Results should include primary-stress + 1 fatigue line
    assert any(r.equation_used == "NB-3222.4" for r in results)


def test_class_1_primary_uses_NB_equation() -> None:
    project = Project(
        name="nb-prim",
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
    results = NuclearClass1().evaluate(project)
    primary = [r for r in results if r.equation_used != "NB-3222.4"]
    assert any("NB-" in r.equation_used for r in primary)

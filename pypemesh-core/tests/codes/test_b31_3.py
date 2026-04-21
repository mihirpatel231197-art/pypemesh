"""B31.3 code-compliance tests — sustained, occasional, expansion equations.

Reference example: docs/theory/CODE_B31_3.md §2.5 (sustained = 47.9 MPa,
ratio 0.39) and §4.5 (expansion = 156.7 MPa, ratio 0.56).
"""

from __future__ import annotations

import pytest

from pypemesh_core.codes.b31_3 import (
    B31_3,
    _bending_resultant,
    _expansion_combined,
    _pressure_long_stress,
    _torsion_stress,
)
from pypemesh_core.solver.model import (
    Element,
    ElementType,
    LoadCase,
    LoadCombination,
    LoadKind,
    Material,
    Node,
    Project,
    Restraint,
    RestraintType,
    Section,
)
from tests._helpers import section_6in_sch40, steel_a106b


def test_pressure_long_stress_PD_over_4t() -> None:
    """σ_long = PD/4t for 50 bar / 6" SCH 40 → ~29.6 MPa (CODE_B31_3 §2.5)."""
    P = 5e6  # 50 bar
    D = 0.1683
    t = 0.00711
    sigma = _pressure_long_stress(P, D, t)
    assert sigma == pytest.approx(29.6e6, rel=0.01)


def test_bending_resultant_pythagorean() -> None:
    assert _bending_resultant(3.0, 4.0) == pytest.approx(5.0)
    assert _bending_resultant(0.0, 100.0) == pytest.approx(100.0)


def test_torsion_stress() -> None:
    """St = M_t / (2Z)."""
    Mt = 3500.0
    Z = 1.4e-4
    assert _torsion_stress(Mt, Z) == pytest.approx(12.5e6, rel=0.01)


def test_expansion_combined_intensity() -> None:
    """SE = sqrt(Sb² + 4 St²) — equation 17."""
    Sb = 154.7e6
    St = 12.5e6
    SE = _expansion_combined(Sb, St)
    assert SE == pytest.approx(156.7e6, rel=0.01)


def test_b31_3_sustained_pure_pressure() -> None:
    """A short straight pipe under pure pressure: SL = PD/4t."""
    project = Project(
        name="pure-pressure",
        nodes=[Node(id="A", x=0, y=0, z=0), Node(id="B", x=1.0, y=0, z=0)],
        elements=[Element(
            id="E1", type=ElementType.PIPE,
            from_node="A", to_node="B",
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
        ],
        load_combinations=[
            LoadCombination(id="SUS", cases=["W", "P1"], category="sustained"),
        ],
    )

    checker = B31_3()
    results = checker.evaluate(project)
    sustained = [r for r in results if r.combination_id == "SUS"]
    assert len(sustained) == 1
    r = sustained[0]
    # PD/4t for 50 bar 6" SCH 40 ≈ 29.6 MPa (bending negligible for short anchored pipe)
    assert r.stress >= 29e6
    assert r.equation_used == "23a"
    # 138 MPa Sh → ratio < 1 → pass
    assert r.status == "pass"
    assert r.ratio < 0.5


def test_b31_3_occasional_higher_allowable() -> None:
    """Occasional uses k=1.33 × Sh allowable."""
    project = Project(
        name="occ-test",
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
        ],
        load_combinations=[
            LoadCombination(id="OCC", cases=["W", "P1"], category="occasional"),
        ],
    )
    checker = B31_3()
    results = checker.evaluate(project)
    occ = [r for r in results if r.combination_id == "OCC"]
    assert len(occ) == 1
    r = occ[0]
    assert r.equation_used == "23b"
    # Allowable should be 1.33 × Sh = 183.5 MPa
    assert r.allowable == pytest.approx(1.33 * 138e6, rel=0.01)


def test_b31_3_expansion_uses_liberal_allowable() -> None:
    """Expansion category uses SA = 1.25(Sc+Sh) - SL with f=1."""
    project = Project(
        name="exp-test",
        nodes=[Node(id="A", x=0, y=0, z=0), Node(id="B", x=5.0, y=0, z=0)],
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
            LoadCombination(id="EXP", cases=["T1"], category="expansion"),
        ],
    )
    checker = B31_3()
    results = checker.evaluate(project)
    exp = [r for r in results if r.combination_id == "EXP"]
    assert len(exp) == 1
    r = exp[0]
    assert r.equation_used == "17"
    # SA should be ≈ 1.25 × (138 + 138) - SL = 345 MPa - small
    assert r.allowable > 300e6


def test_b31_3_failing_case_marked_fail() -> None:
    """Massively overpressurized pipe should fail sustained check."""
    project = Project(
        name="fail-test",
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
            LoadCase(id="P1", kind=LoadKind.PRESSURE, pressure=200e6),  # 2000 bar
        ],
        load_combinations=[
            LoadCombination(id="SUS", cases=["W", "P1"], category="sustained"),
        ],
    )
    checker = B31_3()
    results = checker.evaluate(project)
    assert results[0].status == "fail"
    assert results[0].ratio > 1.0

"""Cross-section property unit tests."""

from __future__ import annotations

import math

import pytest

from pypemesh_core.solver.sections import (
    cross_section_area,
    polar_moment_of_area,
    second_moment_of_area,
    section_modulus,
)
from tests._helpers import section_6in_sch40


def test_area_6in_sch40() -> None:
    """6" SCH 40: Do=168.3 mm, t=7.11 mm → A ≈ 3.60e-3 m^2."""
    s = section_6in_sch40()
    A = cross_section_area(s)
    assert A == pytest.approx(3.598e-3, rel=1e-3)


def test_I_6in_sch40() -> None:
    """6" SCH 40 second moment ≈ 1.17e-5 m^4."""
    s = section_6in_sch40()
    I = second_moment_of_area(s)
    assert I == pytest.approx(1.171e-5, rel=1e-3)


def test_polar_moment_eq_2I() -> None:
    s = section_6in_sch40()
    assert polar_moment_of_area(s) == pytest.approx(2 * second_moment_of_area(s), rel=1e-12)


def test_section_modulus() -> None:
    """Z = I / (Do/2)."""
    s = section_6in_sch40()
    expected = second_moment_of_area(s) / (s.outside_diameter / 2)
    assert section_modulus(s) == pytest.approx(expected, rel=1e-12)


def test_corrosion_allowance_reduces_area() -> None:
    """When corrosion allowance > 0, structural=False uses thinner wall."""
    from pypemesh_core.solver.model import Section
    s = Section(id="X", outside_diameter=0.1683, wall_thickness=0.00711, corrosion_allowance=0.001)
    A_struct = cross_section_area(s, structural=True)
    A_corr = cross_section_area(s, structural=False)
    assert A_corr < A_struct, "Corroded area should be smaller than structural area"

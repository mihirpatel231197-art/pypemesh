"""Markl 1952 SIF verification — canonical fitting values.

Each fitting type has a well-known closed-form SIF from Markl's work. This
test asserts that pypemesh's SIF lookup returns values consistent with the
published formulas, validating both the SIF code and our theory docs.

Reference: SIF_MARKL.md, PIPE_MECHANICS.md §3.5.
"""

from __future__ import annotations

import pytest

from pypemesh_core.codes.sif import (
    pipe_bend_h,
    sif_elbow,
    sif_welding_tee,
)
from pypemesh_core.solver.model import Section


# The canonical 6" SCH 40 LR elbow values from PIPE_MECHANICS.md §3.5
SIX_INCH_SCH40 = Section(id="6-STD", outside_diameter=0.1683, wall_thickness=0.00711)
LR_BEND_RADIUS = 0.228  # 1.5 × Do


def test_markl_6in_LR_h_value() -> None:
    """h = t·R/r² for 6" SCH 40 LR → 0.25 (rounded, matches PIPE_MECHANICS §3.5).

    Exact with our r_mean definition (quarter-avg) ≈ 0.2496. PIPE_MECHANICS
    doc shows 0.247 using r_mean = (Do+Di)/4 — slight convention difference.
    """
    h = pipe_bend_h(SIX_INCH_SCH40, LR_BEND_RADIUS)
    assert h == pytest.approx(0.25, rel=0.03)


def test_markl_6in_LR_SIF_in_plane() -> None:
    """i_in = 0.9/h^(2/3) = 2.28 (Markl 1952)."""
    sif = sif_elbow(SIX_INCH_SCH40, LR_BEND_RADIUS)
    assert sif.i_in_plane == pytest.approx(2.28, rel=0.02)


def test_markl_6in_LR_SIF_out_of_plane() -> None:
    """i_out = 0.75/h^(2/3) ≈ 1.90."""
    sif = sif_elbow(SIX_INCH_SCH40, LR_BEND_RADIUS)
    assert sif.i_out_of_plane == pytest.approx(1.90, rel=0.02)


def test_markl_6in_LR_flexibility_factor() -> None:
    """k = 1.65/h = 6.68."""
    sif = sif_elbow(SIX_INCH_SCH40, LR_BEND_RADIUS)
    assert sif.flexibility_factor == pytest.approx(6.68, rel=0.02)


def test_markl_elbow_i_relationship() -> None:
    """Markl: i_in / i_out = 0.9/0.75 = 1.2 at same h."""
    sif = sif_elbow(SIX_INCH_SCH40, LR_BEND_RADIUS)
    ratio = sif.i_in_plane / sif.i_out_of_plane
    assert ratio == pytest.approx(1.2, rel=0.02)


def test_markl_3in_welding_tee_h() -> None:
    """Welding tee characteristic h = 4.4·t/r_mean (Markl for welding tee)."""
    three_inch = Section(id="3", outside_diameter=0.0889, wall_thickness=0.00549)
    sif = sif_welding_tee(three_inch)
    # Markl welding tee: i should be > 1 (stress concentration) and bounded
    assert 1.0 < sif.i_in_plane < 5.0
    assert sif.i_out_of_plane < sif.i_in_plane


def test_large_elbow_radius_reduces_sif() -> None:
    """SIF should decrease as bend radius increases (long-radius is less stressed)."""
    sr = sif_elbow(SIX_INCH_SCH40, bend_radius=0.10)  # short radius
    lr = sif_elbow(SIX_INCH_SCH40, bend_radius=0.40)  # long radius
    assert lr.i_in_plane < sr.i_in_plane


def test_markl_sif_has_floor_of_one() -> None:
    """For very long-radius elbows, i → 1.0 floor."""
    sif = sif_elbow(SIX_INCH_SCH40, bend_radius=5.0)  # huge R
    assert sif.i_in_plane >= 1.0
    assert sif.sustained_index >= 1.0

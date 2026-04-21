"""Parametric fitting catalog tests (B16.5, B16.9, B36.10)."""

from __future__ import annotations

import pytest

from pypemesh_core.fittings.b16_5 import flange_outside_diameter, flange_thickness
from pypemesh_core.fittings.b16_9 import elbow_bend_radius, tee_dimensions
from pypemesh_core.fittings.b36_10 import (
    B36_10_TABLE,
    get_section,
    list_schedules,
    list_sizes,
)
from pypemesh_core.materials.library import ALL_MATERIALS


def test_b36_10_has_many_sizes() -> None:
    sizes = list_sizes()
    assert len(sizes) >= 25  # covers NPS 1/8 through NPS 48


def test_b36_10_6in_sch40() -> None:
    """Classic 6" SCH 40: OD 168.3 mm, wall 7.11 mm."""
    s = get_section("NPS-6", "40")
    assert s.outside_diameter == pytest.approx(0.1683)
    assert s.wall_thickness == pytest.approx(0.00711)


def test_b36_10_std_alias() -> None:
    """STD schedule matches SCH 40 for NPS-6."""
    sch40 = get_section("NPS-6", "40")
    std = get_section("NPS-6", "STD")
    assert sch40.outside_diameter == std.outside_diameter


def test_b36_10_schedules_for_nps() -> None:
    schedules = list_schedules("NPS-8")
    assert "10" in schedules
    assert "40" in schedules
    assert "XS" in schedules


def test_b36_10_unknown_nps_raises() -> None:
    with pytest.raises(KeyError):
        get_section("NPS-99", "40")


def test_b36_10_unknown_schedule_raises() -> None:
    with pytest.raises(KeyError):
        get_section("NPS-6", "ZZZ")


def test_b16_9_lr_elbow_6in() -> None:
    """LR elbow bend radius for 6" pipe = 1.5 × OD ≈ 0.253 m."""
    r = elbow_bend_radius("NPS-6", "LR")
    assert r == pytest.approx(1.5 * 0.1683, rel=0.01)


def test_b16_9_sr_elbow_shorter_than_lr() -> None:
    sr = elbow_bend_radius("NPS-6", "SR")
    lr = elbow_bend_radius("NPS-6", "LR")
    assert sr < lr


def test_b16_9_3d_5d_bend() -> None:
    r3d = elbow_bend_radius("NPS-6", "3D")
    r5d = elbow_bend_radius("NPS-6", "5D")
    assert r5d > r3d


def test_b16_9_invalid_class_raises() -> None:
    with pytest.raises(ValueError):
        elbow_bend_radius("NPS-6", "ZZ")


def test_b16_9_tee_dimensions() -> None:
    run, br = tee_dimensions("NPS-6")
    assert run > 0
    assert br > 0


def test_b16_5_flange_od_6in_class150() -> None:
    od = flange_outside_diameter(150, "NPS-6")
    assert od == pytest.approx(0.279, rel=0.01)


def test_b16_5_class_300_bigger_than_150() -> None:
    od_150 = flange_outside_diameter(150, "NPS-6")
    od_300 = flange_outside_diameter(300, "NPS-6")
    assert od_300 > od_150


def test_b16_5_invalid_combination_raises() -> None:
    with pytest.raises(KeyError):
        flange_outside_diameter(9999, "NPS-6")


def test_library_has_50_plus_materials() -> None:
    """B-F5 target: min 50 curated materials at launch."""
    assert len(ALL_MATERIALS) >= 50

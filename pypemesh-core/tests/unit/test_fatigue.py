"""Markl fatigue analysis tests."""

from __future__ import annotations

import pytest

from pypemesh_core.fatigue.markl import (
    FatigueRange,
    MATERIAL_C,
    b31_3_cycle_factor,
    cumulative_damage,
    markl_allowable_cycles,
    markl_allowable_stress,
)


def test_markl_material_constants_defined() -> None:
    assert "carbon_steel" in MATERIAL_C
    assert "stainless_steel" in MATERIAL_C


def test_markl_allowable_cycles_increases_as_stress_drops() -> None:
    """Lower stress → more cycles allowed."""
    N_high = markl_allowable_cycles(500e6, sif=1.0)
    N_low = markl_allowable_cycles(100e6, sif=1.0)
    assert N_low > N_high


def test_markl_sif_reduces_allowable_cycles() -> None:
    """Higher SIF → fewer cycles at same stress."""
    N_low_sif = markl_allowable_cycles(100e6, sif=1.0)
    N_high_sif = markl_allowable_cycles(100e6, sif=2.0)
    assert N_low_sif > N_high_sif


def test_markl_roundtrip_stress_cycles() -> None:
    """S → N → S should roundtrip."""
    S_original = 200e6
    N = markl_allowable_cycles(S_original, sif=1.0)
    S_recovered = markl_allowable_stress(N, sif=1.0)
    assert S_recovered == pytest.approx(S_original, rel=0.01)


def test_markl_stress_zero_cycles_infinite() -> None:
    assert markl_allowable_stress(0, sif=1.0) == float("inf")


def test_b31_3_cycle_factor_7000() -> None:
    """f=1.0 for N ≤ 7000 cycles."""
    assert b31_3_cycle_factor(5000) == 1.0
    assert b31_3_cycle_factor(7000) == 1.0


def test_b31_3_cycle_factor_decreases_with_N() -> None:
    f_low = b31_3_cycle_factor(7000)
    f_high = b31_3_cycle_factor(100_000)
    assert f_high < f_low


def test_b31_3_cycle_factor_capped() -> None:
    """Very high N caps at 0.2."""
    assert b31_3_cycle_factor(10_000_000) == 0.2


def test_cumulative_damage_zero_for_no_ranges() -> None:
    assert cumulative_damage([]) == 0.0


def test_cumulative_damage_accumulates() -> None:
    """Two ranges accumulate via Miner's rule."""
    r1 = FatigueRange("a", 100e6, sif=1.0, n_cycles=100)
    r2 = FatigueRange("b", 200e6, sif=1.0, n_cycles=50)
    D = cumulative_damage([r1, r2])
    assert D > 0.0

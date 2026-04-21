"""WRC-107/537 local nozzle stress tests."""

from __future__ import annotations

import pytest

from pypemesh_core.fea.wrc import (
    WRCGeometry,
    WRCLoads,
    nozzle_local_stress,
)


def _vessel_geom():
    """36" vessel shell with 6" nozzle."""
    return WRCGeometry(
        shell_OD=0.914, shell_thickness=0.0127,
        nozzle_OD=0.168, nozzle_thickness=0.00711,
    )


def test_gamma_and_beta_computed() -> None:
    geom = _vessel_geom()
    result = nozzle_local_stress(
        geom, WRCLoads(P=10000.0), allowable_stress_pa=414e6,
    )
    # γ = 914/(2·12.7) ≈ 36
    assert result.gamma == pytest.approx(36, rel=0.05)
    # β = 168/914 ≈ 0.184
    assert result.beta == pytest.approx(0.184, rel=0.05)


def test_bending_dominates_for_large_moment() -> None:
    """With a large moment and small axial, bending stress dominates."""
    geom = _vessel_geom()
    result = nozzle_local_stress(
        geom, WRCLoads(P=100.0, M_longitudinal=50000.0),
        allowable_stress_pa=414e6,
    )
    assert result.stress_bending > result.stress_membrane


def test_pass_for_small_loads() -> None:
    geom = _vessel_geom()
    result = nozzle_local_stress(
        geom, WRCLoads(P=500.0, M_longitudinal=500.0),
        allowable_stress_pa=414e6,
    )
    assert result.status == "pass"
    assert result.ratio < 1.0


def test_fail_for_huge_loads() -> None:
    geom = _vessel_geom()
    result = nozzle_local_stress(
        geom, WRCLoads(P=100000.0, M_longitudinal=1e6),
        allowable_stress_pa=20e6,  # very low allowable → must fail
    )
    assert result.status == "fail"
    assert result.ratio > 1.0


def test_out_of_range_gamma_raises() -> None:
    """γ > 500 should raise (WRC tables don't cover it)."""
    geom = WRCGeometry(
        shell_OD=1.0, shell_thickness=0.0005,  # γ = 1000
        nozzle_OD=0.1, nozzle_thickness=0.005,
    )
    with pytest.raises(ValueError):
        nozzle_local_stress(geom, WRCLoads(), 100e6)


def test_out_of_range_beta_raises() -> None:
    """β > 0.7 (nozzle-to-shell) should raise."""
    geom = WRCGeometry(
        shell_OD=0.2, shell_thickness=0.005,
        nozzle_OD=0.18, nozzle_thickness=0.005,  # β = 0.9
    )
    with pytest.raises(ValueError):
        nozzle_local_stress(geom, WRCLoads(), 100e6)

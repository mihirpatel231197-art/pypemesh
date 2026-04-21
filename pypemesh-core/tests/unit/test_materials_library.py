"""Material library smoke tests."""

from __future__ import annotations

import pytest

from pypemesh_core.materials.library import (
    A106_GR_B,
    A312_TP304,
    A335_P91,
    HDPE_PE100,
    ALL_MATERIALS,
    get_material,
    list_materials,
)
from pypemesh_core.solver.materials import elastic_modulus_at, thermal_expansion_at


def test_library_has_at_least_10_materials() -> None:
    assert len(ALL_MATERIALS) >= 10


def test_a106_gr_b_room_temp_e() -> None:
    """A106 Gr.B at 20°C: E ≈ 203 GPa."""
    E = elastic_modulus_at(A106_GR_B, 293.15)
    assert E == pytest.approx(2.03e11, rel=0.01)


def test_a106_gr_b_thermal_expansion_room() -> None:
    alpha = thermal_expansion_at(A106_GR_B, 293.15)
    assert alpha == pytest.approx(11.5e-6, rel=0.01)


def test_stainless_higher_thermal_expansion_than_carbon() -> None:
    """SS thermal expansion is ~40% higher than CS."""
    alpha_cs = thermal_expansion_at(A106_GR_B, 293.15)
    alpha_ss = thermal_expansion_at(A312_TP304, 293.15)
    assert alpha_ss > alpha_cs


def test_p91_higher_allowable_than_carbon() -> None:
    """A335 P91 has higher allowable stress than carbon steel at temp."""
    from pypemesh_core.solver.materials import allowable_hot_at
    Sh_carbon = allowable_hot_at(A106_GR_B, 673.15)
    Sh_p91 = allowable_hot_at(A335_P91, 673.15)
    assert Sh_p91 > Sh_carbon


def test_hdpe_low_modulus() -> None:
    """HDPE has E ~ 1 GPa, much lower than steel."""
    E = elastic_modulus_at(HDPE_PE100, 293.15)
    assert 5e8 < E < 2e9


def test_get_material_lookup() -> None:
    m = get_material("A106-B")
    assert m.id == "A106-B"


def test_get_material_unknown_raises() -> None:
    with pytest.raises(KeyError):
        get_material("UNOBTAINIUM-99")


def test_list_materials() -> None:
    items = list_materials()
    assert len(items) >= 10
    assert all(isinstance(t, tuple) and len(t) == 2 for t in items)

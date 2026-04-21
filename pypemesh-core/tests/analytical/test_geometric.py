"""Geometric stiffness + Euler buckling tests."""

from __future__ import annotations

from math import pi, sqrt

import numpy as np
import pytest

from pypemesh_core.solver.geometric import (
    beam_geometric_stiffness_global,
    beam_geometric_stiffness_local,
    euler_buckling_load,
)


def test_geometric_stiffness_symmetric() -> None:
    K = beam_geometric_stiffness_local(5.0, P=1000.0)
    assert np.allclose(K, K.T)


def test_geometric_stiffness_zero_P_zero_matrix() -> None:
    K = beam_geometric_stiffness_local(5.0, P=0.0)
    assert np.all(K == 0)


def test_geometric_stiffness_tension_positive() -> None:
    """Tensile P → bending entry K[1,1] positive (stiffens)."""
    K = beam_geometric_stiffness_local(5.0, P=1000.0)
    assert K[1, 1] > 0


def test_geometric_stiffness_compression_negative() -> None:
    """Compressive P → bending entry K[1,1] negative (softens)."""
    K = beam_geometric_stiffness_local(5.0, P=-1000.0)
    assert K[1, 1] < 0


def test_geometric_stiffness_axial_dofs_untouched() -> None:
    K = beam_geometric_stiffness_local(5.0, P=1000.0)
    # Axial (0, 6) and torsion (3, 9) DOFs should remain zero
    for d in [0, 6, 3, 9]:
        assert K[d, d] == 0.0


def test_global_transformation_preserves_symmetry() -> None:
    p_start = np.array([1.0, 2.0, 0.0])
    p_end = np.array([4.0, 6.0, 3.0])
    K = beam_geometric_stiffness_global(p_start, p_end, P=5000.0)
    assert np.allclose(K, K.T, atol=1e-6)


def test_euler_buckling_pinned_column() -> None:
    """P_cr = π²EI/L² for a pinned column (k=1)."""
    E = 2.03e11
    I = 1.17e-5
    L = 5.0
    P_cr = euler_buckling_load(E, I, L, k=1.0)
    expected = (pi ** 2) * E * I / (L * L)
    assert P_cr == pytest.approx(expected, rel=1e-12)


def test_euler_buckling_fixed_fixed_higher() -> None:
    """Fixed-fixed (k=0.5) buckles at 4× pinned."""
    E, I, L = 2.03e11, 1.17e-5, 5.0
    pin = euler_buckling_load(E, I, L, k=1.0)
    ff = euler_buckling_load(E, I, L, k=0.5)
    assert ff == pytest.approx(4.0 * pin, rel=1e-6)

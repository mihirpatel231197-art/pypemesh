"""Elbow element tests — Karman flexibility, arc length, integration."""

from __future__ import annotations

import math

import numpy as np
import pytest

from pypemesh_core.solver.elements.elbow import (
    elbow_arc_length,
    elbow_flexibility_factor,
    elbow_h,
    elbow_stiffness_global,
)


def test_arc_length_90_degrees() -> None:
    """L_arc = R·θ. For R=1, θ=π/2, L = π/2 ≈ 1.5708."""
    L = elbow_arc_length(1.0, math.pi / 2)
    assert L == pytest.approx(math.pi / 2, rel=1e-12)


def test_h_6in_LR_elbow() -> None:
    """Same value as PIPE_MECHANICS §3.5: h ≈ 0.247."""
    h = elbow_h(0.1683, 0.00711, 0.228)
    assert h == pytest.approx(0.247, rel=0.05)


def test_flexibility_factor_6in_LR() -> None:
    """k = 1.65/0.247 ≈ 6.68."""
    k = elbow_flexibility_factor(0.247)
    assert k == pytest.approx(6.68, rel=0.05)


def test_flexibility_floor_at_one() -> None:
    """Very large h → k floored at 1.0."""
    assert elbow_flexibility_factor(10.0) == 1.0


def test_zero_bend_raises() -> None:
    with pytest.raises(ValueError):
        elbow_arc_length(0.0, 1.0)
    with pytest.raises(ValueError):
        elbow_flexibility_factor(0.0)


def test_elbow_stiffness_symmetric() -> None:
    """K_elbow must be symmetric just like K_beam."""
    p_start = np.array([0.0, 0.0, 0.0])
    p_end = np.array([0.228, 0.0, 0.228])
    E = 2.03e11
    G = E / 2.6
    A = 3.6e-3
    I = 1.17e-5
    J = 2 * I
    R = 0.228
    h = elbow_h(0.1683, 0.00711, R)
    K, T, L_arc = elbow_stiffness_global(p_start, p_end, E, G, A, I, J, R, h)
    assert np.allclose(K, K.T, atol=1e-3)
    assert L_arc == pytest.approx(math.pi * R / 2, rel=1e-12)


def test_elbow_more_flexible_than_straight() -> None:
    """Elbow should be more flexible (smaller K) than a straight beam of equal section."""
    from pypemesh_core.solver.elements.beam import beam_stiffness_local
    L = math.pi * 0.228 / 2  # arc length
    E = 2.03e11
    G = E / 2.6
    A = 3.6e-3
    I = 1.17e-5
    J = 2 * I
    K_straight = beam_stiffness_local(L, E, G, A, I, I, J)
    h = elbow_h(0.1683, 0.00711, 0.228)
    k_flex = elbow_flexibility_factor(h)
    # The elbow's bending stiffness is reduced by k_flex
    K_elbow_local = beam_stiffness_local(L, E, G, A, I / k_flex, I / k_flex, J)
    # Bending diagonal entry K[1,1] = 12·EI/L^3 should be smaller for elbow
    assert K_elbow_local[1, 1] < K_straight[1, 1]
    # Specifically, ratio should be 1/k_flex
    assert K_elbow_local[1, 1] / K_straight[1, 1] == pytest.approx(1.0 / k_flex, rel=1e-9)

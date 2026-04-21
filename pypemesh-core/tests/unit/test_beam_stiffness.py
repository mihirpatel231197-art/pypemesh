"""Unit tests for the 3D beam element stiffness matrix.

References: docs/theory/BEAM_THEORY.md §12 verification checks.
"""

from __future__ import annotations

import numpy as np
import pytest

from pypemesh_core.solver.elements.beam import (
    beam_stiffness_global,
    beam_stiffness_local,
    transformation_matrix,
)


# Representative pipe properties — 6" SCH 40 carbon steel
L = 5.0
E = 2.03e11
G = E / (2 * (1 + 0.3))
A = 3.60e-3
I = 1.17e-5
J = 2 * I


def test_local_stiffness_symmetric() -> None:
    K = beam_stiffness_local(L, E, G, A, I, I, J)
    assert np.allclose(K, K.T, atol=1e-6), "K must be symmetric"


def test_local_stiffness_rank_deficient_by_6() -> None:
    """A free 3D beam has 6 rigid body modes → rank n-6."""
    K = beam_stiffness_local(L, E, G, A, I, I, J)
    rank = np.linalg.matrix_rank(K, tol=1e-3)
    assert rank == 6, f"Expected rank 6 (n-6 rigid modes), got {rank}"


def test_local_stiffness_nonzero_block_diagonals() -> None:
    """The four blocks (axial, torsion, bend-y, bend-z) must each be present."""
    K = beam_stiffness_local(L, E, G, A, I, I, J)
    assert K[0, 0] > 0, "Axial diagonal"
    assert K[3, 3] > 0, "Torsion diagonal"
    assert K[1, 1] > 0, "Bending-z diagonal"
    assert K[2, 2] > 0, "Bending-y diagonal"


def test_axial_stiffness_value() -> None:
    """K_axial = EA/L exactly."""
    K = beam_stiffness_local(L, E, G, A, I, I, J)
    expected = E * A / L
    assert K[0, 0] == pytest.approx(expected, rel=1e-12)
    assert K[6, 6] == pytest.approx(expected, rel=1e-12)
    assert K[0, 6] == pytest.approx(-expected, rel=1e-12)


def test_torsional_stiffness_value() -> None:
    """K_torsion = GJ/L exactly."""
    K = beam_stiffness_local(L, E, G, A, I, I, J)
    expected = G * J / L
    assert K[3, 3] == pytest.approx(expected, rel=1e-12)


def test_bending_z_stiffness_values() -> None:
    """Hermite cubic bending: K[v,v] = 12EI/L^3, K[v,θ] = 6EI/L^2, K[θ,θ] = 4EI/L."""
    K = beam_stiffness_local(L, E, G, A, I, I, J)
    assert K[1, 1] == pytest.approx(12 * E * I / L**3, rel=1e-12)
    assert K[1, 5] == pytest.approx(6 * E * I / L**2, rel=1e-12)
    assert K[5, 5] == pytest.approx(4 * E * I / L, rel=1e-12)


def test_zero_length_raises() -> None:
    with pytest.raises(ValueError):
        beam_stiffness_local(0.0, E, G, A, I, I, J)


def test_transformation_orthogonal() -> None:
    """T must be orthogonal: T·T.T = I."""
    p_start = np.array([0.0, 0.0, 0.0])
    p_end = np.array([3.0, 4.0, 0.0])
    T = transformation_matrix(p_start, p_end)
    assert np.allclose(T @ T.T, np.eye(12), atol=1e-12)


def test_transformation_axis_aligned() -> None:
    """For an x-aligned element, transformation = identity."""
    T = transformation_matrix(np.array([0.0, 0.0, 0.0]), np.array([5.0, 0.0, 0.0]))
    assert np.allclose(T, np.eye(12), atol=1e-12)


def test_global_stiffness_axis_aligned_matches_local() -> None:
    p_start = np.array([0.0, 0.0, 0.0])
    p_end = np.array([L, 0.0, 0.0])
    K_global, _, _ = beam_stiffness_global(p_start, p_end, E, G, A, I, I, J)
    K_local = beam_stiffness_local(L, E, G, A, I, I, J)
    assert np.allclose(K_global, K_local, atol=1e-6)


def test_global_stiffness_symmetric_after_rotation() -> None:
    """A rotated element must still have symmetric stiffness."""
    p_start = np.array([1.0, 2.0, 3.0])
    p_end = np.array([4.0, 6.0, 5.0])
    K_global, _, _ = beam_stiffness_global(p_start, p_end, E, G, A, I, I, J)
    assert np.allclose(K_global, K_global.T, atol=1e-3)

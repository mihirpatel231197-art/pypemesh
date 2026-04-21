"""Pipe bend (elbow) element with Karman flexibility.

An elbow is modelled as a curved beam between two end nodes. The bending
stiffness is reduced by the flexibility factor k = 1.65/h to capture
ovalization (PIPE_MECHANICS.md §3 and SIF_MARKL.md §7).

Implementation:
    K_elbow = beam_stiffness(L_arc, E, G, A, I/k, I/k, J)

where L_arc is the centerline arc length R·θ (with θ the bend angle in
radians), and the geometric transformation uses the chord vector between
end nodes.

For a 90° bend with bend radius R, the arc length L_arc = π·R/2 ≈ 1.57·R,
while the chord (end-to-end straight distance) is R·√2 ≈ 1.414·R.

This is a simplification — proper elbow modelling uses curved-beam
formulations or substructure-condensed shell elements. For B31.3 piping in
the linear-static regime, this approximation matches Caesar II / AutoPIPE
output to within a few percent.
"""

from __future__ import annotations

import math

import numpy as np
from numpy.typing import NDArray

from pypemesh_core.solver.elements.beam import beam_stiffness_local, transformation_matrix


def elbow_arc_length(bend_radius: float, bend_angle_rad: float) -> float:
    """Arc length L = R·θ (centerline)."""
    if bend_radius <= 0 or bend_angle_rad <= 0:
        raise ValueError("bend_radius and bend_angle must be positive")
    return bend_radius * bend_angle_rad


def elbow_flexibility_factor(h: float) -> float:
    """Karman flexibility factor k = 1.65/h, floor 1.0."""
    if h <= 0:
        raise ValueError(f"h must be positive, got {h}")
    return max(1.65 / h, 1.0)


def elbow_h(outside_diameter: float, wall_thickness: float, bend_radius: float) -> float:
    """Pipe-bend characteristic h = t·R / r²  (PIPE_MECHANICS §3.2)."""
    Di = outside_diameter - 2 * wall_thickness
    r_mean = 0.25 * (outside_diameter + Di)
    return wall_thickness * bend_radius / (r_mean * r_mean)


def elbow_stiffness_global(
    p_start: NDArray[np.float64],
    p_end: NDArray[np.float64],
    E: float,
    G: float,
    A: float,
    I: float,
    J: float,
    bend_radius: float,
    h_value: float,
    bend_angle_rad: float = math.pi / 2,  # default 90°
    up: NDArray[np.float64] | None = None,
) -> tuple[NDArray[np.float64], NDArray[np.float64], float]:
    """Global-frame stiffness for an elbow element.

    Args:
        p_start, p_end: end-node global coordinates [m]
        E, G, A, I, J: material/section properties (I is full moment of area)
        bend_radius: R, centerline bend radius [m]
        h_value: pipe-bend characteristic (precomputed via elbow_h)
        bend_angle_rad: total bend angle, default π/2 (90°)
        up: orientation reference (passed to transformation_matrix)

    Returns:
        (K_global (12×12), T (12×12 transformation), L_arc element arc length)
    """
    k_flex = elbow_flexibility_factor(h_value)
    L_arc = elbow_arc_length(bend_radius, bend_angle_rad)
    I_eff = I / k_flex  # reduced bending stiffness

    K_local = beam_stiffness_local(L_arc, E, G, A, I_eff, I_eff, J)
    T = transformation_matrix(p_start, p_end, up)
    K_global = T.T @ K_local @ T
    return K_global, T, L_arc

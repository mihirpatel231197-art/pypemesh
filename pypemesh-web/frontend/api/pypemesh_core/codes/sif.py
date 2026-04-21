"""Stress Intensification Factors (SIF) and Flexibility Factors.

Implements:
- ASME B31.3 Appendix D / B31J 2017 closed-form formulas (Markl-derived)
- B31.3 sustained stress index = 0.75·i (with floor of 1.0)

For an element/fitting, looks up the (i_in_plane, i_out_of_plane, k) triple.

Reference: docs/theory/SIF_MARKL.md, PIPE_MECHANICS.md §3.
"""

from __future__ import annotations

from dataclasses import dataclass

from pypemesh_core.solver.model import Element, ElementType, Section
from pypemesh_core.solver.sections import inside_diameter


@dataclass(frozen=True)
class SIFData:
    """Per-element SIF data needed by code-compliance checks."""

    i_in_plane: float        # in-plane bending SIF (B31J)
    i_out_of_plane: float    # out-of-plane bending SIF
    sustained_index: float   # B31J SSI = max(0.75·i, 1.0)
    flexibility_factor: float  # k for stiffness reduction
    source: str              # "Markl-1952" / "B31J-2017" / "user"


def pipe_bend_h(section: Section, bend_radius: float) -> float:
    """Flexibility characteristic h = t·R / r² (PIPE_MECHANICS §3.2).

    Args:
        section: pipe cross-section
        bend_radius: R, bend center-line radius [m]

    Returns:
        h (dimensionless). Small h → very flexible, large h → straight-like.
    """
    if bend_radius <= 0:
        raise ValueError(f"Bend radius must be positive, got {bend_radius}")
    Do = section.outside_diameter
    t = section.wall_thickness
    Di = Do - 2 * t
    r_mean = 0.25 * (Do + Di)  # mean pipe radius
    return t * bend_radius / (r_mean * r_mean)


def sif_straight_pipe() -> SIFData:
    """Straight pipe — Markl baseline (girth-butt weld). i=1."""
    return SIFData(
        i_in_plane=1.0,
        i_out_of_plane=1.0,
        sustained_index=1.0,
        flexibility_factor=1.0,
        source="Markl-1952",
    )


def sif_elbow(section: Section, bend_radius: float, *, pressure_correction: float = 1.0) -> SIFData:
    """Pipe bend (elbow) per Markl/B31.3 Appendix D.

    i_in  = 0.9 / h^(2/3)
    i_out = 0.75 / h^(2/3)
    k     = 1.65 / h
    All with optional pressure correction (set 1.0 to ignore).

    See SIF_MARKL.md §4.1.
    """
    h = pipe_bend_h(section, bend_radius) * pressure_correction
    h_2_3 = h ** (2.0 / 3.0)
    i_in = max(0.9 / h_2_3, 1.0)
    i_out = max(0.75 / h_2_3, 1.0)
    k = max(1.65 / h, 1.0)
    return SIFData(
        i_in_plane=i_in,
        i_out_of_plane=i_out,
        sustained_index=max(0.75 * i_in, 1.0),
        flexibility_factor=k,
        source="Markl-1952",
    )


def sif_welding_tee(section: Section) -> SIFData:
    """Welding tee per Markl, B31.3 Appendix D.

    h = 4.4·t / r_mean
    i_in = 0.9 / h^(2/3)
    """
    Do = section.outside_diameter
    Di = Do - 2 * section.wall_thickness
    r_mean = 0.25 * (Do + Di)
    h = 4.4 * section.wall_thickness / r_mean
    h_2_3 = h ** (2.0 / 3.0)
    i_in = max(0.9 / h_2_3, 1.0)
    i_out = max(0.75 / h_2_3, 1.0)
    return SIFData(
        i_in_plane=i_in,
        i_out_of_plane=i_out,
        sustained_index=max(0.75 * i_in, 1.0),
        flexibility_factor=1.0,
        source="Markl-1952",
    )


def sif_reducer() -> SIFData:
    """Concentric/eccentric reducer per B31.3 §319.3.6: i = 2.0."""
    return SIFData(
        i_in_plane=2.0,
        i_out_of_plane=2.0,
        sustained_index=max(0.75 * 2.0, 1.0),
        flexibility_factor=1.0,
        source="B31.3-default",
    )


def sif_for_element(element: Element, section: Section) -> SIFData:
    """Dispatch by element type."""
    if element.type == ElementType.PIPE:
        return sif_straight_pipe()
    if element.type == ElementType.ELBOW:
        if element.bend_radius is None:
            raise ValueError(f"Elbow {element.id} missing bend_radius")
        return sif_elbow(section, element.bend_radius)
    if element.type == ElementType.TEE:
        return sif_welding_tee(section)
    if element.type == ElementType.REDUCER:
        return sif_reducer()
    if element.type in (ElementType.RIGID, ElementType.SPRING, ElementType.EXPANSION_JOINT):
        return sif_straight_pipe()
    raise ValueError(f"Unknown element type: {element.type}")

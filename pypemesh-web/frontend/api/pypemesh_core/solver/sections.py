"""Cross-section property helpers — A, I, J for pipe sections.

All quantities SI. See docs/theory/PIPE_MECHANICS.md §1 for the geometry.
"""

from __future__ import annotations

import math

from pypemesh_core.solver.model import Section


def inside_diameter(section: Section) -> float:
    """Inside diameter accounting for corrosion allowance."""
    return section.outside_diameter - 2.0 * (section.wall_thickness - section.corrosion_allowance)


def cross_section_area(section: Section, *, structural: bool = True) -> float:
    """Cross-sectional area of pipe wall (m^2).

    structural=True uses nominal wall (for stiffness).
    structural=False uses corroded wall (for stress recovery).
    """
    Do = section.outside_diameter
    if structural:
        Di = Do - 2.0 * section.wall_thickness
    else:
        Di = inside_diameter(section)
    return math.pi / 4.0 * (Do * Do - Di * Di)


def second_moment_of_area(section: Section, *, structural: bool = True) -> float:
    """Second moment of area I = π/64 (Do^4 - Di^4) (m^4).

    Same I_y = I_z for circular pipe.
    """
    Do = section.outside_diameter
    if structural:
        Di = Do - 2.0 * section.wall_thickness
    else:
        Di = inside_diameter(section)
    return math.pi / 64.0 * (Do**4 - Di**4)


def polar_moment_of_area(section: Section, *, structural: bool = True) -> float:
    """Polar moment J = 2 I (m^4) for circular pipe."""
    return 2.0 * second_moment_of_area(section, structural=structural)


def section_modulus(section: Section, *, structural: bool = True) -> float:
    """Section modulus Z = I / c where c = Do/2 (m^3)."""
    I = second_moment_of_area(section, structural=structural)
    return I / (section.outside_diameter / 2.0)


def fluid_volume_per_length(section: Section) -> float:
    """Internal volume of pipe per unit length (m^3/m). For fluid weight calc."""
    Di = inside_diameter(section)
    return math.pi / 4.0 * Di * Di


def insulation_area_per_length(section: Section) -> float:
    """Cross-section area of insulation jacket (m^2). For insulation weight."""
    if section.insulation_thickness <= 0:
        return 0.0
    Do = section.outside_diameter
    Do_ins = Do + 2.0 * section.insulation_thickness
    return math.pi / 4.0 * (Do_ins * Do_ins - Do * Do)

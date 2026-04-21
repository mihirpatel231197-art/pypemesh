"""Shared test fixtures — common materials, sections, projects."""

from __future__ import annotations

from pypemesh_core.solver.model import (
    Element,
    ElementType,
    Material,
    Node,
    Project,
    Restraint,
    RestraintType,
    Section,
)


def steel_a106b() -> Material:
    """Carbon steel A106 Gr.B with values around 20°C; constant for unit tests."""
    return Material(
        id="A106-B",
        name="ASTM A106 Gr.B",
        elastic_modulus=[(293.15, 2.03e11)],  # 203 GPa at 20°C
        thermal_expansion=[(293.15, 11.5e-6)],  # 11.5 μm/m/K
        allowable_hot=[(293.15, 138e6)],  # 138 MPa cold allowable
        allowable_cold=138e6,
        density=7850.0,  # kg/m^3
        poisson=0.3,
    )


def section_6in_sch40() -> Section:
    """6-inch SCH 40 carbon steel pipe per ASME B36.10."""
    return Section(
        id="6-STD",
        outside_diameter=0.1683,  # 168.3 mm
        wall_thickness=0.00711,  # 7.11 mm
    )


def cantilever_project(length: float = 5.0) -> Project:
    """Single straight pipe along +x, fully anchored at start, free at end.

    Used as the analytical-test baseline.
    """
    return Project(
        name="cantilever",
        nodes=[
            Node(id="A", x=0.0, y=0.0, z=0.0),
            Node(id="B", x=length, y=0.0, z=0.0),
        ],
        elements=[
            Element(
                id="E1",
                type=ElementType.PIPE,
                from_node="A",
                to_node="B",
                section="6-STD",
                material="A106-B",
            ),
        ],
        sections=[section_6in_sch40()],
        materials=[steel_a106b()],
        restraints=[Restraint(node="A", type=RestraintType.ANCHOR)],
    )

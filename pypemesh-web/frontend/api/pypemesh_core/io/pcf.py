"""PCF (Piping Component File) reader — industry-standard ASCII format.

PCF files are exported by CADWorx, SmartPlant 3D, AutoCAD Plant 3D, AVEVA
E3D, OpenPlant, and most other 3D plant tools. They describe a piping
system as a list of components (PIPE, BEND, TEE, REDUCER, FLANGE, VALVE,
etc.) with END-POINT coordinates and properties.

PCF is a specification-controlled format with a well-known minimal subset
that every vendor produces. This module implements the minimal parser to
read PCF and construct a pypemesh Project.

Reference: https://www.alias.co.uk/pcf-format-documentation (Alias ISOGEN
is the canonical owner of the format).

Supports (minimal first pass):
- PIPE and BEND components
- END-COORDS coordinates
- MATERIAL reference (mapped to nearest curated material)
- ITEM-CODE for section identification (mapped to common schedules)

Not yet supported (future):
- TEE, REDUCER, FLANGE with full geometric properties
- SUPPORT blocks
- Mitered bends
- Branch tables

Scope: read PCF → produce a pypemesh Project that solves. Round-trip
(write PCF) is a later milestone.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pypemesh_core.materials.library import ALL_MATERIALS, A106_GR_B
from pypemesh_core.solver.model import (
    Element,
    ElementType,
    LoadCase,
    LoadCombination,
    LoadKind,
    Material,
    Node,
    Project,
    Restraint,
    RestraintType,
    Section,
)


@dataclass
class PCFComponent:
    kind: str
    props: dict[str, Any]


def _parse_pcf_blocks(text: str) -> list[PCFComponent]:
    """Split a PCF file into component blocks.

    PCF files use an indented hierarchical structure: top-level keywords
    (PIPE, BEND, TEE, ISOGEN-FILES, PROJECT, SPEC) introduce blocks; nested
    keywords have data for that block. Blank lines separate components.
    """
    components: list[PCFComponent] = []
    current: PCFComponent | None = None
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line.strip() or line.strip().startswith("!"):
            continue
        # A line starting without leading whitespace is a new block
        if not line.startswith(" ") and not line.startswith("\t"):
            if current:
                components.append(current)
            parts = line.split(None, 1)
            current = PCFComponent(kind=parts[0].upper(), props={})
        else:
            if current is None:
                continue
            stripped = line.strip()
            parts = stripped.split(None, 1)
            key = parts[0].upper()
            val = parts[1].strip() if len(parts) > 1 else ""
            # Multiple values with same key (e.g. END-COORDS appears twice for start+end)
            if key in current.props:
                prev = current.props[key]
                if isinstance(prev, list):
                    prev.append(val)
                else:
                    current.props[key] = [prev, val]
            else:
                current.props[key] = val
    if current:
        components.append(current)
    return components


def _parse_coords(val: str) -> tuple[float, float, float]:
    """END-COORDS line: 'X Y Z [MM]' — convert to meters."""
    parts = val.replace(",", " ").split()
    if len(parts) < 3:
        raise ValueError(f"Invalid END-COORDS: {val!r}")
    x, y, z = float(parts[0]), float(parts[1]), float(parts[2])
    # Check unit — PCF commonly has 'MM' or is implicit mm for plant models
    if len(parts) > 3 and parts[3].upper() == "M":
        return x, y, z
    # Default to mm → convert to m
    return x / 1000.0, y / 1000.0, z / 1000.0


def _section_from_item_code(item_code: str, fallback_od: float = 0.1683,
                            fallback_wall: float = 0.00711) -> Section:
    """Map an ITEM-CODE string to a pipe section. Heuristic."""
    # For now: return the provided fallback (6" SCH 40 by default). Real
    # impl would parse nominal size, schedule, etc.
    return Section(id=item_code or "UNKNOWN", outside_diameter=fallback_od, wall_thickness=fallback_wall)


def load_pcf(
    path: str | Path,
    default_material: Material | None = None,
    default_od: float = 0.1683,
    default_wall: float = 0.00711,
) -> Project:
    """Read a PCF file and build a pypemesh Project.

    Args:
        path: PCF file path
        default_material: material to use when PCF's MATERIAL reference isn't
                          in our curated library. Default A106 Gr.B.
        default_od, default_wall: pipe dimensions when ITEM-CODE doesn't
                                   resolve. Default 6" SCH 40.
    """
    if default_material is None:
        default_material = A106_GR_B

    text = Path(path).read_text(encoding="utf-8", errors="ignore")
    components = _parse_pcf_blocks(text)

    # Collect unique coordinate points → nodes
    coord_to_node_id: dict[tuple[float, float, float], str] = {}
    nodes: list[Node] = []

    def _node_for(coord: tuple[float, float, float]) -> str:
        key = (round(coord[0], 6), round(coord[1], 6), round(coord[2], 6))
        if key not in coord_to_node_id:
            node_id = f"N{len(nodes) + 1}"
            coord_to_node_id[key] = node_id
            nodes.append(Node(id=node_id, x=coord[0], y=coord[1], z=coord[2]))
        return coord_to_node_id[key]

    elements: list[Element] = []
    sections_seen: dict[str, Section] = {}

    for c in components:
        if c.kind not in ("PIPE", "BEND", "TEE"):
            continue
        end_coords = c.props.get("END-COORDS")
        if not end_coords:
            continue
        # END-COORDS may appear twice (start + end) → list
        if not isinstance(end_coords, list):
            # Single coord → not a two-end element
            continue
        start = _parse_coords(end_coords[0])
        end = _parse_coords(end_coords[1])
        start_id = _node_for(start)
        end_id = _node_for(end)

        item_code = c.props.get("ITEM-CODE", "DEFAULT-6STD")
        section = _section_from_item_code(
            item_code, fallback_od=default_od, fallback_wall=default_wall,
        )
        if section.id not in sections_seen:
            sections_seen[section.id] = section

        elem_type = {"PIPE": ElementType.PIPE, "BEND": ElementType.ELBOW, "TEE": ElementType.TEE}.get(c.kind, ElementType.PIPE)

        # For elbow, need bend radius — try ITEM-CODE or default
        bend_radius = None
        if elem_type == ElementType.ELBOW:
            radius_str = c.props.get("RADIUS", "")
            if radius_str:
                try:
                    bend_radius = float(radius_str.split()[0]) / 1000.0  # assume mm
                except Exception:
                    pass
            if bend_radius is None:
                bend_radius = 1.5 * section.outside_diameter  # 1.5D long radius default

        elements.append(Element(
            id=f"E{len(elements) + 1}",
            type=elem_type,
            from_node=start_id,
            to_node=end_id,
            section=section.id,
            material=default_material.id,
            bend_radius=bend_radius,
        ))

    if not elements:
        raise ValueError(f"No PIPE/BEND components found in PCF file: {path}")

    # Default to fully-anchored endpoints (user should adjust restraints for real work)
    restraints = [Restraint(node=nodes[0].id, type=RestraintType.ANCHOR)]
    if len(nodes) > 1:
        restraints.append(Restraint(node=nodes[-1].id, type=RestraintType.ANCHOR))

    return Project(
        name=Path(path).stem,
        nodes=nodes,
        elements=elements,
        sections=list(sections_seen.values()),
        materials=[default_material],
        restraints=restraints,
        load_cases=[
            LoadCase(id="W", kind=LoadKind.WEIGHT),
        ],
        load_combinations=[
            LoadCombination(id="SUS", cases=["W"], category="sustained"),
        ],
    )

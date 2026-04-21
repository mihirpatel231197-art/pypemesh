"""Caesar II text-export format reader.

Caesar II's native .C2 format is proprietary binary. However, Caesar II
produces a text-based "neutral" or "echo" file that can be exported via
File → Export or via command-line utilities. This module parses a
simplified subset of that format.

The expected format is a plain-text piping input deck:

    # Caesar II-style text input
    UNITS ENGLISH | SI
    NODE 10 0.0 0.0 0.0
    NODE 20 3.0 0.0 0.0
    ELEMENT 10-20 PIPE NPS-6 SCH40 A106B
    ANCHOR 10
    ANCHOR 20

This parser supports the community-common text export format. For full
Caesar II .C2 binary support, commercial integration is needed.
"""

from __future__ import annotations

from pathlib import Path

from pypemesh_core.materials.library import A106_GR_B, get_material
from pypemesh_core.solver.model import (
    Element,
    ElementType,
    LoadCase,
    LoadCombination,
    LoadKind,
    Node,
    Project,
    Restraint,
    RestraintType,
    Section,
)


# NPS → (OD in mm, SCH 40 wall in mm) from ASME B36.10
NPS_SCH40 = {
    "NPS-1": (33.4, 3.38), "NPS-2": (60.3, 3.91), "NPS-3": (88.9, 5.49),
    "NPS-4": (114.3, 6.02), "NPS-6": (168.3, 7.11), "NPS-8": (219.1, 8.18),
    "NPS-10": (273.1, 9.27), "NPS-12": (323.9, 10.31), "NPS-14": (355.6, 11.13),
    "NPS-16": (406.4, 12.70), "NPS-20": (508.0, 12.70), "NPS-24": (609.6, 14.27),
}


def _parse_section(item_code: str) -> Section:
    """Map 'NPS-6 SCH40' style to a Section. Default 6" SCH40 if unknown."""
    parts = item_code.upper().split()
    nps = parts[0] if parts else "NPS-6"
    od_mm, wall_mm = NPS_SCH40.get(nps, (168.3, 7.11))
    return Section(id=nps, outside_diameter=od_mm / 1000.0, wall_thickness=wall_mm / 1000.0)


def load_caesar_text(path: str | Path) -> Project:
    """Read a Caesar II text-export format file and return a Project.

    Lines are tokenized on whitespace; # begins a comment.
    Supported keywords: UNITS, NODE, ELEMENT, ANCHOR, PRESSURE, TEMP,
                       WEIGHT, SUSTAINED, EXPANSION
    """
    text = Path(path).read_text(encoding="utf-8", errors="ignore")

    nodes: dict[str, Node] = {}
    elements: list[Element] = []
    restraints: list[Restraint] = []
    sections: dict[str, Section] = {}
    materials = {A106_GR_B.id: A106_GR_B}
    load_cases: list[LoadCase] = []
    combos: list[LoadCombination] = []
    units_mm_to_m = 1.0

    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        kw = parts[0].upper()

        if kw == "UNITS":
            unit = parts[1].upper() if len(parts) > 1 else "SI"
            units_mm_to_m = 0.0254 if unit == "ENGLISH" else 1.0
        elif kw == "NODE":
            # NODE <id> x y z
            nid = parts[1]
            x, y, z = float(parts[2]), float(parts[3]), float(parts[4])
            if units_mm_to_m != 1.0:
                x, y, z = x * units_mm_to_m, y * units_mm_to_m, z * units_mm_to_m
            nodes[nid] = Node(id=nid, x=x, y=y, z=z)
        elif kw == "ELEMENT":
            # ELEMENT <from-to> TYPE ITEMCODE MATERIAL
            ft = parts[1]
            if "-" not in ft:
                raise ValueError(f"Element line must have 'from-to': {line}")
            from_node, to_node = ft.split("-")
            etype = parts[2].upper() if len(parts) > 2 else "PIPE"
            item_code = " ".join(parts[3:5]) if len(parts) > 4 else "NPS-6 SCH40"
            material_id = parts[5] if len(parts) > 5 else "A106-B"
            section = _parse_section(item_code)
            if section.id not in sections:
                sections[section.id] = section
            if material_id not in materials:
                try:
                    materials[material_id] = get_material(material_id)
                except KeyError:
                    materials[material_id] = A106_GR_B
            elem_type = {"PIPE": ElementType.PIPE, "ELBOW": ElementType.ELBOW,
                         "TEE": ElementType.TEE, "REDUCER": ElementType.REDUCER,
                         "RIGID": ElementType.RIGID}.get(etype, ElementType.PIPE)
            elements.append(Element(
                id=f"E{len(elements) + 1}",
                type=elem_type,
                from_node=from_node,
                to_node=to_node,
                section=section.id,
                material=material_id,
            ))
        elif kw == "ANCHOR":
            nid = parts[1]
            restraints.append(Restraint(node=nid, type=RestraintType.ANCHOR))
        elif kw == "PRESSURE":
            # PRESSURE <id> <value_pa>
            pressure = float(parts[2])
            load_cases.append(LoadCase(id=parts[1], kind=LoadKind.PRESSURE, pressure=pressure))
        elif kw == "TEMP":
            temp_k = float(parts[2])
            load_cases.append(LoadCase(id=parts[1], kind=LoadKind.THERMAL, temperature=temp_k))
        elif kw == "WEIGHT":
            load_cases.append(LoadCase(id=parts[1] if len(parts) > 1 else "W",
                                       kind=LoadKind.WEIGHT))
        elif kw in ("SUSTAINED", "EXPANSION", "OCCASIONAL"):
            combo_cases = parts[2:] if len(parts) > 2 else []
            combos.append(LoadCombination(
                id=parts[1] if len(parts) > 1 else kw[:3],
                cases=combo_cases,
                category=kw.lower(),
            ))

    if not elements:
        raise ValueError(f"No ELEMENT lines found in {path}")

    return Project(
        name=Path(path).stem,
        nodes=list(nodes.values()),
        elements=elements,
        sections=list(sections.values()),
        materials=list(materials.values()),
        restraints=restraints,
        load_cases=load_cases,
        load_combinations=combos,
    )

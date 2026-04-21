"""Project JSON serialization with versioned schema.

Round-trip: Project → JSON → Project is exact (preserves all values).

Schema versioned via top-level "schema_version" field. Migrations registered
per source-version → target-version pair.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

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


SCHEMA_VERSION = "0.1.0"


def project_to_dict(project: Project) -> dict[str, Any]:
    """Convert a Project to a JSON-serializable dict."""
    return {
        "schema_version": SCHEMA_VERSION,
        "project": {"name": project.name},
        "nodes": [asdict(n) for n in project.nodes],
        "sections": [asdict(s) for s in project.sections],
        "materials": [asdict(m) for m in project.materials],
        "elements": [
            {
                **asdict(e),
                "type": e.type.value,  # enum → string
            }
            for e in project.elements
        ],
        "restraints": [
            {**asdict(r), "type": r.type.value}
            for r in project.restraints
        ],
        "load_cases": [
            {**asdict(lc), "kind": lc.kind.value}
            for lc in project.load_cases
        ],
        "load_combinations": [asdict(c) for c in project.load_combinations],
        "code": project.code,
        "code_version": project.code_version,
    }


def project_to_json(project: Project, indent: int = 2) -> str:
    return json.dumps(project_to_dict(project), indent=indent)


def project_from_dict(data: dict[str, Any]) -> Project:
    """Inverse — load a project from a dict."""
    sv = data.get("schema_version")
    if sv != SCHEMA_VERSION:
        raise NotImplementedError(
            f"Unsupported schema_version {sv} (this build supports {SCHEMA_VERSION}). "
            "Migrations not yet implemented."
        )

    project_meta = data.get("project", {})
    return Project(
        name=project_meta.get("name", "untitled"),
        nodes=[Node(**n) for n in data.get("nodes", [])],
        sections=[Section(**s) for s in data.get("sections", [])],
        materials=[
            Material(
                **{**m, "elastic_modulus": [tuple(p) for p in m["elastic_modulus"]],
                       "thermal_expansion": [tuple(p) for p in m["thermal_expansion"]],
                       "allowable_hot": [tuple(p) for p in m["allowable_hot"]]}
            )
            for m in data.get("materials", [])
        ],
        elements=[
            Element(**{**e, "type": ElementType(e["type"])})
            for e in data.get("elements", [])
        ],
        restraints=[
            Restraint(**{**r, "type": RestraintType(r["type"]),
                          "stiffness": tuple(r.get("stiffness", (0.0, 0.0, 0.0)))})
            for r in data.get("restraints", [])
        ],
        load_cases=[
            LoadCase(**{**lc, "kind": LoadKind(lc["kind"]),
                         "direction": tuple(lc["direction"]) if lc.get("direction") else None})
            for lc in data.get("load_cases", [])
        ],
        load_combinations=[
            LoadCombination(**c) for c in data.get("load_combinations", [])
        ],
        code=data.get("code", "B31.3"),
        code_version=data.get("code_version", "2022"),
    )


def project_from_json(s: str) -> Project:
    return project_from_dict(json.loads(s))


def save_project(project: Project, path: str | Path) -> None:
    Path(path).write_text(project_to_json(project), encoding="utf-8")


def load_project(path: str | Path) -> Project:
    return project_from_json(Path(path).read_text(encoding="utf-8"))

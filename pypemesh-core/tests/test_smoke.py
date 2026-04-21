"""Smoke test — package imports and core data model instantiates."""

from __future__ import annotations

import pypemesh_core
from pypemesh_core import ElementType, Node, Project


def test_version() -> None:
    assert pypemesh_core.__version__.startswith("0.1")


def test_create_empty_project() -> None:
    p = Project(name="smoke")
    assert p.name == "smoke"
    assert p.nodes == []


def test_node_construction() -> None:
    n = Node(id="N10", x=0.0, y=0.0, z=0.0)
    assert n.id == "N10"


def test_element_type_enum() -> None:
    assert ElementType.PIPE == "pipe"

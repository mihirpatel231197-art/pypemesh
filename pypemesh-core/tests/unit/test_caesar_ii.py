"""Caesar II text-format import tests."""

from __future__ import annotations

import pytest

from pypemesh_core.io.caesar_ii import load_caesar_text


def test_load_simple_caesar_text(tmp_path) -> None:
    text = """# Caesar II-style text input
UNITS SI
NODE 10 0.0 0.0 0.0
NODE 20 3.0 0.0 0.0
NODE 30 3.0 0.0 3.0
ELEMENT 10-20 PIPE NPS-6 SCH40 A106-B
ELEMENT 20-30 PIPE NPS-6 SCH40 A106-B
ANCHOR 10
ANCHOR 30
"""
    p = tmp_path / "demo.ctext"
    p.write_text(text)
    project = load_caesar_text(p)
    assert len(project.nodes) == 3
    assert len(project.elements) == 2
    assert len(project.restraints) == 2


def test_caesar_with_loads(tmp_path) -> None:
    text = """UNITS SI
NODE 10 0 0 0
NODE 20 2 0 0
ELEMENT 10-20 PIPE NPS-6 SCH40 A106-B
ANCHOR 10
ANCHOR 20
PRESSURE P1 5000000
TEMP T1 393.15
WEIGHT W
SUSTAINED SUS W P1
"""
    p = tmp_path / "loads.ctext"
    p.write_text(text)
    project = load_caesar_text(p)
    assert len(project.load_cases) == 3
    assert any(lc.kind.value == "pressure" for lc in project.load_cases)
    assert len(project.load_combinations) == 1


def test_caesar_comments_ignored(tmp_path) -> None:
    text = """# top comment
NODE 10 0 0 0  # inline
NODE 20 1 0 0
# middle
ELEMENT 10-20 PIPE NPS-6 SCH40 A106-B
"""
    p = tmp_path / "c.ctext"
    p.write_text(text)
    project = load_caesar_text(p)
    assert len(project.elements) == 1


def test_empty_caesar_raises(tmp_path) -> None:
    p = tmp_path / "e.ctext"
    p.write_text("UNITS SI\n")
    with pytest.raises(ValueError):
        load_caesar_text(p)

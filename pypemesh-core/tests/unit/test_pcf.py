"""PCF file reader tests."""

from __future__ import annotations

import pytest

from pypemesh_core.io.pcf import load_pcf


def test_load_simple_pcf(tmp_path) -> None:
    """A minimal PCF with two pipes should produce a 3-node project."""
    pcf = """ISOGEN-FILES ISOGEN-FILES
PROJECT-IDENTIFIER DEMO

PIPE
    END-COORDS 0 0 0 MM
    END-COORDS 3000 0 0 MM
    ITEM-CODE 6-STD
    MATERIAL A106-B

PIPE
    END-COORDS 3000 0 0 MM
    END-COORDS 6000 0 0 MM
    ITEM-CODE 6-STD
    MATERIAL A106-B
"""
    p = tmp_path / "demo.pcf"
    p.write_text(pcf)
    project = load_pcf(p)

    assert len(project.nodes) == 3  # deduped
    assert len(project.elements) == 2
    assert project.nodes[0].x == 0.0
    assert project.nodes[1].x == 3.0
    assert project.nodes[2].x == 6.0


def test_load_pcf_with_bend(tmp_path) -> None:
    """A bend component should become an elbow element."""
    pcf = """PIPE
    END-COORDS 0 0 0 MM
    END-COORDS 3000 0 0 MM
    ITEM-CODE 6-STD
    MATERIAL A106-B

BEND
    END-COORDS 3000 0 0 MM
    END-COORDS 3000 0 500 MM
    ITEM-CODE 6-ELB
    MATERIAL A106-B
"""
    p = tmp_path / "with-bend.pcf"
    p.write_text(pcf)
    project = load_pcf(p)

    from pypemesh_core.solver.model import ElementType
    assert any(e.type == ElementType.ELBOW for e in project.elements)


def test_load_pcf_default_anchors(tmp_path) -> None:
    """First and last nodes get anchor restraints by default."""
    pcf = """PIPE
    END-COORDS 0 0 0 MM
    END-COORDS 1000 0 0 MM
"""
    p = tmp_path / "single.pcf"
    p.write_text(pcf)
    project = load_pcf(p)
    assert len(project.restraints) == 2
    assert project.restraints[0].node == project.nodes[0].id


def test_load_empty_pcf_raises(tmp_path) -> None:
    p = tmp_path / "empty.pcf"
    p.write_text("PROJECT-IDENTIFIER EMPTY\n")
    with pytest.raises(ValueError):
        load_pcf(p)


def test_load_pcf_comment_handling(tmp_path) -> None:
    """Lines starting with ! should be ignored."""
    pcf = """! This is a comment
PIPE
    ! Another comment
    END-COORDS 0 0 0 MM
    END-COORDS 1000 0 0 MM
"""
    p = tmp_path / "commented.pcf"
    p.write_text(pcf)
    project = load_pcf(p)
    assert len(project.elements) == 1


def test_load_pcf_coord_units(tmp_path) -> None:
    """MM units should be converted to meters."""
    pcf = """PIPE
    END-COORDS 0 0 0 MM
    END-COORDS 1000 2000 3000 MM
"""
    p = tmp_path / "units.pcf"
    p.write_text(pcf)
    project = load_pcf(p)
    assert project.nodes[1].x == pytest.approx(1.0)
    assert project.nodes[1].y == pytest.approx(2.0)
    assert project.nodes[1].z == pytest.approx(3.0)

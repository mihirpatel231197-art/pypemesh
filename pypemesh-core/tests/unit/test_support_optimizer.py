"""Support optimizer tests."""

from __future__ import annotations

from pypemesh_core.optimizer.support_optimizer import (
    apply_recommendations,
    suggest_supports,
)
from pypemesh_core.solver.model import (
    Element, ElementType, Node, Project, Restraint, RestraintType,
)
from tests._helpers import section_6in_sch40, steel_a106b


def _long_unsupported_pipe():
    """10m horizontal pipe anchored only at A → large mid-span deflection."""
    n = 10
    L = 10.0
    nodes = [Node(id=f"N{i}", x=L * i / n, y=0, z=0) for i in range(n + 1)]
    elements = [
        Element(id=f"E{i}", type=ElementType.PIPE,
                from_node=f"N{i}", to_node=f"N{i+1}",
                section="6-STD", material="A106-B")
        for i in range(n)
    ]
    return Project(
        name="long-pipe",
        nodes=nodes, elements=elements,
        sections=[section_6in_sch40()],
        materials=[steel_a106b()],
        restraints=[Restraint(node="N0", type=RestraintType.ANCHOR)],
    )


def test_suggests_supports_for_long_cantilever() -> None:
    project = _long_unsupported_pipe()
    recs = suggest_supports(project, deflection_limit_mm=15.0)
    # Long unsupported pipe should have large tip deflection
    assert len(recs) > 0


def test_no_recommendations_when_well_supported() -> None:
    from tests._helpers import cantilever_project
    project = cantilever_project(length=1.0)  # short pipe
    recs = suggest_supports(project, deflection_limit_mm=100.0)  # generous limit
    assert len(recs) == 0


def test_apply_recommendations_adds_restraints() -> None:
    project = _long_unsupported_pipe()
    recs = suggest_supports(project, deflection_limit_mm=10.0)
    optimized = apply_recommendations(project, recs)
    assert len(optimized.restraints) == len(project.restraints) + len(recs)
    assert "(optimized)" in optimized.name


def test_recommendations_sorted_by_deflection() -> None:
    project = _long_unsupported_pipe()
    recs = suggest_supports(project, deflection_limit_mm=5.0)
    if len(recs) > 1:
        for i in range(len(recs) - 1):
            assert recs[i].deflection_mm >= recs[i + 1].deflection_mm

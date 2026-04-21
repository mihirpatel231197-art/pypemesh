"""Modal analysis verification — analytical cantilever and simply-supported beams.

Reference: DYNAMIC_ANALYSIS.md §9 verification checks.
"""

from __future__ import annotations

import pytest

from pypemesh_core.solver.assembly import assemble_global_mass, assemble_global_stiffness
from pypemesh_core.solver.dynamic import (
    cantilever_first_mode_analytical,
    modal_analysis,
    simply_supported_first_mode_analytical,
)
from pypemesh_core.solver.materials import elastic_modulus_at
from pypemesh_core.solver.model import (
    Element, ElementType, Node, Project, Restraint, RestraintType, Section,
)
from pypemesh_core.solver.sections import cross_section_area, second_moment_of_area
from tests._helpers import cantilever_project, section_6in_sch40, steel_a106b


def _refined_cantilever(length: float = 5.0, n_segments: int = 20) -> Project:
    """A cantilever subdivided into many short elements for accurate modal analysis."""
    nodes = [Node(id=f"N{i}", x=length * i / n_segments, y=0, z=0) for i in range(n_segments + 1)]
    elements = [
        Element(
            id=f"E{i}", type=ElementType.PIPE,
            from_node=f"N{i}", to_node=f"N{i+1}",
            section="6-STD", material="A106-B",
        )
        for i in range(n_segments)
    ]
    return Project(
        name=f"cant-{n_segments}",
        nodes=nodes,
        elements=elements,
        sections=[section_6in_sch40()],
        materials=[steel_a106b()],
        restraints=[Restraint(node="N0", type=RestraintType.ANCHOR)],
    )


def _refined_simply_supported(length: float = 5.0, n_segments: int = 20) -> Project:
    """Simply-supported beam (anchored at both ends in transverse, free axially)."""
    p = _refined_cantilever(length, n_segments)
    p.name = f"ss-{n_segments}"
    last_id = f"N{n_segments}"
    p.restraints = [
        Restraint(node="N0", type=RestraintType.ANCHOR),
        # End restraint: pin (translation only, rotations free)
        Restraint(node=last_id, type=RestraintType.REST,
                  dx=False, dy=True, dz=True, rx=False, ry=False, rz=False),
    ]
    return p


def test_cantilever_first_mode_within_5pct() -> None:
    L = 5.0
    project = _refined_cantilever(L, n_segments=20)
    K, _ = assemble_global_stiffness(project)
    M = assemble_global_mass(project)
    result = modal_analysis(K, M, project, n_modes=5)

    E = elastic_modulus_at(project.materials[0], 293.15)
    I = second_moment_of_area(project.sections[0], structural=True)
    A = cross_section_area(project.sections[0], structural=True)
    rho = project.materials[0].density
    f_analytical = cantilever_first_mode_analytical(L, E, I, rho, A)

    f1 = result.frequencies_hz[0]
    rel_err = abs(f1 - f_analytical) / f_analytical
    # Consistent mass + Euler-Bernoulli should converge to <5% with 20 elements
    assert rel_err < 0.05, (
        f"Cantilever first mode: {f1:.3f} Hz vs analytical {f_analytical:.3f} Hz "
        f"(rel err {rel_err:.4%})"
    )


def test_modes_are_sorted_ascending() -> None:
    project = _refined_cantilever(n_segments=10)
    K, _ = assemble_global_stiffness(project)
    M = assemble_global_mass(project)
    result = modal_analysis(K, M, project, n_modes=5)
    freqs = result.frequencies_hz
    for i in range(len(freqs) - 1):
        assert freqs[i] <= freqs[i + 1], "Frequencies must be ascending"


def test_modes_all_positive() -> None:
    project = _refined_cantilever(n_segments=10)
    K, _ = assemble_global_stiffness(project)
    M = assemble_global_mass(project)
    result = modal_analysis(K, M, project, n_modes=3)
    assert (result.frequencies_hz > 0).all(), "All natural frequencies must be > 0"


def test_n_modes_capped_at_n_dof_minus_1() -> None:
    """Asking for too many modes should silently clamp."""
    project = cantilever_project(length=2.0)  # 2 nodes, 12 DOF, 6 free
    K, _ = assemble_global_stiffness(project)
    M = assemble_global_mass(project)
    # Ask for 100 modes — should clamp to 5 (6-1 free DOFs)
    result = modal_analysis(K, M, project, n_modes=100)
    assert len(result.frequencies_hz) <= 5

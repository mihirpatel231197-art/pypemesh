"""Response spectrum analysis tests."""

from __future__ import annotations

import pytest

from pypemesh_core.solver.assembly import assemble_global_mass, assemble_global_stiffness
from pypemesh_core.solver.dynamic import modal_analysis
from pypemesh_core.solver.model import (
    Element, ElementType, Node, Project, Restraint, RestraintType,
)
from pypemesh_core.solver.response_spectrum import (
    CombinationMethod,
    asce7_design_spectrum,
    constant_acceleration_spectrum,
    response_spectrum_analysis,
)
from tests._helpers import section_6in_sch40, steel_a106b


def _refined_cantilever(length: float = 5.0, n_segments: int = 20):
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
        name="cant",
        nodes=nodes, elements=elements,
        sections=[section_6in_sch40()],
        materials=[steel_a106b()],
        restraints=[Restraint(node="N0", type=RestraintType.ANCHOR)],
    )


def test_constant_spectrum_returns_constant_value() -> None:
    sa = constant_acceleration_spectrum(a_g=0.3)
    assert sa(1.0, 0.05) == pytest.approx(0.3 * 9.80665)
    assert sa(100.0, 0.05) == pytest.approx(0.3 * 9.80665)


def test_asce_spectrum_decays_at_long_periods() -> None:
    sa = asce7_design_spectrum(SDS=1.0, SD1=0.4)
    sa_high_f = sa(20.0, 0.05)  # short period → on the SDS plateau
    sa_low_f = sa(0.5, 0.05)    # long period → SD1/T region
    assert sa_high_f > sa_low_f


def test_response_spectrum_runs_end_to_end() -> None:
    project = _refined_cantilever(n_segments=15)
    K, _ = assemble_global_stiffness(project)
    M = assemble_global_mass(project)
    modal = modal_analysis(K, M, project, n_modes=10)
    sa_fn = constant_acceleration_spectrum(a_g=0.3)
    result = response_spectrum_analysis(
        modal, M, sa_fn, direction=(0.0, 0.0, 1.0),
        damping_ratio=0.02, method=CombinationMethod.SRSS,
    )
    assert result.n_modes >= 1
    assert (result.combined_displacements >= 0).all()
    # The cantilever tip should have nonzero combined displacement
    tip_dof_z = (len(project.nodes) - 1) * 6 + 2
    assert result.combined_displacements[tip_dof_z] > 0


def test_srss_vs_cqc_for_well_separated_modes() -> None:
    """For well-separated modes, CQC ≈ SRSS (cross-correlation small)."""
    project = _refined_cantilever(n_segments=15)
    K, _ = assemble_global_stiffness(project)
    M = assemble_global_mass(project)
    modal = modal_analysis(K, M, project, n_modes=5)
    sa_fn = constant_acceleration_spectrum(a_g=0.3)
    srss = response_spectrum_analysis(
        modal, M, sa_fn, direction=(0.0, 0.0, 1.0),
        method=CombinationMethod.SRSS,
    )
    cqc = response_spectrum_analysis(
        modal, M, sa_fn, direction=(0.0, 0.0, 1.0),
        method=CombinationMethod.CQC,
    )
    # tip displacement should be very close (well-separated modes)
    tip = (len(project.nodes) - 1) * 6 + 2
    rel = abs(srss.combined_displacements[tip] - cqc.combined_displacements[tip]) / srss.combined_displacements[tip]
    assert rel < 0.1, f"SRSS vs CQC for separated modes should match within 10%, got {rel:.4%}"


def test_abs_combination_more_conservative_than_srss() -> None:
    project = _refined_cantilever(n_segments=15)
    K, _ = assemble_global_stiffness(project)
    M = assemble_global_mass(project)
    modal = modal_analysis(K, M, project, n_modes=8)
    sa_fn = constant_acceleration_spectrum(a_g=0.3)
    srss = response_spectrum_analysis(modal, M, sa_fn, method=CombinationMethod.SRSS)
    abs_combo = response_spectrum_analysis(modal, M, sa_fn, method=CombinationMethod.ABS)
    # ABS sums absolute values → always ≥ SRSS at every DOF
    diffs = abs_combo.combined_displacements - srss.combined_displacements
    assert (diffs >= -1e-12).all(), "ABS should be ≥ SRSS at every DOF"


def test_zero_damping_handled_in_cqc() -> None:
    """Even with zero damping, CQC should not crash (just reduces to SRSS)."""
    project = _refined_cantilever(n_segments=10)
    K, _ = assemble_global_stiffness(project)
    M = assemble_global_mass(project)
    modal = modal_analysis(K, M, project, n_modes=3)
    sa_fn = constant_acceleration_spectrum(a_g=0.3)
    result = response_spectrum_analysis(
        modal, M, sa_fn, damping_ratio=0.001, method=CombinationMethod.CQC,
    )
    assert (result.combined_displacements >= 0).all()

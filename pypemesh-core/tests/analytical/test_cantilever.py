"""Cantilever-beam analytical verification.

Tip deflection under a transverse point load: PL^3 / (3EI).
Reference: docs/theory/BEAM_THEORY.md §12, test 3.
"""

from __future__ import annotations

import numpy as np
import pytest

from pypemesh_core.solver.assembly import (
    DOF_PER_NODE,
    assemble_global_stiffness,
    build_dof_map,
    total_dofs,
)
from pypemesh_core.solver.materials import elastic_modulus_at
from pypemesh_core.solver.results import element_end_forces, element_stresses
from pypemesh_core.solver.sections import second_moment_of_area
from pypemesh_core.solver.static import solve_static
from tests._helpers import cantilever_project


def test_cantilever_tip_deflection() -> None:
    """Apply transverse point load P at the free end; verify PL^3/(3EI)."""
    L = 5.0
    P = 1000.0  # N

    project = cantilever_project(length=L)
    K, edata = assemble_global_stiffness(project)

    F = np.zeros(total_dofs(project))
    dof_map = build_dof_map(project)
    F[dof_map["B"] + 2] = -P  # load at B in -z direction (DOF 2)

    result = solve_static(K, F, project)

    E = elastic_modulus_at(project.materials[0], 293.15)
    I = second_moment_of_area(project.sections[0], structural=True)
    expected = -P * L**3 / (3 * E * I)

    tip_deflection_z = result.displacements[dof_map["B"] + 2]
    relative_error = abs(tip_deflection_z - expected) / abs(expected)
    assert relative_error < 0.001, (
        f"Tip deflection {tip_deflection_z:.6e} vs analytical {expected:.6e} "
        f"(rel err {relative_error:.4%})"
    )


def test_cantilever_tip_rotation() -> None:
    """Rotation at free end under a tip moment M: ML/(EI)."""
    L = 5.0
    M = 500.0  # N·m

    project = cantilever_project(length=L)
    K, edata = assemble_global_stiffness(project)

    F = np.zeros(total_dofs(project))
    dof_map = build_dof_map(project)
    F[dof_map["B"] + 4] = M  # moment about y at B

    result = solve_static(K, F, project)

    E = elastic_modulus_at(project.materials[0], 293.15)
    I = second_moment_of_area(project.sections[0], structural=True)
    expected = M * L / (E * I)

    rotation_y = result.displacements[dof_map["B"] + 4]
    relative_error = abs(rotation_y - expected) / abs(expected)
    assert relative_error < 0.001


def test_anchor_reactions_balance_load() -> None:
    """Sum of restraint reactions = applied load (force balance)."""
    L = 5.0
    P = 2500.0
    project = cantilever_project(length=L)
    K, edata = assemble_global_stiffness(project)
    F = np.zeros(total_dofs(project))
    dof_map = build_dof_map(project)
    F[dof_map["B"] + 1] = -P  # transverse y load

    result = solve_static(K, F, project)

    reaction_y = result.reactions["A"][1]
    assert reaction_y == pytest.approx(P, rel=1e-6), (
        f"Reaction y={reaction_y} should equal applied load {P}"
    )

    # Moment balance about A: R_Mz + (-P)*L = 0 → R_Mz = +P*L
    reaction_mz = result.reactions["A"][5]
    assert reaction_mz == pytest.approx(P * L, rel=1e-6)


def test_axial_compression_force_balance() -> None:
    """Apply axial compression to the free end → reaction equal & opposite."""
    L = 3.0
    F_axial = 5000.0
    project = cantilever_project(length=L)
    K, edata = assemble_global_stiffness(project)
    F = np.zeros(total_dofs(project))
    dof_map = build_dof_map(project)
    F[dof_map["B"]] = -F_axial  # push toward A

    result = solve_static(K, F, project)
    assert result.reactions["A"][0] == pytest.approx(F_axial, rel=1e-6)


def test_element_force_recovery_matches_input() -> None:
    """Recovered axial force at the free end should match the applied load."""
    L = 4.0
    F_app = 3000.0
    project = cantilever_project(length=L)
    K, edata = assemble_global_stiffness(project)
    F = np.zeros(total_dofs(project))
    dof_map = build_dof_map(project)
    F[dof_map["B"]] = F_app  # tensile

    result = solve_static(K, F, project)
    forces = element_end_forces(edata, result.displacements)
    ef = forces["E1"]
    assert ef.F_axial_j == pytest.approx(F_app, rel=1e-3)
    assert ef.F_axial_i == pytest.approx(F_app, rel=1e-3)


def test_axial_stress_matches_F_over_A() -> None:
    """σ = F/A for pure axial loading."""
    L = 3.0
    F_app = 10000.0
    project = cantilever_project(length=L)
    K, edata = assemble_global_stiffness(project)
    F = np.zeros(total_dofs(project))
    dof_map = build_dof_map(project)
    F[dof_map["B"]] = F_app

    result = solve_static(K, F, project)
    forces = element_end_forces(edata, result.displacements)
    stresses = element_stresses(project, edata, forces)
    A = edata["E1"]["A"]
    expected_sigma = F_app / A
    assert stresses["E1"].sigma_axial_j == pytest.approx(expected_sigma, rel=1e-3)

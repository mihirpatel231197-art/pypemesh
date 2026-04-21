"""Time-history analysis verification — SDOF oscillator vs analytical.

Reference: DYNAMIC_ANALYSIS.md §5 (Newmark-β) and §9 verification.
"""

from __future__ import annotations

import numpy as np
import pytest
from scipy.sparse import csr_matrix

from pypemesh_core.solver.assembly import assemble_global_mass, assemble_global_stiffness
from pypemesh_core.solver.dynamic import modal_analysis
from pypemesh_core.solver.model import (
    Element, ElementType, Node, Project, Restraint, RestraintType,
)
from pypemesh_core.solver.time_history import (
    newmark_beta_integrate,
    rayleigh_damping,
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
        name="th-cant",
        nodes=nodes, elements=elements,
        sections=[section_6in_sch40()],
        materials=[steel_a106b()],
        restraints=[Restraint(node="N0", type=RestraintType.ANCHOR)],
    )


def test_time_history_free_vibration_oscillates() -> None:
    """Initial displacement + no force → sustained oscillation (no drift, no growth)."""
    project = _refined_cantilever(n_segments=15)
    K, _ = assemble_global_stiffness(project)
    M = assemble_global_mass(project)
    modal = modal_analysis(K, M, project, n_modes=5)
    f1 = modal.frequencies_hz[0]

    # No damping
    n_dof = K.shape[0]
    C = csr_matrix((n_dof, n_dof))

    u0 = np.zeros(n_dof)
    tip_dof_z = (len(project.nodes) - 1) * 6 + 2
    u0[tip_dof_z] = 0.01

    def zero_force(t):
        return np.zeros(n_dof)

    T1 = 1.0 / f1
    result = newmark_beta_integrate(
        K, M, C, zero_force, project,
        total_time=5.0 * T1, n_steps=500, u0=u0,
    )
    tip_history = result.displacements[tip_dof_z, :]

    # Amplitude should stay bounded (avg-accel Newmark is unconditionally stable
    # for linear problems; no amplitude growth)
    max_amp = np.max(np.abs(tip_history))
    assert max_amp <= 1.5 * abs(u0[tip_dof_z]), "Undamped oscillation should not grow"

    # The solution must oscillate — not drift to zero or stay constant
    assert np.std(tip_history) > 0.1 * abs(u0[tip_dof_z]), "Should actually oscillate"

    # Tip should reverse sign at least once (crosses zero → goes negative)
    assert np.any(tip_history < -0.001), "Should swing through zero and reverse"


def test_time_history_damped_oscillation_decays() -> None:
    """With Rayleigh damping, free vibration amplitude should decrease over time."""
    project = _refined_cantilever(n_segments=10)
    K, _ = assemble_global_stiffness(project)
    M = assemble_global_mass(project)

    # High Rayleigh damping for visible decay
    C = rayleigh_damping(M, K, alpha=2.0, beta=0.001)

    n_dof = K.shape[0]
    u0 = np.zeros(n_dof)
    tip_dof_z = (len(project.nodes) - 1) * 6 + 2
    u0[tip_dof_z] = 0.01

    def zero_force(t):
        return np.zeros(n_dof)

    result = newmark_beta_integrate(
        K, M, C, zero_force, project,
        total_time=1.0, n_steps=500, u0=u0,
    )
    # Final amplitude should be much smaller than initial
    initial_amp = abs(u0[tip_dof_z])
    final_amp = np.max(np.abs(result.displacements[tip_dof_z, -50:]))
    assert final_amp < initial_amp * 0.5, "Amplitude should decay with damping"


def test_time_history_zero_initial_zero_force_stays_zero() -> None:
    """No initial condition + no force → zero response throughout."""
    project = _refined_cantilever(n_segments=5)
    K, _ = assemble_global_stiffness(project)
    M = assemble_global_mass(project)
    n_dof = K.shape[0]
    C = csr_matrix((n_dof, n_dof))

    result = newmark_beta_integrate(
        K, M, C, lambda t: np.zeros(n_dof), project,
        total_time=0.1, n_steps=50,
    )
    assert np.max(np.abs(result.displacements)) < 1e-10


def test_rayleigh_damping_formula() -> None:
    """C = αM + βK exactly."""
    from scipy.sparse import eye
    M = eye(6, format="csr") * 2.0
    K = eye(6, format="csr") * 5.0
    C = rayleigh_damping(M, K, alpha=0.1, beta=0.001)
    C_dense = C.toarray()
    M_dense = M.toarray()
    K_dense = K.toarray()
    assert np.allclose(C_dense, 0.1 * M_dense + 0.001 * K_dense)

"""Global stiffness assembly from element contributions.

Sparse matrix assembly via COO triplets, then convert to CSR for solving.
See docs/theory/SOLVER_NUMERICS.md §3.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from scipy.sparse import coo_matrix, csr_matrix

from pypemesh_core.solver.elements.beam import (
    beam_mass_global,
    beam_stiffness_global,
)
from pypemesh_core.solver.elements.elbow import elbow_h, elbow_stiffness_global
from pypemesh_core.solver.materials import elastic_modulus_at, shear_modulus_at
from pypemesh_core.solver.model import ElementType, Project
from pypemesh_core.solver.sections import (
    cross_section_area,
    polar_moment_of_area,
    second_moment_of_area,
)

DOF_PER_NODE = 6


def build_dof_map(project: Project) -> dict[str, int]:
    """Map node id → starting global DOF index."""
    return {node.id: i * DOF_PER_NODE for i, node in enumerate(project.nodes)}


def total_dofs(project: Project) -> int:
    return len(project.nodes) * DOF_PER_NODE


def _lookup(items: list, attr: str, key: str):
    for it in items:
        if getattr(it, attr) == key:
            return it
    raise KeyError(f"Not found: {attr}={key}")


def assemble_global_stiffness(
    project: Project, T_eval: float = 293.15
) -> tuple[csr_matrix, dict[str, NDArray[np.float64]]]:
    """Assemble global K (CSR sparse) at evaluation temperature T_eval [K].

    Returns:
        K_global: (n_dof, n_dof) symmetric sparse matrix
        element_data: dict element_id → {'K_global': (12,12), 'T': (12,12),
                                         'L': float, 'dofs': (12,)}
                      — needed later for stress recovery.

    Notes:
        Only PIPE element type is implemented in this milestone (M1). Elbow,
        tee, reducer, rigid, spring are scheduled for M1.5+ (see MILESTONES.md).
    """
    dof_map = build_dof_map(project)
    n = total_dofs(project)

    rows: list[int] = []
    cols: list[int] = []
    vals: list[float] = []
    element_data: dict[str, NDArray[np.float64]] = {}

    node_index = {n.id: n for n in project.nodes}

    for elem in project.elements:
        if elem.type not in (ElementType.PIPE, ElementType.ELBOW):
            raise NotImplementedError(
                f"Element type {elem.type} not implemented yet. See docs/MILESTONES.md."
            )

        n_start = node_index[elem.from_node]
        n_end = node_index[elem.to_node]
        p_start = np.array([n_start.x, n_start.y, n_start.z])
        p_end = np.array([n_end.x, n_end.y, n_end.z])

        section = _lookup(project.sections, "id", elem.section)
        material = _lookup(project.materials, "id", elem.material)

        E = elastic_modulus_at(material, T_eval)
        G = shear_modulus_at(material, T_eval)
        A = cross_section_area(section, structural=True)
        I = second_moment_of_area(section, structural=True)
        J = polar_moment_of_area(section, structural=True)

        if elem.type == ElementType.ELBOW:
            if elem.bend_radius is None:
                raise ValueError(f"Elbow {elem.id} requires bend_radius")
            h = elbow_h(section.outside_diameter, section.wall_thickness, elem.bend_radius)
            K_e, T_e, L_e = elbow_stiffness_global(
                p_start, p_end, E, G, A, I, J, elem.bend_radius, h
            )
        else:
            K_e, T_e, L_e = beam_stiffness_global(p_start, p_end, E, G, A, I, I, J)

        d_start = dof_map[elem.from_node]
        d_end = dof_map[elem.to_node]
        elem_dofs = np.concatenate([np.arange(d_start, d_start + DOF_PER_NODE),
                                     np.arange(d_end, d_end + DOF_PER_NODE)])

        element_data[elem.id] = {
            "K_global": K_e,
            "T": T_e,
            "L": L_e,
            "dofs": elem_dofs,
            "E": E,
            "G": G,
            "A": A,
            "I": I,
            "J": J,
            "section_id": elem.section,
            "material_id": elem.material,
        }

        for i, gi in enumerate(elem_dofs):
            for j, gj in enumerate(elem_dofs):
                if K_e[i, j] != 0.0:
                    rows.append(int(gi))
                    cols.append(int(gj))
                    vals.append(float(K_e[i, j]))

    K_global = coo_matrix((vals, (rows, cols)), shape=(n, n)).tocsr()
    return K_global, element_data


def assemble_global_mass(project: Project) -> csr_matrix:
    """Assemble global consistent mass matrix.

    Used for modal/dynamic analysis. See DYNAMIC_ANALYSIS.md §2.
    """
    dof_map = build_dof_map(project)
    n = total_dofs(project)
    rows: list[int] = []
    cols: list[int] = []
    vals: list[float] = []

    node_index = {n.id: n for n in project.nodes}

    for elem in project.elements:
        n_start = node_index[elem.from_node]
        n_end = node_index[elem.to_node]
        p_start = np.array([n_start.x, n_start.y, n_start.z])
        p_end = np.array([n_end.x, n_end.y, n_end.z])

        section = _lookup(project.sections, "id", elem.section)
        material = _lookup(project.materials, "id", elem.material)

        from pypemesh_core.solver.sections import (
            cross_section_area,
            insulation_area_per_length,
            polar_moment_of_area,
        )

        A = cross_section_area(section, structural=True)
        # effective density = pipe + insulation per unit area
        rho_eff = material.density
        if section.insulation_density and section.insulation_thickness:
            A_ins = insulation_area_per_length(section)
            rho_eff = (material.density * A + section.insulation_density * A_ins) / A
        J = polar_moment_of_area(section, structural=True)

        M_e, _ = beam_mass_global(p_start, p_end, rho_eff, A, J)

        d_start = dof_map[elem.from_node]
        d_end = dof_map[elem.to_node]
        elem_dofs = np.concatenate([
            np.arange(d_start, d_start + DOF_PER_NODE),
            np.arange(d_end, d_end + DOF_PER_NODE),
        ])

        for i, gi in enumerate(elem_dofs):
            for j, gj in enumerate(elem_dofs):
                if M_e[i, j] != 0.0:
                    rows.append(int(gi))
                    cols.append(int(gj))
                    vals.append(float(M_e[i, j]))

    return coo_matrix((vals, (rows, cols)), shape=(n, n)).tocsr()

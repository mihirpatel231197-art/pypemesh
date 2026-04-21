"""Element load vector assembly — weight, thermal, pressure.

Reference: docs/theory/BEAM_THEORY.md §11 (consistent UDL load) and
docs/theory/PIPE_MECHANICS.md §1.4, §2.

All quantities SI.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pypemesh_core.solver.assembly import DOF_PER_NODE, build_dof_map, total_dofs
from pypemesh_core.solver.materials import elastic_modulus_at, thermal_strain
from pypemesh_core.solver.model import LoadCase, LoadKind, Project
from pypemesh_core.solver.sections import (
    cross_section_area,
    fluid_volume_per_length,
    inside_diameter,
    insulation_area_per_length,
)

GRAVITY = 9.80665  # m/s^2


def _lookup(items: list, attr: str, key: str):
    for it in items:
        if getattr(it, attr) == key:
            return it
    raise KeyError(f"{attr}={key} not found")


def _udl_consistent_local(L: float, w_y: float, w_z: float) -> NDArray[np.float64]:
    """Consistent nodal load vector (12,) for uniform distributed transverse load.

    w_y: load per unit length in local y direction [N/m] (downward = negative)
    w_z: load per unit length in local z direction [N/m]
    Local DOF ordering: [u_i, v_i, w_i, θx_i, θy_i, θz_i, u_j, v_j, w_j, θx_j, θy_j, θz_j]
    See BEAM_THEORY.md §11.
    """
    f = np.zeros(12, dtype=np.float64)
    f[1] = w_y * L / 2.0  # v_i
    f[5] = w_y * L * L / 12.0  # θz_i (moment couple)
    f[7] = w_y * L / 2.0  # v_j
    f[11] = -w_y * L * L / 12.0  # θz_j
    f[2] = w_z * L / 2.0  # w_i
    f[4] = -w_z * L * L / 12.0  # θy_i
    f[8] = w_z * L / 2.0  # w_j
    f[10] = w_z * L * L / 12.0  # θy_j
    return f


def _axial_preload_local(L: float, F_axial: float) -> NDArray[np.float64]:
    """Equivalent nodal force vector (12,) for an axial pre-stress.

    Used for thermal and pressure (Bourdon) loads. Tensile F_axial pulls the
    element apart: -F at node i, +F at node j (in local-x).

    See PIPE_MECHANICS.md §1.4 (Bourdon) and §2.2 (constrained thermal).
    """
    f = np.zeros(12, dtype=np.float64)
    f[0] = -F_axial  # u_i
    f[6] = F_axial  # u_j
    return f


def assemble_load_vector(
    project: Project, element_data: dict, load_case: LoadCase
) -> NDArray[np.float64]:
    """Assemble global load vector for a single load case.

    For weight: distributes pipe self-weight + fluid + insulation as -y UDL
                in *global* frame, transformed to local for each element.
    For thermal: applies axial pre-strain force per element.
    For pressure: applies axial Bourdon pre-strain force per element.

    Args:
        project: full project
        element_data: from assemble_global_stiffness — needs T (12×12), L per elem
        load_case: which load case to assemble

    Returns:
        F_global (n_dof,) load vector.
    """
    n = total_dofs(project)
    F = np.zeros(n, dtype=np.float64)
    dof_map = build_dof_map(project)
    section_index = {s.id: s for s in project.sections}
    material_index = {m.id: m for m in project.materials}

    for elem in project.elements:
        ed = element_data[elem.id]
        L = ed["L"]
        T = ed["T"]
        section = section_index[elem.section]
        material = material_index[elem.material]
        d_start = dof_map[elem.from_node]
        d_end = dof_map[elem.to_node]
        elem_dofs = np.concatenate([
            np.arange(d_start, d_start + DOF_PER_NODE),
            np.arange(d_end, d_end + DOF_PER_NODE),
        ])

        f_local = np.zeros(12, dtype=np.float64)

        if load_case.kind == LoadKind.WEIGHT:
            A_pipe = cross_section_area(section, structural=True)
            w_per_length = A_pipe * material.density * GRAVITY
            # Fluid contents
            if section.insulation_density and section.insulation_thickness:
                w_per_length += insulation_area_per_length(section) * section.insulation_density * GRAVITY
            # We don't yet model fluid — that will come from a "contents" property
            # in a later milestone. For M1 the user specifies it via a custom load.

            # Apply gravity in -global Z: convert to local frame
            # Gravity force per length in global = (0, 0, -w_per_length)
            R = T[0:3, 0:3]  # 3×3 rotation
            g_local = R @ np.array([0.0, 0.0, -w_per_length])
            # local y component: g_local[1], local z: g_local[2]
            f_local += _udl_consistent_local(L, g_local[1], g_local[2])

        elif load_case.kind == LoadKind.THERMAL:
            if load_case.temperature is None:
                raise ValueError(
                    f"Thermal load case {load_case.id} missing temperature parameter"
                )
            T_install = 293.15  # default install temperature; future: per-element
            T_op = load_case.temperature
            E = elastic_modulus_at(material, T_op)
            A = cross_section_area(section, structural=True)
            eps = thermal_strain(material, T_install, T_op)
            F_axial = E * A * eps  # tensile if heating constrained
            f_local += _axial_preload_local(L, F_axial)

        elif load_case.kind == LoadKind.PRESSURE:
            if load_case.pressure is None:
                raise ValueError(
                    f"Pressure load case {load_case.id} missing pressure parameter"
                )
            P = load_case.pressure
            E = elastic_modulus_at(material, 293.15)
            Di = inside_diameter(section)
            Do = section.outside_diameter
            t = section.wall_thickness
            nu = material.poisson
            # Bourdon strain: PD(1-2ν)/(4tE) where D = mean diameter
            D_mean = 0.5 * (Do + Di)
            eps_bourdon = P * D_mean * (1.0 - 2.0 * nu) / (4.0 * t * E)
            A = cross_section_area(section, structural=True)
            F_axial = E * A * eps_bourdon
            f_local += _axial_preload_local(L, F_axial)

        else:
            raise NotImplementedError(
                f"Load kind {load_case.kind} not implemented in M1"
            )

        f_local *= load_case.scale
        f_global = T.T @ f_local
        for i, gi in enumerate(elem_dofs):
            F[gi] += f_global[i]

    return F

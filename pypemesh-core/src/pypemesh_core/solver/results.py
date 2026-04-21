"""Stress and force recovery from solved displacements.

For each element: compute end forces/moments by F_local = K_local @ u_local
(no need for residual subtraction in linear elastic). Then evaluate
longitudinal stress per pipe-mechanics formulas.

Reference: BEAM_THEORY.md §7 + PIPE_MECHANICS.md §5.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

import numpy as np
from numpy.typing import NDArray

from pypemesh_core.solver.model import Project
from pypemesh_core.solver.sections import section_modulus


@dataclass
class ElementForces:
    """End forces/moments in the element's local frame."""

    element_id: str
    F_axial_i: float    # axial force at start node [N], tensile +
    F_axial_j: float    # axial force at end node [N]
    Fy_i: float
    Fy_j: float
    Fz_i: float
    Fz_j: float
    Mx_i: float         # torsion at start [N·m]
    Mx_j: float
    My_i: float         # bending about local y [N·m]
    My_j: float
    Mz_i: float         # bending about local z [N·m]
    Mz_j: float


@dataclass
class ElementStress:
    """Longitudinal stress at each end of an element."""

    element_id: str
    sigma_axial_i: float       # F/A [Pa]
    sigma_bending_i: float     # M_resultant/Z [Pa]
    sigma_axial_j: float
    sigma_bending_j: float


def element_end_forces(
    element_data: dict, displacements: NDArray[np.float64]
) -> dict[str, ElementForces]:
    """Recover end forces/moments for every element from global displacements."""
    out: dict[str, ElementForces] = {}
    for eid, ed in element_data.items():
        u_global = displacements[ed["dofs"]]
        u_local = ed["T"] @ u_global
        # Local-frame element nodal forces:
        #   f_local = K_local @ u_local
        # but we have K_global; use f_global = K_global @ u_global, then rotate.
        f_global = ed["K_global"] @ u_global
        f_local = ed["T"] @ f_global

        out[eid] = ElementForces(
            element_id=eid,
            F_axial_i=float(-f_local[0]),  # negate so tensile is +
            Fy_i=float(f_local[1]),
            Fz_i=float(f_local[2]),
            Mx_i=float(f_local[3]),
            My_i=float(f_local[4]),
            Mz_i=float(f_local[5]),
            F_axial_j=float(f_local[6]),
            Fy_j=float(f_local[7]),
            Fz_j=float(f_local[8]),
            Mx_j=float(f_local[9]),
            My_j=float(f_local[10]),
            Mz_j=float(f_local[11]),
        )
    return out


def element_stresses(
    project: Project,
    element_data: dict,
    forces: dict[str, ElementForces],
) -> dict[str, ElementStress]:
    """Compute axial + bending stress at each element end (no SIF, no pressure)."""
    section_index = {s.id: s for s in project.sections}
    elem_index = {e.id: e for e in project.elements}
    out: dict[str, ElementStress] = {}
    for eid, ef in forces.items():
        elem = elem_index[eid]
        section = section_index[elem.section]
        A = element_data[eid]["A"]
        Z = section_modulus(section, structural=True)

        # Resultant bending moment at each end
        Mb_i = sqrt(ef.My_i**2 + ef.Mz_i**2)
        Mb_j = sqrt(ef.My_j**2 + ef.Mz_j**2)

        out[eid] = ElementStress(
            element_id=eid,
            sigma_axial_i=ef.F_axial_i / A,
            sigma_bending_i=Mb_i / Z,
            sigma_axial_j=ef.F_axial_j / A,
            sigma_bending_j=Mb_j / Z,
        )
    return out

"""ASME B31.12 (Hydrogen Piping and Pipelines) code-compliance check.

B31.12 covers industrial-gas hydrogen piping (Part IP), hydrogen pipelines
(Part PL), and hydrogen fueling stations. Key differences from B31.3:

1. Hydrogen material factor Hf applied to allowable stress (reduces allowable
   by up to ~50% depending on operating pressure for carbon/low-alloy steels
   per B31.12 Table IX-5.1.1)
2. Pipeline section uses design factor approach similar to B31.4/8:
   SL ≤ 0.72 · F · T · SMYS · Hf

This simplified implementation (Part IP, industrial piping subset):
- Sustained:  SL = PD/4t + 0.75·i·Ma/Z ≤ Sh · Hf
- Occasional: SLo ≤ k · Sh · Hf  (k=1.33)
- Expansion:  SE ≤ SA (standard B31.3-style liberal allowable)

The H2 material factor Hf depends on material, pressure, and operating temp.
For design pressures P < 500 psi (3.45 MPa): Hf = 1.0 (no embrittlement risk).
For P between 500-3000 psi: linear de-rate to Hf = 0.7.
For P > 3000 psi: further de-rate to Hf = 0.5-0.6 per table.

Reference: ASME B31.12-2023 Part IP §IP-2.1.
"""

from __future__ import annotations

from pypemesh_core.codes.b31_3 import (
    _bending_resultant,
    _expansion_combined,
    _pressure_long_stress,
    _torsion_stress,
)
from pypemesh_core.codes.base import CodeCheck, CodeResult
from pypemesh_core.codes.sif import sif_for_element
from pypemesh_core.solver.combinations import CombinedSolution, evaluate_combinations
from pypemesh_core.solver.materials import allowable_hot_at
from pypemesh_core.solver.model import LoadKind, Project
from pypemesh_core.solver.sections import section_modulus


OCCASIONAL_FACTOR = 1.33


def hydrogen_material_factor(pressure_pa: float) -> float:
    """Approximate Hf de-rating based on design pressure.

    Simplification of B31.12 Table IX-5.1.1 for common carbon/low-alloy
    steels. In a commercial tier this would be a full material+temperature
    lookup table.
    """
    P_psi = pressure_pa / 6894.757
    if P_psi < 500:
        return 1.0
    if P_psi < 3000:
        # Linear interp 1.0 → 0.7
        return 1.0 - 0.3 * (P_psi - 500) / 2500
    # Above 3000 psi: Hf = 0.6 typical
    return 0.6


class B31_12(CodeCheck):
    code_id = "B31.12"
    version = "2023"

    def __init__(
        self, T_install: float = 293.15, T_evaluation: float | None = None,
        hf_override: float | None = None,
    ):
        self.T_install = T_install
        self.T_evaluation = T_evaluation if T_evaluation is not None else T_install
        self.k_occasional = OCCASIONAL_FACTOR
        self.f_fatigue = 1.0
        self.hf_override = hf_override

    def evaluate(self, project: Project, combinations: list[CombinedSolution] | None = None) -> list[CodeResult]:
        if combinations is None:
            combinations = evaluate_combinations(project, T_eval=self.T_evaluation)

        # Pre-compute sustained SL (for liberal allowable)
        sustained_SL: dict[str, float] = {}
        for combo in combinations:
            if combo.category == "sustained":
                for elem_id, ef in combo.element_forces.items():
                    elem = next(e for e in project.elements if e.id == elem_id)
                    section = next(s for s in project.sections if s.id == elem.section)
                    sif = sif_for_element(elem, section)
                    Z = section_modulus(section, structural=True)
                    P = self._element_pressure(project, combo)
                    sigma_p = _pressure_long_stress(P, section.outside_diameter, section.wall_thickness)
                    Mb = max(
                        _bending_resultant(ef.My_i, ef.Mz_i),
                        _bending_resultant(ef.My_j, ef.Mz_j),
                    )
                    SL = sigma_p + sif.sustained_index * Mb / Z
                    sustained_SL[elem_id] = SL

        results: list[CodeResult] = []
        for combo in combinations:
            for elem_id, ef in combo.element_forces.items():
                elem = next(e for e in project.elements if e.id == elem_id)
                section = next(s for s in project.sections if s.id == elem.section)
                material = next(m for m in project.materials if m.id == elem.material)
                sif = sif_for_element(elem, section)
                Z = section_modulus(section, structural=True)
                Sh = allowable_hot_at(material, self.T_evaluation)
                Sc = material.allowable_cold

                P = self._element_pressure(project, combo)
                Hf = self.hf_override if self.hf_override is not None else hydrogen_material_factor(P)

                Mb_i = _bending_resultant(ef.My_i, ef.Mz_i)
                Mb_j = _bending_resultant(ef.My_j, ef.Mz_j)
                Mb = max(Mb_i, Mb_j)
                Mt = max(abs(ef.Mx_i), abs(ef.Mx_j))

                if combo.category == "sustained":
                    sigma_p = _pressure_long_stress(P, section.outside_diameter, section.wall_thickness)
                    SL = sigma_p + sif.sustained_index * Mb / Z
                    allow = Sh * Hf
                    eq = f"B31.12-sus(Hf={Hf:.2f})"
                    stress = SL

                elif combo.category == "occasional":
                    sigma_p = _pressure_long_stress(P, section.outside_diameter, section.wall_thickness)
                    SLo = sigma_p + sif.sustained_index * Mb / Z
                    allow = self.k_occasional * Sh * Hf
                    eq = f"B31.12-occ(Hf={Hf:.2f})"
                    stress = SLo

                elif combo.category == "expansion":
                    Sb = (sif.i_in_plane * Mb) / Z
                    St = _torsion_stress(Mt, Z)
                    SE = _expansion_combined(Sb, St)
                    SL_sus = sustained_SL.get(elem_id, 0.0)
                    # H2 derates the expansion allowable too
                    SA = self.f_fatigue * (1.25 * (Sc + Sh) - SL_sus) * Hf
                    if SA <= 0:
                        SA = 1.0
                    allow = SA
                    eq = f"B31.12-exp(Hf={Hf:.2f})"
                    stress = SE

                else:
                    continue

                ratio = stress / allow if allow > 0 else float("inf")
                status = "pass" if ratio <= 1.0 else "fail"
                results.append(CodeResult(
                    element_id=elem_id,
                    combination_id=combo.combination_id,
                    stress=stress,
                    allowable=allow,
                    ratio=ratio,
                    status=status,
                    equation_used=eq,
                ))
        return results

    @staticmethod
    def _element_pressure(project: Project, combo: CombinedSolution) -> float:
        case_index = {lc.id: lc for lc in project.load_cases}
        for proj_combo in project.load_combinations:
            if proj_combo.id == combo.combination_id:
                P_max = 0.0
                for case_id in proj_combo.cases:
                    lc = case_index.get(case_id)
                    if lc and lc.kind == LoadKind.PRESSURE and lc.pressure is not None:
                        if lc.pressure > P_max:
                            P_max = lc.pressure
                return P_max
        return 0.0

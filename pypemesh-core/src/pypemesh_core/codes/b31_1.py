"""ASME B31.1 (Power Piping) code-compliance check.

Equations follow B31.1-2022:
- Sustained (Eq. 11A): SL = PD/4t + 0.75·i·Ma/Z ≤ Sh
- Occasional (Eq. 12): SLo = PD/4t + 0.75·i·(Ma+Mb)/Z ≤ k·Sh, k=1.15
- Expansion (Eq. 13):  SE = √(Sb² + 4·St²) ≤ SA, with
                       SA = f·[1.25·Sc + 0.25·Sh]   (more conservative than B31.3)

The differences from B31.3:
- Occasional factor k = 1.15 (vs 1.33 wind / 1.20 seismic in B31.3)
- Expansion allowable doesn't subtract sustained (no liberal allowable)
- Allowables come from ASME B31.1 Appendix A (we reuse same materials lookup
  since open-data tables track ASME II-D values for both codes)

References:
- ASME B31.1-2022 §104.8
- docs/theory/CODE_B31_3.md §7 (cross-code comparison)
"""

from __future__ import annotations

from math import sqrt

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


K_FACTOR_OCCASIONAL = 1.15  # B31.1 §104.8.2


class B31_1(CodeCheck):
    code_id = "B31.1"
    version = "2022"

    def __init__(self, T_install: float = 293.15, T_evaluation: float | None = None):
        self.T_install = T_install
        self.T_evaluation = T_evaluation if T_evaluation is not None else T_install
        self.k_occasional = K_FACTOR_OCCASIONAL
        self.f_fatigue = 1.0

    def evaluate(self, project: Project, combinations: list[CombinedSolution] | None = None) -> list[CodeResult]:
        if combinations is None:
            combinations = evaluate_combinations(project, T_eval=self.T_evaluation)

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

                Mb_i = _bending_resultant(ef.My_i, ef.Mz_i)
                Mb_j = _bending_resultant(ef.My_j, ef.Mz_j)
                Mb = max(Mb_i, Mb_j)
                Mt = max(abs(ef.Mx_i), abs(ef.Mx_j))

                if combo.category == "sustained":
                    P = self._element_pressure(project, combo)
                    sigma_p = _pressure_long_stress(P, section.outside_diameter, section.wall_thickness)
                    SL = sigma_p + sif.sustained_index * Mb / Z
                    allow = Sh
                    eq = "11A"
                    stress = SL

                elif combo.category == "occasional":
                    P = self._element_pressure(project, combo)
                    sigma_p = _pressure_long_stress(P, section.outside_diameter, section.wall_thickness)
                    SLo = sigma_p + sif.sustained_index * Mb / Z
                    allow = self.k_occasional * Sh
                    eq = "12"
                    stress = SLo

                elif combo.category == "expansion":
                    Sb = (sif.i_in_plane * Mb) / Z
                    St = _torsion_stress(Mt, Z)
                    SE = _expansion_combined(Sb, St)
                    # B31.1 Equation 13: SA = f·(1.25·Sc + 0.25·Sh)  (no liberal subtraction)
                    SA = self.f_fatigue * (1.25 * Sc + 0.25 * Sh)
                    allow = SA
                    eq = "13"
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

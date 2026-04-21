"""EN 13480 (European Metallic Industrial Piping) code-compliance check.

Part 3 covers design and calculation. Equations follow the European
convention of using f (nominal design stress) derived from material
properties per the specific part of EN 13480 and the product standard.

Simplified implementation (mirrors B31.3 structure with EN-style allowables):
- Sustained:  σ_lg = P·D/(4·en) + 0.75·i·Ma/Z ≤ f
- Occasional: σ_lg + σ_oc ≤ k·f  (k=1.15)
- Expansion:  σ_e = √(σ_b² + 4·σ_t²) ≤ fa = 1.25·(fc + fh) - σ_lg

(Uses the "liberal allowable" approach similar to B31.3.)

The nominal design stress f is taken as min(Rm/2.4, Rp0.2/1.5) at operating
temperature (EN 13480-3 §4). For our open-data material library, we map
allowable_hot as f_hot and allowable_cold as f_cold.

Reference: EN 13480-3:2017.
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


K_OCCASIONAL = 1.15


class EN_13480(CodeCheck):
    code_id = "EN-13480"
    version = "2017"

    def __init__(self, T_install: float = 293.15, T_evaluation: float | None = None):
        self.T_install = T_install
        self.T_evaluation = T_evaluation if T_evaluation is not None else T_install
        self.f_fatigue = 1.0
        self.k_occasional = K_OCCASIONAL

    def evaluate(self, project: Project, combinations: list[CombinedSolution] | None = None) -> list[CodeResult]:
        if combinations is None:
            combinations = evaluate_combinations(project, T_eval=self.T_evaluation)

        # First pass: collect sustained σ_lg per element for expansion allowable
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
                fh = allowable_hot_at(material, self.T_evaluation)
                fc = material.allowable_cold

                Mb_i = _bending_resultant(ef.My_i, ef.Mz_i)
                Mb_j = _bending_resultant(ef.My_j, ef.Mz_j)
                Mb = max(Mb_i, Mb_j)
                Mt = max(abs(ef.Mx_i), abs(ef.Mx_j))

                if combo.category == "sustained":
                    P = self._element_pressure(project, combo)
                    sigma_p = _pressure_long_stress(P, section.outside_diameter, section.wall_thickness)
                    SL = sigma_p + sif.sustained_index * Mb / Z
                    allow = fh
                    eq = "EN13480-sus"
                    stress = SL

                elif combo.category == "occasional":
                    P = self._element_pressure(project, combo)
                    sigma_p = _pressure_long_stress(P, section.outside_diameter, section.wall_thickness)
                    SLo = sigma_p + sif.sustained_index * Mb / Z
                    allow = self.k_occasional * fh
                    eq = "EN13480-occ"
                    stress = SLo

                elif combo.category == "expansion":
                    Sb = (sif.i_in_plane * Mb) / Z
                    St = _torsion_stress(Mt, Z)
                    SE = _expansion_combined(Sb, St)
                    SL_sus = sustained_SL.get(elem_id, 0.0)
                    fa = self.f_fatigue * (1.25 * (fc + fh) - SL_sus)
                    if fa <= 0:
                        fa = 1.0
                    allow = fa
                    eq = "EN13480-exp"
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

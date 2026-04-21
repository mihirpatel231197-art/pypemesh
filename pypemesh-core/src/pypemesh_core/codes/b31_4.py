"""ASME B31.4 (Liquid Pipeline) code-compliance check.

B31.4 is a pipeline code — different from process piping (B31.3) in
philosophy. Allowables are based on Specified Minimum Yield Strength (SMYS),
not the ASME II-D allowable stress system.

Equations per B31.4-2022:
- Sustained: SL = PD/4t + 0.75·i·Ma/Z ≤ 0.75·F·E·SMYS
  with F (design factor) = 0.72 typical, E (joint efficiency) = 1.0
- Occasional: same with k=1.33
- Expansion: SE = √(Sb² + 4·St²) ≤ 0.72·SMYS

For pipeline materials, allowable_cold field on the Material is interpreted
as SMYS (operations are typically near install temp; high-temp creep not
applicable for buried pipelines).

Reference: ASME B31.4-2022 §402.3.
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
from pypemesh_core.solver.model import LoadKind, Project
from pypemesh_core.solver.sections import section_modulus


DEFAULT_DESIGN_FACTOR = 0.72   # B31.4 §402.3.1, typical above-ground
DEFAULT_JOINT_EFFICIENCY = 1.0
EXPANSION_LIMIT = 0.72         # SE ≤ 0.72·SMYS per B31.4 §402.5
OCCASIONAL_FACTOR = 1.33


class B31_4(CodeCheck):
    code_id = "B31.4"
    version = "2022"

    def __init__(
        self, T_install: float = 293.15, T_evaluation: float | None = None,
        design_factor: float = DEFAULT_DESIGN_FACTOR,
        joint_efficiency: float = DEFAULT_JOINT_EFFICIENCY,
    ):
        self.T_install = T_install
        self.T_evaluation = T_evaluation if T_evaluation is not None else T_install
        self.F = design_factor
        self.E = joint_efficiency
        self.k_occasional = OCCASIONAL_FACTOR

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
                # For B31.4 we interpret allowable_cold as SMYS
                SMYS = material.allowable_cold

                Mb_i = _bending_resultant(ef.My_i, ef.Mz_i)
                Mb_j = _bending_resultant(ef.My_j, ef.Mz_j)
                Mb = max(Mb_i, Mb_j)
                Mt = max(abs(ef.Mx_i), abs(ef.Mx_j))

                if combo.category == "sustained":
                    P = self._element_pressure(project, combo)
                    sigma_p = _pressure_long_stress(P, section.outside_diameter, section.wall_thickness)
                    SL = sigma_p + sif.sustained_index * Mb / Z
                    allow = 0.75 * self.F * self.E * SMYS
                    eq = "B31.4-sus"
                    stress = SL

                elif combo.category == "occasional":
                    P = self._element_pressure(project, combo)
                    sigma_p = _pressure_long_stress(P, section.outside_diameter, section.wall_thickness)
                    SLo = sigma_p + sif.sustained_index * Mb / Z
                    allow = self.k_occasional * 0.75 * self.F * self.E * SMYS
                    eq = "B31.4-occ"
                    stress = SLo

                elif combo.category == "expansion":
                    Sb = (sif.i_in_plane * Mb) / Z
                    St = _torsion_stress(Mt, Z)
                    SE = _expansion_combined(Sb, St)
                    allow = EXPANSION_LIMIT * SMYS
                    eq = "B31.4-exp"
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

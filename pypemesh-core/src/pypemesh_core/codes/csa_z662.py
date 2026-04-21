"""CSA Z662 (Canadian Oil and Gas Pipeline Systems).

The Canadian equivalent of ASME B31.4/B31.8 combined — covers liquid and
gas pipelines. Uses SMYS-based allowables with a design factor F that
varies by location class (Class 1 rural through Class 4 urban).

Equations per CSA Z662-2019 §4.4:
- Sustained: SL ≤ 0.80 · F · L · SMYS  (0.80 vs 0.75 in B31.4/8)
- Expansion: SE ≤ 0.72 · SMYS

L = temperature derating factor (1.0 for most onshore service, lower at high T).

Reference: CSA Z662-2019.
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


# Location class design factor F (CSA Z662-2019 Table 4.2)
CSA_LOCATION_FACTORS = {1: 0.80, 2: 0.72, 3: 0.56, 4: 0.44}
EXPANSION_LIMIT = 0.72
OCCASIONAL_FACTOR = 1.33


class CSA_Z662(CodeCheck):
    code_id = "CSA-Z662"
    version = "2019"

    def __init__(
        self, T_install: float = 293.15, T_evaluation: float | None = None,
        location_class: int = 1, temperature_factor: float = 1.0,
    ):
        if location_class not in CSA_LOCATION_FACTORS:
            raise ValueError(f"location_class must be 1-4, got {location_class}")
        self.T_install = T_install
        self.T_evaluation = T_evaluation if T_evaluation is not None else T_install
        self.location_class = location_class
        self.F = CSA_LOCATION_FACTORS[location_class]
        self.L = temperature_factor

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
                SMYS = material.allowable_cold

                Mb = max(
                    _bending_resultant(ef.My_i, ef.Mz_i),
                    _bending_resultant(ef.My_j, ef.Mz_j),
                )
                Mt = max(abs(ef.Mx_i), abs(ef.Mx_j))

                if combo.category == "sustained":
                    P = self._element_pressure(project, combo)
                    sigma_p = _pressure_long_stress(P, section.outside_diameter, section.wall_thickness)
                    SL = sigma_p + sif.sustained_index * Mb / Z
                    allow = 0.80 * self.F * self.L * SMYS
                    eq = f"CSA-Z662-sus-C{self.location_class}"
                    stress = SL

                elif combo.category == "occasional":
                    P = self._element_pressure(project, combo)
                    sigma_p = _pressure_long_stress(P, section.outside_diameter, section.wall_thickness)
                    SLo = sigma_p + sif.sustained_index * Mb / Z
                    allow = OCCASIONAL_FACTOR * 0.80 * self.F * self.L * SMYS
                    eq = f"CSA-Z662-occ-C{self.location_class}"
                    stress = SLo

                elif combo.category == "expansion":
                    Sb = (sif.i_in_plane * Mb) / Z
                    St = _torsion_stress(Mt, Z)
                    SE = _expansion_combined(Sb, St)
                    allow = EXPANSION_LIMIT * SMYS
                    eq = "CSA-Z662-exp"
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

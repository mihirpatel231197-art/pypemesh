"""DNV-ST-F101 (Submarine Pipeline Systems) — offshore pipeline code.

DNV-ST-F101 (2021, formerly DNV-OS-F101) is the industry standard for
offshore oil and gas pipelines. It uses a partial safety factor (LRFD)
approach unlike the ASME allowable-stress methods.

Key check (simplified, pipe body combined loading):
- σ_eq ≤ η · f_y

where:
- σ_eq = von Mises equivalent stress from pressure + bending + axial
- η = usage factor (default 0.77 for ULS, 0.84 for PLS)
- f_y = SMYS with temperature derating

Equations per DNV-ST-F101 §5.D:
- σ_l (longitudinal) = PD/4t + i·M/Z + F_ax/A
- σ_h (hoop) = PD/2t
- σ_eq = √(σ_l² - σ_l·σ_h + σ_h² + 3·τ²)

**Scope**: linear-static with combined loading. Full LRFD suite (fatigue
per DNV-RP-C203, lateral buckling, local buckling per §5.D.4) deferred
to commercial tier.

Reference: DNV-ST-F101 (2021). Submarine Pipeline Systems.
"""

from __future__ import annotations

from math import sqrt

from pypemesh_core.codes.b31_3 import _bending_resultant, _torsion_stress
from pypemesh_core.codes.base import CodeCheck, CodeResult
from pypemesh_core.codes.sif import sif_for_element
from pypemesh_core.solver.combinations import CombinedSolution, evaluate_combinations
from pypemesh_core.solver.model import LoadKind, Project
from pypemesh_core.solver.sections import cross_section_area, section_modulus


# Usage factors per DNV-ST-F101
USAGE_FACTOR_ULS = 0.77  # Ultimate Limit State, equivalent to "design"
USAGE_FACTOR_PLS = 0.84  # Pressure containment Limit State
USAGE_FACTOR_SLS = 0.96  # Serviceability (for expansion / self-limiting loads)


class DNV_F101(CodeCheck):
    code_id = "DNV-ST-F101"
    version = "2021"

    def __init__(
        self, T_install: float = 293.15, T_evaluation: float | None = None,
        usage_factor: float = USAGE_FACTOR_ULS,
    ):
        self.T_install = T_install
        self.T_evaluation = T_evaluation if T_evaluation is not None else T_install
        self.eta = usage_factor

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
                A = cross_section_area(section, structural=True)
                SMYS = material.allowable_cold

                Do = section.outside_diameter
                t = section.wall_thickness

                Mb = max(
                    _bending_resultant(ef.My_i, ef.Mz_i),
                    _bending_resultant(ef.My_j, ef.Mz_j),
                )
                Mt = max(abs(ef.Mx_i), abs(ef.Mx_j))
                F_ax = max(abs(ef.F_axial_i), abs(ef.F_axial_j))

                P = self._element_pressure(project, combo)

                # Longitudinal: PD/4t + i·M/Z + F/A
                sigma_L = (P * Do) / (4 * t) + sif.i_in_plane * Mb / Z + F_ax / A
                # Hoop (internal pressure)
                sigma_H = (P * Do) / (2 * t)
                # Shear (torsion)
                tau = _torsion_stress(Mt, Z)
                # von Mises
                sigma_eq = sqrt(sigma_L**2 - sigma_L * sigma_H + sigma_H**2 + 3 * tau**2)

                # Use higher usage factor for self-limiting (expansion) loads
                eta = USAGE_FACTOR_SLS if combo.category == "expansion" else self.eta
                allow = eta * SMYS

                ratio = sigma_eq / allow if allow > 0 else float("inf")
                status = "pass" if ratio <= 1.0 else "fail"
                results.append(CodeResult(
                    element_id=elem_id,
                    combination_id=combo.combination_id,
                    stress=sigma_eq,
                    allowable=allow,
                    ratio=ratio,
                    status=status,
                    equation_used=f"DNV-F101-{combo.category}(η={eta:.2f})",
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

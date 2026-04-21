"""ASME Boiler & Pressure Vessel Code Section III — Nuclear Piping.

Implements simplified Class 2 and Class 3 stress equations per Subsections
NC-3600 / ND-3600 (2023 edition):

Design (NC-3652.1): B1·PDo/2t + B2·Do·Ma/(2I) ≤ 1.5·Sh
Level A/B (3652.2):                                 ≤ 1.8·Sh
Level C   (3653):                                   ≤ 2.25·Sh
Level D   (3654):                                   ≤ 3.0·Sh
Expansion (3653.2(c)): iMc/Z ≤ 3·Sc  (simplified; full fatigue check omitted)

B1, B2 are primary-stress indices; for this initial pass we use SIF-style
approximations (B2 = 0.75·i with floor 1.0, B1 = 0.5 for straight pipe —
the real NC-3600 Table NC-3673.2(b)-1 has per-fitting values).

**Important disclaimer:** this implementation is NOT NQA-1 validated and
cannot be used for actual nuclear design/licensing without independent
verification. It's intended for educational and research use.

Class 1 (NB-3600) requires fatigue analysis, thermal stratification,
thermal transients — deferred to a future commercial tier with full
NQA-1 certification.

Reference: ASME B&PV Code Section III Div 1 Subsections NC/ND-3600.
"""

from __future__ import annotations

from enum import Enum

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


class ServiceLevel(str, Enum):
    DESIGN = "design"       # NC-3652.1, allow = 1.5·Sh
    LEVEL_A = "level_a"     # Normal operation, allow = 1.8·Sh
    LEVEL_B = "level_b"     # Upset, allow = 1.8·Sh
    LEVEL_C = "level_c"     # Emergency, allow = 2.25·Sh
    LEVEL_D = "level_d"     # Faulted, allow = 3.0·Sh


SERVICE_LEVEL_FACTORS = {
    ServiceLevel.DESIGN: 1.5,
    ServiceLevel.LEVEL_A: 1.8,
    ServiceLevel.LEVEL_B: 1.8,
    ServiceLevel.LEVEL_C: 2.25,
    ServiceLevel.LEVEL_D: 3.0,
}


def _primary_stress_index_B1() -> float:
    """Axial pressure stress index. Table NC-3673.2(b)-1: B1 = 0.5 for straight pipe."""
    return 0.5


def _primary_stress_index_B2(sif_in_plane: float) -> float:
    """Bending stress index. Approximation: B2 = max(0.75·i, 1.0) for initial impl."""
    return max(0.75 * sif_in_plane, 1.0)


class NuclearSectionIII(CodeCheck):
    """Nuclear Class 2 or 3 (NC-3600 or ND-3600) stress check.

    Full NQA-1 validation and NRC licensing require additional checks:
      - Fatigue (NB-3222.4 for Class 1)
      - Thermal stratification
      - Dynamic event-specific service levels
      - Class 1 full quality assurance
    """

    code_id = "ASME-III-NC"
    version = "2023"

    def __init__(
        self, T_install: float = 293.15, T_evaluation: float | None = None,
        service_class: int = 2,
        service_level: ServiceLevel | str = ServiceLevel.DESIGN,
    ):
        if service_class not in (2, 3):
            raise ValueError(f"Only Class 2 and 3 supported; got {service_class}")
        self.T_install = T_install
        self.T_evaluation = T_evaluation if T_evaluation is not None else T_install
        self.service_class = service_class
        if isinstance(service_level, str):
            service_level = ServiceLevel(service_level)
        self.service_level = service_level
        self.code_id = f"ASME-III-N{'C' if service_class == 2 else 'D'}"

    def evaluate(self, project: Project, combinations: list[CombinedSolution] | None = None) -> list[CodeResult]:
        if combinations is None:
            combinations = evaluate_combinations(project, T_eval=self.T_evaluation)

        level_factor = SERVICE_LEVEL_FACTORS[self.service_level]

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

                Do = section.outside_diameter
                t = section.wall_thickness
                # Use the I = Z·c / (Do/2) = Z · Do/2 — or direct from Section
                from pypemesh_core.solver.sections import second_moment_of_area
                I = second_moment_of_area(section, structural=True)

                B1 = _primary_stress_index_B1()
                B2 = _primary_stress_index_B2(sif.i_in_plane)

                Mb = max(
                    _bending_resultant(ef.My_i, ef.Mz_i),
                    _bending_resultant(ef.My_j, ef.Mz_j),
                )
                Mt = max(abs(ef.Mx_i), abs(ef.Mx_j))

                if combo.category in ("sustained", "operating"):
                    P = self._element_pressure(project, combo)
                    # NC-3652.1 form: B1·PDo/2t + B2·Do·Ma/(2I)
                    stress = B1 * P * Do / (2 * t) + B2 * Do * Mb / (2 * I)
                    allow = level_factor * Sh
                    eq = f"NC-3652.1-{self.service_level.value}"

                elif combo.category == "occasional":
                    P = self._element_pressure(project, combo)
                    # Level B/C treatment
                    stress = B1 * P * Do / (2 * t) + B2 * Do * Mb / (2 * I)
                    allow = level_factor * Sh
                    eq = f"NC-3653-{self.service_level.value}"

                elif combo.category == "expansion":
                    # NC-3653.2(c): iMc/Z ≤ 3·Sc
                    Sb = sif.i_in_plane * Mb / Z
                    St = _torsion_stress(Mt, Z)
                    SE = _expansion_combined(Sb, St)
                    stress = SE
                    allow = 3.0 * Sc
                    eq = "NC-3653.2(c)"

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

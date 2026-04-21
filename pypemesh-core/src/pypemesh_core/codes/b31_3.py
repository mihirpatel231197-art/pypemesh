"""ASME B31.3 (Process Piping) code-compliance check.

Implements:
- Equation 23a (sustained): SL = PD/4t + 0.75·i·Ma/Z ≤ Sh
- Equation 23b (occasional): SLo = PD/4t + 0.75·i·(Ma+Mb)/Z ≤ k·Sh
- Equation 17 (expansion):   SE = sqrt(Sb² + 4·St²) ≤ SA
- SA (allowable) = f·[1.25·(Sc+Sh) - SL]  (liberal allowable)

References:
- ASME B31.3-2022 §319.4
- ASME B31J-2017 (SIF tables)
- docs/theory/CODE_B31_3.md (full derivation)
"""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

from pypemesh_core.codes.base import CodeCheck, CodeResult
from pypemesh_core.codes.sif import sif_for_element
from pypemesh_core.solver.combinations import CombinedSolution, evaluate_combinations
from pypemesh_core.solver.materials import allowable_hot_at, elastic_modulus_at
from pypemesh_core.solver.model import LoadKind, Project
from pypemesh_core.solver.sections import section_modulus


# Occasional load factor k (ASME B31.3 §301.5.3)
K_FACTOR_WIND = 1.33
K_FACTOR_SEISMIC = 1.20


@dataclass
class B31_3Inputs:
    """Per-element values feeding the B31.3 equations."""

    pressure: float       # Pa (sustained)
    Sh: float             # hot allowable [Pa]
    Sc: float             # cold allowable [Pa]
    SL_sustained: float   # SL from equation 23a [Pa]
    f_factor: float       # fatigue cycle factor (1.0 for ≤7000 cycles)


def _pressure_long_stress(P: float, D: float, t: float) -> float:
    """σ_long_pressure = PD/4t (PIPE_MECHANICS §1.2)."""
    return P * D / (4.0 * t)


def _bending_resultant(My: float, Mz: float) -> float:
    return sqrt(My * My + Mz * Mz)


def _torsion_stress(Mx: float, Z: float) -> float:
    """St = Mx / (2Z) for thin-walled circular pipe."""
    return Mx / (2.0 * Z)


def _expansion_combined(Sb: float, St: float) -> float:
    """SE = sqrt(Sb² + 4 St²)  — equation 17 stress intensity."""
    return sqrt(Sb * Sb + 4.0 * St * St)


def _max_pressure_in_combination(project: Project, combo) -> float:
    """Find max pressure across the load cases in a combination."""
    case_index = {lc.id: lc for lc in project.load_cases}
    max_P = 0.0
    for case_id in combo.cases:
        lc = case_index.get(case_id)
        if lc and lc.kind == LoadKind.PRESSURE and lc.pressure is not None:
            if lc.pressure > max_P:
                max_P = lc.pressure
    return max_P


class B31_3(CodeCheck):
    code_id = "B31.3"
    version = "2022"

    def __init__(self, T_install: float = 293.15, T_evaluation: float | None = None):
        self.T_install = T_install
        self.T_evaluation = T_evaluation if T_evaluation is not None else T_install
        # Occasional combination factor — overridable per combination meta
        self.k_occasional = K_FACTOR_WIND
        self.f_fatigue = 1.0

    def evaluate(self, project: Project, combinations: list[CombinedSolution] | None = None) -> list[CodeResult]:
        """Evaluate every load combination against B31.3 rules.

        If combinations is None, automatically solves all from the project.
        """
        if combinations is None:
            combinations = evaluate_combinations(project, T_eval=self.T_evaluation)

        # Index sustained SL per element (used in expansion liberal allowable)
        sustained_SL: dict[str, float] = {}
        for combo in combinations:
            if combo.category == "sustained":
                for elem_id, ef in combo.element_forces.items():
                    elem = next(e for e in project.elements if e.id == elem_id)
                    section = next(s for s in project.sections if s.id == elem.section)
                    sif = sif_for_element(elem, section)
                    Z = section_modulus(section, structural=True)
                    P_max = self._element_pressure(project, combo)
                    sigma_p = _pressure_long_stress(
                        P_max, section.outside_diameter, section.wall_thickness
                    )
                    Mb = _bending_resultant(ef.My_i, ef.Mz_i)  # use start node
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

                # Use the worse of two ends for conservative reporting
                Mb_i = _bending_resultant(ef.My_i, ef.Mz_i)
                Mb_j = _bending_resultant(ef.My_j, ef.Mz_j)
                Mb = max(Mb_i, Mb_j)
                Mt = max(abs(ef.Mx_i), abs(ef.Mx_j))

                if combo.category == "sustained":
                    P = self._element_pressure(project, combo)
                    sigma_p = _pressure_long_stress(P, section.outside_diameter, section.wall_thickness)
                    SL = sigma_p + sif.sustained_index * Mb / Z
                    allow = Sh
                    eq = "23a"
                    stress = SL

                elif combo.category == "occasional":
                    P = self._element_pressure(project, combo)
                    sigma_p = _pressure_long_stress(P, section.outside_diameter, section.wall_thickness)
                    SLo = sigma_p + sif.sustained_index * Mb / Z
                    allow = self.k_occasional * Sh
                    eq = "23b"
                    stress = SLo

                elif combo.category == "expansion":
                    Sb = (sif.i_in_plane * Mb) / Z  # conservative: in-plane SIF on resultant
                    St = _torsion_stress(Mt, Z)
                    SE = _expansion_combined(Sb, St)
                    SL_sus = sustained_SL.get(elem_id, 0.0)
                    SA = self.f_fatigue * (1.25 * (Sc + Sh) - SL_sus)
                    if SA <= 0:
                        SA = 1.0  # degenerate; mark as fail
                    allow = SA
                    eq = "17"
                    stress = SE

                else:
                    continue  # operating-only or unknown category — skip

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
        """Pressure (Pa) seen by elements in this combination — max across pressure cases."""
        case_index = {lc.id: lc for lc in project.load_cases}
        # combo.combination_id maps to project.load_combinations[i]
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

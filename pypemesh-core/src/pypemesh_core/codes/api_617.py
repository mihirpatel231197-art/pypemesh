"""API 617 (American Petroleum Institute) — Axial and Centrifugal
Compressors and Expander-Compressors.

API 617 Table 6 defines allowable forces and moments at compressor
nozzles. This check ensures that pipe loads at machinery connections
don't exceed vendor-acceptance limits, preventing alignment loss and
excessive casing distortion.

The allowable nozzle load is computed as a linear interaction of F/F_allow
and M/M_allow per API 617 §4.3.5.2.

Reference: API Standard 617, 9th Edition (2022). Axial and Centrifugal
Compressors and Expander-Compressors.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt

from pypemesh_core.codes.base import CodeCheck, CodeResult
from pypemesh_core.solver.combinations import CombinedSolution, evaluate_combinations
from pypemesh_core.solver.model import Project


@dataclass
class MachineryNozzle:
    """A machinery nozzle with API 617 allowable loads."""

    node_id: str
    F_allow: float       # allowable resultant force [N]
    M_allow: float       # allowable resultant moment [N·m]
    interaction_limit: float = 2.0  # linear interaction limit per API 617


class API_617(CodeCheck):
    """API 617 compressor nozzle load check.

    Unlike stress codes, this checks restraint REACTIONS against vendor
    allowables at designated machinery nozzles (compressor, turbine,
    pump suction/discharge).
    """

    code_id = "API-617"
    version = "2022"

    def __init__(
        self, nozzles: list[MachineryNozzle] | None = None,
        T_install: float = 293.15, T_evaluation: float | None = None,
    ):
        self.nozzles = nozzles or []
        self.T_install = T_install
        self.T_evaluation = T_evaluation if T_evaluation is not None else T_install

    def evaluate(self, project: Project, combinations: list[CombinedSolution] | None = None) -> list[CodeResult]:
        if combinations is None:
            combinations = evaluate_combinations(project, T_eval=self.T_evaluation)

        results: list[CodeResult] = []
        for combo in combinations:
            for nz in self.nozzles:
                if nz.node_id not in combo.reactions:
                    continue
                R = combo.reactions[nz.node_id]
                F_resultant = sqrt(R[0]**2 + R[1]**2 + R[2]**2)
                M_resultant = sqrt(R[3]**2 + R[4]**2 + R[5]**2)
                F_ratio = F_resultant / nz.F_allow if nz.F_allow > 0 else 0
                M_ratio = M_resultant / nz.M_allow if nz.M_allow > 0 else 0
                total_ratio = F_ratio + M_ratio

                status = "pass" if total_ratio <= nz.interaction_limit else "fail"
                results.append(CodeResult(
                    element_id=nz.node_id,
                    combination_id=combo.combination_id,
                    stress=total_ratio * 1e6,  # fake-Pa so rendering stays consistent
                    allowable=nz.interaction_limit * 1e6,
                    ratio=total_ratio / nz.interaction_limit,
                    status=status,
                    equation_used="API-617-nozzle",
                ))
        return results

"""NORSOK L-002 — Piping Design, Layout and Stress Analysis.

Norwegian offshore standard widely used in the North Sea. Follows ASME
B31.3 equations but with additional offshore-specific requirements
(dynamic loading from waves, hull motions) and conservative allowables.

Implementation: B31.3 with allowable factor (fa_factor) that reduces
sustained and occasional allowables by 10% for offshore environment.

Reference: NORSOK L-002:2017. Piping System Layout, Design and Structural
Analysis.
"""

from __future__ import annotations

from pypemesh_core.codes.b31_3 import B31_3


# NORSOK applies a 0.9 reduction factor on sustained allowables for offshore.
NORSOK_OFFSHORE_FACTOR = 0.9


class NORSOK_L002(B31_3):
    code_id = "NORSOK-L-002"
    version = "2017"

    def evaluate(self, project, combinations=None):
        results = super().evaluate(project, combinations)
        for r in results:
            # Apply offshore conservatism to sustained/occasional
            if r.combination_id and ("SUS" in r.combination_id.upper()
                                     or "OCC" in r.combination_id.upper()):
                r.allowable *= NORSOK_OFFSHORE_FACTOR
                r.ratio = r.stress / r.allowable if r.allowable > 0 else float("inf")
                r.status = "pass" if r.ratio <= 1.0 else "fail"
                r.equation_used = r.equation_used.replace("23a", "NORSOK-sus").replace("23b", "NORSOK-occ")
        return results

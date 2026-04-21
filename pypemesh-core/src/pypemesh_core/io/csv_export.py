"""CSV export for per-node stress and per-restraint reactions.

Simple flat CSVs suitable for Excel / pandas consumption.
"""

from __future__ import annotations

import csv
import io
from pathlib import Path

from pypemesh_core.codes.base import CodeResult
from pypemesh_core.solver.combinations import CombinedSolution


def results_to_csv(results: list[CodeResult]) -> str:
    """Render code-check results as CSV text."""
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["element_id", "combination_id", "equation", "stress_pa",
                "allowable_pa", "ratio", "status"])
    for r in results:
        w.writerow([r.element_id, r.combination_id, r.equation_used,
                    f"{r.stress:.6e}", f"{r.allowable:.6e}",
                    f"{r.ratio:.6f}", r.status])
    return buf.getvalue()


def reactions_to_csv(combinations: list[CombinedSolution]) -> str:
    """Render per-combination restraint reactions as CSV."""
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["combination", "node", "Fx_N", "Fy_N", "Fz_N",
                "Mx_Nm", "My_Nm", "Mz_Nm"])
    for combo in combinations:
        for node_id, r in combo.reactions.items():
            w.writerow([combo.combination_id, node_id,
                        f"{r[0]:.3f}", f"{r[1]:.3f}", f"{r[2]:.3f}",
                        f"{r[3]:.3f}", f"{r[4]:.3f}", f"{r[5]:.3f}"])
    return buf.getvalue()


def save_results_csv(results: list[CodeResult], path: str | Path) -> None:
    Path(path).write_text(results_to_csv(results), encoding="utf-8")


def save_reactions_csv(combinations: list[CombinedSolution], path: str | Path) -> None:
    Path(path).write_text(reactions_to_csv(combinations), encoding="utf-8")

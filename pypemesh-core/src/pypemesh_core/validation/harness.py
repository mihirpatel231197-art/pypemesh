"""Benchmark validation harness.

Loads a project + expected-results pair, runs the solver + B31.3 check, and
reports per-quantity diffs against tolerance. Used by:

- pypemesh-core/tests/ — fast benchmarks for CI gating
- benchmarks/run_all.py — full benchmark suite for releases

Reference: docs/VALIDATION_PLAN.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from pypemesh_core.codes.b31_3 import B31_3
from pypemesh_core.io.project import load_project
from pypemesh_core.solver.assembly import build_dof_map, total_dofs
from pypemesh_core.solver.combinations import evaluate_combinations


@dataclass
class BenchmarkResult:
    name: str
    passed: bool
    failures: list[str]
    summary: dict[str, Any]


def _within(actual: float, expected: float, *, abs_tol: float = 0.0, rel_tol: float = 0.01) -> bool:
    """True if actual is within tolerance of expected."""
    if expected == 0:
        return abs(actual) <= abs_tol
    return abs(actual - expected) / abs(expected) <= rel_tol or abs(actual - expected) <= abs_tol


def run_benchmark(benchmark_dir: str | Path) -> BenchmarkResult:
    """Run the benchmark in the given directory.

    Expected layout:
        benchmark_dir/
          model.json        — pypemesh project JSON
          expected.json     — expected results
          tolerance.yaml    — per-quantity tolerances (optional, default rel=0.01)
    """
    bd = Path(benchmark_dir)
    name = bd.name

    project = load_project(bd / "model.json")
    expected = (bd / "expected.json").read_text(encoding="utf-8")
    import json as _json
    expected_data = _json.loads(expected)

    tol_path = bd / "tolerance.yaml"
    if tol_path.exists():
        tolerances = yaml.safe_load(tol_path.read_text())
    else:
        tolerances = {"default_rel": 0.01}

    rel_tol = float(tolerances.get("default_rel", 0.01))
    abs_tol = float(tolerances.get("default_abs", 0.0))

    failures: list[str] = []

    # Solve
    combos = evaluate_combinations(project)
    checker = B31_3()
    results = checker.evaluate(project, combinations=combos)

    # Compare displacements (per-node, optional)
    if "displacements" in expected_data:
        dof_map = build_dof_map(project)
        for node_id, exp_per_node in expected_data["displacements"].items():
            base = dof_map[node_id]
            for combo_label, exp in exp_per_node.items():
                target_combo = next(c for c in combos if c.combination_id == combo_label)
                actual = target_combo.displacements[base + exp["dof"]]
                if not _within(actual, exp["value"], abs_tol=abs_tol, rel_tol=rel_tol):
                    failures.append(
                        f"Disp {node_id} dof={exp['dof']} combo={combo_label}: "
                        f"actual={actual:.6e} vs expected={exp['value']:.6e}"
                    )

    # Compare stress ratios per element/combination
    if "stress_ratios" in expected_data:
        result_by_key = {(r.element_id, r.combination_id): r for r in results}
        for key_str, exp_ratio in expected_data["stress_ratios"].items():
            elem_id, combo_id = key_str.split(":")
            r = result_by_key.get((elem_id, combo_id))
            if not r:
                failures.append(f"Missing result for {key_str}")
                continue
            if not _within(r.ratio, exp_ratio, abs_tol=abs_tol, rel_tol=rel_tol):
                failures.append(
                    f"Stress ratio {key_str}: actual={r.ratio:.4f} vs expected={exp_ratio:.4f}"
                )

    summary = {
        "n_nodes": len(project.nodes),
        "n_elements": len(project.elements),
        "n_combinations": len(combos),
        "n_failures": len(failures),
        "rel_tol": rel_tol,
    }
    return BenchmarkResult(name=name, passed=not failures, failures=failures, summary=summary)


def run_all_benchmarks(benchmarks_root: str | Path) -> list[BenchmarkResult]:
    root = Path(benchmarks_root)
    results: list[BenchmarkResult] = []
    for bd in sorted(root.iterdir()):
        if bd.is_dir() and (bd / "model.json").exists():
            results.append(run_benchmark(bd))
    return results

"""Validation harness end-to-end test against the included benchmark."""

from __future__ import annotations

from pathlib import Path

from pypemesh_core.validation.harness import run_benchmark, run_all_benchmarks


REPO_ROOT = Path(__file__).resolve().parents[2]
BENCHMARKS_DIR = REPO_ROOT / "benchmarks"


def test_fixed_pressure_benchmark_passes() -> None:
    bench = BENCHMARKS_DIR / "fixed_pressure_b31_3"
    if not bench.exists():
        # Skip if running outside repo context
        import pytest
        pytest.skip(f"benchmark dir not found: {bench}")
    result = run_benchmark(bench)
    assert result.passed, f"Benchmark failed: {result.failures}"
    assert result.summary["n_failures"] == 0


def test_run_all_benchmarks_smoke() -> None:
    if not BENCHMARKS_DIR.exists():
        import pytest
        pytest.skip("benchmarks dir not found")
    results = run_all_benchmarks(BENCHMARKS_DIR)
    assert len(results) > 0
    for r in results:
        assert r.passed, f"{r.name}: {r.failures}"

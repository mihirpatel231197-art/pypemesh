"""CLI smoke tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from pypemesh_core.cli import main as cli_main
from pypemesh_core.io.project import save_project
from tests._helpers import cantilever_project
from pypemesh_core.solver.model import LoadCase, LoadCombination, LoadKind


def _project_with_loads():
    p = cantilever_project()
    p.load_cases = [
        LoadCase(id="W", kind=LoadKind.WEIGHT),
        LoadCase(id="P1", kind=LoadKind.PRESSURE, pressure=5e6),
    ]
    p.load_combinations = [
        LoadCombination(id="SUS", cases=["W", "P1"], category="sustained"),
    ]
    return p


def test_cli_version(capsys) -> None:
    code = cli_main(["version"])
    assert code == 0
    out = capsys.readouterr().out
    assert "pypemesh-core" in out


def test_cli_validate(tmp_path, capsys) -> None:
    p = _project_with_loads()
    project_path = tmp_path / "test.json"
    save_project(p, project_path)
    code = cli_main(["validate", str(project_path)])
    assert code == 0
    out = capsys.readouterr().out
    assert "OK" in out


def test_cli_solve_pretty(tmp_path, capsys) -> None:
    p = _project_with_loads()
    project_path = tmp_path / "test.json"
    save_project(p, project_path)
    code = cli_main(["solve", str(project_path)])
    assert code == 0  # PASS
    out = capsys.readouterr().out
    assert "PASS" in out
    assert "B31.3" in out


def test_cli_solve_json(tmp_path, capsys) -> None:
    p = _project_with_loads()
    project_path = tmp_path / "test.json"
    save_project(p, project_path)
    code = cli_main(["solve", "--json", str(project_path)])
    assert code == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["project_name"] == p.name
    assert len(data["results"]) >= 1


def test_cli_report(tmp_path) -> None:
    p = _project_with_loads()
    project_path = tmp_path / "test.json"
    save_project(p, project_path)
    out_path = tmp_path / "report.pdf"
    code = cli_main(["report", str(project_path), "-o", str(out_path)])
    assert code == 0
    assert out_path.exists()
    assert out_path.read_bytes().startswith(b"%PDF")


def test_cli_bench(capsys) -> None:
    repo = Path(__file__).resolve().parents[3]
    bench_dir = repo / "benchmarks"
    if not bench_dir.exists():
        pytest.skip("benchmarks dir not found")
    code = cli_main(["bench", str(bench_dir)])
    assert code == 0
    out = capsys.readouterr().out
    assert "passed" in out or "failures" in out

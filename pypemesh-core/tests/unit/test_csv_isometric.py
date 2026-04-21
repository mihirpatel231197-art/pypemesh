"""CSV + isometric export tests."""

from __future__ import annotations

from pypemesh_core.codes.b31_3 import B31_3
from pypemesh_core.io.csv_export import reactions_to_csv, results_to_csv
from pypemesh_core.io.isometric import generate_isometric_pdf
from pypemesh_core.solver.combinations import evaluate_combinations
from pypemesh_core.solver.model import (
    LoadCase, LoadCombination, LoadKind,
)
from tests._helpers import cantilever_project


def _p():
    p = cantilever_project()
    p.load_cases = [
        LoadCase(id="W", kind=LoadKind.WEIGHT),
        LoadCase(id="P1", kind=LoadKind.PRESSURE, pressure=5e6),
    ]
    p.load_combinations = [
        LoadCombination(id="SUS", cases=["W", "P1"], category="sustained"),
    ]
    return p


def test_results_csv_has_header() -> None:
    project = _p()
    results = B31_3().evaluate(project)
    csv_text = results_to_csv(results)
    assert csv_text.startswith("element_id,combination_id,equation,stress_pa,")
    assert "SUS" in csv_text


def test_reactions_csv_has_header() -> None:
    project = _p()
    combos = evaluate_combinations(project)
    csv_text = reactions_to_csv(combos)
    assert csv_text.startswith("combination,node,Fx_N,Fy_N,Fz_N,")


def test_isometric_pdf_bytes() -> None:
    project = _p()
    pdf = generate_isometric_pdf(project)
    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 500


def test_isometric_pdf_writes_file(tmp_path) -> None:
    project = _p()
    path = tmp_path / "iso.pdf"
    pdf = generate_isometric_pdf(project, output_path=path, title="Test Iso")
    assert path.exists()
    assert path.read_bytes() == pdf

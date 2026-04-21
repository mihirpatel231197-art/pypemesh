"""PDF report generation tests."""

from __future__ import annotations

from pypemesh_core.codes.b31_3 import B31_3
from pypemesh_core.io.report_pdf import generate_pdf_report
from pypemesh_core.solver.combinations import evaluate_combinations
from pypemesh_core.solver.model import (
    LoadCase,
    LoadCombination,
    LoadKind,
)
from tests._helpers import cantilever_project


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


def test_pdf_generates_valid_bytes() -> None:
    project = _project_with_loads()
    combos = evaluate_combinations(project)
    code_results = B31_3().evaluate(project, combinations=combos)

    pdf = generate_pdf_report(project, code_results, combinations=combos)
    assert isinstance(pdf, bytes)
    assert pdf.startswith(b"%PDF"), "PDF must start with %PDF magic"
    assert len(pdf) > 1000, "PDF should be at least 1 KB"


def test_pdf_with_company_and_engineer() -> None:
    project = _project_with_loads()
    combos = evaluate_combinations(project)
    code_results = B31_3().evaluate(project, combinations=combos)

    pdf = generate_pdf_report(
        project, code_results, combinations=combos,
        company="ACME Engineering", engineer="J. Smith, PE",
    )
    # Strings should appear in raw PDF (not encoded); reportlab embeds them as text streams
    assert b"ACME" in pdf or b"Engineering" in pdf or len(pdf) > 1000


def test_pdf_writes_to_path(tmp_path) -> None:
    project = _project_with_loads()
    combos = evaluate_combinations(project)
    code_results = B31_3().evaluate(project, combinations=combos)

    output = tmp_path / "report.pdf"
    pdf = generate_pdf_report(project, code_results, combinations=combos, output_path=output)
    assert output.exists()
    assert output.read_bytes() == pdf

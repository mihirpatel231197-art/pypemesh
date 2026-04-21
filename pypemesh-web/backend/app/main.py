"""FastAPI entry point for the pypemesh backend.

Endpoints:
  GET  /                  — service info
  GET  /health            — liveness probe
  POST /solve             — submit a project JSON, run solver + code check
  POST /validate          — validate a project JSON without solving
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel

import pypemesh_core
from pypemesh_core.codes.b31_1 import B31_1
from pypemesh_core.codes.b31_3 import B31_3
from pypemesh_core.codes.b31_4 import B31_4
from pypemesh_core.io.project import project_from_dict
from pypemesh_core.io.report_pdf import generate_pdf_report
from pypemesh_core.solver.assembly import assemble_global_mass, assemble_global_stiffness
from pypemesh_core.solver.combinations import evaluate_combinations
from pypemesh_core.solver.dynamic import modal_analysis


CODE_REGISTRY = {
    "B31.3": B31_3,
    "B31.1": B31_1,
    "B31.4": B31_4,
}

app = FastAPI(
    title="pypemesh API",
    version=pypemesh_core.__version__,
    description="Pipe stress analysis API. Validated ASME B31.3 solver. See /docs.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://pypemesh.vercel.app",
        "https://pypemesh-mihirdpatel23-1371s-projects.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Health(BaseModel):
    status: str
    core_version: str


@app.get("/health", response_model=Health)
async def health() -> Health:
    return Health(status="ok", core_version=pypemesh_core.__version__)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "service": "pypemesh-backend",
        "version": pypemesh_core.__version__,
        "docs": "/docs",
    }


class SolveRequest(BaseModel):
    project: dict[str, Any]
    code: str = "B31.3"
    T_evaluation: float | None = None  # K


class SolveResponse(BaseModel):
    status: str
    project_name: str
    n_nodes: int
    n_elements: int
    n_load_cases: int
    n_combinations: int
    code: str
    results: list[dict[str, Any]]
    summary: dict[str, Any]


@app.post("/solve", response_model=SolveResponse)
async def solve(req: SolveRequest) -> SolveResponse:
    try:
        project = project_from_dict(req.project)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid project: {e}")

    if req.code not in CODE_REGISTRY:
        raise HTTPException(
            status_code=400,
            detail=f"Code {req.code} not implemented. Supported: {list(CODE_REGISTRY)}",
        )

    T_eval = req.T_evaluation if req.T_evaluation is not None else 293.15

    try:
        combos = evaluate_combinations(project, T_eval=T_eval)
        CodeCls = CODE_REGISTRY[req.code]
        checker = CodeCls(T_evaluation=T_eval)
        results = checker.evaluate(project, combinations=combos)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Solver error: {e}")

    serialized = [
        {
            "element_id": r.element_id,
            "combination_id": r.combination_id,
            "stress_pa": r.stress,
            "allowable_pa": r.allowable,
            "ratio": r.ratio,
            "status": r.status,
            "equation": r.equation_used,
        }
        for r in results
    ]

    failed = [r for r in results if r.status == "fail"]
    max_ratio = max((r.ratio for r in results), default=0.0)

    return SolveResponse(
        status="ok",
        project_name=project.name,
        n_nodes=len(project.nodes),
        n_elements=len(project.elements),
        n_load_cases=len(project.load_cases),
        n_combinations=len(project.load_combinations),
        code=req.code,
        results=serialized,
        summary={
            "total_checks": len(results),
            "failed": len(failed),
            "max_ratio": max_ratio,
            "overall_status": "fail" if failed else "pass",
        },
    )


class ReportRequest(BaseModel):
    project: dict[str, Any]
    company: str = ""
    engineer: str = ""
    T_evaluation: float | None = None


@app.post("/report")
async def report(req: ReportRequest) -> Response:
    """Generate a PDF stress analysis report for the given project."""
    try:
        project = project_from_dict(req.project)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid project: {e}")

    T_eval = req.T_evaluation if req.T_evaluation is not None else 293.15
    code_id = project.code if project.code in CODE_REGISTRY else "B31.3"
    try:
        combos = evaluate_combinations(project, T_eval=T_eval)
        CodeCls = CODE_REGISTRY[code_id]
        code_results = CodeCls(T_evaluation=T_eval).evaluate(project, combinations=combos)
        pdf_bytes = generate_pdf_report(
            project, code_results, combinations=combos,
            company=req.company, engineer=req.engineer,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report error: {e}")

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{project.name}_b31_3_report.pdf"'
        },
    )


class ModesRequest(BaseModel):
    project: dict[str, Any]
    n_modes: int = 10
    T_evaluation: float | None = None


class ModeShape(BaseModel):
    """Per-node displacement for a single mode (just translation, normalized)."""

    mode_index: int
    frequency_hz: float
    period_s: float
    # Per-node (dx, dy, dz) displacement, normalized to max|d| = 1
    node_displacements: dict[str, list[float]]


class ModesResponse(BaseModel):
    status: str
    project_name: str
    n_modes: int
    frequencies_hz: list[float]
    angular_frequencies: list[float]
    periods_s: list[float]
    mode_shapes: list[ModeShape] = []


@app.post("/modes", response_model=ModesResponse)
async def modes(req: ModesRequest) -> ModesResponse:
    """Solve the eigenproblem and return frequencies + normalized mode shapes."""
    try:
        project = project_from_dict(req.project)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid project: {e}")

    T_eval = req.T_evaluation if req.T_evaluation is not None else 293.15
    try:
        K, _ = assemble_global_stiffness(project, T_eval=T_eval)
        M = assemble_global_mass(project)
        result = modal_analysis(K, M, project, n_modes=req.n_modes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Modal solver error: {e}")

    # Build per-mode per-node translations, normalized for visualization
    import numpy as _np
    shapes: list[ModeShape] = []
    for i in range(len(result.frequencies_hz)):
        phi = result.mode_shapes[:, i]
        # Translation entries are at DOF offsets 0,1,2 within each 6-DOF node block
        node_disp: dict[str, list[float]] = {}
        peak = 0.0
        for j, n in enumerate(project.nodes):
            base = j * 6
            d = [float(phi[base]), float(phi[base + 1]), float(phi[base + 2])]
            mag = (d[0] ** 2 + d[1] ** 2 + d[2] ** 2) ** 0.5
            if mag > peak:
                peak = mag
            node_disp[n.id] = d
        if peak > 0:
            for nid in node_disp:
                node_disp[nid] = [v / peak for v in node_disp[nid]]
        shapes.append(ModeShape(
            mode_index=i,
            frequency_hz=float(result.frequencies_hz[i]),
            period_s=float(result.periods_s[i]) if result.periods_s[i] != float("inf") else 0.0,
            node_displacements=node_disp,
        ))

    return ModesResponse(
        status="ok",
        project_name=project.name,
        n_modes=len(result.frequencies_hz),
        frequencies_hz=result.frequencies_hz.tolist(),
        angular_frequencies=result.angular_freq.tolist(),
        periods_s=[float(t) if t != float("inf") else 0.0 for t in result.periods_s],
        mode_shapes=shapes,
    )


@app.post("/validate")
async def validate_project(req: SolveRequest) -> dict[str, Any]:
    """Parse-and-validate a project without running the solver."""
    try:
        project = project_from_dict(req.project)
        return {
            "status": "ok",
            "project_name": project.name,
            "n_nodes": len(project.nodes),
            "n_elements": len(project.elements),
            "n_load_cases": len(project.load_cases),
            "n_combinations": len(project.load_combinations),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid project: {e}")

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
from pydantic import BaseModel

import pypemesh_core
from pypemesh_core.codes.b31_3 import B31_3
from pypemesh_core.io.project import project_from_dict
from pypemesh_core.solver.combinations import evaluate_combinations

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

    if req.code != "B31.3":
        raise HTTPException(status_code=400, detail=f"Code {req.code} not implemented (only B31.3)")

    T_eval = req.T_evaluation if req.T_evaluation is not None else 293.15

    try:
        combos = evaluate_combinations(project, T_eval=T_eval)
        checker = B31_3(T_evaluation=T_eval)
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

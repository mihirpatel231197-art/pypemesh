"""FastAPI endpoint tests."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app

from pypemesh_core.io.project import project_to_dict
from pypemesh_core.solver.model import (
    Element, ElementType, LoadCase, LoadCombination, LoadKind,
    Material, Node, Project, Restraint, RestraintType, Section,
)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def sample_project_dict() -> dict:
    p = Project(
        name="api-test",
        nodes=[Node(id="A", x=0, y=0, z=0), Node(id="B", x=2.0, y=0, z=0)],
        elements=[Element(
            id="E1", type=ElementType.PIPE,
            from_node="A", to_node="B",
            section="6-STD", material="A106-B",
        )],
        sections=[Section(id="6-STD", outside_diameter=0.1683, wall_thickness=0.00711)],
        materials=[Material(
            id="A106-B", name="ASTM A106 Gr.B",
            elastic_modulus=[(293.15, 2.03e11)],
            thermal_expansion=[(293.15, 11.5e-6)],
            allowable_hot=[(293.15, 138e6)],
            allowable_cold=138e6, density=7850.0, poisson=0.3,
        )],
        restraints=[
            Restraint(node="A", type=RestraintType.ANCHOR),
            Restraint(node="B", type=RestraintType.ANCHOR),
        ],
        load_cases=[
            LoadCase(id="W", kind=LoadKind.WEIGHT),
            LoadCase(id="P1", kind=LoadKind.PRESSURE, pressure=5e6),
        ],
        load_combinations=[
            LoadCombination(id="SUS", cases=["W", "P1"], category="sustained"),
        ],
    )
    return project_to_dict(p)


def test_health(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_root(client: TestClient) -> None:
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["service"] == "pypemesh-backend"


def test_validate_endpoint(client: TestClient, sample_project_dict: dict) -> None:
    r = client.post("/validate", json={"project": sample_project_dict})
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["project_name"] == "api-test"
    assert data["n_nodes"] == 2


def test_solve_endpoint_returns_correct_stress(
    client: TestClient, sample_project_dict: dict
) -> None:
    r = client.post("/solve", json={"project": sample_project_dict})
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["summary"]["total_checks"] == 1
    assert data["summary"]["overall_status"] == "pass"
    # PD/4t = 5e6 × 0.1683 / (4 × 0.00711) = 29.59 MPa
    result = data["results"][0]
    assert result["status"] == "pass"
    assert result["equation"] == "23a"
    assert 29e6 <= result["stress_pa"] <= 30e6
    assert 0.20 <= result["ratio"] <= 0.22


def test_solve_invalid_project_returns_400(client: TestClient) -> None:
    r = client.post("/solve", json={"project": {"invalid": "data"}})
    assert r.status_code == 400


def test_unsupported_code_returns_400(client: TestClient, sample_project_dict: dict) -> None:
    r = client.post("/solve", json={"project": sample_project_dict, "code": "MADE-UP-CODE"})
    assert r.status_code == 400


def test_b31_1_code_works(client: TestClient, sample_project_dict: dict) -> None:
    """Backend /solve should accept B31.1 in addition to B31.3."""
    r = client.post("/solve", json={"project": sample_project_dict, "code": "B31.1"})
    assert r.status_code == 200
    data = r.json()
    assert data["code"] == "B31.1"
    # B31.1 sustained uses equation 11A
    sus = next(r for r in data["results"] if r["combination_id"] == "SUS")
    assert sus["equation"] == "11A"


def test_modes_endpoint(client: TestClient) -> None:
    """Modal analysis needs free DOFs — use a cantilever (one anchor) for this test."""
    cant = Project(
        name="cant-modal",
        nodes=[Node(id="A", x=0, y=0, z=0), Node(id="B", x=2.0, y=0, z=0)],
        elements=[Element(
            id="E1", type=ElementType.PIPE,
            from_node="A", to_node="B",
            section="6-STD", material="A106-B",
        )],
        sections=[Section(id="6-STD", outside_diameter=0.1683, wall_thickness=0.00711)],
        materials=[Material(
            id="A106-B", name="ASTM A106 Gr.B",
            elastic_modulus=[(293.15, 2.03e11)],
            thermal_expansion=[(293.15, 11.5e-6)],
            allowable_hot=[(293.15, 138e6)],
            allowable_cold=138e6, density=7850.0, poisson=0.3,
        )],
        restraints=[Restraint(node="A", type=RestraintType.ANCHOR)],
        load_cases=[], load_combinations=[],
    )
    r = client.post("/modes", json={"project": project_to_dict(cant), "n_modes": 3})
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["n_modes"] >= 1
    assert all(f > 0 for f in data["frequencies_hz"])
    freqs = data["frequencies_hz"]
    for i in range(len(freqs) - 1):
        assert freqs[i] <= freqs[i + 1]


def test_modes_fully_constrained_returns_500(
    client: TestClient, sample_project_dict: dict
) -> None:
    """Fully-constrained model has no free DOFs → graceful 500."""
    r = client.post("/modes", json={"project": sample_project_dict, "n_modes": 5})
    assert r.status_code == 500
    assert "free DOF" in r.json()["detail"] or "constrained" in r.json()["detail"]


def test_report_endpoint_returns_pdf(client: TestClient, sample_project_dict: dict) -> None:
    r = client.post("/report", json={
        "project": sample_project_dict,
        "company": "ACME",
        "engineer": "J. Smith, PE",
    })
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert r.content.startswith(b"%PDF")
    assert len(r.content) > 1000
    assert "attachment" in r.headers.get("content-disposition", "")

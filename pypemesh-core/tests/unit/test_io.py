"""Project I/O round-trip tests."""

from __future__ import annotations

from pypemesh_core.io.project import (
    project_from_json,
    project_to_json,
)
from pypemesh_core.solver.model import (
    LoadCase,
    LoadCombination,
    LoadKind,
)
from tests._helpers import cantilever_project


def test_round_trip_cantilever() -> None:
    p = cantilever_project()
    s = project_to_json(p)
    assert "schema_version" in s
    assert "cantilever" in s
    p2 = project_from_json(s)
    assert p2.name == p.name
    assert len(p2.nodes) == len(p.nodes)
    assert len(p2.elements) == len(p.elements)
    assert p2.elements[0].type == p.elements[0].type


def test_round_trip_with_loads_and_combinations() -> None:
    p = cantilever_project()
    p.load_cases = [
        LoadCase(id="W", kind=LoadKind.WEIGHT),
        LoadCase(id="P1", kind=LoadKind.PRESSURE, pressure=5e6),
        LoadCase(id="T1", kind=LoadKind.THERMAL, temperature=393.15),
    ]
    p.load_combinations = [
        LoadCombination(id="SUS", cases=["W", "P1"], category="sustained"),
        LoadCombination(id="EXP", cases=["T1"], category="expansion"),
    ]
    p2 = project_from_json(project_to_json(p))
    assert len(p2.load_cases) == 3
    assert p2.load_cases[1].pressure == 5e6
    assert p2.load_cases[2].temperature == 393.15
    assert p2.load_combinations[0].category == "sustained"


def test_round_trip_solver_compatibility() -> None:
    """A round-tripped project must produce the same solver result."""
    from pypemesh_core.solver.assembly import (
        assemble_global_stiffness,
        build_dof_map,
        total_dofs,
    )
    from pypemesh_core.solver.static import solve_static
    import numpy as np

    p = cantilever_project()
    p2 = project_from_json(project_to_json(p))

    K1, _ = assemble_global_stiffness(p)
    K2, _ = assemble_global_stiffness(p2)
    assert (K1 - K2).max() < 1e-9

    F = np.zeros(total_dofs(p))
    dof_map = build_dof_map(p)
    F[dof_map["B"] + 2] = -1000.0

    r1 = solve_static(K1, F.copy(), p)
    r2 = solve_static(K2, F.copy(), p2)
    assert np.allclose(r1.displacements, r2.displacements, atol=1e-12)

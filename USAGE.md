# Usage Guide

Practical examples of running pypemesh — Python API, CLI, REST API, and the web UI.

## Install

```bash
git clone https://github.com/mihirpatel231197-art/pypemesh.git
cd pypemesh

# Core solver (Python library + CLI)
pip install -e ./pypemesh-core

# Backend API (optional — for the web UI)
pip install -e ./pypemesh-web/backend
```

Requires Python 3.11+.

## 1. Python API — solve a model end-to-end

```python
from pypemesh_core.solver.model import (
    Element, ElementType, LoadCase, LoadCombination, LoadKind,
    Node, Project, Restraint, RestraintType, Section,
)
from pypemesh_core.materials.library import A106_GR_B
from pypemesh_core.solver.combinations import evaluate_combinations
from pypemesh_core.codes.b31_3 import B31_3
from pypemesh_core.io.report_pdf import generate_pdf_report

# Build a fixed-fixed pipe under thermal expansion
project = Project(
    name="my-line",
    nodes=[
        Node(id="A", x=0.0, y=0.0, z=0.0),
        Node(id="B", x=5.0, y=0.0, z=0.0),
    ],
    elements=[
        Element(
            id="E1", type=ElementType.PIPE,
            from_node="A", to_node="B",
            section="6-STD", material="A106-B",
        ),
    ],
    sections=[Section(id="6-STD", outside_diameter=0.1683, wall_thickness=0.00711)],
    materials=[A106_GR_B],
    restraints=[
        Restraint(node="A", type=RestraintType.ANCHOR),
        Restraint(node="B", type=RestraintType.ANCHOR),
    ],
    load_cases=[
        LoadCase(id="W", kind=LoadKind.WEIGHT),
        LoadCase(id="P1", kind=LoadKind.PRESSURE, pressure=5e6),  # 50 bar
        LoadCase(id="T1", kind=LoadKind.THERMAL, temperature=393.15),  # 120°C
    ],
    load_combinations=[
        LoadCombination(id="SUS", cases=["W", "P1"], category="sustained"),
        LoadCombination(id="EXP", cases=["T1"], category="expansion"),
    ],
)

# Run solver and B31.3 code check
combinations = evaluate_combinations(project)
results = B31_3().evaluate(project, combinations=combinations)

for r in results:
    print(f"{r.element_id} {r.combination_id} eq.{r.equation_used}: "
          f"{r.stress/1e6:.1f} MPa / {r.allowable/1e6:.1f} MPa "
          f"= {r.ratio:.3f} {r.status.upper()}")

# Generate a PDF report
generate_pdf_report(
    project, results, combinations=combinations,
    output_path="my_report.pdf",
    company="ACME Engineering", engineer="J. Smith, PE",
)
```

## 2. CLI — solve a saved project file

```bash
# Save a project from Python
python -c "
from pypemesh_core.io.project import save_project
from pypemesh_core.solver.model import (
    Element, ElementType, LoadCase, LoadCombination, LoadKind,
    Node, Project, Restraint, RestraintType, Section,
)
from pypemesh_core.materials.library import A106_GR_B

p = Project(name='cli-demo', ...)  # build as above
save_project(p, 'demo.json')
"

# Solve and print pretty table
pypemesh solve demo.json

# Machine-readable JSON output (for piping to jq)
pypemesh solve --json demo.json | jq .

# Generate a PDF report
pypemesh report demo.json --output report.pdf --engineer "J. Smith, PE"

# Validate without solving
pypemesh validate demo.json

# Run all benchmarks (validation harness)
pypemesh bench
```

CLI exits 0 if all checks pass, 1 if any fail — useful in CI.

## 3. REST API — call from any language

Start the backend:

```bash
cd pypemesh-web/backend
uvicorn app.main:app --reload
```

Opens at http://localhost:8000. OpenAPI docs at /docs.

### Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness probe |
| GET | `/` | Service info |
| POST | `/solve` | Run solver + B31.3, return per-element results |
| POST | `/modes` | Modal analysis — first N natural frequencies |
| POST | `/report` | Generate PDF report (returns binary PDF) |
| POST | `/validate` | Parse-and-validate without solving |

### Example — POST /solve

```bash
curl -X POST http://localhost:8000/solve \
  -H "Content-Type: application/json" \
  -d '{
    "project": {
      "schema_version": "0.1.0",
      "project": { "name": "from-curl" },
      "nodes": [...],
      ...
    }
  }'
```

Response:
```json
{
  "status": "ok",
  "project_name": "from-curl",
  "n_nodes": 5,
  "n_elements": 4,
  "results": [
    {
      "element_id": "E1",
      "combination_id": "SUS",
      "stress_pa": 29588607.6,
      "allowable_pa": 138000000.0,
      "ratio": 0.214,
      "status": "pass",
      "equation": "23a"
    }
  ],
  "summary": { "total_checks": 8, "failed": 0, "max_ratio": 0.305, "overall_status": "pass" }
}
```

## 4. Web UI

The web UI is hosted on Vercel: **https://pypemesh.vercel.app**

What works there today:
- Pick from 4 sample piping models
- 3D viewport (orbit/pan/zoom)
- Click nodes/elements for properties
- Run B31.3 check with color-coded stress overlay
- Compute first 5 natural frequencies (modal analysis)
- Per-element stress table with stress, allowable, ratio
- PDF report download (requires backend)

The web UI uses mock results when the backend isn't reachable, so the demo
works on Vercel without backend deployment. Run the backend locally
(`uvicorn app.main:app --reload`) and set `VITE_API_BASE` to use real solver
output.

## 5. Project JSON schema

Projects are stored as versioned JSON. See `pypemesh-core/src/pypemesh_core/io/project.py`
for the full schema (`SCHEMA_VERSION = "0.1.0"`). High-level shape:

```json
{
  "schema_version": "0.1.0",
  "project": { "name": "string" },
  "nodes": [ { "id": "...", "x": 0.0, "y": 0.0, "z": 0.0 } ],
  "elements": [ { "id": "E1", "type": "pipe", "from_node": "A", "to_node": "B",
                  "section": "6-STD", "material": "A106-B" } ],
  "sections": [ { "id": "6-STD", "outside_diameter": 0.1683, "wall_thickness": 0.00711 } ],
  "materials": [ { "id": "A106-B", ..., "elastic_modulus": [[T_K, E_Pa], ...] } ],
  "restraints": [ { "node": "A", "type": "anchor" } ],
  "load_cases": [ { "id": "W", "kind": "weight" }, ... ],
  "load_combinations": [ { "id": "SUS", "cases": ["W", "P1"], "category": "sustained" } ],
  "code": "B31.3",
  "code_version": "2022"
}
```

All quantities **SI**: meters, Newtons, Pascals, Kelvin, kilograms, seconds.

## 6. Testing your install

```bash
cd pypemesh-core
pip install -e ".[dev]"
pytest
```

You should see:
```
78 passed in ~1s
TOTAL coverage: 92%
```

If anything fails, please open an issue: https://github.com/mihirpatel231197-art/pypemesh/issues

## 7. Common tasks

### Query a stress at a specific element/combination

```python
sustained_at_E1 = next(
    r for r in results
    if r.element_id == "E1" and r.combination_id == "SUS"
)
print(f"Sustained ratio: {sustained_at_E1.ratio:.3f}")
```

### Iterate over restraint reactions

```python
for combo in combinations:
    print(f"\n{combo.combination_id} ({combo.category}):")
    for node_id, react in combo.reactions.items():
        print(f"  {node_id}: Fx={react[0]:.1f} N, Fy={react[1]:.1f} N, "
              f"Fz={react[2]:.1f} N")
```

### Use a different material from the library

```python
from pypemesh_core.materials.library import (
    A106_GR_B, A312_TP304, A335_P91, HDPE_PE100, list_materials,
)

print("Available materials:")
for mat_id, name in list_materials():
    print(f"  {mat_id} — {name}")
```

### Run modal analysis

```python
from pypemesh_core.solver.assembly import (
    assemble_global_mass, assemble_global_stiffness,
)
from pypemesh_core.solver.dynamic import modal_analysis

K, _ = assemble_global_stiffness(project)
M = assemble_global_mass(project)
result = modal_analysis(K, M, project, n_modes=10)

for i, f in enumerate(result.frequencies_hz, start=1):
    print(f"Mode {i}: {f:.2f} Hz (period {result.periods_s[i-1]:.4f} s)")
```

## 8. Limitations (today)

What works:
- Static linear analysis, fully validated against analytical solutions
- ASME B31.3 sustained, occasional, expansion
- Pipe + elbow elements
- Modal analysis (eigenvalue solver)
- 11 materials with temperature-dependent properties

What's coming (see `docs/MILESTONES.md`):
- Non-linear (gaps, friction)
- Response spectrum, time-history dynamics
- Tee, reducer, rigid, spring elements
- More codes: B31.1, B31.4, B31.8, EN 13480
- Buried pipe, plastic piping
- AI support optimizer
- CAD plugins

What's out of scope (see `docs/REQUIREMENTS.md` §"explicitly out of scope"):
- Process simulation (HYSYS territory)
- Hydraulic transient analysis (PIPENET territory)
- Pressure vessel design (PV Elite territory)

## 9. Validation

Every release runs against the benchmark suite (`pypemesh bench`). Current
benchmarks:
- `fixed_pressure_b31_3` — fixed-fixed 6" SCH 40 at 50 bar (ratio 0.214 ±2%)

Plus 78 unit + analytical tests against:
- Analytical beam theory (cantilever PL³/3EI, thermal EAαΔT to 0.1%)
- Modal analysis (cantilever first mode to 0.02%)
- B31.3 worked examples from `docs/theory/CODE_B31_3.md`
- SIF formulas (6" LR elbow h ≈ 0.247, k ≈ 6.68, i ≈ 2.28 per Markl)

See `docs/VALIDATION_PLAN.md` for the full validation strategy.

# Architecture

**Version:** 0.1
**Status:** Planning

Companion to `REQUIREMENTS.md`. Defines *how* we build what's specified there.

## Guiding principle

**The solver is a library. Everything else is a UI.**

If we do this right, the same `pypemesh_core` package powers the web app, the
desktop app, the CLI, batch-mode CI runners, and any future integration.
UIs are swappable; physics is not.

## Package topology

```
┌──────────────────────────────────────────────────────────────────┐
│                         pypemesh-core                            │
│  (Python library — pip-installable, MIT)                         │
│                                                                   │
│  solver/     codes/     materials/   fittings/   io/             │
│  validation/                                                      │
└──────────────────────────────────────────────────────────────────┘
                               ▲
                               │  imports
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
┌───────────────┐    ┌──────────────────┐    ┌────────────────┐
│  pypemesh-web │    │ pypemesh-desktop │    │  pypemesh-cli  │
│               │    │                  │    │                │
│  FastAPI +    │    │  Qt/PySide6      │    │  Typer CLI     │
│  React/Three  │    │  (Phase C)       │    │  (batch runs)  │
└───────────────┘    └──────────────────┘    └────────────────┘
        │
        │  hosts
        ▼
   ┌──────────┐
   │  Vercel  │  (frontend static)
   └──────────┘
   ┌──────────┐
   │ Railway  │  (FastAPI backend — Python workloads don't run on Vercel)
   │ or Fly   │
   └──────────┘
```

### Why split frontend and backend hosts

Vercel runs serverless JS; it can't host a long-running Python scientific
workload (SciPy sparse solve on 10K nodes takes seconds, well beyond typical
serverless budgets). We host the frontend on Vercel (fast static + edge CDN)
and the backend on Railway or Fly (real Python processes, persistent state).

## Module breakdown

### `pypemesh-core/solver/`

- `model.py` — pure data classes: `Node`, `Element`, `Material`, `LoadCase`, `Restraint`
- `assembly.py` — global stiffness/mass matrix assembly from element-level contributions
- `elements/beam.py` — Euler-Bernoulli 3D beam element (stiffness, mass, stress recovery)
- `elements/pipe_elbow.py` — curved pipe with Karman ovalization flexibility factor
- `elements/rigid.py` — infinitely stiff element (master-slave DOF coupling)
- `elements/spring.py` — linear/nonlinear spring support
- `static.py` — static linear solve (sparse direct or CG)
- `nonlinear.py` — Newton-Raphson for gaps/friction
- `dynamic.py` — eigensolve, response spectrum combinations
- `results.py` — displacement, force, stress recovery at nodes

### `pypemesh-core/codes/`

- `base.py` — `CodeCheck` abstract base class with `evaluate(results, context) -> CodeResult`
- `b31_3.py` — ASME B31.3 implementation (B phase priority)
- `b31_1.py` — B31.1 (B.1 phase)
- `b31_4.py`, `b31_8.py`, `b31_12.py` — (B.2 and C phase)
- `en_13480.py` — European standard (C phase)
- `nuclear_section_iii.py` — nuclear (C phase, requires NQA-1)

Each code module:
- Owns its allowable-stress equations
- Owns its SIF lookup logic
- Owns its report template strings
- Registers itself via entry point (plugin pattern)

### `pypemesh-core/materials/`

- `database.py` — `MaterialDB` class with lookup-by-spec, temp interpolation
- `open_data/` — B-phase material cards (JSON), sourced from public papers + API handbooks
- `licensed/` — (C only, not in repo) ASME Section II Part D cards, shipped encrypted with license check
- `custom.py` — user-defined material handling with schema validation

### `pypemesh-core/fittings/`

- `catalog.py` — fitting lookup by standard + size + schedule
- `b16_9.py` — ASME B16.9 welding fittings (elbows, tees, reducers, caps)
- `b16_5.py` — ASME B16.5 flanges
- `b36_10.py`, `b36_19.py` — pipe dimensions
- `custom.py` — user-defined fittings

### `pypemesh-core/io/`

- `project.py` — native JSON project format, versioned schema, migration registry
- `pcf.py` — PCF (Piping Component File) reader + writer
- `step.py` — STEP geometry read (via `steputils` — stretch)
- `report_pdf.py` — PDF report generator (via ReportLab)

### `pypemesh-core/validation/`

- `benchmarks/` — one subdirectory per official test case
  - `asme_b31_3_appendix_s/` — input JSON + expected output + test script
  - `nc_3600/` — nuclear sample problem
  - `markl_fatigue/` — SIF verification
  - `peng_ch5/`, `peng_ch7/` — textbook problems
- `harness.py` — runs all benchmarks, reports pass/fail with tolerances
- `regression.py` — CI integration, fails build on >1% drift

### `pypemesh-web/frontend/` (React + Vite + TypeScript)

```
src/
├── App.tsx
├── main.tsx
├── components/
│   ├── modeler/         # 3D viewport, Three.js scene
│   ├── tree/            # model tree panel
│   ├── spreadsheet/     # Caesar-style tabular editor
│   ├── props/           # property panel
│   ├── results/         # stress/displacement visualization
│   └── reports/         # report preview
├── state/
│   ├── store.ts         # Zustand store (project state)
│   ├── undo.ts          # undo/redo stack (immer patches)
│   └── sync.ts          # cloud sync layer
├── api/                 # FastAPI client
└── lib/
    ├── three-scene.ts   # Three.js scene manager
    ├── shortcuts.ts     # keyboard shortcut registry
    └── geometry.ts      # client-side geometry helpers
```

### `pypemesh-web/backend/` (FastAPI)

```
app/
├── main.py              # FastAPI app, CORS, routing
├── routes/
│   ├── projects.py      # CRUD for projects
│   ├── solve.py         # POST /solve, async job
│   └── exports.py       # PDF/CSV/PCF export
├── services/
│   ├── solver_runner.py # wraps pypemesh-core, handles timeouts
│   └── job_queue.py     # Celery or RQ for long solves
├── models/              # SQLAlchemy ORM (projects, users, orgs)
├── auth.py              # JWT + OAuth (Phase C adds SSO)
└── schemas.py           # Pydantic request/response models
```

## Data model (persistence)

Native project format (JSON, versioned):

```json
{
  "schema_version": "0.1",
  "project": {
    "id": "uuid",
    "name": "string",
    "created_at": "iso8601",
    "author": "string"
  },
  "units": {"length": "mm", "force": "N", "pressure": "bar", "temperature": "C"},
  "nodes": [{"id": "N10", "x": 0, "y": 0, "z": 0}],
  "elements": [{"id": "E1", "type": "pipe", "from": "N10", "to": "N20", "material": "A106-B", "section": "6-STD"}],
  "materials": [{"id": "A106-B", "properties": {"E_at_T": [[20, 2.03e5], [200, 1.92e5]], ...}}],
  "sections": [{"id": "6-STD", "OD": 168.3, "wall": 7.11}],
  "restraints": [{"node": "N10", "type": "anchor"}],
  "load_cases": [{"id": "W", "kind": "weight", "scale": 1.0}],
  "load_combinations": [{"id": "SUS", "cases": ["W", "P1"], "category": "sustained"}],
  "code_check": {"code": "B31.3", "version": "2022"}
}
```

Database (Phase C):
- PostgreSQL for project metadata + user/org/auth
- Project payloads stored as JSONB (indexable, versioned)
- S3 (or R2) for large attachments (drawings, reports)

## API contracts

### REST (Phase B)

| Method | Path | Purpose |
|---|---|---|
| `GET /projects` | list | |
| `POST /projects` | create | |
| `GET /projects/:id` | fetch full JSON | |
| `PUT /projects/:id` | save | |
| `POST /projects/:id/solve` | kick off solver job | returns `job_id` |
| `GET /jobs/:id` | poll status | `pending`/`running`/`complete`/`failed` |
| `GET /jobs/:id/results` | fetch results | |
| `POST /projects/:id/export/pdf` | generate report | |

### WebSocket (Phase C)

Real-time collaboration: CRDT patches over WS for multi-user editing.
Yjs or Automerge as the CRDT engine.

## Plugin system

Codes, materials, fittings, and CAD adapters load via Python entry points:

```toml
# a third-party "pypemesh-en-13480" package's pyproject.toml
[project.entry-points."pypemesh.codes"]
en_13480 = "pypemesh_en_13480.code:EN13480Code"
```

Core's code registry discovers and validates these at startup. Third parties
can ship commercial codes as separate packages without forking the core.

## Solver job execution

```
User clicks "Run Analysis"
    │
    ▼
Frontend POST /solve → Backend
    │
    ▼
Backend validates project, pushes to queue (RQ/Celery) → returns job_id
    │
    ▼
Worker process imports pypemesh_core, builds model, runs solve, writes results
    │
    ▼
Frontend polls /jobs/:id → gets `complete` → fetches /jobs/:id/results
    │
    ▼
Renders displacement/stress overlay on 3D viewport + populates results panel
```

Long solves stream progress via SSE or WS (Phase B.1).

## Cross-cutting concerns

- **Logging**: structured (JSON), every solver step recorded, replayable
- **Error handling**: typed errors (`SolverError`, `ConvergenceError`, `CodeCheckError`) with user-actionable messages
- **Units**: all internal math in SI; UI converts on display. Never mix.
- **Precision**: float64 throughout. Stress results truncate to 3 sig figs for display, not for storage.
- **Security**: input validation at API boundary (Pydantic), no exec/eval of user data, file uploads sandboxed
- **Observability**: OpenTelemetry traces for solver pipeline (Phase C)

## Directory conventions

- `src/` layout for Python (not flat) — forces proper installs, avoids import shadows
- TypeScript strict mode, no `any`
- Pre-commit hooks: ruff (lint + format), mypy, prettier, eslint
- CI: GitHub Actions matrix (Python 3.11/3.12, Node 20/22, Ubuntu/macOS/Windows)

# pypemesh

**Open-source pipe stress analysis platform. Commercial path B→C.**

Goal: match the capability of Caesar II + AutoPIPE + CAEPIPE + FEPipe combined, with
a UX that a new engineer can learn in a day instead of a month.

## Why

Every commercial pipe stress tool is either powerful and hard (Caesar II spreadsheet
input, 40-year learning curve) or easier but capability-limited (CAEPIPE). None are
cloud-native, none offer real-time collaboration, none have modern plugin ecosystems,
and all are expensive ($10K-30K/seat/year).

pypemesh targets the same accuracy and code coverage with:
- A CAD-like 3D modeler that doesn't hide the spreadsheet power user mode
- Cloud-first architecture with local-first data
- Validated solver (Markl fatigue benchmarks, ASME NC-3600 sample cases)
- Open plugin SDK (SolidWorks, AutoCAD, CADWorx, SmartPlant, OpenPlant)
- Release path: open-source core → commercial enterprise tier (see `docs/COMMERCIAL_ROADMAP.md`)

## Scope

See `docs/REQUIREMENTS.md` for the full capability matrix.

**Phase B (open-source MVP, first milestone):**
- 3D beam element FEA solver, linear static
- Non-linear: gaps, friction, one-way restraints
- ASME B31.3 code compliance (static + occasional loads)
- Dynamic: modal + response spectrum
- Web-based 3D modeler (React + Three.js)
- PCF file import
- PDF stress report
- Validation suite against published benchmarks

**Phase C (commercial, later):**
- B31.1, B31.4, B31.8, B31.12, EN 13480 codes
- Nuclear ASME Section III (requires NQA-1 certification)
- Native desktop (Qt/PySide6) alongside web
- CAD vendor native plugins
- AI support optimizer
- Enterprise (SSO, multi-tenant, audit, RBAC)

## Project layout

```
pypemesh/
├── docs/                        # all planning, architecture, ADRs
├── pypemesh-core/               # Python solver library (pip-installable)
├── pypemesh-web/                # React frontend + FastAPI backend
├── pypemesh-desktop/            # future: Qt native app
├── benchmarks/                  # validation test cases
└── examples/                    # sample models for users
```

## Documentation

Start here, in order:

1. `docs/REQUIREMENTS.md` — what we're building
2. `docs/ARCHITECTURE.md` — how it's structured
3. `docs/UX_PRINCIPLES.md` — the power-vs-simplicity design rules
4. `docs/TECH_DECISIONS.md` — why these choices
5. `docs/VALIDATION_PLAN.md` — how we prove correctness
6. `docs/MILESTONES.md` — session-by-session plan
7. `docs/COMMERCIAL_ROADMAP.md` — B→C gates

## Status

Pre-alpha. Planning phase. See `docs/MILESTONES.md` for the current session.

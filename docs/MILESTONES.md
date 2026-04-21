# Milestones

**Version:** 0.2
**Status:** Living — updated every session. Current as of v0.1.0a0 release.

Session-by-session plan for Phase B (open-source MVP).

## Status summary (as of v0.1.0a0)

| Milestone | Status | What shipped |
|---|---|---|
| **M0: Foundation** | ✅ complete | Planning docs, repo, git, Vercel, CI |
| **M1: Solver spine** | ✅ complete | Static linear solver, 29 analytical tests pass, <0.1% accuracy |
| **M2: First code (B31.3)** | ✅ complete | Full B31.3 equations + SIF + B31J tables |
| **M2b: Elbow + extra elements** | ✅ complete | Elbow (Karman flex), Tee, Rigid, Spring |
| **M2c: Second code (B31.1)** | ✅ complete | B31.1 power piping with different allowables |
| **M3: Modeler MVP** | ✅ complete | React + Three.js viewport, 5 samples, code picker |
| **M3a: JSON I/O + API** | ✅ complete | FastAPI /solve, /modes, /report, /validate |
| **M3b: PDF reports** | ✅ complete | ASME-style report via ReportLab |
| **M3c: CLI** | ✅ complete | `pypemesh solve|validate|report|bench|version` |
| **M4a: Modal analysis** | ✅ complete | Eigensolver, 0.02% accuracy vs analytical |
| **M4b: Response spectrum** | ✅ complete | SRSS/CQC/ABS + ASCE-7 built-in spectrum |
| **M4c: Time history** | 🔜 next | Newmark-β direct integration |
| **M4d: Non-linear** | 🔜 | Gaps, friction, unilateral supports |
| **M5: Validation suite** | 🟡 partial | 2 benchmarks; target: 10+ incl. Peng, Markl, Appendix S |
| **M6: B release** | 🟡 partial | USAGE.md done; docs site + more materials still to do |

## Phase B stats as of v0.1.0a0

- **94 tests passing** (93% coverage)
- **2 validation benchmarks passing**
- **18 commits** to main
- **Deployed:** https://pypemesh.vercel.app (frontend) + GitHub source
- **~10,500 lines** of Python + TypeScript + docs
- **Validated accuracy:** PL³/3EI <0.1%, thermal EAαΔT <0.1%, modal <0.02%, SIF exact

## Original 50-session plan (below, for reference)

## Session-by-session (M0 to M6)

### M0: Foundation (sessions 1-3)

**S1** (this session):
- [x] Directory structure created at `/Users/mihirpatel/Downloads/pypemesh`
- [x] Git init on main branch
- [x] README + LICENSE + .gitignore
- [x] All 7 planning docs (REQUIREMENTS, ARCHITECTURE, UX_PRINCIPLES, TECH_DECISIONS, VALIDATION_PLAN, MILESTONES, COMMERCIAL_ROADMAP)
- [ ] Vercel account linked (user action: `/mcp` → claude.ai Vercel)
- [ ] First commit
- [ ] GitHub repo created, push main

**S2**:
- Scaffold `pypemesh-core`: pyproject.toml, src layout, entry points, stubs for solver/codes/materials/io/validation
- Scaffold `pypemesh-web/frontend`: Vite + React + TS + Three.js + Zustand
- Scaffold `pypemesh-web/backend`: FastAPI + Pydantic + basic health route
- Local dev harness: `docker-compose.yml` with Postgres + Redis
- Landing page (simple): "pypemesh — open-source pipe stress, coming"
- Deploy landing page to Vercel

**S3**:
- GitHub Actions CI: Python lint+test matrix, Node lint+test matrix
- Pre-commit hooks: ruff, mypy, prettier, eslint
- First analytical unit tests: cantilever tip deflection, thermal growth
- Code coverage reporting to Codecov
- `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`

### M1: Solver spine (sessions 4-10)

**S4**: `solver/model.py` — Node, Element, Material, Section, Restraint dataclasses
**S5**: `solver/elements/beam.py` — 3D beam stiffness matrix, unit tested against analytical
**S6**: `solver/assembly.py` — global K assembly from element K's, sparse COO → CSR
**S7**: `solver/static.py` — apply restraints, solve Kd=F, recover reactions
**S8**: Thermal + pressure load vectors
**S9**: Stress recovery: bending moments, axial, torsion at element ends
**S10**: End-to-end: solve a 5-node model (cantilever with thermal), compare to hand calc

Gate: Layer 1 tests all pass. Layer 2 stiffness symmetry/invariance tests pass.

### M2: First benchmark (sessions 11-15)

**S11**: `codes/base.py` + `codes/b31_3.py` skeleton
**S12**: B31.3 equation 17 (expansion stress), equation 23a (sustained)
**S13**: SIF table (B31J), flexibility factors (Appendix D)
**S14**: `codes/b31_3.py` complete: all stress categories, allowable calc
**S15**: Run Appendix S model, fix deltas until within 1%

Gate: Appendix S passes.

### M3: Modeler MVP (sessions 16-25)

**S16**: Frontend: Three.js scene, camera controls, grid
**S17**: Model tree panel + property editor (node/element CRUD via UI)
**S18**: FastAPI routes: projects CRUD, solve job
**S19**: `io/project.py` JSON schema + round-trip test
**S20**: "Run Analysis" button → backend solve → frontend result overlay
**S21**: Results visualization: stress coloring on elements, deformed shape
**S22**: Undo/redo system (immer patches)
**S23**: Spreadsheet editor (second input mode)
**S24**: Keyboard shortcuts + command palette
**S25**: End-to-end polish: 10-node model demo

Gate: Usability test with 1 engineer, 10-minute first-model test passes.

### M4: Non-linear + dynamic (sessions 26-35)

**S26**: `solver/nonlinear.py` — Newton-Raphson skeleton
**S27**: Gap support element + tangent stiffness
**S28**: Coulomb friction element + tangent stiffness
**S29**: Convergence diagnostics + failure UX
**S30**: `solver/dynamic.py` — consistent mass matrix
**S31**: Eigenvalue solver (`scipy.sparse.linalg.eigsh`)
**S32**: Mode shape visualization in frontend
**S33**: Response spectrum: SRSS, CQC combinations
**S34**: Rayleigh damping
**S35**: Dynamic benchmarks vs analytical + Peng ch7

Gate: Layer 1 dynamic tests pass. Peng Ch 7 non-linear within 5%.

### M5: Validation suite (sessions 36-45)

**S36**: `benchmarks/` directory + runner script
**S37**: Encode Appendix S as benchmark (#1)
**S38**: Encode NC-3600 sample (#2)
**S39**: Encode Markl fatigue (#3)
**S40**: Encode 5 Peng textbook problems (#4-#8)
**S41**: Acquire Caesar II trial, build reference models #1-5
**S42**: Reference models #6-10 (loops with restraints)
**S43**: Reference models #11-15 (branched)
**S44**: Reference models #16-20 (mixed/non-linear)
**S45**: Validation report generator (HTML + JSON + CSV)

Gate: All benchmarks pass within tolerance. Validation report published.

### M6: B release (sessions 46-50)

**S46**: Documentation site (Docusaurus or similar)
**S47**: Example projects: "Simple thermal loop", "Pump discharge", "Relief header"
**S48**: PDF report generator polish
**S49**: PCF file import
**S50**: v0.1.0 tag, GitHub release, public announcement

Gate: Public announcement.

---

## What happens after M6

Phase B.1, B.2, then C. Roadmap in `COMMERCIAL_ROADMAP.md`.

Key metric to track: **time-to-first-model** for a new engineer (target: <10 min).
If this slips, stop adding features and fix UX.

---

## Current session status

**We are in S1.**

Completed this session:
- [x] Folder tree
- [x] Git init (main branch)
- [x] README, LICENSE, .gitignore
- [x] REQUIREMENTS.md
- [x] ARCHITECTURE.md
- [x] UX_PRINCIPLES.md
- [x] TECH_DECISIONS.md
- [x] VALIDATION_PLAN.md
- [x] MILESTONES.md (this file)
- [ ] COMMERCIAL_ROADMAP.md (in progress)
- [ ] First commit
- [ ] GitHub repo + push
- [ ] Vercel link

Blocked pending user action:
- Vercel MCP auth: user runs `/mcp` and selects "claude.ai Vercel"

Next session (S2): scaffold core + frontend + backend + local dev harness.

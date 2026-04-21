# Changelog

All notable changes to pypemesh. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning: [SemVer](https://semver.org/).

## [Unreleased]

### Added
- **Modal analysis** (M4a): eigensolver via SciPy Lanczos, /modes endpoint,
  frontend mode-frequency display. Validated to 0.02% vs analytical
  cantilever first-mode formula.
- **CLI runner**: pypemesh solve / validate / report / bench / version
- **Material library**: 11 curated materials (A106-B, A53-B, A333-6, TP304,
  TP316L, TP321, P11, P22, P91, X65, HDPE PE100) with temp-dependent
  properties from open data
- **PDF report generator** (M3b): ASME-style report with cover, summary,
  stress table, restraint reactions, disclaimer. ReportLab-backed.
- **Frontend modeler** (M3): React + Three.js viewport, sidebar with model
  tree + properties + results table, sample-project picker (4 demos),
  modal analysis button, PDF download button
- **FastAPI backend**: /solve, /modes, /report, /validate endpoints with
  Pydantic models, CORS for Vercel + localhost
- **Validation harness** (M5a): benchmark runner with model.json /
  expected.json / tolerance.yaml convention, gates CI
- **Project JSON I/O** (M3a): versioned schema, round-trip exact preservation
- **Elbow element** (M2b): Karman flexibility EI/k, arc-length based
  stiffness, validated against Markl SIF tables
- **B31.3 implementation** (M2): full equations 23a (sustained), 23b
  (occasional), 17 (expansion), with B31J SIF lookup, liberal allowable,
  occasional load factors
- **3D beam FEA solver** (M1): 12×12 stiffness from Hermite shape functions,
  static linear solve via SciPy sparse, thermal/pressure load vectors,
  consistent mass matrix, stress recovery
- Theory docs (NASA-grade): BEAM_THEORY, PIPE_MECHANICS, STRESS_CATEGORIES,
  CODE_B31_3, SIF_MARKL, DYNAMIC_ANALYSIS, SOLVER_NUMERICS
- Comprehensive software landscape doc (50+ tools surveyed) and capability
  matrix (every capability mapped to a phase)
- Initial repository structure
- Planning docs: REQUIREMENTS, ARCHITECTURE, UX_PRINCIPLES, TECH_DECISIONS,
  VALIDATION_PLAN, MILESTONES, COMMERCIAL_ROADMAP
- `pypemesh-core` Python package skeleton (solver data model, codes base, entry points)
- `pypemesh-web/frontend` Vite + React + TypeScript + Three.js landing page
- `pypemesh-web/backend` FastAPI skeleton with health endpoint
- Docker-compose for local Postgres + Redis + backend
- MIT license with engineering disclaimer

### Validated
- Cantilever tip deflection PL³/(3EI) — within 0.1% of analytical
- Cantilever tip rotation ML/(EI) — within 0.1%
- Constrained thermal force EAαΔT — within 0.1%
- Free thermal growth αLΔT — within 0.1%
- Modal first-mode frequency for cantilever — within 0.02%
- B31.3 PD/4t pressure stress (50 bar / 6" SCH 40 → 29.6 MPa) — exact
- B31.3 sustained ratio benchmark — within 0.5%
- Elbow flexibility k = 1.65/h, SIF = 0.9/h^(2/3) per Markl — exact

### Stats
- 78 tests passing in pypemesh-core (92% coverage)
- 9 tests passing in pypemesh-web/backend
- ~7,800 lines of code
- 12 commits

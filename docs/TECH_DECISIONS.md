# Technical Decisions (ADRs)

Architectural decision records. Each entry: context, decision, consequences.
Format borrowed from Michael Nygard's ADR template.

---

## ADR-001: Language choice — Python for core

**Context:** Need fast dev velocity, massive scientific ecosystem (NumPy, SciPy,
sparse solvers, eigenvalue libraries), easy ML integration, readable by domain
engineers.

**Alternatives considered:**
- **Julia**: better raw performance, but smaller library ecosystem, hiring pool, deployment story is rougher
- **C++**: 10-100x faster, but 5-10x dev time, steep onboarding
- **Rust**: memory-safe fast, but immature scientific ecosystem for FEA
- **Fortran**: classic FEA, but nobody wants to maintain it

**Decision:** **Python 3.11+** for core, with NumPy/SciPy for numerics. Drop
to Cython/Rust only at measured bottlenecks.

**Consequences:**
- (+) Huge hiring pool, readable code, excellent scientific libs
- (+) FastAPI, Pydantic, SQLAlchemy for the web tier — same language end-to-end
- (+) ML integration trivial (phase C AI support optimizer)
- (−) Slower than C++. Acceptable trade: 500-node model solves in <5s with SciPy sparse; large-model path optimized later with PETSc/Trilinos bindings
- (−) GIL means parallelism via multiprocessing. OK for batch; not a blocker for solver

---

## ADR-002: Frontend stack — React + TypeScript + Vite

**Context:** Need modern component reactivity, mature ecosystem for 3D (Three.js),
TypeScript for safety on a complex state model.

**Alternatives:**
- **Vue**: smaller, simpler, but smaller Three.js ecosystem
- **Svelte**: fastest runtime, but smaller hiring pool, less mature for large apps
- **Solid**: fine-grained reactivity (great for modeler), but immature

**Decision:** **React 18 + TypeScript (strict) + Vite**. State via Zustand
(lightweight, no Provider hell). Undo via Immer patches.

**Consequences:**
- (+) React Three Fiber for Three.js integration
- (+) Vite for fast dev cycles
- (+) Huge talent pool, huge library pool
- (−) React's re-render story needs care on a 2000-node canvas — solved by rendering 3D outside React tree (R3F handles this)

---

## ADR-003: 3D rendering — Three.js (via react-three-fiber)

**Context:** Need WebGL 3D viewport with pan/zoom/orbit, efficient on 2000+ nodes,
picking/selection, overlays.

**Alternatives:**
- **Raw WebGL**: flexible, but massive amount of boilerplate
- **Babylon.js**: full game engine, overkill, larger bundle
- **Deck.gl**: geospatial focus, wrong primitives
- **Three.js**: industry standard for browser 3D

**Decision:** **Three.js via `@react-three/fiber`**. Add `@react-three/drei`
for controls/helpers. Custom shaders for stress coloring.

**Consequences:**
- (+) Mature, huge community
- (+) R3F makes React + Three.js ergonomic
- (−) Need careful instancing for large models — InstancedMesh for pipes, BufferGeometry for connections

---

## ADR-004: Backend framework — FastAPI

**Context:** Need async Python web framework, automatic OpenAPI generation,
Pydantic validation, WebSocket support.

**Alternatives:** Flask (sync, older), Django (ORM-heavy, overkill), Starlette (FastAPI's base).

**Decision:** **FastAPI** with Pydantic v2 models.

**Consequences:**
- (+) Auto-generated OpenAPI → typed frontend client via `openapi-typescript`
- (+) Pydantic enforces input validation at API boundary
- (+) Async support for streaming long solves
- (+) Easy to wire Celery/RQ for background jobs

---

## ADR-005: Database — PostgreSQL + JSONB

**Context:** Projects are deeply nested. Relational queries needed for
user/org/permission. Want one store for both.

**Alternatives:**
- **MongoDB**: fine for JSON but weak for relational
- **SQLite**: great for desktop, not cloud
- **Two DBs**: rejected — complexity, consistency hell

**Decision:** **PostgreSQL** with JSONB for project payloads, relational for
auth/org. SQLite fallback for offline/desktop mode (same SQL subset).

**Consequences:**
- (+) JSONB indexing for project queries
- (+) Full-text search on project content
- (+) Well-understood scaling story
- (−) Requires schema versioning discipline for JSONB migrations

---

## ADR-006: Hosting — Vercel (frontend) + Railway or Fly (backend)

**Context:** User requested Vercel. Vercel's Python runtime is serverless with
cold-start latency and execution time limits incompatible with a scientific
solver that may run 5-30s per job.

**Decision:** **Vercel** for React frontend (static + edge CDN). **Railway**
(primary) or **Fly.io** (fallback) for FastAPI backend + Celery/RQ workers.
Postgres via Supabase or Railway managed.

**Consequences:**
- (+) Frontend gets Vercel's edge network, fast global delivery
- (+) Backend runs as real long-lived processes
- (−) Two deploy targets to manage. Mitigated with `docker-compose` for local dev and GitHub Actions unified pipeline.

---

## ADR-007: Job queue — RQ (Redis Queue) initially

**Context:** Solver jobs are CPU-heavy, 1-30s typical. Need background processing.

**Alternatives:** Celery (more features, more ops burden), Arq (async-native).

**Decision:** **RQ** for simplicity in phase B. Revisit Celery/Arq if needed at scale.

**Consequences:**
- (+) Minimal ops
- (+) Redis already needed for caching + pub/sub
- (−) Less feature-rich than Celery; fine for our scope

---

## ADR-008: Solver — SciPy sparse, PETSc later

**Context:** Pipe stress models: typically 50-2000 nodes, 300-12000 DOF.
Matrices are sparse, banded.

**Decision:** **SciPy sparse** (CSR + `spsolve` via SuperLU for direct, `cg`
for iterative) for phase B. Interface abstracted so we can swap in PETSc or
MKL PARDISO for phase C when dealing with 50K+ DOF.

**Consequences:**
- (+) Zero install friction (SciPy is a wheel install)
- (+) Covers phase B scope easily
- (−) At 10K+ DOF SuperLU slows; PETSc binding adds ops complexity when we get there

---

## ADR-009: Material data — open-data B phase, licensed C phase

**Context:** ASME Section II Part D is the gold standard material reference.
It's copyrighted. Shipping it in OSS = legal risk.

**Decision:** Phase B ships a **curated open dataset** (API handbooks, EN
public tables, published research). Phase C licenses Section II Part D from
ASME and ships it encrypted with license verification.

**Consequences:**
- (+) Clean OSS release
- (−) B-phase material count is ~50 vs commercial 20000. Adequate for MVP.
- (→) Architecture must support pluggable material DBs from day 1

---

## ADR-010: Testing — pytest + Hypothesis + benchmark regressions

**Context:** Solver correctness is not optional. Engineers will not trust a
tool that isn't validated.

**Decision:**
- **pytest** for unit + integration
- **Hypothesis** for property-based (solver symmetry, invariance under rotation, energy conservation)
- **pytest-benchmark** for perf regression
- **Dedicated `benchmarks/` suite** for ASME/NC-3600/Markl validation, run every PR

**Consequences:**
- CI runs full benchmark suite on every push to main. PR fails if any
  benchmark drifts >1%.
- Every code equation needs a test against a textbook value before merge.

---

## ADR-011: Version control — Git, GitHub, conventional commits

**Context:** Standard industry practice. Need audit trail for commercial buyers.

**Decision:** **GitHub** public repo (MIT), **Conventional Commits**
(`feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `perf:`, `chore:`), signed
commits (GPG or Sigstore), main-branch protected with required CI + review.

**Consequences:**
- (+) Clean changelog generation (automated)
- (+) Semantic versioning from commit stream
- (+) Auditable history satisfies enterprise procurement

---

## ADR-012: Units — SI internal, user-configurable display

**Context:** US customary vs metric is the most common data-entry error in
pipe stress (Caesar II famously does not auto-convert).

**Decision:** **All internal math in SI**. UI has a unit system toggle that
converts on display and input. Project file stores SI with explicit units
metadata. Units never implicit.

**Consequences:**
- (+) Zero unit-confusion bugs in the solver
- (+) International users get native units without data corruption
- (−) Conversion round-trips have tiny float error — tolerable at display

---

## ADR-013: License — MIT for core

**Context:** Need commercial OK (MIT/Apache) not copyleft (GPL). Want
maximum adoption. Want to sell proprietary extensions later.

**Alternatives:**
- Apache 2 (patent grant is nice but adds complexity)
- BSL (Business Source License — delayed OSS) — option if we change our mind

**Decision:** **MIT** for pypemesh-core and open UI. Commercial extensions
ship under a proprietary EULA as separate packages.

---

## ADR-014: Python project layout — src/

**Context:** Flat layout causes subtle import shadowing. src/ layout is
2023+ Python community consensus.

**Decision:** `pypemesh-core/src/pypemesh_core/...`. Installs fail if
package isn't properly built — surfaces bugs early.

---

## ADR-015: Commercial IP separation

**Context:** To sell commercial extensions later, we need clean IP boundaries
from day 1. Retroactive separation is painful.

**Decision:**
- `pypemesh-core`: MIT, public, no proprietary code ever
- `pypemesh-pro`: proprietary (future repo), imports core via entry points
- `pypemesh-nuclear`: proprietary, separate repo, separate QA audit trail
- Contributor License Agreement (CLA) for core — so we retain rights to relicense if needed (mitigation: dual MIT/CLA)

**Consequences:**
- Every contributor to core signs a CLA before first PR merges
- All commercial code lives outside the public repo, even during dev

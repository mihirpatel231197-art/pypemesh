# Requirements

**Version:** 0.1 (living document)
**Status:** Planning

Defines *what* pypemesh does. See `ARCHITECTURE.md` for *how*.

## Product mission

Match the combined capability of Caesar II + AutoPIPE + CAEPIPE + FEPipe with
a UX that a new engineer learns in a day instead of a month, deployed as a
cloud-first web app with an optional desktop build.

## Phasing

| Phase | Name | Scope | Commercial status |
|---|---|---|---|
| **B** | Open-source MVP | Single-code (B31.3), static + basic dynamic, web modeler | Free, MIT |
| **B.1** | Community release | Non-linear, multi-code (B31.1, B31.4), PCF import, reporting | Free, MIT |
| **B.2** | Plus | AI support optimizer, local FEA module, CAD plugins (OSS tier) | Free, MIT |
| **C** | Commercial | Nuclear, enterprise, native desktop, licensed materials, support | Paid, proprietary extensions |

The B phases ship publicly. C is a separate licensed product that *consumes*
the OSS core the same way anyone else would — no secret core.

---

## Phase B functional requirements (the MVP)

### B-F1: Solver — static linear analysis

- 3D beam elements with 6 DOF per node (translations + rotations)
- Element types: straight pipe, curved pipe (elbow with Karman flexibility), rigid, expansion joint, reducer, tee (as junction + local SIF)
- Stiffness matrix assembly via sparse matrices (SciPy CSR)
- Solver: direct sparse (SciPy SuperLU) for <10K DOF, iterative (CG with ILU preconditioner) for larger
- Load cases: weight (W), thermal expansion (T1..T9), pressure (P1..P9), wind (WIN1..WIN3), seismic (U1..U3)
- Displacements imposed at anchors/restraints (6 DOF configurable)

**Acceptance:** reproduce results of ASME NC-3600 sample problem within 2% of published values.

### B-F2: Solver — non-linear

- Gap-type supports (one-way, unilateral contact)
- Coulomb friction at rest/guide supports
- Large-displacement effects (stretch goal; can ship without)
- Newton-Raphson iteration with convergence tolerance configurable
- Convergence failure must produce diagnostic output (which node, which iteration, which residual)

**Acceptance:** match Caesar II textbook non-linear problem (Peng/Peng, "Pipe Stress Engineering", Chapter 7 sample) within 5%.

### B-F3: Solver — dynamic (modal + response spectrum)

- Consistent mass matrix
- Eigenvalue solver for first N modes (user-configurable, default 20)
- Rayleigh damping
- Response spectrum analysis with SRSS, CQC, and ABS combination methods
- Time history (stretch goal for B.1)

**Acceptance:** match published modal frequencies for a simple 3-elbow piping loop (ASME Appendix N sample) within 3%.

### B-F4: Code compliance — ASME B31.3 (Process Piping)

Full implementation of:
- Sustained stress (equation 23a): `SL = PD/4t + 0.75i·Ma/Z`
- Occasional stress (equation 23b)
- Displacement stress range (equation 17): `SE = sqrt(Sb² + 4St²)`, `Sb = iMb/Z`, `St = Mt/2Z`
- Allowable calculation per Table A-1 material properties
- Liberal allowable (`1.25(Sc+Sh) - SL`)
- SIF (Stress Intensification Factors) per ASME B31J (2017+)
- Flexibility factors per B31.3 Appendix D

**Acceptance:** per-node stress ratios match Caesar II within 1% on the official B31.3 Appendix S sample problem.

### B-F5: Material database

- Minimum 50 materials at launch, covering CS (A106 Gr.B, A53), SS (A312 TP304, TP316, TP321), Alloy (A335 P11, P22, P91), LTCS (A333 Gr.6)
- Temperature-dependent: E (modulus), α (thermal expansion), Sh (hot allowable), Sc (cold allowable), ρ (density), ν (Poisson)
- Data source: ASME Section II Part D — BUT Part D is copyrighted. B phase ships with **open-data substitutes** (published research, API handbooks, DIN public tables). Commercial C tier licenses Part D.
- User-editable custom materials with validation

### B-F6: Component library (fittings)

- Straight pipe: all ASME B36.10/B36.19 schedules
- Elbows: SR, LR, 3D, 5D per ASME B16.9
- Tees: welding, sockolet, weldolet, reducing
- Reducers: concentric, eccentric
- Flanges: class 150/300/600/900/1500/2500 per ASME B16.5
- Valves: gate, globe, check, ball, butterfly (as rigid or spring-backed)
- Supports: anchor, resting, guide, spring hanger (variable/constant), snubber
- User-defined custom components

### B-F7: 3D modeler (web)

- Three.js-based viewport with orbit/pan/zoom
- Dual input modes:
  - **Graphical**: point-and-click route building, snap-to-grid, ortho lock
  - **Spreadsheet**: Caesar-style tabular editing (power-user mode)
- Node tree + property panel (AutoPIPE-style)
- Multi-select, copy/paste, rotate, mirror, array
- **Infinite undo/redo** (non-negotiable — Caesar II's biggest UX flaw)
- Auto-routing: drag pipe end to a node, auto-generate elbow + straight
- Snap axes, grid, angles (15/30/45/90)

### B-F8: Import/Export

- PCF (Piping Component File) — industry-standard ASCII format, open spec
- Native JSON project format (versioned schema)
- STEP (read-only, as reference geometry — stretch goal)
- Export: PDF report, isometric PNG, CSV stress table

### B-F9: Reporting

- Single-click PDF generation
- ASME-compliant report structure:
  - Cover page (project metadata, engineer stamp placeholder)
  - Model summary (nodes, elements, materials)
  - Load cases
  - Per-node stress table (sustained/occasional/expansion/ratio/status)
  - Restraint loads table
  - Failed nodes highlighted
- Customizable templates (company logo, disclaimer text)

### B-F10: Validation suite

- Automated test harness running every commit
- Benchmarks required before B ships:
  1. ASME B31.3 Appendix S sample
  2. NC-3600 sample problem
  3. Markl fatigue test data (for SIF verification)
  4. Peng textbook Chapter 5/7 worked examples (4 cases)
  5. PSVP (Pipe Stress Verification Problems) — NIST benchmarks
- CI fails if any regression >1% on accuracy-critical tests

---

## Phase B non-functional requirements

### B-NF1: Performance

- Solver: <5s for a 500-node static linear model on consumer hardware
- Modeler: 60fps pan/zoom on a 2000-node model
- First-paint: <2s for loaded project in browser
- Save: <500ms for any model up to 10K nodes

### B-NF2: Accuracy

- Static: within 1% of Caesar II on B31.3 benchmark
- Dynamic: within 3% on modal frequencies
- Non-linear: within 5% on gap/friction problems
- No silent inaccuracy — if solver can't converge, fail loudly

### B-NF3: Platform

- Web: evergreen Chrome, Edge, Firefox, Safari (no IE)
- Mobile: responsive for viewing only (no modeling on phone)
- Desktop: Electron wrapper shipping same day as web for offline users
- Python core: 3.11+, Linux/macOS/Windows

### B-NF4: UX — see `UX_PRINCIPLES.md` for full spec

Key non-negotiables:
- **Time-to-first-model < 10 minutes** for an engineer familiar with Caesar II
- **No modal dialogs** for normal workflow (inline editing instead)
- **Undo everything**, always
- **Keyboard-first** for power users (every action has a shortcut)
- **Progressive disclosure**: simple by default, advanced on demand

### B-NF5: Quality

- 80%+ test coverage on solver
- Every code equation has a unit test against a textbook value
- Property-based tests (Hypothesis) for symmetry/invariance checks
- Type-checked (mypy strict) for Python, TypeScript strict for frontend
- Every solver run logs structured events for replay/debugging

### B-NF6: Data integrity

- Autosave every 30s to local storage
- Versioned project JSON with migration on format bumps
- Optimistic locking for cloud projects
- Never silently corrupt — refuse to save on schema validation failure

---

## Phase C commercial-only scope (the *extensions*, not the core)

Everything in B stays open. C adds:

- **Codes**: B31.1, B31.4, B31.5, B31.8, B31.9, B31.12, EN 13480, BS 806, ISO 15649, DNV, NORSOK, API 617/650, Nuclear ASME Section III Class 1/2/3, JSME (Japan)
- **Licensed materials**: full ASME Section II Part D data (requires ASME license)
- **CAD native plugins**: SolidWorks, AutoCAD, CATIA, MicroStation, SmartPlant, CADWorx — each an enterprise partner integration
- **AI support optimizer**: ML model trained on curated support configurations
- **Local FEA module**: FEPipe-equivalent shell/brick element for nozzles, tees
- **Nuclear tier**: NQA-1 validated, stratification, fatigue, thermal shock
- **Enterprise**: SSO (SAML/OIDC), RBAC, audit log, multi-tenant, data residency
- **White-label**: private deployment, custom branding
- **SLA + support**: 4-hour response, on-site engineering assistance

See `COMMERCIAL_ROADMAP.md` for how we gate each C feature.

---

## Explicitly out of scope (always)

- **Process simulation** (HYSYS/Aspen territory) — we consume their T/P, we don't compute it
- **Fluid hydraulic analysis** (PIPENET territory) — we ingest force-time curves, we don't solve transient flow
- **Vessel design** (PV Elite territory) — we reference vessel flexibility, we don't design the vessel
- **CAD authoring** (SolidWorks, AutoCAD) — we plug into CAD, we don't replace it
- **Isometric drawing production** (ISOGEN) — we export basic iso views; full iso is v3.0

Attempting any of these expands scope beyond viability.

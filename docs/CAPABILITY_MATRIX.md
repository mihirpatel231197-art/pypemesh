# Capability Matrix

**Version:** 0.1
**Status:** Binding — maps every capability from every tool surveyed in
`SOFTWARE_LANDSCAPE.md` to a specific pypemesh phase and requirement.

> If `SOFTWARE_LANDSCAPE.md` asks *what exists*, this doc asks *what we absorb,
> when, and why*.

## Legend

- **✓** — full native support in pypemesh
- **◑** — partial / planned
- **✗** — explicitly out of scope (see rationale column)
- **∅** — integration point (consume, not re-implement)

---

## A. Pipe Stress Solver Capabilities

| Capability | Source tools | B | B.1 | B.2 | C | Our approach |
|---|---|---|---|---|---|---|
| 3D beam element (Euler-Bernoulli) | all | ✓ | | | | 12×12 stiffness, 6 DOF/node |
| Timoshenko shear correction | Caesar II, AutoPIPE | | ◑ | ✓ | | Selected switch; minor at pipe L/D |
| Curved pipe (elbow) Karman flexibility | all | ✓ | | | | B31.3 Appendix D |
| Tee element with junction SIF | all | ✓ | | | | B31J 2017 table lookup |
| Reducer element | all | ✓ | | | | B31.3 §319 |
| Rigid element (master-slave DOF) | all | ✓ | | | | constraint equations |
| Expansion joint | Caesar II, AutoPIPE | | ✓ | | | bellows spring rates |
| Dummy leg / trunnion | START-PROF | | ✓ | | | rigid offset + beam |
| Static linear solve | all | ✓ | | | | sparse direct (SuperLU) |
| **Load sequencing solver** | **AutoPIPE** | | ✓ | | | path-dependent non-linear |
| Load vector superposition | Caesar II | ✓ | | | | legacy compatibility mode |
| Non-linear: gaps | Caesar II, AutoPIPE | | ✓ | | | bilinear spring |
| Non-linear: friction | Caesar II, AutoPIPE | | ✓ | | | Coulomb, iterative |
| Non-linear: large displacement | ANSYS territory | | | ◑ | ✓ | updated Lagrangian; opt-in |
| Buried pipe / soil springs | START-PROF, Caesar | | | ✓ | | API 1102, PRCI |
| District heating pre-insulated | START-PROF, ROHR2 | | | | ✓ | bonded friction model |
| Subsea / offshore | Caesar II, DNV tools | | | | ✓ | DNV-OS-F101 |
| Dynamic: modal eigensolve | all | ✓ | | | | scipy.sparse.linalg.eigsh |
| Dynamic: response spectrum (SRSS/CQC/ABS) | all | | ✓ | | | NRC RG 1.92 |
| Dynamic: time history (Newmark-β) | Caesar II, AutoPIPE | | ✓ | | | implicit integration |
| Dynamic: harmonic | Caesar II, AutoPIPE | | | ✓ | | complex response |
| Dynamic: water hammer force-time | PIPENET-fed | | ✓ | | | force-time consumption |
| Rayleigh damping | Caesar II, AutoPIPE | | ✓ | | | α, β sliders |
| Spectrum library (UBC/ASCE/IBC/RG1.60) | Caesar II | | ✓ | | | curated first 10 specs |
| Spring hanger sizing (variable/constant) | all | ✓ | | | | Grinnell/Lisega algorithms |
| Flange leakage (Kellogg) | Caesar II, AutoPIPE | | ✓ | | | Kellogg eq |
| Flange ASME Appendix 2 | PV Elite | | | ✓ | | UG-44 bolted |
| WRC-107/297/537 local stress | Caesar II, FEPipe | | | ✓ | | closed-form + NPTEL tables |
| Local shell/brick FEA | FEPipe, NozzlePRO | | | ✓ | | auto-mesh templates |
| Fatigue (Markl fatigue curves) | Caesar II, ASME | | ✓ | | | B31J per SIF |
| Fatigue (ASME VIII Div 2 Part 5) | PV Elite, Compress | | | ✓ | | elastic-plastic |

---

## B. Code Compliance

| Code | Source tools | B | B.1 | B.2 | C | Notes |
|---|---|---|---|---|---|---|
| ASME B31.3 (Process) | all | ✓ | | | | MVP priority |
| ASME B31.1 (Power) | Caesar II, AutoPIPE | | ✓ | | | high-volume code |
| ASME B31.4 (Liquid Pipelines) | Caesar II, START-PROF | | ✓ | | | pipeline focus |
| ASME B31.5 (Refrigeration) | Caesar II, AutoPIPE | | | ✓ | | smaller market |
| ASME B31.8 (Gas Pipelines) | Caesar II, START-PROF | | | ✓ | | large pipeline market |
| ASME B31.9 (Building Services) | Caesar II | | | | ◑ | low priority |
| ASME B31.11 (Slurry) | Caesar II | | | | ◑ | niche |
| ASME B31.12 (Hydrogen) | Caesar II, AutoPIPE | | | ✓ | | emerging market |
| ASME Section III Class 1 | AutoPIPE Nuclear, Caesar Advanced | | | | ✓ | NQA-1 required |
| ASME Section III Class 2/3 | AutoPIPE Nuclear, Caesar Advanced | | | | ✓ | NQA-1 required |
| EN 13480 (European Metallic) | AutoPIPE, ROHR2 | | | ✓ | | Europe entry |
| BS 806 | Caesar II, ROHR2 | | | ✓ | | UK industrial |
| ISO 15649 | Caesar II | | | ✓ | | international |
| DNV-OS-F101 (Offshore) | Caesar II | | | | ✓ | offshore pipelines |
| NORSOK L-002 | Caesar II | | | | ✓ | Norway |
| API 617 (Machinery) | Caesar II | | | | ✓ | compressor connections |
| API 650 (Tanks) | PV Elite, Caesar | | | | ✗ | tank design out of scope |
| CSA Z662 (Canadian Pipeline) | Caesar II, START-PROF | | | | ✓ | Canada |
| KTA (German Nuclear) | ROHR2 | | | | ✓ | German nuclear |
| JSME PPC (Japan) | Caesar II, AutoPIPE Nuclear | | | | ✓ | Japan nuclear |
| GOST R (Russia) | START-PROF | | | | ◑ | Russia market |
| GB 50316 (China) | CAEPIPE, local vendors | | | | ✓ | China industrial |
| HDPE / Plastic (B31.3 Ch. VII) | AutoPIPE, CAEPIPE | | ✓ | | | water utility |
| FRP (B31.3 Ch. VII) | AutoPIPE | | | ✓ | | chemical process |

**Prioritization principle:** every code ships with validation benchmarks
from published sample problems before customers see it. No code ships
without a test that proves correctness.

---

## C. Materials

| Data | Source | B | B.1 | B.2 | C | Notes |
|---|---|---|---|---|---|---|
| Common CS (A106-B, A53, A333-6) | open sources | ✓ | | | | ~10 materials |
| Common SS (A312 TP304/316L/321) | open sources | ✓ | | | | ~10 materials |
| Common alloys (A335 P11/P22/P91) | open sources | ✓ | | | | ~10 materials |
| Full ASME Section II Part D | licensed from ASME | | | | ✓ | ~15,000 entries |
| API 5L pipeline grades | open | | ✓ | | | X42-X100 |
| EN material tables (EN 10216) | open/licensed | | | ✓ | | European |
| DIN material tables | open/licensed | | | ✓ | | German |
| GOST tables | open | | | | ◑ | Russia |
| Plastic (HDPE PE100, PVC, PVDF, PP) | ASTM public | | ✓ | | | water/chem |
| FRP / GRE | manufacturer data | | | ✓ | | chemical |
| Creep (time-dependent E, α at high T) | Larson-Miller, ASME | | | ✓ | | high temp |
| Hydrogen embrittlement factors | ASME B31.12 | | | ✓ | | H2 service |

---

## D. Components / Fittings

| Library | Source | B | B.1 | B.2 | C | Notes |
|---|---|---|---|---|---|---|
| ASME B16.9 welding fittings | all | ✓ | | | | elbows, tees, reducers, caps |
| ASME B16.11 socket/threaded | all | | ✓ | | | small-bore |
| ASME B16.28 long-radius elbows | all | ✓ | | | | LR 1.5D, 3D, 5D |
| ASME B16.5 flanges (Class 150-2500) | all | ✓ | | | | standard flanges |
| ASME B16.47 large flanges | all | | ✓ | | | >24" |
| ASME B36.10 pipe dimensions | all | ✓ | | | | SCH 40, STD, etc. |
| ASME B36.19 stainless dimensions | all | ✓ | | | | thin-wall SS |
| EN pipe dimensions (ISO 3183) | CAEPIPE, ROHR2 | | | ✓ | | European |
| JIS (Japan) dimensions | Caesar II | | | ✓ | | Japan |
| Valve weight library | all | | ✓ | | | common valve weights |
| Vendor catalogs (LISEGA, Bergen, Anvil) | catalog imports | | | ✓ | | support hardware |
| Expansion joint vendor catalogs | Caesar II | | ✓ | | | bellows |
| Spring hanger catalogs | all | ✓ | | | | Grinnell, LISEGA |
| User-defined custom components | all | ✓ | | | | always |

---

## E. Input / Output

| Capability | Source | B | B.1 | B.2 | C | Notes |
|---|---|---|---|---|---|---|
| Graphical 3D modeler | CAEPIPE, AutoPIPE | ✓ | | | | CAD-like input |
| Spreadsheet tabular input | Caesar II | ✓ | | | | power-user mode |
| Infinite undo/redo persistent | AutoPIPE | ✓ | | | | CaesarII's biggest flaw fixed |
| Keyboard shortcuts + command palette | modern IDEs | ✓ | | | | VSCode-style |
| PCF file import | CADWorx, SmartPlant | ✓ | | | | industry standard |
| PCF file export | CADWorx, SmartPlant | | ✓ | | | round-trip |
| AutoCAD DWG/DXF import | all | | ✓ | | | geometry ref |
| Caesar II native file import | Caesar II | | ✓ | | | migration aid |
| AutoPIPE native file import | AutoPIPE | | ✓ | | | migration aid |
| CAEPIPE file import | CAEPIPE | | | ✓ | | migration aid |
| START-PROF file import | START-PROF | | | ✓ | | migration aid |
| SolidWorks plugin (geometry export) | none native | | | ✓ | | big differentiator |
| AutoCAD Plant 3D XML | Plant 3D | | ✓ | | | common format |
| SmartPlant 3D connector | SmartPlant | | | | ✓ | enterprise |
| AVEVA E3D / PDMS connector | AVEVA | | | | ✓ | enterprise |
| OpenPlant / MicroStation | Bentley | | | | ✓ | enterprise |
| CATIA plugin | CATIA | | | | ✓ | aerospace-adjacent |
| IFC (BIM) export | Revit, Tekla | | ✓ | | | coordination |
| STEP read (reference geometry) | all | | ✓ | | | ref geometry |
| HYSYS line list import | HYSYS | | ✓ | | | process boundary |
| UniSim / Aspen Plus line list | Honeywell/AspenTech | | | ✓ | | process boundary |
| PIPENET force-time import | PIPENET | | ✓ | | | transient loads |
| AFT Impulse force-time import | AFT | | | ✓ | | transient loads |
| OLGA slug flow import | SLB | | | | ✓ | subsea |
| ISOGEN export | all | | | ✓ | | deliverables compat |
| Native isometric drawing | none simple | | ✓ | | | basic iso |

---

## F. Analysis Workflow / Productivity

| Feature | Source | B | B.1 | B.2 | C | Notes |
|---|---|---|---|---|---|---|
| Auto-routing (drag to connect) | AutoPIPE | ✓ | | | | user requested |
| Auto-connect (snap to ends) | AutoPIPE | ✓ | | | | "auto-lips" |
| Snap-to-grid / ortho / angles | CAD standard | ✓ | | | | ortho, 15/30/45/90 |
| Multi-select + batch edit | modern | ✓ | | | | property apply |
| Copy/paste/rotate/mirror/array | CAD standard | ✓ | | | | productivity |
| Configurable units (SI / US) | all | ✓ | | | | toggle, never mix |
| AI support optimizer | AutoPIPE Advanced | | | ✓ | | ML on curated set |
| Automated code switching | all | ✓ | | | | change code → re-check |
| Inline error messages | modern | ✓ | | | | UX principle #8 |
| Real-time collaboration | none in class | | | ✓ | | CRDT |
| Version control on projects | none in class | | ✓ | | | git-like |
| Diff view between revisions | none in class | | ✓ | | | audit |
| Review / comment layer | none in class | | | ✓ | | stakeholder sign-off |
| REST API | none in class | | ✓ | | | automation |
| CLI runner (batch mode) | Caesar II has CLI | | ✓ | | | headless |
| Project templates (thermal loop, pump, header) | Caesar II library | | ✓ | | | onboarding |

---

## G. Reporting / Deliverables

| Feature | Source | B | B.1 | B.2 | C | Notes |
|---|---|---|---|---|---|---|
| PDF stress report | all | ✓ | | | | code-compliant layout |
| Customizable report templates | AutoPIPE | | ✓ | | | company logo, format |
| Stress ratio color overlay | AutoPIPE, CAEPIPE | ✓ | | | | 3D model coloring |
| Deformed shape animation | AutoPIPE | ✓ | | | | dynamic modes |
| Mode shape animation | Caesar II, AutoPIPE | | ✓ | | | dynamic |
| Restraint load table | all | ✓ | | | | structural handoff |
| CSV export per node | all | ✓ | | | | automation |
| Material takeoff / BOQ | CADWorx | | ✓ | | | procurement |
| IFC model export | Revit, CADWorx | | ✓ | | | coordination |
| Isometric PDF | ISOGEN | | ✓ | | | deliverables |
| PE-stamp-ready report layout | manual | | | ✓ | | regulatory |
| Validation audit report | none in class | | ✓ | | | regression trace |

---

## H. Enterprise / Commercial (Phase C only)

| Feature | Source | Notes |
|---|---|---|
| SSO (SAML, OIDC) | enterprise standard | required for F500 buyers |
| RBAC (roles) | enterprise standard | admin/engineer/reviewer |
| Audit log | enterprise standard | SOC 2 gate |
| Multi-tenant | SaaS pattern | per-org isolation |
| Self-hosted (Docker/Helm) | customer requirement | air-gapped options |
| Data residency (EU, US, APAC) | customer requirement | regulatory |
| SLA 4-hour response | enterprise standard | paid tier |
| Dedicated support engineer | enterprise standard | paid tier |
| On-site training | enterprise standard | paid tier |
| SOC 2 Type II | enterprise gate | annual audit |
| NQA-1 nuclear | nuclear gate | 12-24 month process |
| E&O insurance | commercial gate | $50-150K/yr |

---

## Putting it together — what's in phase B vs where we go

**Phase B MVP scope (our first ship):**
- Solver: linear static + basic modal
- Code: B31.3
- Materials: ~50 common (open data)
- Components: B16.9, B16.5, B36.10/B36.19
- Input: graphical modeler + spreadsheet, PCF import
- Output: PDF report, CSV, stress overlay
- Non-linear: stretch goal
- Dynamic: modal only (no response spectrum yet)

**Phase B.1 (community release):**
- Codes: B31.1, B31.4
- Solver: non-linear, response spectrum, time history, load sequencing
- Input: Caesar/AutoPIPE import, AutoCAD DWG, HYSYS line list
- Output: customizable templates, mode shape animation
- Workflow: REST API, CLI, templates

**Phase B.2 (plus features, still free):**
- Codes: B31.8, B31.12, EN 13480
- AI support optimizer
- Local FEA module (FEPipe-style templates)
- CAD plugins: AutoCAD Plant 3D, OpenPlant, SolidWorks
- Real-time collaboration
- Fatigue analysis

**Phase C (commercial):**
- Codes: Nuclear Section III, DNV, NORSOK, KTA, JSME, CSA, GB
- Licensed materials (ASME Part D)
- Enterprise connectors: PDMS, E3D, SmartPlant 3D
- SSO/RBAC/audit/multi-tenant
- SOC 2, NQA-1 where applicable
- Support/training SLA

---

## How we refresh this

Every 6 months:
- Re-check vendor websites for new versions/pricing
- Re-check industry forums for new tools
- Interview 3-5 active pipe stress engineers about what they actually use
- Update all ✓ ◑ ✗ states based on actual shipped code

This doc isn't reference — it's a weapon. Use it to say no to scope creep
that doesn't map to a real tool we're replacing.

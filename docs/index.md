# pypemesh

**Open-source pipe stress analysis platform.** Validated ASME B31.3 solver
with a modern 3D web modeler, FastAPI backend, and CLI — all MIT-licensed.

> Live demo: **[pypemesh.vercel.app](https://pypemesh.vercel.app)**
> Code: **[github.com/mihirpatel231197-art/pypemesh](https://github.com/mihirpatel231197-art/pypemesh)**

## What works today

=== "Solver"

    - 3D beam FEA (linear static) — validated to <0.1% on cantilever & thermal
    - Modal analysis — 0.02% accuracy vs analytical first mode
    - Response spectrum (SRSS / CQC / ABS)
    - Time history (Newmark-β)
    - Non-linear gap supports (active-set)
    - 5 element types: pipe, elbow (Karman flexibility), tee, rigid, spring
    - 25 curated materials with temperature-dependent properties

=== "Codes (9 shipping)"

    - ASME **B31.3** Process Piping
    - ASME **B31.1** Power Piping
    - ASME **B31.4** Liquid Pipeline
    - ASME **B31.5** Refrigeration
    - ASME **B31.8** Gas Transmission (4 location classes)
    - ASME **B31.9** Building Services
    - ASME **B31.12** Hydrogen (with Hf derating)
    - **CSA Z662** Canadian Oil & Gas
    - **EN 13480** European Metallic Industrial

=== "Interfaces"

    - **Python API** — `pip install pypemesh-core`
    - **CLI** — `pypemesh solve | report | bench | validate | import-pcf | materials | codes`
    - **FastAPI backend** — `/solve`, `/modes`, `/report`, `/validate`
    - **Web modeler** — React + Three.js with stress overlays, mode animation
    - **PCF file import** — CADWorx / SmartPlant / AutoCAD Plant 3D interop
    - **PDF reports** — ASME-style with cover, stress tables, reactions

## Get started in 30 seconds

```bash
git clone https://github.com/mihirpatel231197-art/pypemesh.git
cd pypemesh/pypemesh-core
pip install -e ".[dev]"
pytest                        # 141 tests, 91% coverage
pypemesh bench                # 3/3 benchmarks pass
pypemesh codes                # list all 9 supported codes
pypemesh materials            # list all 25 materials
```

Or try it live at **[pypemesh.vercel.app](https://pypemesh.vercel.app)**.

## Theory (NASA-grade derivations)

Every piece of physics in pypemesh has a first-principles derivation in
`docs/theory/`. These aren't summaries — they're proper math with citations:

- [Beam Theory](theory/BEAM_THEORY.md) — Euler-Bernoulli & Timoshenko, 12×12 stiffness derivation
- [Pipe Mechanics](theory/PIPE_MECHANICS.md) — Hoop/longitudinal/Bourdon, Karman ovalization
- [Stress Categories](theory/STRESS_CATEGORIES.md) — Primary/secondary/peak per ASME
- [B31.3 Equations](theory/CODE_B31_3.md) — Every equation derived with examples
- [SIF & Markl](theory/SIF_MARKL.md) — 1952 experiments, B31J tables
- [Dynamic Analysis](theory/DYNAMIC_ANALYSIS.md) — Modal, response spectrum, time history
- [Solver Numerics](theory/SOLVER_NUMERICS.md) — Sparse methods, Newton-Raphson, load sequencing

## Stats (as of v0.1.0a0)

| Metric | Value |
|---|---|
| Tests passing | 141 / 141 |
| Code coverage | 91% |
| Codes shipping | 9 |
| Materials | 25 |
| Element types | 5 |
| Analysis types | 5 |
| Validation benchmarks | 3 |
| Commits | 30+ |
| Lines (Python + TS + docs) | ~14,000 |

## License

MIT. Engineering analysis software requires review and approval by a
licensed Professional Engineer before use in safety-critical work.
See [LICENSE](https://github.com/mihirpatel231197-art/pypemesh/blob/main/LICENSE).

# Validation Plan

**Version:** 0.1
**Status:** Binding — every release gated on this.

> A pipe stress tool that isn't validated is a paperweight. Engineers won't
> stamp drawings based on output they can't verify. Validation is not a feature
> — it's the product.

## Scope

- **Phase B**: validates ASME B31.3 static + basic dynamic
- **Phase B.1**: adds B31.1, non-linear, response spectrum
- **Phase C**: adds nuclear (NQA-1 audit process), additional codes

## Validation pyramid

```
                  ┌───────────────────────────┐
                  │   Field/Project validation  │   (C phase — compare to as-built)
                  ├───────────────────────────┤
                  │  Published benchmark suite │   (B phase — ASME, NC-3600, Markl)
                  ├───────────────────────────┤
                  │    Textbook worked examples │   (B phase — Peng, Kannappan)
                  ├───────────────────────────┤
                  │   Commercial cross-check   │   (B phase — Caesar II/AutoPIPE parity)
                  ├───────────────────────────┤
                  │    Component unit tests    │   (continuous — every commit)
                  ├───────────────────────────┤
                  │   Analytical closed-form   │   (continuous — every commit)
                  └───────────────────────────┘
```

Each layer must pass before the one above is meaningful.

---

## Layer 1: Analytical closed-form tests (continuous)

For every solver capability, at least one test against a hand-calculable answer.

### Static beam tests

| Test | Expected | Tolerance |
|---|---|---|
| Cantilever beam tip deflection under point load | `PL³/3EI` | <0.1% |
| Simply-supported beam midpoint deflection under distributed load | `5wL⁴/384EI` | <0.1% |
| Fixed-fixed beam midpoint reaction under axial load | `PA/L` | <0.01% |
| Euler buckling for pinned column | `π²EI/L²` | <1% |

### Thermal expansion

| Test | Expected | Tolerance |
|---|---|---|
| Anchored-free pipe thermal growth | `αΔT·L` | <0.01% |
| Anchored-anchored pipe thermal force | `EAα·ΔT` | <0.01% |
| U-bend loop stress (Peng Ch 2) | Peng worked result | <2% |

### Pressure

| Test | Expected | Tolerance |
|---|---|---|
| Hoop stress at a node under internal pressure | `PD/2t` | <0.1% |
| Longitudinal pressure stress | `PD/4t` | <0.1% |
| Bourdon effect elongation | `PLD/(4tE)(1-2ν)` | <1% |

### Dynamic (modal)

| Test | Expected | Tolerance |
|---|---|---|
| Cantilever beam first mode | `(1.875)²/(L²) · sqrt(EI/ρA)` | <1% |
| Simply-supported beam first mode | `π²/L² · sqrt(EI/ρA)` | <1% |

All live in `pypemesh-core/tests/analytical/` and run on every push.

---

## Layer 2: Component unit tests (continuous)

- **Stiffness matrices**: symmetry check (K == K.T), positive-definite (all eigenvalues > 0 for constrained system), rotational invariance
- **Mass matrices**: symmetric, positive-definite, total mass conservation (sum of diagonal translational terms = total weight)
- **SIF lookups**: every B31J table entry has a test
- **Flexibility factors**: match B31.3 Appendix D closed-form
- **Unit conversions**: round-trip check (SI → US → SI within 1e-10)
- **Project JSON**: round-trip serialization/deserialization preserves all values

---

## Layer 3: Commercial cross-check (B-phase gate)

We need Caesar II AND AutoPIPE output for the same sample models. We compare
our output node-by-node, force-by-force, stress-by-stress.

### Plan

1. Acquire Caesar II student license or 30-day trial (legally) — $0-500
2. Acquire AutoPIPE student license or trial — $0-500
3. Build a **reference set** of 20 progressively harder models:
   - #1-5: simple 3-5 node straight runs, weight + thermal
   - #6-10: L/U/Z loops with various restraints
   - #11-15: branched systems with tees, reducers
   - #16-20: mixed materials, support types, non-linear gaps

For each model, record:
- Displacement at every node (x/y/z/rx/ry/rz)
- Force/moment at every restraint
- Stress ratio at every element
- Modal frequencies (first 10)

**Acceptance:** all 20 models match Caesar II within 1% AND AutoPIPE within
1% on every quantity. Disagreements between Caesar and AutoPIPE documented.

---

## Layer 4: Textbook worked examples (B-phase gate)

Validation against textbooks engineers trust, run as automated tests.

| Source | Problems to pass |
|---|---|
| Peng & Peng, *Pipe Stress Engineering* (ASME Press) | Ch 2 ex 2.1, 2.2; Ch 5 ex 5.3, 5.5; Ch 7 ex 7.1 (nonlinear) |
| Kannappan, *Introduction to Pipe Stress Analysis* | Ch 3 worked example, Ch 6 U-bend |
| Smith & van Laan, *Piping and Pipeline Calculations* | Ch 4 sample, Ch 7 sample |
| Becht, *Process Piping (B31.3 handbook)* | Any worked SIF example, any worked flexibility example |

Each textbook problem encoded as a project JSON + expected output JSON +
tolerance. Test fails if drift exceeds tolerance.

---

## Layer 5: Published benchmark suite (B-phase gate)

### ASME B31.3 Appendix S — The canonical benchmark

ASME publishes a sample problem in B31.3 Appendix S with expected stress
values for a specific model. Every pipe stress code on earth gets benchmarked
against this. So do we.

**Acceptance:** sustained + expansion + occasional stress at every node within 1% of Appendix S values.

### ASME NC-3600 sample problem

Nuclear-class sample from ASME Section III Subsection NC.

**Acceptance (B-phase):** deformation and static stress within 2%. Full Class
1/2/3 validation deferred to Phase C with NQA-1.

### Markl fatigue test data (SIF verification)

A.R.C. Markl's 1952 fatigue tests on pipe components are the experimental
basis for all SIF values in all codes worldwide. We verify our solver plus
SIF tables predict Markl's results within experimental scatter (~15%).

**Data source:** Markl, "Fatigue Tests of Piping Components", Trans. ASME, 1952.
Tables available in public domain.

### NIST PSVP (Pipe Stress Verification Problems)

NIST's benchmark suite (if publicly accessible) or equivalent open benchmarks.

---

## Layer 6: Field/project validation (C-phase)

Only meaningful once we have real users on real projects.

- Compare our output to commercial-tool output on a **committed customer project** (with permission)
- Compare predicted support loads to measured loads on an instrumented piping system
- Track bug reports per user-month as a leading indicator of validation gaps

---

## Validation infrastructure

### Directory layout

```
pypemesh-core/
├── tests/
│   ├── analytical/           # layer 1 tests
│   ├── unit/                 # layer 2 tests
│   └── integration/          # layer 3 prep (cross-check fixtures)
└── benchmarks/               # layer 4+5 — heavier, gated

benchmarks/                    # repo root — multi-package benchmark suite
├── asme_b31_3_appendix_s/
│   ├── model.json
│   ├── expected.json
│   ├── tolerance.yaml
│   └── test_run.py
├── nc_3600_sample/
├── markl_fatigue/
├── peng_ch5_ex5_3/
├── ...
└── run_all.py                # runs every benchmark, writes summary CSV
```

### CI rules

- Every PR runs Layer 1 + Layer 2 (<30s total)
- Every merge to main runs Layer 4 + Layer 5 (<10 min)
- Nightly: full cross-check regression against frozen commercial outputs
- Any Layer 5 regression >1% blocks merge

### Reporting

Each run writes:
- `validation_report.html` — human-readable, per-test pass/fail with diffs
- `validation_report.json` — machine-readable for dashboards
- `validation_report.csv` — per-quantity diff table

Shipped with every release. Buyers/regulators can verify independently.

---

## Review & signoff

For Phase B release:
- [ ] All Layer 1 + Layer 2 tests pass
- [ ] Layer 4 textbook problems match within specified tolerance
- [ ] Layer 5 Appendix S, NC-3600, Markl all within tolerance
- [ ] Cross-check against Caesar II on 20 reference models (Layer 3)
- [ ] Validation report published
- [ ] Known limitations documented (what we don't validate yet)

For Phase C (commercial):
- All above, plus:
- [ ] NQA-1 audit (nuclear)
- [ ] ASME certification submission
- [ ] Commercial QA test plan
- [ ] Third-party independent validation engineer signoff
- [ ] PE signoff on validation report

---

## What validation does NOT do

- Make pypemesh safe for all projects automatically — users must still stamp their own work.
- Cover every edge case — every tool has bugs. We minimize unknown ones.
- Replace engineering judgment — tools inform; engineers decide.

These caveats live in `LICENSE` and in every report footer.

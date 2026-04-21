# Theory

Rigorous mechanical engineering derivations for every piece of physics inside
pypemesh. This is where we document the *why* behind every line of solver code.

## Standard

These docs are written to **MIT/NASA technical standard**:
- First-principles derivations, not summaries
- Every equation has its origin stated (textbook, code, paper, experiment)
- Proper math notation throughout (MathJax rendered on GitHub)
- No shortcuts — full steps
- Citations at the end of each doc
- Every solver function in `pypemesh-core` links back to its theory doc

## Reading order

1. **[BEAM_THEORY.md](BEAM_THEORY.md)** — Euler-Bernoulli & Timoshenko beam theory, 3D beam stiffness matrix derivation, local-to-global transformation
2. **[PIPE_MECHANICS.md](PIPE_MECHANICS.md)** — Hoop, longitudinal, axial pressure stress; Bourdon effect; thermal expansion; Karman ovalization for curved pipe
3. **[STRESS_CATEGORIES.md](STRESS_CATEGORIES.md)** — ASME Section III stress classification (primary, secondary, peak), membrane vs bending, why it matters for code compliance
4. **[CODE_B31_3.md](CODE_B31_3.md)** — Every B31.3 equation derived: sustained (23a), occasional (23b), expansion (17), allowable stress calculation
5. **[SIF_MARKL.md](SIF_MARKL.md)** — A.R.C. Markl's fatigue experiments (1952), the SIF definition, B31J modern SIF tables, flexibility factors
6. **[DYNAMIC_ANALYSIS.md](DYNAMIC_ANALYSIS.md)** — Modal analysis (eigenproblem), response spectrum method (SRSS, CQC, ABS), time history (Newmark-β), Rayleigh damping
7. **[SOLVER_NUMERICS.md](SOLVER_NUMERICS.md)** — Sparse matrix methods, direct vs iterative solvers, Newton-Raphson for non-linear, generalized eigenvalue algorithms

## Why this depth matters

Buyers of pipe stress software ask *how does it work?* Commercial tools
typically answer with marketing. We answer with this folder.

Every code equation in `pypemesh-core/codes/` has an accompanying theory
doc section. Every solver function has a derivation. When a user clicks
"why is this stress ratio 0.94?" in the UI, they can follow the chain all
the way down to Euler's beam bending equation from 1750.

## Conventions

**Notation:**
- $\vec{u}$ — displacement vector
- $\mathbf{K}$ — stiffness matrix (bold uppercase = matrix)
- $\sigma$ — normal stress
- $\tau$ — shear stress
- $\varepsilon$ — strain
- $E$ — Young's modulus
- $G$ — shear modulus
- $I$ — second moment of area
- $J$ — polar moment of area
- $\alpha$ — coefficient of thermal expansion
- $\nu$ — Poisson's ratio

**Units:** SI throughout — meters, Pascals, Newtons, seconds, Kelvin.

**References:** IEEE citation style at the end of each doc.

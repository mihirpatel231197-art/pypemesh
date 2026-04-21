# Solver Numerics — Sparse Matrices, Direct/Iterative Solvers, Newton-Raphson

**Scope:** The numerical methods that turn the FEA equations into actual
floating-point answers. Pipe stress models are sparse, banded, and modest
in size (hundreds to thousands of DOF). The right algorithms exploit this.

## 1. Why this matters

A naive dense solver on a 1000-DOF model:
- Memory: $1000^2 \cdot 8$ bytes = **8 MB** per matrix (fine)
- Solve time: $O(n^3)$ → **billions of FLOPs** → seconds-to-minutes

A sparse solver on the same model:
- Memory: ~50 KB (assuming ~1% fill-in)
- Solve time: ~milliseconds

The factor-of-1000 speedup is what makes interactive analysis possible.

## 2. Global stiffness matrix structure

### 2.1 Sparsity pattern

For a piping model with $n$ nodes (so $6n$ DOF), each beam element couples
12 DOF (6 at each end node). The global $\mathbf{K}$ matrix has:

- Total entries: $(6n)^2 = 36 n^2$
- Non-zero entries: ~$144 \cdot n_{\text{elements}}$ (rough upper bound)
- For typical pipe model: $n_{\text{elements}} \approx n$, so ~$144 n$ non-zeros
- Sparsity ratio: $144 / (36 n) = 4 / n$ — for $n = 1000$, **0.4% non-zero**

### 2.2 Bandedness

Pipe topology is mostly tree-like (with small loops). Node-numbering
heuristics (Cuthuill-McKee, AMD reordering) produce a tightly banded
matrix. Bandwidth typically **10-50** for well-numbered pipe models.

Banded direct solvers exploit this for $O(n \cdot bw^2)$ operations
instead of $O(n^3)$.

## 3. Sparse storage formats

### 3.1 COO (Coordinate)

`(row, col, value)` triples. Easy to assemble (just append). Inefficient
for solving.

```python
# Assembly phase
rows, cols, vals = [], [], []
for elem in elements:
    K_e = compute_element_stiffness(elem)
    dofs = element_dofs(elem)
    for i, gi in enumerate(dofs):
        for j, gj in enumerate(dofs):
            rows.append(gi)
            cols.append(gj)
            vals.append(K_e[i, j])
```

### 3.2 CSR (Compressed Sparse Row)

Three arrays: `data` (non-zero values), `indices` (column indices),
`indptr` (row start positions). Optimal for matrix-vector multiply.
Direct solvers expect CSR.

Conversion: `scipy.sparse.coo_matrix(...).tocsr()` — pypemesh does this
once after assembly.

### 3.3 LIL / DOK

Convenient for incremental construction; convert to CSR for solving.

pypemesh uses LIL during assembly, COO when accumulating element
contributions in batch, CSR for solving. The choice is per-phase.

## 4. Direct solvers

### 4.1 LU decomposition

Factorize $\mathbf{K} = \mathbf{L}\mathbf{U}$, then solve in two triangular
back-substitutions:
$$\mathbf{L}\vec{y} = \vec{F}; \quad \mathbf{U}\vec{u} = \vec{y}$$

Cost (sparse): $O(n \cdot bw^2)$ with bandwidth $bw$. Memory: $O(n \cdot bw)$.

For the 1000-DOF pipe model: factorization in ~10 ms, solve in <1 ms.

### 4.2 Cholesky decomposition

For symmetric positive-definite $\mathbf{K}$: $\mathbf{K} = \mathbf{L}\mathbf{L}^T$.
Faster than LU (half the operations, half the memory).

After applying boundary conditions (removing rigid body modes),
$\mathbf{K}$ is positive-definite and Cholesky applies.

### 4.3 SuperLU

The standard sparse direct solver. SciPy wraps it as `scipy.sparse.linalg.spsolve`.
Adequate for pypemesh's Phase B.

### 4.4 PARDISO / MUMPS / Eigen

Higher-performance sparse solvers, used at large scale. pypemesh's solver
interface is abstracted so we can swap to PARDISO (via Intel MKL) for
50K+ DOF models in Phase C.

```python
# Solver interface (pypemesh-core/solver/static.py)
def solve_static(K, F, restraints):
    K_reduced, F_reduced, free_dofs = apply_restraints(K, F, restraints)
    u_reduced = scipy.sparse.linalg.spsolve(K_reduced, F_reduced)
    u = expand_to_full(u_reduced, free_dofs)
    return u
```

## 5. Iterative solvers — for very large models

When direct solvers run out of memory (~$10^5$ DOF on consumer hardware),
iterative methods take over.

### 5.1 Conjugate Gradient (CG)

For symmetric positive-definite systems. Converges in $\leq n$ iterations,
typically much fewer with good preconditioning.

```python
from scipy.sparse.linalg import cg
u, info = cg(K, F, x0=u_initial, tol=1e-8, M=preconditioner)
```

### 5.2 Preconditioning

CG converges fast only for well-conditioned $\mathbf{K}$. Pipe stress
matrices have **high condition number** (long pipes have very stiff
behaviour for axial DOF, very soft for bending — ratio $\sim 10^4$). Without
preconditioning, CG can take 1000s of iterations.

Practical preconditioners:
- **ILU(0)** — incomplete LU with zero fill-in (fast but weak)
- **ILUT** — drop-tolerance ILU (better, more memory)
- **AMG** (algebraic multigrid) — best for big problems, complex to set up

pypemesh starts with ILU(0); will add AMG via `pyamg` for Phase C.

### 5.3 GMRES — for non-symmetric

If non-linear analysis produces non-symmetric tangent stiffness (uncommon
in pipe stress), GMRES is the iterative method of choice.

## 6. Boundary condition handling

### 6.1 Direct elimination (preferred)

Constrained DOFs are simply removed from $\mathbf{K}$ and $\vec{F}$ before
solving. Restraint reactions recovered as $R = \mathbf{K}_{cf} u_f$ where
the subscripts denote constrained-free coupling.

### 6.2 Penalty method

Add a large stiffness $K_{\text{pen}} = 10^{15}$ at the constrained DOF.
Crude, conditioning-destroying, but simple. We avoid this.

### 6.3 Lagrange multipliers

For complex constraints (master-slave, MPC). Increases system size but
handles arbitrary linear constraints. Used for rigid elements in pypemesh.

## 7. Non-linear analysis — Newton-Raphson

### 7.1 The non-linear system

Gaps, friction, and large-displacement effects make $\mathbf{K}$ depend on
$\vec{u}$:
$$\mathbf{K}(\vec{u}) \vec{u} = \vec{F}$$

### 7.2 Newton iteration

Define residual:
$$\vec{r}(\vec{u}) = \mathbf{K}(\vec{u}) \vec{u} - \vec{F}$$

Newton update from current iterate $\vec{u}_k$:
$$\mathbf{K}_T(\vec{u}_k) \cdot \Delta \vec{u} = -\vec{r}(\vec{u}_k)$$
$$\vec{u}_{k+1} = \vec{u}_k + \Delta \vec{u}$$

where $\mathbf{K}_T$ is the **tangent stiffness matrix** —
$\partial \vec{r} / \partial \vec{u}$ at the current iterate.

### 7.3 Convergence criteria

- $\|\Delta \vec{u}\|_\infty / \|\vec{u}\|_\infty < \varepsilon_u$ (typically $10^{-6}$)
- $\|\vec{r}\|_2 / \|\vec{F}\|_2 < \varepsilon_r$ (typically $10^{-8}$)
- Energy: $|\Delta \vec{u}^T \vec{r}| / |\vec{u}_0^T \vec{F}| < \varepsilon_e$

Both displacement and residual must converge. pypemesh requires both.

### 7.4 Modified Newton — when to use

Re-factorizing the tangent at every iteration is expensive. **Modified
Newton** uses the initial $\mathbf{K}_T$ for several iterations, only
re-factorizing when convergence stalls. Faster for mildly non-linear
problems but more iterations needed.

pypemesh uses full Newton by default, modified Newton when iterations
exceed a threshold.

### 7.5 Line search & arc-length

For sharply non-linear systems (snap-through, snap-back), pure Newton can
diverge. Line search picks $\alpha \in (0, 1]$ such that
$\vec{u}_{k+1} = \vec{u}_k + \alpha \Delta \vec{u}$ minimizes residual.
Arc-length methods (Riks) handle limit points. Phase B.2+ if needed.

### 7.6 Convergence failure

When Newton fails:
- Check load step size — try smaller increments
- Check non-linear element formulations (gaps, friction)
- Check for singularities (locked DOFs)
- Provide diagnostic: which DOF? which residual component? at what iteration?

pypemesh writes a structured diagnostic log on every failure — never just
"convergence failed".

## 8. Load sequencing — AutoPIPE's killer feature

### 8.1 The problem with load vector superposition

Caesar II's traditional approach treats loads as vectors that superpose
linearly:
$$\vec{u}_{\text{total}} = \vec{u}_W + \vec{u}_T + \vec{u}_P$$

For **linear systems**, this is exactly correct.

For **non-linear** systems with friction or gaps, it's *wrong*. Friction
forces depend on the contact direction; gaps depend on the relative
displacement; both depend on **what loads are applied in what order**.

### 8.2 Load sequencing

AutoPIPE applies loads incrementally:
1. Install at cold/no-pressure state
2. Apply weight (slow ramp) — gaps close, friction develops
3. Apply pressure (slow ramp) — Bourdon elongation, more friction
4. Heat to operating temperature (slow ramp) — thermal growth, friction reverses if necessary
5. Now we're at the operating state

Each increment uses the previous state as starting condition. The friction
forces, gap states, and plastic strains accumulate path-dependently.

### 8.3 Implementation in pypemesh

```python
# pypemesh-core/solver/nonlinear.py (sketch)
def solve_load_sequence(model, sequence):
    state = initial_state()
    history = []
    for load_step in sequence:
        state = newton_solve(model, state, load_step)
        history.append(state.copy())
    return history
```

Each load step is a partial-Newton solve starting from the previous step.
The full operating-condition state is the result of integrating through
the load history — not just superposing.

For purely linear problems (no friction, no gaps), the result equals
superposition. For non-linear, it's the physically correct answer.

## 9. Eigenvalue solvers (referenced from DYNAMIC_ANALYSIS.md)

For modal analysis: **Lanczos** for symmetric eigenproblems (the case
in pipe stress). Implemented as `scipy.sparse.linalg.eigsh` (wraps ARPACK).

For very large problems: **LOBPCG** (Locally Optimal Block PCG). Better
parallelism but requires good preconditioning.

For complex eigenvalue problems (non-classical damping, complex modes):
**QZ** decomposition or specialized solvers. Phase C.

## 10. Floating-point precision

All pypemesh internal math is **float64** (double precision). Single
precision saves memory but can give wrong answers in stress recovery
(stress is computed by differencing displacements, which loses precision).

Float128 (extended precision) not used — overkill, not portable.

## 11. Numerical conditioning checks

pypemesh runs after every solve:

1. **Condition number** of $\mathbf{K}_{\text{reduced}}$ — warn if $> 10^{12}$
2. **Force balance** — sum of restraint reactions = applied loads to <1e-8
3. **Energy balance** — strain energy = work done by external loads to <1e-6
4. **Symmetry of $\mathbf{K}$** — $\|K - K^T\|_\infty < 10^{-10}$

If any fails, the solve is flagged as unreliable. Better to fail loudly
than silently produce wrong numbers.

## 12. Performance benchmarks

Targets (consumer hardware, single core):

| Model size | Static linear | Modal (20 modes) | Non-linear (10 steps) |
|---|---|---|---|
| 100 nodes | <50 ms | <100 ms | <500 ms |
| 1000 nodes | <500 ms | <2 s | <10 s |
| 10000 nodes | <10 s | <30 s | <2 min |

Phase B targets the first two rows. Phase C extends to the third row with
PARDISO + parallel solves.

## 13. The validation suite for numerics

In `pypemesh-core/tests/numerics/`:
- Sparse matrix assembly correctness
- Direct vs iterative agreement to <1e-6
- Newton convergence on textbook non-linear problems (Belytschko Ch 6 examples)
- Eigenvalue accuracy on hand-computable cases (cantilever beam, simply-supported)
- Round-trip COO ↔ CSR ↔ dense identity
- Determinant of a known matrix matches numpy.linalg.det

## References

[1] Saad, Y. (2003). *Iterative Methods for Sparse Linear Systems* (2nd ed.). SIAM.

[2] Davis, T. A. (2006). *Direct Methods for Sparse Linear Systems*. SIAM.

[3] Bathe, K.-J. (1996). *Finite Element Procedures*. Prentice Hall. (Ch. 8, 9, 10)

[4] Belytschko, T., Liu, W. K., Moran, B., & Elkhodary, K. I. (2014). *Nonlinear Finite Elements for Continua and Structures* (2nd ed.). Wiley.

[5] Nocedal, J., & Wright, S. (2006). *Numerical Optimization* (2nd ed.). Springer. (Newton & line-search methods.)

[6] Lehoucq, R. B., Sorensen, D. C., & Yang, C. (1998). *ARPACK Users' Guide*. SIAM.

[7] Demmel, J. W. (1997). *Applied Numerical Linear Algebra*. SIAM.

[8] George, A., & Liu, J. W. H. (1981). *Computer Solution of Large Sparse Positive Definite Systems*. Prentice Hall. (Bandwidth reduction.)

[9] Crisfield, M. A. (1991). *Non-linear Finite Element Analysis of Solids and Structures, Vol. 1*. Wiley. (Path-dependent integration, load sequencing.)

# Dynamic Analysis — Modal, Response Spectrum, Time History

**Scope:** The mathematics behind dynamic pipe stress analysis. Why pipes
oscillate, how we predict the oscillations, and how we combine the
predictions into design stresses.

## 1. The dynamic governing equation

For a discretized pipe model with $n$ degrees of freedom, the equation of
motion is:

$$\mathbf{M}\ddot{\vec{u}} + \mathbf{C}\dot{\vec{u}} + \mathbf{K}\vec{u} = \vec{F}(t)$$

where:
- $\mathbf{M}$ — global mass matrix ($n \times n$)
- $\mathbf{C}$ — global damping matrix
- $\mathbf{K}$ — global stiffness matrix (from BEAM_THEORY.md §7)
- $\vec{u}$ — nodal displacement vector
- $\vec{F}(t)$ — time-varying applied force vector

Three classes of analysis solve this equation in different ways:

| Type | What it solves | Output |
|---|---|---|
| **Modal (eigenanalysis)** | $\mathbf{K}\vec{\phi} = \omega^2 \mathbf{M}\vec{\phi}$ | natural frequencies + mode shapes |
| **Response spectrum** | Combines modal responses to a spectrum input | peak stress per mode then combined |
| **Time history** | Direct integration of EOM | displacements/stresses at every time step |

## 2. Mass matrix

### 2.1 Lumped vs consistent

**Lumped mass**: total element mass split equally between end nodes.
Diagonal $\mathbf{M}$. Fast but underestimates rotational inertia.

**Consistent mass**: derived from the same Hermite shape functions used
for stiffness. For a 3D beam element:

$$\mathbf{m}_{\text{cons}} = \frac{\rho A L}{420}\begin{bmatrix}
140 & 0 & 0 & 0 & 0 & 0 & 70 & 0 & 0 & 0 & 0 & 0 \\
0 & 156 & 0 & 0 & 0 & 22L & 0 & 54 & 0 & 0 & 0 & -13L \\
0 & 0 & 156 & 0 & -22L & 0 & 0 & 0 & 54 & 0 & 13L & 0 \\
\dots
\end{bmatrix}$$

(full 12×12 form omitted for brevity; the code has it).

The consistent mass matrix is what pypemesh uses by default. Lumped is
available as a fast approximation for very large models.

### 2.2 Distributed mass contributions

Beyond pipe self-weight, mass contributions include:
- Fluid contents (pipe internal volume × fluid density)
- Insulation (insulation thickness × density × outer surface)
- Cladding, refractory lining
- Concentrated masses (valves, instruments) — added as point masses at
  the relevant node

All combine into one global $\mathbf{M}$.

## 3. Modal analysis — the eigenvalue problem

### 3.1 Setting up the eigenproblem

Free vibration: no damping, no applied force. The EOM becomes:
$$\mathbf{M}\ddot{\vec{u}} + \mathbf{K}\vec{u} = 0$$

Assume harmonic solution $\vec{u}(t) = \vec{\phi} \cos(\omega t)$:
$$(\mathbf{K} - \omega^2 \mathbf{M})\vec{\phi} = 0$$

Non-trivial solutions exist when:
$$\det(\mathbf{K} - \omega^2 \mathbf{M}) = 0$$

This is the **generalized eigenvalue problem**. Eigenvalues $\omega_i^2$
give the squared natural frequencies; eigenvectors $\vec{\phi}_i$ give the
mode shapes.

### 3.2 Properties

- $n$ DOF → $n$ modes (in principle; we usually want only first $N \ll n$)
- Eigenvalues are real and positive (for positive-definite $\mathbf{K}$, $\mathbf{M}$)
- Eigenvectors are **mass-orthogonal**: $\vec{\phi}_i^T \mathbf{M} \vec{\phi}_j = 0$ for $i \neq j$
- Eigenvectors are **stiffness-orthogonal**: $\vec{\phi}_i^T \mathbf{K} \vec{\phi}_j = 0$ for $i \neq j$
- Normalization: $\vec{\phi}_i^T \mathbf{M} \vec{\phi}_i = 1$ (unit mass-normalized)

### 3.3 Solver — Lanczos / Arnoldi

For the partial eigenvalue problem (find first $N$ modes of a sparse matrix
of size $n$), the **Lanczos** method (symmetric) or **Arnoldi** (general)
is the standard. SciPy's `scipy.sparse.linalg.eigsh` (Lanczos for
symmetric problems) wraps ARPACK and works well up to $n \sim 10^5$ DOF.

Key tuning parameters:
- $k$ — number of eigenvalues to find (default 20 for pypemesh)
- `which="SM"` — find smallest-magnitude (lowest frequencies)
- `sigma` — shift for shift-invert mode if desired

```python
from scipy.sparse.linalg import eigsh

eigenvalues, eigenvectors = eigsh(
    K_global, k=20, M=M_global, sigma=0, which="LM"
)
frequencies = np.sqrt(eigenvalues) / (2 * np.pi)  # Hz
```

### 3.4 Modal participation factor

For a base motion in direction $\vec{r}$ (e.g., earthquake along the
$x$-axis), each mode $i$ participates with factor:

$$\Gamma_i = \frac{\vec{\phi}_i^T \mathbf{M} \vec{r}}{\vec{\phi}_i^T \mathbf{M} \vec{\phi}_i}$$

Modes with high $\Gamma_i$ dominate the response in that direction. Pipe
stress engineers care most about modes with $\Gamma_i > 0.05$.

The cumulative **mass participation** in a direction:
$$\sum_i \frac{(\Gamma_i)^2 \cdot (\vec{\phi}_i^T \mathbf{M} \vec{\phi}_i)}{\vec{r}^T \mathbf{M} \vec{r}}$$

ASME and NRC require ≥90% mass participation in seismic directions before
analysis is considered complete. pypemesh checks this and warns if modes
are missing.

## 4. Response spectrum analysis

### 4.1 The concept

A response spectrum is a curve: maximum acceleration response of a
single-DOF oscillator vs. its natural frequency, for a given input
ground motion (e.g., a recorded earthquake or a code-defined design
motion).

For each mode $i$ of our piping system:
1. Look up the spectral acceleration $S_a(\omega_i, \zeta)$ at the mode's
   frequency and damping
2. Compute the modal peak displacement: $u_{\max,i} = \Gamma_i \cdot S_a / \omega_i^2$
3. Compute the modal stress field: $\sigma_i = $ stress recovery from
   $\vec{\phi}_i \cdot u_{\max,i}$

But each mode peaks at a different time — they don't all add. We combine
them statistically.

### 4.2 Combination methods

**SRSS (Square Root of Sum of Squares)** — assumes modes are uncorrelated:
$$\sigma_{\text{combined}} = \sqrt{\sum_i \sigma_i^2}$$

Adequate when modal frequencies are well-separated (>10% apart).

**CQC (Complete Quadratic Combination)** — accounts for correlation
between closely-spaced modes:
$$\sigma_{\text{combined}} = \sqrt{\sum_i \sum_j \rho_{ij} \sigma_i \sigma_j}$$

with cross-correlation coefficient (Der Kiureghian 1980):
$$\rho_{ij} = \frac{8 \sqrt{\zeta_i \zeta_j} (\zeta_i + r \zeta_j) r^{3/2}}{(1-r^2)^2 + 4\zeta_i \zeta_j r (1+r^2) + 4(\zeta_i^2 + \zeta_j^2) r^2}$$

with $r = \omega_j / \omega_i$. CQC is required for nuclear and
recommended for any model with closely-spaced modes.

**ABS (Absolute Sum)** — most conservative; rarely used:
$$\sigma_{\text{combined}} = \sum_i |\sigma_i|$$

NRC RG 1.92 mandates CQC for nuclear; pypemesh defaults to CQC for
seismic, SRSS for wind/water-hammer.

### 4.3 Multi-direction combinations

For three-directional earthquake, run response-spectrum in $x$, $y$, $z$
separately, then combine **directionally**:

$$\sigma_{\text{seismic}} = \sqrt{\sigma_x^2 + \sigma_y^2 + \sigma_z^2}$$

Or per ASCE 7-22 for buildings: 100%-30%-30% rule (one direction at full,
others at 30%, take envelope).

## 5. Time history analysis

When the load is time-varying and the system is non-linear (gaps,
friction), modal superposition fails. Direct time integration is needed.

### 5.1 Newmark-β method

Implicit time integration. At time $t_{n+1} = t_n + \Delta t$:

$$\mathbf{K}^* \vec{u}_{n+1} = \vec{F}^*_{n+1}$$

with effective stiffness:
$$\mathbf{K}^* = \mathbf{K} + \frac{1}{\beta \Delta t^2}\mathbf{M} + \frac{\gamma}{\beta \Delta t}\mathbf{C}$$

and effective force vector built from $\vec{u}_n$, $\dot{\vec{u}}_n$,
$\ddot{\vec{u}}_n$.

Standard parameters:
- $\beta = 1/4$, $\gamma = 1/2$ → unconditionally stable, no algorithmic damping
- $\beta = 1/6$, $\gamma = 1/2$ → linear acceleration (less robust)
- $\beta = 1/12$, $\gamma = 1/2$ → Fox-Goodwin (4th order accuracy)

pypemesh uses average acceleration ($\beta = 1/4, \gamma = 1/2$) by
default — matches the AutoPIPE and Caesar II default.

### 5.2 Time step selection

For accuracy: $\Delta t \leq T_{\min} / 10$ where $T_{\min}$ is the
shortest period of interest (typically the highest mode below 100 Hz).

For non-linear convergence: smaller $\Delta t$ improves Newton-Raphson
convergence at gaps/friction.

### 5.3 Force-time inputs

Common time-history inputs:
- **Water hammer**: from PIPENET, AFT Impulse, or analytical pressure-pulse
- **Pump trip**: rapid valve closure, instrument-recorded
- **Turbine trip**: machinery transient, vendor-supplied
- **Recorded earthquakes**: NGA-West2 database for ground motions

pypemesh accepts CSV, AFT-format, and PIPENET-format force-time files.

## 6. Damping

### 6.1 Material damping

Steel: $\zeta = 1\%$ at low strain, increases with strain amplitude.
Concrete: $\zeta = 5\%$. Insulated pipe: 1.5-3%.

### 6.2 Friction damping at supports

Coulomb friction at rest/guide supports dissipates energy. Energy
dissipation rate per cycle is amplitude-dependent — strictly non-linear.
For modal analysis, equivalent viscous damping approximation:
$$\zeta_{\text{eq}} = \frac{2 F_f}{\pi m \omega^2 |u|}$$

### 6.3 Rayleigh damping

For modal/time-history use:
$$\mathbf{C} = \alpha \mathbf{M} + \beta \mathbf{K}$$

Choosing $\alpha$, $\beta$ to give specified damping at two frequencies
$\omega_1$, $\omega_2$:
$$\alpha = \frac{2 \omega_1 \omega_2 (\zeta_1 \omega_2 - \zeta_2 \omega_1)}{\omega_2^2 - \omega_1^2}$$
$$\beta = \frac{2 (\zeta_2 \omega_2 - \zeta_1 \omega_1)}{\omega_2^2 - \omega_1^2}$$

Common choice: $\zeta_1 = \zeta_2 = 0.02$ at $\omega_1 = $ first mode and
$\omega_2 = $ tenth mode. Damping at intermediate modes is slightly less.

## 7. Standard spectra in pypemesh

Phase B.1 ships these spectrum libraries:

- **UBC 97** (legacy, still in some specs)
- **ASCE 7-22** — current US building code
- **IBC 2021** — building code
- **NRC RG 1.60** — nuclear (US)
- **CSA N289.3** — nuclear (Canada)
- **JEAG 4601** — nuclear (Japan)
- **EC8 (EN 1998-1)** — Eurocode seismic

User-defined spectra via CSV are always available.

## 8. Practical numbers

For a typical 6" SCH 40 process pipe loop, ~100 elements:
- First mode: 5-30 Hz depending on span
- 90% mass participation: typically reached by mode 30-50
- Solver time (Lanczos for 30 modes): <1s
- Response spectrum (CQC, 30 modes, 3 directions): <0.5s
- Time history (Newmark, $\Delta t = 0.001$s, 10s duration): 30-120s

## 9. Verification tests pypemesh runs

1. **Cantilever beam first mode**: $\omega_1 = (1.875)^2 / L^2 \cdot \sqrt{EI/(\rho A)}$. Tolerance: <1%.
2. **Simply-supported beam first mode**: $\omega_1 = \pi^2 / L^2 \cdot \sqrt{EI/(\rho A)}$. Tolerance: <1%.
3. **Modal orthogonality**: $\vec{\phi}_i^T \mathbf{M} \vec{\phi}_j$ vanishes for $i \neq j$, equals 1 for $i = j$.
4. **Mass conservation**: sum of diagonal translational entries of $\mathbf{M}$ = total system mass.
5. **Time-history vs analytical**: SDOF oscillator with known harmonic input, compare to closed-form solution.
6. **Modal vs time-history**: linear time-history matches modal superposition reconstruction within float precision.

All in `pypemesh-core/tests/analytical/test_dynamics.py`.

## 10. Pitfalls

- **Missing high-frequency modes**: ZPA (zero-period acceleration) correction needed if mass participation <90%
- **Closely-spaced modes**: SRSS underestimates; use CQC
- **Non-classical damping**: not all modes have the same $\zeta$; modal complex eigenanalysis required (Phase C)
- **Resonance**: if a forcing frequency matches a natural frequency, response amplifies dramatically. Solver must capture this — meaning enough modes and proper damping.

## References

[1] Newmark, N. M. (1959). "A method of computation for structural dynamics". *J. Engineering Mechanics Div., ASCE*, 85(EM3), 67–94.

[2] Wilson, E. L., Der Kiureghian, A., & Bayo, E. P. (1981). "A replacement for the SRSS method in seismic analysis". *Earthquake Engineering & Structural Dynamics*, 9(2), 187–192. *(Origin of CQC.)*

[3] Bathe, K.-J. (1996). *Finite Element Procedures*. Prentice Hall. (§9 — eigenvalue problems; §9.4 — Lanczos)

[4] Chopra, A. K. (2017). *Dynamics of Structures: Theory and Applications to Earthquake Engineering* (5th ed.). Pearson.

[5] NRC Regulatory Guide 1.92, Rev. 3 (2012). *Combining Modal Responses and Spatial Components in Seismic Response Analysis*.

[6] ASCE 7-22 (2022). *Minimum Design Loads and Associated Criteria for Buildings and Other Structures*. ASCE.

[7] Lehoucq, R. B., Sorensen, D. C., & Yang, C. (1998). *ARPACK Users' Guide*. SIAM. *(The numerical library SciPy wraps for eigenvalue problems.)*

[8] Peng, L.-C. (2009). *Pipe Stress Engineering*. ASME Press. (Ch. 7 — dynamic analysis)

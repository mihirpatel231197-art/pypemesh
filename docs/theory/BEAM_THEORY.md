# Beam Theory & the 3D Pipe Element Stiffness Matrix

**Scope:** Derivation of the 12×12 stiffness matrix for a 3D two-node straight
pipe element, starting from Euler's beam bending equation. This is the matrix
that goes into every pipe stress analysis ever written.

## 1. Physical setup

A straight prismatic pipe segment connecting two nodes, labelled $i$ (start)
and $j$ (end), aligned with the local $x$-axis. The local $y$ and $z$ axes
are the beam's principal bending axes.

Each node has **6 degrees of freedom** (DOF):
- 3 translations: $u$, $v$, $w$ along $x$, $y$, $z$
- 3 rotations: $\theta_x$, $\theta_y$, $\theta_z$ about $x$, $y$, $z$

So the element has 12 DOF total:
$$\vec{u}_e = \{ u_i, v_i, w_i, \theta_{xi}, \theta_{yi}, \theta_{zi}, u_j, v_j, w_j, \theta_{xj}, \theta_{yj}, \theta_{zj} \}^T$$

We seek a **12×12 stiffness matrix** $\mathbf{K}_e$ such that:
$$\vec{f}_e = \mathbf{K}_e \vec{u}_e$$

where $\vec{f}_e$ is the vector of end forces and moments.

## 2. Decoupling into four fundamental modes

Under small-deformation linear assumptions, the 12 DOF decouple into four
independent behaviours:

| Mode | DOF involved |
|---|---|
| Axial extension | $u_i, u_j$ |
| Torsion | $\theta_{xi}, \theta_{xj}$ |
| Bending about $z$ (in $x$-$y$ plane) | $v_i, \theta_{zi}, v_j, \theta_{zj}$ |
| Bending about $y$ (in $x$-$z$ plane) | $w_i, \theta_{yi}, w_j, \theta_{yj}$ |

We derive each block separately and assemble.

## 3. Axial stiffness (2×2 block)

### Governing equation

One-dimensional axial deformation follows from Hooke's law and
equilibrium along the bar:
$$EA \frac{d^2 u}{dx^2} = 0$$

where $E$ is Young's modulus and $A$ is the cross-sectional area. $EA$ is
the axial stiffness constant.

### Shape functions

Linear interpolation between end nodes:
$$u(x) = N_1(x) u_i + N_2(x) u_j$$

with
$$N_1(x) = 1 - \frac{x}{L}, \quad N_2(x) = \frac{x}{L}$$

### Stiffness by variational principle

Strain energy:
$$U = \frac{1}{2}\int_0^L EA \left(\frac{du}{dx}\right)^2 dx$$

Substituting the shape functions and differentiating with respect to the
nodal displacements gives:
$$\mathbf{k}_{\text{axial}} = \frac{EA}{L}\begin{bmatrix} 1 & -1 \\ -1 & 1 \end{bmatrix}$$

The off-diagonal sign captures reciprocal pull: pulling on one end pulls
equally on the other.

## 4. Torsional stiffness (2×2 block)

### Governing equation

Under pure torsion of a prismatic circular cross-section:
$$GJ \frac{d^2\theta_x}{dx^2} = 0$$

where $G = E/[2(1+\nu)]$ is the shear modulus and $J$ is the polar moment
of area. For a hollow pipe:
$$J = \frac{\pi}{32}\left(D_o^4 - D_i^4\right)$$

### Stiffness

By identical variational derivation to axial:
$$\mathbf{k}_{\text{torsion}} = \frac{GJ}{L}\begin{bmatrix} 1 & -1 \\ -1 & 1 \end{bmatrix}$$

## 5. Bending stiffness — Euler-Bernoulli beam (4×4 block)

### Governing equation

Bending in the $x$-$y$ plane (deflection $v(x)$, rotation
$\theta_z = dv/dx$) under Euler-Bernoulli assumptions (plane sections
remain plane and normal to the beam axis — no shear deformation):
$$EI_z \frac{d^4 v}{dx^4} = 0$$

### Shape functions

Cubic Hermite polynomials interpolate both displacement and slope:
$$v(x) = N_1 v_i + N_2 \theta_{zi} + N_3 v_j + N_4 \theta_{zj}$$

with
$$\begin{aligned}
N_1(x) &= 1 - \frac{3x^2}{L^2} + \frac{2x^3}{L^3} \\
N_2(x) &= x - \frac{2x^2}{L} + \frac{x^3}{L^2} \\
N_3(x) &= \frac{3x^2}{L^2} - \frac{2x^3}{L^3} \\
N_4(x) &= -\frac{x^2}{L} + \frac{x^3}{L^2}
\end{aligned}$$

These satisfy the four boundary conditions:
$$N_1(0)=1, N_1(L)=0, N_1'(0)=0, N_1'(L)=0$$
(and analogous for $N_2, N_3, N_4$).

### Stiffness by variational principle

Strain energy in bending:
$$U = \frac{1}{2}\int_0^L EI_z \left(\frac{d^2 v}{dx^2}\right)^2 dx$$

After substituting the Hermite polynomials and evaluating
$\partial^2 U / \partial u_a \partial u_b$ for each pair, the result is the
celebrated **Euler-Bernoulli beam stiffness** block:

$$\mathbf{k}_{\text{bend-z}} = \frac{EI_z}{L^3}\begin{bmatrix}
12 & 6L & -12 & 6L \\
6L & 4L^2 & -6L & 2L^2 \\
-12 & -6L & 12 & -6L \\
6L & 2L^2 & -6L & 4L^2
\end{bmatrix}$$

The same form applies for bending about $y$ with $I_y$ replacing $I_z$ and
the sign convention adjusted for the right-handed coordinate system:

$$\mathbf{k}_{\text{bend-y}} = \frac{EI_y}{L^3}\begin{bmatrix}
12 & -6L & -12 & -6L \\
-6L & 4L^2 & 6L & 2L^2 \\
-12 & 6L & 12 & 6L \\
-6L & 2L^2 & 6L & 4L^2
\end{bmatrix}$$

## 6. Timoshenko correction (optional)

Euler-Bernoulli assumes shear deformation is negligible. For short pipes
or small bending spans this breaks down. Timoshenko beam theory adds a
shear contribution via the shear correction factor $\kappa$ (0.5 for
thin-walled circular cross-sections):
$$\phi = \frac{12 EI}{\kappa G A L^2}$$

The bending stiffness becomes:
$$\mathbf{k}_{\text{Tim}} = \frac{EI}{L^3 (1+\phi)} \cdot \left[ \text{modified Hermite terms} \right]$$

For pipe runs where $L/D > 10$, Euler-Bernoulli is accurate to <1%.
For $L/D < 5$, Timoshenko becomes important. pypemesh defaults to
Euler-Bernoulli, with a Timoshenko flag when short elements detected
(Phase B.1+).

## 7. Assembled 12×12 local stiffness matrix

Assembling the four blocks into the 12×12 element matrix (ordering
$\{u, v, w, \theta_x, \theta_y, \theta_z\}$ at each node):

$$\mathbf{K}_e^{\text{local}} = \begin{bmatrix}
\frac{EA}{L} & 0 & 0 & 0 & 0 & 0 & -\frac{EA}{L} & 0 & 0 & 0 & 0 & 0 \\
0 & \frac{12EI_z}{L^3} & 0 & 0 & 0 & \frac{6EI_z}{L^2} & 0 & -\frac{12EI_z}{L^3} & 0 & 0 & 0 & \frac{6EI_z}{L^2} \\
0 & 0 & \frac{12EI_y}{L^3} & 0 & -\frac{6EI_y}{L^2} & 0 & 0 & 0 & -\frac{12EI_y}{L^3} & 0 & -\frac{6EI_y}{L^2} & 0 \\
0 & 0 & 0 & \frac{GJ}{L} & 0 & 0 & 0 & 0 & 0 & -\frac{GJ}{L} & 0 & 0 \\
0 & 0 & -\frac{6EI_y}{L^2} & 0 & \frac{4EI_y}{L} & 0 & 0 & 0 & \frac{6EI_y}{L^2} & 0 & \frac{2EI_y}{L} & 0 \\
0 & \frac{6EI_z}{L^2} & 0 & 0 & 0 & \frac{4EI_z}{L} & 0 & -\frac{6EI_z}{L^2} & 0 & 0 & 0 & \frac{2EI_z}{L} \\
-\frac{EA}{L} & 0 & 0 & 0 & 0 & 0 & \frac{EA}{L} & 0 & 0 & 0 & 0 & 0 \\
0 & -\frac{12EI_z}{L^3} & 0 & 0 & 0 & -\frac{6EI_z}{L^2} & 0 & \frac{12EI_z}{L^3} & 0 & 0 & 0 & -\frac{6EI_z}{L^2} \\
0 & 0 & -\frac{12EI_y}{L^3} & 0 & \frac{6EI_y}{L^2} & 0 & 0 & 0 & \frac{12EI_y}{L^3} & 0 & \frac{6EI_y}{L^2} & 0 \\
0 & 0 & 0 & -\frac{GJ}{L} & 0 & 0 & 0 & 0 & 0 & \frac{GJ}{L} & 0 & 0 \\
0 & 0 & -\frac{6EI_y}{L^2} & 0 & \frac{2EI_y}{L} & 0 & 0 & 0 & \frac{6EI_y}{L^2} & 0 & \frac{4EI_y}{L} & 0 \\
0 & \frac{6EI_z}{L^2} & 0 & 0 & 0 & \frac{2EI_z}{L} & 0 & -\frac{6EI_z}{L^2} & 0 & 0 & 0 & \frac{4EI_z}{L}
\end{bmatrix}$$

### Properties

- **Symmetric**: $\mathbf{K}_e = \mathbf{K}_e^T$ (follows from energy symmetry)
- **Rank-deficient**: null space of dimension 6 (rigid body modes: 3 translations + 3 rotations)
- **Positive-semi-definite**: all eigenvalues $\geq 0$

These are **numerical invariants pypemesh tests on every commit** — see
`pypemesh-core/tests/unit/test_beam_stiffness.py`.

## 8. Pipe-specific cross-section properties

For a circular pipe with outer diameter $D_o$ and wall thickness $t$:
$$D_i = D_o - 2t$$
$$A = \frac{\pi}{4}\left(D_o^2 - D_i^2\right)$$
$$I = I_y = I_z = \frac{\pi}{64}\left(D_o^4 - D_i^4\right)$$
$$J = 2I = \frac{\pi}{32}\left(D_o^4 - D_i^4\right)$$

For insulated pipe, effective area and density are adjusted in the load
vector (insulation adds weight but not structural stiffness). For corrosion
allowance, wall thickness for stiffness uses nominal $t$; wall thickness for
stress recovery uses $t - CA$.

## 9. Local-to-global transformation

The global stiffness matrix aggregates element contributions, each rotated
from the element's local frame to the global coordinate frame.

The transformation is driven by the element's **direction cosine matrix**
$\mathbf{R}$ — a 3×3 matrix where row $k$ is the unit vector of local axis $k$
expressed in global coordinates.

The 12×12 rotation operator is:
$$\mathbf{T} = \begin{bmatrix} \mathbf{R} & 0 & 0 & 0 \\ 0 & \mathbf{R} & 0 & 0 \\ 0 & 0 & \mathbf{R} & 0 \\ 0 & 0 & 0 & \mathbf{R} \end{bmatrix}$$

(Block-diagonal because we rotate the 3 translations and 3 rotations at each
node using the same $\mathbf{R}$.)

The element's global-frame stiffness:
$$\mathbf{K}_e^{\text{global}} = \mathbf{T}^T \mathbf{K}_e^{\text{local}} \mathbf{T}$$

And the global force-displacement relation, assembled across all elements by
overlapping DOFs:
$$\mathbf{K}_{\text{global}} \vec{u}_{\text{global}} = \vec{f}_{\text{global}}$$

## 10. Geometric (initial-stress) stiffness — for buckling & P-delta

When axial load $P$ is significant relative to Euler buckling load
$P_{cr} = \pi^2 EI / L^2$, the bending stiffness is modified by a
"geometric stiffness" term:
$$\mathbf{K}_{\text{geom}} = \frac{P}{30L}\begin{bmatrix}
36 & 3L & -36 & 3L \\
3L & 4L^2 & -3L & -L^2 \\
-36 & -3L & 36 & -3L \\
3L & -L^2 & -3L & 4L^2
\end{bmatrix}$$

Total stiffness: $\mathbf{K} = \mathbf{K}_{\text{elastic}} + \mathbf{K}_{\text{geom}}$.

pypemesh adds this in Phase B.1 for slender piping (risers, long spans
under high axial thrust).

## 11. Distributed loads — consistent load vector

For a uniformly distributed transverse load $w$ (e.g., self-weight for a
horizontal pipe), the consistent nodal force vector derived by virtual work:

$$\vec{f}_{UDL} = \left\{ 0, \frac{wL}{2}, 0, 0, 0, \frac{wL^2}{12}, 0, \frac{wL}{2}, 0, 0, 0, -\frac{wL^2}{12}\right\}^T$$

This includes moment couples at the ends — critical for accurate bending
moment recovery.

For thermal expansion (distributed "load" from $\alpha \Delta T$):
$$\vec{f}_{\text{thermal}} = \left\{ -EA\alpha\Delta T, 0, 0, 0, 0, 0, EA\alpha\Delta T, 0, 0, 0, 0, 0\right\}^T$$

This is how constrained thermal growth becomes an axial force in the
stiffness solve.

## 12. Verification checks (pypemesh runs these on every commit)

1. **Symmetry**: $\|\mathbf{K} - \mathbf{K}^T\|_\infty < 10^{-10}$
2. **Rank deficiency** (free element): null space dim = 6, matching rigid body modes
3. **Cantilever tip deflection**: apply point load $P$ at free end, solve, check $v_{tip} = PL^3/(3EI)$ to <0.01%
4. **Thermal axial force**: fixed-fixed pipe at $\Delta T$, check axial force $= EA\alpha\Delta T$
5. **Rotational invariance**: rotate an element 45° about any axis, verify $\mathbf{K}^{\text{global}}$ matches a hand-computed transformation

All five tests live in
`pypemesh-core/tests/analytical/test_beam_stiffness.py`.

## References

[1] Euler, L. (1750). *Methodus inveniendi lineas curvas maximi minimive proprietate gaudentes*. Lausanne.

[2] Bernoulli, J. (1705). *Véritable hypothèse de la résistance des solides avec la démonstration de la courbure des corps qui font ressort*. Mém. Acad. Roy. Sci. Paris.

[3] Timoshenko, S. P. (1921). "On the correction for shear of the differential equation for transverse vibrations of prismatic bars". *Philosophical Magazine*, 41(245), 744–746.

[4] Bathe, K.-J. (1996). *Finite Element Procedures*. Prentice Hall. (§4.2 — beam elements)

[5] Cook, R. D., Malkus, D. S., Plesha, M. E., & Witt, R. J. (2002). *Concepts and Applications of Finite Element Analysis* (4th ed.). Wiley. (Ch. 2, 3)

[6] Peng, L.-C., & Peng, T.-L. (2009). *Pipe Stress Engineering*. ASME Press. (Ch. 3)

[7] Kannappan, S. (1986). *Introduction to Pipe Stress Analysis*. Wiley. (Ch. 2)

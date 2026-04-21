# Pipe Mechanics — Internal Pressure, Thermal Expansion, Curved Pipe

**Scope:** The three physical phenomena that make pipe stress different from
general beam analysis: internal pressure generating hoop/longitudinal/Bourdon
stresses, thermal expansion becoming a constrained force, and curved-pipe
flexibility that departs from straight-beam theory.

## 1. Stresses from internal pressure

### 1.1 Hoop (circumferential) stress

Consider a thin-walled pipe of mean diameter $D$, wall thickness $t$, under
internal pressure $P$. Take a half-cylinder of length $L$ as a free body.

The pressure force acting on the projected diameter:
$$F_P = P \cdot D \cdot L$$

The resisting hoop stress acts on two wall cross-sections of area $t \cdot L$:
$$F_{\sigma} = 2 \sigma_h \cdot t \cdot L$$

Equilibrium $F_P = F_{\sigma}$ gives:
$$\boxed{\sigma_h = \frac{PD}{2t}}$$

Valid for $t/D < 0.1$ (thin-wall). For thick-walled pipe use Lamé's equations.

### 1.2 Longitudinal (axial) stress from pressure

Consider a full cross-section cap: pressure acts on the end area
$\pi D^2 / 4$, resisted by axial stress on the annular wall area
$\pi D t$ (thin-wall approximation):

$$\sigma_{ax} \cdot \pi D t = P \cdot \frac{\pi D^2}{4}$$

$$\boxed{\sigma_{ax} = \frac{PD}{4t}}$$

Note: $\sigma_{ax} = \sigma_h / 2$. Hoop is always twice longitudinal in a
capped thin-walled pipe — this is why pressure vessels fail axially (along a
seam) under over-pressure.

### 1.3 Radial stress

For thin-walled pipe at the outer surface $\sigma_r \approx 0$; at the inner
surface $\sigma_r = -P$ (compressive). For B31.3-scope piping
($P \ll \sigma_y$), radial stress is neglected.

### 1.4 Bourdon effect — pressure elongation

A capped pipe under internal pressure elongates axially even without
external load. The net axial strain is:
$$\varepsilon_{ax} = \frac{1}{E}\left(\sigma_{ax} - \nu \sigma_h \right) = \frac{1}{E}\left(\frac{PD}{4t} - \nu \frac{PD}{2t}\right) = \frac{PD(1-2\nu)}{4tE}$$

Length change:
$$\Delta L_P = \varepsilon_{ax} L = \frac{PDL(1-2\nu)}{4tE}$$

For steel ($\nu = 0.3$): $\varepsilon_{ax} = 0.1 \cdot PD/(tE)$. For a 6"
schedule 40 pipe (D=168 mm, t=7.1 mm) at 50 bar, $E=2\times10^{11}$ Pa:
$$\varepsilon_{ax} = \frac{5\times10^6 \cdot 0.168 \cdot 0.4}{4 \cdot 7.1\times10^{-3} \cdot 2\times10^{11}} = 5.9 \times 10^{-5}$$

A 100 m run grows **5.9 mm** from pressure alone. This elongation shows up
as an anchor force if the pipe is constrained — same physics as thermal
growth, proportional to $(1-2\nu)/4 \cdot PD/(tE)$ instead of $\alpha \Delta T$.

pypemesh treats pressure as a distributed axial "pre-strain" load in the
element load vector, mathematically identical to thermal.

### 1.5 Thick-walled pipe (Lamé equations)

When $t/D > 0.1$, the thin-wall assumption breaks. Lamé's solution for a
cylinder under internal pressure $P_i$:

$$\sigma_h(r) = P_i \frac{r_i^2}{r_o^2 - r_i^2}\left(1 + \frac{r_o^2}{r^2}\right)$$

$$\sigma_r(r) = P_i \frac{r_i^2}{r_o^2 - r_i^2}\left(1 - \frac{r_o^2}{r^2}\right)$$

$$\sigma_{ax} = P_i \frac{r_i^2}{r_o^2 - r_i^2}$$

where $r_i$ and $r_o$ are inner and outer radii.

pypemesh uses thin-wall by default (all B31.3-scope); thick-wall solver
available in Phase C for high-pressure services ($P > 300$ bar).

## 2. Thermal expansion — from strain to force

### 2.1 Free thermal expansion

Unconstrained pipe heated from $T_1$ to $T_2$ grows by:
$$\Delta L = \alpha L (T_2 - T_1) = \alpha L \Delta T$$

where $\alpha$ is the coefficient of linear thermal expansion.

### 2.2 Constrained thermal growth → thermal force

If both ends are rigidly anchored and thermal growth prevented, the pipe
experiences a thermal strain:
$$\varepsilon_{th} = \alpha \Delta T$$

Because the pipe is physically unable to grow, a compressive stress develops
equal to $E \varepsilon_{th}$ (no Poisson effect since lateral strain is
free):
$$\sigma_{th} = -E \alpha \Delta T$$

Axial thermal force (compressive for heating):
$$\boxed{F_{th} = -EA\alpha\Delta T}$$

### 2.3 Partial constraint

Real piping is never fully rigid — anchors have some flexibility, and
bends/loops absorb some growth. The thermal force is reduced by the
flexibility factor $\beta$:
$$F_{th,\text{actual}} = -EA\alpha\Delta T \cdot (1 - \beta)$$

where $\beta$ is computed from the solver (the ratio of actual thermal
displacement to free thermal displacement). For a fully rigid line,
$\beta = 0$; for a perfectly flexible line (long loop), $\beta = 1$ and
thermal force vanishes.

### 2.4 Temperature-dependent properties

$E$ and $\alpha$ both vary with temperature. ASME Section II Part D
tabulates them. pypemesh interpolates linearly between tabulated points
(cubic for Phase C).

**Example:** A106-B carbon steel:
| T (°C) | E (GPa) | α (×10⁻⁶/K) |
|---|---|---|
| 20 | 203 | 11.5 |
| 200 | 192 | 12.6 |
| 400 | 176 | 13.8 |
| 500 | 166 | 14.3 |

High-temperature service can drop E by 20% — the solver must use $E(T)$ at
operating temperature, not $E(20°C)$, for stress calculation.

### 2.5 Combined thermal + pressure elongation

A pipe under operating conditions sees both thermal and pressure strain:
$$\varepsilon_{\text{op}} = \alpha \Delta T + \frac{PD(1-2\nu)}{4tE}$$

Both contribute to the "displacement load" in the solver's load vector. In
the sustained (weight + pressure) load case, only pressure contributes;
in the expansion (thermal) case, only thermal; in the operating case, both.

## 3. Curved pipe — Karman ovalization

### 3.1 Why curved pipe isn't a curved beam

A straight beam under bending keeps its cross-section circular: each fibre
strains linearly with distance from the neutral axis, classic beam theory.

A **curved pipe** (elbow) under bending experiences an additional effect:
the cross-section **ovalizes** — the inner half squashes and the outer half
stretches. This is because the inner fibres take shorter arc length under
bending than the neutral axis, and the tube walls can't maintain circular
shape against this mismatch.

The ovalization makes the pipe **more flexible** than a straight beam of the
same cross-section — you can bend it further for the same moment — and
**concentrates bending stress** on certain fibres.

### 3.2 Von Kármán's flexibility factor (1911)

Theodore von Kármán showed that a curved pipe's bending flexibility is
enhanced by a dimensionless factor $k$:

$$k = \frac{1.65}{h}$$

where
$$h = \frac{tR}{r^2}$$

is the **pipe bend characteristic** (or *flexibility characteristic*),
with:
- $t$ — wall thickness
- $R$ — bend radius (center of curvature to center of pipe)
- $r$ — mean pipe radius (not bend radius)

**Physical meaning of $h$:** a short-radius, thin-walled elbow has small
$h$ and large $k$ (very flexible). A long-radius, thick-walled elbow has
large $h$ and $k \to 1$ (behaves like a straight beam).

### 3.3 ASME B31.3 Appendix D treatment

ASME codifies the Karman result with an empirical refinement for internal
pressure (which stiffens the bend):

$$k = \frac{1.65}{h \left(1 + \frac{P r}{E t} \cdot \frac{R}{r}^{4/3}\right)}$$

For most operating pressures the pressure correction is <10% and often
neglected.

### 3.4 Stress intensification factor (SIF)

The same ovalization that increases flexibility concentrates stress. The
**stress intensification factor** (see next doc, SIF_MARKL.md) is:

$$i = \frac{0.9}{h^{2/3}}$$

for in-plane bending of a pipe bend (ASME B31.3 Appendix D).

For out-of-plane bending: $i = 0.75/h^{2/3}$.

### 3.5 Curved-beam element in the solver

pypemesh handles elbows by replacing the straight-beam bending stiffness
with a **reduced stiffness** multiplied by $1/k$:

$$EI_{\text{effective}} = \frac{EI}{k}$$

This gives the beam element the correct flexibility in the global solve.
Stress recovery then applies SIF $i$ to the recovered bending moment.

**Example:** 6" SCH 40 LR elbow (R = 228 mm, r = 81 mm, t = 7.1 mm):
$$h = \frac{7.1 \cdot 228}{81^2} = 0.247$$
$$k = 1.65 / 0.247 = 6.68$$
$$i = 0.9 / 0.247^{2/3} = 2.28$$

The elbow is **6.7× more flexible** than a straight pipe of the same
cross-section and length. The peak stress on the outer fibre is **2.28× the
nominal** bending stress.

This is why Caesar II and AutoPIPE get different results from a naïve
beam analysis — getting Karman flexibility right is 60% of the answer.

## 4. Flexibility of other fittings

### 4.1 Tee junctions

A tee introduces a stress concentration at the crotch. SIF varies by tee
type (welding tee, sockolet, reinforced saddle). B31J 2017 provides tabulated
values; pypemesh ships the table in `codes/b31j.py`.

Typical values:
- Welding tee: $i_{\text{run}} \approx 1.0$, $i_{\text{branch}} \approx 2.2$
- Sockolet: $i \approx 1.8$
- Stub-in: $i \approx 2.5$

### 4.2 Reducers

Eccentric or concentric reducers: $i = 2.0$ per B31.3 unless tested lower.

### 4.3 Flanges

Flanges themselves don't concentrate stress at the bolt holes the same way;
their failure mode is gasket leakage, handled by Kellogg or ASME Appendix 2
checks separately.

## 5. Summary of force contributions

The total longitudinal stress in a pipe element:
$$\sigma_{L} = \underbrace{\frac{PD}{4t}}_{\text{pressure}} + \underbrace{\frac{M_a}{Z}}_{\text{bending}} + \underbrace{\frac{F_{ax}}{A}}_{\text{axial}}$$

And the peak stress at the outer fibre with SIF:
$$\sigma_{\text{peak}} = \sqrt{(i_i M_i)^2 + (i_o M_o)^2}/Z + \frac{PD}{4t} + \frac{F_{ax}}{A}$$

This is what B31.3 uses in its equations (next doc).

## References

[1] von Kármán, T. (1911). "Über die Formänderung dünnwandiger Rohre, insbesondere federnder Ausgleichrohre". *Z. VDI*, 55, 1889–1895.

[2] Gross, N. (1952). "Experiments on short-radius pipe bends". *Proc. IMechE*, Part 1B, Vol. 1(3).

[3] ASME B31.3 (2022). *Process Piping*. ASME. (Appendix D)

[4] ASME B31J (2017). *Stress Intensification Factors, Flexibility Factors, and Sustained Stress Indices for Metallic Piping Components*. ASME.

[5] Lamé, G. (1866). *Leçons sur la théorie mathématique de l'élasticité des corps solides*. Paris: Gauthier-Villars.

[6] Peng, L.-C., & Peng, T.-L. (2009). *Pipe Stress Engineering*. ASME Press. (Ch. 2–3)

[7] Dodge, W. G., & Moore, S. E. (1972). "Stress indices and flexibility factors for moment loadings on elbows and curved pipe". *ORNL-TM-3658*.

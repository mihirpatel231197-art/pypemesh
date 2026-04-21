# ASME B31.3 — Equations Derived from First Principles

**Scope:** Every B31.3 stress equation pypemesh implements, derived and
explained. Read STRESS_CATEGORIES.md, BEAM_THEORY.md, PIPE_MECHANICS.md,
and SIF_MARKL.md first.

> ASME B31.3 is the most widely used pipe stress code on Earth. Its core
> equations look simple — three lines per check — but each line encodes
> ~80 years of refinement. Understanding *why* each equation looks the way
> it does prevents misuse.

## 1. Section structure

B31.3 §302.3 ("Allowable Stresses and Other Stress Limits") sets the rules.
The stress equations live in §319.4. SIF and flexibility tables are in
Appendix D (now harmonized with B31J).

## 2. Sustained stress (Eq. 23a)

### Equation as written in B31.3:

$$S_L = \frac{P D}{4 t} + \frac{0.75 i M_a}{Z} \leq S_h$$

### Term-by-term derivation

**$\frac{PD}{4t}$** — longitudinal pressure stress (see PIPE_MECHANICS.md §1.2).

**$M_a$** — resultant bending moment from sustained loads (weight + sustained
external loads). Computed as:
$$M_a = \sqrt{M_x^2 + M_y^2 + M_z^2}$$

(or, more precisely, the resultant of the two bending moments only, with
torsion handled separately).

**$Z$** — section modulus, $Z = I / c$ where $c$ is distance from neutral
axis to outer fibre. For a hollow pipe:
$$Z = \frac{\pi}{32} \cdot \frac{D_o^4 - D_i^4}{D_o}$$

**$0.75 i$** — the **sustained stress index** (SSI). Why 0.75 and not just $i$?

Markl's tests measured SIF in *cyclic loading* (fatigue regime). For
sustained (one-way) loading, the actual stress concentration is somewhat
*lower* because no plastic shakedown has occurred. ASME's empirical
correction factor is 0.75 — the SSI for most fittings is 75% of the
fatigue-derived SIF, with a minimum of 1.0.

(In B31J 2017, separate sustained stress indices replaced the blanket
0.75 multiplier. pypemesh uses B31J SSI tables when available, falls back
to $0.75 i$ otherwise.)

**$S_h$** — hot allowable from ASME Section II Part D. For carbon steel
A106-B at 200°C: $S_h \approx 124$ MPa. This is approximately the lower
of:
- $\sigma_y / 1.5$ (factor of 1.5 against yield)
- $\sigma_u / 3$ (factor of 3 against ultimate)
- creep-rupture-time-dependent values at high temp

### Acceptance

$S_L \leq S_h$ — the sustained longitudinal stress must not exceed the hot
allowable. This is a **collapse check** — if violated, the pipe will
deform plastically under sustained gravity + pressure load and may fail
catastrophically.

### Example calculation

6" SCH 40 A106-B pipe, $D_o = 168.3$ mm, $t = 7.1$ mm, $P = 50$ bar = 5 MPa,
sustained bending moment $M_a = 1500$ N·m at a long-radius elbow ($i = 2.28$
from PIPE_MECHANICS.md §3.5).

$$Z = \frac{\pi}{32} \cdot \frac{0.1683^4 - 0.1541^4}{0.1683} = 1.40 \times 10^{-4}~\text{m}^3$$

$$\frac{PD}{4t} = \frac{5\times10^6 \cdot 0.1683}{4 \cdot 0.0071} = 29.6~\text{MPa}$$

$$\frac{0.75 \cdot 2.28 \cdot 1500}{1.40\times10^{-4}} = 18.3~\text{MPa}$$

$$S_L = 29.6 + 18.3 = 47.9~\text{MPa}$$

At 200°C, $S_h = 124$ MPa. Stress ratio $= 47.9 / 124 = 0.39$. **Pass.**

## 3. Occasional stress (Eq. 23b)

### Equation:

$$S_{Lo} = \frac{P D}{4 t} + \frac{0.75 i (M_a + M_b)}{Z} \leq k S_h$$

where:
- $M_b$ — resultant bending moment from occasional loads (wind, seismic,
  pressure relief)
- $k$ — occasional load factor:
  - $k = 1.33$ for short-term events (wind, water hammer)
  - $k = 1.20$ for very-short-term (seismic per ASCE 7)

### Why $k$ is greater than 1

Occasional loads act for short durations. Materials have higher allowable
stress for short-duration loading because:
- Low cycle count → fatigue not critical
- Strain rate effects → yield strength is rate-dependent (steel is
  ~10% stronger at seismic strain rates)
- Probabilistic argument → low probability of simultaneous max occurrences

ASME's $1.33$ is empirical, conservative.

### Operating stress (informational)

The combination $S_L + S_E$ at operating temperature may approach or
exceed yield, but this is OK if shakedown applies. ASME doesn't make this
an explicit check in B31.3 (it's an explicit check in B31.1 and §III).
pypemesh reports it as informational.

## 4. Expansion (displacement) stress (Eq. 17)

### Equation:

$$S_E = \sqrt{S_b^2 + 4 S_t^2} \leq S_A$$

where:

$$S_b = \frac{i_i M_i + i_o M_o}{Z}$$

(quadrature combination of in-plane and out-of-plane bending with their
respective SIFs)

$$S_t = \frac{M_t}{2 Z}$$

(torsion stress; the $2Z$ is because torsion uses the polar section modulus
$2Z$ for thin-walled circular tubes)

### Why $\sqrt{S_b^2 + 4 S_t^2}$?

This is the **maximum shear stress** (Tresca-like) intensity in 3D bending +
torsion. Bending creates a uniaxial normal stress on the outer fibre;
torsion creates a shear stress. The principal stresses are:
$$\sigma_{1,2} = \frac{S_b}{2} \pm \sqrt{(S_b/2)^2 + S_t^2}$$

Maximum shear stress:
$$\tau_{max} = \sigma_1 - \sigma_2 = 2\sqrt{(S_b/2)^2 + S_t^2} = \sqrt{S_b^2 + 4 S_t^2}$$

ASME interprets this as the "stress intensity" — the equivalent uniaxial
stress that would produce the same maximum shear.

### Allowable $S_A$

$$S_A = f \left[ 1.25 (S_c + S_h) - S_L \right]$$

with:
- $S_c$ — cold (installation) allowable
- $S_h$ — hot (operating) allowable
- $S_L$ — actual sustained stress at this point
- $f$ — fatigue cycle factor:
  - $f = 1.0$ for $N \leq 7000$ cycles
  - $f = (10^6/N)^{0.2}$ for higher cycle counts (capped at 0.15)

### Why "liberal allowable" matters

The $1.25 (S_c + S_h)$ term is the **shakedown allowable** — about
$3 S_m$ (per Bree 1967, see STRESS_CATEGORIES.md §3.2).

Subtracting $S_L$ gives the **remaining margin** available for thermal/
expansion stress, after sustained stress has consumed its share. A pipe
heavily loaded sustained (high $S_L$) gets less expansion allowable; a
lightly-loaded pipe gets more. This is more efficient than a flat
allowable.

### Example calculation

Same elbow as before. Operating temperature 200°C, install temperature 20°C.
A106-B: $S_c = 138$ MPa, $S_h = 124$ MPa.

Suppose thermal solve produces:
- In-plane moment $M_i = 8500$ N·m
- Out-of-plane moment $M_o = 1200$ N·m
- Torsion $M_t = 3500$ N·m

In-plane SIF $i_i = 2.28$, out-of-plane $i_o = 0.75/h^{2/3} = 1.90$.

$$S_b = \frac{2.28 \cdot 8500 + 1.90 \cdot 1200}{1.40\times10^{-4}} = \frac{19380 + 2280}{1.40\times10^{-4}} = 154.7~\text{MPa}$$

$$S_t = \frac{3500}{2 \cdot 1.40\times10^{-4}} = 12.5~\text{MPa}$$

$$S_E = \sqrt{154.7^2 + 4 \cdot 12.5^2} = \sqrt{23932 + 625} = 156.7~\text{MPa}$$

Allowable:
$$S_A = 1.0 \cdot [1.25 (138 + 124) - 47.9] = 327.5 - 47.9 = 279.6~\text{MPa}$$

Stress ratio $= 156.7 / 279.6 = 0.56$. **Pass.**

## 5. Pressure design — wall thickness (Eq. 3a/3b)

Outside the stress analysis itself, B31.3 also requires a minimum wall
thickness for pressure containment:

$$t = \frac{P D}{2 (S E + P Y)}$$

with:
- $S$ — allowable stress at design temperature
- $E$ — quality (joint efficiency) factor (0.85 for ERW, 1.0 for seamless)
- $Y$ — temperature-dependent coefficient (0.4 for ferritic ≤482°C)

This is the **Barlow's formula** with refinements. pypemesh checks this
on every pipe element as a separate "pressure design" gate (red-flag
warning if violated, even if stress analysis passes).

## 6. Allowable stress derivation — where $S_h$ comes from

ASME Section II Part D's allowable stress is the lowest of:

1. $\sigma_u / 3.5$ (3.5× ultimate strength at temp)
2. $\sigma_y / 1.5$ (1.5× yield strength at temp)
3. $\sigma_R^{100k}$ (stress to rupture in 100,000 hours of creep)
4. $\sigma_{1\%}^{100k}$ (stress to give 1% creep strain in 100,000 h)
5. $\sigma^{100k} / 1.5$ (creep stress / 1.5)

For low-temperature service: items 1 and 2 dominate. For high-temperature
(>425°C for carbon steel, higher for alloys): items 3-5 dominate.

The factor 3.5 (changed from 4.0 in 1999) reflects modern materials science
and statistical confidence.

## 7. Differences across the B31 family

| Code | Sustained allow | Expansion allow | Occasional factor |
|---|---|---|---|
| **B31.3** (Process) | $S_h$ | $1.25(S_c+S_h) - S_L$ | $1.33 S_h$ wind, $1.20 S_h$ seismic |
| B31.1 (Power) | $S_h$ | $f[1.25 S_c + 0.25 S_h]$ | $1.15 S_h$ |
| B31.4 (Liquid Pipe) | $0.75 S_y$ | $0.72 S_y$ | $0.75 S_y \cdot 1.33$ |
| B31.8 (Gas Pipe) | $0.72 S_y$ (Class 1, Div 1) | $0.72 S_y$ | various |

Notice: process piping (B31.3) is **stress-based**, pipeline (B31.4/8) is
**yield-based**. Different philosophies, different allowables. pypemesh
implements each separately — they are not equivalent.

## 8. Dynamic combinations

For dynamic analysis, B31.3 §301.5.3 says occasional load factor applies:
$$S_{\text{dyn}} \leq 1.33 S_h$$

Response-spectrum results combine via SRSS, CQC, or ABS (see
DYNAMIC_ANALYSIS.md). Time-history results are evaluated at peak.

## 9. Special cases pypemesh handles

### 9.1 Reinforced branch connections

B31.3 §304.3 has full reinforcement equations. pypemesh evaluates them
when the user defines a reinforced tee.

### 9.2 Mitered bends

B31.3 §304.2.3 — different SIF, lower flexibility than fabricated elbow.

### 9.3 Anchor displacements

B31.3 §319.5 — settlement, vessel growth — same expansion stress
equation, but with imposed displacement instead of thermal.

### 9.4 Plastic piping (Chapter VII)

B31.3 Chapter VII — different allowables for HDPE/PE100, FRP. pypemesh
B.1 phase only; data sources require manufacturer cooperation.

## 10. The pypemesh implementation

```python
# pypemesh-core/codes/b31_3.py (sketch)

class B31_3(CodeCheck):
    code_id = "B31.3"
    version = "2022"

    def evaluate(self, model, results) -> list[CodeResult]:
        out = []
        for combo in model.load_combinations:
            for elem in model.elements:
                stress, allow, eq = self._dispatch(combo.category, elem, results)
                ratio = stress / allow
                status = "pass" if ratio <= 1.0 else "fail"
                out.append(CodeResult(
                    element_id=elem.id,
                    combination_id=combo.id,
                    stress=stress,
                    allowable=allow,
                    ratio=ratio,
                    status=status,
                    equation_used=eq,
                ))
        return out

    def _dispatch(self, category, elem, results):
        if category == "sustained":
            return self._eq_23a(elem, results)
        elif category == "occasional":
            return self._eq_23b(elem, results)
        elif category == "expansion":
            return self._eq_17(elem, results)
        elif category == "operating":
            return self._eq_op(elem, results)
        else:
            raise ValueError(f"Unknown category: {category}")
```

Each `_eq_*` method maps directly to the equation derivations above. Every
equation has a unit test against the example calculation in this doc.

## 11. Validation references

The pypemesh B31.3 implementation must match:

- **B31.3 Appendix S sample problem**: ASME publishes worked stresses
  for a specific model. Our output: within 1% of every node's stress.
- **Becht textbook example**: Becht's *Process Piping* book has a
  worked example we encode and validate.
- **Caesar II output on 20 reference models**: cross-check.

See `docs/VALIDATION_PLAN.md` Layer 5.

## References

[1] ASME B31.3-2022 (2022). *Process Piping*. ASME.

[2] ASME B31J-2017 (2017). *Stress Intensification Factors, Flexibility Factors, and Sustained Stress Indices for Metallic Piping Components*. ASME.

[3] Becht, C. (2013). *Process Piping: The Complete Guide to ASME B31.3* (3rd ed.). ASME Press. (the "Becht book")

[4] Markl, A. R. C. (1952). "Fatigue Tests of Piping Components". *Trans. ASME*, 74, 287–303.

[5] Markl, A. R. C., & George, H. H. (1950). "Fatigue Tests on Flanged Assemblies". *Trans. ASME*, 72, 77–87.

[6] ASME Section II Part D (current edition). *Properties (Metric)*. ASME. (Allowable stress tables.)

[7] Peng, L.-C., & Peng, T.-L. (2009). *Pipe Stress Engineering*. ASME Press. (Ch. 5–6)

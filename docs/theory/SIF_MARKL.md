# Stress Intensification Factors — Markl's Experiments and B31J

**Scope:** The experimental and theoretical basis of the Stress
Intensification Factor (SIF) used by every pipe stress code on Earth.
Without Markl's 1952 paper, modern pipe stress engineering would not exist.

## 1. The problem Markl set out to solve

By the late 1940s, designers of process piping had a problem. Beam theory
predicted stress at a fitting (elbow, tee, branch connection) accurately
when bending was static. But fittings *failed in fatigue* at much lower
loads than beam theory predicted. The geometry was concentrating stress in
ways the calculations missed.

Engineers needed a single multiplier they could apply to nominal beam
stress to get the actual peak stress at a fitting — calibrated to *fatigue
failure*, not static yield.

A.R.C. Markl at Tube Turns (a fittings manufacturer) ran the definitive
experiments.

## 2. The experimental setup

Markl built a cantilever-style fatigue rig. A test fitting (elbow, tee,
nipple) was welded onto a long pipe. The free end was driven with a known
oscillating displacement that produced a known nominal bending stress range
$S$ at the fitting.

The fitting was cycled until it cracked through the wall. The number of
cycles to failure $N$ was recorded.

Hundreds of fittings tested across:
- Elbows: SR, LR, mitered (1, 2, 3-segment)
- Tees: welded, sockolet, weldolet, reinforced
- Reducers: concentric, eccentric
- Nipples, flanges, bends with various radius ratios

## 3. The reference baseline — straight pipe girth weld

Every test was normalized to a baseline: the **fatigue life of a straight
pipe with a girth-butt weld**, which Markl had separately characterized.
Markl's empirical fit:

$$i \cdot S = 245{,}000 \cdot N^{-0.2}$$

(in psi units), where $S$ is the actual stress range applied to the
fitting and $N$ is cycles to failure.

By definition, the baseline straight-pipe girth weld has **$i = 1$**.

So **SIF $i$ for a fitting** = (stress range that fatigues a girth weld
in $N$ cycles) / (stress range that fatigues this fitting in the same $N$
cycles).

A fitting with $i = 2$ fails in the same number of cycles at half the
applied stress. A fitting with $i = 1$ matches a plain girth weld.

## 4. The empirical SIF formulae

From the experimental data, Markl proposed:

### 4.1 Pipe bend (elbow, in-plane bending)

$$i_i = \frac{0.9}{h^{2/3}}$$

where the **flexibility characteristic** is:
$$h = \frac{tR}{r^2}$$

with $t$ = wall thickness, $R$ = bend radius, $r$ = mean pipe radius.

Out-of-plane bending: $i_o = 0.75/h^{2/3}$.

### 4.2 Welded tee

In-plane: $i_i = 0.9 (h)^{-2/3}$ where $h = 4.4 t / r$ for a butt-welded tee.

Out-of-plane: $i_o \approx 0.75 i_i$.

### 4.3 Reducer

$i \approx 2.0$ (concentric, eccentric).

These are *empirical fits to fatigue test data*. They are not analytical
derivations from elasticity theory. ASME adopted them in B31.3 Appendix D
in the 1955 edition, and they remained essentially unchanged for 60 years.

## 5. The 2017 update — B31J

Three problems with Markl's original tables motivated a major update:

1. **Modern materials** behave differently (Markl tested 1940s carbon steels).
2. **Welded tees** have evolved (better quality control, different procedures).
3. **Sustained stress** isn't the same as fatigue stress — Markl tested
   fully-reversed cyclic loading; sustained loading concentrates stress
   differently.

The Pressure Vessel Research Council (PVRC) sponsored a multi-decade
effort that produced **ASME B31J-2017** ("Stress Intensification Factors,
Flexibility Factors, and Sustained Stress Indices for Metallic Piping
Components"). B31J:

- Replaces the simple $i = 0.9/h^{2/3}$ formulas with **finite-element-
  derived tables** for ~50 fitting geometries
- Distinguishes **fatigue SIF** ($i$, used in expansion check) from
  **sustained stress index** ($i_s$, used in sustained check)
- Provides separate **flexibility factors** $k_x$, $k_y$, $k_z$ for each
  axis (Markl assumed isotropic)
- Adds **branch-side and run-side** SIFs for tees (Markl gave one number)

The B31J tables come from Wais, Rodabaugh, and other PVRC researchers.
They're more accurate for modern fittings but more complex to use.

## 6. SIF in pypemesh

```python
# pypemesh-core/codes/b31j.py (sketch)

from dataclasses import dataclass

@dataclass
class FittingSIF:
    fitting_type: str       # "elbow_lr", "tee_welding", etc.
    i_in_plane: float
    i_out_of_plane: float
    i_torsion: float
    sustained_index: float  # B31J SSI
    flexibility_factor: float
    source: str             # "B31J-2017" or "Markl-1952"

def lookup_sif(fitting_type: str, geometry: dict) -> FittingSIF:
    """Look up SIF from B31J tables; fall back to Markl formulas."""
    ...
```

Every fitting in the model carries its `FittingSIF`. The code-check module
applies the appropriate $i$ to bending moments. The output report shows
which SIF source (B31J or Markl) was used and why.

For new fittings without B31J coverage, pypemesh refuses to silently use
Markl — the user must explicitly accept the older formula and acknowledge
the assumption.

## 7. Flexibility factor — companion to SIF

The same Karman ovalization that concentrates stress also makes the
fitting more flexible. Flexibility factor $k$ multiplies the local
flexibility (compliance):

$$k = \frac{1.65}{h}$$

For an LR elbow with $h = 0.247$ (from PIPE_MECHANICS.md): $k = 6.68$.

The flexibility factor goes into the **stiffness matrix** (the elbow
element is 6.68× more compliant in bending than a straight beam of the
same dimensions). The SIF goes into the **stress recovery** (the recovered
moment at the elbow gets multiplied by 2.28 for outer-fibre stress).

These are two sides of the same physical effect (ovalization) showing up
in two different solver stages. Both must be applied — using $k$ without
$i$ underpredicts stress; using $i$ without $k$ overpredicts displacement.

## 8. The deep insight: why SIF is "fatigue-calibrated"

A subtle but important point: Markl's SIF is **calibrated to give the
right fatigue life when used in beam theory**.

It is NOT the actual local-stress concentration factor (which would come
from FEA). The actual peak stress at an elbow's outer fibre might be
3-4× nominal, but Markl's SIF is 2-3× nominal.

The reason: Markl's tests used *fully-reversed* loading. The real local
stress at peak loading enters the plastic regime and shakes down. After a
few cycles, the elastic stress range stabilizes at a lower value than the
true peak. Markl's SIF captures this *post-shakedown effective stress*.

This means:
- For **fatigue analysis** (cyclic loading), Markl/B31J SIF is correct.
- For **static strength** (one-shot loading), it overpredicts the
  effective stress (which is why ASME multiplies by 0.75 in the sustained
  equation).
- For **true peak stress** (e.g., for local FEA), use a higher value from
  finite-element analysis (FEPipe or our local-FEA module).

This three-way distinction — fatigue, sustained, peak — is what B31J
codified explicitly. Older codes blurred it.

## 9. Validation against Markl

pypemesh's validation suite includes a benchmark that **runs Markl's
fatigue equation backwards**. For each fitting type:

1. Apply nominal stress range $S_{nom}$
2. Apply pypemesh-computed SIF $i$
3. Compute "Markl life": $N = (245{,}000 / (i \cdot S_{nom}))^{1/0.2}$
4. Verify $N$ matches Markl's reported life within 15% (experimental scatter)

This proves not just our code arithmetic but the *physical interpretation*
of SIF. See `benchmarks/markl_fatigue/`.

## 10. SIF for non-Markl fittings — the gap

Markl tested standard fittings of his era. Modern systems include:

- **3D printed fittings** — no Markl test data
- **Composite (FRP) elbows** — no Markl test data
- **Sockolets and Weldolets** under torsion — Markl tested only bending

For these, B31.3 §319.3.6 allows the user to compute SIF from finite
element analysis or from manufacturer testing. pypemesh's local-FEA
module (Phase B.2) generates SIF from auto-meshed shell models for
custom fittings — the same approach FEPipe takes.

## 11. The pedagogical example

Why does an LR elbow need 6.7× more flexibility than a straight pipe? Run
this thought experiment:

1. Imagine a long-radius elbow as a thin-walled tube curved into a quarter
   circle.
2. Apply an in-plane bending moment $M$ at one end, fixed at the other.
3. The inner side of the curve must compress (fibres on the small-radius
   side go shorter); the outer side must stretch.
4. But the tube can't compress and stretch axisymmetrically — the
   cross-section deforms from circular to oval. The "in-plane diameter"
   shrinks; the "out-of-plane diameter" grows.
5. This ovalization makes the cross-section much less stiff to bending
   than it would be if it stayed circular.
6. Net result: the elbow rotates much more for the same $M$ than a
   straight tube of equal length and section properties would.

Karman quantified this with energy methods. Modern FEA confirms his result
to <2%. The ovalization angle is largest at the elbow midpoint and tapers
to zero at the ends (where the connecting straight pipe enforces a
circular section).

Stress concentration at the inner-bend fibre comes from the same
ovalization — that fibre's strain is amplified relative to what beam
theory predicts. The SIF captures this stress amplification.

## References

[1] **Markl, A. R. C. (1952). "Fatigue Tests of Piping Components".** *Trans. ASME*, 74, 287–303. *(The foundational paper.)*

[2] Markl, A. R. C., & George, H. H. (1950). "Fatigue Tests on Flanged Assemblies". *Trans. ASME*, 72, 77–87.

[3] George, H. H., & Rodabaugh, E. C. (1956). "Stress indices for ASME Code calculations". *ASME Pressure Vessel and Piping Conference*.

[4] Rodabaugh, E. C. (1987). "Accuracy of Stress Intensification Factors for Branch Connections". *WRC Bulletin*, 329.

[5] Wais, E. A., et al. (2014). "Development of B31J — Stress Intensification Factors and Flexibility Factors for Metallic Piping Components". *PVP2014-28220, ASME PVP Conference*.

[6] **ASME B31J-2017 (2017). *Stress Intensification Factors, Flexibility Factors, and Sustained Stress Indices for Metallic Piping Components*. ASME.** *(Current SIF standard.)*

[7] Dodge, W. G., & Moore, S. E. (1972). "Stress indices and flexibility factors for moment loadings on elbows and curved pipe". *ORNL-TM-3658*.

[8] Peng, L.-C. (2009). *Pipe Stress Engineering*. ASME Press. Ch. 4 & Appendix.

[9] WRC Bulletin 537 (2010). *Local Stresses in Cylindrical Shells Due to External Loadings on Nozzles* (replaces WRC 107/297).

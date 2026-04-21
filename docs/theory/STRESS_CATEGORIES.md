# ASME Stress Categories — Primary, Secondary, Peak

**Scope:** The classification system that underpins every ASME pressure-piping
and pressure-vessel code. Without understanding this taxonomy, you cannot
read or apply B31.3 (or any sister code) correctly.

> Why this matters: a 100% sustained stress is *failure*. A 100% expansion
> stress is *fine*. A 100% peak stress *might* be fine or fatigue-failed
> depending on cycle count. Same stress *number*, different physical meaning,
> different consequences. The category is everything.

## 1. The fundamental insight

A pipe carries different *kinds* of stress depending on where the load
ultimately comes from. ASME — through landmark work by W.E. Cooper and
others on the original ASME Section III in the 1960s — recognized that:

- **Force-controlled loads** (gravity, pressure) generate stress that
  *cannot relax*. If the stress exceeds yield, the pipe collapses.
- **Displacement-controlled loads** (thermal expansion, support settlement)
  generate stress that *self-relieves* through plastic deformation. The
  pipe doesn't collapse; it accommodates by yielding once, then stays put.

These two situations need *fundamentally different allowable stresses*.
Force-controlled needs a safety margin against catastrophic yield.
Displacement-controlled needs a safety margin against fatigue from cyclic
yield-and-spring-back.

This is the basis of the primary/secondary/peak classification.

## 2. Primary stress

**Definition:** Stress required to maintain equilibrium with externally
applied mechanical loads (pressure, weight, wind, seismic inertia).

**Key property:** Cannot self-relieve. If the material yields, the load is
*still there* and continues to drive deformation until rupture.

**Subcategories:**

### 2.1 Primary general membrane ($P_m$)

Average stress across the section, far from discontinuities. Hoop stress
from internal pressure away from a nozzle is the canonical example.

**Allowable:** $S_m$ (design stress intensity, ~$2/3$ of yield for most
ductile materials).

### 2.2 Primary local membrane ($P_L$)

Membrane stress in a localized region (near a nozzle, support, etc.).

**Allowable:** $1.5 S_m$ (the higher allowable recognizes that the local
region can shed load to surrounding material).

### 2.3 Primary bending ($P_b$)

Linear stress distribution from an applied moment (wind, dead weight,
hanging valve weight). Not sustained pressure.

**Allowable:** $1.5 S_m$ for $P_b$ alone; $1.5 S_m$ also for $P_L + P_b$
combined.

### 2.4 In B31.3 terms

Primary stresses are checked under the **Sustained** category (W + P)
and **Occasional** category (W + P + wind, seismic). The B31.3 sustained
stress equation 23a evaluates these. The allowable is the hot allowable
$S_h$ (ASME's sustained allowable, derived to give ~3:1 against yield and
~4:1 against ultimate at temperature).

## 3. Secondary stress

**Definition:** Stress arising from constraint of free thermal expansion or
imposed displacements (settlement, anchor movement). Self-relieving.

**Key property:** Plastic deformation of a small region locally relieves
the stress. The pipe doesn't fail catastrophically — it accommodates,
typically through a small permanent set on the first cycle and elastic
behavior thereafter (if cycle range stays elastic — *shakedown*).

### 3.1 Why secondary stress can exceed yield safely

Imagine a pipe perfectly anchored at both ends, heated 200°C above install.
Free thermal growth would give $\varepsilon = \alpha \Delta T = 11.5\times10^{-6} \cdot 200 = 0.0023$.

Constrained, this would generate stress $\sigma = E\varepsilon = 2\times10^{11} \cdot 0.0023 = 460$ MPa, well above yield (~250 MPa).

But here's the magic: as soon as $\sigma$ reaches yield, the material
plastically strains *just enough* to absorb the constraint mismatch. The
stress drops to yield. When the pipe later cools, it springs back through
that same plastic strain. The remaining elastic strain stays within
$[-\sigma_y, +\sigma_y]$.

The pipe has **shaken down to a stable elastic cycle**. It will not fail
unless the cycle is repeated thousands of times (then fatigue takes over).

### 3.2 Shakedown criterion

Bree (1967) showed the shakedown limit is when total stress range stays
within $2\sigma_y$ — twice the yield stress. ASME generalizes this:
$$S_{\text{secondary range}} \leq 2 S_y \approx 3 S_m$$

This is why B31.3 allows a **higher allowable for thermal (expansion)
stresses** than for sustained stresses — explicitly accepting that initial
yielding is OK if shakedown is achieved.

### 3.3 In B31.3 terms

Secondary stresses are checked under the **Displacement (Expansion)**
category. The B31.3 expansion stress equation 17 evaluates these. The
allowable is:
$$S_A = f \left[1.25 (S_c + S_h) - S_L \right]$$

where $f$ is a fatigue cycle factor (1.0 for ≤7000 cycles), $S_c$ is cold
allowable, $S_h$ is hot allowable, $S_L$ is sustained stress.

The **liberal allowable** form lets unused sustained-stress margin be
recovered for expansion: a pipe with low sustained stress (light, low
pressure) gets more thermal allowable than one already loaded to its
sustained limit.

## 4. Peak stress

**Definition:** The highest local stress, including stress concentrations
at notches, welds, fillets, threads. Used only for **fatigue analysis**.

**Key property:** Peak stress alone doesn't fail anything statically. Its
only role is in cyclic fatigue calculations: count cycles, compare against
S-N curve.

In piping, the SIF (Stress Intensification Factor — see SIF_MARKL.md)
captures the peak/nominal stress ratio at fittings.

**Allowable:** Determined by S-N (stress-cycle) fatigue curves, e.g.:
- ASME Section VIII Div 2 mandatory Appendix 5
- ASME B31.3 Markl-type curves (built into SIF tables)

## 5. The three-circle stress visualization

ASME shows stress categories on a "three-circle" diagram (Hopper's diagram
or similar):

```
   PEAK
    ●  (allowable: fatigue curve)
   ╱
  ╱  SECONDARY
 ╱     ●  (allowable: 3 S_m, shakedown)
╱     ╱
●━━━━╱
PRIMARY
●  (allowable: S_m or 1.5 S_m)
```

Allowables increase as you move from primary to secondary to peak —
because the consequence of exceeding each becomes less catastrophic.

## 6. Mapping to B31.3 piping practice

| Load category | Loads included | Code equation | Stress symbol | Allowable |
|---|---|---|---|---|
| Sustained | Weight + Pressure (acting all the time) | 23a | $S_L$ | $S_h$ |
| Occasional | Sustained + (wind OR seismic OR water hammer) | 23b | $S_O$ | $1.33 S_h$ |
| Displacement (Expansion) | Thermal (T2 - T1) + anchor movement | 17 | $S_E$ | $S_A$ |
| Operating | Sustained + thermal (T_op condition) | (informational) | $S_{op}$ | $3 S_h$ practical |

Each combination gets its own check. A pipe must pass *all* applicable
categories.

## 7. The non-obvious case: occasional-plus-thermal

What about an earthquake during operation? The pipe is already at
operating temperature (thermal stress present), and now wind or seismic
adds. Two schools of thought:

- **Older Caesar II practice**: combine occasional and expansion
  conservatively (algebraic add).
- **AutoPIPE load sequencing**: the pipe has already shaken down by the
  time the earthquake hits, so secondary thermal stress is *not* additive
  to primary occasional stress. Only primary sustained + occasional must
  be checked against $1.33 S_h$.

Modern ASME practice supports the load-sequencing view. pypemesh defaults
to load sequencing (AutoPIPE-style) but supports legacy load combination
mode for users migrating from Caesar II.

## 8. Where this lives in pypemesh

In `pypemesh-core/codes/base.py` we define:

```python
class StressCategory(str, Enum):
    SUSTAINED = "sustained"
    OCCASIONAL = "occasional"
    EXPANSION = "expansion"
    OPERATING = "operating"
    FATIGUE = "fatigue"
```

Each `LoadCombination` has a `category`. The code-check module routes the
combined stress to the appropriate allowable equation. The output report
labels each stress with its category so the engineer can see at a glance
what kind of failure mode each ratio represents.

## 9. The mistakes engineers make (and we prevent)

1. **Treating thermal as primary.** Common in undergraduate courses. Leads to over-conservative designs by 100%+.
2. **Adding all loads regardless of category.** Conservative but unphysical. Wastes pipe and supports.
3. **Ignoring thermal entirely.** Leads to support failures and pipe rupture in long runs.
4. **Treating peak stress as primary.** Leads to over-designed fittings.
5. **Mixing static and dynamic into the same category.** Caesar II legacy mode does this; load sequencing fixes it.

pypemesh's UI explicitly labels load cases with their category and refuses
to combine across categories silently — every cross-category combination
is an explicit user choice with a warning.

## References

[1] ASME Boiler and Pressure Vessel Code, Section III, Subsection NB, Appendix XIII (1969 origin, current edition).

[2] Cooper, W. E. (1962). "The use of plastic analysis in pressure vessel design". *J. Engineering for Industry*, 84(1), 67–73.

[3] Bree, J. (1967). "Elastic-plastic behaviour of thin tubes subjected to internal pressure and intermittent high-heat fluxes". *J. Strain Analysis*, 2(3), 226–238.

[4] ASME PTB-1 (2014). *ASME Section VIII, Division 2 Criteria and Commentary*. ASME. (The "yellow book" explaining categories.)

[5] Becht, C. (2013). *Process Piping: The Complete Guide to ASME B31.3* (3rd ed.). ASME Press. (Ch. 4)

[6] Peng, L.-C., & Peng, T.-L. (2009). *Pipe Stress Engineering*. ASME Press. (Ch. 5)

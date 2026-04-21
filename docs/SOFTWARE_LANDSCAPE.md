# Software Landscape — Complete Piping Industry Survey

**Version:** 0.1
**Status:** Authoritative market reference. Every pypemesh capability decision references this doc.
**Last refreshed:** 2026-04-20

> Goal: catalog **every** software product used anywhere in the piping design
> and analysis workflow, classify by category, and identify the specific
> capabilities pypemesh must absorb to be a credible replacement.

## How this doc is organized

Eight categories. For each tool: vendor, price tier, market position, core
capabilities, unique strengths, weaknesses, and what pypemesh takes from it.

1. Pipe stress analysis (core category)
2. Local FEA / pressure vessel
3. Flow & hydraulic analysis
4. Process simulation
5. 3D plant design / CAD
6. Pipeline (long-distance transport)
7. Isometric / drafting / deliverables
8. Support design & specialty

---

## 1. Pipe Stress Analysis — our primary category

### 1.1 CAESAR II (Hexagon PPM / Intergraph)

- **Since:** 1984. The industry's de facto standard.
- **Price:** $15,000-30,000/seat/year (Advanced tier up to $50K)
- **Market:** Global leader. ~50-60% market share in EPC firms worldwide.
- **Core capabilities:**
  - Static + dynamic (seismic, wind, water hammer, response spectrum, harmonic, time history)
  - 30+ piping codes including ASME B31.1/3/4/5/8/9/11/12, nuclear ASME Section III, EN 13480, BS 806, CSA, Z662, Stoomwezen
  - Non-linear: gaps, friction, one-way restraints, bilinear soil (underground)
  - Buried pipe (soil-pipe interaction with API 1102, PRCI)
  - Flange analysis (Kellogg, NC-3658, ASME-equivalent)
  - WRC-107/297/537 local stress
  - Built-in B31J SIF (2017+)
  - Fatigue analysis (ASME VIII Div 2, BS 5500)
  - Spectrum library (UBC, ASCE, IBC, nuclear)
- **Unique strengths:**
  - Largest talent pool (every pipe stress engineer has used it)
  - CADWorx/SmartPlant/PDS native integration
  - Unmatched breadth of codes
  - FEPipe plugin for local FEA
- **Weaknesses:**
  - Spreadsheet-only input (steep learning curve, ~3-6 months to proficiency)
  - Undo stack lost on exit (no persistent undo)
  - No plastic/HDPE native support (big gap for water/gas utility)
  - UI unchanged since ~2005
  - No cloud / no collaboration
  - Load combinations require intermediate L3 equations (verbose outputs)
  - Expensive
- **pypemesh takes:** code breadth, spectrum library approach, WRC local checks, burial soil model, CADWorx PCF interop, dynamic analysis feature set.

### 1.2 AutoPIPE (Bentley Systems, formerly Rebis)

- **Since:** 1986
- **Price:** $10,000-25,000/seat/year (Standard/Advanced/Nuclear tiers)
- **Market:** #2 global, dominant in North America, Bentley-standardized EPCs.
- **Core capabilities:**
  - Load sequencing solver (AutoPIPE's killer differentiator — see below)
  - HDPE, FRP, GRE, non-metallic plastic piping support
  - 30+ codes, nuclear Section III Class 1/2/3
  - Dynamic: response spectrum, time history, harmonic, SAM (Site-Specific)
  - Non-linear with no iteration convergence problems (load sequencing advantage)
  - ML-powered **Support Optimizer** in Advanced tier (evaluates 10,000+ configurations)
  - Integrated AutoPIPE Vessel for PV
  - Bidirectional link to STAAD.Pro (structure-pipe coupling)
  - Bentley iModel cloud sync
  - 99-level undo/redo persistent across sessions
  - Graphical CAD-like input
- **Unique strengths:**
  - **Load sequencing**: no intermediate L-equations, cleaner reports, more physically accurate non-linear convergence
  - ML support optimizer (5-10 years ahead of everyone)
  - Native plastic support
  - Bentley ecosystem (OpenPlant, MicroStation, STAAD)
  - Nuclear tier validated for ASME Section III
- **Weaknesses:**
  - Smaller global talent pool than Caesar II
  - Bentley ecosystem lock-in
  - Cloud is iModel-specific (not a general web app)
  - Price tier jumps aggressive ($10K Standard to $25K Advanced)
- **pypemesh takes:** **load sequencing as the default solver mode**, ML support optimizer concept, plastic support native, 99-level undo, graphical input.

### 1.3 CAEPIPE (SST Systems)

- **Since:** ~1985
- **Price:** $5,000-10,000/seat/year (roughly 1/3 of Caesar II)
- **Market:** Mid-size firms, rapid modeling, consultants.
- **Core capabilities:**
  - Static + modal + response spectrum
  - ASME B31.1/3/5/8, EN 13480, Swedish SSP, Chinese GB, Japanese JPI
  - Support optimization (simpler than AutoPIPE, rule-based)
  - Buried pipe
  - WRC-107
  - User-definable materials
  - Integrated CAEPIPE/ROHR import
- **Unique strengths:**
  - **Simplest UI in the market** — point-and-click, windowed, clean
  - Fast modeling (claimed 3-5x faster than Caesar II for same model)
  - Cost-effective
  - Intuitive defaults
  - Fast learning curve (~days, not months)
- **Weaknesses:**
  - Smaller code coverage than Caesar/AutoPIPE
  - No time history dynamics
  - No nuclear
  - Smaller material library
  - No plastic support
  - Not widely supported in EPC specs (some buyers require Caesar output)
- **pypemesh takes:** **UI philosophy** — CAEPIPE's ease-of-use is our north star. Sensible defaults. Fast modeling.

### 1.4 START-PROF (PASS Engineering)

- **Since:** 1965 (oldest piping software still sold)
- **Price:** $4,000-8,000/seat/year (half of Caesar II)
- **Market:** Growing from Russia, now worldwide; oil & gas, district heating, pipeline.
- **Core capabilities:**
  - Static + dynamic (modal, response spectrum, seismic, wind, water hammer)
  - Buried pipe (best-in-class for pipelines)
  - Jacketed pipe, trunnions, dummy legs
  - Above-ground + underground mixed systems
  - ASME B31.1/3/4/5/8, Russian GOST, European EN, British BS
  - District heating specialty (pre-insulated bonded pipe systems)
  - Built-in B31J SIF
  - Over 15,000 materials
  - Pipeline crossings (road, river, fault)
  - Free student version with major capabilities
- **Unique strengths:**
  - Strongest in pipeline / oil & gas / district heating
  - Priced aggressively for emerging markets
  - PhD-level solver (Russian thermal mechanics tradition)
  - Pre-insulated pipe (polyurethane foam-bonded CS carrier pipe) models
- **Weaknesses:**
  - Smaller Western community / support
  - UI improving but still dated
  - Not widely on EPC specs
- **pypemesh takes:** buried pipe model, pipeline crossings, district heating / pre-insulated pipe support.

### 1.5 ROHR2 (SIGMA Ingenieurgesellschaft, Germany)

- **Since:** 1970s
- **Price:** €8,000-15,000/seat/year
- **Market:** European, particularly German-speaking countries; power, district heating.
- **Core capabilities:**
  - Static + dynamic
  - DIN/EN code compliance (strongest EN 13480 implementation)
  - Nuclear KTA (German nuclear code)
  - Buried / underground heating networks
  - Good 3D graphics
- **Unique strengths:**
  - Best German/European code coverage
  - KTA nuclear (Germany-specific)
  - Precision reporting expected by German power utilities
- **Weaknesses:**
  - Limited outside Europe
  - Mostly German documentation
- **pypemesh takes:** EN 13480 depth, KTA reference for future European nuclear, precision report formats.

### 1.6 TRIFLEX Windows (PipingSolutions / AVEVA)

- **Since:** late 1960s (originally TRIFLEX by Engineering Dynamics)
- **Price:** $10,000-20,000/seat/year
- **Market:** Legacy presence in big oil/chemical; smaller today.
- **Core capabilities:** Static + dynamic, most major codes, buried pipe.
- **Unique strengths:** Long oil & gas legacy; some specifications still mandate it.
- **Weaknesses:** UI decades behind; shrinking market share; ownership has changed hands.
- **pypemesh takes:** legacy code compatibility notes only.

### 1.7 PipePAK / PIPESTRESS (Intergraph → Hexagon)

- Historic. Some older projects still reference PIPESTRESS output. Essentially
  superseded by Caesar II within Hexagon's portfolio.
- **pypemesh takes:** ability to import legacy PIPESTRESS files (low priority).

### 1.8 NozzlePRO (Paulin Research Group)

- Technically a local-FEA tool but often bundled with stress workflows.
- See §2.1.

---

## 2. Local FEA / Pressure Vessel

### 2.1 FEPipe + NozzlePRO + FEATools (Paulin Research Group)

- **Since:** 1990s; Paulin Research Group founded 1978
- **Price:** $5,000-15,000/seat/year for full suite
- **Market:** The gold standard for local piping/vessel FEA.
- **Core capabilities:**
  - FEPipe: shell, brick, axisymmetric FEA for pressure vessels & piping components
  - Template-driven: auto-mesh for standard configs (nozzle-on-shell, tee, elbow, bolted flange)
  - Auto-generates ASME-compliant reports (WRC-107/297, ASME VIII Div 2 Part 5)
  - Handles weight, thermal, seismic, wind, fluid head, pressure
  - Integrates with Caesar II (loads from Caesar → FEPipe for local check)
  - NozzlePRO: simpler, nozzle-specific subset
  - FEATools: plugin for Caesar II that calls FEPipe in background
- **Unique strengths:**
  - Only tool that makes FEA accessible to non-FEA engineers
  - Template-based so users don't need ANSYS expertise
  - Standard reports that meet ASME certification
- **Weaknesses:**
  - Not a pipe stress tool (used as complement, not replacement)
  - Requires companion beam-element tool (Caesar II)
  - No cloud, no collaboration
- **pypemesh takes:** **template-driven local FEA** as the core paradigm for our Phase B.2 local-stress module. Auto-WRC reports.

### 2.2 PV Elite (Hexagon PPM)

- **Since:** 1982
- **Price:** $10,000-15,000/seat/year
- **Market:** #1 pressure vessel design tool globally.
- **Core capabilities:**
  - ASME VIII Div 1 & Div 2 vessel design
  - Heat exchanger (TEMA) design via companion Tank & Exchanger
  - Nozzle design per WRC, UG-37, Appendix 1-7
  - Flange design per ASME Appendix 2 and Kellogg
  - Wind, seismic, platforms
- **Unique strengths:** complete VIII Div 1/2 workflow, huge materials library, output accepted by most inspection authorities.
- **Weaknesses:** pressure vessel only, not piping.
- **pypemesh takes:** Appendix 2 flange method, material DB approach (not the tool itself — it's out of scope for pipe stress).

### 2.3 Compress (Codeware)

- ASME VIII Div 1 vessel design. Competitor to PV Elite.
- Priced $5,000-12,000/seat/year.
- **pypemesh takes:** nothing directly; reference for vessel edge-case handling.

### 2.4 AutoPIPE Vessel (Bentley)

- Vessel add-on to AutoPIPE. Competitor to PV Elite.
- **pypemesh takes:** the integration pattern (piping + vessel in one app).

### 2.5 ANSYS Mechanical / Ansys Piping

- **Since:** 1970
- **Price:** $20,000-50,000/seat/year (commercial); $0 research versions
- **Market:** General FEA powerhouse; used for the hard local cases.
- **Core capabilities:** Any geometry, full non-linear, plasticity, contact, large deformation, fatigue (FKM, ASME, BS), CFD coupling.
- **pypemesh takes:** **as escape valve** — export our model to ANSYS for the 1% of cases we can't handle. Validation cross-check reference.

### 2.6 Abaqus (Dassault), LS-DYNA (Ansys), NX Nastran (Siemens)

- General-purpose FEA. Same role as ANSYS for us: escape hatch for edge cases.

### 2.7 Simcenter Femap / Nastran (Siemens)

- Similar category, used in specific aerospace-adjacent piping.

---

## 3. Flow & Hydraulic Analysis

### 3.1 PIPENET (Sunrise Systems, UK)

- **Since:** 1980s
- **Price:** £8,000-20,000/seat/year
- **Market:** #1 for fire protection, transient hydraulic analysis.
- **Core capabilities:**
  - Steady-state flow networks (any fluid)
  - Transient (water hammer, pump trip, valve closure)
  - Fire protection module (NFPA sprinkler, deluge)
  - Offshore (spray, washdown)
  - Two-phase simple cases
- **Unique strengths:** transient analysis with force-time outputs that feed directly into pipe stress.
- **Weaknesses:** no structural, no stress analysis.
- **pypemesh takes:** **interface to PIPENET force-time output** so our dynamic solver consumes transient loads. Not re-implementing hydraulics.

### 3.2 AFT Fathom / AFT Impulse / AFT Arrow (Applied Flow Technology)

- Fathom: steady-state incompressible. Impulse: transient. Arrow: compressible gas.
- Price: $8,000-15,000/module/year.
- Strong US market, well-regarded UI.
- **pypemesh takes:** AFT Impulse export format support.

### 3.3 FluidFlow (Flite Software)

- Steady-state + simple transient.
- Cheap ($2,000-5,000/year), popular with smaller firms.
- **pypemesh takes:** file format read.

### 3.4 KYPipe / KYWH (University of Kentucky)

- Academic-origin tool, cheap license. Water utility networks.
- **pypemesh takes:** nothing directly.

### 3.5 HAMMER (Bentley)

- Water hammer for water utilities. Bentley stack integration.
- **pypemesh takes:** integration pattern reference.

### 3.6 PIPESIM (Schlumberger, now SLB)

- Multiphase flow for oil & gas production networks.
- **pypemesh takes:** nothing directly — upstream of our scope.

### 3.7 OLGA (SLB / Schlumberger)

- Multiphase transient pipeline flow. The gold standard for subsea.
- **pypemesh takes:** slug flow force data import (rare case).

### 3.8 Flowmaster (Mentor / Siemens), Flownex (M-Tech Industrial)

- 1D thermofluid simulators. Wider than pipe stress scope.
- **pypemesh takes:** nothing directly.

### 3.9 Aspen HYSYS Hydraulics, Aspen Pipeline Hydraulics

- Process-to-pipe boundary condition handoff.
- **pypemesh takes:** see §4.1.

---

## 4. Process Simulation

### 4.1 Aspen HYSYS (AspenTech)

- **Since:** 1990s (merged with HYSIM + HYSYM)
- **Price:** $30,000-60,000/year (process licensing)
- **Market:** #1 process simulator in refineries / gas plants.
- **Role in piping workflow:** produces the temperature/pressure boundary
  conditions that pipe stress engineers need. Every stress model starts with
  HYSYS output.
- **pypemesh takes:** **HYSYS line list import** — parse HYSYS stream reports
  (temperature, pressure, density, flow) and auto-populate pipe conditions.
  This alone saves 10-20 hours per project.

### 4.2 Aspen Plus (AspenTech)

- Sister product to HYSYS, chemical processes.
- Same integration pattern as HYSYS.

### 4.3 UniSim Design (Honeywell)

- HYSYS-like; similar interop pattern.

### 4.4 ProMax (Bryan Research & Engineering)

- Gas processing focus; popular in North American upstream.

### 4.5 CHEMCAD (Chemstations)

- Mid-market process sim.

### 4.6 PRO/II (AVEVA, formerly SimSci)

- Classic process simulator, refinery-focused.

### 4.7 Symmetry (Schlumberger)

- Upstream hydrocarbon flow assurance.

**pypemesh takes:** unified **line list import adapter** that reads any of
HYSYS/Plus/UniSim/ProMax/CHEMCAD export formats and produces a pypemesh
starting model with T/P/medium populated.

---

## 5. 3D Plant Design / CAD

### 5.1 AVEVA PDMS / Everything3D (E3D, now AVEVA Engineering)

- **Since:** PDMS 1976, E3D 2010s
- **Price:** Enterprise (six-figure+ per site)
- **Market:** Dominant in European/Asian EPC for large plants.
- **Core capabilities:** 3D plant modeling, spec-driven piping, steel, equipment, HVAC.
- **Integration:** PCF export (standard), PDMS/E3D-specific adapters.
- **pypemesh takes:** PCF import at minimum; direct E3D adapter later (enterprise sale).

### 5.2 SmartPlant 3D / S3D (Hexagon PPM, formerly Intergraph)

- **Since:** late 1990s
- **Price:** Enterprise
- **Market:** Dominant in US EPC; competes directly with PDMS.
- **pypemesh takes:** PCF import; SmartPlant native adapter (commercial tier).

### 5.3 CADWorx Plant / CADWorx Structure (Hexagon, formerly Coade)

- **Since:** 1990s
- **Price:** $5,000-15,000/seat
- **Market:** AutoCAD-based 3D plant, mid-size firms.
- **Core capabilities:** AutoCAD plugin for 3D piping, spec-driven, direct Caesar II export.
- **Integration:** Caesar II ecosystem standard; we must read CADWorx output.
- **pypemesh takes:** CADWorx PCF + XML round-trip.

### 5.4 AutoCAD Plant 3D (Autodesk)

- Plant module on AutoCAD, spec-driven piping.
- Common in mid-market.
- **pypemesh takes:** AutoCAD Plant 3D PCF, XML project file read.

### 5.5 OpenPlant (Bentley, formerly Hevacomp / AEC)

- Bentley's answer to SmartPlant/PDMS. MicroStation-based.
- Integrates with AutoPIPE natively.
- **pypemesh takes:** PCF via OpenPlant; iModel connector as stretch goal.

### 5.6 Revit MEP (Autodesk)

- BIM-focused, building services. Some MEP piping.
- Not mainstream for industrial; relevant for buildings.
- **pypemesh takes:** light integration (export IFC from pypemesh to Revit coordination models).

### 5.7 SolidWorks Routing (Piping) (Dassault)

- Mechanical CAD with piping module. Popular in equipment skid design.
- **pypemesh takes:** **SolidWorks plugin that exports pipe geometry** for stress analysis — a major differentiator since Caesar/AutoPIPE don't have this natively.

### 5.8 CATIA Piping (Dassault)

- High-end plant/aerospace-adjacent.
- **pypemesh takes:** CATIA export support (commercial tier).

### 5.9 Inventor Plant Design (Autodesk)

- Smaller use in mechanical/equipment packaging.

### 5.10 Tekla Structures (Trimble)

- Primarily structural, occasionally for pipe racks.
- **pypemesh takes:** IFC round-trip.

### 5.11 PDS / Plant Design System (Intergraph legacy)

- Precursor to SmartPlant 3D; legacy installations exist.
- **pypemesh takes:** legacy PDS file format read (low priority).

### 5.12 Bentley OpenPlant PowerPID, SP P&ID (Hexagon)

- Schematic P&ID tools. Upstream of 3D; produce line lists.
- **pypemesh takes:** line-list import from P&ID exports.

---

## 6. Pipeline (long-distance transport)

### 6.1 PIPESIM (SLB)

- Steady-state production pipelines.
- See §3.6.

### 6.2 OLGA (SLB)

- Transient multiphase; subsea flow assurance standard.
- See §3.7.

### 6.3 Synergi Pipeline Simulator (DNV)

- Natural gas pipeline transient.
- **pypemesh takes:** soil-pipe interaction references, integration pattern.

### 6.4 Stoner Pipeline Simulator (SPS, now DNV)

- Natural gas transient.
- **pypemesh takes:** nothing directly.

### 6.5 TGNET (DNV)

- Gas network transient.

### 6.6 PipeTech (Pipeline Research Council International, PRCI)

- Pipeline-specific analysis tools.

### 6.7 AutoPIPE Vessel / Pipeline (Bentley)

- Pipeline-specific add-on.

### 6.8 CEPA / CSA Z662 tools

- Canadian pipeline code compliance tools. Specialized.

### 6.9 PIPE-FLO (Engineered Software)

- Pipeline hydraulic.

**pypemesh takes:** for Phase C pipeline tier — buried pipe model, API 1102
road crossing, PRCI soil interaction, DNV offshore pipeline codes. These are
all specifications to implement, not tools to replace.

---

## 7. Isometric / Drafting / Deliverables

### 7.1 ISOGEN (Alias → Hexagon)

- **Since:** 1980s
- **Price:** Enterprise (part of SmartPlant/CADWorx ecosystem)
- **Market:** The industry-standard isometric drawing generator. Plugs into
  every major 3D tool.
- **pypemesh takes:** ISOGEN-compatible data export so customers can still
  use their existing ISOGEN workflow. Our own iso output is a later-phase goal.

### 7.2 SmartSketch (Hexagon)

- P&ID and drawing tool. Legacy.

### 7.3 CADWorx Draftpro

- Drawing automation.

### 7.4 Plant-4D (Cesium)

- Mid-market plant drawing.

### 7.5 Iso-Metrix

- Pipe isometric generator; less common.

**pypemesh takes:** ISOGEN export compatibility; native simple isometric
generator in Phase B.1.

---

## 8. Support Design & Specialty

### 8.1 LISEGA / Anvil / Carpenter-Paterson / Bergen Supports

- Pipe support catalog vendors with accompanying design software.
- **pypemesh takes:** LISEGA support catalog format import; vendor library
  integration so users can drop a LISEGA hanger into a model with real specs.

### 8.2 NozzleFEM (Russian specialty)

- Nozzle-on-shell FEA. Competitor to NozzlePRO for Russian market.

### 8.3 CAEPIPE Vessel / ROHR2 Vessel

- Category equivalents to PV Elite.

### 8.4 Insulation takeoff / spec tools

- Various small tools; not critical to absorb.

### 8.5 Spring hanger sizing tools (catalog-specific)

- Bundled with LISEGA/Bergen/Anvil products.

### 8.6 Fatigue specialist tools (FKM, BS 7608 workbooks)

- Typically custom spreadsheets.

---

## Summary: the capability absorption list

| Category | From | What pypemesh absorbs |
|---|---|---|
| **Solver engine** | AutoPIPE | Load sequencing, no intermediate L-equations |
| **Solver breadth** | Caesar II | 30+ code library, spectrum library, buried pipe |
| **Solver robustness** | START-PROF | Pipeline buried, district heating |
| **UI philosophy** | CAEPIPE | Simplicity, defaults, fast modeling |
| **Plastic support** | AutoPIPE | Native HDPE/PE/FRP/GRE |
| **Support optimization** | AutoPIPE Advanced | ML-driven, 10K+ config evaluation |
| **Local FEA** | FEPipe/NozzlePRO | Template-driven, auto-WRC reports |
| **Flange analysis** | Caesar II + PV Elite | Kellogg + ASME Appendix 2 |
| **Transient loads** | PIPENET / AFT Impulse | Force-time interface |
| **Process boundary** | HYSYS/Plus/UniSim | Line-list import adapter |
| **CAD input (enterprise)** | SmartPlant 3D / PDMS / E3D | Enterprise adapters |
| **CAD input (mid-market)** | CADWorx / AutoCAD Plant 3D / OpenPlant | PCF + XML |
| **CAD input (mech)** | SolidWorks Routing / Inventor | Plugin SDK |
| **Deliverables** | ISOGEN | Export format compatibility |
| **Support catalogs** | LISEGA / Bergen / Anvil | Catalog import |
| **Escape valve** | ANSYS / Abaqus | Model export for edge cases |

This list drives what's in `REQUIREMENTS.md` and how we prioritize.

## What we explicitly do NOT replace (always)

- Process simulators (HYSYS, Plus, UniSim, ProMax) — we consume their output
- Hydraulic simulators (PIPENET, AFT, Flowmaster) — we consume their force-time data
- Pressure vessel design (PV Elite, Compress) — out of scope
- 3D plant CAD (PDMS, SmartPlant, E3D, CADWorx) — we integrate, we don't replace
- General FEA (ANSYS, Abaqus) — we produce export for them, we don't replace them
- Pipeline transient (OLGA, SPS) — too specialized
- BIM/coordination (Revit) — we export to it

Scope discipline is our survival mechanism.

## References

Every claim here traceable to:
- Vendor public documentation
- "What Is Piping" comparison articles (whatispiping.com)
- Piping Technology & Products vendor comparison (pipingtech.com)
- Industry practitioner forums (Eng-Tips Piping, LinkedIn Piping groups)
- ASME Section VIII, Section III, B31 series
- Peng & Peng, "Pipe Stress Engineering", ASME Press
- Kellogg, "Design of Piping Systems"
- Paulin Research Group publications

Every version/price/feature claim must be dated; this doc is refreshed every
6 months. Competitive intelligence is a living function, not a one-time doc.

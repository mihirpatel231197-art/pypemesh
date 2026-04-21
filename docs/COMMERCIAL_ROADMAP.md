# Commercial Roadmap (B → C)

**Version:** 0.1
**Audience:** Founder (you) and future investors/partners.
**Status:** Strategic direction, not a promise.

> Goal: build an open-source pipe stress platform that matures into a commercial
> product competitive with Caesar II ($10-30K/seat/year) and AutoPIPE
> ($8-25K/seat/year) — but with modern UX, cloud-first deployment, and a
> real pricing model.

## Strategy in one sentence

**Open-source the core. Charge for everything engineers actually pay for in
the real world: codes, materials data, certifications, CAD integrations,
support, enterprise features.**

## Why this works

- Commercial pipe stress buyers don't pay for *the solver*. They pay for:
  - **Code coverage** (nuclear, B31.4 pipeline, EN 13480 Europe)
  - **Validated results** (someone else's stamp of validation)
  - **Licensed material data** (ASME Section II Part D)
  - **CAD integrations** (SolidWorks, AutoCAD, SmartPlant, CADWorx)
  - **Support + training** (the real revenue driver)
  - **Enterprise features** (SSO, audit, multi-tenant)
- Open-sourcing the solver gives us: **community**, **free QA**, **credibility**, **partner reach**, **developer hiring funnel**. Caesar II/AutoPIPE have none of this.

This is the same playbook as: GitLab (OSS + self-hosted paid), MongoDB (OSS + Atlas), HashiCorp (OSS tools + Terraform Cloud), Metabase.

## Phase gates

### B → B.1 (no commercial yet)

**Entry:** Phase B ships. Validated on Appendix S, NC-3600, Markl, 5 textbook problems.

**During B.1:**
- Add B31.1, B31.4 code support
- Add non-linear + full dynamic
- Add PCF import
- **Collect usage data** (opt-in analytics, user surveys)
- **Identify the first 10 paying customers** — talk to real EPC shops, process engineers, consultants

**Exit:** 1000+ active OSS users, 20+ GitHub stars/week, at least 3 organizations using it in production (even if non-critical), clear list of "what do you need to pay us for this?"

**Time:** 3-6 months post-B release.

### B.1 → B.2

**Entry:** B.1 ships, we have user interview signal.

**During B.2:**
- Add AI support optimizer (ML on curated dataset)
- Add local FEA module (FEPipe-style shell elements)
- Add OSS-tier CAD plugin bridges (AutoCAD via OpenDWG, SolidWorks via API if license allows)
- **Form a legal entity** (LLC or C-Corp depending on investor path)
- **Draft commercial EULA** for C-tier products

**Exit:** We have proof that users would pay. At least one customer willing to prepay for a C feature ("I'll pay $X for nuclear support").

**Time:** 3-6 months further.

### B.2 → C (the commercial launch)

**Entry:** Legal entity exists, paid pilot customer exists, validation infrastructure bulletproof.

**During C:**
- Ship first commercial feature: **licensed ASME Section II Part D material data**
  - Requires: ASME commercial license agreement (~$X/year, negotiable)
  - Delivered as encrypted data pack with license verification
  - Pricing: $2000/user/year
- Ship EU/British code pack (EN 13480, BS 806): $1500/user/year
- Ship pipeline code pack (B31.4, B31.8, B31.12, DNV, NORSOK): $2000/user/year
- Ship enterprise tier: SSO, RBAC, audit, multi-tenant, SLA: $500/user/month
- Nuclear tier (separate product): NQA-1 validation multi-year project

**Exit:** Self-sustaining revenue. Real customers. Growth path clear.

**Time:** 6-18 months further. This is the hardest phase.

## What you need for C (the honest list)

### Legal / business

- [ ] LLC or C-Corp formed (C-Corp required for VC; LLC fine bootstrapped)
- [ ] Trademark for "pypemesh" or chosen commercial name
- [ ] Terms of Service + Privacy Policy + EULA (lawyer-reviewed)
- [ ] Commercial Contributor License Agreement (CCLA) signed by every contributor
- [ ] E&O insurance (errors & omissions) — $50-150K/year for engineering software
- [ ] General liability + cyber insurance

### Certifications / data licenses

- [ ] **ASME Section II Part D data license** — critical. Get a quote now, plan for it.
- [ ] ASME B31.1/3/4/8 code subscriptions (required for reference)
- [ ] EN/ISO/DIN subscriptions for European codes
- [ ] **NQA-1 audit** for nuclear tier — 12-24 month process, $500K-$2M, needs a QA manager
- [ ] NRC 10 CFR 50 Appendix B if doing US nuclear work

### People (a solo founder cannot ship C)

- [ ] **Licensed PE in Mechanical/Piping** — founder or co-founder ideal. Literally required to stamp validation reports buyers will ask about.
- [ ] **Solver/numerical engineer** — FEA PhD ideal, strong NumPy/SciPy/PETSc experience
- [ ] **Frontend engineer** — React + Three.js + large state apps
- [ ] **QA manager for nuclear tier** — if pursuing nuclear
- [ ] **Technical writer** — for docs + validation reports
- [ ] **Sales engineer** — for enterprise sales (pipe stress is still a relationship-driven sale)
- [ ] **Customer success** — keeping enterprise accounts retained

### Infrastructure

- [ ] Production cloud (AWS or GCP, enterprise buyers want both options eventually)
- [ ] SOC 2 Type II audit (enterprise gate) — 6-12 month process, $30-100K
- [ ] Data residency options (EU buyers require this)
- [ ] 24/7 on-call rotation for enterprise SLA

### Funding options

- **Bootstrap**: possible. Need revenue from B.2 to fund C. Slower. No investor.
- **Angel**: $250K-$1M to hire first 2 engineers. Likely best first round.
- **Seed VC**: $2-5M. Possible if traction from B phase is strong. Dilution ~20%.
- **Customer-funded**: sign a large EPC as design partner, they fund first year of C in exchange for features + discount. Often best path for vertical tools.

### Realistic financial model (rough)

- Break-even revenue needed: ~$1.5M/year (covers ~6 engineers + overhead)
- Per-user ARPU target: $5-10K/year (between CAEPIPE low and Caesar II high)
- Users needed at break-even: 150-300
- Realistic B.1 OSS users: 1000-5000
- Realistic conversion: 3-10% (generous for B2B vertical tools)
- So: ~$750K-$2.5M ARR achievable at OSS user scale of 5000+

This is a real business. Not a huge one. Pipe stress is a $XXM market, not $XB.

## Commercial product tiers (proposed pricing)

| Tier | Price | Includes |
|---|---|---|
| **pypemesh OSS** | $0 | Everything in Phase B. MIT. Host it yourself. |
| **pypemesh Cloud** | $49/user/month | Hosted version, cloud collab, 5 projects |
| **pypemesh Team** | $199/user/month | Unlimited projects, team features, integrations |
| **pypemesh Pro** | $499/user/month | Commercial codes, licensed materials, AI optimizer |
| **pypemesh Enterprise** | Custom (from $50K/year) | SSO, SLA, dedicated support, self-hosted |
| **pypemesh Nuclear** | Custom (from $150K/year) | NQA-1, Section III, nuclear audit support |

## Competitive positioning (honest)

| Competitor | Price | Our edge | Their edge |
|---|---|---|---|
| **Caesar II** | $15-30K/seat/yr | Modern UX, cloud, open core | 40-year reputation, global install base |
| **AutoPIPE** | $10-25K/seat/yr | Cloud collab, transparent, open core | Bentley ecosystem, AI already shipping |
| **CAEPIPE** | $5-10K/seat/yr | More features, open core | Already easy, cheap |
| **START-PROF** | $4-8K/seat/yr | Modern stack, open core | Cheap, pipeline focus |

**Our positioning**: "The Caesar II you can hire into, fork, audit, deploy
yourself, or buy managed — with real UX."

**Who buys us first**:
- Consultants who bounce between tools and want one cloud tool
- Mid-size EPC firms priced out of Caesar II seats
- Academic/research users (OSS is instant adoption)
- Enterprises with a security team that mandates open source
- International firms outside Caesar II/AutoPIPE's stronghold

**Who won't buy us first**: large US EPC firms already Caesar-standardized.
That's fine; they're a 5-year goal.

## Risks (honest)

1. **Solver validation burden** is bigger than founders typically estimate. Plan for it.
2. **PE liability**: without a licensed PE, commercial sales are hard. Mitigate early.
3. **CAD integration politics**: SolidWorks/AutoCAD SDK access is at their discretion. Plan to negotiate or ship partial integrations.
4. **Nuclear is a trap** for a small team. Do it only with a serious partner and upfront funding.
5. **ASME material data cost** could be gating. Get a quote in year 1.
6. **Competitor response**: Bentley/Hexagon will eventually respond with cloud + modern UX. We need to be 3+ years ahead by then.
7. **You're solo**. Hire the first engineer (numerical/FEA) before trying to ship C.

## The first dollar test

By end of Phase B.1 you should be able to answer:
- Who will be the first customer to pay?
- What will they pay for?
- How much?
- When?

If you can't answer by then, stay OSS and build a community. Forcing C without
these answers burns runway fast.

## Decision points (coming up)

- **Post-M6 (phase B release)**: measure OSS adoption. If >1000 users/month, push to B.1. If <100, rethink positioning.
- **Mid B.1**: start conversations with 3 real EPC firms. Listen, don't pitch.
- **End B.2**: commit to C or stay OSS. Based on: do you have a paying pilot?
- **Mid C**: raise or bootstrap decision.

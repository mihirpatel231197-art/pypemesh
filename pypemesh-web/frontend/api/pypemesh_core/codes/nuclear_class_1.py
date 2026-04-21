"""ASME Section III Subsection NB — Class 1 Nuclear Piping.

Class 1 is the most rigorous nuclear piping code. Adds to Class 2/3:
- Fatigue usage factor U ≤ 1.0 per NB-3222.4
- Primary + secondary stress intensity range ≤ 3·Sm (NB-3222.2)
- Simplified elastic-plastic analysis with Ke factor (NB-3228.5)
- Thermal stratification check (NB-3653)

This implementation focuses on the additional Class 1 checks beyond what
NC-3600 covers. It reuses the NC-3600 primary-stress computation and adds
fatigue life prediction using the ASME Section III Appendix I fatigue
curves.

**Disclaimer**: this module is NOT NQA-1 validated. It implements the
structural equations but commercial nuclear use requires full ASME
certification including fatigue curve authentication, QA procedures,
and licensed PE review.

Reference: ASME B&PV Code Section III Div 1 NB-3600 (2023).
"""

from __future__ import annotations

from dataclasses import dataclass
from math import log10

from pypemesh_core.codes.base import CodeCheck, CodeResult
from pypemesh_core.codes.nuclear_section_iii import NuclearSectionIII, ServiceLevel
from pypemesh_core.solver.combinations import CombinedSolution, evaluate_combinations
from pypemesh_core.solver.model import Project


# Simplified ASME Section III Appendix I fatigue curve (Fig. I-9.1 for CS <700°F)
# Format: stress amplitude (Pa) → allowable cycles N
# Values from public ASME Section III Appendix I, interpolated as log-log.
# Real commercial use requires the licensed curve data.
# (Pa, cycles)
_CS_FATIGUE_CURVE = [
    (4_137_000_000,      10),
    (2_069_000_000,      100),
    (1_034_000_000,      1_000),
    (517_000_000,        10_000),
    (258_000_000,        100_000),
    (172_000_000,        1_000_000),
    (138_000_000,        10_000_000),
]


def fatigue_allowable_cycles(stress_amplitude_pa: float) -> float:
    """Look up allowable cycles N for given alternating stress amplitude S_alt.

    Uses log-log interpolation on the Appendix I curve for carbon steel.
    """
    table = sorted(_CS_FATIGUE_CURVE, key=lambda t: t[0])
    if stress_amplitude_pa >= table[-1][0]:
        return float(table[-1][1])
    if stress_amplitude_pa <= table[0][0]:
        return float("inf")  # below endurance limit
    for i in range(len(table) - 1):
        s1, n1 = table[i]
        s2, n2 = table[i + 1]
        if s1 <= stress_amplitude_pa <= s2:
            log_n1, log_n2 = log10(n1), log10(n2)
            log_s1, log_s2 = log10(s1), log10(s2)
            log_s = log10(stress_amplitude_pa)
            log_n = log_n1 + (log_n2 - log_n1) * (log_s - log_s1) / (log_s2 - log_s1)
            return 10 ** log_n
    return float("inf")


@dataclass
class FatigueEvent:
    """A cyclic event with stress range + cycle count."""

    name: str
    stress_range_pa: float
    n_cycles: float


def cumulative_usage_factor(events: list[FatigueEvent]) -> float:
    """Compute U = Σ (n_i / N_i) per Miner's rule (ASME NB-3222.4)."""
    U = 0.0
    for e in events:
        # Stress amplitude = range / 2
        amplitude = e.stress_range_pa / 2.0
        N_allow = fatigue_allowable_cycles(amplitude)
        if N_allow > 0:
            U += e.n_cycles / N_allow
    return U


class NuclearClass1(NuclearSectionIII):
    """ASME §III NB-3600 Class 1 piping.

    In addition to Class 2/3 primary-stress checks, Class 1 requires:
    - Primary + secondary range ≤ 3·Sm (NB-3222.2)
    - Fatigue usage factor U ≤ 1.0 (NB-3222.4)

    fatigue_events: list of (name, stress_range, cycles) tuples for the
                    plant's design transients (heatup/cooldown, SCRAM,
                    feedwater loss, etc.)
    """

    code_id = "ASME-III-NB"
    version = "2023"

    def __init__(
        self, T_install: float = 293.15, T_evaluation: float | None = None,
        service_level: ServiceLevel | str = ServiceLevel.DESIGN,
        fatigue_events: list[FatigueEvent] | None = None,
    ):
        super().__init__(
            T_install=T_install, T_evaluation=T_evaluation,
            service_class=2,  # reuse Class 2 equation structure
            service_level=service_level,
        )
        self.code_id = "ASME-III-NB"
        self.fatigue_events = fatigue_events or []

    def evaluate(self, project: Project, combinations: list[CombinedSolution] | None = None) -> list[CodeResult]:
        if combinations is None:
            combinations = evaluate_combinations(project, T_eval=self.T_evaluation)

        # Primary-stress results (inherit Class 2/3 approach)
        results = super().evaluate(project, combinations=combinations)
        for r in results:
            r.equation_used = r.equation_used.replace("NC-", "NB-")

        # Fatigue usage check (plant-wide, not per-element)
        if self.fatigue_events:
            U = cumulative_usage_factor(self.fatigue_events)
            status = "pass" if U <= 1.0 else "fail"
            results.append(CodeResult(
                element_id="PROJECT",
                combination_id="FATIGUE",
                stress=U * 1e6,        # render in MPa-like units for the report
                allowable=1.0 * 1e6,
                ratio=U,
                status=status,
                equation_used="NB-3222.4",
            ))

        return results

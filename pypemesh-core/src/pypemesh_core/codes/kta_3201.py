"""KTA 3201 (Germany) — Components of the reactor coolant pressure boundary.

German nuclear code (Kerntechnischer Ausschuss). Similar in structure to
ASME Section III but uses conservative allowables derived from design stress
f = min(Rp0.2/1.5, Rm/2.4). Different service levels: A, B, C, D + testing.

Service-level factors more conservative than ASME III:
- Design (A level): 1.0·f (not 1.5·Sh)
- Level B: 1.3·f
- Level C: 1.8·f
- Level D: 2.4·f

Reference: KTA 3201.2 (2017). Design and Construction. Part 2:
Safety-related requirements.
"""

from __future__ import annotations

from pypemesh_core.codes.nuclear_section_iii import (
    NuclearSectionIII,
    ServiceLevel,
)


# KTA uses different factors (relative to design stress f, not Sh)
KTA_SERVICE_FACTORS = {
    ServiceLevel.DESIGN: 1.0,    # design against f
    ServiceLevel.LEVEL_A: 1.0,   # normal = design
    ServiceLevel.LEVEL_B: 1.3,   # anticipated operational occurrences
    ServiceLevel.LEVEL_C: 1.8,   # infrequent events
    ServiceLevel.LEVEL_D: 2.4,   # design basis accident
}


class KTA_3201(NuclearSectionIII):
    """KTA 3201 German nuclear primary circuit piping.

    Mapped to ASME III Class 2/3 structure but with KTA factors. Allowable
    stress is tagged as 'f' per KTA convention (derived from Sh/Sy material
    properties in our library).
    """

    code_id = "KTA-3201"
    version = "2017"

    def __init__(
        self, T_install: float = 293.15, T_evaluation: float | None = None,
        service_level: ServiceLevel | str = ServiceLevel.DESIGN,
    ):
        super().__init__(T_install=T_install, T_evaluation=T_evaluation,
                         service_class=2, service_level=service_level)
        self.code_id = "KTA-3201"

    def evaluate(self, project, combinations=None):
        import pypemesh_core.codes.nuclear_section_iii as nsm
        original = nsm.SERVICE_LEVEL_FACTORS
        nsm.SERVICE_LEVEL_FACTORS = KTA_SERVICE_FACTORS
        try:
            results = super().evaluate(project, combinations)
        finally:
            nsm.SERVICE_LEVEL_FACTORS = original
        for r in results:
            r.equation_used = r.equation_used.replace("NC-", "KTA-").replace("level_", "level-")
        return results

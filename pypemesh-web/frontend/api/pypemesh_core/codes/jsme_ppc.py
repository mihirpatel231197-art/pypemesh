"""JSME S NC1 (Japan) — Codes for Nuclear Power Generation Facilities.

Japan's nuclear piping code is JSME S NC1, which parallels ASME Section III
but with additional seismic provisions and stricter fatigue checks for
Class 2/3 components. Equations are the same B1·PDo/2t + B2·Do·M/(2I)
form with slightly different service-level factors.

Reference: JSME S NC1-2022 PPC Part (Piping and Pipe Components).
"""

from __future__ import annotations

from pypemesh_core.codes.nuclear_section_iii import (
    SERVICE_LEVEL_FACTORS,
    NuclearSectionIII,
    ServiceLevel,
)


# JSME has slightly different service-level factors for Class 2/3
JSME_SERVICE_FACTORS = {
    ServiceLevel.DESIGN: 1.5,
    ServiceLevel.LEVEL_A: 1.5,   # more conservative than ASME (1.8)
    ServiceLevel.LEVEL_B: 1.65,  # more conservative than ASME (1.8)
    ServiceLevel.LEVEL_C: 2.25,
    ServiceLevel.LEVEL_D: 3.0,
}


class JSME_PPC(NuclearSectionIII):
    """JSME S NC1 Class 2/3. Inherits ASME III NC/ND with stricter factors."""

    code_id = "JSME-S-NC1"
    version = "2022"

    def __init__(
        self, T_install: float = 293.15, T_evaluation: float | None = None,
        service_class: int = 2,
        service_level: ServiceLevel | str = ServiceLevel.DESIGN,
    ):
        super().__init__(T_install=T_install, T_evaluation=T_evaluation,
                         service_class=service_class, service_level=service_level)
        self.code_id = f"JSME-S-NC1-Class{service_class}"

    def evaluate(self, project, combinations=None):
        # Patch the service level factors temporarily
        import pypemesh_core.codes.nuclear_section_iii as nsm
        original = nsm.SERVICE_LEVEL_FACTORS
        nsm.SERVICE_LEVEL_FACTORS = JSME_SERVICE_FACTORS
        try:
            results = super().evaluate(project, combinations)
        finally:
            nsm.SERVICE_LEVEL_FACTORS = original
        # Override equation labels to show JSME
        for r in results:
            r.equation_used = r.equation_used.replace("NC-", "JSME-")
        return results

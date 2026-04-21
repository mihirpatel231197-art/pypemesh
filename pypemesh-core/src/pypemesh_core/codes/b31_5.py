"""ASME B31.5 (Refrigeration Piping and Heat Transfer Components).

Structurally similar to B31.3 with small-bore refrigeration focus. Same
equations, same allowables. Main practical differences are the material
subset (copper alloys, aluminum) and insulation/vapor-barrier detailing —
both outside our structural scope.

Reference: ASME B31.5-2022.
"""

from __future__ import annotations

from pypemesh_core.codes.b31_3 import B31_3


class B31_5(B31_3):
    code_id = "B31.5"
    version = "2022"

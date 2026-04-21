"""ASME B31.9 (Building Services Piping).

Simplified code for building utility piping: HVAC hot/chilled water,
domestic water, condensate, steam ≤150 psig, low-pressure gas. Similar
equations to B31.1 but with a simpler occasional-load treatment (no seismic
spectrum required in most buildings).

Uses B31.1 equation structure.

Reference: ASME B31.9-2022.
"""

from __future__ import annotations

from pypemesh_core.codes.b31_1 import B31_1


class B31_9(B31_1):
    code_id = "B31.9"
    version = "2022"

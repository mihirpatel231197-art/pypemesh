"""ISO 15649 (International Standard) — Petroleum and Natural Gas Industries
— Piping. Harmonizes ASME B31.3 with international practice.

Structurally identical to B31.3 for metallic piping; the main differences
are referenced codes for materials (EN/ISO vs ASME II-D) and testing
procedures. For stress analysis purposes, maps directly to B31.3.

Reference: ISO 15649:2001.
"""

from __future__ import annotations

from pypemesh_core.codes.b31_3 import B31_3


class ISO_15649(B31_3):
    code_id = "ISO-15649"
    version = "2001"

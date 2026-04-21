"""BS 806 (British Standard) — Specification for Design and Construction of
Ferrous Piping Installations for and in Connection with Land Boilers.

Pre-Eurocode standard still referenced in UK industrial projects. Similar
to ASME B31.1 but with British Standard materials and stress conventions.

Simplified implementation: inherits B31.1 equations with BS-style allowables.
For UK-specific service factors, use the k_occasional override.

Reference: BS 806:1993 + A1:1998.
"""

from __future__ import annotations

from pypemesh_core.codes.b31_1 import B31_1


class BS_806(B31_1):
    code_id = "BS-806"
    version = "1993"

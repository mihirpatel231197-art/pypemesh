"""Tee element — junction with stress intensification at the crotch.

In our beam-element model a tee is mechanically a regular straight pipe
(the run portion that this element represents). The "tee" character lives
in the SIF applied at stress recovery — the run-side and branch-side both
get higher SIFs because of the local stress concentration.

For a more accurate representation, the branch connection itself is
typically modelled as a separate element joining at the run node, with
the run element passing through unchanged. The SIF is applied to whichever
element's moments dominate at the junction node.

This module provides convenience: a TEE element with stiffness identical
to a PIPE, but flagged so the code-check picks tee SIF values from B31J.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from pypemesh_core.solver.elements.beam import beam_stiffness_global


def tee_stiffness_global(
    p_start: NDArray[np.float64],
    p_end: NDArray[np.float64],
    E: float,
    G: float,
    A: float,
    I: float,
    J: float,
    up: NDArray[np.float64] | None = None,
) -> tuple[NDArray[np.float64], NDArray[np.float64], float]:
    """Tee run stiffness — same as straight pipe."""
    return beam_stiffness_global(p_start, p_end, E, G, A, I, I, J, up=up)

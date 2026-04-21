"""Abstract base for a code-compliance check (ASME B31.3, B31.1, EN 13480, ...)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class CodeResult:
    """Per-element compliance outcome for a single combination."""

    element_id: str
    combination_id: str
    stress: float  # Pa
    allowable: float  # Pa
    ratio: float
    status: str  # "pass" | "fail" | "warn"
    equation_used: str


class CodeCheck(ABC):
    """Base class for all code checks. Register via `pypemesh.codes` entry point."""

    code_id: str = ""
    version: str = ""

    @abstractmethod
    def evaluate(self, model, results) -> list[CodeResult]:
        """Given a solved model, produce a list of CodeResults."""
        raise NotImplementedError

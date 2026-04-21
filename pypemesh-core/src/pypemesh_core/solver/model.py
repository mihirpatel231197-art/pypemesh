"""Core data model for a pipe stress project.

All quantities SI internally. See docs/ARCHITECTURE.md §Units.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ElementType(str, Enum):
    PIPE = "pipe"
    ELBOW = "elbow"
    TEE = "tee"
    REDUCER = "reducer"
    RIGID = "rigid"
    SPRING = "spring"
    EXPANSION_JOINT = "expansion_joint"


class RestraintType(str, Enum):
    ANCHOR = "anchor"
    GUIDE = "guide"
    REST = "rest"
    LIMIT_STOP = "limit_stop"
    SPRING_HANGER = "spring_hanger"
    SNUBBER = "snubber"


class LoadKind(str, Enum):
    WEIGHT = "weight"
    THERMAL = "thermal"
    PRESSURE = "pressure"
    WIND = "wind"
    SEISMIC = "seismic"
    USER = "user"


@dataclass(frozen=True)
class Node:
    """A point in space with 6 DOF (3 translation, 3 rotation). Coordinates in meters."""

    id: str
    x: float
    y: float
    z: float


@dataclass(frozen=True)
class Section:
    """Pipe cross-section. Dimensions in meters."""

    id: str
    outside_diameter: float
    wall_thickness: float
    corrosion_allowance: float = 0.0
    insulation_thickness: float = 0.0
    insulation_density: float = 0.0  # kg/m^3


@dataclass
class Material:
    """Material with temperature-dependent properties.

    Properties are stored as (temperature [K], value) tuples; interpolated on demand.
    """

    id: str
    name: str
    # (T [K], E [Pa])
    elastic_modulus: list[tuple[float, float]]
    # (T [K], alpha [1/K])
    thermal_expansion: list[tuple[float, float]]
    # (T [K], Sh [Pa]) — hot allowable
    allowable_hot: list[tuple[float, float]]
    # Sc [Pa] — cold allowable
    allowable_cold: float
    density: float  # kg/m^3
    poisson: float = 0.3


@dataclass
class Element:
    """A connection between two nodes with an associated cross-section and material."""

    id: str
    type: ElementType
    from_node: str
    to_node: str
    section: str
    material: str
    # Elbow-specific
    bend_radius: float | None = None
    # Tee-specific
    branch_section: str | None = None


@dataclass
class Restraint:
    """A constraint on degrees of freedom at a node."""

    node: str
    type: RestraintType
    # Per-DOF: True = constrained, False = free
    dx: bool = False
    dy: bool = False
    dz: bool = False
    rx: bool = False
    ry: bool = False
    rz: bool = False
    # Spring support stiffness [N/m], zero = rigid
    stiffness: tuple[float, float, float] = (0.0, 0.0, 0.0)
    # Gap size for one-way [m]
    gap: float | None = None
    # Friction coefficient (dimensionless, 0..1)
    friction: float = 0.0


@dataclass
class LoadCase:
    """A single load case (weight, thermal, pressure, etc.)."""

    id: str
    kind: LoadKind
    scale: float = 1.0
    # Kind-specific parameters
    temperature: float | None = None  # K (for thermal)
    pressure: float | None = None  # Pa (for pressure)
    direction: tuple[float, float, float] | None = None  # (for wind/seismic)


@dataclass
class LoadCombination:
    """Combine load cases for a code check (sustained, occasional, expansion)."""

    id: str
    cases: list[str]
    category: str  # "sustained" | "occasional" | "expansion" | "operating"
    scales: list[float] = field(default_factory=list)


@dataclass
class Project:
    """Full pipe stress model."""

    name: str
    nodes: list[Node] = field(default_factory=list)
    elements: list[Element] = field(default_factory=list)
    sections: list[Section] = field(default_factory=list)
    materials: list[Material] = field(default_factory=list)
    restraints: list[Restraint] = field(default_factory=list)
    load_cases: list[LoadCase] = field(default_factory=list)
    load_combinations: list[LoadCombination] = field(default_factory=list)
    code: str = "B31.3"
    code_version: str = "2022"

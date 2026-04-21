"""ASME B36.10M — Welded and Seamless Wrought Steel Pipe — standard sizes.

Parametric table of Nominal Pipe Size (NPS) vs schedules with actual
outside diameter (OD) and wall thickness. All values in SI (meters).

Covers NPS 1/8 through NPS 48 for schedules 10, 20, 30, 40 (STD), 60, 80
(XS), 100, 120, 140, 160, XXS.

Reference: ASME B36.10M-2022.
"""

from __future__ import annotations

from pypemesh_core.solver.model import Section


# Format: nps_key → (OD_mm, {schedule: wall_mm})
# STD = Standard, XS = Extra Strong, XXS = Double Extra Strong
# Populated from ASME B36.10M-2022 public tables.
B36_10_TABLE: dict[str, tuple[float, dict[str, float]]] = {
    "NPS-1/8":   (10.3,   {"10": 1.24, "40": 1.73, "STD": 1.73, "80": 2.41, "XS": 2.41}),
    "NPS-1/4":   (13.7,   {"10": 1.65, "40": 2.24, "STD": 2.24, "80": 3.02, "XS": 3.02}),
    "NPS-3/8":   (17.1,   {"10": 1.65, "40": 2.31, "STD": 2.31, "80": 3.20, "XS": 3.20}),
    "NPS-1/2":   (21.3,   {"10": 2.11, "40": 2.77, "STD": 2.77, "80": 3.73, "XS": 3.73, "160": 4.78, "XXS": 7.47}),
    "NPS-3/4":   (26.7,   {"10": 2.11, "40": 2.87, "STD": 2.87, "80": 3.91, "XS": 3.91, "160": 5.56, "XXS": 7.82}),
    "NPS-1":     (33.4,   {"10": 2.77, "40": 3.38, "STD": 3.38, "80": 4.55, "XS": 4.55, "160": 6.35, "XXS": 9.09}),
    "NPS-1-1/4": (42.2,   {"10": 2.77, "40": 3.56, "STD": 3.56, "80": 4.85, "XS": 4.85, "160": 6.35, "XXS": 9.70}),
    "NPS-1-1/2": (48.3,   {"10": 2.77, "40": 3.68, "STD": 3.68, "80": 5.08, "XS": 5.08, "160": 7.14, "XXS": 10.15}),
    "NPS-2":     (60.3,   {"10": 2.77, "40": 3.91, "STD": 3.91, "80": 5.54, "XS": 5.54, "160": 8.74, "XXS": 11.07}),
    "NPS-2-1/2": (73.0,   {"10": 3.05, "40": 5.16, "STD": 5.16, "80": 7.01, "XS": 7.01, "160": 9.53, "XXS": 14.02}),
    "NPS-3":     (88.9,   {"10": 3.05, "40": 5.49, "STD": 5.49, "80": 7.62, "XS": 7.62, "160": 11.13, "XXS": 15.24}),
    "NPS-3-1/2": (101.6,  {"10": 3.05, "40": 5.74, "STD": 5.74, "80": 8.08, "XS": 8.08}),
    "NPS-4":     (114.3,  {"10": 3.05, "40": 6.02, "STD": 6.02, "80": 8.56, "XS": 8.56, "120": 11.13, "160": 13.49, "XXS": 17.12}),
    "NPS-5":     (141.3,  {"10": 3.40, "40": 6.55, "STD": 6.55, "80": 9.53, "XS": 9.53, "120": 12.70, "160": 15.88, "XXS": 19.05}),
    "NPS-6":     (168.3,  {"10": 3.40, "40": 7.11, "STD": 7.11, "80": 10.97, "XS": 10.97, "120": 14.27, "160": 18.26, "XXS": 21.95}),
    "NPS-8":     (219.1,  {"10": 3.76, "20": 6.35, "30": 7.04, "40": 8.18, "STD": 8.18, "60": 10.31, "80": 12.70, "XS": 12.70, "100": 15.09, "120": 18.26, "140": 20.62, "160": 23.01, "XXS": 22.23}),
    "NPS-10":    (273.1,  {"10": 4.19, "20": 6.35, "30": 7.80, "40": 9.27, "STD": 9.27, "60": 12.70, "80": 15.09, "XS": 12.70, "100": 18.26, "120": 21.44, "140": 25.40, "160": 28.58}),
    "NPS-12":    (323.9,  {"10": 4.57, "20": 6.35, "30": 8.38, "40": 10.31, "STD": 9.53, "60": 14.27, "80": 17.48, "XS": 12.70, "100": 21.44, "120": 25.40, "140": 28.58, "160": 33.32}),
    "NPS-14":    (355.6,  {"10": 6.35, "20": 7.92, "30": 9.53, "STD": 9.53, "40": 11.13, "60": 15.09, "80": 19.05, "XS": 12.70, "100": 23.83, "120": 27.79, "140": 31.75, "160": 35.71}),
    "NPS-16":    (406.4,  {"10": 6.35, "20": 7.92, "30": 9.53, "STD": 9.53, "40": 12.70, "60": 16.66, "80": 21.44, "XS": 12.70, "100": 26.19, "120": 30.96, "140": 36.53, "160": 40.49}),
    "NPS-18":    (457.0,  {"10": 6.35, "20": 7.92, "STD": 9.53, "30": 11.13, "40": 14.27, "60": 19.05, "80": 23.83, "XS": 12.70, "100": 29.36, "120": 34.93, "140": 39.67, "160": 45.24}),
    "NPS-20":    (508.0,  {"10": 6.35, "20": 9.53, "STD": 9.53, "30": 12.70, "40": 15.09, "60": 20.62, "80": 26.19, "XS": 12.70, "100": 32.54, "120": 38.10, "140": 44.45, "160": 50.01}),
    "NPS-24":    (609.6,  {"10": 6.35, "20": 9.53, "STD": 9.53, "30": 14.27, "40": 17.48, "60": 24.61, "80": 30.96, "XS": 12.70, "100": 38.89, "120": 46.02, "140": 52.37, "160": 59.54}),
    "NPS-30":    (762.0,  {"10": 7.92, "20": 12.70, "STD": 9.53, "30": 15.88}),
    "NPS-32":    (813.0,  {"10": 7.92, "20": 12.70, "STD": 9.53}),
    "NPS-36":    (914.4,  {"10": 7.92, "20": 12.70, "STD": 9.53, "40": 19.05}),
    "NPS-42":    (1066.8, {"STD": 9.53, "XS": 12.70}),
    "NPS-48":    (1219.2, {"STD": 9.53, "XS": 12.70}),
}


def list_sizes() -> list[str]:
    """Return all NPS keys in the catalog."""
    return list(B36_10_TABLE.keys())


def list_schedules(nps: str) -> list[str]:
    """Return available schedules for a given NPS."""
    if nps not in B36_10_TABLE:
        raise KeyError(f"Unknown NPS: {nps}. Use list_sizes() to see available.")
    return list(B36_10_TABLE[nps][1].keys())


def get_section(
    nps: str, schedule: str = "STD", section_id: str | None = None
) -> Section:
    """Look up a pipe section by NPS and schedule.

    Args:
        nps: Nominal pipe size key (e.g. "NPS-6", "NPS-1-1/2")
        schedule: Schedule ("10", "40", "STD", "80", "XS", "160", "XXS", ...)
        section_id: Override id. Defaults to "<nps>-<schedule>".

    Returns:
        Section with OD and wall in meters.
    """
    if nps not in B36_10_TABLE:
        raise KeyError(f"Unknown NPS: {nps}. Use list_sizes().")
    od_mm, schedules = B36_10_TABLE[nps]
    if schedule not in schedules:
        raise KeyError(
            f"Schedule {schedule} not available for {nps}. "
            f"Options: {list(schedules.keys())}"
        )
    wall_mm = schedules[schedule]
    sid = section_id or f"{nps}-{schedule}"
    return Section(
        id=sid,
        outside_diameter=od_mm / 1000.0,
        wall_thickness=wall_mm / 1000.0,
    )

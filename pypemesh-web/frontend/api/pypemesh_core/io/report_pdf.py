"""ASME-style PDF stress analysis report generator.

Produces a structured PDF: cover, model summary, code/loading, per-combination
stress table, restraint reactions, pass/fail summary, disclaimer.

Built on ReportLab. See docs/REQUIREMENTS.md §B-F9.
"""

from __future__ import annotations

import io
from datetime import datetime
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from pypemesh_core.codes.base import CodeResult
from pypemesh_core.solver.combinations import CombinedSolution
from pypemesh_core.solver.model import Project


def _stress_format(value_pa: float) -> str:
    if abs(value_pa) >= 1e6:
        return f"{value_pa / 1e6:.1f} MPa"
    if abs(value_pa) >= 1e3:
        return f"{value_pa / 1e3:.1f} kPa"
    return f"{value_pa:.1f} Pa"


def _build_styles() -> dict:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title", parent=base["Title"], fontSize=22, spaceAfter=10, alignment=TA_LEFT,
            textColor=colors.HexColor("#0c1628"),
        ),
        "subtitle": ParagraphStyle(
            "Subtitle", parent=base["Normal"], fontSize=12, spaceAfter=24,
            textColor=colors.HexColor("#4b5563"),
        ),
        "h2": ParagraphStyle(
            "H2", parent=base["Heading2"], fontSize=14, spaceBefore=12, spaceAfter=6,
            textColor=colors.HexColor("#0c1628"),
        ),
        "body": ParagraphStyle(
            "Body", parent=base["BodyText"], fontSize=10, leading=14,
        ),
        "small": ParagraphStyle(
            "Small", parent=base["Normal"], fontSize=8.5, textColor=colors.HexColor("#6b7280"),
        ),
        "right": ParagraphStyle(
            "Right", parent=base["Normal"], fontSize=10, alignment=TA_RIGHT,
        ),
    }


def _summary_table(project: Project, results: list[CodeResult]) -> Table:
    failed = sum(1 for r in results if r.status == "fail")
    max_ratio = max((r.ratio for r in results), default=0.0)
    overall = "FAIL" if failed else "PASS"
    data = [
        ["Project", project.name],
        ["Code", f"{project.code} ({project.code_version})"],
        ["Nodes", str(len(project.nodes))],
        ["Elements", str(len(project.elements))],
        ["Combinations", str(len(project.load_combinations))],
        ["Total checks", str(len(results))],
        ["Failed", str(failed)],
        ["Max ratio", f"{max_ratio:.3f}"],
        ["Overall status", overall],
    ]
    t = Table(data, colWidths=[1.7 * inch, 4.5 * inch])
    color = colors.HexColor("#16a34a") if overall == "PASS" else colors.HexColor("#dc2626")
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#6b7280")),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
        ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.HexColor("#e5e7eb")),
        ("FONTNAME", (1, -1), (1, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (1, -1), (1, -1), color),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def _stress_table(results: list[CodeResult]) -> Table:
    data: list[list[Any]] = [
        ["Element", "Combination", "Eq.", "Stress", "Allowable", "Ratio", "Status"],
    ]
    for r in results:
        data.append([
            r.element_id,
            r.combination_id,
            r.equation_used,
            _stress_format(r.stress),
            _stress_format(r.allowable),
            f"{r.ratio:.3f}",
            r.status.upper(),
        ])

    t = Table(data, colWidths=[
        0.9 * inch, 1.0 * inch, 0.5 * inch, 1.0 * inch, 1.0 * inch, 0.7 * inch, 0.7 * inch
    ], repeatRows=1)

    base_style = [
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
        ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.HexColor("#e5e7eb")),
        ("ALIGN", (3, 1), (-1, -1), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    # Color status cells
    for i, r in enumerate(results, start=1):
        color = colors.HexColor("#16a34a") if r.status == "pass" else colors.HexColor("#dc2626")
        base_style.append(("TEXTCOLOR", (-1, i), (-1, i), color))
        base_style.append(("FONTNAME", (-1, i), (-1, i), "Helvetica-Bold"))
    t.setStyle(TableStyle(base_style))
    return t


def _restraint_table(combinations: list[CombinedSolution]) -> Table | None:
    if not combinations:
        return None
    data: list[list[Any]] = [["Combination", "Node", "Fx [N]", "Fy [N]", "Fz [N]", "Mx [Nm]", "My [Nm]", "Mz [Nm]"]]
    for combo in combinations:
        for node_id, react in combo.reactions.items():
            data.append([
                combo.combination_id, node_id,
                f"{react[0]:.1f}", f"{react[1]:.1f}", f"{react[2]:.1f}",
                f"{react[3]:.1f}", f"{react[4]:.1f}", f"{react[5]:.1f}",
            ])
    if len(data) == 1:
        return None
    t = Table(data, repeatRows=1)
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
        ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.HexColor("#e5e7eb")),
        ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def generate_pdf_report(
    project: Project,
    code_results: list[CodeResult],
    combinations: list[CombinedSolution] | None = None,
    output_path: str | Path | None = None,
    company: str = "",
    engineer: str = "",
) -> bytes:
    """Generate a PDF stress analysis report.

    If output_path is provided, also writes to disk. Returns the raw PDF bytes.
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=LETTER,
        leftMargin=0.7 * inch, rightMargin=0.7 * inch,
        topMargin=0.7 * inch, bottomMargin=0.7 * inch,
        title=f"pypemesh stress report — {project.name}",
        author="pypemesh",
    )
    styles = _build_styles()

    story: list[Any] = []

    # Cover
    story.append(Paragraph("Pipe Stress Analysis Report", styles["title"]))
    cover_subtitle = f"Project: <b>{project.name}</b> · Code: <b>{project.code} {project.code_version}</b>"
    story.append(Paragraph(cover_subtitle, styles["subtitle"]))

    # Metadata
    meta_data = [
        ["Generated", datetime.now().strftime("%Y-%m-%d %H:%M")],
        ["Solver", "pypemesh-core (open-source)"],
    ]
    if company:
        meta_data.insert(0, ["Company", company])
    if engineer:
        meta_data.insert(1, ["Engineer", engineer])
    meta_table = Table(meta_data, colWidths=[1.5 * inch, 4.5 * inch])
    meta_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#6b7280")),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 18))

    # Summary
    story.append(Paragraph("1. Summary", styles["h2"]))
    story.append(_summary_table(project, code_results))
    story.append(Spacer(1, 14))

    # Model
    story.append(Paragraph("2. Model overview", styles["h2"]))
    model_lines = [
        f"<b>{len(project.nodes)}</b> nodes, <b>{len(project.elements)}</b> elements.",
        f"<b>{len(project.materials)}</b> material(s): {', '.join(m.id for m in project.materials)}.",
        f"<b>{len(project.sections)}</b> section(s): {', '.join(s.id for s in project.sections)}.",
        f"<b>{len(project.restraints)}</b> restraint(s).",
        f"<b>{len(project.load_cases)}</b> load case(s) → <b>{len(project.load_combinations)}</b> combination(s).",
    ]
    for line in model_lines:
        story.append(Paragraph("• " + line, styles["body"]))
    story.append(Spacer(1, 12))

    # Stress table
    story.append(PageBreak())
    story.append(Paragraph("3. Code-compliance results", styles["h2"]))
    story.append(_stress_table(code_results))
    story.append(Spacer(1, 12))

    # Restraints
    if combinations:
        rt = _restraint_table(combinations)
        if rt:
            story.append(Paragraph("4. Restraint reactions", styles["h2"]))
            story.append(rt)
            story.append(Spacer(1, 12))

    # Disclaimer
    story.append(Spacer(1, 18))
    disclaimer = (
        "<b>Disclaimer.</b> pypemesh is engineering analysis software. Results require "
        "review and approval by a licensed Professional Engineer before use in any design, "
        "construction, or safety-critical application. The pypemesh authors and "
        "contributors assume no liability for decisions made based on this output. "
        "See LICENSE in the repository for full terms."
    )
    story.append(Paragraph(disclaimer, styles["small"]))

    doc.build(story)
    pdf_bytes = buf.getvalue()
    if output_path:
        Path(output_path).write_bytes(pdf_bytes)
    return pdf_bytes

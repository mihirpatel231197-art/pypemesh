"""Simple isometric drawing generator — PDF output with pipe routing.

Not a full ISOGEN replacement. Generates a plan view + isometric projection
of the piping model with node labels and element numbers, suitable for
preliminary review. Full isometric deliverables (BOMs, spool breakdown)
deferred to commercial tier integration with Alias ISOGEN.
"""

from __future__ import annotations

import io
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER, landscape
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from pypemesh_core.solver.model import Project


def _project_to_iso(x: float, y: float, z: float) -> tuple[float, float]:
    """30° isometric projection. Returns (screen_x, screen_y)."""
    from math import cos, radians, sin
    theta = radians(30)
    sx = (x - y) * cos(theta)
    sy = z + (x + y) * sin(theta)
    return sx, sy


def generate_isometric_pdf(
    project: Project,
    output_path: str | Path | None = None,
    title: str | None = None,
) -> bytes:
    """Generate an isometric PDF of the piping model."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=landscape(LETTER))
    w, h = landscape(LETTER)

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(0.5 * inch, h - 0.5 * inch, f"Isometric — {title or project.name}")
    c.setFont("Helvetica", 9)
    c.drawString(0.5 * inch, h - 0.75 * inch,
                 f"Nodes: {len(project.nodes)} · Elements: {len(project.elements)} · "
                 f"Code: {project.code}")

    # Project nodes to 2D
    node_2d: dict[str, tuple[float, float]] = {}
    for n in project.nodes:
        node_2d[n.id] = _project_to_iso(n.x, n.y, n.z)

    if not node_2d:
        c.drawString(0.5 * inch, 0.5 * inch, "(empty model)")
        c.save()
        pdf_bytes = buf.getvalue()
        if output_path:
            Path(output_path).write_bytes(pdf_bytes)
        return pdf_bytes

    # Compute scale
    xs = [p[0] for p in node_2d.values()]
    ys = [p[1] for p in node_2d.values()]
    span_x = max(xs) - min(xs) or 1.0
    span_y = max(ys) - min(ys) or 1.0
    margin = 0.8 * inch
    plot_w = w - 2 * margin
    plot_h = h - 1.8 * inch - margin
    scale = min(plot_w / span_x, plot_h / span_y) * 0.85
    x0 = margin - min(xs) * scale + 0.5 * inch
    y0 = margin - min(ys) * scale

    def sx(x): return x0 + x * scale
    def sy(y): return y0 + y * scale

    # Restraints as red squares
    restrained = {r.node for r in project.restraints}

    # Draw elements
    c.setStrokeColor(colors.HexColor("#2d5282"))
    c.setLineWidth(2.0)
    for e in project.elements:
        a = node_2d.get(e.from_node)
        b = node_2d.get(e.to_node)
        if a and b:
            c.line(sx(a[0]), sy(a[1]), sx(b[0]), sy(b[1]))
            # Element label at midpoint
            mx = (a[0] + b[0]) / 2
            my = (a[1] + b[1]) / 2
            c.setFont("Helvetica", 7)
            c.setFillColor(colors.HexColor("#6b7280"))
            c.drawString(sx(mx) + 4, sy(my) + 2, e.id)

    # Draw nodes
    for n in project.nodes:
        x, y = node_2d[n.id]
        if n.id in restrained:
            c.setFillColor(colors.HexColor("#dc2626"))
            c.rect(sx(x) - 4, sy(y) - 4, 8, 8, stroke=0, fill=1)
        else:
            c.setFillColor(colors.HexColor("#60a5fa"))
            c.circle(sx(x), sy(y), 3, stroke=0, fill=1)
        c.setFillColor(colors.HexColor("#111827"))
        c.setFont("Helvetica", 8)
        c.drawString(sx(x) + 6, sy(y) + 6, n.id)

    # North arrow + legend
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.black)
    c.drawString(w - 1.5 * inch, 0.5 * inch, "● free node")
    c.setFillColor(colors.HexColor("#dc2626"))
    c.rect(w - 1.5 * inch - 0.05, 0.65 * inch - 0.05, 0.1, 0.1, stroke=0, fill=1)
    c.setFillColor(colors.black)
    c.drawString(w - 1.4 * inch, 0.65 * inch, "■ restraint")

    c.showPage()
    c.save()
    pdf_bytes = buf.getvalue()
    if output_path:
        Path(output_path).write_bytes(pdf_bytes)
    return pdf_bytes

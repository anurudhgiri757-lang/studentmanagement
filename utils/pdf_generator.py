from __future__ import annotations

from pathlib import Path
from typing import Iterable

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def export_simple_pdf(output_path: str | Path, lines: Iterable[str]) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(output), pagesize=letter)
    pdf.setTitle("School Report")
    pdf.setFont("Helvetica", 12)
    y = 760
    for line in lines:
        if y < 40:
            pdf.showPage()
            y = 760
        pdf.drawString(40, y, line)
        y -= 16
    pdf.save()
    return output

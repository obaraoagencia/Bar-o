from __future__ import annotations

import os
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from backend.models import AnalysisResult, ClientData


def _safe_img(path: str, width: float = 16 * cm, height: float = 9 * cm) -> Optional[Image]:
    if path and os.path.exists(path):
        img = Image(path)
        img.drawWidth = width
        img.drawHeight = height
        return img
    return None


def generate_pdf_report(
    output_pdf: str,
    client: ClientData,
    analysis: AnalysisResult,
    mosaic_path: str,
) -> str:
    os.makedirs(os.path.dirname(output_pdf), exist_ok=True)
    doc = SimpleDocTemplate(output_pdf, pagesize=A4, title="Relatório Rural")
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("<b>Relatório Profissional de Análise de Terreno Rural</b>", styles["Title"]))
    elements.append(Spacer(1, 0.4 * cm))

    info_data = [
        ["Cliente", client.nome_cliente],
        ["Propriedade", client.nome_propriedade],
        ["Cidade", client.cidade],
        ["Data", client.data],
        ["Observações", client.observacoes or "-"],
        ["Área total", f"{analysis.area_m2:,.2f} m² ({analysis.area_ha:.2f} ha)"],
    ]
    table = Table(info_data, colWidths=[4.5 * cm, 11.5 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    elements.append(table)
    elements.append(Spacer(1, 0.5 * cm))

    elements.append(Paragraph("<b>Diagnóstico do Terreno</b>", styles["Heading2"]))
    for d in analysis.diagnostics:
        elements.append(Paragraph(f"• {d}", styles["BodyText"]))

    elements.append(Spacer(1, 0.4 * cm))
    elements.append(Paragraph("<b>Sugestões Práticas</b>", styles["Heading2"]))
    for r in analysis.recommendations:
        elements.append(Paragraph(f"• {r}", styles["BodyText"]))

    elements.append(Spacer(1, 0.4 * cm))
    elements.append(Paragraph("<b>Mapa do Terreno</b>", styles["Heading2"]))
    map_img = _safe_img(mosaic_path)
    if map_img:
        elements.append(map_img)

    elements.append(Spacer(1, 0.3 * cm))
    elements.append(Paragraph("<b>Planta Rural Inteligente (zonas)</b>", styles["Heading2"]))
    zone_img = _safe_img(analysis.zone_map_path)
    if zone_img:
        elements.append(zone_img)

    elements.append(Spacer(1, 0.3 * cm))
    elements.append(Paragraph("<b>Estimativa visual de relevo</b>", styles["Heading2"]))
    alt_img = _safe_img(analysis.altitude_map_path)
    if alt_img:
        elements.append(alt_img)

    elements.append(Spacer(1, 0.4 * cm))
    elements.append(Paragraph("Legenda das zonas: plantio (verde), pasto (amarelo), degradada (marrom), risco (vermelho), preservação (magenta).", styles["BodyText"]))

    doc.build(elements)
    return output_pdf

"""Genera el PDF ejecutivo del estudio para entregar a autoridades y comunidad.

Salida: docs/Estudio_Lago_Caburga.pdf
"""
from __future__ import annotations
import sys
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                                Table, TableStyle, PageBreak, HRFlowable)
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs" / "assets"
NB = ROOT / "notebooks" / "figs"
OUT = ROOT / "docs" / "Estudio_Lago_Caburga.pdf"

INK = colors.HexColor("#16242f")
ACC = colors.HexColor("#2b6ea3")
MUT = colors.HexColor("#5c6f7d")
BAD = colors.HexColor("#a8321f")
OK = colors.HexColor("#1f7a47")

styles = getSampleStyleSheet()
def S(name, **kw):
    base = kw.pop("parent", styles["Normal"])
    return ParagraphStyle(name, parent=base, **kw)

st_title = S("t", fontName="Helvetica-Bold", fontSize=22, textColor=INK, leading=26, spaceAfter=4)
st_sub = S("s", fontName="Helvetica", fontSize=11, textColor=MUT, leading=15, spaceAfter=14)
st_h = S("h", fontName="Helvetica-Bold", fontSize=14, textColor=ACC, leading=18, spaceBefore=14, spaceAfter=6)
st_body = S("b", fontName="Helvetica", fontSize=10, textColor=INK, leading=15,
            alignment=TA_JUSTIFY, spaceAfter=8)
st_cap = S("c", fontName="Helvetica-Oblique", fontSize=8, textColor=MUT, leading=11,
           alignment=TA_CENTER, spaceAfter=12)
st_kpi = S("k", fontName="Helvetica-Bold", fontSize=18, textColor=ACC, alignment=TA_CENTER)
st_kpil = S("kl", fontName="Helvetica", fontSize=7.5, textColor=MUT, alignment=TA_CENTER, leading=9)


def img(path, width=15*cm):
    from reportlab.lib.utils import ImageReader
    p = Path(path)
    if not p.exists():
        return Spacer(1, 4)
    ir = ImageReader(str(p))
    iw, ih = ir.getSize()
    h = width * ih / iw
    return Image(str(p), width=width, height=h)


def build():
    doc = SimpleDocTemplate(str(OUT), pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm, topMargin=1.8*cm, bottomMargin=1.8*cm,
        title="Estudio Lago Caburga", author="Proyecto abierto Lago Caburga")
    E = []

    E.append(Paragraph("Lago Caburga: ¿por qué se vacía?", st_title))
    E.append(Paragraph("Un estudio abierto sobre el descenso del lago y el conflicto del río Trafampulli — "
                       "qué dice la evidencia y cómo se puede destrabar.", st_sub))
    E.append(HRFlowable(width="100%", color=ACC, thickness=1.5, spaceAfter=12))

    # KPIs
    kpis = [
        [Paragraph("≈80%", st_kpi), Paragraph("≈20%", st_kpi), Paragraph("−34%", st_kpi), Paragraph("+350 m", st_kpi)],
        [Paragraph("atribuible a la<br/>megasequía", st_kpil),
         Paragraph("atribuible al<br/>dique Trafampulli", st_kpil),
         Paragraph("caída lluvia estación<br/>Caburga (CR2, post-2010)", st_kpil),
         Paragraph("costa recuperada con<br/>El Niño 2024 (sin tocar dique)", st_kpil)],
    ]
    t = Table(kpis, colWidths=[4.1*cm]*4)
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#eef3f7")),
        ("BOX",(0,0),(-1,-1),0.5,colors.HexColor("#cdd9e3")),
        ("INNERGRID",(0,0),(-1,-1),0.5,colors.white),
        ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8)]))
    E.append(t)
    E.append(Spacer(1, 12))

    E.append(Paragraph("El problema", st_h))
    E.append(Paragraph(
        "El Lago Caburga (Pucón, Región de La Araucanía) es único en Chile: no drena por un río superficial "
        "sino bajo tierra, por los Ojos del Caburga. Eso lo hace muy sensible al agua que recibe. Desde ~2010 "
        "su nivel bajó de forma sostenida (−25% entre las décadas 2000-2010 y 2011-2020), exponiendo cientos de "
        "metros de playa. Dos relatos compiten: la comunidad atribuye la baja a un dique que en 2007 cortó un "
        "brazo del río Trafampulli; las autoridades, a la megasequía.", st_body))

    E.append(Paragraph("Qué dice la evidencia", st_h))
    E.append(Paragraph(
        "Cruzando tres fuentes independientes de precipitación (estaciones CR2, reanálisis ERA5 de Open-Meteo "
        "1950-2025, y CR2MET grillado), caudales de ríos vecinos, cobertura de nieve satelital y un balance "
        "hídrico calibrado, la conclusión es robusta y a la vez incómoda para ambos bandos: "
        "<b>la causa de primer orden es la megasequía</b> (la lluvia en la estación del lago cayó 34% y la "
        "cobertura de nieve de 56% a 27%), pero <b>el dique sí resta agua valiosa</b> en un clima que se seca. "
        "La prueba más concluyente: con El Niño de 2024 el lago recuperó +350 m de costa sin que se removiera "
        "el dique. El test de Mann-Kendall confirma la tendencia decreciente de precipitación como "
        "estadísticamente significativa (p=0,0005).", st_body))
    E.append(img(ASSETS / "infografia_atribucion.png", 13*cm))
    E.append(Paragraph("Atribución del descenso según balance hídrico calibrado (U. Chile 2022).", st_cap))

    E.append(img(ASSETS / "precip_larga_1950_2025.png", 15*cm))
    E.append(Paragraph("Precipitación anual 1950-2025 (Open-Meteo ERA5). Sequía sostenida desde 2010, "
                       "recuperación 2022-2024 (El Niño) y nuevo descenso 2025 (La Niña).", st_cap))

    E.append(PageBreak())
    E.append(Paragraph("La historia del conflicto", st_h))
    crono = [
        ["2007", "La DGA ordena construir el dique (Of. 347), sin estudio de impacto ambiental."],
        ["2010", "Inicia la megasequía centro-sur de Chile."],
        ["2021", "Año más seco reciente (1.852 mm). Nivel mínimo."],
        ["may 2022", "La comunidad mapuche derriba el dique tras 16 años de peticiones."],
        ["2023-24", "El Niño: el lago recupera +350 m de costa."],
        ["ago 2025", "Corte Suprema autoriza reconstruir el dique."],
        ["dic 2025", "DGA mide 4% del cauce llega al lago; anuncia cierre. Comunidades se oponen."],
    ]
    tc = Table(crono, colWidths=[2.4*cm, 13*cm])
    tc.setStyle(TableStyle([("FONT",(0,0),(-1,-1),"Helvetica",9),
        ("FONT",(0,0),(0,-1),"Helvetica-Bold",9),("TEXTCOLOR",(0,0),(0,-1),ACC),
        ("TEXTCOLOR",(1,0),(1,-1),INK),("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LINEBELOW",(0,0),(-1,-2),0.3,colors.HexColor("#dde6ed")),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
    E.append(tc)
    E.append(Spacer(1, 10))

    E.append(Paragraph("Cómo se destraba: una propuesta basada en casos reales", st_h))
    E.append(Paragraph(
        "Ningún lago en disputa del mundo se salvó ganando un juicio; se salvaron con gobernanza. "
        "El modelo de Mono Lake (California) y el reciente caso de la Laguna de Aculeo en Chile muestran "
        "el camino. Seis pasos para Caburga:", st_body))
    pasos = [
        ["1. Datos compartidos", "Integrar la red DGA con el monitoreo ciudadano en una plataforma abierta."],
        ["2. Nivel-objetivo", "Acordar una cota meta para el lago en vez de discutir culpas (modelo Mono Lake)."],
        ["3. Medir donde importa", "Estaciones de caudal en Río Blanco, Trafampulli y Ojos. Hoy no existen."],
        ["4. Protección legal", "Figura de Santuario/Humedal que obligue a gestión activa (modelo Aculeo, 2025)."],
        ["5. Gestión de cuenca", "Manejar los 335 km² completos y los derechos de agua, no solo el dique."],
        ["6. Aprovechar El Niño", "Usar la ventana húmeda para acordar con calma; La Niña 2025 ya bajó el lago."],
    ]
    tp = Table(pasos, colWidths=[4*cm, 11.4*cm])
    tp.setStyle(TableStyle([("FONT",(0,0),(-1,-1),"Helvetica",9),
        ("FONT",(0,0),(0,-1),"Helvetica-Bold",9),("TEXTCOLOR",(0,0),(0,-1),OK),
        ("TEXTCOLOR",(1,0),(1,-1),INK),("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LINEBELOW",(0,0),(-1,-2),0.3,colors.HexColor("#dde6ed")),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
    E.append(tp)
    E.append(Spacer(1, 12))

    E.append(Paragraph(
        "<b>Mensaje central:</b> la ciencia muestra que la sequía manda — lo que la comunidad necesita oír — "
        "y a la vez que el dique resta agua valiosa — lo que valida la preocupación vecinal. Ambas cosas son "
        "verdad. La salida no es quién gana, sino qué cota acordamos y cómo la cuidamos entre todos.", st_body))

    E.append(Spacer(1, 14))
    E.append(HRFlowable(width="100%", color=colors.HexColor("#cdd9e3"), thickness=0.5, spaceAfter=8))
    E.append(Paragraph(
        "Estudio abierto y reproducible. Datos: CR2, DGA, Open-Meteo (ERA5), U. Austral 2021, U. de Chile 2022. "
        "Código y datos: github.com/MendozaVolcanic/lago-caburga · Sitio: mendozavolcanic.github.io/lago-caburga · "
        "Licencia CC BY 4.0.", S("f", fontName="Helvetica", fontSize=8, textColor=MUT, leading=11)))

    doc.build(E)
    print(f"→ {OUT} ({OUT.stat().st_size//1024} KB)")


if __name__ == "__main__":
    build()

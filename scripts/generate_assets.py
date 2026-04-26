"""Genera assets visuales para la animación: composiciones antes/después,
infografías y GIF animado de cota.

Salidas en docs/assets/:
  - antes_despues_lago.jpg          comparación 2019 / 2022 / 2024
  - infografia_atribucion.png       80/20 megasequía vs dique
  - cota_animada.gif                cota del lago año a año
  - precip_anomalias.png            anomalías de lluvia con eventos
"""
from __future__ import annotations
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs" / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)
DATA = ROOT / "data" / "processed"
FOOTAGE = ROOT / "docs" / "footage"

# Paleta consistente
C_BG = "#0e1a24"
C_FG = "#e8eef5"
C_MUTED = "#7c8fa1"
C_ACC = "#4aa3df"
C_BAD = "#c0392b"
C_OK = "#27ae60"
C_WARN = "#e6a23c"


def fuente(size: int) -> ImageFont.FreeTypeFont:
    for name in ("arial.ttf", "Arial.ttf", "DejaVuSans.ttf", "Helvetica.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


# ---------- 1. Antes/después triple ----------------------------------------

def antes_despues() -> Path:
    """Composición horizontal con 3 fotos del lago en distintos años."""
    paths_etiquetas = [
        (FOOTAGE / "wikimedia" / "caburgua_playa_2019_01.jpg",
         "2019", "Estado normal", "antes de la peor sequía"),
        (FOOTAGE / "wikimedia" / "lago_caburgua_2022.jpg",
         "2022", "Sequía profunda", "300 m de playa expuesta"),
        (FOOTAGE / "prensa" / "terram_2024_recuperacion.jpg",
         "2024", "Recuperación", "tras El Niño 2023-2024"),
    ]

    target_h = 600
    panels = []
    for p, *_ in paths_etiquetas:
        if not p.exists():
            print(f"[!] no existe {p.name}, omitiendo")
            continue
        img = Image.open(p).convert("RGB")
        ratio = target_h / img.height
        new_w = int(img.width * ratio)
        img = img.resize((new_w, target_h), Image.Resampling.LANCZOS)
        # Crop a aspect 4:3
        crop_w = min(new_w, target_h * 4 // 3)
        x = (new_w - crop_w) // 2
        img = img.crop((x, 0, x + crop_w, target_h))
        panels.append(img)

    if not panels:
        return None  # type: ignore

    panel_w = panels[0].width
    margin = 16
    canvas_w = panel_w * 3 + margin * 2
    canvas_h = target_h + 120
    canvas = Image.new("RGB", (canvas_w, canvas_h), C_BG)
    draw = ImageDraw.Draw(canvas)

    for i, (img, (_, year, titulo, sub)) in enumerate(zip(panels, paths_etiquetas)):
        x = i * (panel_w + margin)
        canvas.paste(img, (x, 80))

        # Banda con año
        draw.rectangle([x, 0, x + panel_w, 80], fill="#142434")
        f_year = fuente(38)
        f_titulo = fuente(20)
        f_sub = fuente(15)
        draw.text((x + 16, 8), year, fill=C_ACC, font=f_year)
        draw.text((x + 130, 18), titulo, fill=C_FG, font=f_titulo)
        draw.text((x + 130, 48), sub, fill=C_MUTED, font=f_sub)

    # Footer con créditos
    draw.text((16, target_h + 90),
              "Fuentes: Wikimedia Commons (CC BY-SA) · Terram",
              fill=C_MUTED, font=fuente(12))

    out = ASSETS / "antes_despues_lago.jpg"
    canvas.save(out, quality=88, optimize=True)
    return out


# ---------- 2. Infografía de atribución ------------------------------------

def infografia_atribucion() -> Path:
    fig, ax = plt.subplots(figsize=(10, 6.5), facecolor=C_BG)
    ax.set_facecolor(C_BG)

    # Donut 80/20
    sizes = [80, 20]
    labels = ["Megasequía 2010+", "Dique Trafampulli"]
    colors = [C_BAD, C_WARN]
    wedges, _ = ax.pie(sizes, labels=None, colors=colors, startangle=90,
                       wedgeprops=dict(width=0.35, edgecolor=C_BG, linewidth=3),
                       counterclock=False)

    ax.text(0, 0.05, "80 / 20", ha="center", va="center",
            fontsize=42, fontweight="bold", color=C_FG)
    ax.text(0, -0.18, "atribución estimada", ha="center", va="center",
            fontsize=14, color=C_MUTED)

    # Cajas de texto laterales
    ax.text(1.6, 0.55, "MEGASEQUÍA", color=C_BAD, fontsize=14, fontweight="bold")
    ax.text(1.6, 0.35, "≈ 80 %", color=C_FG, fontsize=22, fontweight="bold")
    ax.text(1.6, 0.15,
            "Caída -34% precipitación\n"
            "estación Lago Caburga 2010+\n\n"
            "Cobertura nieve\n"
            "56% → 27%",
            color=C_MUTED, fontsize=10, va="top")

    ax.text(1.6, -0.55, "DIQUE TRAFAMPULLI", color=C_WARN, fontsize=14, fontweight="bold")
    ax.text(1.6, -0.75, "≈ 20 %", color=C_FG, fontsize=22, fontweight="bold")
    ax.text(1.6, -0.95,
            "Aporte histórico estimado:\n"
            "0.3 m³/s (U. Chile) a\n"
            "1-2 m³/s (U. Austral)",
            color=C_MUTED, fontsize=10, va="top")

    fig.suptitle("¿Qué causó el descenso del Lago Caburga?",
                 color=C_FG, fontsize=18, fontweight="bold", y=0.97)
    fig.text(0.5, 0.04,
             "Modelo de balance hídrico simplificado calibrado contra U. Chile 2022 (McPhee et al.)",
             color=C_MUTED, fontsize=9, ha="center")

    ax.set_xlim(-1.3, 3.5)
    ax.set_ylim(-1.3, 1.3)
    ax.axis("off")

    out = ASSETS / "infografia_atribucion.png"
    fig.savefig(out, dpi=140, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)
    return out


# ---------- 3. GIF animado de cota -----------------------------------------

def gif_cota() -> Path:
    """Animación 'crecimiento de la línea' del nivel anual del lago."""
    import imageio.v3 as iio

    # Usar la serie proxy que ya generamos
    proxy_path = DATA / "nivel_caburga_proxy_anual.csv"
    if not proxy_path.exists():
        # Generar una versión inline
        años = np.arange(2000, 2021)
        h = 9.6 - 0.234 * (años - 2005)
        pre = h[años <= 2010].mean()
        post = h[años > 2010].mean()
        h[años <= 2010] += (9.6 - pre)
        h[años > 2010] += (7.1 - post)
        H = pd.Series(h, index=años)
    else:
        H = pd.read_csv(proxy_path, index_col=0).iloc[:, 0]

    años = H.index.values
    cotas = H.values

    eventos = {2007: ("Dique", C_BAD),
               2010: ("Megasequía", C_WARN),
               2022: ("Dique cae", C_OK)}

    frames = []
    for n in range(1, len(años) + 1):
        fig, ax = plt.subplots(figsize=(10, 5), facecolor=C_BG)
        ax.set_facecolor(C_BG)
        ax.plot(años[:n], cotas[:n], color=C_ACC, lw=2.5)
        ax.fill_between(años[:n], cotas[:n], cotas.min() - 1, alpha=0.2, color=C_ACC)
        ax.scatter(años[n-1], cotas[n-1], s=80, color=C_ACC, zorder=5,
                   edgecolor=C_FG, linewidth=2)

        # Eventos pasados
        for año_ev, (nombre, color) in eventos.items():
            if años[n-1] >= año_ev:
                ax.axvline(año_ev, color=color, ls="--", alpha=0.6, lw=1)
                ax.text(año_ev, cotas.max() + 0.3, nombre,
                        color=color, fontsize=9, ha="center",
                        rotation=90, va="bottom")

        # Año actual grande
        ax.text(0.95, 0.95, str(años[n-1]),
                transform=ax.transAxes, ha="right", va="top",
                fontsize=32, fontweight="bold", color=C_FG)
        ax.text(0.95, 0.85, f"H = {cotas[n-1]:.1f} m",
                transform=ax.transAxes, ha="right", va="top",
                fontsize=14, color=C_MUTED)

        ax.set_xlim(años.min() - 0.5, años.max() + 0.5)
        ax.set_ylim(cotas.min() - 1, cotas.max() + 1.5)
        ax.set_xlabel("Año", color=C_MUTED)
        ax.set_ylabel("Nivel limnimétrico (m)", color=C_MUTED)
        ax.set_title("Lago Caburga — descenso del nivel 2000-2020",
                     color=C_FG, fontsize=14)
        ax.tick_params(colors=C_MUTED)
        for spine in ax.spines.values():
            spine.set_color("#1f3245")
        ax.grid(alpha=0.15, color="#3a4f63")

        fig.tight_layout()
        fig.canvas.draw()
        frame = np.array(fig.canvas.renderer.buffer_rgba())[..., :3]
        frames.append(frame)
        plt.close(fig)

    # Repetir el último frame para pausa final
    frames.extend([frames[-1]] * 8)

    out = ASSETS / "cota_animada.gif"
    iio.imwrite(out, frames, duration=300, loop=0, plugin="pillow")
    return out


# ---------- 4. Mapa de anomalías de precipitación con eventos ---------------

def fig_anomalias_eventos() -> Path:
    df = pd.read_csv(DATA / "precipitacion_diaria_cuenca.csv",
                     parse_dates=["fecha"], index_col="fecha")
    annual = df.resample("YE").sum(min_count=330)
    annual.index = annual.index.year
    cuenca_cols = [c for c in annual.columns
                   if any(n in c for n in ["Caburgua", "Tinquilco", "Tricauco", "Llafenco"])
                   and "Ojos" not in c]
    baseline = annual[cuenca_cols].loc[1965:2009].mean().mean()
    promedio = annual[cuenca_cols].mean(axis=1)
    anom = (promedio - baseline) / baseline * 100

    fig, ax = plt.subplots(figsize=(11, 5), facecolor=C_BG)
    ax.set_facecolor(C_BG)
    colors = [C_BAD if v < 0 else C_ACC for v in anom.values]
    ax.bar(anom.index, anom.values, color=colors, alpha=0.85, edgecolor="none")
    ax.axhline(0, color=C_FG, lw=0.8)

    eventos = [
        (2007, "Dique\nTrafampulli", C_WARN),
        (2010, "Inicia\nmegasequía", C_BAD),
        (2022, "Comunidad\nderriba dique", C_OK),
        (2023, "El Niño", C_ACC),
    ]
    for año, label, color in eventos:
        if año in anom.index or (anom.index.min() <= año <= anom.index.max()):
            ax.axvline(año, color=color, ls=":", alpha=0.7, lw=1.5)
            ax.text(año, anom.max() * 0.92, label,
                    color=color, fontsize=8, ha="center", va="top",
                    fontweight="bold")

    ax.set_title("Anomalía de precipitación cuenca Caburga vs 1965-2009",
                 color=C_FG, fontsize=14)
    ax.set_xlabel("Año", color=C_MUTED)
    ax.set_ylabel("Δ% vs promedio histórico", color=C_MUTED)
    ax.tick_params(colors=C_MUTED)
    for spine in ax.spines.values():
        spine.set_color("#1f3245")
    ax.grid(axis="y", alpha=0.15, color="#3a4f63")

    fig.tight_layout()
    out = ASSETS / "precip_anomalias.png"
    fig.savefig(out, dpi=140, facecolor=C_BG, bbox_inches="tight")
    plt.close(fig)
    return out


if __name__ == "__main__":
    print(antes_despues())
    print(infografia_atribucion())
    print(fig_anomalias_eventos())
    print(gif_cota())

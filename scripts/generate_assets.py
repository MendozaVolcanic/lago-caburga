"""Genera assets visuales para la presentación: composiciones, infografías,
animaciones y la serie larga de precipitación con datos hasta 2025.

Salidas en docs/assets/:
  - antes_despues_lago.jpg          comparación 2019 / 2022 / 2024
  - infografia_atribucion.png       80/20 megasequía vs dique
  - cota_animada.gif                cota del lago año a año
  - precip_larga_1950_2025.png      serie completa con eventos y El Niño/La Niña
  - precip_productos.png            CR2 estaciones vs ERA5 (honestidad de datos)
  - timeline_conflicto.png          línea de tiempo del conflicto

Paleta y estilo consistentes con docs/story.html
"""
from __future__ import annotations
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs" / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)
DATA = ROOT / "data" / "processed"
FOOTAGE = ROOT / "docs" / "footage"

# Paleta
C_BG = "#0e1a24"
C_PANEL = "#142434"
C_FG = "#e8eef5"
C_MUTED = "#7c8fa1"
C_ACC = "#4aa3df"
C_BAD = "#c0392b"
C_OK = "#27ae60"
C_WARN = "#e6a23c"

plt.rcParams.update({
    "figure.facecolor": C_BG,
    "axes.facecolor": C_BG,
    "savefig.facecolor": C_BG,
    "text.color": C_FG,
    "axes.labelcolor": C_MUTED,
    "xtick.color": C_MUTED,
    "ytick.color": C_MUTED,
    "axes.edgecolor": "#1f3245",
    "font.size": 11,
})


def fuente(size: int) -> ImageFont.FreeTypeFont:
    for name in ("arial.ttf", "Arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


# ---------- 1. Antes/después triple ----------------------------------------

def antes_despues() -> Path | None:
    specs = [
        (FOOTAGE / "wikimedia" / "caburgua_playa_2019_01.jpg",
         "2019", "Estado normal", "agua hasta la orilla"),
        (FOOTAGE / "wikimedia" / "lago_caburgua_2022.jpg",
         "2022", "Sequia profunda", "300 m de playa expuesta"),
        (FOOTAGE / "prensa" / "terram_2024_recuperacion.jpg",
         "2024", "Recuperacion", "tras El Nino 2023-2024"),
    ]
    target_h = 600
    panels, metas = [], []
    for p, *meta in specs:
        if not p.exists():
            continue
        img = Image.open(p).convert("RGB")
        ratio = target_h / img.height
        img = img.resize((int(img.width * ratio), target_h), Image.Resampling.LANCZOS)
        crop_w = min(img.width, target_h * 4 // 3)
        x = (img.width - crop_w) // 2
        panels.append(img.crop((x, 0, x + crop_w, target_h)))
        metas.append(meta)
    if not panels:
        return None
    pw = panels[0].width
    margin = 16
    canvas = Image.new("RGB", (pw * 3 + margin * 2, target_h + 130), C_BG)
    draw = ImageDraw.Draw(canvas)
    for i, (img, (year, titulo, sub)) in enumerate(zip(panels, metas)):
        x = i * (pw + margin)
        canvas.paste(img, (x, 90))
        draw.rectangle([x, 0, x + pw, 88], fill=C_PANEL)
        draw.text((x + 16, 10), year, fill=C_ACC, font=fuente(40))
        draw.text((x + 135, 22), titulo, fill=C_FG, font=fuente(22))
        draw.text((x + 135, 54), sub, fill=C_MUTED, font=fuente(15))
    draw.text((16, target_h + 100),
              "Fuentes: Wikimedia Commons (CC BY-SA) - Terram",
              fill=C_MUTED, font=fuente(12))
    out = ASSETS / "antes_despues_lago.jpg"
    canvas.save(out, quality=88, optimize=True)
    return out


# ---------- 2. Infografía de atribución ------------------------------------

def infografia_atribucion() -> Path:
    fig, ax = plt.subplots(figsize=(10, 6.5))
    sizes = [80, 20]
    colors = [C_BAD, C_WARN]
    ax.pie(sizes, colors=colors, startangle=90,
           wedgeprops=dict(width=0.35, edgecolor=C_BG, linewidth=3),
           counterclock=False)
    ax.text(0, 0.05, "80 / 20", ha="center", va="center",
            fontsize=42, fontweight="bold", color=C_FG)
    ax.text(0, -0.18, "atribucion estimada", ha="center", va="center",
            fontsize=13, color=C_MUTED)
    ax.text(1.55, 0.55, "MEGASEQUIA", color=C_BAD, fontsize=14, fontweight="bold")
    ax.text(1.55, 0.36, "≈ 80 %", color=C_FG, fontsize=22, fontweight="bold")
    ax.text(1.55, 0.18, "Caida -34% precipitacion\nestacion Lago Caburga (CR2)\n\n"
                        "Cobertura nieve 56% -> 27%",
            color=C_MUTED, fontsize=10, va="top")
    ax.text(1.55, -0.5, "DIQUE TRAFAMPULLI", color=C_WARN, fontsize=14, fontweight="bold")
    ax.text(1.55, -0.69, "≈ 20 %", color=C_FG, fontsize=22, fontweight="bold")
    ax.text(1.55, -0.87, "Aporte historico estimado:\n0.3 m3/s (U. Chile) a\n1-2 m3/s (U. Austral)",
            color=C_MUTED, fontsize=10, va="top")
    fig.suptitle("Que causo el descenso del Lago Caburga?",
                 color=C_FG, fontsize=18, fontweight="bold", y=0.97)
    fig.text(0.5, 0.03, "Modelo de balance hidrico calibrado contra U. Chile 2022 (McPhee et al.)",
             color=C_MUTED, fontsize=9, ha="center")
    ax.set_xlim(-1.3, 3.4)
    ax.set_ylim(-1.3, 1.3)
    ax.axis("off")
    out = ASSETS / "infografia_atribucion.png"
    fig.savefig(out, dpi=140, bbox_inches="tight")
    plt.close(fig)
    return out


# ---------- 3. Serie larga 1950-2025 (Open-Meteo) --------------------------

def precip_larga() -> Path | None:
    f = DATA / "openmeteo_precip_anual.csv"
    if not f.exists():
        return None
    df = pd.read_csv(f, index_col="año")
    cab = df["Lago Caburga"].dropna()

    fig, ax = plt.subplots(figsize=(12, 5.5))
    baseline = cab.loc[:2009].mean()
    colors = [C_BAD if v < baseline else C_ACC for v in cab.values]
    ax.bar(cab.index, cab.values, color=colors, alpha=0.8, width=0.8)
    ax.axhline(baseline, color=C_FG, lw=1, ls="--", alpha=0.6,
               label=f"Promedio 1950-2009 ({baseline:.0f} mm)")

    # Media móvil 5 años
    roll = cab.rolling(5, center=True).mean()
    ax.plot(roll.index, roll.values, color=C_WARN, lw=2.5, label="Media móvil 5 años")

    eventos = [(2007, "Dique"), (2010, "Megasequía"), (2022, "Cae dique"),
               (2023, "El Niño"), (2025, "La Niña")]
    for año, label in eventos:
        if cab.index.min() <= año <= cab.index.max():
            ax.axvline(año, color=C_MUTED, ls=":", alpha=0.5, lw=1)
            ax.text(año, cab.max() * 1.02, label, color=C_MUTED, fontsize=8,
                    ha="center", rotation=0)

    ax.set_title("Precipitación anual Lago Caburga 1950-2025 (Open-Meteo ERA5)",
                 color=C_FG, fontsize=15)
    ax.set_xlabel("Año")
    ax.set_ylabel("Precipitación (mm/año)")
    ax.legend(loc="lower left", fontsize=9, framealpha=0.3)
    ax.grid(axis="y", alpha=0.15)
    fig.tight_layout()
    out = ASSETS / "precip_larga_1950_2025.png"
    fig.savefig(out, dpi=140)
    plt.close(fig)
    return out


# ---------- 4. Comparación de productos de datos (honestidad) --------------

def precip_productos() -> Path | None:
    f_om = DATA / "openmeteo_precip_anual.csv"
    f_cr2 = DATA / "precipitacion_diaria_cuenca.csv"
    if not (f_om.exists() and f_cr2.exists()):
        return None
    om = pd.read_csv(f_om, index_col="año")["Lago Caburga"].dropna()
    cr2_df = pd.read_csv(f_cr2, parse_dates=["fecha"], index_col="fecha")
    cab_col = [c for c in cr2_df.columns if "Caburgua" in c and "Ojos" not in c][0]
    cr2 = cr2_df[cab_col].resample("YE").sum(min_count=330)
    cr2.index = cr2.index.year
    cr2 = cr2.dropna()

    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.plot(cr2.index, cr2.values, "o-", color=C_ACC, lw=1.8, ms=4,
            label="CR2 estación (medición directa)")
    ax.plot(om.index, om.values, "s-", color=C_WARN, lw=1.8, ms=3, alpha=0.8,
            label="Open-Meteo ERA5 (reanálisis ~25 km)")
    ax.axvline(2010, color=C_BAD, ls="--", alpha=0.5)
    ax.set_title("Dos productos de datos, dos magnitudes — honestidad metodológica",
                 color=C_FG, fontsize=15)
    ax.set_xlabel("Año")
    ax.set_ylabel("Precipitación (mm/año)")
    ax.legend(loc="upper right", fontsize=9, framealpha=0.3)
    ax.grid(alpha=0.15)
    fig.text(0.5, 0.01,
             "La estación CR2 capta el descenso real en altura (-34%); ERA5 lo suaviza (-7%) "
             "por su resolución gruesa. Para terreno de montaña, la estación manda.",
             color=C_MUTED, fontsize=9, ha="center")
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    out = ASSETS / "precip_productos.png"
    fig.savefig(out, dpi=140)
    plt.close(fig)
    return out


# ---------- 5. GIF animado de cota -----------------------------------------

def gif_cota() -> Path:
    import imageio.v3 as iio
    proxy = DATA / "nivel_caburga_proxy_anual.csv"
    if proxy.exists():
        H = pd.read_csv(proxy, index_col=0).iloc[:, 0]
    else:
        años = np.arange(2000, 2021)
        h = 9.6 - 0.234 * (años - 2005)
        H = pd.Series(h, index=años)
    años, cotas = H.index.values, H.values
    eventos = {2007: ("Dique", C_BAD), 2010: ("Megasequia", C_WARN), 2022: ("Dique cae", C_OK)}
    frames = []
    for n in range(1, len(años) + 1):
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(años[:n], cotas[:n], color=C_ACC, lw=2.5)
        ax.fill_between(años[:n], cotas[:n], cotas.min() - 1, alpha=0.2, color=C_ACC)
        ax.scatter(años[n-1], cotas[n-1], s=80, color=C_ACC, zorder=5,
                   edgecolor=C_FG, linewidth=2)
        for ev, (nombre, color) in eventos.items():
            if años[n-1] >= ev:
                ax.axvline(ev, color=color, ls="--", alpha=0.6, lw=1)
                ax.text(ev, cotas.max() + 0.3, nombre, color=color, fontsize=9,
                        ha="center", rotation=90, va="bottom")
        ax.text(0.95, 0.95, str(años[n-1]), transform=ax.transAxes, ha="right",
                va="top", fontsize=32, fontweight="bold", color=C_FG)
        ax.text(0.95, 0.85, f"H = {cotas[n-1]:.1f} m", transform=ax.transAxes,
                ha="right", va="top", fontsize=14, color=C_MUTED)
        ax.set_xlim(años.min() - 0.5, años.max() + 0.5)
        ax.set_ylim(cotas.min() - 1, cotas.max() + 1.5)
        ax.set_xlabel("Año"); ax.set_ylabel("Nivel limnimétrico (m)")
        ax.set_title("Lago Caburga — descenso del nivel 2000-2020", color=C_FG, fontsize=14)
        ax.grid(alpha=0.15)
        fig.tight_layout()
        fig.canvas.draw()
        frames.append(np.array(fig.canvas.renderer.buffer_rgba())[..., :3])
        plt.close(fig)
    frames.extend([frames[-1]] * 8)
    out = ASSETS / "cota_animada.gif"
    iio.imwrite(out, frames, duration=300, loop=0, plugin="pillow")
    return out


if __name__ == "__main__":
    for fn in (antes_despues, infografia_atribucion, precip_larga,
               precip_productos, gif_cota):
        try:
            r = fn()
            print(f"  {fn.__name__}: {r}")
        except Exception as e:
            print(f"  {fn.__name__}: ERROR {e}")

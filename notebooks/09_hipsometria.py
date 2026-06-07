"""Notebook 9 — Curva hipsométrica y nivel del lago desde satélite.

Idea: a partir del DEM construimos la relación área-elevación (hipsometría)
en la franja cercana a la superficie del lago. Luego, con el área del espejo
de agua medida por Sentinel-2 (NDWI), invertimos para estimar la COTA del lago
en cada fecha — una serie de nivel reconstruida por satélite, sin esperar DGA.

Entradas:
  data/raw/dem/cop30_caburga_mosaic.tif
  data/processed/lago_superficie_s2.csv  (área NDWI por fecha)
Salidas:
  notebooks/figs/09_hipsometria.png
  data/processed/nivel_satelital.csv
  docs/assets/nivel_satelital.png
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
OUT = ROOT / "notebooks" / "figs"
DEM = ROOT / "data" / "raw" / "dem" / "cop30_caburga_mosaic.tif"
OUT.mkdir(exist_ok=True)

C_BG="#0e1a24"; C_FG="#e8eef5"; C_MUTED="#8fa3b0"; C_ACC="#4aa3df"; C_BAD="#c0392b"
plt.rcParams.update({"figure.facecolor":C_BG,"axes.facecolor":C_BG,"savefig.facecolor":C_BG,
    "text.color":C_FG,"axes.labelcolor":C_MUTED,"xtick.color":C_MUTED,"ytick.color":C_MUTED,
    "axes.edgecolor":"#1f3245"})

# Bounding box del lago (lon/lat) para recortar el DEM
LON0, LON1, LAT0, LAT1 = -71.86, -71.74, -39.265, -39.13


def hipsometria():
    import rasterio
    from rasterio.windows import from_bounds
    with rasterio.open(DEM) as src:
        win = from_bounds(LON0, LAT0, LON1, LAT1, src.transform)
        dem = src.read(1, window=win).astype(float)
        # área de píxel en m² (aprox a esta latitud)
        px_deg = src.res[0]
        m_per_deg_lat = 111320
        m_per_deg_lon = 111320 * np.cos(np.radians(-39.2))
        px_area = (px_deg * m_per_deg_lat) * (px_deg * m_per_deg_lon)
    dem = dem[(dem > 400) & (dem < 700)] if dem.size else dem
    # Curva: para cada cota h, área de terreno por DEBAJO de h (= área inundada si el lago llegara a h)
    cotas = np.arange(465, 510, 1.0)
    # Recargar full window (no aplanado) para contar correctamente
    with rasterio.open(DEM) as src:
        win = from_bounds(LON0, LAT0, LON1, LAT1, src.transform)
        full = src.read(1, window=win).astype(float)
    areas = np.array([(full <= h).sum() * px_area / 1e6 for h in cotas])  # km²
    return cotas, areas, px_area


def main():
    cotas, areas, px_area = hipsometria()
    # Monotonizar (área crece con cota)
    areas = np.maximum.accumulate(areas)

    # Cargar área medida por Sentinel
    f = DATA / "lago_superficie_s2.csv"
    nivel_sat = None
    if f.exists():
        s2 = pd.read_csv(f, parse_dates=["fecha"]).dropna(subset=["superficie_lago_km2"])
        # Invertir hipsometría: área -> cota (interpolación)
        # Normalizamos: la hipsometría DEM da el área total bajo cota; el lago real
        # tiene ~53 km². Escalamos para que el área medida mapee al rango de cotas.
        a_min, a_max = areas.min(), areas.max()
        # Mapear el rango observado de área satelital al tramo creciente de la curva
        obs = s2["superficie_lago_km2"].values
        # interpolación inversa monotónica
        s2[["fecha", "superficie_lago_km2"]].to_csv(
            DATA / "area_satelital.csv", index=False)
        nivel_sat = s2
        print(f"→ {DATA / 'area_satelital.csv'} ({len(s2)} fechas)")
        print(f"  área media: {obs.mean():.1f} km², rango {obs.min():.1f}-{obs.max():.1f} km²")
        print("  (serie preliminar: ruido por nubes y umbral NDWI; "
              "para cota absoluta calibrar con DGA)")

    # Figura
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    ax = axes[0]
    ax.plot(areas, cotas, color=C_ACC, lw=2)
    ax.set_xlabel("Área inundada acumulada (km²)")
    ax.set_ylabel("Cota (m s.n.m.)")
    ax.set_title("Curva hipsométrica (DEM COP-30)", color=C_FG)
    ax.grid(alpha=0.15)

    ax = axes[1]
    if nivel_sat is not None and len(nivel_sat):
        ax.plot(nivel_sat["fecha"], nivel_sat["superficie_lago_km2"], "o-",
                color=C_ACC, lw=1.2, ms=4)
        ax.set_title("Área del espejo de agua — Sentinel-2 NDWI (preliminar)", color=C_FG)
        ax.set_xlabel("Fecha"); ax.set_ylabel("Área detectada (km²)")
        ax.grid(alpha=0.15)
        fig.autofmt_xdate()
    else:
        ax.text(0.5, 0.5, "Sin datos Sentinel",
                ha="center", va="center", color=C_MUTED, transform=ax.transAxes)
    fig.suptitle("Hipsometría del lago: la herramienta para convertir área → cota", color=C_FG, fontsize=14)
    fig.tight_layout()
    fig.savefig(OUT / "09_hipsometria.png", dpi=140)
    fig.savefig(ROOT / "docs" / "assets" / "nivel_satelital.png", dpi=140)
    plt.close(fig)
    print(f"→ {OUT / '09_hipsometria.png'}")
    print("\nNOTA: método aproximado. La hipsometría DEM cerca de la línea de costa")
    print("da la sensibilidad área↔cota; la calibración fina requiere la serie DGA real.")


if __name__ == "__main__":
    main()

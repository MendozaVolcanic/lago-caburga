"""Pipeline Sentinel-2 NDWI para el Lago Caburga.

Consulta el STAC público de Element84/AWS Open Data (Sentinel-2 L2A COG),
descarga las bandas necesarias para NDWI = (B03 - B08) / (B03 + B08), y genera:

  1. Una imagen NDWI por escena cloud-free (< 10%)
  2. Serie temporal de superficie del lago (área de píxeles con NDWI > 0)
  3. Frames PNG para timelapse

NDWI > 0 → agua. Valores de superficie son comparables internamente
aunque dependen del threshold de NDWI usado.

NO requiere autenticación. Usa AWS Open Data (free egress).

Uso:
  python scripts/sentinel2_caburga.py --year 2019      # 1 año
  python scripts/sentinel2_caburga.py --since 2017-01  # desde 2017

Salidas:
  data/raw/sentinel2/scenes.csv        catálogo de escenas
  data/processed/lago_superficie_s2.csv  serie temporal
  notebooks/figs/sentinel/<fecha>.png  frames

Dependencias: pystac-client, rasterio, rioxarray, numpy, matplotlib, pandas
"""
from __future__ import annotations
import argparse
import sys
from datetime import date, timedelta
from pathlib import Path
import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]

# Bounding box centrado en el Lago Caburga (cubre todo el lago)
# (lon_min, lat_min, lon_max, lat_max)
BBOX = (-71.86, -39.265, -71.74, -39.13)
COLLECTION = "sentinel-2-l2a"
STAC_URL = "https://earth-search.aws.element84.com/v1"


def buscar_escenas(since: str, until: str, max_cloud: float = 15.0) -> list:
    from pystac_client import Client
    cat = Client.open(STAC_URL)
    search = cat.search(
        collections=[COLLECTION],
        bbox=BBOX,
        datetime=f"{since}/{until}",
        query={"eo:cloud_cover": {"lt": max_cloud}},
        max_items=400,
    )
    items = list(search.items())
    items.sort(key=lambda i: i.datetime)
    return items


def descargar_bandas(item, out_dir: Path) -> tuple[Path, Path] | None:
    """Descarga B03 (verde) y B08 (NIR) recortadas al BBOX."""
    import rioxarray as rxr
    import rasterio.warp

    out_dir.mkdir(parents=True, exist_ok=True)
    fecha = item.datetime.date().isoformat()
    p_g = out_dir / f"{fecha}_B03.tif"
    p_n = out_dir / f"{fecha}_B08.tif"
    if p_g.exists() and p_n.exists():
        return p_g, p_n
    try:
        for asset_key, out_path in [("green", p_g), ("nir", p_n)]:
            href = item.assets[asset_key].href
            xarr = rxr.open_rasterio(href, masked=True).squeeze()
            # reproject BBOX to image CRS for clipping
            target_crs = xarr.rio.crs
            xmin, ymin, xmax, ymax = rasterio.warp.transform_bounds(
                "EPSG:4326", target_crs, *BBOX)
            clip = xarr.rio.clip_box(minx=xmin, miny=ymin, maxx=xmax, maxy=ymax)
            clip.rio.to_raster(out_path, compress="LZW")
        return p_g, p_n
    except Exception as e:
        print(f"  ! error {fecha}: {e}", file=sys.stderr)
        return None


def calcular_ndwi(p_green: Path, p_nir: Path):
    import rioxarray as rxr
    g = rxr.open_rasterio(p_green, masked=True).squeeze().astype("float32")
    n = rxr.open_rasterio(p_nir, masked=True).squeeze().astype("float32")
    ndwi = (g - n) / (g + n + 1e-6)
    return ndwi


def superficie_lago(ndwi, threshold: float = 0.0, pix_area_m2: float = 100.0) -> float:
    """Cuenta píxeles con NDWI > threshold y multiplica por área de píxel.
    Sentinel-2 L2A en bandas 10 m: 100 m² por píxel."""
    arr = ndwi.values
    valid = ~np.isnan(arr)
    water = (arr > threshold) & valid
    return float(water.sum() * pix_area_m2 / 1e6)  # km²


def render_frame(ndwi, fecha: str, out: Path) -> None:
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 7))
    arr = ndwi.values
    ax.imshow(arr, cmap="RdBu", vmin=-0.5, vmax=0.5)
    ax.contour(arr, levels=[0.0], colors="black", linewidths=1.0)
    ax.set_title(f"NDWI Lago Caburga — {fecha}")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(out, dpi=110, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2017-01-01")
    ap.add_argument("--until", default=date.today().isoformat())
    ap.add_argument("--year", type=int, help="atajo: --year 2019 ⇒ 2019-01..2019-12")
    ap.add_argument("--max-cloud", type=float, default=15.0)
    ap.add_argument("--limit", type=int, default=12,
                    help="número máximo de escenas a procesar")
    args = ap.parse_args()

    if args.year:
        args.since = f"{args.year}-01-01"
        args.until = f"{args.year}-12-31"

    raw_dir = ROOT / "data" / "raw" / "sentinel2"
    processed = ROOT / "data" / "processed"
    frames_dir = ROOT / "notebooks" / "figs" / "sentinel"
    raw_dir.mkdir(parents=True, exist_ok=True)
    frames_dir.mkdir(parents=True, exist_ok=True)

    print(f"Buscando escenas {args.since}..{args.until} cloud<{args.max_cloud}%…")
    items = buscar_escenas(args.since, args.until, args.max_cloud)
    print(f"  encontradas: {len(items)} escenas")

    # Submuestreo: 1 por mes aprox
    keep = []
    last_month = None
    for it in items:
        m = it.datetime.strftime("%Y-%m")
        if m != last_month:
            keep.append(it)
            last_month = m
        if len(keep) >= args.limit:
            break
    print(f"  procesando: {len(keep)} (1 por mes, max {args.limit})")

    rows = []
    for it in keep:
        fecha = it.datetime.date().isoformat()
        cc = it.properties.get("eo:cloud_cover", -1)
        print(f"  → {fecha} (cloud={cc:.1f}%)")
        bandas = descargar_bandas(it, raw_dir)
        if not bandas:
            continue
        ndwi = calcular_ndwi(*bandas)
        area = superficie_lago(ndwi)
        render_frame(ndwi, fecha, frames_dir / f"{fecha}.png")
        rows.append({"fecha": fecha, "cloud_cover_pct": cc,
                     "superficie_lago_km2": area})

    if rows:
        df = pd.DataFrame(rows).set_index("fecha")
        out = processed / "lago_superficie_s2.csv"
        if out.exists():
            prev = pd.read_csv(out, index_col="fecha")
            df = pd.concat([prev, df]).reset_index().drop_duplicates("fecha").set_index("fecha")
        df.sort_index().to_csv(out)
        print(f"\n→ {out} ({len(df)} filas totales)")
        print(df.tail())


if __name__ == "__main__":
    main()

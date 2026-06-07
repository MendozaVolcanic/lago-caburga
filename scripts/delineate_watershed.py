"""Delinea la cuenca real del Lago Caburga desde el DEM Copernicus GLO-30
usando pysheds, y exporta el polígono a GeoJSON para el mapa 3D.

Entrada: data/raw/dem/cop30_S39_W072.tif + cop30_S40_W072.tif (mosaico)
Salida:  docs/data/cuenca_caburga.geojson
         docs/data/red_drenaje.geojson (opcional, ríos principales)
"""
from __future__ import annotations
import sys, json
from pathlib import Path
import numpy as np

# Compat NumPy 2.0: pysheds usa np.in1d (removido). Alias a np.isin.
if not hasattr(np, "in1d"):
    np.in1d = np.isin

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
DEM_DIR = ROOT / "data" / "raw" / "dem"
OUT = ROOT / "docs" / "data"
OUT.mkdir(parents=True, exist_ok=True)

# Punto de salida (pour point): el Río Caburga (emisario superficial) sale
# por el sur. Buscamos la celda de máxima acumulación en esa zona.
POUR = (-71.80, -39.25)  # lon, lat — zona de salida sur del lago


def mosaico() -> Path:
    """Une las dos tiles en un solo GeoTIFF."""
    import rasterio
    from rasterio.merge import merge
    out = DEM_DIR / "cop30_caburga_mosaic.tif"
    if out.exists():
        return out
    srcs = [rasterio.open(DEM_DIR / f) for f in
            ["cop30_S39_W072.tif", "cop30_S40_W072.tif"]]
    arr, transform = merge(srcs)
    meta = srcs[0].meta.copy()
    meta.update({"height": arr.shape[1], "width": arr.shape[2], "transform": transform})
    with rasterio.open(out, "w", **meta) as dst:
        dst.write(arr)
    for s in srcs:
        s.close()
    print(f"  mosaico → {out}")
    return out


def delinear(dem_path: Path):
    from pysheds.grid import Grid
    grid = Grid.from_raster(str(dem_path))
    dem = grid.read_raster(str(dem_path))
    print("  acondicionando DEM (fill/resolve)…")
    pit_filled = grid.fill_pits(dem)
    flooded = grid.fill_depressions(pit_filled)
    inflated = grid.resolve_flats(flooded)
    print("  dirección y acumulación de flujo…")
    fdir = grid.flowdir(inflated)
    acc = grid.accumulation(fdir)

    # Snap pour point a la celda de MÁXIMA acumulación dentro de una ventana
    # alrededor de la salida del lago (evita engancharse a afluentes menores).
    x, y = POUR
    accview = grid.view(acc)
    # Ventana de búsqueda ±0.05° alrededor del pour point
    import numpy as _np
    rows, cols = accview.shape
    aff = grid.affine
    # convertir lon/lat a índices
    col0 = int((x - 0.05 - aff.c) / aff.a); col1 = int((x + 0.05 - aff.c) / aff.a)
    row0 = int((y + 0.05 - aff.f) / aff.e); row1 = int((y - 0.05 - aff.f) / aff.e)
    col0, col1 = sorted((max(0, col0), min(cols, col1)))
    row0, row1 = sorted((max(0, row0), min(rows, row1)))
    win = accview[row0:row1, col0:col1]
    ri, ci = _np.unravel_index(_np.argmax(win), win.shape)
    gr, gc = row0 + ri, col0 + ci
    x_snap = aff.c + (gc + 0.5) * aff.a
    y_snap = aff.f + (gr + 0.5) * aff.e
    print(f"  pour point snap: ({x_snap:.4f},{y_snap:.4f}), "
          f"acc local={win.max():.0f}, acc global max={acc.max():.0f}")

    catch = grid.catchment(x=x_snap, y=y_snap, fdir=fdir, xytype="coordinate")
    grid.clip_to(catch)
    catch_view = grid.view(catch, dtype=np.uint8)

    # Polígono de la cuenca
    shapes = grid.polygonize(catch_view)
    polys = [geom for geom, val in shapes if val == 1]
    print(f"  polígonos cuenca: {len(polys)}")

    # Red de drenaje (acumulación alta)
    branches = grid.extract_river_network(fdir, acc > 2000)

    return polys, branches, float(acc.max())


def main():
    dem_path = mosaico()
    polys, branches, accmax = delinear(dem_path)

    # Exportar cuenca
    feats = [{"type": "Feature",
              "properties": {"nombre": "Cuenca aportante Lago Caburga (pysheds/COP30)"},
              "geometry": geom} for geom in polys]
    gj = {"type": "FeatureCollection", "features": feats}
    (OUT / "cuenca_caburga.geojson").write_text(
        json.dumps(gj), encoding="utf-8")
    print(f"→ {OUT / 'cuenca_caburga.geojson'}")

    # Área aproximada
    try:
        from shapely.geometry import shape
        import pyproj
        from shapely.ops import transform as shp_transform
        total = 0
        proj = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:32719", always_xy=True).transform
        for geom in polys:
            total += shp_transform(proj, shape(geom)).area
        print(f"  área cuenca: {total/1e6:.0f} km² (referencia U. Austral: 335 km²)")
    except Exception as e:
        print(f"  (área no calculada: {e})")

    # Exportar red de drenaje
    (OUT / "red_drenaje.geojson").write_text(json.dumps(branches), encoding="utf-8")
    print(f"→ {OUT / 'red_drenaje.geojson'}")


if __name__ == "__main__":
    main()

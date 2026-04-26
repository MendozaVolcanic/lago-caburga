"""Extrae series CAMELS-CL para las cuencas de la zona Caburga (cuenca Toltén).

CAMELS-CL es el dataset estandarizado más completo de hidrología chilena.
Cubre 516 cuencas con caudal diario y precipitación CR2MET 1979-2018.

Cuencas relevantes (gauge_id = código BNA estación de salida):
  9404001  Río Allipén en Los Laureles
  9405001  Río Curaco en Colico
  9412001  Río Trancura en Curarrehue
  9414001  Río Trancura antes Río Llafenco
  9416001  Río Liucura en Liucura
  9418001  Río Pucón en Balseadero Quelhue
  9420001  Río Toltén en Villarrica

Salida: data/processed/camels_cuenca_tolten.csv (caudal y precipitación)
y data/processed/camels_attributes.csv (atributos físicos cuencas)
"""
from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "raw" / "camels"
OUT = ROOT / "data" / "processed"

CUENCAS = ["9404001", "9405001", "9412001", "9414001", "9416001",
           "9418001", "9420001"]


def cargar_serie(archivo: str) -> pd.DataFrame:
    """Lee un .txt CAMELS-CL en formato wide (col 0 = fecha, resto = gauge_ids)."""
    df = pd.read_csv(SRC / archivo, sep="\t", na_values=["", " ", "NA", "-9999"],
                     low_memory=False, index_col=0)
    df.index.name = "fecha"
    df.index = pd.to_datetime(df.index, errors="coerce")
    df = df[~df.index.isna()].sort_index()
    # Las columnas son gauge_ids como strings tipo "1001001"
    cols_keep = [c for c in df.columns if str(c).strip().lstrip("0")
                 in [x.lstrip("0") for x in CUENCAS]]
    return df[cols_keep].apply(pd.to_numeric, errors="coerce")


def cargar_atributos() -> pd.DataFrame:
    df = pd.read_csv(SRC / "1_CAMELScl_attributes.txt", sep="\t",
                     na_values=["", " ", "NA", "-9999"], index_col=0,
                     low_memory=False)
    # filas son atributos (gauge_name, gauge_lat, ...), columnas son cuencas
    df.columns = [c.strip() for c in df.columns]
    df = df.T
    df = df.loc[df.index.isin(CUENCAS)]
    return df


def main() -> None:
    print("Atributos…")
    attrs = cargar_atributos()
    if not attrs.empty:
        cols_int = ["gauge_name", "gauge_lat", "gauge_lon",
                    "area_km2", "elev_mean", "p_mean_cr2met",
                    "q_mean_cr2met", "runoff_ratio_cr2met",
                    "interv_degree", "big_dam", "lc_glacier",
                    "lc_forest", "lc_grass", "fr_lakes"]
        keep = [c for c in cols_int if c in attrs.columns]
        attrs[keep].to_csv(OUT / "camels_attributes.csv")
        print(f"  → {OUT / 'camels_attributes.csv'} ({len(attrs)} cuencas)")
        print(attrs[keep[:6]] if keep else attrs.head())

    print("\nCaudales…")
    q = cargar_serie("2_CAMELScl_streamflow_m3s.txt")
    if not q.empty:
        q.to_csv(OUT / "camels_caudal_diario.csv")
        annual = q.resample("YE").mean()
        counts = q.resample("YE").count()
        annual = annual.where(counts >= 330)
        annual.index = annual.index.year
        annual.round(2).to_csv(OUT / "camels_caudal_anual.csv")
        print(f"  diaria: {q.shape}, rango {q.index.min().date()}..{q.index.max().date()}")
        print(annual.tail(5).round(1))

    print("\nPrecipitación CR2MET (cuenca-promedio)…")
    p = cargar_serie("4_CAMELScl_precip_cr2met.txt")
    if not p.empty:
        annual = p.resample("YE").sum(min_count=330)
        annual.index = annual.index.year
        annual.round(1).to_csv(OUT / "camels_precip_cuenca_anual.csv")
        print(f"  diaria: {p.shape}, rango {p.index.min().date()}..{p.index.max().date()}")
        print(annual.tail(5).round(0))


if __name__ == "__main__":
    main()

"""Extrae caudales diarios de las estaciones de la cuenca Toltén/Pucón desde CR2."""
from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "raw" / "cr2" / "cr2_qflxDaily_2020" / "cr2_qflxDaily_2020.txt"
OUT_DAILY = ROOT / "data" / "processed" / "caudales_diarios_cuenca.csv"
OUT_ANNUAL = ROOT / "data" / "processed" / "caudales_anuales_cr2.csv"

ESTACIONES = {
    "09416001": "Río Liucura en Liucura",
    "09420001": "Río Toltén en Villarrica",
    "09414001": "Río Trancura antes Llafenco",
    "09412001": "Río Trancura en Curarrehue",
    "09405001": "Río Curaco en Colico",
}


def main() -> None:
    header = pd.read_csv(SRC, nrows=0).columns.tolist()
    use_cols = ["codigo_estacion"] + [c for c in ESTACIONES if c in header]
    missing = [c for c in ESTACIONES if c not in header]
    if missing:
        print(f"[!] no encontradas: {missing}")
    df = pd.read_csv(SRC, usecols=use_cols, skiprows=range(1, 15),
                     na_values=["-9999", "-9999.0"])
    df = df.rename(columns={"codigo_estacion": "fecha"})
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df = df.dropna(subset=["fecha"]).set_index("fecha").sort_index()
    df = df.rename(columns={c: f"{c} {n}" for c, n in ESTACIONES.items() if c in df.columns})
    df.to_csv(OUT_DAILY)
    print(f"diaria → {OUT_DAILY} ({len(df):,} días, {df.shape[1]} estaciones)")

    annual = df.resample("YE").mean()
    counts = df.resample("YE").count()
    annual = annual.where(counts >= 330)
    annual.index = annual.index.year
    annual.index.name = "año"
    annual.round(2).to_csv(OUT_ANNUAL)
    print(f"anual  → {OUT_ANNUAL} ({len(annual)} años)")
    print(annual.tail(10).round(1))


if __name__ == "__main__":
    main()

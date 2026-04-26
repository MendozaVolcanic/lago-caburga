"""Extrae series diarias de precipitación de las estaciones de interés desde el
archivo CR2 nacional. Salida: data/processed/precipitacion_diaria_cuenca.csv
con columnas (fecha, código → nombre).
"""
from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "raw" / "cr2" / "cr2_prDaily_2020" / "cr2_prDaily_2020.txt"
OUT_DAILY = ROOT / "data" / "processed" / "precipitacion_diaria_cuenca.csv"
OUT_ANNUAL = ROOT / "data" / "processed" / "precipitacion_anual_cr2.csv"

# Códigos DGA (8 dígitos con cero a la izquierda) → nombre legible
ESTACIONES = {
    "09401001": "Tricauco",
    "09416002": "Lago Tinquilco",
    "09417001": "Lago Caburgua",
    "09417002": "Ojos del Caburgua",
    "09420002": "Pucón",
    "09414002": "Llafenco",
    "09412002": "Curarrehue",
    "09412003": "Puesco",
}


def main() -> None:
    # Filas 0-14 son metadatos. Fila 15 en adelante: fecha, valores...
    # Para no cargar 233 MB de RAM, leemos solo columnas necesarias.
    header = pd.read_csv(SRC, nrows=0).columns.tolist()
    use_cols = ["codigo_estacion"] + [c for c in ESTACIONES if c in header]
    missing = [c for c in ESTACIONES if c not in header]
    if missing:
        print(f"[!] no encontradas en CR2: {missing}")

    df = pd.read_csv(SRC, usecols=use_cols, skiprows=range(1, 15),
                     na_values=["-9999", "-9999.0"])
    df = df.rename(columns={"codigo_estacion": "fecha"})
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df = df.dropna(subset=["fecha"]).set_index("fecha")
    df = df.rename(columns={c: f"{c} {n}" for c, n in ESTACIONES.items() if c in df.columns})
    df = df.sort_index()

    df.to_csv(OUT_DAILY)
    print(f"diaria → {OUT_DAILY} ({len(df):,} días, {df.shape[1]} estaciones)")
    print(f"  rango: {df.index.min().date()} a {df.index.max().date()}")

    annual = df.resample("YE").agg(["sum", "count"])
    rows = []
    for col in df.columns:
        s = annual[col]["sum"]
        n = annual[col]["count"]
        s = s.where(n >= 330)  # exigir al menos 330 días con dato por año
        for fecha, valor in s.items():
            if pd.notna(valor):
                rows.append({"año": fecha.year, "estacion": col, "precip_mm": round(valor, 1)})
    annual_long = pd.DataFrame(rows)
    annual_wide = annual_long.pivot(index="año", columns="estacion", values="precip_mm")
    annual_wide.to_csv(OUT_ANNUAL)
    print(f"anual  → {OUT_ANNUAL} ({len(annual_wide)} años)")
    print(annual_wide.tail(10))


if __name__ == "__main__":
    main()

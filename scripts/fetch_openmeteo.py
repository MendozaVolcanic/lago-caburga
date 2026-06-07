"""Descarga precipitación, temperatura y nieve de Open-Meteo (ERA5) para las
estaciones clave de la zona Caburga. 1950-presente, CC BY 4.0, sin API key.

Ventaja sobre CR2: cobertura hasta HOY (CR2 termina en 2020). Permite ver la
recuperación El Niño 2023-24 y el nuevo descenso 2025-26.

Salidas:
  data/processed/openmeteo_precip_anual.csv     precipitación anual por punto
  data/processed/openmeteo_diario.csv           serie diaria multi-variable Caburga
"""
from __future__ import annotations
import sys
import time
import urllib.request
import json
from pathlib import Path
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

# Puntos de interés (lat, lon)
PUNTOS = {
    "Lago Caburga": (-39.20, -71.81),
    "Lago Colico": (-39.10, -71.95),
    "Lago Villarrica": (-39.27, -72.07),
    "Pucon": (-39.28, -71.95),
    "Cuenca alta Trafampulli": (-39.04, -71.65),
}

START = "1950-01-01"
END = "2025-12-31"
API = "https://archive-api.open-meteo.com/v1/archive"


def fetch(lat: float, lon: float, daily: list[str]) -> dict:
    url = (f"{API}?latitude={lat}&longitude={lon}"
           f"&start_date={START}&end_date={END}"
           f"&daily={','.join(daily)}&timezone=America%2FSantiago")
    with urllib.request.urlopen(url, timeout=120) as r:
        return json.load(r)


def main() -> None:
    precip_anual = {}
    diario_caburga = None

    for nombre, (lat, lon) in PUNTOS.items():
        print(f"  {nombre} ({lat},{lon})…")
        try:
            d = fetch(lat, lon, ["precipitation_sum", "temperature_2m_mean",
                                 "snowfall_sum"])
        except Exception as e:
            print(f"    ERROR: {e}")
            continue
        df = pd.DataFrame({
            "fecha": pd.to_datetime(d["daily"]["time"]),
            "precip": d["daily"]["precipitation_sum"],
            "temp": d["daily"]["temperature_2m_mean"],
            "nieve": d["daily"]["snowfall_sum"],
        }).set_index("fecha")

        # Precip anual
        anual = df["precip"].resample("YE").sum(min_count=330)
        anual.index = anual.index.year
        precip_anual[nombre] = anual.round(0)

        if nombre == "Lago Caburga":
            diario_caburga = df

        print(f"    {df.index.min().date()}..{df.index.max().date()}, "
              f"PMA={anual.mean():.0f} mm")
        time.sleep(1.0)  # cortesía con la API

    if precip_anual:
        pa = pd.DataFrame(precip_anual)
        pa.index.name = "año"
        pa.to_csv(OUT / "openmeteo_precip_anual.csv")
        print(f"\n→ {OUT / 'openmeteo_precip_anual.csv'} ({pa.shape})")
        print("\nPrecipitación anual reciente (mm):")
        print(pa.tail(8).round(0))

        # Resumen de cambio por década
        print("\n=== Cambio pre/post 2010 ===")
        for col in pa.columns:
            s = pa[col].dropna()
            pre = s.loc[:2009].mean()
            post = s.loc[2010:].mean()
            if pre:
                print(f"  {col:28s} pre={pre:.0f}  post={post:.0f}  Δ={(post-pre)/pre*100:+.1f}%")

    if diario_caburga is not None:
        diario_caburga.round(2).to_csv(OUT / "openmeteo_diario.csv")
        print(f"\n→ {OUT / 'openmeteo_diario.csv'} ({diario_caburga.shape})")


if __name__ == "__main__":
    main()

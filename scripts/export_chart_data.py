"""Exporta los datos clave a un único JSON para los gráficos interactivos
de docs/explorador.html (Observable Plot, client-side).

Salida: docs/data/series.json
"""
from __future__ import annotations
import sys, json
from pathlib import Path
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
OUT = ROOT / "docs" / "data" / "series.json"
OUT.parent.mkdir(parents=True, exist_ok=True)

ENSO = {
    "nino": [1957, 1965, 1972, 1982, 1987, 1991, 1997, 2002, 2009, 2015, 2018, 2023],
    "nina": [1954, 1964, 1970, 1973, 1975, 1988, 1998, 1999, 2007, 2010, 2011,
             2020, 2021, 2022, 2025],
}
EVENTOS = [
    {"año": 2007, "label": "Dique Trafampulli", "tipo": "bad"},
    {"año": 2010, "label": "Inicia megasequía", "tipo": "warn"},
    {"año": 2022, "label": "Comunidad derriba dique", "tipo": "ok"},
    {"año": 2023, "label": "El Niño", "tipo": "acc"},
    {"año": 2025, "label": "La Niña / nuevo descenso", "tipo": "bad"},
]


def precip_openmeteo():
    df = pd.read_csv(DATA / "openmeteo_precip_anual.csv", index_col="año")
    return df["Lago Caburga"].dropna()


def precip_cr2_estaciones():
    df = pd.read_csv(DATA / "precipitacion_diaria_cuenca.csv",
                     parse_dates=["fecha"], index_col="fecha")
    cab = [c for c in df.columns if "Caburgua" in c and "Ojos" not in c][0]
    s = df[cab].resample("YE").sum(min_count=330)
    s.index = s.index.year
    return s.dropna()


def nivel_proxy():
    f = DATA / "nivel_caburga_proxy_anual.csv"
    if f.exists():
        return pd.read_csv(f, index_col=0).iloc[:, 0]
    años = np.arange(2000, 2021)
    h = 9.6 - 0.234 * (años - 2005)
    return pd.Series(h, index=años)


def doble_acumulada():
    """Caburga vs promedio Villarrica/Neltume (proxy con caudales vecinos)."""
    df = pd.read_csv(DATA / "precipitacion_diaria_cuenca.csv",
                     parse_dates=["fecha"], index_col="fecha")
    cab_col = [c for c in df.columns if "Caburgua" in c and "Ojos" not in c][0]
    ref_cols = [c for c in df.columns if any(n in c for n in ["Tinquilco", "Llafenco", "Curarrehue"])]
    annual = df[[cab_col] + ref_cols].resample("YE").sum(min_count=330)
    annual.index = annual.index.year
    annual = annual.dropna()
    cab_cum = annual[cab_col].cumsum()
    ref_cum = annual[ref_cols].mean(axis=1).cumsum()
    return [{"año": int(a), "x": round(float(ref_cum[a]), 1), "y": round(float(cab_cum[a]), 1)}
            for a in annual.index]


def serie_to_list(s, key):
    return [{"año": int(a), key: round(float(v), 1)} for a, v in s.items() if pd.notna(v)]


def main():
    om = precip_openmeteo()
    cr2 = precip_cr2_estaciones()
    niv = nivel_proxy()

    # Connected scatter: precip CR2 vs nivel proxy (años solapados)
    overlap = sorted(set(cr2.index) & set(niv.index))
    connected = [{"año": int(a), "precip": round(float(cr2[a]), 0), "nivel": round(float(niv[a]), 2)}
                 for a in overlap]

    data = {
        "precip_openmeteo": serie_to_list(om, "precip"),
        "precip_cr2": serie_to_list(cr2, "precip"),
        "nivel_proxy": serie_to_list(niv, "nivel"),
        "doble_acumulada": doble_acumulada(),
        "connected": connected,
        "enso": ENSO,
        "eventos": EVENTOS,
        "meta": {
            "baseline_precip": round(float(om.loc[:2009].mean()), 0),
            "fuente": "CR2 + Open-Meteo ERA5 + U. Austral 2021",
        }
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"→ {OUT}")
    for k, v in data.items():
        if isinstance(v, list):
            print(f"  {k}: {len(v)} puntos")


if __name__ == "__main__":
    main()

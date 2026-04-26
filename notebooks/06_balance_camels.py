"""Notebook 6 — Recalibración del balance hídrico con CAMELS-CL.

CAMELS-CL ofrece precipitación promedio de cuenca (CR2MET grillado, no estación
puntual) que es más representativa para el balance del lago. Recalibra el
modelo del notebook 03 usando esta serie y compara la atribución.

Cuenca de referencia: 9416001 Río Liucura en Liucura — la más cercana
geográficamente a la cuenca aportante del Caburga (no hay estación CAMELS
para Caburga directamente).
"""
from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
OUT = ROOT / "notebooks" / "figs"
OUT.mkdir(exist_ok=True)

# Parámetros (idénticos al notebook 03)
A_LAGO = 53e6
A_CUENCA = 282e6
H0 = 489.7
H_BASE = 482.0
EVAP_MM = 600.0
ALPHA_DRENAJE = 70.0
SEG_POR_AÑO = 365.25 * 86400


def cargar_precip_camels() -> pd.Series:
    """Precip cuenca-promedio CAMELS-CL — Río Liucura como proxy del Caburga."""
    df = pd.read_csv(DATA / "camels_precip_cuenca_anual.csv", index_col=0)
    # Promedio de las 3 cuencas más cercanas: Liucura, Trancura-Curarrehue, Trancura-Llafenco
    cols = [c for c in df.columns if c in ("9416001", "9412001", "9414001")]
    return df[cols].mean(axis=1).dropna()


def cargar_precip_cr2() -> pd.Series:
    """Precip estación-promedio (notebook 03)."""
    df = pd.read_csv(DATA / "precipitacion_diaria_cuenca.csv",
                     parse_dates=["fecha"], index_col="fecha")
    cols = [c for c in df.columns
            if any(n in c for n in ["Caburgua", "Tinquilco", "Tricauco", "Llafenco"])
            and "Ojos" not in c]
    s = df[cols].resample("YE").sum(min_count=330).mean(axis=1)
    s.index = s.index.year
    return s.dropna()


def simular(P: pd.Series, q_traf: float, fac_p: float = 1.0) -> pd.DataFrame:
    P_use = P * fac_p / 1000.0
    QDTf = q_traf * SEG_POR_AÑO
    E = EVAP_MM / 1000.0 * A_LAGO
    Qoe = 0.05 * SEG_POR_AÑO  # extracción default
    H = H0
    rows = []
    for año, p in P_use.items():
        Qo = ALPHA_DRENAJE * 1e6 * max(H - H_BASE, 0)
        ingreso = p * A_LAGO + p * A_CUENCA * 0.65 + QDTf
        egreso = Qo + E + Qoe
        H = H + (ingreso - egreso) / A_LAGO
        rows.append({"año": año, "H_m": H})
    return pd.DataFrame(rows).set_index("año")


def fig_comparacion(camels: pd.Series, cr2: pd.Series) -> Path:
    fig, axes = plt.subplots(2, 1, figsize=(11, 8), sharex=False)

    ax = axes[0]
    ax.plot(cr2.index, cr2.values, "o-", color="#48a", lw=1.5, label="CR2 estaciones")
    ax.plot(camels.index, camels.values, "s-", color="#c44", lw=1.5,
            label="CAMELS-CL cuenca (CR2MET grillado)")
    ax.axvline(2010, color="orange", ls="--", alpha=0.5)
    ax.set(xlabel="Año", ylabel="Precipitación cuenca (mm/año)",
           title="Comparación de productos de precipitación")
    ax.legend()
    ax.grid(alpha=0.3)

    # Comparación balance
    ax = axes[1]
    base_cr2 = simular(cr2, 0.0, 1.0)
    base_camels = simular(camels, 0.0, 1.0)
    sin_seq_cr2 = simular(cr2, 0.0, 1.20)
    sin_seq_camels = simular(camels, 0.0, 1.20)

    ax.plot(base_cr2.index, base_cr2["H_m"], "o-", color="#48a", lw=1.5,
            label="CR2 base")
    ax.plot(base_camels.index, base_camels["H_m"], "s-", color="#c44", lw=1.5,
            label="CAMELS-CL base")
    ax.plot(sin_seq_cr2.index, sin_seq_cr2["H_m"], "o:", color="#48a", lw=1,
            alpha=0.7, label="CR2 sin megasequía")
    ax.plot(sin_seq_camels.index, sin_seq_camels["H_m"], "s:", color="#c44", lw=1,
            alpha=0.7, label="CAMELS-CL sin megasequía")
    ax.axvline(2010, color="orange", ls="--", alpha=0.5)
    ax.set(xlabel="Año", ylabel="Cota lago (m s.n.m.)",
           title="Cota simulada con dos productos de precipitación")
    ax.legend(loc="lower left")
    ax.grid(alpha=0.3)

    out = OUT / "06_balance_camels.png"
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return out


def reporte(camels: pd.Series, cr2: pd.Series) -> None:
    print(f"\nCR2:    {cr2.index.min()}-{cr2.index.max()}, n={len(cr2)}, "
          f"media={cr2.mean():.0f} mm/año")
    print(f"CAMELS: {camels.index.min()}-{camels.index.max()}, n={len(camels)}, "
          f"media={camels.mean():.0f} mm/año")

    overlap = cr2.index.intersection(camels.index)
    if len(overlap) > 5:
        corr = cr2.loc[overlap].corr(camels.loc[overlap])
        print(f"Correlación en años solapados ({len(overlap)} años): r={corr:.3f}")

    pre = camels.loc[:2009].mean() if (camels.index <= 2009).any() else np.nan
    post = camels.loc[2010:].mean() if (camels.index >= 2010).any() else np.nan
    if pd.notna(pre) and pre:
        print(f"\nCAMELS pre-2010: {pre:.0f} mm/año")
        print(f"CAMELS 2010+:    {post:.0f} mm/año  ({(post-pre)/pre*100:+.1f}%)")


if __name__ == "__main__":
    camels = cargar_precip_camels()
    cr2 = cargar_precip_cr2()
    reporte(camels, cr2)
    print(fig_comparacion(camels, cr2))

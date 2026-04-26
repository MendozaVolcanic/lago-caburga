"""Notebook 2 — Análisis de doble acumulada y detección de quiebre.

La técnica de doble acumulada compara dos series temporales acumuladas. Si la
relación es lineal, ambas series están gobernadas por el mismo proceso. Un
cambio de pendiente sugiere que algo distinto al proceso compartido (el clima
regional) afectó a una de las dos series.

Aplicamos esto sobre las series diarias CR2 de las estaciones de precipitación
de la cuenca Caburgua, comparando con estaciones regionales de control.
"""
from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
OUT = ROOT / "notebooks" / "figs"
OUT.mkdir(exist_ok=True)


def load_precip_diaria() -> pd.DataFrame:
    df = pd.read_csv(DATA / "precipitacion_diaria_cuenca.csv",
                     parse_dates=["fecha"], index_col="fecha")
    return df


def fig_series_anual_completa(df: pd.DataFrame) -> Path:
    annual = df.resample("YE").sum(min_count=330)
    annual.index = annual.index.year
    fig, ax = plt.subplots(figsize=(11, 5.5))
    for col in annual.columns:
        s = annual[col].dropna()
        if len(s) < 5:
            continue
        ax.plot(s.index, s.values, "o-", lw=1, ms=3, alpha=0.7,
                label=col.split(" ", 1)[1] if " " in col else col)
    # Promedio cuenca (Tinquilco + Caburgua + Tricauco + Llafenco)
    cuenca_cols = [c for c in annual.columns
                   if any(n in c for n in ["Caburgua", "Tinquilco", "Tricauco", "Llafenco"])
                   and "Ojos" not in c]
    cuenca = annual[cuenca_cols].mean(axis=1)
    ax.plot(cuenca.index, cuenca.values, "k-", lw=2.4, label="Promedio cuenca")
    z = np.polyfit(cuenca.dropna().index, cuenca.dropna().values, 1)
    ax.plot(cuenca.index, np.poly1d(z)(cuenca.index), "r--", lw=1.5,
            label=f"Tendencia: {z[0]:.0f} mm/año")
    ax.axvspan(2010, 2020, alpha=0.1, color="orange", label="Megasequía 2010+")
    ax.axvline(2007, color="purple", ls=":", alpha=0.6, label="Cierre Trafampulli")
    ax.set(xlabel="Año", ylabel="Precipitación anual (mm)",
           title="Precipitación anual — estaciones cuenca Caburga (CR2 1965-2019)")
    ax.legend(loc="upper right", fontsize=8, ncol=2)
    ax.grid(alpha=0.3)
    out = OUT / "02_precip_anual_completa.png"
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return out


def fig_doble_acumulada(df: pd.DataFrame) -> Path:
    """Caburgua vs Tinquilco/Tricauco/Llafenco/Curarrehue — anual."""
    annual = df.resample("YE").sum(min_count=330)
    annual.index = annual.index.year
    cab = [c for c in annual.columns if "Caburgua" in c and "Ojos" not in c][0]
    refs = [c for c in annual.columns if c != cab and "Ojos" not in c]

    annual_clean = annual[[cab] + refs].dropna(how="any").copy()
    cum = annual_clean.cumsum()

    fig, axes = plt.subplots(2, 3, figsize=(13, 8))
    axes = axes.flat

    for ax, ref in zip(axes, refs):
        ax.plot(cum[ref], cum[cab], "o-", ms=4, lw=1, color="#356")
        for yr in [2007, 2010, 2016]:
            if yr in cum.index:
                ax.scatter(cum.loc[yr, ref], cum.loc[yr, cab], s=80, color="r",
                           zorder=5)
                ax.annotate(str(yr), (cum.loc[yr, ref], cum.loc[yr, cab]),
                            xytext=(6, -2), textcoords="offset points", fontsize=8)
        ax.set(xlabel=f"Σ {ref.split(' ', 1)[1] if ' ' in ref else ref} (mm)",
               ylabel=f"Σ {cab.split(' ', 1)[1]} (mm)",
               title=f"Caburgua vs {ref.split(' ', 1)[1] if ' ' in ref else ref}")
        ax.grid(alpha=0.3)
    for ax in axes[len(refs):]:
        ax.axis("off")
    fig.suptitle("Doble acumulada: precipitación Caburgua vs estaciones regionales\n"
                 "Si las series fueran homogéneas, los puntos formarían una línea recta",
                 fontsize=11)
    out = OUT / "02_doble_acumulada.png"
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return out


def fig_anomalias_precipitacion(df: pd.DataFrame) -> Path:
    """Anomalía respecto al promedio 1965-2009 — muestra megasequía visualmente."""
    annual = df.resample("YE").sum(min_count=330)
    annual.index = annual.index.year
    baseline = annual.loc[1965:2009].mean()
    anomalia = (annual - baseline) / baseline * 100

    cuenca_cols = [c for c in annual.columns
                   if any(n in c for n in ["Caburgua", "Tinquilco", "Tricauco", "Llafenco"])
                   and "Ojos" not in c]
    promedio = anomalia[cuenca_cols].mean(axis=1)

    fig, ax = plt.subplots(figsize=(11, 5))
    colors = ["#c44" if v < 0 else "#48a" for v in promedio.dropna().values]
    ax.bar(promedio.dropna().index, promedio.dropna().values, color=colors, alpha=0.85)
    ax.axhline(0, color="k", lw=0.8)
    ax.axvline(2010, color="orange", ls="--", alpha=0.7, label="Inicio megasequía")
    ax.set(xlabel="Año",
           ylabel="Anomalía precipitación (%) vs promedio 1965-2009",
           title="Megasequía en cuenca Caburga — desviación respecto a la normal")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    out = OUT / "02_anomalias_precipitacion.png"
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return out


def reporte_estadistico(df: pd.DataFrame) -> None:
    annual = df.resample("YE").sum(min_count=330)
    annual.index = annual.index.year
    print("\n=== Estadísticas por estación ===")
    for col in annual.columns:
        s = annual[col].dropna()
        if len(s) < 10:
            continue
        pre = s.loc[:2009].mean() if (s.index <= 2009).any() else np.nan
        post = s.loc[2010:].mean() if (s.index >= 2010).any() else np.nan
        delta = (post - pre) / pre * 100 if pd.notna(pre) and pre else np.nan
        print(f"  {col[:40]:40s}  pre2010={pre:7.1f}  post2010={post:7.1f}  Δ={delta:+5.1f}%  n={len(s)}")


if __name__ == "__main__":
    df = load_precip_diaria()
    print(fig_series_anual_completa(df))
    print(fig_doble_acumulada(df))
    print(fig_anomalias_precipitacion(df))
    reporte_estadistico(df)

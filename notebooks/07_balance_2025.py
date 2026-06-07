"""Notebook 7 — Balance hídrico extendido a 2025 con Open-Meteo (ERA5).

A diferencia del notebook 03 (que usaba CR2 hasta 2018/2020), este usa la serie
Open-Meteo 1950-2025, lo que permite simular:
  - la sequía sostenida 2010-2021
  - la recuperación El Niño 2022-2024
  - el nuevo descenso 2025 (La Niña)

Produce una figura con la cota simulada cubriendo el periodo completo y marca
los eventos clave (dique, megasequía, derribo, El Niño, La Niña).
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
ASSETS = ROOT / "docs" / "assets"
OUT.mkdir(exist_ok=True)
ASSETS.mkdir(exist_ok=True)

# Parámetros del modelo (idénticos a notebook 03)
A_LAGO = 53e6
A_CUENCA = 282e6
H0 = 489.7
H_BASE = 482.0
EVAP_MM = 600.0
ALPHA = 70.0
SEG = 365.25 * 86400

C_BG = "#0e1a24"; C_FG = "#e8eef5"; C_MUTED = "#7c8fa1"
C_ACC = "#4aa3df"; C_BAD = "#c0392b"; C_OK = "#27ae60"; C_WARN = "#e6a23c"
plt.rcParams.update({"figure.facecolor": C_BG, "axes.facecolor": C_BG,
    "savefig.facecolor": C_BG, "text.color": C_FG, "axes.labelcolor": C_MUTED,
    "xtick.color": C_MUTED, "ytick.color": C_MUTED, "axes.edgecolor": "#1f3245"})


def precip_openmeteo() -> pd.Series:
    df = pd.read_csv(DATA / "openmeteo_precip_anual.csv", index_col="año")
    return df["Lago Caburga"].dropna()


def simular(P: pd.Series, q_traf: float = 0.0, fac: float = 1.0) -> pd.Series:
    P_use = P * fac / 1000.0
    QDTf = q_traf * SEG
    E = EVAP_MM / 1000.0 * A_LAGO
    Qoe = 0.05 * SEG
    H = H0
    out = {}
    for año, p in P_use.items():
        Qo = ALPHA * 1e6 * max(H - H_BASE, 0)
        ingreso = p * A_LAGO + p * A_CUENCA * 0.65 + QDTf
        H += (ingreso - (Qo + E + Qoe)) / A_LAGO
        out[año] = H
    return pd.Series(out)


def fig_balance_2025(P: pd.Series) -> Path:
    # Arrancar la simulación en 1990 para tener estado estable hacia 2000
    P = P.loc[1990:]
    base = simular(P, 0.0, 1.0)
    sin_seq = simular(P, 0.0, 1.18)
    con_dique = simular(P, 1.0, 1.0)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(base.index, base.values, "o-", color=C_ACC, lw=2.2, ms=3,
            label="Observado (con sequía y dique)")
    ax.plot(sin_seq.index, sin_seq.values, "--", color=C_OK, lw=1.6, alpha=0.8,
            label="Contrafactual: sin megasequía")
    ax.plot(con_dique.index, con_dique.values, ":", color=C_WARN, lw=1.6, alpha=0.8,
            label="Contrafactual: con aporte Trafampulli +1 m³/s")

    eventos = [(2007, "Dique", C_BAD), (2010, "Megasequía", C_WARN),
               (2022, "Cae dique", C_OK), (2023, "El Niño", C_ACC),
               (2025, "La Niña", C_BAD)]
    for año, label, color in eventos:
        if base.index.min() <= año <= base.index.max():
            ax.axvline(año, color=color, ls=":", alpha=0.45, lw=1)
            ax.text(año, base.max() + 0.2, label, color=color, fontsize=8,
                    ha="center", rotation=90, va="bottom")

    ax.set_title("Balance hídrico Lago Caburga 1990-2025 (Open-Meteo ERA5)",
                 color=C_FG, fontsize=15)
    ax.set_xlabel("Año"); ax.set_ylabel("Cota simulada (m s.n.m.)")
    ax.legend(loc="lower left", framealpha=0.3, fontsize=9)
    ax.grid(alpha=0.15)
    fig.tight_layout()
    out = ASSETS / "balance_2025.png"
    fig.savefig(out, dpi=140)
    fig.savefig(OUT / "07_balance_2025.png", dpi=130)
    plt.close(fig)
    return out


def reporte(P: pd.Series) -> None:
    base = simular(P.loc[1990:], 0.0, 1.0)
    print("Cota simulada en años clave:")
    for año in [2000, 2010, 2018, 2021, 2024, 2025]:
        if año in base.index:
            print(f"  {año}: {base[año]:.2f} m")
    print(f"\nMín histórico simulado: {base.min():.2f} m en {base.idxmin()}")
    print(f"Recuperación 2021→2024: {base.get(2024, np.nan) - base.get(2021, np.nan):+.2f} m")
    print(f"Descenso 2024→2025:     {base.get(2025, np.nan) - base.get(2024, np.nan):+.2f} m")


if __name__ == "__main__":
    P = precip_openmeteo()
    print(f"Serie Open-Meteo: {P.index.min()}-{P.index.max()}, n={len(P)}")
    print(fig_balance_2025(P))
    reporte(P)

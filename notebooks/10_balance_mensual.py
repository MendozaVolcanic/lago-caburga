"""Notebook 10 — Balance hídrico MENSUAL con estacionalidad nival.

El balance anual (notebooks 03/07) oculta la dinámica estacional. Este modelo
mensual reparte la precipitación entre lluvia (escorrentía rápida) y nieve
(almacenada y liberada en primavera), reproduciendo el régimen nival del lago:
máximos de nivel en primavera, mínimos a fines de otoño.

Usa la serie diaria Open-Meteo (precip + temperatura + nieve).
Salida: notebooks/figs/10_balance_mensual.png + docs/assets/balance_mensual.png
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
OUT = ROOT / "notebooks" / "figs"
OUT.mkdir(exist_ok=True)

C_BG="#0e1a24"; C_FG="#e8eef5"; C_MUTED="#8fa3b0"; C_ACC="#4aa3df"; C_BAD="#c0392b"; C_OK="#27ae60"
plt.rcParams.update({"figure.facecolor":C_BG,"axes.facecolor":C_BG,"savefig.facecolor":C_BG,
    "text.color":C_FG,"axes.labelcolor":C_MUTED,"xtick.color":C_MUTED,"ytick.color":C_MUTED,
    "axes.edgecolor":"#1f3245"})

# Parámetros
A_LAGO = 53e6; A_CUENCA = 282e6
H0 = 489.7; H_BASE = 482.0
EVAP_MM_ANUAL = 600.0
ALPHA = 70.0/12  # drenaje mensual (Hm³/mes por metro)
SEG_MES = 365.25/12 * 86400
T_NIEVE = 2.0      # °C umbral nieve
FUSION = 0.6       # fracción del manto que se derrite por mes cuando T>0


def cargar():
    df = pd.read_csv(DATA / "openmeteo_diario.csv", parse_dates=["fecha"], index_col="fecha")
    m = pd.DataFrame({
        "precip": df["precip"].resample("ME").sum(),
        "temp": df["temp"].resample("ME").mean(),
        "nieve": df["nieve"].resample("ME").sum(),
    })
    return m.dropna()


def simular(m):
    H = H0; manto = 0.0
    rows = []
    # evaporación con ciclo estacional (más en verano)
    for fecha, r in m.iterrows():
        mes = fecha.month
        # partición lluvia/nieve por temperatura
        frac_nieve = 1.0 if r["temp"] < T_NIEVE else (0.0 if r["temp"] > T_NIEVE+3 else 0.4)
        precip_m = r["precip"] / 1000.0
        lluvia = precip_m * (1 - frac_nieve)
        nieva = precip_m * frac_nieve
        manto += nieva
        # fusión si templado
        fusion = 0.0
        if r["temp"] > 0:
            fusion = manto * FUSION * min(1.0, max(0.0, r["temp"]/8))
            manto -= fusion
        agua_disp = lluvia + fusion
        # evaporación estacional (sinusoide, pico enero)
        evap = EVAP_MM_ANUAL/1000.0/12 * (1 + 0.6*np.cos((mes-1)/12*2*np.pi))
        Qo = ALPHA * 1e6 * max(H - H_BASE, 0)
        ingreso = agua_disp * A_LAGO + agua_disp * A_CUENCA * 0.65
        egreso = Qo + evap * A_LAGO
        H += (ingreso - egreso) / A_LAGO
        rows.append({"fecha": fecha, "H": H, "manto": manto*1000})
    return pd.DataFrame(rows).set_index("fecha")


def main():
    m = cargar()
    sim = simular(m)
    print(f"Periodo: {m.index.min().date()}..{m.index.max().date()}")

    # Ciclo estacional medio (climatología mensual del nivel simulado)
    sim["mes"] = sim.index.month
    clim = sim.groupby("mes")["H"].mean()
    print("\nNivel medio por mes (climatología):")
    meses = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
    for mo in range(1,13):
        print(f"  {meses[mo-1]}: {clim[mo]:.2f} m")
    print(f"\nMáximo: {meses[clim.idxmax()-1]} · Mínimo: {meses[clim.idxmin()-1]}")

    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    ax = axes[0]
    reciente = sim.loc["2015":]
    ax.plot(reciente.index, reciente["H"], color=C_ACC, lw=1.2)
    ax.set_title("Nivel mensual simulado 2015-2025 (régimen nival visible)", color=C_FG)
    ax.set_ylabel("Cota (m s.n.m.)"); ax.grid(alpha=0.15)
    ax.axhline(H0, color=C_MUTED, ls=":", alpha=0.5)

    ax = axes[1]
    ax.plot(range(1,13), [clim[mo] for mo in range(1,13)], "o-", color=C_OK, lw=2)
    ax.set_xticks(range(1,13)); ax.set_xticklabels(meses)
    ax.set_title("Ciclo estacional medio: máximo en primavera (deshielo), mínimo en otoño",
                 color=C_FG)
    ax.set_ylabel("Cota media (m s.n.m.)"); ax.grid(alpha=0.15)
    fig.tight_layout()
    fig.savefig(OUT / "10_balance_mensual.png", dpi=140)
    fig.savefig(ROOT / "docs" / "assets" / "balance_mensual.png", dpi=140)
    plt.close(fig)
    print(f"\n→ {OUT / '10_balance_mensual.png'}")


if __name__ == "__main__":
    main()

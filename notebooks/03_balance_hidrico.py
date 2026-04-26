"""Notebook 3 — Balance hídrico simplificado del Lago Caburga.

Replica una versión didáctica del modelo de balance del informe U. Chile 2022
(McPhee et al.). Permite explorar 4 escenarios:

  1. Base                — observado
  2. +Lluvia             — qué pasaría si la megasequía no hubiera ocurrido
  3. +Trafampulli        — qué pasaría si el dique no se hubiera construido
  4. +Lluvia y +Trafampulli — el contrafactual completo

El modelo no busca exactitud predictiva sino mostrar la magnitud relativa de
cada factor sobre el balance del lago.

Parámetros calibrados U. Chile:
  - K (conductividad hidráulica acuífero salida) = 0.00101505 m/s
  - c (coef. escorrentía cuenca) = 0.65
  - H0 (cota inicial año 2000) = 489.7 m s.n.m.
  - Área del lago = 53 km²
  - Cuenca aportante = 282 km² (sin lago)
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

# -- Parámetros físicos ----------------------------------------------------
# Geometría
A_LAGO = 53e6           # m²
A_CUENCA = 282e6        # m² (cuenca aportante sin lago)
H0 = 489.7              # m s.n.m. cota inicial 2000
H_BASE = 482.0          # cota base del nivel hidráulico de salida (asumida)

# Hidroclimáticos
c_ESCORR = 0.65         # coef. escorrentía
EVAP_MM = 600.0         # mm/año

# Drenaje subterráneo: Qo = ALPHA * (H - Hbase), Hm³/año por metro de columna.
# Calibrado para balance estacionario con P=3000 mm/año pre-2010 (ingreso ≈ 590 Hm³/a,
# evap 31.8 Hm³/a → Qo ≈ 558 Hm³/a a H-Hbase=8 m → α ≈ 70 Hm³/(año·m))
ALPHA_DRENAJE = 70.0
SEG_POR_AÑO = 365.25 * 86400


def construir_serie_p() -> pd.Series:
    """Precipitación anual promedio cuenca (estaciones cuenca interior)."""
    df = pd.read_csv(DATA / "precipitacion_diaria_cuenca.csv",
                     parse_dates=["fecha"], index_col="fecha")
    cols = [c for c in df.columns
            if any(n in c for n in ["Caburgua", "Tinquilco", "Tricauco", "Llafenco"])
            and "Ojos" not in c]
    annual = df[cols].resample("YE").sum(min_count=330).mean(axis=1)
    annual.index = annual.index.year
    return annual.dropna()


def simular(P_mm: pd.Series, q_trafampulli_m3s: float = 0.0,
            factor_p: float = 1.0, q_extraccion_m3s: float = 0.05) -> pd.DataFrame:
    """Balance hídrico anual: dS/dt = Pl + Qi + QDTf - Qo - E - Qoe.

    Devuelve DataFrame con cota anual del lago en m s.n.m.
    """
    P = P_mm * factor_p / 1000.0  # m/año

    Pl = P * A_LAGO                                  # m³/año
    Qi = P * A_CUENCA * c_ESCORR                     # m³/año
    QDTf = q_trafampulli_m3s * SEG_POR_AÑO           # m³/año
    E = EVAP_MM / 1000.0 * A_LAGO                    # m³/año
    Qoe = q_extraccion_m3s * SEG_POR_AÑO             # m³/año

    H = H0
    rows = []
    for año, p in P.items():
        # Drenaje subterráneo proporcional a la altura sobre el nivel base
        Qo = ALPHA_DRENAJE * 1e6 * max(H - H_BASE, 0)  # m³/año
        Pl_a = p * A_LAGO
        Qi_a = p * A_CUENCA * c_ESCORR
        ingreso = Pl_a + Qi_a + QDTf
        egreso = Qo + E + Qoe
        dV = ingreso - egreso
        dH = dV / A_LAGO
        H = H + dH
        rows.append({"año": año, "P_mm": P_mm.loc[año], "H_m": H,
                     "ingreso_Hm3": ingreso / 1e6, "egreso_Hm3": egreso / 1e6,
                     "dH_m": dH})
    return pd.DataFrame(rows).set_index("año")


def fig_escenarios(P: pd.Series) -> Path:
    base = simular(P, q_trafampulli_m3s=0.0, factor_p=1.0)
    s2 = simular(P, q_trafampulli_m3s=0.0, factor_p=1.20)   # +20% lluvia (sin megaseq)
    s3 = simular(P, q_trafampulli_m3s=1.0, factor_p=1.0)    # +Trafampulli 1 m³/s
    s4 = simular(P, q_trafampulli_m3s=1.0, factor_p=1.20)   # ambos contrafactuales

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(base.index, base["H_m"], "o-", lw=1.8, color="#c44",
            label="Base (observado: megasequía + dique)")
    ax.plot(s2.index, s2["H_m"], "s-", lw=1.8, color="#4a7",
            label="Sin megasequía (lluvia +20%)")
    ax.plot(s3.index, s3["H_m"], "^-", lw=1.8, color="#46c",
            label="Sin dique (Trafampulli +1 m³/s)")
    ax.plot(s4.index, s4["H_m"], "d-", lw=1.8, color="#888",
            label="Ni megasequía ni dique")
    ax.axvline(2010, color="orange", ls="--", alpha=0.5)
    ax.set(xlabel="Año", ylabel="Cota lago (m s.n.m.)",
           title="Balance hídrico Caburga — escenarios contrafactuales\n"
                 "Modelo simplificado tipo U. de Chile 2022")
    ax.legend(loc="lower left")
    ax.grid(alpha=0.3)
    out = OUT / "03_escenarios_balance.png"
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    plt.close(fig)

    # Tabla comparativa final
    print("\n=== Cota final por escenario (m s.n.m.) ===")
    print(f"  Base                     : {base['H_m'].iloc[-1]:7.2f}")
    print(f"  Sin megasequía (+20% P)  : {s2['H_m'].iloc[-1]:7.2f}  Δ = +{s2['H_m'].iloc[-1] - base['H_m'].iloc[-1]:.2f} m")
    print(f"  Sin dique (Trafampulli)  : {s3['H_m'].iloc[-1]:7.2f}  Δ = +{s3['H_m'].iloc[-1] - base['H_m'].iloc[-1]:.2f} m")
    print(f"  Ambos contrafactuales    : {s4['H_m'].iloc[-1]:7.2f}  Δ = +{s4['H_m'].iloc[-1] - base['H_m'].iloc[-1]:.2f} m")

    # Atribución (descomposición)
    delta_total = s4["H_m"].iloc[-1] - base["H_m"].iloc[-1]
    delta_p = s2["H_m"].iloc[-1] - base["H_m"].iloc[-1]
    delta_q = s3["H_m"].iloc[-1] - base["H_m"].iloc[-1]
    print(f"\n=== Atribución del descenso (al final del periodo) ===")
    if delta_total > 0:
        print(f"  Megasequía:  {delta_p / delta_total * 100:.0f}%")
        print(f"  Dique:       {delta_q / delta_total * 100:.0f}%")
    return out


if __name__ == "__main__":
    P = construir_serie_p()
    print(f"Periodo: {P.index.min()}-{P.index.max()}, n={len(P)} años")
    print(fig_escenarios(P))

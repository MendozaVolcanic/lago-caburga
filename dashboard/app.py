"""Dashboard didáctico — Lago Caburga.

Ejecutar:  streamlit run dashboard/app.py
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"

# -- Parámetros del modelo (idénticos a notebooks/03_balance_hidrico.py) ---
A_LAGO = 53e6
A_CUENCA = 282e6
H0 = 489.7
H_BASE = 482.0
EVAP_MM = 600.0
ALPHA_DRENAJE = 70.0
SEG_POR_AÑO = 365.25 * 86400


@st.cache_data
def cargar_precip() -> pd.Series:
    df = pd.read_csv(DATA / "precipitacion_diaria_cuenca.csv",
                     parse_dates=["fecha"], index_col="fecha")
    cols = [c for c in df.columns
            if any(n in c for n in ["Caburgua", "Tinquilco", "Tricauco", "Llafenco"])
            and "Ojos" not in c]
    s = df[cols].resample("YE").sum(min_count=330).mean(axis=1)
    s.index = s.index.year
    return s.dropna()


def simular(P: pd.Series, q_traf: float, fac_p: float,
            c_esc: float, alpha: float, q_ext: float) -> pd.DataFrame:
    P_use = P * fac_p / 1000.0
    QDTf = q_traf * SEG_POR_AÑO
    E = EVAP_MM / 1000.0 * A_LAGO
    Qoe = q_ext * SEG_POR_AÑO
    H = H0
    rows = []
    for año, p in P_use.items():
        Qo = alpha * 1e6 * max(H - H_BASE, 0)
        ingreso = p * A_LAGO + p * A_CUENCA * c_esc + QDTf
        egreso = Qo + E + Qoe
        H = H + (ingreso - egreso) / A_LAGO
        rows.append({"año": año, "H_m": H, "ingreso_Hm3": ingreso / 1e6,
                     "egreso_Hm3": egreso / 1e6})
    return pd.DataFrame(rows).set_index("año")


# -- UI -------------------------------------------------------------------
st.set_page_config(page_title="Lago Caburga", page_icon="💧", layout="wide")
st.title("💧 Lago Caburga — explorador del balance hídrico")
st.caption("Datos: CR2 1965-2019. Modelo simplificado calibrado contra U. Chile 2022.")

with st.sidebar:
    st.header("Parámetros del modelo")
    fac_p = st.slider("Factor de precipitación (1.0 = observado)",
                      0.7, 1.4, 1.0, 0.05,
                      help="1.0 = lluvia observada. 1.2 simula 'sin megasequía'.")
    q_traf = st.slider("Aporte Trafampulli (m³/s)",
                       0.0, 2.0, 0.0, 0.1,
                       help="0 = post-dique. 0.3 = est. U. Chile. 1-2 = est. U. Austral.")
    with st.expander("Avanzado"):
        c_esc = st.slider("Coef. escorrentía", 0.4, 0.9, 0.65, 0.05)
        alpha = st.slider("α drenaje subterráneo (Hm³/año/m)", 30.0, 120.0, 70.0, 5.0)
        q_ext = st.slider("Extracción derechos (m³/s)", 0.0, 0.3, 0.05, 0.01)

    st.markdown("---")
    st.markdown("**Escenarios sugeridos**")
    st.caption("• Base: factor=1.0, Trafampulli=0\n"
               "• Sin megasequía: factor=1.2\n"
               "• Sin dique (U.Ch): Trafampulli=0.3\n"
               "• Sin dique (U.Aus): Trafampulli=1.5")

P = cargar_precip()
base = simular(P, 0.0, 1.0, 0.65, 70.0, 0.05)
escenario = simular(P, q_traf, fac_p, c_esc, alpha, q_ext)

# -- Métricas top ---------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Cota base 2018 (m s.n.m.)", f"{base['H_m'].iloc[-1]:.2f}")
col2.metric("Cota escenario 2018 (m s.n.m.)", f"{escenario['H_m'].iloc[-1]:.2f}",
            f"{escenario['H_m'].iloc[-1] - base['H_m'].iloc[-1]:+.2f} m")
col3.metric("Δ H período (m)",
            f"{escenario['H_m'].iloc[-1] - escenario['H_m'].iloc[0]:+.2f}")
col4.metric("Precip promedio (mm/año)", f"{(P * fac_p).mean():.0f}")

# -- Gráfico principal -----------------------------------------------------
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7), sharex=True,
                                gridspec_kw={"height_ratios": [2, 1]})
ax1.plot(base.index, base["H_m"], "o-", color="#888", lw=1.4, ms=3,
         label="Base (observado)")
ax1.plot(escenario.index, escenario["H_m"], "o-", color="#c44", lw=2, ms=4,
         label=f"Escenario (P×{fac_p:.2f}, Traf={q_traf:.1f} m³/s)")
ax1.axvline(2010, color="orange", ls="--", alpha=0.5, label="Megasequía")
ax1.axvline(2007, color="purple", ls=":", alpha=0.5, label="Dique Trafampulli")
ax1.set(ylabel="Cota lago (m s.n.m.)",
        title="Cota simulada del Lago Caburga")
ax1.legend(loc="lower left", fontsize=9)
ax1.grid(alpha=0.3)

ax2.bar(P.index, P, color="#48a", alpha=0.55, label="P observada")
ax2.bar(P.index, P * fac_p - P, bottom=P, color="#c44", alpha=0.6,
        label=f"Δ por factor {fac_p:.2f}")
ax2.set(xlabel="Año", ylabel="Precipitación cuenca (mm)")
ax2.legend(fontsize=9)
ax2.grid(axis="y", alpha=0.3)
st.pyplot(fig)

# -- Atribución -----------------------------------------------------------
st.markdown("### Atribución del descenso")
contra_clima = simular(P, q_traf, 1.20, c_esc, alpha, q_ext)
contra_dique = simular(P, max(q_traf + 1.0, 1.0), fac_p, c_esc, alpha, q_ext)
delta_clima = contra_clima["H_m"].iloc[-1] - escenario["H_m"].iloc[-1]
delta_dique = contra_dique["H_m"].iloc[-1] - escenario["H_m"].iloc[-1]
total = delta_clima + delta_dique
if total > 0:
    pct_clima = delta_clima / total * 100
    pct_dique = delta_dique / total * 100
    a, b = st.columns(2)
    a.metric("Atribución a megasequía", f"{pct_clima:.0f}%",
             f"+{delta_clima:.2f} m si no hubiera ocurrido")
    b.metric("Atribución a dique Trafampulli", f"{pct_dique:.0f}%",
             f"+{delta_dique:.2f} m si se restituyera")

st.markdown("---")
st.markdown("""
**Lectura honesta del modelo:**

- Este modelo es **didáctico**, no predictivo. Calibrado a lo grueso contra el
  balance hídrico de U. Chile 2022 (McPhee et al.).
- La atribución relativa (~80% megasequía / ~20% dique) es coherente con las
  conclusiones cualitativas tanto del estudio U. Chile como del informe
  técnico U. Austral, que dice textualmente que el desvío *exacerba* el
  efecto climático (no que sea la causa principal).
- Los datos vienen de CR2 (precipitación diaria por estación, 1965-2019).
  Faltan series de nivel del lago directas — pendiente bajar de DGA.
""")

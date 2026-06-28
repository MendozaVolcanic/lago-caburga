"""Dashboard didáctico — Lago Caburga.

Ejecutar:  streamlit run dashboard/app.py
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
sys.path.insert(0, str(ROOT / "notebooks"))

# Paleta consistente con el sitio
PCOL = dict(bg="#0e1a24", panel="#142434", fg="#e8eef5", muted="#8fa3b0",
            acc="#4aa3df", bad="#c0392b", ok="#27ae60", warn="#e6a23c")
# Nota: NO incluir 'legend' aquí — varias figuras pasan legend= explícito y
# unirlo con **PLOTLY_LAYOUT daría "multiple values for keyword argument 'legend'".
PLOTLY_LAYOUT = dict(
    paper_bgcolor=PCOL["bg"], plot_bgcolor=PCOL["bg"],
    font=dict(color=PCOL["fg"], family="Inter, system-ui, sans-serif"),
    margin=dict(l=60, r=20, t=50, b=40), hovermode="x unified",
)

# -- Parámetros del modelo ------------------------------------------------
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


@st.cache_data
def cargar_precip_openmeteo() -> pd.Series:
    """Serie Open-Meteo ERA5 1950-2025 (cubre hasta el presente)."""
    f = DATA / "openmeteo_precip_anual.csv"
    if not f.exists():
        return pd.Series(dtype=float)
    return pd.read_csv(f, index_col="año")["Lago Caburga"].dropna()


# Fases ENSO (El Niño cálido / La Niña frío) — años hidrológicos australes
ENSO = {
    "niño": [1957, 1965, 1972, 1982, 1987, 1991, 1997, 2002, 2009, 2015, 2018, 2023],
    "niña": [1954, 1964, 1970, 1973, 1975, 1988, 1998, 1999, 2007, 2010, 2011,
             2020, 2021, 2022, 2025],
}


@st.cache_data
def cargar_anomalias() -> pd.DataFrame:
    df = pd.read_csv(DATA / "precipitacion_diaria_cuenca.csv",
                     parse_dates=["fecha"], index_col="fecha")
    annual = df.resample("YE").sum(min_count=330)
    annual.index = annual.index.year
    baseline = annual.loc[1965:2009].mean()
    anom = (annual - baseline) / baseline * 100
    return anom


@st.cache_data
def cargar_caudales() -> pd.DataFrame:
    df = pd.read_csv(DATA / "caudales_diarios_cuenca.csv",
                     parse_dates=["fecha"], index_col="fecha")
    annual = df.resample("YE").mean()
    counts = df.resample("YE").count()
    annual = annual.where(counts >= 330)
    annual.index = annual.index.year
    return annual.dropna(how="all")


@st.cache_data
def cargar_nivel_proxy() -> pd.Series:
    return pd.read_csv(DATA / "nivel_caburga_proxy_anual.csv",
                       index_col=0)["H_proxy_m"]


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
st.caption("Datos: CR2 (precipitación y caudales 1965-2019). "
           "Modelo simplificado calibrado contra U. Chile 2022.")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["📈 Balance hídrico", "🌧 Datos observados", "🗺 Mapa",
     "📜 Historia", "🛰 Sentinel-2", "ℹ️ Lectura"])

with st.sidebar:
    st.header("Fuente de datos")
    fuente = st.radio(
        "Serie de precipitación",
        ["Open-Meteo ERA5 (1950-2025)", "CR2 estaciones (1965-2019)"],
        help="Open-Meteo llega hasta 2025 (incluye El Niño 2024 y La Niña 2025). "
             "CR2 es medición directa de estación, más fuerte la señal de sequía.")
    st.markdown("---")
    st.header("Parámetros del modelo")
    fac_p = st.slider("Factor de precipitación", 0.7, 1.4, 1.0, 0.05,
                      help="1.0 = lluvia observada. 1.2 simula 'sin megasequía'.")
    q_traf = st.slider("Aporte Trafampulli (m³/s)", 0.0, 2.0, 0.0, 0.1,
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

if fuente.startswith("Open-Meteo"):
    P_full = cargar_precip_openmeteo()
    P = P_full.loc[1990:] if not P_full.empty else cargar_precip()
else:
    P = cargar_precip()

base = simular(P, 0.0, 1.0, 0.65, 70.0, 0.05)
escenario = simular(P, q_traf, fac_p, c_esc, alpha, q_ext)


def marca_enso(ax):
    """Sombrea El Niño (azul) y La Niña (rojo) detrás de la serie."""
    for año in ENSO["niño"]:
        if P.index.min() <= año <= P.index.max():
            ax.axvspan(año - 0.5, año + 0.5, color="#4aa3df", alpha=0.10, zorder=0)
    for año in ENSO["niña"]:
        if P.index.min() <= año <= P.index.max():
            ax.axvspan(año - 0.5, año + 0.5, color="#c0392b", alpha=0.10, zorder=0)


# ============ Tab 1: Balance ============
with tab1:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(f"Cota base {base.index[-1]} (m s.n.m.)", f"{base['H_m'].iloc[-1]:.2f}")
    col2.metric("Cota escenario (m s.n.m.)", f"{escenario['H_m'].iloc[-1]:.2f}",
                f"{escenario['H_m'].iloc[-1] - base['H_m'].iloc[-1]:+.2f} m")
    col3.metric("Δ período (m)",
                f"{escenario['H_m'].iloc[-1] - escenario['H_m'].iloc[0]:+.2f}")
    col4.metric("Precip prom (mm/año)", f"{(P * fac_p).mean():.0f}")

    st.caption("🟦 bandas azules = El Niño · 🟥 bandas rojas = La Niña · "
               "pasa el cursor para ver valores, arrastra para hacer zoom")

    figp = make_subplots(rows=2, cols=1, shared_xaxes=True,
                         row_heights=[0.62, 0.38], vertical_spacing=0.08,
                         subplot_titles=("Cota simulada del Lago Caburga",
                                         "Precipitación de la cuenca"))
    # Bandas ENSO como shapes de fondo
    for año in ENSO["niño"]:
        if P.index.min() <= año <= P.index.max():
            figp.add_vrect(x0=año-0.5, x1=año+0.5, fillcolor=PCOL["acc"],
                           opacity=0.10, line_width=0, row=1, col=1)
            figp.add_vrect(x0=año-0.5, x1=año+0.5, fillcolor=PCOL["acc"],
                           opacity=0.10, line_width=0, row=2, col=1)
    for año in ENSO["niña"]:
        if P.index.min() <= año <= P.index.max():
            figp.add_vrect(x0=año-0.5, x1=año+0.5, fillcolor=PCOL["bad"],
                           opacity=0.10, line_width=0, row=1, col=1)
            figp.add_vrect(x0=año-0.5, x1=año+0.5, fillcolor=PCOL["bad"],
                           opacity=0.10, line_width=0, row=2, col=1)
    # Líneas de cota
    figp.add_trace(go.Scatter(x=base.index, y=base["H_m"], name="Base (observado)",
                   mode="lines+markers", line=dict(color=PCOL["muted"], width=2),
                   marker=dict(size=4),
                   hovertemplate="%{x}: %{y:.2f} m<extra>Base</extra>"), row=1, col=1)
    figp.add_trace(go.Scatter(x=escenario.index, y=escenario["H_m"],
                   name=f"Escenario (P×{fac_p:.2f}, Traf={q_traf:.1f})",
                   mode="lines+markers", line=dict(color=PCOL["bad"], width=3),
                   marker=dict(size=5),
                   hovertemplate="%{x}: %{y:.2f} m<extra>Escenario</extra>"), row=1, col=1)
    # Eventos
    for año, txt, col in [(2007, "Dique", PCOL["warn"]), (2010, "Megasequía", PCOL["warn"]),
                          (2022, "Cae dique", PCOL["ok"])]:
        if P.index.min() <= año <= P.index.max():
            figp.add_vline(x=año, line=dict(color=col, dash="dot", width=1),
                           row=1, col=1)
    # Precipitación
    figp.add_trace(go.Bar(x=P.index, y=P.values, name="P observada",
                   marker_color=PCOL["acc"], opacity=0.65,
                   hovertemplate="%{x}: %{y:.0f} mm<extra></extra>"), row=2, col=1)
    if fac_p != 1.0:
        figp.add_trace(go.Bar(x=P.index, y=(P*fac_p - P).values, name=f"Δ factor {fac_p:.2f}",
                       marker_color=PCOL["bad"], opacity=0.6,
                       hovertemplate="+%{y:.0f} mm<extra></extra>"), row=2, col=1)
        figp.update_layout(barmode="stack")
    figp.update_yaxes(title_text="Cota (m s.n.m.)", gridcolor="#1f3245", row=1, col=1)
    figp.update_yaxes(title_text="mm/año", gridcolor="#1f3245", row=2, col=1)
    figp.update_xaxes(gridcolor="#1f3245", row=2, col=1)
    figp.update_layout(**PLOTLY_LAYOUT, height=560,
                       legend=dict(orientation="h", y=1.12, x=0))
    st.plotly_chart(figp, use_container_width=True)

    if fuente.startswith("Open-Meteo") and base.index.max() >= 2025:
        st.info(f"📍 El modelo reproduce la **recuperación** de El Niño "
                f"(2021→2024: {base['H_m'].get(2024, float('nan')) - base['H_m'].get(2021, float('nan')):+.1f} m) "
                f"y el **nuevo descenso** de La Niña "
                f"(2024→2025: {base['H_m'].get(2025, float('nan')) - base['H_m'].get(2024, float('nan')):+.1f} m). "
                "Esta sensibilidad a la lluvia es la mejor evidencia de que el clima manda.")

    st.markdown("### Atribución del descenso")
    contra_clima = simular(P, q_traf, 1.20, c_esc, alpha, q_ext)
    contra_dique = simular(P, max(q_traf + 1.0, 1.0), fac_p, c_esc, alpha, q_ext)
    delta_clima = contra_clima["H_m"].iloc[-1] - escenario["H_m"].iloc[-1]
    delta_dique = contra_dique["H_m"].iloc[-1] - escenario["H_m"].iloc[-1]
    total = delta_clima + delta_dique
    if total > 0:
        a, b = st.columns(2)
        a.metric("Atribución a megasequía",
                 f"{delta_clima / total * 100:.0f}%",
                 f"+{delta_clima:.2f} m si no hubiera ocurrido")
        b.metric("Atribución a dique Trafampulli",
                 f"{delta_dique / total * 100:.0f}%",
                 f"+{delta_dique:.2f} m si se restituyera")

# ============ Tab 2: Datos observados ============
with tab2:
    st.subheader("Anomalías de precipitación post-2010")
    anom = cargar_anomalias()
    cols_orden = sorted(anom.columns,
                        key=lambda c: anom.loc[2010:, c].mean() if anom.loc[2010:, c].notna().any() else 0)
    promedio = anom[[c for c in anom.columns
                     if any(n in c for n in ["Caburgua", "Tinquilco", "Tricauco", "Llafenco"])
                     and "Ojos" not in c]].mean(axis=1).dropna()
    colors = [PCOL["bad"] if v < 0 else PCOL["acc"] for v in promedio.values]
    figa = go.Figure()
    figa.add_trace(go.Bar(x=promedio.index, y=promedio.values, marker_color=colors,
                          opacity=0.85, name="Anomalía",
                          hovertemplate="%{x}: %{y:+.0f}%<extra></extra>"))
    figa.add_hline(y=0, line=dict(color=PCOL["fg"], width=1))
    figa.add_vline(x=2010, line=dict(color=PCOL["warn"], dash="dash", width=1.5))
    figa.add_annotation(x=2010, y=1, yref="paper", yanchor="bottom",
                        text="megasequía", showarrow=False, font=dict(color=PCOL["warn"], size=11))
    figa.update_yaxes(title_text="Anomalía (%) vs 1965-2009", gridcolor="#1f3245", zeroline=False)
    figa.update_xaxes(title_text="Año", gridcolor="#1f3245")
    figa.update_layout(**PLOTLY_LAYOUT, height=420, showlegend=False,
                       title="Anomalía de precipitación promedio cuenca")
    st.plotly_chart(figa, use_container_width=True)
    st.caption("Pasa el cursor para ver el valor de cada año · arrastra para hacer zoom.")

    st.subheader("Caída por estación post-2010")
    res = []
    for col in anom.columns:
        s = anom[col].dropna()
        post = s.loc[2010:].mean() if (s.index >= 2010).any() else np.nan
        if pd.notna(post):
            nombre = col.split(" ", 1)[1] if " " in col else col
            res.append({"Estación": nombre, "Δ% post-2010": round(post, 1)})
    st.dataframe(pd.DataFrame(res).sort_values("Δ% post-2010"),
                 hide_index=True, use_container_width=True)
    st.caption("Lago Caburga muestra la caída más fuerte (-30% a -34%), "
               "mientras estaciones más bajas como Pucón o Curarrehue solo "
               "-10% a -15%. La señal climática es real y diferencial por altitud.")

    st.subheader("Validación cruzada: CR2 estaciones vs CAMELS-CL cuenca")
    fig06 = ROOT / "notebooks" / "figs" / "06_balance_camels.png"
    if fig06.exists():
        st.image(str(fig06), use_container_width=True,
                 caption="Comparación de productos de precipitación (r=0.957). "
                         "CAMELS-CL cuenca-promedio (CR2MET grillado) vs CR2 estaciones. "
                         "Ambos confirman caída sostenida post-2010, validando los datos de entrada al balance.")

    st.subheader("Caudales medios anuales — ríos vecinos")
    Q = cargar_caudales()
    figq = go.Figure()
    for col in Q.columns:
        s = Q[col].dropna()
        if len(s) < 5:
            continue
        nombre = col.split(" ", 1)[1] if " " in col else col
        figq.add_trace(go.Scatter(x=s.index, y=s.values, mode="lines+markers",
                       name=nombre, line=dict(width=1.5), marker=dict(size=4),
                       hovertemplate="%{x}: %{y:.1f} m³/s<extra>" + nombre + "</extra>"))
    figq.add_vline(x=2010, line=dict(color=PCOL["warn"], dash="dash", width=1.5))
    figq.update_yaxes(title_text="Caudal medio anual (m³/s)", gridcolor="#1f3245")
    figq.update_xaxes(title_text="Año", gridcolor="#1f3245")
    figq.update_layout(**PLOTLY_LAYOUT, height=440,
                       title="Caudales — ríos de la cuenca Toltén",
                       legend=dict(orientation="h", y=-0.18, x=0))
    st.plotly_chart(figq, use_container_width=True)

# ============ Tab 3: Mapa ============
with tab3:
    st.subheader("Mapa de la cuenca")
    map_path = ROOT / "notebooks" / "figs" / "04_mapa.html"
    if map_path.exists():
        st.components.v1.html(map_path.read_text(encoding="utf-8"), height=600)
    else:
        st.warning("Genera el mapa con: `python notebooks/04_mapa.py`")
    st.caption("Marcadores rojos = dique Trafampulli, azules = estaciones DGA, "
               "morados = Ojos del Caburga (drenaje subterráneo).")

# ============ Tab 4: Historia ============
with tab4:
    st.subheader("Cronología del conflicto")
    eventos = [
        ("Holoceno", "Lava volcánica bloquea drenaje superficial; nace el sistema Ojos del Caburga"),
        ("1940s", "Primer descenso histórico documentado por testimonio"),
        ("1979-2007", "Aerofotografías SAF muestran el brazo del Trafampulli activo hacia el Caburga"),
        ("2005", "Vecinos del Lago Colico denuncian a propietario fundo Llanqui-Llanqui"),
        ("2007 (Of. DGA 347)", "DGA obliga a construir el dique. Sin EIA"),
        ("2009", "Dique entra en operación. Caudal hacia Caburga = 0"),
        ("2010", "Inicia la megasequía centro-sur de Chile"),
        ("Dic 2021", "Informe U. Austral (Iroumé & Ulloa). 'El desvío exacerba el efecto climático'"),
        ("Ene 2022", "Informe U. Chile (McPhee). 'La megasequía es la causa de primer orden'"),
        ("16 mayo 2022", "🪓 Comunidad mapuche destruye el dique tras 4 días de trabajo manual"),
        ("31 ene 2023", "Resolución DGA: ordena reconstruir el dique"),
        ("Mar 2024", "Informe Contraloría: observaciones administrativas a la DGA"),
        ("Jun 2023 - Jun 2024", "El Niño. Lago recupera +350 m de costa"),
        ("13 mar 2025", "Apelaciones Temuco: orden de no innovar"),
        ("5 ago 2025", "⚖️ Corte Suprema revoca y autoriza reconstrucción del dique"),
        ("Nov 2025", "DGA confirma cierre del Estero La Cascada"),
        ("Dic 2025", "DGA mide: solo 4% del estero llega al lago en 11 puntos"),
        ("Abr 2026", "Estado actual: conflicto abierto, lago descendiendo estacionalmente"),
    ]
    for fecha, evento in eventos:
        c1, c2 = st.columns([1, 4])
        c1.markdown(f"**{fecha}**")
        c2.markdown(evento)
    st.caption("Detalle completo en HISTORIA_TRAFAMPULLI.md del repositorio.")

# ============ Tab 5: Sentinel-2 ============
with tab5:
    st.subheader("Superficie del lago — análisis NDWI Sentinel-2")
    s2_path = DATA / "lago_superficie_s2.csv"
    if s2_path.exists():
        s2 = pd.read_csv(s2_path, parse_dates=["fecha"])
        if not s2.empty:
            s2 = s2.sort_values("fecha").set_index("fecha")
            fig, ax = plt.subplots(figsize=(11, 4.5))
            ax.plot(s2.index, s2["superficie_lago_km2"], "o-", color="#46a", lw=1.5)
            ax.set(xlabel="Fecha", ylabel="Superficie con NDWI > 0 (km²)",
                   title="Superficie del lago detectada en imágenes Sentinel-2")
            ax.grid(alpha=0.3)
            ax.axvspan(pd.Timestamp("2010-01-01"), pd.Timestamp("2020-12-31"),
                       alpha=0.08, color="orange", label="Megasequía")
            ax.legend()
            st.pyplot(fig)
            st.dataframe(s2.tail(15), use_container_width=True)
            st.caption(f"{len(s2)} escenas procesadas. Para añadir más años: "
                       "`python scripts/sentinel2_caburga.py --since 2020-01-01`")
        else:
            st.info("No hay datos aún. Corre `python scripts/sentinel2_caburga.py --year 2020`")
    else:
        st.info("Aún no hay datos Sentinel-2. Corre `python scripts/sentinel2_caburga.py --year 2020`")

    st.markdown("### Timelapse")
    gif_path = ROOT / "notebooks" / "figs" / "sentinel_timelapse.gif"
    if gif_path.exists():
        st.image(str(gif_path), caption="Timelapse NDWI Sentinel-2 (regenerar con `python scripts/make_gif.py`)")

    st.markdown("### Frames disponibles")
    sentinel_frames = sorted((ROOT / "notebooks" / "figs" / "sentinel").glob("*.png"))
    if sentinel_frames:
        cols = st.columns(min(3, len(sentinel_frames)))
        for i, f in enumerate(sentinel_frames[:9]):
            with cols[i % 3]:
                st.image(str(f), caption=f.stem, use_container_width=True)

# ============ Tab 6: Lectura ============
with tab6:
    st.markdown("""
### Lectura honesta del modelo

- Este modelo es **didáctico**, no predictivo. Calibrado a lo grueso contra el
  balance hídrico de U. Chile 2022 (McPhee et al.).
- La atribución relativa (~80% megasequía / ~20% dique) es coherente con las
  conclusiones cualitativas tanto del estudio U. Chile como del informe
  técnico U. Austral, que dice textualmente que el desvío *exacerba* el
  efecto climático (no que sea la causa principal).
- Los datos de precipitación y caudales vienen de CR2 (1965-2019, cobertura
  diaria). Las series de nivel del lago directas se descargan desde el
  portal DGA SNIA — el procedimiento está documentado en
  `docs/DESCARGA_DGA_NIVEL.md`.

### Hallazgos clave

1. **La precipitación cayó en TODAS las estaciones post-2010**, pero la caída
   es desigual: Lago Caburga -34%, Tinquilco -22%, Pucón -11%, Curarrehue -9%.
   Las estaciones de mayor altitud cayeron más → señal climática real.

2. **El nivel del Caburga cayó 6× más rápido que Villarrica o Neltume**
   (-0.234 vs -0.036/-0.042 m/año). Esto es el indicio más fuerte de que
   algo más que el clima regional opera en este caso particular.

3. **El modelo de balance**, incluso suponiendo el aporte máximo del
   Trafampulli (2 m³/s, U. Austral), no logra explicar todo el descenso —
   la megasequía es necesaria.

### Datos faltantes críticos

- Caudal histórico Río Blanco (estación recién instalada nov 2021)
- Caudal histórico Trafampulli al punto de cierre con Caburga
- Limnimetría Lago Colico (sin estación DGA)
- Caudal Ojos del Caburga / Río Caburga aguas abajo
- Batimetría actualizada del lago

### Repositorio

[github.com/MendozaVolcanic/lago-caburga](https://github.com/MendozaVolcanic/lago-caburga)
""")

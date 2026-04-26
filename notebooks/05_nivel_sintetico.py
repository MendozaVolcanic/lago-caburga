"""Notebook 5 — Reconstrucción de la serie de nivel del Lago Caburga.

Mientras no se baje la serie diaria del portal DGA (ver
docs/DESCARGA_DGA_NIVEL.md), reconstruimos una serie anual aproximada
usando:

  (a) los puntos conocidos: promedios por década y trend de U. Austral 2021
  (b) la correlación esperada con la precipitación de cuenca (CR2)

Genera figura comparativa nivel observado (proxy) vs precipitación.
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


def serie_nivel_proxy() -> pd.Series:
    """Construye una serie anual aproximada del nivel del Caburga 2000-2020.

    Se basa en:
      - Tendencia lineal -0.234 m/año (U. Austral)
      - Cota promedio 2000-2010 = 9.6 m
      - Cota promedio 2011-2020 = 7.1 m
    """
    años = np.arange(2000, 2021)
    base = 9.6 - 0.234 * (años - 2005)
    # Ajuste para que promedios por década calcen
    pre = base[años <= 2010].mean()
    post = base[años > 2010].mean()
    base[años <= 2010] += (9.6 - pre)
    base[años > 2010] += (7.1 - post)
    return pd.Series(base, index=años, name="H_proxy_m")


def serie_precip_cuenca() -> pd.Series:
    df = pd.read_csv(DATA / "precipitacion_diaria_cuenca.csv",
                     parse_dates=["fecha"], index_col="fecha")
    cols = [c for c in df.columns
            if any(n in c for n in ["Caburgua", "Tinquilco", "Tricauco", "Llafenco"])
            and "Ojos" not in c]
    s = df[cols].resample("YE").sum(min_count=330).mean(axis=1)
    s.index = s.index.year
    return s.dropna()


def fig_correlacion(H: pd.Series, P: pd.Series) -> Path:
    df = pd.concat([H, P.rename("P_mm")], axis=1).dropna()
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    ax = axes[0]
    ax2 = ax.twinx()
    ax.bar(P.index, P.values, color="#48a", alpha=0.55, label="Precipitación cuenca")
    ax2.plot(H.index, H.values, "o-", color="#c44", lw=2, label="Nivel Caburga (proxy)")
    ax.set_xlabel("Año")
    ax.set_ylabel("Precipitación cuenca (mm)", color="#48a")
    ax2.set_ylabel("Nivel Caburga (m)", color="#c44")
    ax.set_title("Precipitación vs Nivel del lago — anual")
    ax.set_xlim(1965, 2021)

    ax = axes[1]
    ax.scatter(df["P_mm"], df["H_proxy_m"], color="#356", s=60)
    for año in df.index:
        ax.annotate(str(año), (df.loc[año, "P_mm"], df.loc[año, "H_proxy_m"]),
                    xytext=(4, 2), textcoords="offset points", fontsize=8)
    z = np.polyfit(df["P_mm"], df["H_proxy_m"], 1)
    xs = np.linspace(df["P_mm"].min(), df["P_mm"].max(), 50)
    ax.plot(xs, np.poly1d(z)(xs), "r--",
            label=f"y = {z[0]:.3f}x + {z[1]:.1f}")
    r2 = np.corrcoef(df["P_mm"], df["H_proxy_m"])[0, 1] ** 2
    ax.set(xlabel="Precipitación cuenca (mm/año)",
           ylabel="Nivel Caburga (m)",
           title=f"Correlación P vs H — R² = {r2:.2f}")
    ax.legend()
    ax.grid(alpha=0.3)
    out = OUT / "05_correlacion_p_h.png"
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    plt.close(fig)
    print(f"R² entre precipitación y nivel proxy: {r2:.3f}")
    return out


if __name__ == "__main__":
    H = serie_nivel_proxy()
    P = serie_precip_cuenca()
    H.to_csv(DATA / "nivel_caburga_proxy_anual.csv", header=True)
    print(f"Serie proxy guardada → {DATA / 'nivel_caburga_proxy_anual.csv'}")
    print(fig_correlacion(H, P))

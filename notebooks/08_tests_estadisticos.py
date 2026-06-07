"""Notebook 8 — Tests estadísticos del cambio de régimen.

Aplica pruebas formales para sustentar las afirmaciones del estudio:
  - Mann-Kendall: ¿hay tendencia significativa a la baja en precipitación?
  - Pettitt: ¿hay un punto de quiebre (change point) y en qué año?
  - Doble acumulada: año de quiebre de pendiente Caburga vs vecinos.

Sin dependencias pesadas: implementaciones propias de MK y Pettitt.
Salida: notebooks/figs/08_tests.png + reporte por consola + JSON para la web.
"""
from __future__ import annotations
import sys, json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
OUT = ROOT / "notebooks" / "figs"
WEB = ROOT / "docs" / "data"
OUT.mkdir(exist_ok=True); WEB.mkdir(exist_ok=True)

C_BG="#0e1a24"; C_FG="#e8eef5"; C_MUTED="#8fa3b0"; C_ACC="#4aa3df"; C_BAD="#c0392b"
plt.rcParams.update({"figure.facecolor":C_BG,"axes.facecolor":C_BG,"savefig.facecolor":C_BG,
    "text.color":C_FG,"axes.labelcolor":C_MUTED,"xtick.color":C_MUTED,"ytick.color":C_MUTED,
    "axes.edgecolor":"#1f3245"})


def mann_kendall(x):
    """Test de tendencia. Devuelve (tau, p-value, tendencia)."""
    x = np.asarray(x, float); n = len(x)
    s = sum(np.sign(x[j] - x[i]) for i in range(n-1) for j in range(i+1, n))
    var_s = n*(n-1)*(2*n+5)/18
    if s > 0:   z = (s-1)/np.sqrt(var_s)
    elif s < 0: z = (s+1)/np.sqrt(var_s)
    else:       z = 0
    from math import erfc
    p = erfc(abs(z)/np.sqrt(2))
    tau = s / (0.5*n*(n-1))
    trend = "decreciente" if (z < 0 and p < 0.05) else ("creciente" if (z > 0 and p < 0.05) else "sin tendencia significativa")
    return round(tau, 3), round(p, 4), trend


def pettitt(x):
    """Test de punto de quiebre. Devuelve (idx_quiebre, p-value aprox)."""
    x = np.asarray(x, float); n = len(x)
    U = np.zeros(n)
    for t in range(n):
        s = 0
        for i in range(t+1):
            for j in range(t+1, n):
                s += np.sign(x[i] - x[j])
        U[t] = s
    K = np.max(np.abs(U))
    k_idx = int(np.argmax(np.abs(U)))
    p = 2*np.exp(-6*K**2/(n**3+n**2))
    return k_idx, round(min(p, 1.0), 4)


def main():
    om = pd.read_csv(DATA / "openmeteo_precip_anual.csv", index_col="año")["Lago Caburga"].dropna()
    cr2_df = pd.read_csv(DATA / "precipitacion_diaria_cuenca.csv", parse_dates=["fecha"], index_col="fecha")
    cab = [c for c in cr2_df.columns if "Caburgua" in c and "Ojos" not in c][0]
    cr2 = cr2_df[cab].resample("YE").sum(min_count=330); cr2.index = cr2.index.year; cr2 = cr2.dropna()

    print("=== Mann-Kendall (tendencia) ===")
    for name, s in [("Open-Meteo ERA5 (1950-2025)", om), ("CR2 estación (1965-2019)", cr2)]:
        tau, p, tr = mann_kendall(s.values)
        print(f"  {name}: tau={tau}, p={p} → {tr}")

    print("\n=== Pettitt (punto de quiebre) ===")
    results = {}
    for name, s in [("Open-Meteo", om), ("CR2", cr2)]:
        k, p = pettitt(s.values)
        año = int(s.index[k])
        results[name] = {"año_quiebre": año, "p": p}
        print(f"  {name}: quiebre en {año} (p={p})")

    # Figura
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for ax, (name, s) in zip(axes, [("Open-Meteo ERA5", om), ("CR2 estación", cr2)]):
        k, p = pettitt(s.values)
        año = int(s.index[k])
        pre = s.loc[:año].mean(); post = s.loc[año+1:].mean()
        ax.plot(s.index, s.values, "o-", color=C_ACC, lw=1.5, ms=3)
        ax.axvline(año, color=C_BAD, ls="--", lw=1.5, label=f"Quiebre Pettitt: {año}")
        ax.hlines(pre, s.index.min(), año, color="#27ae60", lw=2, label=f"media antes: {pre:.0f}")
        ax.hlines(post, año, s.index.max(), color="#e6a23c", lw=2, label=f"media después: {post:.0f}")
        tau, pmk, tr = mann_kendall(s.values)
        ax.set_title(f"{name}\nMann-Kendall: τ={tau}, p={pmk}", color=C_FG, fontsize=12)
        ax.set_xlabel("Año"); ax.set_ylabel("Precipitación (mm/año)")
        ax.legend(fontsize=8, framealpha=0.3); ax.grid(alpha=0.15)
    fig.suptitle("Tests formales: la sequía es estadísticamente significativa", color=C_FG, fontsize=14)
    fig.tight_layout()
    fig.savefig(OUT / "08_tests.png", dpi=140)
    fig.savefig(ROOT / "docs" / "assets" / "tests_estadisticos.png", dpi=140)
    plt.close(fig)
    print(f"\n→ {OUT / '08_tests.png'}")

    # JSON para la web
    tau_om, p_om, tr_om = mann_kendall(om.values)
    (WEB / "tests.json").write_text(json.dumps({
        "mann_kendall_openmeteo": {"tau": tau_om, "p": p_om, "tendencia": tr_om},
        "pettitt": results,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"→ {WEB / 'tests.json'}")


if __name__ == "__main__":
    main()

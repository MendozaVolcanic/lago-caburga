"""
Notebook 1 — Correlación maestra: precipitación vs nivel del Lago Caburgua.

Este script carga los datos extraídos del informe U. Austral 2021 y produce:
  (a) Series temporales de precipitación promedio entre estaciones de cuenca.
  (b) Comparación con el nivel limnimétrico (resumen por periodo).
  (c) Tendencia lineal y correlación.

Datos crudos consolidados aún pendientes de descargar desde el portal DGA
(https://snia.mop.gob.cl/BNAConsultas). Mientras tanto trabajamos con los
datos publicados en los informes.
"""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
OUT = ROOT / "notebooks" / "figs"
OUT.mkdir(exist_ok=True)


def load_precip() -> pd.DataFrame:
    df = pd.read_csv(DATA / "precipitacion_anual_uaustral.csv")
    df["promedio"] = df.drop(columns=["año"]).mean(axis=1, skipna=True)
    return df


def load_caudal() -> pd.DataFrame:
    return pd.read_csv(DATA / "caudales_anuales_uaustral.csv")


def fig_precipitacion(df: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(10, 5))
    for col in df.columns:
        if col in ("año", "promedio"):
            continue
        ax.plot(df["año"], df[col], alpha=0.35, label=col)
    ax.plot(df["año"], df["promedio"], color="black", lw=2.2, label="Promedio")

    z = np.polyfit(df["año"], df["promedio"], 1)
    ax.plot(df["año"], np.poly1d(z)(df["año"]), "r--",
            label=f"Tendencia: {z[0]:.0f} mm/año")

    ax.set_title("Precipitación anual — estaciones cuenca Caburga (2000-2020)")
    ax.set_xlabel("Año")
    ax.set_ylabel("Precipitación (mm)")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(alpha=0.3)
    out = OUT / "01_precipitacion_anual.png"
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return out


def fig_caudales(df: pd.DataFrame) -> Path:
    fig, axes = plt.subplots(2, 3, figsize=(13, 7), sharex=True)
    cols = [c for c in df.columns if c != "año"]
    for ax, col in zip(axes.flat, cols):
        ax.plot(df["año"], df[col], "o-", lw=1.2)
        valid = df[["año", col]].dropna()
        if len(valid) > 2:
            z = np.polyfit(valid["año"], valid[col], 1)
            ax.plot(df["año"], np.poly1d(z)(df["año"]), "r--",
                    label=f"{z[0]:+.2f} m³/s/año")
            ax.legend(fontsize=8)
        ax.set_title(col.replace("_", " "), fontsize=9)
        ax.grid(alpha=0.3)
    axes.flat[-1].axis("off")
    fig.suptitle("Caudal medio anual — estaciones vecinas (2000-2020)")
    out = OUT / "01_caudales_vecinos.png"
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return out


def fig_nivel_resumen() -> Path:
    df = pd.read_csv(DATA / "nivel_caburgua_resumen.csv")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    x = np.arange(len(df))
    w = 0.25
    ax.bar(x - w, df["h_min_m"], w, label="Mín", color="#c44")
    ax.bar(x, df["h_promedio_m"], w, label="Promedio", color="#48a")
    ax.bar(x + w, df["h_max_m"], w, label="Máx", color="#4a7")
    ax.set_xticks(x)
    ax.set_xticklabels(df["periodo"])
    ax.set_ylabel("Altura limnimétrica (m)")
    ax.set_title("Lago Caburga — nivel por década (DGA via U. Austral 2021)")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    out = OUT / "01_nivel_resumen.png"
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return out


if __name__ == "__main__":
    precip = load_precip()
    caudal = load_caudal()
    print(fig_precipitacion(precip))
    print(fig_caudales(caudal))
    print(fig_nivel_resumen())
    print("\nResumen precipitación promedio cuenca:")
    print(precip[["año", "promedio"]].to_string(index=False))

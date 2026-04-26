"""Parser idempotente para los archivos descargados manualmente del portal DGA BNA.

Detecta automáticamente formato (Excel xlsx, CSV con encoding latin-1, TXT con
header de 5-15 líneas) y produce un CSV unificado por estación.

El portal DGA SNIA típicamente exporta archivos con:
  - 5-15 líneas de header con metadatos (Estación, Cuenca, Variable, etc)
  - Tabla con columnas: AÑO, MES, DIA, VALOR, CALIDAD
  - Encoding latin-1 (Windows-1252) habitual

Uso:
  Coloca los archivos descargados en data/raw/dga/ con nombres descriptivos:
    lago_caburgua_nivel_diario.xlsx
    lago_villarrica_nivel_diario.xlsx
    rio_pucon_caudal_diario.csv
    ... etc.

  Luego:
    python scripts/extract_dga_niveles.py

Salidas:
  data/processed/niveles_lagos_diarios.csv
  data/processed/caudales_dga_diarios.csv
  data/processed/precipitacion_dga_diaria.csv
"""
from __future__ import annotations
import re
import sys
from pathlib import Path
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "raw" / "dga"
OUT = ROOT / "data" / "processed"

# Mapeo nombre archivo → variable / estación
ARCHIVOS = {
    # nivel
    "lago_caburgua_nivel": ("nivel", "lago_caburgua"),
    "lago_villarrica_nivel": ("nivel", "lago_villarrica"),
    "lago_tinquilco_nivel": ("nivel", "lago_tinquilco"),
    # precip
    "lago_caburgua_precip": ("precip", "lago_caburgua"),
    # caudal
    "rio_pucon_caudal": ("caudal", "rio_pucon_quelhue"),
    "rio_curaco_colico_caudal": ("caudal", "rio_curaco_colico"),
    "rio_trafampulli_caudal": ("caudal", "rio_trafampulli"),
    "rio_blanco_caburga_caudal": ("caudal", "rio_blanco_caburga"),
}


def detect_header_rows(path: Path) -> int:
    """Cuenta líneas hasta encontrar la fila de datos (empieza con 'AÑO' o año numérico)."""
    encodings = ["latin-1", "utf-8", "cp1252"]
    for enc in encodings:
        try:
            with open(path, "r", encoding=enc, errors="replace") as f:
                for i, line in enumerate(f):
                    line_norm = line.strip().upper()
                    if re.match(r"^(A[ÑN]O|FECHA|YEAR|YEAR;|\d{4}[\-/])", line_norm):
                        return i
                    if i > 50:
                        break
            break
        except UnicodeDecodeError:
            continue
    return 0


def leer_archivo(path: Path) -> pd.DataFrame:
    """Lee un archivo DGA, devuelve DF con columnas (fecha, valor, calidad)."""
    suffix = path.suffix.lower()
    if suffix in (".xlsx", ".xls"):
        # Probar varias filas de header
        for skip in range(0, 16):
            try:
                df = pd.read_excel(path, skiprows=skip)
                if len(df.columns) >= 3 and any(
                    c.upper().startswith(("A", "F", "Y")) for c in map(str, df.columns[:2])
                ):
                    break
            except Exception:
                continue
        else:
            df = pd.read_excel(path)
    else:
        skip = detect_header_rows(path)
        for sep in [",", ";", "\t", r"\s+"]:
            try:
                df = pd.read_csv(path, skiprows=skip, sep=sep,
                                 encoding="latin-1", engine="python",
                                 on_bad_lines="skip")
                if len(df.columns) >= 3:
                    break
            except Exception:
                continue
        else:
            raise ValueError(f"No pude parsear {path.name}")

    # Normalizar columnas
    df.columns = [str(c).strip().upper() for c in df.columns]
    print(f"    columnas: {list(df.columns)[:6]}…")

    # Detectar fecha (AÑO/MES/DIA o FECHA o YEAR/MONTH/DAY)
    if {"AÑO", "MES", "DIA"}.issubset(df.columns) or {"ANO", "MES", "DIA"}.issubset(df.columns):
        y = df.get("AÑO", df.get("ANO"))
        m = df["MES"]
        d = df["DIA"]
        df["fecha"] = pd.to_datetime(
            dict(year=pd.to_numeric(y, errors="coerce"),
                 month=pd.to_numeric(m, errors="coerce"),
                 day=pd.to_numeric(d, errors="coerce")),
            errors="coerce")
    elif "FECHA" in df.columns:
        df["fecha"] = pd.to_datetime(df["FECHA"], errors="coerce", dayfirst=True)
    elif {"YEAR", "MONTH", "DAY"}.issubset(df.columns):
        df["fecha"] = pd.to_datetime(
            dict(year=df["YEAR"], month=df["MONTH"], day=df["DAY"]),
            errors="coerce")
    else:
        raise ValueError(f"No identifico columna fecha en {path.name}")

    # Detectar columna de valor (último numérico)
    valor_cols = [c for c in df.columns
                  if c not in ("AÑO", "ANO", "MES", "DIA", "FECHA", "YEAR", "MONTH", "DAY", "fecha")
                  and not c.startswith("CALIDAD")]
    if not valor_cols:
        raise ValueError(f"No identifico columna de valor en {path.name}")
    valor = pd.to_numeric(df[valor_cols[0]], errors="coerce")

    out = pd.DataFrame({"fecha": df["fecha"], "valor": valor}).dropna(subset=["fecha"])
    return out.set_index("fecha").sort_index()


def main() -> None:
    if not SRC.exists():
        print(f"No existe {SRC}. Cree la carpeta y coloque los archivos descargados del portal DGA.")
        return

    archivos = list(SRC.glob("*.xlsx")) + list(SRC.glob("*.csv")) + list(SRC.glob("*.xls"))
    if not archivos:
        print(f"No hay archivos en {SRC}.")
        print(f"Esperados (cualquier nombre que contenga estas claves):")
        for k in ARCHIVOS:
            print(f"  - {k}*.xlsx|csv")
        return

    series = {"nivel": {}, "caudal": {}, "precip": {}}
    for f in archivos:
        name_lower = f.stem.lower()
        match = next((k for k in ARCHIVOS if k in name_lower), None)
        if not match:
            print(f"[!] {f.name}: no reconocido, saltando")
            continue
        variable, estacion = ARCHIVOS[match]
        print(f"  {f.name} → {variable} / {estacion}")
        try:
            df = leer_archivo(f)
            series[variable][estacion] = df["valor"]
            print(f"    {len(df)} días, {df.index.min().date()}..{df.index.max().date()}")
        except Exception as e:
            print(f"    ERROR: {e}")

    OUT.mkdir(exist_ok=True)
    mapping = {"nivel": "niveles_lagos_diarios.csv",
               "caudal": "caudales_dga_diarios.csv",
               "precip": "precipitacion_dga_diaria.csv"}
    for var, fname in mapping.items():
        if not series[var]:
            continue
        df = pd.DataFrame(series[var]).sort_index()
        df.to_csv(OUT / fname)
        print(f"\n→ {OUT / fname} ({df.shape})")


if __name__ == "__main__":
    main()

# Descarga manual de niveles del Lago Caburga (DGA)

El portal SNIA/BNA de la DGA no expone API pública. Las series limnimétricas
se descargan interactivamente. Esta guía documenta el procedimiento exacto
para tener un dataset completo y reproducible.

## 1. Acceso al portal

URL: <https://snia.mop.gob.cl/BNAConsultas/reportes>

Si exige login, crear cuenta gratuita (toma 2 minutos).

## 2. Búsqueda

| Campo | Valor |
|---|---|
| Tipo de estación | Limnimétrica |
| Código BNA | `09417001-K` |
| O por nombre | `Lago Caburgua` |
| Cuenca | `Río Toltén` |

## 3. Parámetros y rango

- Variable: **Nivel medio diario (m)**
- Rango: desde `01-01-1985` hasta hoy (la serie operativa empieza ~1985)
- Frecuencia: `diaria`
- Formato: `Excel` o `CSV`

Repetir para:
| Código | Nombre | Variable |
|---|---|---|
| 09417001-K | Lago Caburga | Nivel diario |
| 09417007-9 | Lago Caburga | Precipitación diaria |
| 09420009-1 | Lago Villarrica | Nivel diario |
| 09416006-5 | Lago Tinquilco | Nivel diario |

## 4. Guardar en el repo

Mover los archivos a:
```
data/raw/dga/lago_caburgua_nivel_diario.csv
data/raw/dga/lago_villarrica_nivel_diario.csv
data/raw/dga/lago_tinquilco_nivel_diario.csv
```

(Esa carpeta está en `.gitignore` por privacidad de origen — los datos son
públicos pero se prefiere recrearlos por script para garantizar trazabilidad.)

## 5. Procesamiento

Crear `scripts/extract_dga_niveles.py` que:
1. Lee los CSV crudos del portal (formato suele tener header de 5-10 líneas)
2. Estandariza fecha, variable, valor, calidad
3. Genera `data/processed/niveles_lagos_diarios.csv` con columnas
   `(fecha, lago_caburgua_m, lago_villarrica_m, lago_tinquilco_m)`

## 6. Datos ya conocidos (mientras tanto)

Cifras extraídas del informe U. Austral 2021 (Fig. 11) que sirven como
ground truth mientras no tengamos la serie diaria completa:

| Periodo | H promedio (m) | H máx (m) | H mín (m) |
|---|---|---|---|
| 2000-2010 | 9.6 | 12.2 | 6.9 |
| 2011-2020 | 7.1 | 9.2 | 5.0 |

Tendencia anual reportada (regresión lineal):
- Lago Caburga: **-0.234 m/año** (2000-2021)
- Lago Villarrica: -0.036 m/año
- Lago Neltume: -0.042 m/año

El descenso de Caburga es **~6× mayor** que el de los lagos vecinos, lo que
es la mejor evidencia indirecta de que algo más que el clima regional
opera en este caso (aunque no permite cuantificar la atribución).

## 7. Por qué no se puede automatizar

- El portal usa formularios JSP con sesión PHP que no expone endpoints REST
- El sistema de Reportes envía el archivo por email tras un job batch
- Se intentó scraping con `requests` y `selenium`; está protegido contra
  automatización (CAPTCHA al volumen)
- Existe el [Observatorio Georreferenciado](https://snia.mop.gob.cl/observatorio/)
  como visor pero tampoco descarga programática

Solicitud formal alternativa: vía Ley de Transparencia (`portaltransparencia.cl`)
indicando RUT del solicitante y entidad solicitada (DGA). Plazo legal 20 días
hábiles, los datos llegan por email.

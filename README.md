# Lago Caburga — estudio abierto

Estudio abierto y reproducible sobre el descenso del **Lago Caburga** (Pucón, Región de La Araucanía, Chile) y la polémica del desvío del río **Trafampulli**.

El objetivo es ofrecer evidencia abierta que permita a la ciudadanía, autoridades y científicos evaluar el problema sobre un terreno común de datos, evitando la dicotomía mediática y aportando un camino concreto de solución.

## 🌐 Sitio web

**https://mendozavolcanic.github.io/lago-caburga/**

| Página | Qué es |
|---|---|
| [`index.html`](docs/index.html) | Portada con resumen, cronología y galería |
| [`story.html`](docs/story.html) · [`story_en.html`](docs/story_en.html) | El estudio completo en 5 secciones (ES / EN) |
| [`solucion.html`](docs/solucion.html) | Propuesta de gobernanza estilo Mono Lake |
| [`recorrido.html`](docs/recorrido.html) | Recorrido scrollytelling 3D sobre el terreno |
| [`nivel3d.html`](docs/nivel3d.html) | Animación 3D del nivel del agua 2000–2025 |
| [`terrain.html`](docs/terrain.html) | Mapa 3D libre con capas y tour de cámara |
| [`explorador.html`](docs/explorador.html) | Gráficos interactivos (timeline ENSO, doble masa, scatter) |
| [`comparador.html`](docs/comparador.html) | Swipe satelital Sentinel-2 entre años |
| [`Estudio_Lago_Caburga.pdf`](docs/Estudio_Lago_Caburga.pdf) | PDF ejecutivo para autoridades/comunidad |

## Conclusión técnica

La causa de **primer orden es la megasequía** 2010–presente (la lluvia en la estación del lago cayó −34%, la nieve de la cuenca de 56% a 27%); el cierre del Trafampulli es un **factor agravante secundario** (~20%, entre 0,3 y 2 m³/s según fuente). Prueba clave: con El Niño 2024 el lago recuperó +350 m de costa sin remover el dique. Las narrativas "es solo el clima" y "es solo el dique" son ambas simplificaciones. Detalle en [HALLAZGOS.md](HALLAZGOS.md), [HISTORIA_TRAFAMPULLI.md](HISTORIA_TRAFAMPULLI.md) y [CASOS_ANALOGOS.md](CASOS_ANALOGOS.md).

## Estructura

```
.
├── docs/                       SITIO WEB (GitHub Pages)
│   ├── *.html                  páginas del estudio y visualizaciones
│   ├── assets/                 figuras, GIF/MP4, PDF
│   ├── data/                   GeoJSON + series.json para los gráficos
│   ├── footage/                imágenes (CC) optimizadas
│   └── estudios/ dga/ prensa/  PDFs fuente (no versionados; ver scripts/)
├── data/
│   ├── raw/                    descargas crudas (no versionadas)
│   └── processed/              CSVs limpios y consolidados
├── notebooks/                  10 análisis .py + figs/
├── dashboard/app.py            dashboard Streamlit (6 tabs)
└── scripts/                    descarga, extracción y generación
```

## Documentos de referencia

- [HALLAZGOS.md](HALLAZGOS.md) — síntesis ejecutiva de los 3 estudios
- [HISTORIA_TRAFAMPULLI.md](HISTORIA_TRAFAMPULLI.md) — cronología completa del conflicto
- [CASOS_ANALOGOS.md](CASOS_ANALOGOS.md) — Mono Lake, Aculeo, Urmia, Aral, Poopó y sus lecciones
- [FUENTES_DATOS.md](FUENTES_DATOS.md) — ecosistema chileno de datos hídricos
- [STORYBOARD.md](STORYBOARD.md) · [FOOTAGE.md](FOOTAGE.md) — producción audiovisual
- [docs/DESCARGA_DGA_NIVEL.md](docs/DESCARGA_DGA_NIVEL.md) — guía para bajar series DGA

## Análisis (notebooks/)

| # | Notebook | Tema |
|---|---|---|
| 01 | correlacion_precipitacion_nivel | series base precip/caudal/nivel |
| 02 | doble_acumulada | doble masa + anomalías post-2010 |
| 03 | balance_hidrico | balance simplificado, 4 escenarios |
| 04 | mapa | mapa folium de estaciones |
| 05 | nivel_sintetico | serie proxy de nivel + correlación P–H |
| 06 | balance_camels | validación cruzada CR2 vs CAMELS-CL |
| 07 | balance_2025 | balance extendido 1990–2025 (Open-Meteo) |
| 08 | tests_estadisticos | Mann-Kendall + Pettitt |
| 09 | hipsometria | curva área–cota + área satelital |
| 10 | balance_mensual | estacionalidad nival (máx primavera) |

## Datos clave (códigos DGA / BNA)

| Código | Estación | Tipo |
|---|---|---|
| `09417001-K` | Lago Caburga | Limnimétrica + pluviométrica |
| `09417002-8` | Ojos del Caburga | Manantial |
| `09416001-4` | Río Liucura en Liucura | Fluviométrica |
| `09416002-2` | Lago Tinquilco | Limnimétrica + pluviométrica |
| `09418001-5` | Río Pucón en Balseadero Quelhue | Fluviométrica |
| `09420009-1` | Lago Villarrica | Limnimétrica |
| `09420001`   | Río Toltén en Villarrica | Fluviométrica |

**Datos faltantes críticos** (para calibración futura): nivel limnimétrico del lago (DGA, descarga manual), caudal histórico del Río Blanco y del Trafampulli al punto de cierre, limnimetría del Lago Colico, caudal de los Ojos del Caburga, batimetría reciente.

## Fuentes de datos usadas

- **CR2** (estaciones + CAMELS-CL): precipitación y caudales 1900–2020
- **Open-Meteo ERA5**: precipitación/temp/nieve 1950–2025 (cubre años recientes)
- **Copernicus GLO-30**: DEM para terreno 3D e hipsometría
- **Sentinel-2** (vía STAC AWS + EOX cloudless): imágenes y NDWI
- **U. Austral 2021** y **U. de Chile 2022**: cifras de los informes

## Cómo reproducir

```bash
pip install -r requirements.txt

# Documentos y datos crudos
bash scripts/download_docs.sh         # PDFs de los estudios
bash scripts/download_cr2.sh          # ~30 MB de datos CR2
python scripts/extract_cr2_stations.py
python scripts/extract_cr2_caudales.py
python scripts/extract_camels.py
python scripts/fetch_openmeteo.py     # 1950–2025 (sin API key)

# DEM Copernicus GLO-30 (keyless, AWS) para terreno e hipsometría
mkdir -p data/raw/dem && cd data/raw/dem
curl -L -o cop30_S39_W072.tif https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_S39_00_W072_00_DEM/Copernicus_DSM_COG_10_S39_00_W072_00_DEM.tif
curl -L -o cop30_S40_W072.tif https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_S40_00_W072_00_DEM/Copernicus_DSM_COG_10_S40_00_W072_00_DEM.tif
cd ../../..

# Análisis y figuras
python notebooks/02_doble_acumulada.py
python notebooks/07_balance_2025.py
python notebooks/08_tests_estadisticos.py
python notebooks/10_balance_mensual.py
python scripts/export_chart_data.py   # genera docs/data/series.json
python scripts/generate_assets.py     # figuras del sitio
python scripts/make_pdf.py            # PDF ejecutivo

# Apps
streamlit run dashboard/app.py        # dashboard
# el sitio: abrir docs/index.html o servir docs/ con un http server
```

## Estado

- [x] Investigación, datos (CR2, Open-Meteo, CAMELS-CL, Sentinel-2, DEM)
- [x] 10 notebooks de análisis + tests estadísticos formales
- [x] Sitio web: estudio (ES/EN), propuesta, 3 mapas 3D, explorador, comparador
- [x] PDF ejecutivo, video, dashboard
- [ ] **Pendiente**: serie diaria de nivel del lago (DGA, descarga manual) para
      calibrar la hipsometría y robustecer la doble masa

## Licencia

Datos y análisis bajo **CC BY 4.0**. Imágenes Wikimedia Commons bajo sus licencias CC BY-SA. Documentos originales conservan su licencia de origen.

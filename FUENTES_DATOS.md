# Ecosistema chileno de datos hidrometeorológicos

Inventario de fuentes públicas, con URL directos cuando existen, y observaciones
sobre dificultad de acceso programático. Ordenado de más útil a más limitado
para nuestro caso.

## 0. Open-Meteo (ERA5) ✅ USADO — el mejor para datos recientes

URL: <https://open-meteo.com/en/docs/historical-weather-api>

**La mejor fuente para cobertura hasta HOY.** CR2 termina en 2020; Open-Meteo
llega al presente. Reanálisis ERA5 (~25 km) desde 1940, ERA5-Land (~9 km) desde
1950. **Sin API key, CC BY 4.0, descarga programática directa.**

Endpoint archivo: `https://archive-api.open-meteo.com/v1/archive`
Ejemplo Caburga:
```
https://archive-api.open-meteo.com/v1/archive?latitude=-39.20&longitude=-71.81
  &start_date=1950-01-01&end_date=2025-12-31
  &daily=precipitation_sum,temperature_2m_mean,snowfall_sum
  &timezone=America/Santiago
```

Variables útiles: `precipitation_sum`, `temperature_2m_mean`, `snowfall_sum`,
`et0_fao_evapotranspiration`, `soil_moisture_*`.

**Limitación importante:** ERA5 a 25 km **suaviza** la precipitación en montaña.
Para Caburga muestra -7% post-2010, mientras la estación CR2 (medición directa)
muestra -34%. Para magnitudes precisas en terreno montañoso, preferir estación;
Open-Meteo es ideal para tendencia general y años recientes (2021-2025).

Script: `scripts/fetch_openmeteo.py` → `data/processed/openmeteo_*.csv`

---

## 1. CR2 — Centro de Ciencia del Clima y la Resiliencia ✅ USADO

URL: <https://www.cr2.cl/>

Es la fuente más práctica y abierta. Compilan, integran y publican datos
de DGA + DMC + DGAC + estaciones automáticas, con control de calidad.

| Producto | URL directo | Periodo | Formato |
|---|---|---|---|
| Precipitación diaria nacional | <https://www.cr2.cl/download/cr2-prdaily-2019-zip/?wpdmdl=25581> | 1900-2019 | CSV (zip) |
| Caudales diarios nacional | <https://www.cr2.cl/download/cr2-qflxdaily-2019-zip/?wpdmdl=25589> | 1929-2019 | CSV (zip) |
| Caudales mensuales | <https://www.cr2.cl/download/cr2_qflxamon_2018-zip/?wpdmdl=15415> | 1929-2018 | CSV (zip) |
| CR2MET grillado | <https://doi.org/10.5281/zenodo.7529681> | 1960-2021 | NetCDF |
| CAMELS-CL (cuencas) | <https://doi.pangaea.de/10.1594/PANGAEA.894885> | 1979-2018 | TXT |
| Explorador cuencas | <https://camels.cr2.cl/> | — | UI |
| GitHub | <https://github.com/calvarezgarreton/camels-cl> | — | scripts |

**Limitación:** la serie diaria nacional se actualiza cada ~3-5 años; la última
disponible es a marzo 2020. Para datos posteriores hay que ir al portal DGA.

## 2. DGA — Dirección General de Aguas

URL principal: <https://dga.mop.gob.cl/>

### 2.1 BNAConsultas (Banco Nacional de Aguas) ⚠ INTERACTIVO

URL: <https://snia.mop.gob.cl/BNAConsultas/reportes>

Tiene **TODAS** las series oficiales: nivel limnimétrico, caudal, precipitación,
calidad de agua, evaporación, temperatura. Resolución diaria. Actualizado al mes.

**Cómo usar:**
1. Tipo de estación → seleccionar (Limnimétrica / Fluviométrica / etc.)
2. Cuenca → `Río Toltén` (para nuestro caso)
3. Código → `09417001-K` (Lago Caburga)
4. Variable → Nivel medio diario
5. Periodo → desde `1985-01-01`
6. Formato → CSV o Excel
7. El sistema envía un archivo por email tras unos minutos

**No hay API pública**. Se intentó scraping con requests/selenium; protegido.

### 2.2 Repositorio digital DGA

URL: <https://snia.mop.gob.cl/repositoriodga/>
URL alterna: <https://repositoriodirplan.mop.gob.cl/biblioteca/>

Estudios técnicos como PDF. Aquí están:
- `Análisis de Potenciales Causas del Descenso del Lago Caburgua` (U. Chile 2022) — descargado
- `Estudio Hidráulico y Modelación Río Trafampulli` (handle 126134, fallido el día de la consulta)
- Balance Hídrico DGA 2017 — descargado
- Reporte Red de Control de Lagos DGA 2017 — descargado

### 2.3 Otros endpoints DGA

| Servicio | URL |
|---|---|
| Sistema Hidrométrico en Línea | <https://dga.mop.gob.cl/sistema-hidrometrico-en-linea/> |
| Estadísticas estaciones | <https://dga.mop.gob.cl/estadisticas-estaciones-dga/> |
| Estaciones fluviométricas (lista) | <https://snia.mop.gob.cl/dgasat/> |
| Observatorio georreferenciado | <https://snia.mop.gob.cl/observatorio/> |
| Mapas DGA | <https://mapas2.mop.gob.cl/> |
| ArcGIS REST (derechos) | <https://rest-sit.mop.gov.cl/arcgis/rest/services/SNIA/SNIA_DerechoAprovechamiento/MapServer> |
| CPA (calidad agua) | <https://snia.mop.gob.cl/CPAConsultas/> |
| Solicitud por Ley de Transparencia | <https://www.portaltransparencia.cl/> |

## 3. DMC — Dirección Meteorológica de Chile

URL: <https://climatologia.meteochile.gob.cl/>

524 estaciones meteorológicas desde 1922. Web Services con formato JSON-GeoJSON.
El acceso a series históricas requiere formulario.

| Servicio | URL |
|---|---|
| Portal Servicios Climáticos | <https://climatologia.meteochile.gob.cl/> |
| Estaciones Automáticas | <https://climatologia.meteochile.gob.cl/application/index/menuTematicoEmas> |
| Datos históricos (form) | <https://climatologia.meteochile.gob.cl/application/requerimiento/producto/RE3017> |
| GeoNode | <http://geonode.meteochile.gob.cl/> |
| Catálogo por elemento | <https://climatologia.meteochile.gob.cl/application/informacion/CatalogoInversoDeElemento/60> |

## 4. Plataforma de Datos del Estado de Chile

URL: <https://www.plataformadedatos.cl/>

Iniciativa de datos abiertos. Indexa datasets de varios servicios.

| Dataset | ID | URL |
|---|---|---|
| DMC precipitación 24h | `6d7ba7c949f9ea5d` | <https://www.plataformadedatos.cl/datasets/es/6d7ba7c949f9ea5d> |
| DMC precipitación 6h | `b22f448493fff975` | <https://www.plataformadedatos.cl/datasets/es/b22f448493fff975> |
| MMA estaciones meteo (hora) | `J4KRX6T12U50WZ7C` | <https://www.plataformadedatos.cl/datasets/es/J4KRX6T12U50WZ7C> |
| Red meteo DMC | `8dc61a6825d657a6` | <https://www.plataformadedatos.cl/datasets/es/8dc61a6825d657a6> |

**Acceso programático:** paquete `pytrend` (no el de Google Trends — el de iTrend
Chile). Identificador: `itrend-ds:6d7ba7c949f9ea5d`. Los archivos requieren
sesión web; no hay descarga curl directa.

## 5. Monitoreo ciudadano

| Plataforma | URL | Cobertura |
|---|---|---|
| Vigilantes Lagos (app) | <https://app.vigilanteslagos.org/> | Caburga, Villarrica, otros |
| Caburga Sustentable | <https://caburguasustentable.cl/> | Caburga específico |
| Sustenta Pucón | <https://www.sustentapucon.cl/> | Cuenca Toltén |

Los datos de Vigilantes Lagos son crowdsourced, valiosos para validación
cualitativa pero sin metadatos formales.

## 6. Geodatos / GIS

| Plataforma | URL |
|---|---|
| IDE Chile | <https://www.ide.cl/> |
| MMA Líneas de Base | <https://lineasdebasepublicas.mma.gob.cl/> |
| SERNAGEOMIN | <https://www.sernageomin.cl/> |
| CIREN | <https://bibliotecadigital.ciren.cl/> |
| SHOA (Armada) | <https://www.shoa.cl/> |

## 7. Datos académicos

| Recurso | Notas |
|---|---|
| Repositorio U. Chile | <https://repositorio.uchile.cl/> — tesis y memorias |
| Repositorio UC | <https://repositorio.uc.cl/> |
| SciELO Chile | <https://www.scielo.cl/> |
| Biodiversity Heritage Library | <https://www.biodiversitylibrary.org/> — Campos 1987 (Gayana Botánica) |

## 8. Para el caso Caburga específicamente

### Series ya descargadas (en repo)

- ✅ Precipitación diaria 1965-2019, 8 estaciones (CR2)
- ✅ Caudal diario 1929-2019, 5 ríos vecinos (CR2)

### Pendientes

- ⚠ Nivel limnimétrico Lago Caburga (BNA `09417001-K`) — descarga manual del portal DGA
- ⚠ Nivel limnimétrico Lago Villarrica (`09420009-1`) — ídem
- ⚠ Nivel limnimétrico Lago Tinquilco (`09416006-5`) — ídem
- ⚠ Caudal Río Trafampulli en Rinconada — datos parciales 2016-2020 disponibles en CR2
- ⚠ Caudal Río Blanco en Caburga — estación recién instalada nov 2021
- ❌ Caudal Ojos del Caburga / Río Caburga aguas abajo — sin estación
- ❌ Limnimetría Lago Colico — sin estación
- ❌ Batimetría reciente del lago — última publicada por Campos 1987

### Batimetría

- **Campos, H. (1984/1987)** "Limnological studies in Lake Caburgua, Chile",
  *Gayana Botánica*. Profundidad máxima reportada: **327 m** (2do más profundo
  de los lagos araucanos). Disponible en Biodiversity Heritage Library:
  <https://www.biodiversitylibrary.org/part/98667>
- **Estudios limnológicos de los lagos Caburgua y Maihue** —
  <https://snia.mop.gob.cl/sad/LGO589.pdf> (nuestro fetch retornó 199 bytes,
  probablemente requiere user-agent o sesión específica)
- **No existe batimetría reciente publicada** del lago. El estudio U. Chile
  2022 lo identifica explícitamente como un dato faltante crítico y
  recomienda hacer una nueva.
- Para una batimetría nueva: empresas chilenas como Cyanowater
  (<https://cyanowater.com/batimetrias/>) hacen levantamientos con multibeam.

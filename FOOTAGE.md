# Footage del Lago Caburga — banco de fuentes visuales

Inventario de imágenes y videos disponibles para mostrar la baja del nivel del
lago. Pensado para ser consumido luego con Claude Design / Remotion para
animaciones comparativas y storytelling.

Marcado por **utilidad**:
- 🔥 imprescindible (bajado al repo)
- ⭐ alto valor (URL conocida, descargable)
- 💡 útil contextual

---

## 1. Videos YouTube — reportajes y drones

Bajamos los thumbnails en `docs/footage/thumbs/` (todas Public via YouTube oembed).

| ID | Título | Canal | Duración | Views | Uso |
|---|---|---|---|---|---|
| 🔥 [`MX8IYQ9NBdc`](https://www.youtube.com/watch?v=MX8IYQ9NBdc) | El misterio de la sequía en el lago Caburga | Teletrece | 3:15 | 100k | reportaje principal |
| 🔥 [`z71NzEVbgvs`](https://www.youtube.com/watch?v=z71NzEVbgvs) | Bajo nivel de agua en el Lago Caburgua | Meganoticias | 2:35 | 9k | sequía nota corta |
| 🔥 [`jkt4vOB2RQQ`](https://www.youtube.com/watch?v=jkt4vOB2RQQ) | Las causas del bajo nivel de agua en el Lago Caburgua | CHV Noticias | 9:23 | 12k | causas explicadas |
| ⭐ [`4eIuEYIJJJo`](https://www.youtube.com/watch?v=4eIuEYIJJJo) | Municipio de Pucón busca destruir dique | UATV | 3:39 | 32k | conflicto político |
| ⭐ [`Tb4DQWnMvYo`](https://www.youtube.com/watch?v=Tb4DQWnMvYo) | Lago Caburgua recupera su nivel normal | Pucón TV | 1:37 | 2.4k | recuperación 2024 |
| ⭐ [`Pmu10z0faBc`](https://www.youtube.com/watch?v=Pmu10z0faBc) | Preocupación por disminución (Araucanía 360°) | UfroMedios | 19:09 | 1.7k | reportaje extenso |
| ⭐ [`ny-I43zUu4k`](https://www.youtube.com/watch?v=ny-I43zUu4k) | Nivel del lago aumentó (Araucanía 360°) | UfroMedios | 14:07 | 2.5k | recuperación 2024 |
| 💡 [`Wnh-NTpwZfk`](https://www.youtube.com/watch?v=Wnh-NTpwZfk) | Playa Blanca Verano 2023 vista drone 4K | Drone Temuco | — | — | imágenes aéreas estado normal |
| 💡 [`Bp9IWLTIlsU`](https://www.youtube.com/watch?v=Bp9IWLTIlsU) | Pucón Playa Blanca 4K drone | Drone Temuco | — | — | imágenes aéreas |
| 💡 [`HBalz60IDxo`](https://www.youtube.com/watch?v=HBalz60IDxo) | Lago Caburgua Lake Life 2019 | — | — | — | referencia pre-crisis |
| 💡 [`LxCx2w9kibg`](https://www.youtube.com/watch?v=LxCx2w9kibg) | Argentinos en Chile visitan Caburgua | — | — | — | turismo |

**Para descarga real del video**: usar `yt-dlp` (`pip install yt-dlp` luego
`yt-dlp <URL>`). Los reportajes de canales chilenos suelen ser libres de geo-block.

---

## 2. Imágenes Wikimedia Commons (licencia CC)

Categoría completa: <https://commons.wikimedia.org/wiki/Category:Caburgua_Lake>
(32 archivos). Bajadas las 4 con mayor relevancia y resolución a
`docs/footage/wikimedia/`:

| Archivo local | Original Wikimedia | Año | Licencia | Notas |
|---|---|---|---|---|
| 🔥 `lago_caburgua_2022.jpg` (131 KB) | [Lago Caburgua 2022](https://commons.wikimedia.org/wiki/File:Lago_Caburgua_2022.jpg) | 2022 | CC BY-SA 4.0 | **Estado de sequía. La pieza clave.** |
| 🔥 `caburgua_playa_2019_01.jpg` (4.2 MB) | [Caburgua, playa, 2019 (01)](https://commons.wikimedia.org/wiki/File:Caburgua,_playa,_2019_(01).jpg) | 2019 | CC BY-SA 4.0 | Playa pre-crisis (alto valor comparativo) |
| 🔥 `ojos_2019_01.jpg` (7.3 MB) | [Ojos del Caburgua 2019 (01)](https://commons.wikimedia.org/wiki/File:Ojos_del_Caburgua,_2019_(01).jpg) | 2019 | CC BY-SA 4.0 | Drenaje subterráneo en operación |
| 🔥 `atardecer_caburgua.jpg` (2.9 MB) | [Atardecer en Caburgua](https://commons.wikimedia.org/wiki/File:Atardecer_en_Caburgua.JPG) | — | CC BY-SA 3.0 | Estética |

Otras 28 imágenes disponibles vía API en la categoría. Las descargas con menos
de 3 KB en `docs/footage/wikimedia/` fueron 1×1 placeholders y se eliminaron;
se pueden re-bajar con `Special:FilePath/<filename>` o vía la API REST.

---

## 3. Imágenes de prensa

Bajadas a `docs/footage/prensa/`:

| Archivo | Origen | Tema |
|---|---|---|
| 🔥 `laderasur_2021_caburgua.jpg` (110 KB) | [Ladera Sur 2021](https://laderasur.com/articulo/notoria-baja-en-el-nivel-del-agua-del-lago-caburgua-vecinos-exigen-respuestas/) — © Andrés Bravo / Caburgua Sustentable | Vista del lago en sequía |
| 🔥 `terram_2024_recuperacion.jpg` (70 KB) | [Terram 2024](https://www.terram.cl/lago-caburgua-recupera-el-agua-luego-de-15-anos-aumento-mas-de-350-metros/) | Recuperación post El Niño |

Bloqueadas por hotlink (URL conocidas, hay que bajarlas vía navegador):

| URL | Tema |
|---|---|
| <https://www.latercera.com/resizer/v2/7NYZX4MQYFBJBOX6AST2XXNO2A.jpg> | Lago en oct 2024 — Vigilantes del Lago |
| <https://www.latercera.com/resizer/v2/RLFVXSFPJVALVH4RBJAYPBY7KI.jpg> | Lago oct 2024 — Juan Ignacio Barros |
| <https://www.latercera.com/resizer/v2/SQVFT56NEBFZVIN2OXOCKYUJEQ.JPG> | Última crecida domingo |
| <https://www.latercera.com/resizer/v2/4HOSYZ6BBVAL7OPGCNT2BAVPNQ.jpg> | Estado previo a la crecida |
| <https://www.latercera.com/resizer/v2/5ZGZBKUE6RHZZH3BRPAQBQON7I.JPG> | Imagen interior artículo |

> **Cómo bajarlas manualmente:** abrir el [artículo La Tercera](https://www.latercera.com/que-pasa/noticia/lago-caburgua-recupera-el-agua-luego-de-15-anos-aumento-mas-de-350-metros/F7AM5BYFUVFFPIPTLFYGD5DBVU/) en navegador, click derecho → guardar imagen.

### Imágenes Google Earth comparativas (en artículos)

El artículo de [Ladera Sur](https://laderasur.com/articulo/notoria-baja-en-el-nivel-del-agua-del-lago-caburgua-vecinos-exigen-respuestas/) incluye **imágenes Google Earth comparativas 2013 vs 2021** del lago, embebidas como base64 (no extraíbles automáticamente). Se ven al hacer scroll en el artículo. Para captura: screenshot manual.

---

## 4. Instagram

Cuentas y posts relevantes:

| Cuenta / Post | Tipo | Notas |
|---|---|---|
| [@puconchile.travel](https://www.instagram.com/puconchile.travel/) | Oficial Pucón Turismo | Reel "Verano 2025: Lago Caburgua" — DC2GuWxRCvG |
| [@cabanas.las.rosas](https://www.instagram.com/cabanas.las.rosas/) | Playa Blanca Caburgua | Cabañas, tienen archivo histórico |
| [@parqueojosdelcaburgua](https://www.instagram.com/parqueojosdelcaburgua/) | Ojos del Caburga | Drenaje subterráneo |
| [@lakehopecaburgua](https://www.instagram.com/lakehopecaburgua/) | Hostal lago | Fotos diarias |
| [Reel "Después de años de sequía"](https://www.instagram.com/reel/DBO_6ocy5LN/) | MOP Araucanía oct 2024 | Recuperación |
| [Locación Lago Caburga (Pucón)](https://www.instagram.com/explore/locations/260178084/lago-caburga-pucon/) | Geotag | Decenas de posts diarios |
| [Locación Lago Caburgua Pucón](https://www.instagram.com/explore/locations/1028080995/lago-caburgua-pucon/) | Geotag | Geotag alterno |
| [Locación Playa Blanca Caburgua](https://www.instagram.com/explore/locations/429753796/playa-blanca-caburgua/) | Geotag | Específico playa |

> **Hashtags útiles**: `#lagocaburgua` `#caburga` `#caburgua` `#playablanca` `#playanegra` `#pucon`. Para timelapse comparativo: filtrar por fecha.

---

## 5. Imágenes satelitales

### Google Earth Engine Timelapse 🔥

URL directa para el lago:
<https://earthengine.google.com/timelapse#v=-39.20,-71.81,11.5,latLng&t=0.5>

Permite ver la evolución 1984-2022 del lago en navegador. Capturable con
herramientas como ScreenToGif.

### Sentinel Hub / Copernicus Browser ⭐

URL para ROI Caburga, Sentinel-2 desde 2017:
<https://browser.dataspace.copernicus.eu/?zoom=12&lat=-39.20&lng=-71.81&themeId=DEFAULT-THEME>

Descarga: bandas raw (TCI, NDWI, etc.), animación timelapse desde la UI.
Resolución 10 m. Para nuestro caso, **NDWI** (índice de agua) es ideal —
permite ver superficie del lago semana a semana.

### NASA Worldview ⭐

<https://worldview.earthdata.nasa.gov/?v=-72.5,-39.6,-71.0,-38.8&t=2024-01-15-T00%3A00%3A00Z>

MODIS y VIIRS diarios. Buen para anomalías a gran escala (sequía regional).

### Landsat directos (para procesamiento)

USGS EarthExplorer: <https://earthexplorer.usgs.gov/>
Path/Row para Caburga: aproximadamente **path 233 row 088** (Landsat 8/9).

---

## 6. Pipeline propuesto para animaciones

Cuando estemos listos para el lado visual:

1. **Comparativa "antes/después"** (la más impactante):
   - Imagen 2019 alta resolución (Wikimedia) → estado normal
   - Imagen 2022 sequía (Wikimedia) → crisis
   - Imagen oct 2024 (La Tercera/Terram) → recuperación
   - Imagen actual abr 2026 → bajando otra vez (a captar)

2. **Timelapse satelital** generado con Sentinel-2 NDWI:
   - 2017–2026, frame mensual
   - Overlay con anomalía de precipitación CR2

3. **Drone fragmentos**:
   - Reportaje Teletrece [`MX8IYQ9NBdc`] tiene la mejor toma aérea de la sequía
   - Drone Temuco [`Wnh-NTpwZfk` y `Bp9IWLTIlsU`] tienen tomas 4K en estado normal
   - Pedir permiso a los autores antes de redistribuir; alternativa: linkear

4. **Mapa interactivo + transición**:
   - Usar el `notebooks/figs/04_mapa.html` como base
   - Animar el cambio de polígono del lago entre 2019/2022/2024

5. **Storytelling Remotion / Claude Design**:
   - Acto 1: "El lago que se va" — sequía 2017-2022, drone reportaje
   - Acto 2: "El conflicto" — dique, ruptura mayo 2022
   - Acto 3: "La recuperación" — El Niño 2024
   - Acto 4: "Y ahora qué" — Suprema 2025, La Cascada dic 2025
   - Cierre: balance hídrico interactivo del dashboard

---

## 7. Pendientes para el usuario

- [ ] Pedir a [Caburgua Sustentable](https://caburguasustentable.cl/) acceso a su archivo fotográfico (Andrés Bravo)
- [ ] Captura screenshot del Google Earth Timelapse (link arriba)
- [ ] Bajar las imágenes La Tercera vía navegador (5 URLs listadas)
- [ ] Si quieres video real (no solo thumbs): `yt-dlp <URL>` localmente
- [ ] Consultar a [Vigilantes del Lago](https://app.vigilanteslagos.org/) si tienen archivo de fotos georreferenciadas

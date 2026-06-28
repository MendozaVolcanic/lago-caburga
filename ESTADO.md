# ESTADO DEL PROYECTO — Lago Caburga

> Handoff entre sesiones. Última actualización: sesión de auditoría + anatomía + Plotly.
> Repo: https://github.com/MendozaVolcanic/lago-caburga · Sitio: https://mendozavolcanic.github.io/lago-caburga/
> Rama `main` sincronizada con origin. Working tree limpio.

## Qué es el proyecto

Estudio abierto y reproducible sobre el descenso del Lago Caburga (Pucón, Araucanía)
y la polémica del desvío del río Trafampulli. Toma postura basada en evidencia
(**~80% megasequía / ~20% dique**) pero con fin de **destrabar el conflicto**, no
de ganar un bando. Sitio web estático (GitHub Pages) + análisis Python + dashboard.

## Conclusión técnica (consistente en todo el sitio)

Causa de primer orden: **megasequía 2010–presente** (lluvia estación Caburga −34%,
nieve cuenca 56%→27%). Dique Trafampulli: agravante secundario (~20%, 0,3–2 m³/s
según fuente). Prueba clave: recuperó +350 m de costa con El Niño 2024 **sin** tocar
el dique. Tests: Mann-Kendall CR2 significativo (τ=−0.45, p=0.0005).

## Estructura actual

```
docs/                     SITIO WEB (GitHub Pages, /docs, .nojekyll)
  index.html              portada + hub de 11 herramientas
  story.html / story_en.html   estudio 5 secciones (ES/EN, toggle idioma)
  solucion.html           propuesta gobernanza estilo Mono Lake
  anatomia.html           ⭐ corte transversal SVG animado (cómo baja el lago)
  recorrido.html          scrollytelling 3D (Scrollama + MapLibre)
  nivel3d.html            lago 3D fill-extrusion que baja por año
  terrain.html            mapa 3D libre con capas + tour
  explorador.html         gráficos interactivos (Observable Plot + D3)
  comparador.html         swipe satelital Sentinel-2 (maplibre-gl-compare 0.5.0)
  Estudio_Lago_Caburga.pdf  PDF ejecutivo
  SOLICITUD_TRANSPARENCIA_DGA.md  solicitud Ley 20.285 lista para presentar
  DESCARGA_DGA_NIVEL.md   guía descarga manual DGA
  assets/  data/  footage/  estudios/ (PDFs no versionados)
notebooks/  01–10 .py (análisis) + figs/
dashboard/app.py          Streamlit 6 tabs (balance ahora con Plotly)
scripts/                  descarga, extracción, generación (incl. make_pdf, make_video,
                          generate_assets, delineate_watershed, fetch_openmeteo, etc.)
README.md HALLAZGOS.md HISTORIA_TRAFAMPULLI.md CASOS_ANALOGOS.md FUENTES_DATOS.md
STORYBOARD.md FOOTAGE.md LICENSE .gitattributes
```

## Datos disponibles (data/processed/)

- Precipitación diaria CR2 (1965-2019) + CAMELS-CL (6 cuencas) + **Open-Meteo ERA5
  1950-2025** (cubre años recientes, sin API key)
- Caudales diarios CR2 + CAMELS-CL
- Nivel: **solo proxy** (U. Austral cifras por década) — FALTA serie DGA real
- DEM Copernicus GLO-30 en data/raw/dem (no versionado; recrear con curl, ver README)
- Sentinel-2 NDWI: 28 frames + serie de área (ruidosa)

## Auditoría aplicada esta sesión (todo arreglado)

- ✅ index cargaba GIF desde ../notebooks (404 en Pages) → copiado a assets
- ✅ comparador roto: maplibre-gl-compare 0.6.0 (404) → 0.5.0
- ✅ imágenes footage optimizadas 30MB→2MB + lazy loading
- ✅ requirements.txt completado (faltaban 6 deps) + plotly
- ✅ tipografía editorial (Newsreader+Inter+Plex Mono) en las 9 páginas
- ✅ README reescrito, .nojekyll, favicons, LICENSE, .gitattributes
- ✅ verificado: CDNs 200, assets/geojson/fetch existen, sin secretos, 23 .py OK

## Nuevo esta sesión

- ⭐ anatomia.html (corte transversal animado)
- dashboard tab Balance → Plotly interactivo

## Mejoras visuales (sesión actual) — TODAS HECHAS ✅

1. ✅ **nivel3d más pulido** — tween con easing (easeInOutQuad) del bloque de agua,
   anillo de "playa expuesta" (banda tipo bañera entre nivel actual y máximo histórico)
   que crece al bajar, autorotación suave de cámara en play.
2. ✅ **Resto del dashboard a Plotly** — anomalías de precipitación y caudales (tab
   "Datos observados") ahora interactivos. De paso se arregló un bug: `legend` estaba
   en PLOTLY_LAYOUT y al combinarlo con `legend=` explícito reventaba update_layout
   (afectaba también al tab Balance). Dashboard verificado: arranca, HTTP 200, figuras
   serializan contra datos reales.
3. ✅ **Count-up animado** en las 4 cifras del index (IntersectionObserver, parsea
   números dentro de "-25%", "56→27%", "~80/20") + reveal escalonado de la galería.
4. ✅ **Hero con shimmer de agua** sutil (CSS, repeating-linear-gradient animado) en
   index y story. Respeta prefers-reduced-motion.
5. ✅ **Mini-mapa locator** (SVG estilizado de Chile con punto en Caburga 39°S) en
   nivel3d, terrain y recorrido.

## PENDIENTE DE DATOS (bloquea calibración, requiere acción humana)

- **Serie diaria de nivel del lago (DGA, estación 09417001-K)** — descarga manual
  del portal SNIA/BNA o vía Ley de Transparencia (solicitud ya redactada en
  docs/SOLICITUD_TRANSPARENCIA_DGA.md). Al llegar: correr
  `scripts/extract_dga_niveles.py` → calibrar hipsometría (notebook 09) y robustecer
  la doble masa (notebook 02).
- Activar GitHub Pages ya está hecho (status: built).

## Notas técnicas

- pysheds falla para delinear la cuenca (drenaje subterráneo rompe ruteo D8);
  se usa contorno aproximado etiquetado en docs/data/cuenca_caburga.geojson.
- numpy pineado <2.1 (pysheds usa np.in1d, parcheado a np.isin en el script).
- El nivel en nivel3d.html y anatomia.html es proxy/ilustrativo (etiquetado).

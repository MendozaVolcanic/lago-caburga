# Storyboard — animación didáctica del Lago Caburga

Documento estructurado para producción de animaciones con
[Claude Design](https://claude.com/design) o [Remotion](https://www.remotion.dev/).

Cada escena especifica: duración, narración, visual, datos a mostrar y
fuentes de footage disponibles en `docs/footage/`.

**Audiencia**: ciudadanía general, vecinos de Pucón, autoridades locales.
**Duración total objetivo**: 4-5 minutos.
**Tono**: divulgativo, honesto sobre la incertidumbre, no toma partido entre
"es el clima" y "es el dique" — muestra que ambos relatos contienen verdad.

---

## Acto 1 — "Un lago que se va" (60s)

### 1.1 Apertura aérea ✨ (8s)
- **Visual**: Drone cenital sobre el Lago Caburga al atardecer, condiciones
  normales, agua hasta la orilla
- **Footage sugerido**: `docs/footage/wikimedia/atardecer_caburgua.jpg` (CC BY-SA 3.0)
  o frame del drone Temuco YouTube `Bp9IWLTIlsU`
- **Narración**: *"En la cordillera de la Araucanía, a 23 km de Pucón, hay un
  lago único en Chile. Tiene 327 metros de profundidad — el segundo más
  profundo de los lagos araucanos — y a diferencia de todos los demás, sus
  aguas no salen por un río. Drenan bajo tierra, a través de los Ojos del
  Caburga."*

### 1.2 Los Ojos del Caburga (10s)
- **Visual**: Toma de las cascadas subterráneas
- **Footage**: `docs/footage/wikimedia/ojos_2019_01.jpg` (7 MB, CC BY-SA 4.0)
- **Narración**: *"Es como una bañera con el tapón abajo. Si entra menos de
  lo que sale, el lago se vacía hacia adentro de la tierra."*

### 1.3 La crisis (15s)
- **Visual**: Comparación lado a lado:
  - 2019 (lago lleno) → `caburgua_playa_2019_01.jpg`
  - 2022 (lago seco) → `lago_caburgua_2022.jpg`
  - 2024 (recuperación) → `terram_2024_recuperacion.jpg`
- **Datos sobreimpresos**: -25% nivel promedio entre 2000-2010 y 2011-2020
- **Narración**: *"Entre 2010 y 2022, el agua bajó tanto que aparecieron 300
  metros de playa donde antes había un metro. Una caída sin precedentes en el
  registro instrumental moderno."*

### 1.4 Los datos (15s)
- **Visual**: Gráfico animado de precipitación anual cuenca, 1965-2019
  (notebook 02, fig `02_anomalias_precipitacion.png`)
- **Acompañamiento**: barras rojas para años secos, azules para húmedos
- **Datos**: estación Lago Caburga -34% post-2010 (CR2)
- **Narración**: *"Y no es solo el lago. La cuenca completa perdió un tercio
  de su lluvia. Los datos del Centro de Ciencia del Clima muestran una
  megasequía sin precedentes en mil años, según los anillos de los árboles."*

### 1.5 Bisagra (10s)
- **Visual**: Mapa de la cuenca con el dique destacado
- **Footage**: usar `notebooks/figs/04_mapa.html` o screenshot
- **Narración**: *"Pero los vecinos no creen que sea solo el clima. Apuntan a
  un dique. Construido en 2007 por orden de la Dirección General de Aguas. Un
  dique que cierra un brazo del río Trafampulli que durante años llegó al
  lago."*

---

## Acto 2 — "El dique" (75s)

### 2.1 Cómo era antes (12s)
- **Visual**: Foto histórica del brazo del Trafampulli con cascada
- **Footage**: foto Rosa Zúñiga Novoa años 80 (en informe U. Austral PDF p.9)
  o aerofotografía SAF 1979 (en informe U. Chile)
- **Datos**: registro continuo SAF 1943, 1961, 1979, 1994, 1998, 2007
  → cauce visible
- **Narración**: *"Hasta 2007, así se veía. Una cascada caía sobre el lago.
  Familias del lugar dicen que existió 'desde tiempos inmemoriales'."*

### 2.2 El conflicto privado (15s)
- **Visual**: Animación esquemática mostrando los dos cauces del Trafampulli
  (al Caburga y al Colico)
- **Datos**: 2005 — vecinos del Colico denuncian al señor Marcelo Benito
- **Narración**: *"En 2005, vecinos del Lago Colico denunciaron al dueño de
  un fundo: decían que él había desviado el río al Caburga. La DGA le ordenó
  construir un dique para 'restaurar el cauce natural'. Sin estudio de
  impacto ambiental."*

### 2.3 El dique en operación (15s)
- **Visual**: Foto aérea actual del dique
- **Footage**: imágenes de la Contraloría 2024 (`docs/estudios/contraloria_trafampulli_2024.pdf`,
  páginas con anexo fotográfico)
- **Datos**: 0 m³/s al Caburga desde 2009; sin dique, el lago habría recibido
  entre 0,3 m³/s (estimación U. Chile) y 2 m³/s (estimación U. Austral)
- **Narración**: *"Desde 2009 el dique funcionó. El brazo se secó. Y el lago,
  ya golpeado por la sequía, empezó a vaciarse aún más rápido."*

### 2.4 La acción directa (18s)
- **Visual**: Toma del dique destruido (2022)
- **Footage**: tomas YouTube `4eIuEYIJJJo` (UATV sobre la destrucción)
- **Datos animados**:
  - 16 mayo 2022
  - 4 días de trabajo manual
  - Comunidad mapuche del sector
  - Justificación: 16 años de peticiones a la DGA
- **Narración**: *"En mayo de 2022, después de dieciséis años de cartas y
  peticiones que no habían cambiado nada, una comunidad mapuche del sector
  decidió actuar. Cuatro días de trabajo, con palas y manos, y el dique cayó.
  El agua del Trafampulli volvió al lago."*

### 2.5 La respuesta institucional (15s)
- **Visual**: Línea de tiempo sobreimpuesta
- **Datos**:
  - ene 2023 — DGA ordena reconstruir
  - mar 2024 — Contraloría observa
  - mar 2025 — Apelaciones Temuco da orden de no innovar
  - ago 2025 — Corte Suprema revoca, autoriza dique
  - nov 2025 — DGA mide 4% del cauce llega al lago
- **Narración**: *"La DGA ordenó reconstruirlo. La municipalidad lo demandó.
  La Apelaciones detuvo las obras. La Corte Suprema autorizó la reconstrucción.
  Y hoy, en 2026, el conflicto sigue abierto."*

---

## Acto 3 — "¿Qué dicen los datos?" (90s)

### 3.1 Dos estudios, dos relatos (12s)
- **Visual**: Caja con los dos estudios:
  - U. Austral 2021: 1-2 m³/s histórico, dique exacerba
  - U. de Chile 2022: 0,3 m³/s histórico, dique marginal
- **Narración**: *"Dos universidades estudiaron el problema con datos.
  Llegaron a estimaciones distintas de cuánta agua llegaba antes al lago. Pero
  ambas coincidieron en algo: la sequía es el factor principal."*

### 3.2 La precipitación (18s)
- **Visual**: Gráfico animado por estación (notebook 02 fig
  `02_precip_anual_completa.png`), señalando que el Lago Caburga (la cuenca
  alta) cayó -34%, mientras Pucón (la zona baja) solo -11%
- **Datos**:
  - Lago Caburga -34%
  - Lago Tinquilco -22%
  - Curarrehue -9%
  - Pucón -11%
- **Narración**: *"Y la sequía golpeó más fuerte arriba en la cordillera, donde
  está el lago, que abajo. La estación del propio lago perdió un tercio de su
  lluvia."*

### 3.3 La nieve (10s)
- **Visual**: Animación de la cuenca con cobertura de nieve
- **Datos**: 56% promedio 2001-2011 → 27% promedio 2012-2021
- **Narración**: *"Y la nieve, que es el otro gran aporte del lago en
  primavera, cayó casi a la mitad."*

### 3.4 El balance hídrico (20s)
- **Visual**: Sliders del dashboard moviéndose
- **Footage**: capturar pantalla del `dashboard/app.py`
- **Datos animados — escenarios contrafactuales**:
  - Si la lluvia no hubiera bajado: +2 m de lago
  - Si el dique no se hubiera construido: +0,5 m
  - Atribución resultante: ~80% clima, ~20% dique
- **Narración**: *"Cuando combinamos los datos en un modelo simple, los
  números cuentan una historia incómoda para los dos relatos: ni 'es solo el
  clima' ni 'es solo el dique'. Es ambos. Pero no en partes iguales."*

### 3.5 La recuperación (15s)
- **Visual**: Comparación oct 2024 lago lleno vs sequía 2022
- **Footage**: `terram_2024_recuperacion.jpg`, tomas YouTube `Tb4DQWnMvYo`
- **Datos**: +350 m lineales de costa recuperados, octubre 2024
- **Narración**: *"En 2024, llegó El Niño. Las lluvias volvieron y el lago
  recuperó 350 metros de costa. Sin remover el dique. Eso es la mejor
  evidencia de que el clima es el factor dominante."*

### 3.6 La nueva amenaza (15s)
- **Visual**: Mapa con La Cascada destacado, fechas dic 2025
- **Datos**:
  - DGA: 4% del Estero La Cascada llega al lago (medición 11 puntos)
  - Gobernador Saffirio: oposición pública
- **Narración**: *"Y ahora, en diciembre de 2025, la DGA volvió a anunciar
  que cerrará el cauce. Argumenta que solo el 4% llega al lago, que es
  marginal. Vecinos y el gobernador regional lo rechazan. La pregunta de
  fondo: en un Chile que se seca, ¿tiene sentido cerrar uno de los pocos
  aportes que el lago todavía recibe?"*

---

## Acto 4 — "Lo que sigue" (60s)

### 4.1 Los datos faltantes (15s)
- **Visual**: Mapa de la cuenca con marcadores rojos sobre los puntos donde
  no hay estación de medición
- **Datos**:
  - ❌ Caudal histórico Río Blanco
  - ❌ Caudal histórico Trafampulli al cierre
  - ❌ Limnimetría Lago Colico
  - ❌ Caudal Ojos del Caburga
  - ❌ Batimetría reciente del lago
- **Narración**: *"Lo más impactante es que durante todo el conflicto, no se
  midieron las cosas que importaban. No hay registros de cuánta agua entraba
  por el Río Blanco. No hay limnimetría del Lago Colico. La última batimetría
  es de los años ochenta."*

### 4.2 La invitación (20s)
- **Visual**: Dashboard interactivo del repositorio
- **Footage**: capturar `streamlit run dashboard/app.py`
- **Datos**: invitar a usar el dashboard, links al repo
- **Narración**: *"Por eso construimos esta herramienta. Todos los datos que
  encontramos están abiertos. El modelo está abierto. Si tienes una hipótesis,
  puedes probarla. Si encuentras un error, puedes corregirlo. Si quieres
  proponer una solución, los números están a tu disposición."*

### 4.3 El cierre (15s)
- **Visual**: Vuelta al lago al atardecer, lleno
- **Footage**: `atardecer_caburgua.jpg`
- **Narración**: *"El Lago Caburga sobrevivió a la sequía de los años cuarenta
  y a la de los años noventa. Sobrevivirá a esta también. La pregunta es qué
  decisiones tomamos hoy para cuando vuelva a llover poco. Y para ese
  momento, lo más importante es que la conversación se base en datos, no en
  trincheras."*

### 4.4 Créditos (10s)
- Datos: CR2, DGA, U. Austral, U. de Chile, Wikimedia Commons
- Repositorio: github.com/MendozaVolcanic/lago-caburga
- Animación: hecha con [herramienta]

---

## Recursos visuales por escena

| Escena | Archivo en repo | Origen |
|---|---|---|
| 1.1 atardecer | `docs/footage/wikimedia/atardecer_caburgua.jpg` | CC BY-SA 3.0 |
| 1.2 Ojos | `docs/footage/wikimedia/ojos_2019_01.jpg` | CC BY-SA 4.0 |
| 1.3a 2019 | `docs/footage/wikimedia/caburgua_playa_2019_01.jpg` | CC BY-SA 4.0 |
| 1.3b 2022 | `docs/footage/wikimedia/lago_caburgua_2022.jpg` | CC BY-SA 4.0 |
| 1.3c 2024 | `docs/footage/prensa/terram_2024_recuperacion.jpg` | © Terram (uso editorial) |
| 1.4 anomalías | `notebooks/figs/02_anomalias_precipitacion.png` | propio |
| 1.5 mapa | `notebooks/figs/04_mapa.html` (screenshot) | propio |
| 2.x dique | extraer frames de `4eIuEYIJJJo` (YouTube UATV) | © UATV |
| 3.2 precip | `notebooks/figs/02_precip_anual_completa.png` | propio |
| 3.4 balance | screenshot dashboard | propio |
| 3.5 recuperación | `latercera_2024_*` | © La Tercera |
| 4.2 dashboard | screenshot dashboard | propio |
| 4.3 atardecer | mismo que 1.1 | CC BY-SA 3.0 |

---

## Producción

### Texto narrativo
Total ~750 palabras. Velocidad ~150 palabras/min → ~5 minutos. Locutor neutro.
Versión en español de Chile.

### Música
Sugerencia: instrumental ambiental de bajo perfil. Cambios de pace en cada
acto. Para el momento de la acción mapuche (2.4), un instrumento andino
(trutruka, kultrún) sería contextualmente apropiado y respetuoso si se hace
con autorización.

### Subtítulos
Generar bilingüe (es-CL, en-US) para alcance internacional.

### Hooks por plataforma
- Versión 60s para Instagram/TikTok: solo Acto 1 + invitación dashboard
- Versión 5min completa para YouTube
- Versión 90s para Twitter/X: Acto 2 + 3.5

# Lago Caburga — análisis abierto

Herramienta didáctica para visualizar y comprender el descenso del Lago Caburga (Pucón, Región de La Araucanía, Chile) y la polémica sobre el desvío del río Trafampulli.

El objetivo es ofrecer evidencia abierta y reproducible que permita a la ciudadanía evaluar por sí misma las tres hipótesis en juego (megasequía, desvío del Trafampulli, fisuras post-terremoto), evitando la dicotomía mediática y reduciendo la desconfianza entre comunidades, autoridades y científicos.

## Estado de los hallazgos

Ver [HALLAZGOS.md](HALLAZGOS.md) para el resumen ejecutivo del análisis de los tres estudios principales (U. Austral 2021, U. de Chile 2022, Contraloría 2024).

**Conclusión técnica preliminar:** la causa de primer orden es la megasequía 2010–presente; el cierre del Trafampulli es un factor agravante de magnitud incierta (entre 0.3 y 2 m³/s según fuente). Las narrativas "es solo el clima" y "es solo el dique" son ambas simplificaciones.

## Estructura del repositorio

```
.
├── HALLAZGOS.md            síntesis ejecutiva
├── docs/                   documentos fuente (PDFs no versionados; ver scripts/)
│   ├── estudios/           informes U. Austral, U. Chile, Contraloría, CR2
│   ├── dga/                balance hídrico, red de lagos
│   └── prensa/             cartas y notas
├── data/
│   ├── raw/                series DGA descargadas (no versionadas)
│   └── processed/          CSVs limpios y consolidados
├── notebooks/              análisis Jupyter
├── dashboard/              app interactiva (Streamlit / Observable)
└── scripts/
    └── download_docs.sh    recrea docs/ desde fuentes públicas
```

## Datos clave (códigos DGA)

| Código BNA | Estación | Tipo |
|---|---|---|
| `09417001-K` | Lago Caburga | Limnimétrica + pluviométrica |
| `09417002-8` | Ojos del Caburga | Manantial |
| `09416001-4` | Río Liucura en Liucura | Fluviométrica |
| `09416002-2` | Lago Tinquilco | Limnimétrica + pluviométrica |
| `09418001-5` | Río Pucón en Balseadero Quelhue | Fluviométrica |
| `09420009-1` | Lago Villarrica | Limnimétrica |
| `09420002-4` | Pucón | Meteorológica |
| `09401001-2` | Tricauco | Pluviométrica |
| `09412001` | Río Trancura en Curarrehue | Fluviométrica |
| `09414001` | Río Trancura antes Río Llafenco | Fluviométrica |
| `09420001` | Río Toltén en Villarrica | Fluviométrica |

Datos faltantes críticos: caudal histórico Río Blanco (estación recién instalada nov 2021), caudal Trafampulli al punto de cierre, limnimetría Lago Colico, caudal Ojos del Caburga.

## Roadmap

- [x] Investigación documental y descarga de fuentes
- [x] Síntesis crítica de los tres estudios principales
- [ ] **(en curso)** Descarga de series DGA y construcción de dataset consolidado
- [ ] Notebook 1: precipitación vs nivel del lago (correlación maestra)
- [ ] Notebook 2: doble acumulada Caburga vs Villarrica/Neltume (detección de quiebre)
- [ ] Notebook 3: balance hídrico simplificado (replicar U. Chile escenarios 1-4)
- [ ] Dashboard interactivo con sliders de balance hídrico
- [ ] Animaciones (Claude design) sobre implicancias de Δnivel y Δprecipitación

## Licencia

Datos y análisis bajo CC BY 4.0. Documentos originales conservan su licencia de origen.

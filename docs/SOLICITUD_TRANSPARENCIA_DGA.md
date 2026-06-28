# Solicitud de Acceso a la Información Pública — DGA

> Para presentar en el **Portal de Transparencia** (portaltransparencia.cl) o por la
> OIRS/SIAC de la Dirección General de Aguas, Región de La Araucanía.
> Marco legal: **Ley N° 20.285** sobre Acceso a la Información Pública.
> Plazo de respuesta: 20 días hábiles (prorrogable por 10).

---

## Texto de la solicitud (listo para pegar)

Estimados:

En el marco de la Ley N° 20.285 sobre Acceso a la Información Pública, y con el
objeto de desarrollar un estudio ciudadano abierto y reproducible sobre el
descenso del nivel del **Lago Caburga** (comunas de Pucón y Cunco, Región de La
Araucanía) y su relación con el río Trafampulli, vengo a solicitar a la Dirección
General de Aguas la siguiente información. Solicito que, en lo posible, las series
de datos se entreguen en **formato digital reutilizable** (CSV, Excel o
equivalente, no PDF escaneado), conforme al principio de apertura y reutilización
de la información pública.

**1. Series hidrométricas históricas completas (resolución diaria o la máxima
disponible), desde el inicio de registro hasta la fecha, de las siguientes
estaciones de la Red Hidrométrica Nacional:**

- Nivel limnimétrico — **Lago Caburga** (BNA 09417001-K)
- Precipitación — estación **Lago Caburga** (09417001 / 09417007-9)
- Nivel y/o caudal — **Ojos del Caburga** (BNA 09417002-8)
- Nivel limnimétrico — **Lago Villarrica** (BNA 09420009-1)
- Nivel limnimétrico — **Lago Tinquilco** (BNA 09416002-2)
- Caudal — **Río Curaco en Colico** (BNA 09405001)
- Caudal — **Río Pucón en Balseadero Quelhue** (BNA 09418001-5)
- Caudal — **Río Liucura en Liucura** (BNA 09416001-4)
- Caudal — **Río Trafampulli en Rinconada** y cualquier otra estación o punto de
  aforo sobre el río Trafampulli o el denominado "Estero La Cascada".
- Caudal — **Río Blanco** afluente al Lago Caburga (estación instalada
  aproximadamente en noviembre de 2021): toda la serie registrada a la fecha.

**2. Para el Lago Colico**, indicar si existe estación limnimétrica o de caudal
y, de existir, entregar su serie histórica; en caso contrario, certificar su
inexistencia.

**3. Aforos y mediciones puntuales** realizados por la DGA sobre el río
Trafampulli / Estero La Cascada y su conexión con el Lago Caburga, incluyendo:
las minutas de las visitas técnicas de 2021 (en particular la del 30 de
septiembre de 2021 y la Minuta Técnica N° 1 de diciembre de 2021), y los
resultados de las **once (11) mediciones** realizadas entre noviembre y
diciembre de 2025 que fundamentaron la afirmación de que solo un 4% del caudal
llegaría al lago (datos crudos por punto, coordenadas y fechas).

**4. Estudios técnicos en versión íntegra, con sus anexos digitales:**

- "Análisis de potenciales causas del descenso del Lago Caburga" (SIT N° 494,
  2022, ejecutado por la Universidad de Chile), incluyendo los **anexos digitales**
  citados en el informe: datos de evaporación, caudales máximos del río
  Trafampulli, calidad de agua, planilla de balance hídrico, proyecto SIG y
  códigos utilizados.
- "Estudio Hidráulico y Modelación Río Trafampulli" y cualquier otro estudio de
  caudales o de defensa ribereña asociado al sector Llanqui-Llanqui.

**5. Expedientes y actos administrativos** relativos a la intervención del cauce:
el Oficio DGA N° 347 (2007), el Oficio DGA N° 1718 (31 de octubre de 2006), el
expediente DGA IX N° 493 (defensa ribereña / pretil), la Resolución Exenta
N° 199 de 2023, el Memorándum Técnico N° 1 de la DGA Regional Araucanía (diciembre
de 2023), y la resolución que dispone la restitución del cauce tras el fallo de
la Corte Suprema (rol N° 12.225-2025).

**6. Derechos de aprovechamiento de aguas** otorgados, regularizados o en trámite
en la cuenca aportante del Lago Caburga y subcuencas de los ríos Blanco y
Trafampulli, con caudal, naturaleza (superficial/subterránea), tipo de ejercicio
y fecha de constitución.

**7. Cualquier batimetría del Lago Caburga** que obre en poder de la DGA, y la
georreferenciación de la red de monitoreo de la zona (coordenadas de las
estaciones señaladas).

Agradeceré indicar, respecto de cada ítem, si la información existe y está
disponible, o bien certificar su inexistencia cuando corresponda. La finalidad es
estrictamente de interés público: poner a disposición de la comunidad, las
autoridades y la academia un conjunto común de datos que permita analizar
objetivamente las causas del descenso del lago.

Quedo atento a su respuesta. Saluda atentamente,

[Nombre completo]
[RUT]
[Correo electrónico / domicilio para notificaciones]

---

### Notas para presentar

- Si el Portal de Transparencia limita la extensión, dividir en 2 solicitudes:
  (A) series hidrométricas e ítems 1–3; (B) estudios, expedientes y derechos (4–7).
- Pedir explícitamente **formato reutilizable** ayuda a recibir CSV/Excel en vez
  de PDF.
- Una vez recibidas las series de nivel, correr `scripts/extract_dga_niveles.py`
  para integrarlas y calibrar la hipsometría y el balance.

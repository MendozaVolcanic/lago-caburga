"""Notebook 4 — Mapa GIS de la cuenca Caburga.

Genera un mapa Folium interactivo con:
  - Estaciones DGA de precipitación y caudal
  - Lagos (Caburga, Colico, Villarrica, Tinquilco)
  - Río Trafampulli y ubicación aproximada del dique 2007
  - Ojos del Caburga (drenaje subterráneo)
  - Río Blanco (afluente principal)

Fondo: tiles OpenStreetMap.

Salida: notebooks/figs/04_mapa.html (auto-contenido, abre en cualquier navegador)
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import folium
from folium.plugins import MarkerCluster

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
OUT = ROOT / "notebooks" / "figs"
OUT.mkdir(exist_ok=True)

# Centro del mapa: Lago Caburga
CENTRO = (-39.20, -71.81)

# Puntos de interés (no en estaciones DGA)
POIS = [
    {"nombre": "Lago Caburga (centro)", "lat": -39.20, "lon": -71.81,
     "tipo": "lago", "info": "53 km², drenaje subterráneo único en Chile"},
    {"nombre": "Ojos del Caburga", "lat": -39.2367, "lon": -71.8356,
     "tipo": "drenaje", "info": "Salida subterránea natural del lago"},
    {"nombre": "Lago Colico", "lat": -39.10, "lon": -71.95,
     "tipo": "lago", "info": "Recibe el caudal del Trafampulli desde 2007/2009"},
    {"nombre": "Lago Villarrica", "lat": -39.27, "lon": -72.07,
     "tipo": "lago", "info": "Lago vecino, usado como referencia regional"},
    {"nombre": "Dique Trafampulli / Estero La Cascada", "lat": -39.0667, "lon": -71.7833,
     "tipo": "dique", "info": "Construido 2007 por oficio DGA 347 (sin EIA). Destruido por comunidad mapuche 16-may-2022. Corte Suprema autoriza reconstrucción ago-2025. DGA mide 4% del cauce llega al lago (nov-2025)."},
    {"nombre": "Río Blanco (afluente principal)", "lat": -39.10, "lon": -71.78,
     "tipo": "rio", "info": "Cuenca 180 km², principal afluente del Caburga"},
    {"nombre": "Río Trafampulli (alto)", "lat": -39.04, "lon": -71.65,
     "tipo": "rio", "info": "Cuenca 38 km² al punto de cierre, antes alimentaba ambos lagos"},
]

ICON = {
    "precipitacion": ("cloud", "blue"),
    "fluviometrica": ("tint", "darkblue"),
    "lago": ("info-sign", "lightblue"),
    "drenaje": ("download", "purple"),
    "dique": ("ban-circle", "red"),
    "rio": ("forward", "cadetblue"),
}


def construir_mapa() -> Path:
    m = folium.Map(location=CENTRO, zoom_start=11, tiles="OpenStreetMap",
                   control_scale=True)
    folium.TileLayer("Esri.WorldImagery", name="Satélite").add_to(m)

    # Polígono aproximado del lago Caburga
    folium.Polygon(
        locations=[
            (-39.130, -71.820), (-39.140, -71.790), (-39.180, -71.770),
            (-39.220, -71.770), (-39.245, -71.795), (-39.245, -71.835),
            (-39.215, -71.860), (-39.165, -71.860), (-39.135, -71.840),
        ],
        color="#26c", weight=2, fill=True, fill_color="#69f", fill_opacity=0.35,
        popup="Lago Caburga (contorno aproximado, 53 km²)"
    ).add_to(m)

    # Cuenca aportante (caja simplificada)
    folium.Rectangle(
        bounds=[(-39.30, -72.05), (-38.95, -71.55)],
        color="#888", weight=1, fill=False, dash_array="5,5",
        popup="Cuenca aportante aproximada (335 km²)"
    ).add_to(m)

    # Línea aproximada del Sistema de Fallas Liquiñe-Ofqui (eje N-S)
    folium.PolyLine(
        locations=[(-38.5, -71.83), (-39.0, -71.81), (-39.5, -71.79)],
        color="#a44", weight=2, dash_array="4,8",
        popup="Sistema de Fallas Liquiñe-Ofqui (esquemático)"
    ).add_to(m)

    # Estaciones DGA
    estaciones = pd.read_csv(DATA / "estaciones_geo.csv")
    fg_est = folium.FeatureGroup(name="Estaciones DGA", show=True).add_to(m)
    for _, r in estaciones.iterrows():
        ico, color = ICON.get(r["tipo"], ("info-sign", "gray"))
        cod = str(r["codigo_estacion"]).zfill(8)
        folium.Marker(
            location=(r["latitud"], r["longitud"]),
            popup=folium.Popup(
                f"<b>{r['nombre']}</b><br>Código: {cod}<br>"
                f"Tipo: {r['tipo']}<br>Altitud: {r['altura']} m s.n.m.",
                max_width=260),
            tooltip=r["nombre"],
            icon=folium.Icon(icon=ico, color=color, prefix="glyphicon"),
        ).add_to(fg_est)

    # POIs
    fg_poi = folium.FeatureGroup(name="Puntos de interés", show=True).add_to(m)
    for p in POIS:
        ico, color = ICON.get(p["tipo"], ("info-sign", "gray"))
        folium.Marker(
            location=(p["lat"], p["lon"]),
            popup=folium.Popup(
                f"<b>{p['nombre']}</b><br>{p['info']}", max_width=260),
            tooltip=p["nombre"],
            icon=folium.Icon(icon=ico, color=color, prefix="glyphicon"),
        ).add_to(fg_poi)

    # Línea aproximada del brazo del Trafampulli histórico hacia Caburga
    folium.PolyLine(
        locations=[(-39.0667, -71.7833), (-39.10, -71.79), (-39.13, -71.79)],
        color="#c44", weight=3, dash_array="2,6",
        popup="Brazo histórico Trafampulli → Caburga (cerrado en 2007)"
    ).add_to(m)

    # Línea del Trafampulli hacia Colico (activo desde 2007)
    folium.PolyLine(
        locations=[(-39.0667, -71.7833), (-39.08, -71.85), (-39.10, -71.95)],
        color="#48a", weight=3,
        popup="Trafampulli → Colico (activo desde 2007)"
    ).add_to(m)

    folium.LayerControl().add_to(m)
    out = OUT / "04_mapa.html"
    m.save(str(out))
    return out


if __name__ == "__main__":
    print(construir_mapa())

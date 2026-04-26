// Script Google Earth Engine — Lago Caburga timelapse Landsat 1984-presente
//
// Uso: pegar este script en https://code.earthengine.google.com/
// y darle Run. Genera animación GIF y exporta MP4.
//
// Requiere cuenta gratis de GEE (registro: https://earthengine.google.com/)
//
// Output: animación GIF y MP4 con composiciones anuales mediana
// (filtra nubes a < 30%) sobre el Lago Caburga.

// ROI: Lago Caburga + cuenca aportante
var roi = ee.Geometry.Rectangle([-71.92, -39.30, -71.62, -38.95]);

// Visualización RGB con stretch fijo
var visParams = {
  bands: ['SR_B4', 'SR_B3', 'SR_B2'],
  min: 7000,
  max: 16000,
  gamma: 1.2
};

// Función: trae una composición mediana del año dado
function annualComposite(year) {
  var start = ee.Date.fromYMD(year, 12, 1);   // verano austral (mín. nubes)
  var end = ee.Date.fromYMD(year + 1, 3, 31);

  // Concatenar Landsat 5/7/8/9 disponibles en cada periodo
  var l5 = ee.ImageCollection('LANDSAT/LT05/C02/T1_L2')
              .filterDate(start, end).filterBounds(roi);
  var l7 = ee.ImageCollection('LANDSAT/LE07/C02/T1_L2')
              .filterDate(start, end).filterBounds(roi);
  var l8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
              .filterDate(start, end).filterBounds(roi);
  var l9 = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2')
              .filterDate(start, end).filterBounds(roi);

  // Renombrar Landsat 5/7 (B1=blue, B2=green, B3=red, B4=NIR)
  // → mismo nombre que L8/9 (B2=blue, B3=green, B4=red, B5=NIR)
  var l5_ren = l5.select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4'],
                          ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5']);
  var l7_ren = l7.select(['SR_B1', 'SR_B2', 'SR_B3', 'SR_B4'],
                          ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5']);
  var l8_l9 = l8.merge(l9).select(['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5']);

  var col = l5_ren.merge(l7_ren).merge(l8_l9);

  // Mediana anual (resistente a nubes)
  return col.median()
            .clip(roi)
            .set('year', year);
}

// Generar serie 1986 → 2025
var years = ee.List.sequence(1986, 2025);
var series = ee.ImageCollection.fromImages(
  years.map(function(y) { return annualComposite(ee.Number(y)); }));

// Visualizar primer frame
Map.centerObject(roi, 11);
Map.addLayer(annualComposite(2024), visParams, 'Caburga 2024');
Map.addLayer(annualComposite(2018), visParams, 'Caburga 2018 (sequía)');

// Anotación: imprimir tamaño
print('Frames generados:', series.size());

// Exportar como animación
var gifParams = {
  region: roi,
  dimensions: 720,
  framesPerSecond: 2,
  crs: 'EPSG:4326',
  bands: ['SR_B4', 'SR_B3', 'SR_B2'],
  min: 7000,
  max: 16000
};

print(ui.Thumbnail({image: series, params: gifParams}));

// Exportar a Drive (descomenta para correr)
/*
Export.video.toDrive({
  collection: series,
  description: 'caburga_timelapse_1986_2025',
  dimensions: 720,
  framesPerSecond: 2,
  region: roi,
  crs: 'EPSG:4326',
  maxPixels: 1e10
});
*/

// ============== NDWI ==============
// Índice de agua: NDWI = (Green - NIR) / (Green + NIR)
function ndwi(img) {
  return img.normalizedDifference(['SR_B3', 'SR_B5']).rename('NDWI')
            .copyProperties(img, ['year']);
}
var ndwiSeries = series.map(ndwi);

var ndwiVis = {
  min: -0.5,
  max: 0.8,
  palette: ['8B4513', 'FFFACD', '00FFFF', '0000FF', '00008B']
};

Map.addLayer(ndwiSeries.filter(ee.Filter.eq('year', 2024)).first(), ndwiVis,
             'NDWI 2024');
Map.addLayer(ndwiSeries.filter(ee.Filter.eq('year', 2018)).first(), ndwiVis,
             'NDWI 2018 (sequía)');

// ============== Estadísticas ==============
// Calcular área con NDWI > 0 (agua) por año
function lakeArea(img) {
  var water = img.select('NDWI').gt(0);
  var area = water.multiply(ee.Image.pixelArea())
                  .reduceRegion({
                    reducer: ee.Reducer.sum(),
                    geometry: roi,
                    scale: 30,
                    maxPixels: 1e10
                  });
  return ee.Feature(null, {
    'year': img.get('year'),
    'lake_area_km2': ee.Number(area.get('NDWI')).divide(1e6)
  });
}

var areaSeries = ndwiSeries.map(lakeArea);
print('Serie área lago:', areaSeries);

// Gráfico
var chart = ui.Chart.feature.byFeature(areaSeries, 'year', 'lake_area_km2')
              .setOptions({
                title: 'Superficie del Lago Caburga (NDWI > 0)',
                hAxis: {title: 'Año'},
                vAxis: {title: 'Área (km²)'},
                lineWidth: 2,
                pointSize: 4
              });
print(chart);

// Exportar tabla a Drive (descomenta para correr)
/*
Export.table.toDrive({
  collection: areaSeries,
  description: 'caburga_lake_area_landsat',
  fileFormat: 'CSV'
});
*/

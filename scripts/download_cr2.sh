#!/usr/bin/env bash
# Descarga las bases de datos diarias de precipitación y caudales del CR2.
# Idempotente: omite archivos ya descargados.
set -e
cd "$(dirname "$0")/.."
mkdir -p data/raw/cr2
cd data/raw/cr2

UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

dl() {
  local url="$1" out="$2"
  if [ -s "$out" ]; then echo "ok  $out"; return; fi
  echo "get $out"
  curl -L -A "$UA" -s -o "$out" "$url" --max-time 600
}

dl "https://www.cr2.cl/download/cr2-prdaily-2019-zip/?wpdmdl=25581" cr2_prDaily_2019.zip
dl "https://www.cr2.cl/download/cr2-qflxdaily-2019-zip/?wpdmdl=25589" cr2_qflxDaily_2019.zip

for z in cr2_prDaily_2019.zip cr2_qflxDaily_2019.zip; do
  if [ ! -d "$(basename "$z" .zip | sed 's/2019/2020/')" ]; then
    unzip -q -o "$z"
  fi
done

echo "listo. corre: python scripts/extract_cr2_stations.py && python scripts/extract_cr2_caudales.py"

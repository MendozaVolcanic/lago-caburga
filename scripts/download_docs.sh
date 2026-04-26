#!/usr/bin/env bash
# Recrea docs/ desde fuentes públicas. Idempotente.
set -e
cd "$(dirname "$0")/.."
mkdir -p docs/estudios docs/dga docs/prensa

UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

dl() {
  local url="$1" out="$2"
  if [ -s "$out" ]; then echo "ok  $out"; return; fi
  echo "get $out"
  curl -L -A "$UA" -s -o "$out" "$url" --max-time 600
}

dl "https://www.sustentapucon.cl/wp-content/uploads/2021/12/INFORME-CABURGUA-SUSTENTABLE-3.pdf" \
   "docs/estudios/informe_caburgua_sustentable_uach_2021.pdf"

dl "https://repositoriodirplan.mop.gob.cl/biblioteca/bitstreams/c005b353-85cb-4542-bf55-ed3afe2e07e5/download" \
   "docs/estudios/uchile_caburgua_2022.pdf"

dl "https://www.lavozdepucon.cl/wp-content/uploads/2024/03/trafampulli_contraloria.pdf" \
   "docs/estudios/contraloria_trafampulli_2024.pdf"

dl "https://www.cr2.cl/wp-content/uploads/2015/11/informe-megasequia-cr21.pdf" \
   "docs/estudios/megasequia_cr2_2015.pdf"

dl "https://uchile.cl/dam/jcr:c9895061-40f4-4f23-8cf7-64737495bbad/balancehidricodga2017sit417resumenejecutivovf.pdf" \
   "docs/dga/balance_hidrico_dga_2017.pdf"

dl "https://bibliotecadigital.ciren.cl/bitstream/handle/20.500.13082/32406/DGA_2017_reporte_red_control_lagos_DGA.pdf?sequence=1&isAllowed=y" \
   "docs/dga/red_control_lagos_dga_2017.pdf"

dl "https://caburguasustentable.cl/wp-content/uploads/sites/23/2022/06/CartaDirector_LaTercera_21.06.22.pdf" \
   "docs/prensa/carta_caburgua_latercera_2022.pdf"

echo "listo."

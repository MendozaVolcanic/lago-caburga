"""Genera GIF animado consolidando los frames Sentinel-2 NDWI.

También genera un MP4 si ffmpeg/imageio-ffmpeg está disponible.

Uso:
  python scripts/make_gif.py                 # default: 1.0s/frame
  python scripts/make_gif.py --duration 0.4  # más rápido
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path
import imageio.v3 as iio
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
FRAMES_DIR = ROOT / "notebooks" / "figs" / "sentinel"
OUT_GIF = ROOT / "notebooks" / "figs" / "sentinel_timelapse.gif"
OUT_MP4 = ROOT / "notebooks" / "figs" / "sentinel_timelapse.mp4"


def add_caption(img: Image.Image, text: str) -> Image.Image:
    """Sobreimprime fecha en la esquina inferior izquierda."""
    img = img.convert("RGB")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 28)
    except OSError:
        font = ImageFont.load_default()
    margin = 12
    bbox = draw.textbbox((margin, img.height - 50), text, font=font)
    draw.rectangle(bbox, fill=(0, 0, 0, 200))
    draw.text((margin, img.height - 50), text, fill="white", font=font)
    return img


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--duration", type=float, default=0.8,
                    help="segundos por frame")
    ap.add_argument("--width", type=int, default=720)
    args = ap.parse_args()

    frames = sorted(FRAMES_DIR.glob("*.png"))
    if not frames:
        print("No hay frames. Corre `python scripts/sentinel2_caburga.py` primero.")
        return

    print(f"Procesando {len(frames)} frames…")
    # Determinar tamaño común (todos al primer frame)
    first = Image.open(frames[0])
    ratio = args.width / first.width
    target_size = (args.width, int(first.height * ratio))

    images = []
    for f in frames:
        fecha = f.stem
        img = Image.open(f).convert("RGB")
        img = img.resize(target_size, Image.Resampling.LANCZOS)
        img = add_caption(img, fecha)
        images.append(np.array(img))

    # GIF
    iio.imwrite(OUT_GIF, images, duration=int(args.duration * 1000), loop=0,
                plugin="pillow")
    print(f"  → {OUT_GIF} ({OUT_GIF.stat().st_size // 1024} KB, {len(images)} frames)")

    # MP4 (si está ffmpeg disponible)
    try:
        iio.imwrite(OUT_MP4, images, fps=int(1 / args.duration),
                    codec="libx264", quality=8)
        print(f"  → {OUT_MP4} ({OUT_MP4.stat().st_size // 1024} KB)")
    except Exception as e:
        print(f"  (MP4 omitido: {e})")


if __name__ == "__main__":
    main()

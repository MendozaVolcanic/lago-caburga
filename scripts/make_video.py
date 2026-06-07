"""Genera un video MP4 resumen del estudio (formato redes sociales).

Ensambla title cards + imágenes del lago + gráficos en una secuencia de ~70s
con texto sobreimpuesto. No requiere ffmpeg externo (usa imageio-ffmpeg).

Dos formatos:
  - docs/assets/video_horizontal.mp4   1280x720 (YouTube/web)
  - docs/assets/video_vertical.mp4     720x1280 (IG/TikTok)

Cada "escena" = imagen de fondo + caja de texto. Transiciones por crossfade.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import imageio.v3 as iio
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs" / "assets"
FOOTAGE = ROOT / "docs" / "footage"
FPS = 30

C_BG = (14, 26, 36)
C_FG = (232, 238, 245)
C_ACC = (74, 163, 223)
C_MUTED = (155, 175, 193)


def font(size: int, bold=False):
    names = (["arialbd.ttf", "Arial Bold.ttf"] if bold else []) + \
            ["arial.ttf", "Arial.ttf", "DejaVuSans.ttf"]
    for n in names:
        try:
            return ImageFont.truetype(n, size)
        except OSError:
            continue
    return ImageFont.load_default()


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=fnt) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def scene_bg(size, bg_img: Path | None, darken=0.55):
    W, H = size
    canvas = Image.new("RGB", size, C_BG)
    if bg_img and bg_img.exists():
        img = Image.open(bg_img).convert("RGB")
        # cover
        ratio = max(W / img.width, H / img.height)
        img = img.resize((int(img.width * ratio), int(img.height * ratio)), Image.LANCZOS)
        x = (img.width - W) // 2
        y = (img.height - H) // 2
        img = img.crop((x, y, x + W, y + H))
        canvas.paste(img, (0, 0))
        overlay = Image.new("RGB", size, C_BG)
        canvas = Image.blend(canvas, overlay, darken)
    return canvas


def draw_scene(size, bg, kicker, title, body, accent_metric=None):
    W, H = size
    vertical = H > W
    canvas = scene_bg(size, bg)
    d = ImageDraw.Draw(canvas)
    margin = int(W * 0.08)
    y = int(H * (0.32 if vertical else 0.30))

    if kicker:
        fk = font(int(W * 0.028), bold=True)
        d.text((margin, y), kicker.upper(), font=fk, fill=C_ACC)
        y += int(W * 0.05)

    ft = font(int(W * (0.058 if vertical else 0.052)), bold=True)
    for line in wrap(d, title, ft, W - 2 * margin):
        d.text((margin, y), line, font=ft, fill=C_FG)
        y += int(ft.size * 1.18)
    y += int(W * 0.02)

    if accent_metric:
        fm = font(int(W * (0.14 if vertical else 0.11)), bold=True)
        d.text((margin, y), accent_metric, font=fm, fill=C_ACC)
        y += int(fm.size * 1.05)

    if body:
        fb = font(int(W * (0.034 if vertical else 0.03)))
        for line in wrap(d, body, fb, W - 2 * margin):
            d.text((margin, y), line, font=fb, fill=C_MUTED)
            y += int(fb.size * 1.35)

    return np.array(canvas)


def frames_for(arr, seconds, fade_in=0.4):
    n = int(seconds * FPS)
    out = []
    fade_n = int(fade_in * FPS)
    for i in range(n):
        if i < fade_n:
            a = i / fade_n
            black = np.zeros_like(arr)
            out.append((arr * a + black * (1 - a)).astype(np.uint8))
        else:
            out.append(arr)
    return out


def build(size, suffix):
    W, H = size
    wm = FOOTAGE / "wikimedia"
    scenes = [
        dict(bg=wm / "atardecer_caburgua.jpg", kicker="Estudio abierto",
             title="El Lago Caburga se está vaciando", body="Qué dicen los datos — y cómo se resuelve el conflicto.", sec=4),
        dict(bg=wm / "ojos_2019_01.jpg", kicker="01 · El fenómeno",
             title="Un lago que drena bajo tierra", body="Por los Ojos del Caburga. Único en Chile. Por eso es tan sensible al agua que recibe.", sec=4.5),
        dict(bg=wm / "lago_caburgua_2022.jpg", kicker="La crisis",
             title="300 metros de playa donde antes había agua", accent_metric="−25%", body="caída del nivel entre 2000-2010 y 2011-2020.", sec=4.5),
        dict(bg=None, kicker="02 · El conflicto",
             title="Un dique cortó el río Trafampulli en 2007", body="La comunidad culpa al dique. Las autoridades, a la sequía. 18 años de disputa hasta la Corte Suprema.", sec=5),
        dict(bg=None, kicker="16 de mayo de 2022",
             title="La comunidad mapuche derribó el dique", body="Tras 16 años de peticiones sin respuesta. Cuatro días con palas y manos. El agua volvió.", sec=5),
        dict(bg=ASSETS / "precip_larga_1950_2025.png", kicker="03 · Los datos",
             title="La lluvia cayó un tercio desde 2010", accent_metric="−34%", body="en la estación del lago. Y la nieve de la cuenca: de 56% a 27%.", sec=5),
        dict(bg=ASSETS / "infografia_atribucion.png", kicker="04 · La evidencia",
             title="Megasequía 80% · Dique 20%", body="El lago recuperó +350 m con El Niño 2024 sin remover el dique. El clima manda.", sec=5),
        dict(bg=None, kicker="Pero",
             title="Secundario no es irrelevante", body="En un clima que se seca, cerrar uno de los pocos aportes del lago no se justifica.", sec=4.5),
        dict(bg=wm / "ojos_2019_01.jpg", kicker="05 · La salida",
             title="Cómo lo resolvió Mono Lake", body="Nivel-objetivo acordado + ciencia independiente + gobernanza. No un juicio ganado.", sec=5),
        dict(bg=None, kicker="El camino",
             title="Datos compartidos · Cota meta · Protección legal", body="Como Aculeo, declarada Humedal Urbano en 2025. La salida es colaborativa.", sec=5),
        dict(bg=wm / "atardecer_caburgua.jpg", kicker="Estudio abierto",
             title="Todos los datos son públicos", body="github.com/MendozaVolcanic/lago-caburga", sec=4.5),
    ]
    all_frames = []
    for s in scenes:
        arr = draw_scene(size, s.get("bg"), s["kicker"], s["title"],
                         s.get("body", ""), s.get("accent_metric"))
        all_frames.extend(frames_for(arr, s["sec"]))

    out = ASSETS / f"video_{suffix}.mp4"
    iio.imwrite(out, all_frames, fps=FPS, codec="libx264", quality=7,
                macro_block_size=16)
    print(f"  {out} ({out.stat().st_size // 1024} KB, {len(all_frames)//FPS}s)")
    return out


if __name__ == "__main__":
    print("Horizontal…")
    build((1280, 720), "horizontal")
    print("Vertical…")
    build((720, 1280), "vertical")

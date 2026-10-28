"""
Comprueba la portada de un short: el primer fotograma, que Instagram y TikTok usan como
miniatura del perfil. Falla (código 1) si el fotograma está casi vacío (solo fondo y rejilla)
o si hay contenido fuera del recorte 3:4 de la cuadrícula de Instagram.
Guarda el fotograma junto al video como portada.png.

Uso: python tools/portada.py shorts/NN_tema/final.mp4 [t=0]
"""
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops

video = Path(sys.argv[1])
t = sys.argv[2] if len(sys.argv) > 2 else "0"
salida = video.with_name("portada.png")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", t, "-i", str(video), "-frames:v", "1",
                str(salida)], check=True)
im = Image.open(salida).convert("L")
fondo = Image.new("L", im.size, 18)                    # #0B1220 en gris ≈ 18
dif = ImageChops.difference(im, fondo).point(lambda v: 255 if v > 60 else 0)
w, h = im.size
total = sum(dif.histogram()[255:]) / (w * h)
recorte = (h - w * 4 // 3) // 2                         # 240 px en 1080×1920
fuera = dif.crop((0, 0, w, recorte)).histogram()[255] + \
    dif.crop((0, h - recorte, w, h)).histogram()[255]
print(f"{salida}: contenido {100 * total:.1f} % del fotograma; "
      f"píxeles fuera del recorte 3:4: {fuera}")
errores = []
if total < 0.02:
    errores.append("la portada está casi vacía: el gancho debe verse desde t = 0")
if fuera > 0.002 * w * recorte:
    errores.append("hay contenido en la franja que Instagram recorta en la cuadrícula")
for e in errores:
    print("ERROR:", e)
sys.exit(1 if errores else 0)

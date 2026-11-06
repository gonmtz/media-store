"""
Avatar del canal con el avión refinado en 3D (lib/avion.py), 6-nov-2026.
Uso:  python marca/logo3d.py [variante]   → marca/avatar3d_<variante>.png (800 y 1600 px)
Variantes: anillo (como el avatar actual: avión dentro de los tres arcos) y sale (avión más
grande que se sale del anillo). Los tres arcos llevan los colores de los tres giros; el avión
lleva los mandos en los mismos colores (alerones rosa, elevador azul, timón amarillo).
Todo cabe en el círculo inscrito (recorte redondo de YouTube, Instagram y TikTok).
"""
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib import avion as A  # noqa: E402

BG = (11, 18, 32, 255)
AZUL, ROSA, AMARILLO = (56, 189, 248), (251, 113, 133), (251, 191, 36)
N = 2400                                  # lienzo de trabajo (supermuestreo)


def fondo():
    im = Image.new("RGBA", (N, N), BG)
    # halo azul muy suave en el centro
    y, x = np.mgrid[0:N, 0:N]
    r = np.hypot(x - N / 2, y - N / 2) / (N * 0.42)
    a = np.clip(1 - r, 0, 1) ** 1.6 * 0.38
    capa = np.zeros((N, N, 4), np.uint8)
    capa[..., 0], capa[..., 1], capa[..., 2] = 30, 90, 140
    capa[..., 3] = (a * 255).astype(np.uint8)
    return Image.alpha_composite(im, Image.fromarray(capa))


def arcos(radio_frac=0.385, ancho_frac=0.03, hueco=11):
    """Tres arcos (PIL: ángulos en grados, 0 = derecha, sentido horario)."""
    capa = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    R, w = N * radio_frac, int(N * ancho_frac)
    caja = [N / 2 - R, N / 2 - R, N / 2 + R, N / 2 + R]
    # azul arriba a la izquierda, amarillo arriba a la derecha, rosa abajo (como el avatar actual)
    for ini, col in ((150, AZUL), (270, AMARILLO), (30, ROSA)):
        d.arc(caja, ini + hueco, ini + 120 - hueco, fill=col + (255,), width=w)
    return capa


def avion(lado):
    r = A.Avion3DReal(1600, 1600, 2, campo=42, colores_mando=True)
    im = Image.fromarray(r.imagen(azimut=-145, elevacion=50, alabeo=22, cabeceo=8))
    im = im.crop(im.getbbox())
    k = lado / max(im.size)
    return im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)


def sombra(im, desp=(0.012, 0.02), radio=0.012, opac=0.55):
    a = im.split()[3].point(lambda v: int(v * opac))
    s = Image.new("RGBA", im.size, (0, 0, 0, 0))
    s.putalpha(a)
    s = s.filter(ImageFilter.GaussianBlur(N * radio))
    return s, (int(N * desp[0]), int(N * desp[1]))


def componer(variante):
    im = fondo()
    if variante == "anillo":
        im = Image.alpha_composite(im, arcos())
        pl = avion(int(N * 0.6))
    else:   # «sale»: el avión pasa por delante del anillo
        im = Image.alpha_composite(im, arcos(0.37, 0.03))
        pl = avion(int(N * 0.72))
    pos = ((N - pl.width) // 2, (N - pl.height) // 2)
    s, d = sombra(pl)
    im.alpha_composite(s, (pos[0] + d[0], pos[1] + d[1]))
    im.alpha_composite(pl, pos)
    return im


if __name__ == "__main__":
    variantes = sys.argv[1:] or ["anillo", "sale"]
    out = Path(__file__).parent
    for v in variantes:
        im = componer(v).convert("RGB")
        im.resize((1600, 1600), Image.LANCZOS).save(out / f"avatar3d_{v}_1600.png")
        im.resize((800, 800), Image.LANCZOS).save(out / f"avatar3d_{v}.png")
        print("ok", v)

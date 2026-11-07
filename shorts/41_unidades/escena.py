"""
Short 41 (ficha): las unidades de la aviación y su equivalencia en el SI. Imagen fija sin voz.
1 kt = 1,852 km/h ≈ 0,514 m/s · 1 ft = 0,3048 m · 1 NM = 1852 m · FL350 = 35 000 ft ≈ 10 670 m
1000 ft/min ≈ 5,08 m/s · 1013,25 hPa = 29,92 inHg (atmósfera estándar a nivel del mar).
Render de la imagen:  manim -qh -s shorts/41_unidades/escena.py Unidades
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403
from lib import avion as A  # noqa: E402
from lib.avion2d import _parche_manim_imagenes  # noqa: E402

FILAS = [
    ("kt", "Nudo", "velocidad", "1 kt = 1,852 km/h ≈ 0,514 m/s", C_CABECEO),
    ("ft", "Pie", "altitud", "1 ft = 0,3048 m", C_GUINADA),
    ("NM", "Milla náutica", "distancia", "1 NM = 1852 m", C_ALABEO),
    ("FL", "Nivel de vuelo", "centenas de pies", "FL350 = 35 000 ft ≈ 10 670 m", "#34D399"),
    ("ft/min", "Velocidad vertical", "sube o baja", "1000 ft/min ≈ 5,08 m/s", "#A78BFA"),
    ("hPa", "Presión", "ajuste del altímetro", "1013,25 hPa = 29,92 inHg", "#F97316"),
]


class Unidades(ShortBase):
    def construct(self):
        _parche_manim_imagenes()
        self.add(rejilla())
        y0, h = 2.75, 1.3
        filas = VGroup()
        for i, (sim, nombre, uso, eq, col) in enumerate(FILAS):
            y = y0 - i * h
            fondo = RoundedRectangle(width=8.8, height=h - 0.16, corner_radius=0.22, fill_color="#111827",
                                     fill_opacity=0.92, stroke_color=col, stroke_width=2).move_to([0, y, 0])
            chip = RoundedRectangle(width=1.75, height=h - 0.42, corner_radius=0.18, fill_color=col,
                                    fill_opacity=1, stroke_width=0).move_to([-3.35, y, 0])
            s = T(sim, size=40, color=BG, weight=HEAVY, font=F_TIT).move_to(chip)
            if s.width > 1.5:
                s.scale_to_fit_width(1.5)
            n = T(nombre, size=27, color=TEXTO, weight=HEAVY)
            u = T(uso, size=19, color=TEXTO_SEC, weight=MEDIUM)
            e = T(eq, size=24, color=col, weight=BOLD)
            if e.width > 6.2:
                e.scale_to_fit_width(6.2)
            linea1 = VGroup(n, u).arrange(RIGHT, buff=0.22, aligned_edge=DOWN)
            bloque = VGroup(linea1, e).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
            bloque.move_to([-2.25, y, 0], aligned_edge=LEFT)
            filas.add(fondo, chip, s, bloque)
        # avión 3D de lado, pequeño, como sello de la ficha
        r = A.Avion3DReal(1200, 560, 2, campo=50, colores_mando=False)
        im = ImageMobject(r.imagen(azimut=-90, elevacion=6)).scale_to_fit_width(4.6).move_to([2.3, 4.05, 0])
        sup = T("NUDOS, PIES, MILLAS…", size=30, color=TEXTO_SEC, weight=SEMIBOLD)
        tit = VGroup(T("UNIDADES", size=74, weight=HEAVY, font=F_TIT),
                     T("DE LA AVIACIÓN", size=44, weight=HEAVY, font=F_TIT, color=C_CABECEO)).arrange(DOWN, buff=0.06,
                                                                                                aligned_edge=LEFT)
        cab = VGroup(sup, tit).arrange(DOWN, buff=0.12, aligned_edge=LEFT).move_to([-1.6, 4.55, 0])
        nota = T("La OACI admite estas unidades junto al SI", size=20, color=TEXTO_SEC,
                 weight=MEDIUM).move_to(DOWN * 4.4)
        pie = T("@porquevuela · Guárdalo", size=26, color=TEXTO_SEC, weight=SEMIBOLD).move_to(DOWN * 5.6)
        reto = T("¿A cuántos metros vuela un avión en FL390? Comenta ↓", size=28, color=C_CABECEO, weight=HEAVY).move_to(DOWN * 5.0)
        if reto.width > 8.4:
            reto.scale_to_fit_width(8.4)
        self.add(brillo([0, 0.0, 0], C_CABECEO, 4.6, 0.5), filas, im, cab, nota, reto, pie)
        self.wait(0.1)

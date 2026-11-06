"""
Short 12 (ficha): alfabeto aeronáutico (alfabeto de deletreo de la OACI).
Grafía oficial de la OACI: "Alfa" y "Juliett". Imagen fija sin voz; solo música.
Avión 3D de lado con la matrícula de ejemplo XA-ABC pintada en el fuselaje trasero.
Render de la imagen:  manim -qh -s shorts/12_alfabeto/escena.py Alfabeto
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403
from lib import avion as A  # noqa: E402
from lib.avion2d import _parche_manim_imagenes  # noqa: E402

PALABRAS = ["Alfa", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf", "Hotel", "India",
            "Juliett", "Kilo", "Lima", "Mike", "November", "Oscar", "Papa", "Quebec", "Romeo",
            "Sierra", "Tango", "Uniform", "Victor", "Whiskey", "X-ray", "Yankee", "Zulu"]
COLORES = [C_CABECEO, C_ALABEO, C_GUINADA]
FILA = 0.56


def entrada(palabra, color):
    letra = T(palabra[0], size=44, color=color, weight=HEAVY, font=F_TIT)
    caja = RoundedRectangle(width=0.62, height=0.56, corner_radius=0.14, fill_color=color,
                            fill_opacity=0.14, stroke_color=color, stroke_width=2)
    letra.scale_to_fit_height(0.34)
    if letra.width > 0.44:
        letra.scale_to_fit_width(0.44)
    letra.move_to(caja)
    pal = T(palabra, size=36, weight=BOLD).next_to(caja, RIGHT, buff=0.22)
    alto_mayus = T("H", size=36, weight=BOLD).height          # alinear por la línea base
    pal.shift(UP * (caja.get_center()[1] + alto_mayus / 2 - pal.get_top()[1]))
    return VGroup(caja, letra, pal)


class Alfabeto(ShortBase):
    def construct(self):
        self.add(rejilla())
        sup = T("CÓMO SE DELETREA POR RADIO", size=30, color=TEXTO_SEC, weight=SEMIBOLD)
        tit = T("ALFABETO AERONÁUTICO", size=64, weight=HEAVY, font=F_TIT)
        cab = VGroup(sup, tit).arrange(DOWN, buff=0.12).move_to(UP * 5.5)
        cols = VGroup()
        for c in range(2):
            col = VGroup()
            for i in range(13):
                e = entrada(PALABRAS[13 * c + i], COLORES[(13 * c + i) % 3])
                e.shift([-3.3 + 3.75 * c - e[0].get_center()[0], 4.0 - i * FILA - e[0].get_center()[1], 0])
                col.add(e)
            cols.add(col)
        cols.move_to(UP * 1.1)
        # avión 3D de lado con la matrícula pintada en la cola (ejemplo)
        _parche_manim_imagenes()
        W, H, ANCHO = 1400, 560, 7.6
        r = A.Avion3DReal(W, H, 2, campo=23, colores_mando=False)
        vista = dict(azimut=-90, elevacion=6, cabeceo=3)
        av = ImageMobject(r.imagen(**vista)).scale_to_fit_width(ANCHO)
        Y_AV = -3.8
        av.move_to([0, Y_AV, 0])
        k = ANCHO / W

        def pant(X, Z):
            px = r.proyectar([A.a_cuerpo(X, 0, Z)], **vista)[0]
            return np.array([(px[0] - W / 2) * k, (H / 2 - px[1]) * k + Y_AV, 0])
        mat = T("XA-ABC", size=17, color="#1E293B", weight=HEAVY, font=F_TIT)
        mat.move_to(pant(29.0, 0.55))
        mat.rotate(3 * DEGREES)
        ej_t = T("XA-ABC se dice:", size=26, color=TEXTO_SEC, weight=SEMIBOLD)
        ej = T("X-ray Alfa – Alfa Bravo Charlie", size=34, color=C_GUINADA, weight=HEAVY)
        pie = T("@porquevuela · Guárdalo y practica tu nombre", size=24, color=TEXTO_SEC,
                weight=SEMIBOLD)
        abajo = VGroup(VGroup(ej_t, ej).arrange(DOWN, buff=0.08), pie).arrange(DOWN, buff=0.25)
        abajo.move_to(DOWN * 5.25)
        self.portada(cab, cols, av, mat, abajo)
        self.wait(0.1)

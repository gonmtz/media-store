"""
Short 14 (ficha): las partes de un avión, sobre el avión 3D (lib/avion.py).
Imagen fija sin voz; solo música. Mandos en los colores de cada giro (alerón = alabeo,
elevador = cabeceo, timón = guiñada), como en el short 01.
Render de la imagen:  manim -qh -s shorts/14_partes/escena.py Partes
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403
from lib import avion as A  # noqa: E402
from lib.avion2d import _parche_manim_imagenes  # noqa: E402

CENTRO = np.array([0.3, -0.5, 0])
VISTA = dict(azimut=-38, elevacion=24, campo=40)


def _estab(yy, xc):
    e = A.ESTAB
    u = (yy - e["y_raiz"]) / (e["y_punta"] - e["y_raiz"])
    cu = e["cuerda_raiz"] + (e["cuerda_punta"] - e["cuerda_raiz"]) * u
    X = e["x_ba_raiz"] + (yy - e["y_raiz"]) * np.tan(np.radians(e["flecha"])) + xc * cu
    z = e["z_raiz"] + (yy - e["y_raiz"]) * np.tan(np.radians(e["diedro"]))
    return A.a_cuerpo(X, -yy, z)


X0, CM, *_ = A.datos_motor(-1)
# (texto, punto del avión, posición del rótulo en pantalla, color)
PARTES = [
    ("Timón", A.a_cuerpo(34.6, 0, 4.6), (-3.35, 3.25), C_GUINADA),
    ("Deriva", A.a_cuerpo(31.6, 0, 4.3), (-0.75, 3.25), TEXTO),
    ("Estabilizador horizontal", _estab(3.3, 0.3), (-1.75, 2.3), TEXTO),
    ("Elevador", _estab(4.6, 0.85), (-3.45, 1.35), C_CABECEO),
    ("Fuselaje", A.a_cuerpo(*A.punto_fuselaje(13.0, np.pi - 0.5)), (2.55, 1.6), TEXTO),
    ("Cabina de mando", A.a_cuerpo(*A.punto_fuselaje(3.9, np.pi - np.radians(55))), (2.7, 0.15), TEXTO),
    ("Winglet", A.punto_ala(17.2, -1, 0.4, dz=1.0), (-3.4, -2.75), TEXTO),
    ("Alerón", A.punto_ala(13.9, -1, 0.88), (-2.45, -3.6), C_ALABEO),
    ("Ala", A.punto_ala(9.5, -1, 0.35), (-1.45, -2.75), TEXTO),
    ("Flaps", A.punto_ala(6.0, -1, 0.88), (-0.6, -3.6), TEXTO),
    ("Pilón", A.a_cuerpo(X0 + 3.4, CM[0], CM[1] + 1.15), (0.45, -2.75), TEXTO),
    ("Motor", A.a_cuerpo(X0 + 1.0, CM[0], CM[1]), (1.55, -3.6), TEXTO),
]


class Partes(ShortBase):
    def construct(self):
        _parche_manim_imagenes()
        self.add(rejilla())
        r = A.Avion3DReal(1200, 1200, 2, campo=VISTA["campo"], colores_mando=True)
        img = r.imagen(**VISTA)
        ancho = 9.6
        im = ImageMobject(img).scale_to_fit_width(ancho).move_to(CENTRO)
        k = ancho / r.ancho
        px = r.proyectar(np.array([p for _, p, _, _ in PARTES]), **VISTA)
        pts = [np.array([(x - r.ancho / 2) * k, (r.alto / 2 - y) * k, 0]) + CENTRO for x, y in px]
        sup = T("¿CÓMO SE LLAMA CADA PARTE?", size=30, color=TEXTO_SEC, weight=SEMIBOLD)
        tit = T("PARTES DE UN AVIÓN", size=72, weight=HEAVY, font=F_TIT)
        cab = VGroup(sup, tit).arrange(DOWN, buff=0.12).move_to(UP * 5.2)
        rot = VGroup()
        for (texto, _, pos, col), p in zip(PARTES, pts):
            t = T(texto, size=23, color=col, weight=BOLD)
            fondo = RoundedRectangle(width=t.width + 0.34, height=t.height + 0.24,
                                     corner_radius=0.13, fill_color=PANEL, fill_opacity=0.95,
                                     stroke_color=col if col != TEXTO else BORDE, stroke_width=1.5)
            etq = VGroup(fondo, t.move_to(fondo)).move_to([*pos, 0])
            borde = etq.get_critical_point(np.sign(p - etq.get_center()) * np.array([0, 1, 0])
                                           if abs(p[1] - pos[1]) > abs(p[0] - pos[0]) * 0.6
                                           else np.sign(p - etq.get_center()) * np.array([1, 0, 0]))
            linea = Line(borde, p, color=col if col != TEXTO else "#94A3B8", stroke_width=2)
            rot.add(VGroup(linea, Dot(p, radius=0.05, color=col if col != TEXTO else WHITE), etq))
        pie = T("@porquevuela · Guárdalo", size=26, color=TEXTO_SEC, weight=SEMIBOLD)
        pie.move_to(DOWN * 5.0)
        self.add(brillo(CENTRO, C_CABECEO, 4.6, 0.8), im, rot, cab, pie)
        self.wait(0.1)

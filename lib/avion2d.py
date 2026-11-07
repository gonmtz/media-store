"""
Vistas 2D vectoriales del avión de `lib/avion.py` (la misma geometría que el 3D): lateral,
superior y frontal. Cada función devuelve un objeto `Vista` (VGroup) con las piezas con
nombre en `vista.partes` y la conversión de metros a pantalla en `vista.a_pantalla(X, Y, Z)`
(para colocar flechas, etiquetas o descargadores exactamente sobre el dibujo).

Escala: `ancho` = unidades de pantalla que ocupa el largo (lateral, superior) o la envergadura
(frontal). Los mandos (alerones, elevador, timón) pueden ir en sus colores (`colores_mando`).
"""
import numpy as np
from manim import VGroup, VMobject, Polygon, Line, Dot, Ellipse, Circle, RoundedRectangle
from scipy.spatial import ConvexHull

from lib import avion as A

BORDE = "#64748B"
SOMBRA = "#A7B3C2"


def _vm(puntos, relleno, opacidad=1.0, borde=BORDE, ancho_borde=1.2, suave=False,
        degradado=None, sheen=None):
    v = VMobject()
    pts = [np.array([p[0], p[1], 0.0]) for p in puntos]
    if suave:
        v.set_points_smoothly(pts + [pts[0]])
    else:
        v.set_points_as_corners(pts + [pts[0]])
    if degradado:
        v.set_fill(color=list(degradado), opacity=opacidad)
        if sheen is not None:
            v.set_sheen_direction(sheen)
    else:
        v.set_fill(relleno, opacity=opacidad)
    v.set_stroke(borde, width=ancho_borde, opacity=0.9 if ancho_borde else 0)
    return v


def _casco(P):
    P = np.asarray(P)[:, :2]
    h = ConvexHull(P)
    return P[h.vertices]


class Vista(VGroup):
    def __init__(self, a_pantalla, **kw):
        super().__init__(**kw)
        self.partes = {}
        self.a_pantalla = a_pantalla

    def pieza(self, nombre, mob):
        self.partes[nombre] = mob
        self.add(mob)
        return mob


def _piezas(nombre):
    """Piezas por nombre. «ala» incluye flaps, slats y spoilers; «gondola», el capó trasero."""
    grupo = {"ala": ("ala", "flap", "slat", "spoiler"), "gondola": ("gondola", "reversa")}
    nombres = grupo.get(nombre, (nombre,))
    return [m for m in A.mallas_avion() if m.nombre in nombres]


def _union(ms, cols):
    """Casco convexo de varias piezas juntas, en las columnas `cols` (p. ej. [0, 2] = X, Z)."""
    return _casco(np.vstack([m.v[:, cols] for m in ms]))


def _lado(ms, s):
    return [m for m in ms if np.sign(np.mean(m.v[:, 1])) == s]


def _color_mando(n, colores_mando):
    if not colores_mando:
        return None
    return {"aleron": A.ROSA, "elevador": A.AZUL, "timon": A.AMARILLO}[n]


# ---------------------------------------------------------------- vista lateral
def lateral_2d(ancho=7.6, centro=(0, 0), colores_mando=False, lado=1, tren=False):
    """Vista de lado, morro a la derecha (se ve el lado izquierdo del avión con lado=1).
    `tren=True` dibuja el tren de aterrizaje fuera (ruedas apoyadas en Z = A.Z_SUELO)."""
    k = ancho / A.L
    cx, cy = centro

    def P(X, Z):
        return ((A.X_CG - X) * k + cx, Z * k + cy)
    vista = Vista(lambda X, Y, Z: np.array([*P(X, Z), 0.0]))
    Xs = np.concatenate([np.linspace(0, 1.2, 25), np.linspace(1.25, A.L, 120)])
    if tren:
        t = A.TREN
        for X, r, z0 in ((t["x_principal"], t["r_principal"], -1.25), (t["x_morro"], t["r_morro"], -1.6)):
            ze = A.Z_SUELO + r
            pata = Line([*P(X, z0), 0], [*P(X, ze), 0], color="#94A3B8", stroke_width=5 * ancho / 7.6)
            rueda = Circle(radius=r * k).set_fill("#1F2937", 1).set_stroke("#475569", 1.5)
            llanta = Circle(radius=r * k * 0.5).set_fill("#CBD5E1", 1).set_stroke(width=0)
            vista.pieza("tren_morro" if X < 10 else "tren_principal",
                        VGroup(pata, rueda.move_to([*P(X, ze), 0]), llanta.move_to([*P(X, ze), 0])))

    def bordes(fz):
        return [P(X, fz(X)) for X in Xs]
    arriba = bordes(lambda X: A.seccion(X)[2] + A.seccion(X)[1])
    abajo = bordes(lambda X: A.seccion(X)[2] - A.seccion(X)[1])
    # deriva (una sola silueta) y timón encima
    vista.pieza("deriva", _vm([P(x, z) for x, z in _union(_piezas("deriva") + _piezas("timon"),
                                                          [0, 2])], A.BLANCO,
                              degradado=("#FFFFFF", "#CBD5E1"), sheen=np.array([-1, 0, 0])))
    col = _color_mando("timon", colores_mando)
    tim = _vm([P(x, z) for x, z in _union(_piezas("timon"), [0, 2])], col or A.BLANCO,
              opacidad=1 if col else 0, borde="#94A3B8", ancho_borde=1.0)
    vista.pieza("timon", tim)
    # fuselaje con degradado
    vista.pieza("fuselaje", _vm(arriba + abajo[::-1], A.BLANCO, suave=False,
                                degradado=("#FFFFFF", "#C9D2DE"), sheen=np.array([0, -1, 0])))
    # panza
    panza = [P(X, A.seccion(X)[2] - 0.62 * A.seccion(X)[1]) for X in Xs]
    vista.pieza("panza", _vm(panza + abajo[::-1], A.GRIS_PANZA, opacidad=0.9, ancho_borde=0))
    # brillo superior
    brillo = [P(X, A.seccion(X)[2] + 0.72 * A.seccion(X)[1]) for X in Xs[8:-15]]
    vista.pieza("brillo", VMobject().set_points_smoothly([np.array([*p, 0]) for p in brillo])
                .set_stroke("#FFFFFF", width=3, opacity=0.8))
    # línea azul
    Xl = np.linspace(6.0, 27.6, 60)
    z4 = [P(X, A.seccion(X)[2] + A.seccion(X)[1] * np.sin(np.radians(4.5))) for X in Xl]
    z7 = [P(X, A.seccion(X)[2] + A.seccion(X)[1] * np.sin(np.radians(7.5))) for X in Xl]
    vista.pieza("linea", _vm(z7 + z4[::-1], A.AZUL, ancho_borde=0))
    # ventanillas
    vent = VGroup()
    zs = np.radians(A.TH_VENTANILLA)
    for X in A.ventanillas_X():
        ry, rz, zc = A.seccion(X)
        h = rz * (np.sin(zs + np.radians(3.6)) - np.sin(zs - np.radians(3.6))) * k
        r = RoundedRectangle(width=0.2 * k, height=h, corner_radius=min(0.2 * k, h) * 0.45,
                             fill_color=A.OSCURO_VIDRIO, fill_opacity=1, stroke_width=0)
        vent.add(r.move_to([*P(X, zc + rz * np.sin(zs)), 0]))
    vista.pieza("ventanillas", vent)
    # puertas
    puertas = VGroup()
    for (X0, X1, t0, t1) in A.PUERTAS:
        pts = [P(X, A.seccion(X)[2] + A.seccion(X)[1] * np.sin(np.radians(t)))
               for X, t in ((X0, t0), (X1, t0), (X1, t1), (X0, t1))]
        puertas.add(_vm(pts, A.BLANCO, opacidad=0, borde="#94A3B8", ancho_borde=1.4))
    vista.pieza("puertas", puertas)
    # parabrisas (proyección exacta de los parches)
    cab = VGroup()
    for esq in A.PARABRISAS:
        pts = A.contorno_parabrisas(esq, espejo=lado < 0)
        cab.add(_vm([P(p[0], p[2]) for p in pts], A.OSCURO_VIDRIO, borde="#0B1220",
                    ancho_borde=0.8))
    vista.pieza("cabina", cab)
    # ala cercana (una silueta), winglet y alerón
    vista.pieza("winglet", _vm([P(x, z) for x, z in _union(_lado(_piezas("winglet"), lado),
                                                           [0, 2])], A.GRIS_ALA,
                               degradado=("#E8EDF3", "#AEB9C7"), sheen=np.array([-1, 0, 0])))
    vista.pieza("ala", _vm([P(x, z) for x, z in _union(_lado(_piezas("ala") + _piezas("aleron"),
                                                             lado), [0, 2])], A.GRIS_ALA,
                           degradado=("#EEF2F7", "#AEB9C7"), sheen=np.array([0, -1, 0])))
    col = _color_mando("aleron", colores_mando)
    if col:
        vista.pieza("aleron", _vm([P(x, z) for x, z in _union(_lado(_piezas("aleron"), lado),
                                                              [0, 2])], col, ancho_borde=0.8))
    # estabilizador cercano (una silueta) y elevador
    vista.pieza("estabilizador", _vm([P(x, z) for x, z in _union(
        _lado(_piezas("estabilizador") + _piezas("elevador"), lado), [0, 2])], A.BLANCO,
        degradado=("#FFFFFF", "#C3CCD8"), sheen=np.array([0, -1, 0])))
    col = _color_mando("elevador", colores_mando)
    vista.pieza("elevador", _vm([P(x, z) for x, z in _union(_lado(_piezas("elevador"), lado),
                                                            [0, 2])], col or A.BLANCO,
                                opacidad=1 if col else 0, borde="#94A3B8", ancho_borde=0.9))
    # motor cercano
    X0, c, Xba, z_inf, cu = A.datos_motor(lado)
    R = A.MOTOR["radio"]
    prof = [(0.0, 0.84), (0.03, 0.93), (0.12, 0.985), (0.35, 1.0), (1.4, 1.0), (2.6, 0.95),
            (3.6, 0.8), (4.4, 0.6)]
    pilon_m = [m for m in _lado(_piezas("pilon"), lado)][0]
    vista.pieza("pilon", _vm([P(x, z) for x, z in _casco(pilon_m.v[:, [0, 2]])], A.GRIS_MOTOR,
                             ancho_borde=1.0))
    sup = [P(X0 + dx, c[1] + r * R) for dx, r in prof]
    inf = [P(X0 + dx, c[1] - r * R) for dx, r in prof]
    vista.pieza("gondola", _vm(sup + inf[::-1], A.GRIS_MOTOR, suave=False,
                               degradado=("#EEF2F7", "#9AA7B8"), sheen=np.array([0, -1, 0])))
    esc = [P(X0 + 4.3, c[1] + 0.47 * R), P(X0 + 4.9, c[1] + 0.3 * R), P(X0 + 5.3, c[1]),
           P(X0 + 4.9, c[1] - 0.3 * R), P(X0 + 4.3, c[1] - 0.47 * R)]
    vista.pieza("escape", _vm(esc, "#94A3B8", ancho_borde=0.8))
    lab = Ellipse(width=0.16 * k, height=1.68 * R * k, fill_color="#94A3B8", fill_opacity=1,
                  stroke_color=BORDE, stroke_width=1).move_to([*P(X0, c[1]), 0])
    vista.pieza("labio", lab)
    # luces: navegación (roja a la izquierda / verde a la derecha), cola blanca, anticolisión
    Xp, Zp, _ = A.geometria_ala_en(A.ALA["y_punta"], 0.15)
    luces = VGroup(_luz(P(A.L, 1.0), "#FFFFFF", k),
                   _luz(P(16.0, A.R_Z), A.ROJA, k * 0.8))
    vista.pieza("luces", luces)
    return vista


def _luz(p, color, k, r=0.16):
    return VGroup(Dot([*p, 0], radius=r * k * 3.2, color=color).set_opacity(0.2),
                  Dot([*p, 0], radius=r * k * 1.7, color=color).set_opacity(0.4),
                  Dot([*p, 0], radius=r * k, color=color))


# ---------------------------------------------------------------- vista superior
def superior_2d(ancho=7.6, centro=(0, 0), colores_mando=False):
    """Vista desde arriba, morro hacia arriba; `ancho` = envergadura en pantalla."""
    k = ancho / (2 * (A.ALA["y_punta"] + 0.5))
    cx, cy = centro

    def P(X, Y):
        return (-Y * k + cx, (A.X_CG - X) * k + cy)
    vista = Vista(lambda X, Y, Z: np.array([*P(X, Y), 0.0]))
    # motores (debajo del ala: se dibujan primero)
    for s in (1, -1):
        X0, c, *_ = A.datos_motor(s)
        R = A.MOTOR["radio"]
        prof = [(0.0, 0.84), (0.12, 0.985), (0.35, 1.0), (1.4, 1.0), (2.6, 0.95), (3.6, 0.8),
                (4.4, 0.6)]
        izq = [P(X0 + dx, c[0] + r * R) for dx, r in prof]
        der = [P(X0 + dx, c[0] - r * R) for dx, r in prof]
        vista.pieza(f"motor{s}", _vm(izq + der[::-1], A.GRIS_MOTOR,
                                     degradado=("#EEF2F7", "#9AA7B8"), sheen=np.array([s, 0, 0])))
    # alas (una silueta por lado), alerones, flaps (línea) y winglets
    for s in (1, -1):
        ala = _lado(_piezas("ala") + _piezas("aleron"), s)
        vista.pieza(f"ala{s}", _vm([P(x, y) for x, y in _union(ala, [0, 1])], A.GRIS_ALA,
                                   degradado=("#EEF2F7", "#B3BECC"), sheen=np.array([s, 0, 0])))
        col = _color_mando("aleron", colores_mando)
        vista.pieza(f"aleron{s}", _vm([P(x, y) for x, y in _union(_lado(_piezas("aleron"), s),
                                                                  [0, 1])], col or A.GRIS_ALA,
                                      opacidad=1 if col else 0, borde="#94A3B8", ancho_borde=1.0))
        y0 = A.ALA["y_raiz"] + 0.3
        y1 = A.ALA["aleron"][0] - 0.1
        fl = [A.geometria_ala_en(y, 0.78) for y in (y0, y1)]
        vista.pieza(f"flap{s}", Line([*P(fl[0][0], s * y0), 0], [*P(fl[1][0], s * y1), 0],
                                     color="#94A3B8", stroke_width=1.2))
        vista.pieza(f"winglet{s}", _vm([P(x, y) for x, y in _union(_lado(_piezas("winglet"), s),
                                                                   [0, 1])], A.GRIS_ALA,
                                       ancho_borde=1.0))
    # estabilizadores (una silueta por lado) y elevadores
    for s in (1, -1):
        est = _lado(_piezas("estabilizador") + _piezas("elevador"), s)
        vista.pieza(f"estab{s}", _vm([P(x, y) for x, y in _union(est, [0, 1])], A.BLANCO,
                                     degradado=("#FFFFFF", "#C3CCD8"), sheen=np.array([s, 0, 0])))
        col = _color_mando("elevador", colores_mando)
        vista.pieza(f"elevador{s}", _vm([P(x, y) for x, y in _union(_lado(_piezas("elevador"), s),
                                                                    [0, 1])], col or A.BLANCO,
                                        opacidad=1 if col else 0, borde="#94A3B8",
                                        ancho_borde=0.9))
    # fuselaje
    Xs = np.concatenate([np.linspace(0, 1.2, 25), np.linspace(1.25, A.L, 120)])
    izq = [P(X, A.seccion(X)[0]) for X in Xs]
    der = [P(X, -A.seccion(X)[0]) for X in Xs]
    vista.pieza("fuselaje", _vm(izq + der[::-1], A.BLANCO,
                                degradado=("#FFFFFF", "#C9D2DE"), sheen=np.array([1, 0, 0])))
    lomo = VMobject().set_points_smoothly([np.array([*P(X, 0.25), 0]) for X in Xs[10:-12]])
    vista.pieza("brillo", lomo.set_stroke("#FFFFFF", width=4, opacity=0.8))
    # deriva vista desde arriba
    vista.pieza("deriva", _vm([P(x, y) for x, y in _union(_piezas("deriva") + _piezas("timon"),
                                                          [0, 1])], "#E2E8F0", ancho_borde=0.8))
    # parabrisas desde arriba
    cab = VGroup()
    for s in (1, -1):
        for esq in A.PARABRISAS:
            pts = A.contorno_parabrisas(esq, espejo=s < 0)
            cab.add(_vm([P(p[0], p[1]) for p in pts], A.OSCURO_VIDRIO, borde="#0B1220",
                        ancho_borde=0.6))
    vista.pieza("cabina", cab)
    Xp, _, _ = A.geometria_ala_en(A.ALA["y_punta"], 0.15)
    vista.pieza("luces", VGroup(_luz(P(Xp, A.ALA["y_punta"] + 0.1), A.ROJA, k),
                                _luz(P(Xp, -A.ALA["y_punta"] - 0.1), A.VERDE, k),
                                _luz(P(A.L, 0), "#FFFFFF", k)))
    return vista


# ---------------------------------------------------------------- vista frontal
def frontal_2d(ancho=7.6, centro=(0, 0), colores_mando=False):
    """Vista de frente (el ala izquierda del avión queda a la DERECHA de la pantalla)."""
    k = ancho / (2 * (A.ALA["y_punta"] + 0.6))
    cx, cy = centro

    def P(Y, Z):
        return (Y * k + cx, Z * k + cy)
    vista = Vista(lambda X, Y, Z: np.array([*P(Y, Z), 0.0]))
    vista.pieza("deriva", _vm([P(y, z) for y, z in _union(_piezas("deriva") + _piezas("timon"),
                                                          [1, 2])], "#CBD5E1", ancho_borde=0.8))
    for s in (1, -1):
        vista.pieza(f"estab{s}", _vm([P(y, z) for y, z in _union(
            _lado(_piezas("estabilizador") + _piezas("elevador"), s), [1, 2])], "#CBD5E1",
            ancho_borde=0.8))
        vista.pieza(f"ala{s}", _vm([P(y, z) for y, z in _union(
            _lado(_piezas("ala") + _piezas("aleron"), s), [1, 2])], A.GRIS_ALA,
            degradado=("#F1F5F9", "#A9B5C4"), sheen=np.array([0, -1, 0])))
        vista.pieza(f"winglet{s}", _vm([P(y, z) for y, z in _union(_lado(_piezas("winglet"), s),
                                                                   [1, 2])], A.GRIS_ALA,
                                       degradado=("#F1F5F9", "#A9B5C4"), ancho_borde=0.9))
    # fuselaje: sección máxima
    fus = Ellipse(width=2 * A.R_Y * k, height=2 * A.R_Z * k).move_to([*P(0, 0), 0])
    fus.set_fill(color=["#FFFFFF", "#BCC6D3"], opacity=1).set_sheen_direction(np.array([0, -1, 0]))
    vista.pieza("fuselaje", fus.set_stroke(BORDE, width=1.2))
    panza = Ellipse(width=2 * A.R_Y * k * 0.78, height=2 * A.R_Z * k * 0.3,
                    fill_color=A.GRIS_PANZA, fill_opacity=0.6, stroke_width=0)
    vista.pieza("panza", panza.move_to([*P(0, -A.R_Z * 0.8), 0]))
    morro = Ellipse(width=1.2 * A.R_Y * k, height=1.0 * A.R_Z * k, fill_color="#FFFFFF",
                    fill_opacity=0.55, stroke_width=0).move_to([*P(0, -0.45), 0])
    vista.pieza("morro", morro)
    cab = VGroup()
    for s in (1, -1):
        for esq in A.PARABRISAS[:2]:
            pts = A.contorno_parabrisas(esq, espejo=s < 0)
            cab.add(_vm([P(p[1], p[2]) for p in pts], A.OSCURO_VIDRIO, borde="#0B1220",
                        ancho_borde=0.6))
    vista.pieza("cabina", cab)
    # motores
    for s in (1, -1):
        X0, c, Xba, z_inf, cu = A.datos_motor(s)
        R = A.MOTOR["radio"]
        centro_m = np.array([*P(c[0], c[1]), 0])
        pil = [m for m in _lado(_piezas("pilon"), s)][0]
        vista.pieza(f"pilon{s}", _vm([P(y, z) for y, z in _casco(pil.v[:, [1, 2]])], A.GRIS_MOTOR,
                                     ancho_borde=0.8))
        g = VGroup(
            Circle(radius=R * k).set_fill(color=["#F1F5F9", "#94A3B8"], opacity=1)
            .set_sheen_direction(np.array([0, -1, 0])).set_stroke(BORDE, width=1.2),
            Circle(radius=0.84 * R * k, fill_color="#94A3B8", fill_opacity=1, stroke_width=0),
            Circle(radius=0.78 * R * k, fill_color=A.OSCURO, fill_opacity=1, stroke_width=0))
        g.move_to(centro_m)
        alabes = VGroup(*[Line(centro_m + 0.3 * k * np.array([np.cos(a), np.sin(a), 0]),
                               centro_m + 0.77 * R * k * np.array([np.cos(a + 0.12), np.sin(a + 0.12), 0]),
                               color="#64748B", stroke_width=1.4)
                          for a in np.linspace(0, 2 * np.pi, 22, endpoint=False)])
        cono = Circle(radius=0.28 * k).set_fill(color=["#FFFFFF", "#94A3B8"], opacity=1) \
            .set_sheen_direction(np.array([-1, -1, 0])).set_stroke(width=0).move_to(centro_m)
        vista.pieza(f"motor{s}", VGroup(g, alabes, cono))
    Xp, Zp, _ = A.geometria_ala_en(A.ALA["y_punta"], 0.15)
    vista.pieza("luces", VGroup(_luz(P(A.ALA["y_punta"] + 0.1, Zp), A.ROJA, k),
                                _luz(P(-A.ALA["y_punta"] - 0.1, Zp), A.VERDE, k)))
    return vista


# ---------------------------------------------------------------- 3D real dentro de Manim
def _parche_manim_imagenes():
    """Manim 0.22 + Pillow reciente: `Camera.display_image_mobject` crea el lienzo con
    `Image.fromarray(np.zeros((h, w)), mode="RGBA")`, que Pillow ya no acepta. Se reemplaza
    esa línea por `Image.new` (mismo resultado)."""
    import inspect
    import textwrap
    from manim.camera import camera as cam_mod
    f = cam_mod.Camera.display_image_mobject
    if getattr(f, "_parcheado", False):
        return
    src = textwrap.dedent(inspect.getsource(f))
    viejo = """Image.fromarray(
        np.zeros((self.pixel_height, self.pixel_width)),
        mode="RGBA",
    )"""
    if viejo not in src:
        return
    src = src.replace(viejo, 'Image.new("RGBA", (self.pixel_width, self.pixel_height))')
    ns = {}
    exec(compile("from __future__ import annotations\n" + src, cam_mod.__file__, "exec"),
         cam_mod.__dict__, ns)
    nueva = ns["display_image_mobject"]
    nueva._parcheado = True
    cam_mod.Camera.display_image_mobject = nueva


def capa_3d(render, ancho_pantalla=9.0, centro=(0, 0), **params):
    """Capa que redibuja el render 3D en cada fotograma. Cada parámetro de
    `Avion3DReal.imagen` puede ser un número, un ValueTracker (p. ej. azimut=ValueTracker(0))
    o una función sin argumentos (p. ej. mirar=lambda: (x.get_value(), 0, 0)). `centro` también
    puede ser una función (el avión se desplaza por la pantalla).
    Si no cambia ningún parámetro, reutiliza la última imagen."""
    from manim import ImageMobject, always_redraw, ValueTracker, RESAMPLING_ALGORITHMS, config
    config.disable_caching = True     # el hash de Manim no sabe serializar el renderizador
    _parche_manim_imagenes()
    cache = {}

    def _centro():
        """`centro` puede ser una tupla o una función sin argumentos (avión que se desplaza)."""
        return centro() if callable(centro) else centro

    def valores():
        return {k: (v.get_value() if isinstance(v, ValueTracker) else v() if callable(v) else v)
                for k, v in params.items()}

    def dibujar():
        val = valores()
        clave = tuple(sorted((k, round(float(np.asarray(v).sum()), 4)) for k, v in val.items()))
        if cache.get("clave") != clave:
            cache["clave"], cache["img"] = clave, render.imagen(**val)
        im = ImageMobject(cache["img"])
        im.set_resampling_algorithm(RESAMPLING_ALGORITHMS["bilinear"])
        c = _centro()
        return im.scale_to_fit_width(ancho_pantalla).move_to([c[0], c[1], 0])
    capa = always_redraw(dibujar)

    def a_pantalla(puntos, en_ala=False):
        """Coordenadas de Manim de puntos del avión (metros, ejes del avión) con los
        parámetros actuales: para poner flechas, halos o rótulos sobre el render."""
        px = render.proyectar(puntos, en_ala=en_ala, **valores())
        k = ancho_pantalla / render.ancho
        c = _centro()
        x = (px[:, 0] - render.ancho / 2) * k + c[0]
        y = (render.alto / 2 - px[:, 1]) * k + c[1]
        return np.column_stack([x, y, np.zeros(len(x))])
    capa.a_pantalla = a_pantalla
    capa.valores = valores
    return capa

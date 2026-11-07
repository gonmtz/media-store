"""
Piezas comunes de la serie «modos dinámicos» (shorts 23–27, narrados).
Disposición fija: avión arriba (y ≈ 1,9), gráfica respuesta–tiempo abajo (y ≈ −0,6), HUD con
título/frase/dato y subtítulos en SUB_Y. Un reloj de simulación (ValueTracker) mueve a la vez el
avión y la traza de la gráfica, así nunca hay más de 3 s sin movimiento.
"""
import numpy as np
from manim import (VGroup, ValueTracker, Axes, Dot, Line, Arrow, DashedLine, RoundedRectangle,
                   always_redraw, linear, DEGREES, PI, ORIGIN, UP, DOWN, LEFT, RIGHT, FadeIn)

from lib.porquevuela import (ShortBase, T, F_TIT, HEAVY, BOLD, MEDIUM, BG, TEXTO, TEXTO_SEC,
                             brillo, frase_cinetica)
from lib.avion2d import lateral_2d, superior_2d, frontal_2d, capa_3d
from lib import avion as A

Y_AV, Y_GR = 1.75, -0.8


def flecha(p0, p1, color, ancho=9, punta=0.3):
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    if np.linalg.norm(p1 - p0) < 0.05:
        return VGroup()
    return Arrow(p0, p1, buff=0, color=color, stroke_width=ancho,
                 max_tip_length_to_length_ratio=min(0.45, punta / max(np.linalg.norm(p1 - p0), 1e-3)),
                 max_stroke_width_to_length_ratio=20)


class ModoBase(ShortBase):
    SUBS_DESDE = "b1"
    SIN_SUBS_DESDE = "cierre"

    # ---------- vistas del avión que siguen funciones del reloj ----------
    def lateral(self, ancho, centro, cabeceo=lambda: 0.0, dy=lambda: 0.0, **kw):
        base = lateral_2d(ancho, (0, 0), **kw)
        c = np.array([*centro, 0.0])
        return always_redraw(lambda: base.copy().rotate(cabeceo() * DEGREES, about_point=ORIGIN)
                             .shift(c + UP * dy()))

    def frontal(self, ancho, centro, alabeo=lambda: 0.0, **kw):
        base = frontal_2d(ancho, (0, 0), **kw)
        c = np.array([*centro, 0.0])
        # visto de frente (el avión viene hacia nosotros): alabeo a la derecha (+) baja el ala
        # derecha del avión, que en pantalla está a la izquierda → giro antihorario en pantalla
        return always_redraw(lambda: base.copy().rotate(alabeo() * DEGREES, about_point=ORIGIN).shift(c))

    def superior(self, ancho, centro, guinada=lambda: 0.0, **kw):
        base = superior_2d(ancho, (0, 0), **kw)
        c = np.array([*centro, 0.0])
        # visto desde arriba con el morro hacia arriba: guiñada a la derecha (+) = giro horario
        return always_redraw(lambda: base.copy().rotate(-guinada() * DEGREES, about_point=ORIGIN).shift(c))

    # ---------- avión 3D (render real, lib/avion.py) ----------
    def avion3d(self, centro=(0.0, Y_AV), campo=40.0, ancho_pantalla=9.0, alto_px=720, **params):
        """Capa 3D (1080 px de ancho, transparente). Cada parámetro de `imagen` puede ser un
        número, un ValueTracker o una función; `centro` también puede ser una función.
        Convenio del 3D: alabeo + = ala derecha abajo; guiñada + = morro a la derecha;
        cabeceo + = morro arriba; azimut 0 = de frente, 180 = desde atrás, −90 = de lado
        con el morro a la derecha."""
        if not hasattr(self, "_r3d"):
            self._r3d = {}
        mandos = params.pop("colores_mando", True)
        if not isinstance(campo, (int, float)):      # campo animado (ValueTracker o función)
            params["campo"] = campo
            campo = 40.0
        clave = (alto_px, campo, mandos)
        if clave not in self._r3d:
            from manim import config
            ss = 2 if config.pixel_height >= 1000 else 1      # al iterar con -ql, sin supermuestreo
            self._r3d[clave] = A.Avion3DReal(1080, alto_px, ss, campo=campo, colores_mando=mandos)
        return capa_3d(self._r3d[clave], ancho_pantalla, centro, **params)

    @staticmethod
    def flecha3d(capa, p0, v, color, ancho=9, en_ala=False, minimo=0.08):
        """Flecha en pantalla desde el punto p0 del avión (m, ejes del avión) con el vector v
        (m, ejes del avión; p0 y v pueden ser funciones)."""
        def dib():
            a = np.asarray(p0() if callable(p0) else p0, float)
            b = a + np.asarray(v() if callable(v) else v, float)
            q = capa.a_pantalla([a, b], en_ala=en_ala)
            if np.linalg.norm(q[1] - q[0]) < minimo:
                return VGroup()
            return VGroup(flecha(q[0], q[1], color, ancho))
        return always_redraw(dib)

    # ---------- gráfica ----------
    def grafica(self, t_max, y_rango=(-1.2, 1.2), etiqueta_y="perturbación", etiqueta_x="tiempo",
                alto=2.9, ancho=7.6, centro=(0.0, Y_GR)):
        ax = Axes(x_range=[0, t_max, t_max / 4], y_range=[*y_rango, (y_rango[1] - y_rango[0]) / 4],
                  x_length=ancho, y_length=alto, tips=True,
                  axis_config=dict(color="#64748B", stroke_width=3, include_ticks=False,
                                   tip_length=0.2))
        ax.move_to([*centro, 0])
        et = VGroup(T(etiqueta_x, size=24, color=TEXTO_SEC, weight=MEDIUM)
                    .next_to(ax.x_axis.get_end(), DOWN, buff=0.12).shift(LEFT * 0.45),
                    T(etiqueta_y, size=24, color=TEXTO_SEC, weight=MEDIUM)
                    .next_to(ax.y_axis.get_top(), RIGHT, buff=0.15))
        return ax, et

    def traza(self, ax, f, color, reloj, t_max=None, ancho=7, punta=True, paso=None):
        t_max = t_max if t_max is not None else ax.x_range[1]
        paso = paso or t_max / 300

        def dib():
            t = min(max(reloj.get_value(), paso * 2), t_max)
            c = ax.plot(f, x_range=[0, t, paso], color=color, stroke_width=ancho)
            g = VGroup(c)
            if punta:
                g.add(Dot(ax.c2p(t, f(t)), radius=0.1, color=TEXTO).set_stroke(color, 4))
            return g
        return always_redraw(dib)

    # ---------- textos ----------
    def gancho_texto(self, linea, destacado, color, size=88):
        l1 = T(linea, size=52, weight=HEAVY, font=F_TIT)
        pal = T(destacado, size=size, color=BG, weight=HEAVY, font=F_TIT)
        caja = RoundedRectangle(width=pal.width + 0.6, height=pal.height + 0.45, corner_radius=0.3,
                                fill_color=color, fill_opacity=1, stroke_width=0).move_to(pal)
        dest = VGroup(caja, pal).rotate(-3 * DEGREES)
        if dest.width > 7.6:
            dest.scale_to_fit_width(7.6)
        preg = self.hud(VGroup(l1, dest).arrange(DOWN, buff=0.3).move_to(UP * 4.45))
        return preg, dest

    def bloque_ajustado(self, *a, **k):
        barra, tit, fr, dt = self.bloque(*a, **k)
        if tit.width > 7.6:
            tit.scale_to_fit_width(7.6)
        return barra, tit, fr, dt

    def abrir_bloque(self, barra, color, tit, fr, dt, *entradas, run_time=0.6):
        """Fundido cruzado con lo anterior + frase palabra a palabra + dato."""
        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.2), barra.animate.set_fill(color),
                    *entradas, run_time=run_time)
        self.entrar_palabras(fr)
        if dt is not None:
            self.play(FadeIn(dt), run_time=0.3)

    def avanzar(self, t_fin, *anims, min_rt=0.3):
        """Reproduce `anims` (normalmente relojes con .animate) hasta el instante absoluto t_fin."""
        rt = t_fin - self.renderer.time
        if rt < min_rt:
            return
        self.play(*anims, run_time=rt, rate_func=linear)

    def tarjeta(self, texto, color, ancho=7.4, size=40):
        fondo = RoundedRectangle(width=ancho, height=1.2, corner_radius=0.25, fill_color="#141E31",
                                 fill_opacity=1, stroke_color=color, stroke_width=3)
        t = T(texto, size=size, color=TEXTO, weight=BOLD)
        if t.width > ancho - 0.5:
            t.scale_to_fit_width(ancho - 0.5)
        return VGroup(fondo, t.move_to(fondo))

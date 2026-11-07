"""
Short 31 (narrado): el estampido sónico. Supersónico tipo Concorde en 3D (lib/concorde.py), de lado a Mach 2; los frentes de onda (círculos
que crecen a la velocidad del sonido desde cada punto por donde pasó) forman el cono de Mach,
sen μ = 1/M (μ = 30° a M = 2). El cono barre el suelo: cada persona oye el estampido cuando le
llega, mientras el avión siga supersónico. Escala vertical no real (rotulado en pantalla).
Render:  manim -qh --fps 60 shorts/31_estampido/escena.py Estampido
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403
from lib.modos import ModoBase, flecha  # noqa: E402
from lib.concorde import Concorde3D  # noqa: E402
from lib import concorde as CC  # noqa: E402
from lib.avion2d import capa_3d  # noqa: E402

C_ONDA, C_CONO, C_BUM = C_CABECEO, C_ALABEO, C_GUINADA
XP, YP, YS = 3.5, 1.3, -1.85          # avión (fijo en pantalla) y suelo
U = 1.6                               # velocidad del avión en pantalla (unidades/s)
MACH = 2.0
C = U / MACH
MU = np.arcsin(1 / MACH)
XG = XP - (YP - YS) / np.tan(MU)      # donde el cono toca el suelo
CAMPO_C = 72.0                        # el supersónico (61,7 m) ocupa unas 3,6 unidades


def persona(color=TEXTO_SEC):
    return VGroup(Circle(radius=0.08, stroke_width=0, fill_color=color, fill_opacity=1).shift(UP * 0.36),
                  RoundedRectangle(width=0.16, height=0.28, corner_radius=0.06, stroke_width=0,
                                   fill_color=color, fill_opacity=1).shift(UP * 0.14))


class Estampido(ModoBase):
    VOZ_JSON = Path(__file__).parent / "voz.json"

    def escena(self, s):
        """Ondas, cono y suelo en función del tiempo simulado s (ValueTracker)."""
        from manim import config
        if not hasattr(self, "_conc"):
            self._conc = Concorde3D(1080, 500, 2 if config.pixel_height >= 1000 else 1, campo=CAMPO_C)
        r = self._conc
        px = r.proyectar([CC.a_cuerpo(0.0, 0.0, 0.0)], azimut=-90, elevacion=10, campo=CAMPO_C)[0]
        k = 9.0 / r.ancho
        dx, dy = (px[0] - r.ancho / 2) * k, (r.alto / 2 - px[1]) * k
        av = capa_3d(r, 9.0, (XP - dx, YP - dy), azimut=-90, elevacion=10)

        def ondas():
            g = VGroup()
            tt = s.get_value()
            for i in range(14):
                edad = (tt % 0.5) + 0.5 * i
                x = XP + 0.0 - U * edad
                r = C * edad
                if r < 0.05:
                    continue
                g.add(Circle(radius=r, stroke_color=C_ONDA, stroke_width=3)
                      .move_to([x, YP, 0]).set_stroke(opacity=max(0.0, 0.75 - 0.045 * i)))
            return g
        on = always_redraw(ondas)
        largo = 9.5
        cono = VGroup(Line([XP, YP, 0], [XP - largo * np.cos(MU), YP + largo * np.sin(MU), 0], color=C_CONO, stroke_width=7),
                      Line([XP, YP, 0], [XP - largo * np.cos(MU), YP - largo * np.sin(MU), 0], color=C_CONO, stroke_width=7))
        suelo = Line([-4.8, YS, 0], [4.8, YS, 0], color="#475569", stroke_width=6)
        tierra = Rectangle(width=9.8, height=0.5, stroke_width=0, fill_color="#1E293B",
                           fill_opacity=1).move_to([0, YS - 0.26, 0])
        return av, on, cono, VGroup(tierra, suelo)

    def construct(self):
        self.iniciar()
        s = ValueTracker(3.0)
        av, on, cono, suelo = self.escena(s)
        fondo = brillo([0, 0.5, 0], C_ONDA, 4.2, 0.7)
        preg, dest = self.gancho_texto("El estampido sónico…", "¿SUENA UNA VEZ?", C_CONO, 88)
        sello = self.sello("CONCORDE · MACH 2", C_CONO, DOWN * 3.95, size=50)

        # ---------- Gancho ----------
        self.portada(fondo, suelo, on, cono, av, preg)
        self.wait(0.15)
        self.poner_sello(sello)
        self.avanzar(2.45, s.animate.set_value(5.0))

        # ---------- 1. Ondas y cono ----------
        t0, d = self.voz("b1")
        self.play(self.poner_cabecera("EL ESTAMPIDO SÓNICO", 3), run_time=0.01)
        self.dejar(preg, sello)
        barra, tit, fr, dt = self.bloque_ajustado(0, "Más rápido que su sonido",
                                                  "Las ondas se amontonan en un cono", C_ONDA,
                                                  dato="sen μ = 1 / M · a Mach 2, μ = 30° · escala vertical no real",
                                                  resaltar=["cono"])
        self.abrir_bloque(barra, C_ONDA, tit, fr, dt, cono.animate.set_opacity(0.0),
                          s.animate.set_value(5.6))
        self.avanzar(t0 + d * 0.45, s.animate.set_value(8.5))
        arco = Arc(radius=1.5, start_angle=PI, angle=MU, arc_center=[XP, YP, 0], color=C_CONO, stroke_width=5)
        emu = self.etiqueta("30°", C_CONO, [XP - 1.95, YP + 0.45, 0], size=26)
        ec = self.etiqueta("CONO DE MACH", C_CONO, [XP - 3.3, YP + 1.55, 0], size=24)
        self.sonido("pop", -9)
        self.play(cono.animate.set_opacity(1.0), Create(arco), FadeIn(emu), FadeIn(ec),
                  s.animate.set_value(9.2), run_time=0.7, rate_func=linear)
        self.avanzar(t0 + d - 0.15, s.animate.set_value(14.0))

        # ---------- 2. La alfombra ----------
        t0, d = self.voz("b2")
        self.dejar(tit, fr, dt, arco, emu, ec)
        barra, tit, fr, dt = self.bloque_ajustado(1, "La alfombra", "El cono barre el suelo con el avión",
                                                  C_CONO, dato="cada persona lo oye cuando le llega",
                                                  resaltar=["barre"])
        gente_x = [4.4 + 1.7 * k for k in range(12)]       # posiciones iniciales (se mueven con el suelo)
        s_ini = ValueTracker(s.get_value())

        def gente():
            g = VGroup()
            dx = U * (s.get_value() - s_ini.get_value())
            for x0 in gente_x:
                x = x0 - dx
                if -4.6 < x < 4.6:
                    oido = x < XG
                    p = persona(C_BUM if oido else TEXTO_SEC).scale(1.6).move_to([x, YS + 0.36, 0])
                    g.add(p)
                    if oido and x > XG - 1.1:
                        g.add(T("¡BUM!", size=26, color=C_BUM, weight=HEAVY, font=F_TIT)
                              .move_to([x, YS + 1.15, 0]))
            return g
        ge = always_redraw(gente)

        def alfombra():
            return Rectangle(width=XG + 4.8, height=0.14, stroke_width=0, fill_color=C_BUM,
                             fill_opacity=0.55).move_to([(XG - 4.8) / 2, YS - 0.07, 0])
        alf = alfombra()
        self.abrir_bloque(barra, C_CONO, tit, fr, dt, FadeIn(alf), s.animate.set_value(14.6))
        self.add(ge)
        self.avanzar(t0 + d - 0.15, s.animate.set_value(14.6 + (d - 1.6) * 1.0))

        # ---------- 3. Todo el camino ----------
        t0, d = self.voz("b3")
        self.dejar(tit, fr, dt)
        barra, tit, fr, dt = self.bloque_ajustado(2, "Todo el camino", "Suena mientras vuele supersónico",
                                                  C_BUM, dato="no es un golpe único al cruzar la barrera del sonido",
                                                  resaltar=["mientras"])
        self.abrir_bloque(barra, C_BUM, tit, fr, dt, s.animate.set_value(s.get_value() + 0.6))
        self.avanzar(t0 + d - 0.15, s.animate.set_value(s.get_value() + d - 1.4))

        # ---------- Cierre ----------
        t0, d = self.voz("cierre")
        ge.clear_updaters()
        self.dejar(tit, fr, dt, ge, alf, self.tema, self.barras)
        tj = self.tarjeta("Vuelos supersónicos civiles sobre tierra: limitados", C_CONO, size=32).move_to([0, 4.0, 0])
        preg2 = self.cta("¿En qué año dejó de volar el Concorde?", ["año"], C_CONO, y=-3.4)
        self.cambio(FadeIn(tj, shift=DOWN * 0.3), FadeIn(preg2, shift=UP * 0.3), run_time=0.7)
        self.avanzar(t0 + d * 0.5, s.animate.set_value(s.get_value() + d * 0.5))
        self.pulso(preg2, 1.06)
        self.avanzar(t0 + d - 0.75, s.animate.set_value(s.get_value() + d * 0.3))
        preg, _ = self.gancho_texto("El estampido sónico…", "¿SUENA UNA VEZ?", C_CONO, 88)
        self.dejar(tj, preg2)
        self.cambio(FadeIn(preg), run_time=0.45, desplazar=UP * 0.6)
        self.wait(0.3)

"""
Short 24 (narrado): modo fugoide. Intercambio de velocidad y altura a ángulo de ataque casi
constante: en lo más bajo de la trayectoria va más rápido, en lo más alto más despacio
(altura y velocidad en oposición de fase). Periodo de Lanchester T ≈ π·√2·V/g ≈ 0,45·V s.
Trayectoria con la amplitud vertical exagerada; curvas ilustrativas.
Render:  manim -qh --fps 60 shorts/24_fugoide/escena.py Fugoide
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403
from lib.modos import ModoBase, Y_AV, Y_GR, flecha  # noqa: E402
from lib.avion2d import lateral_2d  # noqa: E402

C_ALT, C_VEL, C_FUG = C_CABECEO, C_GUINADA, C_GUINADA
Y_T, AMP, XT = 1.4, 0.45, 3.1          # trayectoria en pantalla


def altura(u):          # u en ciclos; empieza abajo (rápido) y subiendo
    return -np.cos(2 * PI * u)


def velocidad(u):
    return np.cos(2 * PI * u)


class Fugoide(ModoBase):
    VOZ_JSON = Path(__file__).parent / "voz.json"

    def trayectoria(self, u):
        """u: fase (ciclos). El avión cruza la pantalla en un ciclo y vuelve a empezar."""
        base = lateral_2d(2.1, (0, 0))
        tray = DashedVMobject(FunctionGraph(lambda x: Y_T + AMP * altura((x + XT) / (2 * XT)),
                                            x_range=[-XT - 0.8, XT + 0.8], color=C_FUG, stroke_width=3),
                              num_dashes=50).set_stroke(opacity=0.55)

        def av():
            f = u.get_value() % 1.0
            x = -XT + 2 * XT * f
            pend = AMP * 2 * PI / (2 * XT) * np.sin(2 * PI * f)
            return base.copy().rotate(0.6 * np.arctan(pend), about_point=ORIGIN).move_to(
                [x, Y_T + AMP * altura(f), 0])
        return tray, always_redraw(av)

    def portada_mobs(self):
        u = ValueTracker(0.22)
        tray, av = self.trayectoria(u)
        ax, et = self.grafica(2.0, etiqueta_y="altura")
        th = self.traza(ax, altura, C_ALT, u)
        fondo = brillo([0, Y_T - 0.6, 0], C_FUG, 3.6, 0.8)
        preg, dest = self.gancho_texto("Sin tocar los mandos…", "¿SUBE Y BAJA SOLO?", C_FUG, 76)
        return u, tray, av, ax, et, th, fondo, preg, dest

    def construct(self):
        self.iniciar()
        u, tray, av, ax, et, th, fondo, preg, dest = self.portada_mobs()

        # ---------- Gancho ----------
        sello = self.sello("FUGOIDE", C_FUG, DOWN * 3.95, size=56)
        self.portada(fondo, tray, ax, et, th, av, preg)
        self.wait(0.15)
        self.poner_sello(sello)
        self.avanzar(2.3, u.animate.set_value(0.42))

        # ---------- 1. Sube y baja ----------
        t0, d = self.voz("b1")
        self.play(self.poner_cabecera("MODOS DINÁMICOS · 2", 3), run_time=0.01)
        self.dejar(preg, sello)
        barra, tit, fr, dt = self.bloque_ajustado(0, "Fugoide", "Acelera, sube, frena, baja… y otra vez",
                                                  C_FUG, dato="trayectoria con la altura exagerada",
                                                  resaltar=["sube", "baja"])
        self.abrir_bloque(barra, C_FUG, tit, fr, dt, u.animate.set_value(1.0))
        u.set_value(0.0)
        marcas = VGroup(
            self.etiqueta("ACELERA", C_VEL, [-XT + 0.2, Y_T - AMP - 0.45, 0], size=22),
            self.etiqueta("SUBE", C_ALT, [-XT / 2 - 0.2, Y_T + 0.45, 0], size=22),
            self.etiqueta("FRENA", C_VEL, [0, Y_T + AMP + 0.5, 0], size=22),
            self.etiqueta("BAJA", C_ALT, [XT / 2 + 0.2, Y_T + 0.45, 0], size=22))
        self.sonido("pop", -10)
        self.play(FadeIn(marcas[0], scale=1.2), run_time=0.3)
        self.avanzar(t0 + d * 0.3, u.animate.set_value(0.25))
        self.sonido("pop", -10)
        self.play(FadeIn(marcas[1], scale=1.2), u.animate.set_value(0.3), run_time=0.3, rate_func=linear)
        self.avanzar(t0 + d * 0.5, u.animate.set_value(0.5))
        self.sonido("pop", -10)
        self.play(FadeIn(marcas[2], scale=1.2), u.animate.set_value(0.55), run_time=0.3, rate_func=linear)
        self.avanzar(t0 + d * 0.72, u.animate.set_value(0.75))
        self.sonido("pop", -10)
        self.play(FadeIn(marcas[3], scale=1.2), u.animate.set_value(0.8), run_time=0.3, rate_func=linear)
        self.avanzar(t0 + d - 0.1, u.animate.set_value(1.0))

        # ---------- 2. Velocidad por altura ----------
        t0, d = self.voz("b2")
        th.clear_updaters()
        self.dejar(tit, fr, dt, marcas, th, et)
        barra, tit, fr, dt = self.bloque_ajustado(1, "Intercambio", "Cambia velocidad por altura",
                                                  C_ALT, dato="el ángulo de ataque casi no cambia",
                                                  resaltar=["velocidad", "altura"])
        u2 = ValueTracker(1.0)
        ax2, et2 = self.grafica(1.0)
        et2[1].become(T("altura y velocidad", size=24, color=TEXTO_SEC, weight=MEDIUM)
                      .next_to(ax2.y_axis.get_top(), RIGHT, buff=0.15))
        ga = self.traza(ax2, altura, C_ALT, ValueTracker(0), punta=True)
        # trazas en función de la fase del ciclo (0–1)
        fase = ValueTracker(0.02)
        ga = self.traza(ax2, altura, C_ALT, fase)
        gv = self.traza(ax2, velocidad, C_VEL, fase)
        la = self.etiqueta("ALTURA", C_ALT, ax2.c2p(0.5, 1.15), size=22)
        lv = self.etiqueta("VELOCIDAD", C_VEL, ax2.c2p(0.25, -0.7), size=22)
        self.abrir_bloque(barra, C_ALT, tit, fr, dt, FadeIn(et2))
        self.add(ga, gv)
        u.set_value(0.0)
        self.play(FadeIn(la), FadeIn(lv), run_time=0.3)
        self.avanzar(t0 + d - 0.15, u.animate.set_value(1.0), fase.animate.set_value(1.0))
        del u2

        # ---------- 3. Lento y poco amortiguado ----------
        t0, d = self.voz("b3")
        ga.clear_updaters()
        gv.clear_updaters()
        self.dejar(tit, fr, dt, ga, gv, la, lv, ax, et2)
        barra, tit, fr, dt = self.bloque_ajustado(2, "Muy lento", "Un ciclo: decenas de segundos",
                                                  C_FUG, dato="aprox. de Lanchester: T ≈ 0,45·V (V en m/s) → a 230 m/s, ≈ 100 s",
                                                  resaltar=["decenas"])
        ax3, et3 = self.grafica(400, etiqueta_x="tiempo (s)", etiqueta_y="altura")
        marcas_t = VGroup(*[self.etiqueta(f"{s} s", TEXTO_SEC, ax3.c2p(s, -0.2), size=18)
                            for s in (100, 200, 300)])
        r3 = ValueTracker(2.0)

        def h3(t):
            return -np.exp(-t / 450) * np.cos(2 * PI * t / 104)
        g3 = self.traza(ax3, h3, C_ALT, r3, paso=1.0)
        env = DashedVMobject(ax3.plot(lambda t: np.exp(-t / 450), x_range=[0, 400], color=C_ALT,
                                      stroke_width=3), num_dashes=40).set_stroke(opacity=0.5)
        self.abrir_bloque(barra, C_FUG, tit, fr, dt, FadeIn(ax3), FadeIn(et3), FadeIn(marcas_t))
        self.add(g3)
        self.avanzar(t0 + d * 0.58, r3.animate.set_value(230), u.animate.set_value(2.2))
        # «Y se amortigua poco: solo lo frena la resistencia»
        e5 = self.etiqueta("SE AMORTIGUA POCO", C_ALABEO, ax3.c2p(260, 1.15), size=22)
        self.sonido("pop", -9)
        self.play(FadeIn(e5, scale=1.2), Create(env), r3.animate.set_value(250),
                  u.animate.set_value(2.3), run_time=0.4, rate_func=linear)
        self.avanzar(t0 + d - 0.15, r3.animate.set_value(400), u.animate.set_value(3.0))

        # ---------- Cierre ----------
        t0, d = self.voz("cierre")
        g3.clear_updaters()
        self.dejar(tit, fr, dt, ax3, et3, marcas_t, g3, env, e5, tray, av, fondo, self.tema, self.barras)
        tj = VGroup(self.tarjeta("Velocidad ⇄ altura", C_FUG),
                    self.tarjeta("El piloto lo corrige sin notarlo", C_ALT)).arrange(DOWN, buff=0.3).move_to([0, 2.2, 0])
        preg2 = self.hud(frase_cinetica("¿Lo conocías?", size=72, resaltar=["conocías?"],
                                        color_resalte=C_FUG).move_to(DOWN * 0.8))
        self.cambio(LaggedStart(*[FadeIn(x, shift=RIGHT * 0.4) for x in tj], lag_ratio=0.4),
                    FadeIn(preg2, shift=UP * 0.3), run_time=0.8)
        self.hasta(t0, d * 0.4)
        self.pulso(tj[1], 1.05)
        self.hasta(t0, d * 0.75)
        self.pulso(preg2, 1.08)
        self.hasta(t0, d - 0.7)
        u, tray, av, ax, et, th, fondo, preg, dest = self.portada_mobs()
        self.dejar(tj, preg2)
        self.cambio(*[FadeIn(m) for m in (fondo, tray, ax, et, th, av, preg)], run_time=0.45,
                    desplazar=UP * 0.6)
        self.wait(0.3)

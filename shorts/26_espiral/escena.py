"""
Short 26 (narrado): modo espiral. Con el avión inclinado, resbala hacia el ala baja; el efecto
diedro tiende a nivelarlo y la estabilidad direccional (deriva) gira el morro hacia el giro, con
lo que el ala de fuera va más rápido y genera más sustentación (alabeo por guiñada). Si domina la
deriva, la inclinación crece despacio (divergencia en espiral, decenas de segundos).
Vista de frente: el avión viene hacia nosotros (su ala derecha está a la izquierda de la pantalla).
Curvas ilustrativas.
Render:  manim -qh --fps 60 shorts/26_espiral/escena.py Espiral
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403
from lib.modos import ModoBase, Y_AV, flecha  # noqa: E402
from lib.avion2d import superior_2d  # noqa: E402

C_ESP, C_DIE, C_DER = C_ALABEO, C_CABECEO, C_GUINADA
TM = 60.0


def phi_ine(t):
    return 0.18 * np.exp(t / 26.0)


def phi_est(t):
    return 0.18 * np.exp(-t / 14.0)


class Espiral(ModoBase):
    VOZ_JSON = Path(__file__).parent / "voz.json"

    def base(self, r0):
        r = ValueTracker(r0)
        av = self.frontal(5.4, (0, Y_AV), alabeo=lambda: 12 + 25 * phi_ine(r.get_value()))
        ax, et = self.grafica(TM, y_rango=(-0.1, 1.2), etiqueta_y="inclinación",
                              etiqueta_x="tiempo (s)")
        tr = self.traza(ax, phi_ine, C_ESP, r)
        fondo = brillo([0, Y_AV - 0.4, 0], C_ESP, 3.6, 0.8)
        return r, av, ax, et, tr, fondo

    def construct(self):
        self.iniciar()
        r, av, ax, et, tr, fondo = self.base(4.0)
        preg, dest = self.gancho_texto("Inclinado y sin tocar nada…", "¿QUÉ PASA?", C_ESP, 96)

        # ---------- Gancho ----------
        sello = self.sello("MODO ESPIRAL", C_ESP, DOWN * 3.95, size=54)
        self.portada(fondo, ax, et, tr, av, preg)
        self.wait(0.15)
        self.poner_sello(sello)
        self.avanzar(2.9, r.animate.set_value(14.0))

        # ---------- 1. Resbala ----------
        t0, d = self.voz("b1")
        self.play(self.poner_cabecera("MODOS DINÁMICOS · 4", 3), run_time=0.01)
        self.dejar(preg, sello)
        barra, tit, fr, dt = self.bloque_ajustado(0, "Resbala", "Se va hacia el ala baja",
                                                  C_ESP, dato="vista de frente: el avión viene hacia ti",
                                                  resaltar=["ala", "baja"])
        res = flecha([0.6, Y_AV - 1.05, 0], [-1.6, Y_AV - 1.05, 0], C_ESP, 10)
        eres = self.etiqueta("RESBALA", C_ESP, [1.6, Y_AV - 1.05, 0], size=24)
        self.abrir_bloque(barra, C_ESP, tit, fr, dt, r.animate.set_value(15.0))
        self.sonido("whoosh_suave", -12)
        self.play(GrowArrow(res), FadeIn(eres), r.animate.set_value(16.0), run_time=0.5)
        self.avanzar(t0 + d * 0.65, r.animate.set_value(22.0))
        duelo = VGroup(pastilla(T("DIEDRO", size=34, color=C_DIE, weight=HEAVY, font=F_TIT), C_DIE),
                       T("vs", size=30, color=TEXTO_SEC, weight=BOLD),
                       pastilla(T("DERIVA", size=34, color=C_DER, weight=HEAVY, font=F_TIT), C_DER)
                       ).arrange(RIGHT, buff=0.35).move_to([0.9, 0.15, 0])
        self.sonido("golpe", -12)
        self.play(FadeIn(duelo, scale=1.3), r.animate.set_value(23.0), run_time=0.4,
                  rate_func=rate_functions.ease_out_back)
        self.avanzar(t0 + d - 0.15, r.animate.set_value(26.0))

        # ---------- 2. Los dos efectos ----------
        t0, d = self.voz("b2")
        tr.clear_updaters()
        self.dejar(tit, fr, dt, res, eres, duelo, av, ax, et, tr)
        barra, tit, fr, dt = self.bloque_ajustado(1, "Dos efectos", "El diedro nivela; la deriva lo inclina más",
                                                  C_DER, dato="izquierda: de frente · derecha: desde arriba",
                                                  resaltar=["nivela", "más"])
        Y2 = 0.7
        g1 = ValueTracker(28.0)     # alabeo en la vista de frente
        avf = self.frontal(3.7, (-2.3, Y2), alabeo=lambda: g1.get_value())
        g2 = ValueTracker(0.0)      # guiñada en la vista desde arriba
        avs = self.superior(2.3, (2.3, Y2 + 0.2), guinada=lambda: g2.get_value())
        sep = DashedLine([0, Y2 + 1.7, 0], [0, Y2 - 1.7, 0], color="#334155", stroke_width=3)
        die = always_redraw(lambda: flecha_giro([-2.3, Y2, 0], 1.55, PI + 0.35, -0.9, C_DIE))
        edie = VGroup(T("DIEDRO", size=32, color=C_DIE, weight=HEAVY, font=F_TIT),
                      T("tiende a nivelar", size=24, color=TEXTO_SEC, weight=MEDIUM)
                      ).arrange(DOWN, buff=0.06).move_to([-2.3, Y2 - 1.85, 0])
        eder = VGroup(T("DERIVA", size=32, color=C_DER, weight=HEAVY, font=F_TIT),
                      T("morro hacia el giro", size=24, color=TEXTO_SEC, weight=MEDIUM)
                      ).arrange(DOWN, buff=0.06).move_to([2.3, Y2 - 1.85, 0])
        self.abrir_bloque(barra, C_DER, tit, fr, dt, FadeIn(avf), FadeIn(sep))
        self.add(die)
        self.play(FadeIn(edie, shift=UP * 0.2), g1.animate.set_value(22.0), run_time=0.5)
        self.avanzar(t0 + d * 0.33, g1.animate.set_value(16.0))
        # «La deriva gira el morro hacia el giro»
        self.sonido("pop", -9)
        self.play(FadeIn(avs), FadeIn(eder, shift=UP * 0.2), run_time=0.4)
        self.avanzar(t0 + d * 0.58, g2.animate.set_value(22.0))
        # «el ala de fuera va más rápido y lo inclina más»
        ang = -22 * DEGREES

        def velocidades():
            c = np.array([2.3, Y2, 0])
            ex = np.array([np.cos(ang), np.sin(ang), 0])      # eje de las alas (girado)
            ey = np.array([-np.sin(ang), np.cos(ang), 0])     # hacia el morro
            c = c + UP * 0.2
            fuera, dentro = c - ex * 1.0, c + ex * 1.0      # ala izquierda = fuera del giro a la derecha
            return VGroup(flecha(fuera, fuera + ey * 1.0, C_DER, 9),
                          flecha(dentro, dentro + ey * 0.45, C_DER, 9))
        vel = velocidades()
        efu = self.etiqueta("MÁS RÁPIDA", C_DER, [1.25, Y2 + 1.45, 0], size=20)
        self.sonido("pop", -9)
        self.play(FadeIn(vel), FadeIn(efu), FadeOut(die), g1.animate.set_value(30.0), run_time=0.5)
        self.avanzar(t0 + d - 0.15, g1.animate.set_value(38.0))

        # ---------- 3. La espiral ----------
        t0, d = self.voz("b3")
        self.dejar(tit, fr, dt, avf, avs, sep, edie, eder, vel, efu)
        barra, tit, fr, dt = self.bloque_ajustado(2, "La espiral", "Si gana la deriva, se cierra poco a poco",
                                                  C_ESP, dato="muchos aviones son un poco inestables en espiral",
                                                  resaltar=["deriva", "cierra"])
        # trayectoria vista desde arriba (espiral que se cierra) y gráfica
        CS = np.array([0.0, Y_AV - 0.05, 0])

        def punto(th):
            rr = 1.55 * np.exp(-0.1 * th)
            return CS + np.array([rr * np.cos(th), 0.62 * rr * np.sin(th), 0])
        ths = np.linspace(0, 4 * PI, 300)
        camino = VMobject().set_points_smoothly([punto(t) for t in ths]).set_stroke(C_ESP, 3, opacity=0.45)
        s3 = ValueTracker(0.0)
        mini = superior_2d(1.0, (0, 0))

        def avion_esp():
            th = s3.get_value()
            p0, p1 = punto(th), punto(th + 0.05)
            dirc = np.arctan2(p1[1] - p0[1], p1[0] - p0[0])
            return mini.copy().rotate(dirc - PI / 2, about_point=ORIGIN).move_to(p0)
        ave = always_redraw(avion_esp)
        r2 = ValueTracker(0.5)
        ax2, et2 = self.grafica(TM, y_rango=(-0.1, 1.2), etiqueta_y="inclinación", etiqueta_x="tiempo (s)")
        ti = self.traza(ax2, phi_ine, C_ESP, r2)
        te = self.traza(ax2, phi_est, C_DIE, r2, ancho=5)
        marcas_t = VGroup(*[self.etiqueta(f"{s} s", TEXTO_SEC, ax2.c2p(s, -0.04), size=18) for s in (20, 40)])
        self.abrir_bloque(barra, C_ESP, tit, fr, dt, FadeIn(camino), FadeIn(ax2), FadeIn(et2),
                          FadeIn(marcas_t))
        self.add(ave, ti, te)
        l1 = self.etiqueta("GANA LA DERIVA: CRECE", C_ESP, ax2.c2p(30, 1.05), size=22)
        l2 = self.etiqueta("GANA EL DIEDRO: SE NIVELA", C_DIE, ax2.c2p(30, 0.32), size=22)
        self.avanzar(t0 + d * 0.3, s3.animate.set_value(1.5 * PI), r2.animate.set_value(22))
        self.sonido("pop", -9)
        self.play(FadeIn(l1, scale=1.2), FadeIn(l2, scale=1.2), run_time=0.3)
        self.avanzar(t0 + d - 0.15, s3.animate.set_value(4 * PI), r2.animate.set_value(TM))

        # ---------- Cierre ----------
        t0, d = self.voz("cierre")
        for m in (ti, te, ave):
            m.clear_updaters()
        self.dejar(tit, fr, dt, camino, ave, ax2, et2, marcas_t, ti, te, l1, l2, self.tema, self.barras)
        tj = VGroup(self.tarjeta("Lento: se corrige sin esfuerzo", C_DIE),
                    self.tarjeta("Sin ver el horizonte, traicionero", C_ESP)).arrange(DOWN, buff=0.3).move_to([0, 2.2, 0])
        preg2 = self.hud(frase_cinetica("¿Lo conocías?", size=76, resaltar=["conocías?"],
                                        color_resalte=C_ESP).move_to(DOWN * 0.8))
        self.cambio(LaggedStart(*[FadeIn(x, shift=RIGHT * 0.4) for x in tj], lag_ratio=0.4),
                    FadeIn(preg2, shift=UP * 0.3), run_time=0.8)
        self.hasta(t0, d * 0.35)
        self.pulso(tj[0], 1.04)
        self.hasta(t0, d * 0.6)
        self.pulso(tj[1], 1.04)
        self.hasta(t0, d * 0.85)
        self.pulso(preg2, 1.08)
        self.hasta(t0, d - 0.7)
        r, av, ax, et, tr, fondo = self.base(4.0)
        preg, _ = self.gancho_texto("Inclinado y sin tocar nada…", "¿QUÉ PASA?", C_ESP, 96)
        self.dejar(tj, preg2)
        self.cambio(*[FadeIn(m) for m in (fondo, ax, et, tr, av, preg)], run_time=0.45,
                    desplazar=UP * 0.6)
        self.wait(0.3)

"""
Short 25 (narrado): convergencia en alabeo (amortiguamiento en alabeo, L_p).
Tras un impulso de alabeo: p(t) = p0·e^(−t/τ), φ(t) = p0·τ·(1 − e^(−t/τ)). La velocidad de
alabeo se apaga en ~τ (del orden de 1 s) y la inclinación se queda donde estaba.
Vista de frente (el avión viene hacia nosotros); curvas ilustrativas.
Render:  manim -qh --fps 60 shorts/25_convergencia_alabeo/escena.py ConvergenciaAlabeo
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403
from lib.modos import ModoBase, Y_AV, flecha  # noqa: E402

C_P, C_PHI, C_SUST = C_ALABEO, C_CABECEO, C_CABECEO
TAU, PHI_F, TM = 0.8, 22.0, 4.0
ANCHO = 5.6


def p(t):          # velocidad de alabeo (normalizada a 1 al principio)
    return np.exp(-t / TAU)


def phi(t):        # inclinación (normalizada a 1 al final)
    return 1 - np.exp(-t / TAU)


def girar(v, ang):
    a = ang * DEGREES
    return np.array([np.cos(a) * v[0] - np.sin(a) * v[1], np.sin(a) * v[0] + np.cos(a) * v[1], 0])


class ConvergenciaAlabeo(ModoBase):
    VOZ_JSON = Path(__file__).parent / "voz.json"

    def base(self, r0):
        r = ValueTracker(r0)
        av = self.frontal(ANCHO, (0, Y_AV), alabeo=lambda: PHI_F * phi(r.get_value()))
        ax, et = self.grafica(TM, y_rango=(-0.2, 1.2), etiqueta_y="alabeo")
        tp = self.traza(ax, p, C_P, r)
        tf = self.traza(ax, phi, C_PHI, r)
        fondo = brillo([0, Y_AV - 0.4, 0], C_P, 3.6, 0.8)
        return r, av, ax, et, tp, tf, fondo

    def puntas(self, r):
        ang = PHI_F * phi(r.get_value())
        c = np.array([0, Y_AV, 0])
        return c + girar([-ANCHO * 0.42, 0.15, 0], ang), c + girar([ANCHO * 0.42, 0.15, 0], ang), ang

    def gancho_mobs(self):
        r, av, ax, et, tp, tf, fondo = self.base(0.35)
        raf = VGroup(*[flecha([-2.3 + 0.4 * k, Y_AV - 1.2, 0], [-2.3 + 0.4 * k, Y_AV - 0.45, 0],
                              "#CBD5E1", 8) for k in range(3)])
        preg, dest = self.gancho_texto("¿Por qué el avión", "NO SIGUE RODANDO?", C_P, 80)
        return r, av, ax, et, tp, tf, fondo, raf, preg, dest

    def construct(self):
        self.iniciar()
        r, av, ax, et, tp, tf, fondo, raf, preg, dest = self.gancho_mobs()

        # ---------- Gancho ----------
        sello = self.sello("CONVERGENCIA EN ALABEO", C_P, DOWN * 3.95, size=44)
        self.portada(fondo, ax, et, tp, tf, av, raf, preg)
        self.wait(0.15)
        self.poner_sello(sello)
        self.avanzar(2.1, r.animate.set_value(TM), raf.animate.set_opacity(0))

        # ---------- 1. El ala que baja ----------
        t0, d = self.voz("b1")
        self.play(self.poner_cabecera("MODOS DINÁMICOS · 3", 3), run_time=0.01)
        self.dejar(preg, sello, raf)
        barra, tit, fr, dt = self.bloque_ajustado(0, "El ala que baja", "Ve el aire más de frente",
                                                  C_SUST, dato="más ángulo de ataque → más sustentación",
                                                  resaltar=["frente"])

        def sustentaciones():
            t = r.get_value()
            izq, der, ang = self.puntas(r)
            n = girar([0, 1, 0], ang)
            k = 0.55 * p(t)
            g = VGroup(flecha(izq, izq + n * (0.55 + k), C_SUST, 10),     # ala que baja (izquierda en pantalla)
                       flecha(der, der + n * max(0.55 - k, 0.1), C_SUST, 10))
            return g
        sust = always_redraw(sustentaciones)

        def aire():
            izq, _, _ = self.puntas(r)
            a = 0.9 * p(r.get_value())
            return flecha(izq + DOWN * (0.25 + a), izq + DOWN * 0.25, "#CBD5E1", 7)
        vien = always_redraw(aire)
        self.abrir_bloque(barra, C_SUST, tit, fr, dt, r.animate.set_value(0.0))
        self.add(sust, vien)
        e1 = self.etiqueta("AIRE DESDE ABAJO", "#CBD5E1", [-1.2, Y_AV - 0.8, 0], size=22)
        self.play(FadeIn(e1), run_time=0.3)
        self.avanzar(t0 + d * 0.55, r.animate.set_value(0.5))
        e2 = self.etiqueta("MÁS SUSTENTACIÓN", C_SUST, [-1.3, Y_AV + 1.2, 0], size=22)
        self.sonido("pop", -9)
        self.play(FadeIn(e2, scale=1.2), run_time=0.3)
        self.avanzar(t0 + d - 0.15, r.animate.set_value(0.9))

        # ---------- 2. Frena el giro ----------
        t0, d = self.voz("b2")
        self.dejar(tit, fr, dt, e1, e2, vien)
        barra, tit, fr, dt = self.bloque_ajustado(1, "Frena el giro", "Un momento contrario",
                                                  C_P, dato="en cerca de un segundo",
                                                  resaltar=["contrario"])
        e3 = self.etiqueta("MENOS", C_SUST, [2.7, Y_AV + 1.0, 0], size=22)

        def momento():
            k = p(r.get_value())
            if k < 0.05:
                return VGroup()
            return flecha_giro([0, Y_AV, 0], 1.55, PI / 2 + 0.6, -1.2 * k, C_P)
        mom = always_redraw(momento)
        self.abrir_bloque(barra, C_P, tit, fr, dt, r.animate.set_value(0.0))
        self.play(FadeIn(e3), run_time=0.3)
        self.add(mom)
        e4 = self.etiqueta("FRENA", C_P, [0, Y_AV + 1.0, 0], size=24)
        self.hasta(t0, d * 0.4)
        self.sonido("golpe", -12)
        self.play(FadeIn(e4, scale=1.3), run_time=0.3)
        self.avanzar(t0 + d - 0.15, r.animate.set_value(TM))

        # ---------- 3. No endereza ----------
        t0, d = self.voz("b3")
        self.dejar(tit, fr, dt, e3, e4, mom, sust)
        barra, tit, fr, dt = self.bloque_ajustado(2, "No endereza", "Se para el giro, no la inclinación",
                                                  C_PHI, dato="convergencia: sin oscilar · curvas ilustrativas",
                                                  resaltar=["giro", "inclinación"])
        r2 = ValueTracker(0.02)
        tp2 = self.traza(ax, p, C_P, r2, ancho=8)
        tf2 = self.traza(ax, phi, C_PHI, r2, ancho=8)
        tp.clear_updaters()
        tf.clear_updaters()
        self.abrir_bloque(barra, C_PHI, tit, fr, dt, tp.animate.set_stroke(opacity=0.25),
                          tf.animate.set_stroke(opacity=0.25))
        self.add(tp2, tf2)
        r.set_value(0.0)
        self.avanzar(t0 + d * 0.5, r.animate.set_value(TM * 0.6), r2.animate.set_value(TM * 0.6))
        l1 = self.etiqueta("VELOCIDAD DE ALABEO → 0", C_P, ax.c2p(2.7, 0.3), size=22)
        l2 = self.etiqueta("INCLINACIÓN: SE QUEDA", C_PHI, ax.c2p(2.7, 1.2), size=22)
        self.sonido("pop", -9)
        self.play(FadeIn(l1, scale=1.2), FadeIn(l2, scale=1.2), run_time=0.35)
        self.avanzar(t0 + d - 0.15, r.animate.set_value(TM), r2.animate.set_value(TM))

        # ---------- Cierre ----------
        t0, d = self.voz("cierre")
        for m in (tp2, tf2):
            m.clear_updaters()
        self.dejar(tit, fr, dt, l1, l2, tp, tf, tp2, tf2, ax, et, av, fondo, self.tema, self.barras)
        tj = VGroup(self.tarjeta("Alerones: velocidad de alabeo, no ángulo", C_P),
                    self.tarjeta("Para dejar de girar, se centran", C_PHI)).arrange(DOWN, buff=0.3).move_to([0, 2.2, 0])
        preg2 = self.hud(frase_cinetica("¿Lo sabías?", size=76, resaltar=["sabías?"],
                                        color_resalte=C_P).move_to(DOWN * 0.8))
        self.cambio(LaggedStart(*[FadeIn(x, shift=RIGHT * 0.4) for x in tj], lag_ratio=0.4),
                    FadeIn(preg2, shift=UP * 0.3), run_time=0.8)
        self.hasta(t0, d * 0.35)
        self.pulso(tj[0], 1.04)
        self.hasta(t0, d * 0.6)
        self.pulso(tj[1], 1.04)
        self.hasta(t0, d * 0.82)
        self.pulso(preg2, 1.08)
        self.hasta(t0, d - 0.7)
        r, av, ax, et, tp, tf, fondo, raf, preg, dest = self.gancho_mobs()
        self.dejar(tj, preg2)
        self.cambio(*[FadeIn(m) for m in (fondo, ax, et, tp, tf, av, raf, preg)], run_time=0.45,
                    desplazar=UP * 0.6)
        self.wait(0.3)

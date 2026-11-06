"""
Short 27 (narrado): balanceo holandés, con el avión 3D (render real).
Oscilación acoplada de guiñada y alabeo: si el morro se va a la derecha, el ala izquierda
avanza, gana sustentación y sube (el avión alabea a la derecha, con retraso); la deriva devuelve
el morro, se pasa y el ciclo se repite. La flecha aumenta el efecto diedro; el amortiguador de
guiñada mueve el timón para frenarlo. ψ y φ ~ e^(−σt)·sen(ωt), φ retrasado ~80°; curvas
ilustrativas (periodo de 3 s). La estela de la punta del ala dibuja el óvalo en directo.
Render:  manim -qh --fps 60 shorts/27_balanceo_holandes/escena.py BalanceoHolandes
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403
from lib.modos import ModoBase, Y_AV  # noqa: E402
from lib import avion as A  # noqa: E402

C_PSI, C_PHI, C_YD = C_GUINADA, C_ALABEO, C_CABECEO
W = 2 * PI / 3.0
TM = 12.0
K_PSI, K_PHI = 9.0, 11.0              # grados en el 3D por unidad de la curva
PUNTA = A.punto_ala(17.0, s=1, xc=0.5)  # punta del ala izquierda (la que avanza al guiñar a la derecha)


def psi(t, s=0.07):
    return np.exp(-s * t) * np.sin(W * t)


def dpsi(t, s=0.07):
    return np.exp(-s * t) * (W * np.cos(W * t) - s * np.sin(W * t))


def phi(t, s=0.07):
    return 1.15 * np.exp(-s * t) * np.sin(W * t - PI / 2.2) * (1 - np.exp(-2.5 * t))


class BalanceoHolandes(ModoBase):
    VOZ_JSON = Path(__file__).parent / "voz.json"

    def base(self, r0, s=0.07):
        r = ValueTracker(r0)
        ss = ValueTracker(s)
        tim = ValueTracker(0.0)          # 1 = amortiguador de guiñada activo (mueve el timón)
        av = self.avion3d(centro=(0, Y_AV + 0.2), campo=46, azimut=-150, elevacion=24,
                          guinada=lambda: K_PSI * psi(r.get_value(), ss.get_value()),
                          alabeo=lambda: K_PHI * phi(r.get_value(), ss.get_value()),
                          timon=lambda: -9 * tim.get_value() * dpsi(r.get_value(), ss.get_value()))
        ax, et = self.grafica(TM, etiqueta_y="ángulos")
        tg = self.traza(ax, psi, C_PSI, r)
        ta = self.traza(ax, phi, C_PHI, r)
        fondo = brillo([0, Y_AV - 0.3, 0], C_PSI, 3.8, 0.8)
        return r, ss, tim, av, ax, et, tg, ta, fondo

    def estela(self, av, color=C_PHI, vida=2.6):
        punto = always_redraw(lambda: Dot(av.a_pantalla([PUNTA])[0], radius=0.09, color=color)
                              .set_stroke(TEXTO, 2))
        rastro = TracedPath(lambda: av.a_pantalla([PUNTA])[0], stroke_color=color,
                            stroke_width=5, dissipating_time=vida)
        return punto, rastro

    def construct(self):
        self.iniciar()
        r, ss, tim, av, ax, et, tg, ta, fondo = self.base(0.9)
        preg, dest = self.gancho_texto("¿Un avión que se mece", "DE LADO A LADO?", C_PSI, 84)

        # ---------- Gancho ----------
        sello = self.sello("BALANCEO HOLANDÉS", C_PSI, DOWN * 3.95, size=50)
        self.portada(fondo, ax, et, tg, ta, av, preg)
        self.wait(0.15)
        self.poner_sello(sello)
        self.avanzar(2.4, r.animate.set_value(2.6))

        # ---------- 1. Guiña y alabea ----------
        t0, d = self.voz("b1")
        self.play(self.poner_cabecera("MODOS DINÁMICOS · 5", 3), run_time=0.01)
        self.dejar(preg, sello)
        barra, tit, fr, dt = self.bloque_ajustado(0, "Balanceo holandés", "Guiña y alabea a la vez",
                                                  C_PSI, dato="el ala que avanza gana sustentación y sube",
                                                  resaltar=["guiña", "alabea"])
        self.abrir_bloque(barra, C_PSI, tit, fr, dt, r.animate.set_value(0.02))
        lg = self.etiqueta("GUIÑADA", C_PSI, ax.c2p(10.2, 1.2), size=22)
        la = self.etiqueta("ALABEO", C_PHI, ax.c2p(10.2, 0.55), size=22)
        self.sonido("whoosh_suave", -12)
        self.play(FadeIn(lg), r.animate.set_value(0.5), run_time=0.5, rate_func=linear)
        # «el ala que avanza sube»: sustentación extra en la punta que avanza
        sust = self.flecha3d(av, PUNTA, lambda: np.array([0, 0, 2.0 + 10.0 * max(psi(r.get_value()), 0)]),
                             C_PHI, 9, minimo=0.15)
        e_ala = always_redraw(lambda: self.etiqueta("AVANZA Y SUBE", C_PHI, ORIGIN, size=20)
                              .next_to(av.a_pantalla([PUNTA])[0], UP, buff=0.9))
        self.avanzar(t0 + d * 0.45, r.animate.set_value(1.2))
        self.sonido("pop", -9)
        self.add(sust)
        self.play(FadeIn(e_ala), FadeIn(la), r.animate.set_value(1.4), run_time=0.35, rate_func=linear)
        self.avanzar(t0 + d - 0.15, r.animate.set_value(3.2))

        # ---------- 2. Se pasa (la punta dibuja un óvalo) ----------
        t0, d = self.voz("b2")
        e_ala.clear_updaters()
        self.dejar(tit, fr, dt, e_ala, sust)
        barra, tit, fr, dt = self.bloque_ajustado(1, "Se pasa", "La deriva lo devuelve… y se pasa",
                                                  C_PHI, dato="y vuelta a empezar, cada pocos segundos",
                                                  resaltar=["pasa"])
        punto, rastro = self.estela(av)
        self.abrir_bloque(barra, C_PHI, tit, fr, dt, r.animate.set_value(3.5))
        self.add(rastro, punto)
        self.avanzar(t0 + d * 0.6, r.animate.set_value(6.5))
        ep = self.etiqueta("PERIODO: POCOS SEGUNDOS", TEXTO, ax.c2p(5.6, 1.3), size=22)
        self.sonido("pop", -9)
        self.play(FadeIn(ep, scale=1.2), r.animate.set_value(6.8), run_time=0.3, rate_func=linear)
        self.avanzar(t0 + d - 0.15, r.animate.set_value(TM * 0.72))

        # ---------- 3. Flecha y amortiguador ----------
        t0, d = self.voz("b3")
        for m in (tg, ta, punto):
            m.clear_updaters()
        self.dejar(tit, fr, dt, ep, lg, la, punto, rastro)
        barra, tit, fr, dt = self.bloque_ajustado(2, "Amortiguador", "El timón se mueve solo",
                                                  C_YD, dato="las alas en flecha lo acentúan, sobre todo a gran altitud",
                                                  resaltar=["timón", "solo"])
        r2 = ValueTracker(0.02)
        tg2 = self.traza(ax, lambda t: psi(t, 0.55), C_YD, r2, ancho=8)
        self.abrir_bloque(barra, C_YD, tit, fr, dt, tg.animate.set_stroke(opacity=0.3),
                          ta.animate.set_stroke(opacity=0.3), r.animate.set_value(TM * 0.75))
        e1 = self.etiqueta("SIN AMORTIGUADOR", C_PSI, ax.c2p(8.6, 1.25), size=22)
        self.play(FadeIn(e1), run_time=0.3)
        # el avión vuelve a empezar con el amortiguador: el timón (amarillo) se mueve solo
        self.avanzar(t0 + d * 0.42, r.animate.set_value(TM * 0.95))
        r.set_value(0.02)
        ss.set_value(0.55)
        tim.set_value(1.0)
        self.add(tg2)
        e2 = self.etiqueta("CON AMORTIGUADOR DE GUIÑADA", C_YD, ax.c2p(7.4, -0.55), size=22)
        et_t = self.etiqueta("TIMÓN", C_GUINADA, ORIGIN, size=20)
        et_t.add_updater(lambda m: m.move_to(av.a_pantalla([A.a_cuerpo(35.5, 0, 6.5)])[0] + UP * 0.35))
        self.sonido("pop", -9)
        self.play(FadeIn(e2, scale=1.2), FadeIn(et_t), run_time=0.3)
        self.avanzar(t0 + d - 0.15, r.animate.set_value(TM * 0.5), r2.animate.set_value(TM))

        # ---------- Cierre: la punta del ala dibuja un óvalo ----------
        t0, d = self.voz("cierre")
        for m in (tg2, et_t):
            m.clear_updaters()
        self.dejar(tit, fr, dt, e1, e2, et_t, tg, ta, tg2, ax, et, self.tema, self.barras)
        r.set_value(0.6)
        ss.set_value(0.0)
        tim.set_value(0.0)
        punto, rastro = self.estela(av, vida=3.2)
        tj = self.tarjeta("La punta del ala dibuja un óvalo", C_PHI).move_to([0, 4.2, 0])
        preg2 = self.hud(frase_cinetica("¿Qué modo te faltaba?", size=66, resaltar=["modo"],
                                        color_resalte=C_PSI).move_to(DOWN * 1.3))
        self.cambio(FadeIn(tj), FadeIn(preg2, shift=UP * 0.3), run_time=0.6)
        self.add(rastro, punto)
        self.avanzar(t0 + d * 0.4, r.animate.set_value(2.4))
        self.pulso(tj, 1.05)
        self.avanzar(t0 + d * 0.72, r.animate.set_value(4.0))
        self.pulso(preg2, 1.06)
        self.avanzar(t0 + d - 0.75, r.animate.set_value(5.2))
        # vuelve a la imagen del gancho
        punto.clear_updaters()
        r.set_value(0.9)
        ss.set_value(0.07)
        _, _, _, _, ax, et, tg, ta, fondo2 = self.base(0.9)
        preg, _ = self.gancho_texto("¿Un avión que se mece", "DE LADO A LADO?", C_PSI, 84)
        self.dejar(tj, punto, rastro, preg2)
        self.cambio(*[FadeIn(m) for m in (ax, et, tg, ta, preg)], run_time=0.45, desplazar=UP * 0.6)
        self.wait(0.3)

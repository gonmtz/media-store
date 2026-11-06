"""
Short 27 (narrado): balanceo holandés. Oscilación acoplada de guiñada y alabeo: si el morro se
va a la derecha, el ala izquierda avanza, gana sustentación y sube (el avión alabea a la
derecha, con retraso); la deriva devuelve el morro, se pasa y el ciclo se repite al otro lado.
La flecha aumenta el efecto diedro; el amortiguador de guiñada mueve el timón para frenarlo.
Guiñada ψ y alabeo φ ~ e^(−σt)·sen(ωt), φ retrasado ~90°; curvas ilustrativas.
Vistas: desde arriba (morro arriba) y de frente (el avión viene hacia nosotros).
Render:  manim -qh --fps 60 shorts/27_balanceo_holandes/escena.py BalanceoHolandes
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403
from lib.modos import ModoBase, Y_AV, flecha  # noqa: E402

C_PSI, C_PHI, C_YD = C_GUINADA, C_ALABEO, C_CABECEO
W = 2 * PI / 3.0          # periodo ilustrativo de 3 s
TM = 12.0
Y_V = Y_AV + 0.05


def psi(t, s=0.07):
    return np.exp(-s * t) * np.sin(W * t)


def phi(t, s=0.07):
    return 1.15 * np.exp(-s * t) * np.sin(W * t - PI / 2.2) * (1 - np.exp(-2.5 * t))


class BalanceoHolandes(ModoBase):
    VOZ_JSON = Path(__file__).parent / "voz.json"

    def vistas(self, r, s=0.07, colores=False):
        sup = self.superior(1.9, (-2.2, Y_V), guinada=lambda: 13 * psi(r.get_value(), s),
                            colores_mando=colores)
        fro = self.frontal(3.4, (2.0, Y_V), alabeo=lambda: 16 * phi(r.get_value(), s),
                           colores_mando=colores)
        rot = VGroup(T("desde arriba", size=20, color=TEXTO_SEC, weight=MEDIUM).move_to([-0.75, Y_V - 0.75, 0]),
                     T("de frente", size=20, color=TEXTO_SEC, weight=MEDIUM).move_to([2.0, Y_V - 0.75, 0]))
        return sup, fro, rot

    def base(self, r0):
        r = ValueTracker(r0)
        sup, fro, rot = self.vistas(r)
        ax, et = self.grafica(TM, etiqueta_y="ángulos")
        tg = self.traza(ax, psi, C_PSI, r)
        ta = self.traza(ax, phi, C_PHI, r)
        fondo = brillo([0, Y_V - 0.3, 0], C_PSI, 3.8, 0.8)
        return r, sup, fro, rot, ax, et, tg, ta, fondo

    def construct(self):
        self.iniciar()
        r, sup, fro, rot, ax, et, tg, ta, fondo = self.base(0.9)
        preg, dest = self.gancho_texto("¿Un avión que se mece", "DE LADO A LADO?", C_PSI, 84)

        # ---------- Gancho ----------
        sello = self.sello("BALANCEO HOLANDÉS", C_PSI, DOWN * 3.95, size=50)
        self.portada(fondo, ax, et, tg, ta, sup, fro, rot, preg)
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
        # «el ala que avanza sube»
        av_ala = self.etiqueta("AVANZA Y SUBE", C_PHI, [-3.3, Y_V + 0.8, 0], size=18)
        self.avanzar(t0 + d * 0.45, r.animate.set_value(1.2))
        self.sonido("pop", -9)
        self.play(FadeIn(av_ala), FadeIn(la), r.animate.set_value(1.4), run_time=0.35, rate_func=linear)
        self.avanzar(t0 + d - 0.15, r.animate.set_value(3.2))

        # ---------- 2. Se pasa ----------
        t0, d = self.voz("b2")
        self.dejar(tit, fr, dt, av_ala)
        barra, tit, fr, dt = self.bloque_ajustado(1, "Se pasa", "La deriva lo devuelve… y se pasa",
                                                  C_PHI, dato="y vuelta a empezar, cada pocos segundos",
                                                  resaltar=["pasa"])
        self.abrir_bloque(barra, C_PHI, tit, fr, dt, r.animate.set_value(3.5))
        self.avanzar(t0 + d * 0.6, r.animate.set_value(6.5))
        ep = self.etiqueta("PERIODO: POCOS SEGUNDOS", TEXTO, ax.c2p(5.6, 1.3), size=22)
        self.sonido("pop", -9)
        self.play(FadeIn(ep, scale=1.2), r.animate.set_value(6.8), run_time=0.3, rate_func=linear)
        self.avanzar(t0 + d - 0.15, r.animate.set_value(TM * 0.72))

        # ---------- 3. Flecha y amortiguador ----------
        t0, d = self.voz("b3")
        for m in (tg, ta):
            m.clear_updaters()
        self.dejar(tit, fr, dt, ep, lg, la, sup, fro)
        barra, tit, fr, dt = self.bloque_ajustado(2, "Amortiguador", "El timón se mueve solo",
                                                  C_YD, dato="las alas en flecha lo acentúan, sobre todo a gran altitud",
                                                  resaltar=["timón", "solo"])
        r2 = ValueTracker(0.02)
        sup2, fro2, _ = self.vistas(r2, s=0.55, colores=True)
        tg2 = self.traza(ax, lambda t: psi(t, 0.55), C_YD, r2, ancho=8)
        self.abrir_bloque(barra, C_YD, tit, fr, dt, FadeIn(sup2), FadeIn(fro2),
                          tg.animate.set_stroke(opacity=0.3), ta.animate.set_stroke(opacity=0.3))
        e1 = self.etiqueta("SIN AMORTIGUADOR", C_PSI, ax.c2p(8.6, 1.25), size=22)
        self.play(FadeIn(e1), r2.animate.set_value(0.4), run_time=0.3, rate_func=linear)
        self.avanzar(t0 + d * 0.42, r2.animate.set_value(2.6))
        self.add(tg2)
        e2 = self.etiqueta("CON AMORTIGUADOR DE GUIÑADA", C_YD, ax.c2p(7.4, -0.55), size=22)
        self.sonido("pop", -9)
        self.play(FadeIn(e2, scale=1.2), run_time=0.3)
        r2.set_value(0.02)
        self.avanzar(t0 + d - 0.15, r2.animate.set_value(TM))

        # ---------- Cierre: la punta del ala dibuja un óvalo ----------
        t0, d = self.voz("cierre")
        tg2.clear_updaters()
        self.dejar(tit, fr, dt, e1, e2, tg, ta, tg2, ax, et, sup2, fro2, rot, self.tema, self.barras)
        CE = np.array([0, 1.7, 0])
        ov = Ellipse(width=3.6, height=1.5, stroke_color=C_PHI, stroke_width=4).move_to(CE)
        ov = DashedVMobject(ov, num_dashes=40)
        ang = ValueTracker(0.0)
        punta = always_redraw(lambda: Dot(CE + np.array([1.8 * np.cos(ang.get_value()),
                                                         0.75 * np.sin(ang.get_value()), 0]),
                                          radius=0.16, color=C_PHI).set_stroke(TEXTO, 3))
        ept = T("punta del ala", size=26, color=TEXTO_SEC, weight=MEDIUM).move_to(CE + DOWN * 1.15)
        preg2 = self.hud(frase_cinetica("¿Qué modo te faltaba?", size=66, resaltar=["modo"],
                                        color_resalte=C_PSI).move_to(DOWN * 0.8))
        tj = self.tarjeta("La punta del ala dibuja un óvalo", C_PHI).move_to([0, 3.5, 0])
        self.cambio(FadeIn(tj), FadeIn(ov), FadeIn(punta), FadeIn(ept), FadeIn(preg2, shift=UP * 0.3), run_time=0.7)
        self.avanzar(t0 + d * 0.35, ang.animate.set_value(2 * PI * 0.8))
        self.pulso(tj, 1.05)
        self.avanzar(t0 + d * 0.68, ang.animate.set_value(2 * PI * 1.6))
        self.pulso(preg2, 1.06)
        self.avanzar(t0 + d - 0.75, ang.animate.set_value(2 * PI * 2.2))
        r, sup, fro, rot, ax, et, tg, ta, fondo = self.base(0.9)
        preg, _ = self.gancho_texto("¿Un avión que se mece", "DE LADO A LADO?", C_PSI, 84)
        punta.clear_updaters()
        self.dejar(tj, ov, punta, ept, preg2)
        self.cambio(*[FadeIn(m) for m in (fondo, ax, et, tg, ta, sup, fro, rot, preg)], run_time=0.45,
                    desplazar=UP * 0.6)
        self.wait(0.3)

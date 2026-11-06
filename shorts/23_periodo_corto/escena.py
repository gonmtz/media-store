"""
Short 23 (narrado): modo de periodo corto (cabeceo rápido, bien amortiguado).
θ(t) = A·e^(−σt)·cos(ωt), curva ilustrativa (no de un avión concreto). Muelle = estabilidad
estática (Cm_α); amortiguador = estabilizador horizontal (Cm_q): si el morro sube, la cola baja,
el aire le llega desde abajo y su fuerza hacia arriba frena el giro.
Render:  manim -qh --fps 60 shorts/23_periodo_corto/escena.py PeriodoCorto
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403
from lib.modos import ModoBase, Y_AV, flecha  # noqa: E402
from lib.avion2d import lateral_2d  # noqa: E402

C_ALFA, C_VEL, C_MUELLE, C_AMORT = C_CABECEO, C_GUINADA, C_CABECEO, C_ALABEO
W, S, TM = 3.0, 1.0, 4.5          # rad/s, 1/s, duración simulada
ANCHO_AV = 4.6
K_ANG = 13.0                       # grados en pantalla por unidad de θ


def theta(t, s=S):
    return 0.9 * np.exp(-s * t) * np.cos(W * t)


def q(t, s=S):
    return 0.9 * np.exp(-s * t) * (-s * np.cos(W * t) - W * np.sin(W * t))


def vel(t):
    return 0.06 * np.exp(-0.4 * t) * np.sin(1.1 * t)


class PeriodoCorto(ModoBase):
    VOZ_JSON = Path(__file__).parent / "voz.json"

    def escena_base(self, r0):
        r = ValueTracker(r0)
        av = self.lateral(ANCHO_AV, (0, Y_AV), cabeceo=lambda: K_ANG * theta(r.get_value()))
        ax, et = self.grafica(TM, etiqueta_y="ángulo de ataque")
        tr = self.traza(ax, theta, C_ALFA, r)
        fondo = brillo([0, Y_AV - 0.5, 0], C_ALFA, 3.4, 0.9)
        return r, av, ax, et, tr, fondo

    def construct(self):
        self.iniciar()
        r, av, ax, et, tr, fondo = self.escena_base(0.02)
        raf = VGroup(*[flecha([-4.25 + 0.45 * k, 1.05 - 0.28 * k, 0], [-3.55 + 0.45 * k, 1.75 - 0.28 * k, 0],
                              "#CBD5E1", 8) for k in range(3)])

        # ---------- Gancho ----------
        preg, dest = self.gancho_texto("Tras una ráfaga, el morro…", "¿POR QUÉ REBOTA?", C_ALFA, 80)
        sello = self.sello("PERIODO CORTO", C_ALFA, DOWN * 3.95, size=52)
        self.portada(fondo, ax, et, tr, av, raf, preg)
        self.wait(0.15)
        self.poner_sello(sello)
        self.avanzar(2.4, r.animate.set_value(TM), raf.animate.set_opacity(0))

        # ---------- 1. Qué es ----------
        t0, d = self.voz("b1")
        barra_anim = self.poner_cabecera("MODOS DINÁMICOS · 1", 3)
        self.play(barra_anim, run_time=0.01)
        self.dejar(preg, sello, raf)
        barra, tit, fr, dt = self.bloque_ajustado(0, "Periodo corto", "Cabecea rápido; la velocidad no cambia",
                                                  C_ALFA, dato="el modo rápido del cabeceo",
                                                  resaltar=["rápido"])
        rv = ValueTracker(0.02)
        tv = self.traza(ax, vel, C_VEL, rv, ancho=6)
        self.abrir_bloque(barra, C_ALFA, tit, fr, dt, r.animate.set_value(0.02))
        e1 = self.etiqueta("ÁNGULO DE ATAQUE", C_ALFA, ax.c2p(2.3, 0.75), size=22)
        e2 = self.etiqueta("VELOCIDAD ≈ IGUAL", C_VEL, ax.c2p(3.4, 0.38), size=22)
        self.add(tv)
        self.sonido("subida", -12)
        self.play(FadeIn(e1), run_time=0.3)
        self.avanzar(t0 + d * 0.8, r.animate.set_value(TM), rv.animate.set_value(TM))
        self.play(FadeIn(e2, scale=1.2), run_time=0.3)
        self.rellenar(t0, d, margen=-0.1)

        # ---------- 2. Muelle y amortiguador ----------
        t0, d = self.voz("b2")
        tv.clear_updaters()
        self.dejar(tit, fr, dt, e1, e2, tv)
        barra, tit, fr, dt = self.bloque_ajustado(1, "Muelle y freno", "La cola frena cada giro",
                                                  C_AMORT, dato="muelle: estabilidad estática · freno: estabilizador horizontal",
                                                  resaltar=["frena"])
        base = lateral_2d(ANCHO_AV, (0, 0))
        p_cola = base.a_pantalla(33.2, 0, 1.6)
        p_morro = base.a_pantalla(4.0, 0, 0.6)

        def girar(p):
            a = K_ANG * theta(r.get_value()) * DEGREES
            R = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])
            return R @ p + np.array([0, Y_AV, 0])

        def fuerzas():
            t = r.get_value()
            g = VGroup()
            # amortiguador: fuerza en la cola proporcional a q (morro sube → cola baja → fuerza arriba)
            pc = girar(p_cola)
            g.add(flecha(pc, pc + UP * 0.4 * q(t), C_AMORT, 10))
            # muelle: momento que devuelve el morro, proporcional a −θ
            pm = girar(p_morro)
            g.add(flecha(pm, pm + DOWN * 1.3 * theta(t), C_MUELLE, 10))
            return g
        fz = always_redraw(fuerzas)
        em = self.etiqueta("MUELLE", C_MUELLE, [2.9, Y_AV + 1.15, 0], size=24)
        ea = self.etiqueta("AMORTIGUADOR (COLA)", C_AMORT, [-2.2, Y_AV + 1.15, 0], size=24)
        self.abrir_bloque(barra, C_AMORT, tit, fr, dt, r.animate.set_value(0.25))
        self.add(fz)
        self.sonido("pop", -9)
        self.play(FadeIn(em), FadeIn(ea), run_time=0.3)
        self.avanzar(t0 + d - 0.2, r.animate.set_value(TM))

        # ---------- 3. Pocos segundos ----------
        t0, d = self.voz("b3")
        self.dejar(tit, fr, dt, em, ea, fz)
        barra, tit, fr, dt = self.bloque_ajustado(2, "Pocos segundos", "Se apaga en una o dos oscilaciones",
                                                  C_ALFA, dato="curvas ilustrativas, no de un avión concreto",
                                                  resaltar=["apaga"])
        r2 = ValueTracker(0.02)
        sin_am = self.traza(ax, lambda t: theta(t, 0.12), C_AMORT, r2, ancho=5)
        self.abrir_bloque(barra, C_ALFA, tit, fr, dt, r.animate.set_value(0.02))
        e3 = self.etiqueta("CON LA COLA", C_ALFA, ax.c2p(2.2, 0.75), size=22)
        self.play(FadeIn(e3), run_time=0.3)
        self.avanzar(t0 + d * 0.5, r.animate.set_value(TM))
        # «Sin ese amortiguador…»
        self.add(sin_am)
        e4 = self.etiqueta("SIN AMORTIGUADOR", C_AMORT, ax.c2p(3.0, -1.1), size=22)
        self.sonido("golpe", -12)
        self.play(FadeIn(e4, scale=1.2), run_time=0.3)
        self.avanzar(t0 + d - 0.15, r2.animate.set_value(TM))

        # ---------- Cierre ----------
        t0, d = self.voz("cierre")
        sin_am.clear_updaters()
        self.dejar(tit, fr, dt, e3, e4, sin_am, tr, ax, et, av, fondo, self.tema, self.barras)
        tj = VGroup(self.tarjeta("Muelle: la estabilidad estática", C_MUELLE),
                    self.tarjeta("Amortiguador: la cola", C_AMORT)).arrange(DOWN, buff=0.3).move_to([0, 2.2, 0])
        preg2 = self.hud(frase_cinetica("¿Lo has sentido en un vuelo con turbulencia?", size=58,
                                        resaltar=["turbulencia?"], color_resalte=C_ALFA).move_to(DOWN * 1.1))
        self.cambio(LaggedStart(*[FadeIn(x, shift=RIGHT * 0.4) for x in tj], lag_ratio=0.4),
                    FadeIn(preg2, shift=UP * 0.3), run_time=0.8)
        self.hasta(t0, d * 0.45)
        self.pulso(tj[1], 1.05)
        self.hasta(t0, d * 0.75)
        self.pulso(preg2, 1.05)
        self.hasta(t0, d - 0.7)
        r, av, ax, et, tr, fondo = self.escena_base(0.02)
        preg, _ = self.gancho_texto("Tras una ráfaga, el morro…", "¿POR QUÉ REBOTA?", C_ALFA, 80)
        raf = VGroup(*[flecha([-4.25 + 0.45 * k, 1.05 - 0.28 * k, 0], [-3.55 + 0.45 * k, 1.75 - 0.28 * k, 0],
                              "#CBD5E1", 8) for k in range(3)])
        self.dejar(tj, preg2)
        self.cambio(*[FadeIn(m) for m in (fondo, ax, et, tr, av, raf, preg)], run_time=0.45,
                    desplazar=UP * 0.6)
        self.wait(0.3)

"""
Short 37 (narrado): estela turbulenta. Avión 3D visto desde atrás con los dos vórtices de punta
(desde atrás: el de la derecha gira antihorario y el de la izquierda horario; suben por fuera y
bajan por dentro). Los vórtices bajan unos 2 m/s (dibujo: escala no real).
Intensidad ∝ peso / (densidad · velocidad · envergadura). Un avión ligero dentro de un vórtice
alabea en el sentido de giro del vórtice. Separación de ejemplo (OACI): tras un pesado, un ligero
espera del orden de 2–3 min al despegar o ~11 km (6 NM) en aproximación.
Render:  manim -qh --fps 60 shorts/37_estelas/escena.py Estelas
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403
from lib.modos import ModoBase, flecha  # noqa: E402
from lib import avion as A  # noqa: E402

C_VOR, C_PEQ, C_SEP = C_CABECEO, C_ALABEO, C_GUINADA
PUNTAS = [A.punto_ala(16.9, s, 0.95) for s in (1, -1)]     # izquierda, derecha (ejes del avión)
Y_AV = 0.9


class Estelas(ModoBase):
    VOZ_JSON = Path(__file__).parent / "voz.json"

    def detras(self, reloj, baja, fuerza, vis):
        """Avión grande desde atrás + dos vórtices que bajan `baja` (pantalla) y crecen con `fuerza`."""
        av = self.avion3d(campo=41, alto_px=760, centro=(0, Y_AV), azimut=180, elevacion=5,
                          colores_mando=False)
        q = av.a_pantalla(PUNTAS)
        # desde atrás el ala izquierda queda a la izquierda de la pantalla
        izq, der = (q[0], q[1]) if q[0][0] < q[1][0] else (q[1], q[0])

        def vort():
            g = VGroup()
            tt = reloj.get_value()
            b = baja.get_value()
            for p, sen in ((izq, -1), (der, 1)):
                c = p + DOWN * b + RIGHT * (-sen) * 0.25 * b
                r = 0.45 + 0.35 * fuerza.get_value()
                for k in range(2):
                    g.add(espiral(c, r, fase=sen * 3.0 * tt + k * PI, sentido=sen, color=C_VOR,
                                  ancho=5, opacidad=vis.get_value()))
            return g
        return av, always_redraw(vort), (izq, der)

    def construct(self):
        self.iniciar()
        reloj = ValueTracker(0.0)
        reloj.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(reloj)
        baja, fuerza, vis = ValueTracker(0.15), ValueTracker(0.5), ValueTracker(0.95)
        av, vo, (izq, der) = self.detras(reloj, baja, fuerza, vis)
        fondo = brillo([0, Y_AV - 0.6, 0], C_VOR, 3.8, 0.8)
        preg, dest = self.gancho_texto("¿Por qué esperan tras", "UN AVIÓN GRANDE?", C_VOR, 84)
        sello = self.sello("ESTELA TURBULENTA", C_VOR, DOWN * 3.95, size=52)

        # ---------- Gancho ----------
        self.portada(fondo, av, vo, preg)
        self.wait(0.15)
        self.poner_sello(sello)
        self.avanzar(2.2, baja.animate.set_value(0.3))

        # ---------- 1. Dos remolinos ----------
        t0, d = self.voz("b1")
        self.play(self.poner_cabecera("ESTELA TURBULENTA", 3), run_time=0.01)
        self.dejar(preg, sello)
        barra, tit, fr, dt = self.bloque_ajustado(0, "Dos remolinos", "Giran en sentidos opuestos y bajan",
                                                  C_VOR, dato="unos 2 m/s hacia abajo · vista desde atrás",
                                                  resaltar=["opuestos", "bajan"])
        self.abrir_bloque(barra, C_VOR, tit, fr, dt, baja.animate.set_value(0.45))
        ev = VGroup(self.etiqueta("HORARIO", C_VOR, izq + np.array([0.3, -1.25, 0]), size=20),
                    self.etiqueta("ANTIHORARIO", C_VOR, der + np.array([-0.5, -1.25, 0]), size=20))
        self.sonido("pop", -9)
        self.play(FadeIn(ev, shift=UP * 0.2), baja.animate.set_value(0.5), run_time=0.4, rate_func=linear)
        self.avanzar(t0 + d * 0.5, baja.animate.set_value(0.6))
        self.play(FadeOut(ev), run_time=0.3)
        self.avanzar(t0 + d * 0.6, baja.animate.set_value(1.1))
        fb = VGroup(*[flecha(p + np.array([s * 0.0, -0.9, 0]), p + np.array([0, -1.9, 0]), TEXTO_SEC, 7)
                      for p, s in ((izq, 1), (der, -1))])
        eb = self.etiqueta("≈ 2 m/s", TEXTO, [0, Y_AV - 1.9, 0], size=26)
        self.play(GrowArrow(fb[0]), GrowArrow(fb[1]), FadeIn(eb), baja.animate.set_value(1.25),
                  run_time=0.5, rate_func=linear)
        self.avanzar(t0 + d - 0.15, baja.animate.set_value(1.7))

        # ---------- 2. Peligro para el pequeño ----------
        t0, d = self.voz("b2")
        self.dejar(tit, fr, dt, fb, eb)
        barra, tit, fr, dt = self.bloque_ajustado(1, "Más pesado, más fuerte", "Un avión pequeño puede alabear sin control",
                                                  C_PEQ, dato="intensidad ∝ peso / (velocidad · envergadura)",
                                                  resaltar=["alabear"])
        self.abrir_bloque(barra, C_PEQ, tit, fr, dt, baja.animate.set_value(0.4), fuerza.animate.set_value(0.8),
                          run_time=0.7)
        al = ValueTracker(0.0)
        cpeq = izq + DOWN * 0.4 + RIGHT * 0.1
        peq = self.avion3d(campo=14, alto_px=500, centro=(cpeq[0], cpeq[1]), azimut=180, elevacion=5,
                           colores_mando=False, ancho_pantalla=2.4, alabeo=al,
                           resaltar={"fuselaje": C_PEQ})
        self.hasta(t0, d * 0.4)
        self.sonido("whoosh", -10)
        self.play(FadeIn(peq, scale=0.6), run_time=0.4)
        self.play(al.animate.set_value(55), run_time=1.1, rate_func=rate_functions.ease_in_quad)
        ep = self.etiqueta("¡ALABEO!", C_PEQ, cpeq + np.array([0.2, -1.05, 0]), size=24)
        self.sonido("golpe", -12)
        self.play(FadeIn(ep, scale=1.2), al.animate.set_value(75), run_time=0.4)
        self.avanzar(t0 + d - 0.15, al.animate.set_value(95))

        # ---------- 3. Separación ----------
        t0, d = self.voz("b3")
        vo.clear_updaters()
        self.dejar(tit, fr, dt, av, vo, peq, ep, fondo)
        barra, tit, fr, dt = self.bloque_ajustado(2, "Separación", "Tras un muy pesado, el ligero espera",
                                                  C_SEP, dato="ejemplo OACI: ≈ 2–3 min o ≈ 11 km (6 NM)",
                                                  resaltar=["espera"])
        x_g = ValueTracker(1.9)
        grande = self.avion3d(campo=34, alto_px=600, centro=lambda: (x_g.get_value(), 1.0), azimut=-90,
                              elevacion=4, colores_mando=False, ancho_pantalla=5.2)
        ligero = self.avion3d(campo=22, alto_px=500, centro=(-3.3, 0.55), azimut=-90, elevacion=4,
                              colores_mando=False, ancho_pantalla=2.0, resaltar={"fuselaje": C_PEQ})

        def estela():
            g = VGroup()
            tt = reloj.get_value()
            xc = x_g.get_value() - 2.0
            for i in range(9):
                x = xc - 0.55 * i
                if x < -2.4:
                    break
                op = 0.85 * (1 - i / 9)
                g.add(espiral([x, 0.85 - 0.1 * i, 0], 0.22 + 0.02 * i, fase=3 * tt + i, sentido=1,
                              color=C_VOR, ancho=3, opacidad=op, punta=False))
            return g
        es = always_redraw(estela)
        sep = VGroup(DoubleArrow([-3.1, -0.75, 0], [x_g.get_value() - 0.4, -0.75, 0], buff=0, color=C_SEP,
                                 stroke_width=5, tip_length=0.2),
                     T("≈ 11 km  ·  2–3 min", size=34, color=C_SEP, weight=HEAVY).move_to([-0.3, -1.3, 0]))
        nombres = VGroup(self.etiqueta("PESADO", TEXTO, [2.0, 2.15, 0], size=20),
                         self.etiqueta("LIGERO", C_PEQ, [-3.3, 1.35, 0], size=20))
        self.abrir_bloque(barra, C_SEP, tit, fr, dt, FadeIn(grande), FadeIn(ligero), FadeIn(es), FadeIn(nombres),
                          x_g.animate.set_value(2.0), run_time=0.7)
        self.hasta(t0, d * 0.45)
        self.sonido("pop", -9)
        self.play(GrowFromCenter(sep[0]), FadeIn(sep[1]), x_g.animate.set_value(2.15), run_time=0.5)
        self.hasta(t0, d * 0.7)
        self.pulso(sep[1], 1.08)
        self.avanzar(t0 + d - 0.15, x_g.animate.set_value(2.4))

        # ---------- Cierre ----------
        t0, d = self.voz("cierre")
        es.clear_updaters()
        baja2, fuerza2, vis2 = ValueTracker(0.6), ValueTracker(0.8), ValueTracker(0.9)
        av2, vo2, _ = self.detras(reloj, baja2, fuerza2, vis2)
        fondo2 = brillo([0, Y_AV - 0.6, 0], C_VOR, 3.8, 0.8)
        self.dejar(tit, fr, dt, grande, ligero, es, sep, nombres, self.tema, self.barras)
        tj = self.tarjeta("Invisibles y duran minutos", C_VOR, size=40).move_to([0, -1.25, 0])
        preg2 = self.hud(frase_cinetica("¿Lo sabías?", size=72, resaltar=["sabías?"],
                                        color_resalte=C_VOR).move_to(DOWN * 3.6))
        self.cambio(FadeIn(fondo2), FadeIn(av2), FadeIn(vo2), FadeIn(tj, shift=UP * 0.2), FadeIn(preg2, shift=UP * 0.3),
                    run_time=0.6)
        self.avanzar(t0 + d * 0.5, vis2.animate.set_value(0.2), baja2.animate.set_value(0.8))
        self.pulso(preg2, 1.06)
        self.avanzar(t0 + d - 0.75, vis2.animate.set_value(0.95), baja2.animate.set_value(0.3))
        preg, _ = self.gancho_texto("¿Por qué esperan tras", "UN AVIÓN GRANDE?", C_VOR, 84)
        self.dejar(tj, preg2)
        self.cambio(FadeIn(preg), run_time=0.45, desplazar=UP * 0.6)
        self.wait(0.3)

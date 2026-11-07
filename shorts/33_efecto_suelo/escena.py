"""
Short 33 (narrado): efecto suelo. Por debajo de una envergadura (y sobre todo de media), el suelo
frena el flujo descendente y los vórtices de punta: menos resistencia inducida y, a igual ángulo
de ataque, algo más de sustentación. Barra de resistencia inducida con el factor de McCormick
φ = (16h/b)² / (1 + (16h/b)²) (aproximación). Vórtices y flechas: dibujo cualitativo.
Vista de frente: el avión viene hacia nosotros (vórtice de la izquierda de la pantalla, horario).
Render:  manim -qh --fps 60 shorts/33_efecto_suelo/escena.py EfectoSuelo
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403
from lib.modos import ModoBase, flecha  # noqa: E402
from lib import avion as A  # noqa: E402

C_VOR, C_DOWN, C_SUELO, C_DRAG = C_CABECEO, C_GUINADA, "#475569", C_ALABEO
Y_S = -1.5                       # suelo
B_PANT = 4.6                     # envergadura en pantalla (aprox.)


def phi(h_b):
    x = 16 * max(h_b, 1e-3)
    return x * x / (1 + x * x)


class EfectoSuelo(ModoBase):
    VOZ_JSON = Path(__file__).parent / "voz.json"

    def base(self, h0):
        h = ValueTracker(h0)                # altura del ala sobre el suelo (en envergaduras)
        reloj = ValueTracker(0.0)
        reloj.add_updater(lambda m, dt: m.increment_value(dt))
        av = self.avion3d(campo=38, alto_px=760, centro=lambda: (0, Y_S + 0.55 + h.get_value() * B_PANT),
                          colores_mando=False, azimut=8, elevacion=4, tren=True)

        def flujo():
            hb = h.get_value()
            yw = Y_S + 0.35 + hb * B_PANT
            k = phi(hb)
            g = VGroup()
            for s, x in ((-1, -B_PANT / 2), (1, B_PANT / 2)):
                r = 0.18 + 0.4 * k
                g.add(espiral([x + s * 0.05, yw, 0], r, fase=reloj.get_value() * 4 * (-s), sentido=s,
                              color=C_VOR, ancho=4, opacidad=0.9))
            for x in np.linspace(-1.5, 1.5, 5):
                largo = min(0.9 * k + 0.1, max(0.1, yw - Y_S - 0.25))
                g.add(flecha([x, yw - 0.25, 0], [x, yw - 0.25 - largo, 0], C_DOWN, 6))
            return g
        fl = always_redraw(flujo)
        suelo = VGroup(Rectangle(width=9.8, height=0.4, stroke_width=0, fill_color="#1E293B",
                                 fill_opacity=1).move_to([0, Y_S - 0.2, 0]),
                       Line([-4.8, Y_S, 0], [4.8, Y_S, 0], color=C_SUELO, stroke_width=6))
        fondo = brillo([0, 1.0, 0], C_VOR, 3.8, 0.8)
        return h, reloj, av, fl, suelo, fondo

    def construct(self):
        self.iniciar()
        h, reloj, av, fl, suelo, fondo = self.base(0.12)
        self.add(reloj)
        preg, dest = self.gancho_texto("¿Por qué flota antes", "DE TOCAR LA PISTA?", C_VOR, 80)
        sello = self.sello("EFECTO SUELO", C_VOR, DOWN * 3.95, size=54)

        # ---------- Gancho ----------
        self.portada(fondo, suelo, av, fl, preg)
        self.wait(0.15)
        self.poner_sello(sello)
        self.avanzar(2.45, h.animate.set_value(0.1))

        # ---------- 1. Menos de una envergadura ----------
        t0, d = self.voz("b1")
        self.play(self.poner_cabecera("EFECTO SUELO", 3), run_time=0.01)
        self.dejar(preg, sello)
        barra, tit, fr, dt = self.bloque_ajustado(0, "Cerca del suelo", "A menos de una envergadura",
                                                  C_VOR, dato="se nota de verdad por debajo de media envergadura",
                                                  resaltar=["envergadura"])

        def cotas():
            hb = h.get_value()
            yw = Y_S + 0.35 + hb * B_PANT
            g = VGroup(DoubleArrow([-B_PANT / 2, yw + 1.25, 0], [B_PANT / 2, yw + 1.25, 0], buff=0,
                                   color=TEXTO_SEC, stroke_width=3, tip_length=0.15),
                       T("b (envergadura)", size=22, color=TEXTO_SEC, weight=BOLD).move_to([0, yw + 1.5, 0]))
            if hb > 0.06:
                g.add(DoubleArrow([B_PANT / 2 + 0.45, Y_S, 0], [B_PANT / 2 + 0.45, yw, 0], buff=0,
                                  color=C_VOR, stroke_width=4, tip_length=0.15),
                      T("h", size=30, color=C_VOR, weight=HEAVY).move_to([B_PANT / 2 + 0.75, (Y_S + yw) / 2, 0]))
            return g
        co = always_redraw(cotas)
        self.abrir_bloque(barra, C_VOR, tit, fr, dt, h.animate.set_value(0.45), run_time=0.8)
        self.add(co)
        self.avanzar(t0 + d * 0.5, h.animate.set_value(0.38))
        self.sonido("whoosh_suave", -12)
        self.avanzar(t0 + d - 0.15, h.animate.set_value(0.2))

        # ---------- 2. Menos resistencia ----------
        t0, d = self.voz("b2")
        co.clear_updaters()
        self.dejar(tit, fr, dt, co)
        barra, tit, fr, dt = self.bloque_ajustado(1, "El suelo frena", "Menos remolinos y menos aire hacia abajo",
                                                  C_DRAG, dato="resistencia inducida: aproximación de McCormick",
                                                  resaltar=["remolinos"])

        def barra_drag():
            k = phi(h.get_value())
            fondo_b = RoundedRectangle(width=5.0, height=0.36, corner_radius=0.12, stroke_color="#334155",
                                       stroke_width=2, fill_opacity=0).move_to([0.3, 1.95, 0])
            llena = RoundedRectangle(width=max(0.05, 5.0 * k), height=0.36, corner_radius=0.12,
                                     stroke_width=0, fill_color=C_DRAG, fill_opacity=0.9)
            llena.align_to(fondo_b, LEFT).move_to([fondo_b.get_left()[0] + max(0.05, 5.0 * k) / 2, 1.95, 0])
            et = T("RESISTENCIA INDUCIDA", size=20, color=C_DRAG, weight=HEAVY).next_to(fondo_b, UP, buff=0.1)
            return VGroup(fondo_b, llena, et)
        bd = always_redraw(barra_drag)
        self.abrir_bloque(barra, C_DRAG, tit, fr, dt, h.animate.set_value(0.42), FadeIn(bd), run_time=0.8)
        self.avanzar(t0 + d * 0.7, h.animate.set_value(0.05))
        em = self.etiqueta("MÁS SUSTENTACIÓN", C_VOR, [0, 0.9, 0], size=22)
        self.sonido("pop", -9)
        self.play(FadeIn(em, scale=1.2), run_time=0.3)
        self.avanzar(t0 + d - 0.15, h.animate.set_value(0.04))

        # ---------- 3. Flota ----------
        t0, d = self.voz("b3")
        bd.clear_updaters()
        fl.clear_updaters()
        self.dejar(tit, fr, dt, bd, em, fl, av)
        barra, tit, fr, dt = self.bloque_ajustado(2, "Flota", "En la recogida parece que no quiere bajar",
                                                  C_VOR, dato="si llega rápido, alarga el aterrizaje",
                                                  resaltar=["flota", "bajar"])
        u = ValueTracker(0.0)

        def y_tray(x):            # senda que se aplana cerca del suelo
            return Y_S + 0.15 + 1.6 * np.exp(-(x + 4.6) / 1.3)
        tray = DashedVMobject(FunctionGraph(y_tray, x_range=[-4.6, 4.6], color=C_VOR, stroke_width=3),
                              num_dashes=45).set_stroke(opacity=0.6)

        def pos():
            x = -2.3 + 5.6 * u.get_value()
            return (x, y_tray(x) + 0.55)
        av2 = self.avion3d(campo=70, alto_px=620, centro=pos, colores_mando=False, azimut=-90,
                           elevacion=3, tren=True, cabeceo=lambda: 3 + 3 * u.get_value(), flap=30)
        ef = self.etiqueta("FLOTA", C_VOR, [1.2, Y_S + 1.2, 0], size=26)
        self.abrir_bloque(barra, C_VOR, tit, fr, dt, FadeIn(tray), FadeIn(av2))
        self.avanzar(t0 + d * 0.45, u.animate.set_value(0.45))
        self.sonido("pop", -9)
        self.play(FadeIn(ef, scale=1.2), u.animate.set_value(0.5), run_time=0.3, rate_func=linear)
        self.avanzar(t0 + d - 0.15, u.animate.set_value(0.9))

        # ---------- Cierre ----------
        t0, d = self.voz("cierre")
        h, reloj2, av, fl, suelo2, fondo2 = self.base(0.1)
        self.add(reloj2)
        self.dejar(tit, fr, dt, tray, av2, ef, self.tema, self.barras)
        tj = self.tarjeta("Ekranoplanos: siempre en efecto suelo", C_VOR, size=40).move_to([0, 3.4, 0])
        preg2 = self.hud(frase_cinetica("¿Los conocías?", size=72, resaltar=["conocías?"],
                                        color_resalte=C_VOR).move_to(DOWN * 3.6))
        self.cambio(FadeIn(av), FadeIn(fl), FadeIn(tj, shift=DOWN * 0.3), FadeIn(preg2, shift=UP * 0.3),
                    run_time=0.7)
        self.avanzar(t0 + d * 0.5, h.animate.set_value(0.14))
        self.pulso(preg2, 1.06)
        self.avanzar(t0 + d - 0.75, h.animate.set_value(0.1))
        preg, _ = self.gancho_texto("¿Por qué flota antes", "DE TOCAR LA PISTA?", C_VOR, 80)
        self.dejar(tj, preg2)
        self.cambio(FadeIn(preg), run_time=0.45, desplazar=UP * 0.6)
        self.wait(0.3)

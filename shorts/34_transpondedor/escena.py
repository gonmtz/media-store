"""
Short 34 (narrado): el transpondedor y los códigos 7500, 7600 y 7700.
Pantalla de radar con barrido; cada avión lleva su etiqueta con el código de cuatro cifras
octales (0–7, 4096 combinaciones). Al marcar 7700 la traza se resalta en rojo.
La regla para recordarlos (75 secuestro, 76 sin radio, 77 socorro) no es oficial: se rotula.
Render:  manim -qh --fps 60 shorts/34_transpondedor/escena.py Transpondedor
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403
from lib.modos import ModoBase, flecha  # noqa: E402

C_RAD, C_75, C_76, C_77 = C_CABECEO, C_ALABEO, C_GUINADA, "#EF4444"
RC, RR = np.array([0.0, 0.85, 0.0]), 2.25          # centro y radio del radar
Y_XPDR = -1.95
TRAZAS = [  # (ángulo°, radio relativo, indicativo, código propio)
    (75, 0.6, "AMX402", "4521"),
    (165, 0.65, "VOI915", "2163"),
    (235, 0.5, "IBE6401", "3307"),
    (300, 0.8, "AAL73", "1450"),
]


class Transpondedor(ModoBase):
    VOZ_JSON = Path(__file__).parent / "voz.json"

    # ---------- piezas ----------
    def radar(self, reloj, emerg, codigo_0):
        """Pantalla de radar. emerg (0–1) pone en rojo la traza 0 con el código codigo_0()."""
        def dib():
            tt = reloj.get_value()
            g = VGroup()
            g.add(Circle(radius=RR, stroke_color=C_RAD, stroke_width=3, fill_color="#06121F",
                         fill_opacity=0.95).move_to(RC))
            for r in (0.33, 0.66):
                g.add(Circle(radius=RR * r, stroke_color=C_RAD, stroke_width=1.5).set_stroke(opacity=0.35).move_to(RC))
            for a in range(0, 360, 45):
                u = np.array([np.cos(np.radians(a)), np.sin(np.radians(a)), 0])
                g.add(Line(RC + u * 0.12, RC + u * RR, stroke_color=C_RAD, stroke_width=1).set_stroke(opacity=0.25))
            ang = -tt * 1.6                              # barrido horario
            for k in range(14):                          # estela del barrido
                a = ang + k * 0.04
                g.add(Line(RC, RC + RR * np.array([np.cos(a), np.sin(a), 0]), stroke_color=C_RAD,
                           stroke_width=6).set_stroke(opacity=0.5 * (1 - k / 14)))
            e = emerg.get_value()
            for i, (a, r, ind, cod) in enumerate(TRAZAS):
                p = RC + RR * r * np.array([np.cos(np.radians(a)), np.sin(np.radians(a)), 0])
                roja = i == 0 and e > 0.01
                col = interpolate_color(ManimColor(TEXTO), ManimColor(C_77), e) if i == 0 else TEXTO
                apagar = 1 - 0.55 * e if i != 0 else 1
                c = cod if i != 0 else codigo_0()
                g.add(Square(0.16, stroke_width=0, fill_color=col, fill_opacity=apagar).rotate(PI / 4).move_to(p))
                et = VGroup(T(ind, size=25, color=col, weight=HEAVY),
                            T(c, size=24, color=C_77 if roja else TEXTO_SEC, weight=BOLD)
                            ).arrange(DOWN, buff=0.04, aligned_edge=LEFT).set_opacity(apagar)
                et.next_to(p, RIGHT if np.cos(np.radians(a)) < 0.5 else LEFT, buff=0.12)
                g.add(Line(p, et.get_corner(DL if np.cos(np.radians(a)) < 0.5 else DR), stroke_color=col,
                           stroke_width=1.5).set_stroke(opacity=0.6 * apagar), et)
                if roja:
                    fase = (tt * 1.4) % 1.0
                    for f in (fase, (fase + 0.5) % 1.0):
                        g.add(Circle(radius=0.15 + 0.55 * f, stroke_color=C_77, stroke_width=4)
                              .set_stroke(opacity=e * (1 - f)).move_to(p))
            return g
        return always_redraw(dib)

    def xpdr(self, codigo, color=lambda: TEXTO):
        """Panel del transpondedor con las cuatro cifras de codigo() (cadena)."""
        def dib():
            c = codigo()
            col = color()
            caja = RoundedRectangle(width=5.6, height=1.05, corner_radius=0.18, fill_color="#111827",
                                    fill_opacity=1, stroke_color="#334155", stroke_width=3).move_to([0, Y_XPDR, 0])
            et = T("XPDR", size=26, color=TEXTO_SEC, weight=HEAVY).move_to([-2.05, Y_XPDR, 0])
            g = VGroup(caja, et)
            for i, ch in enumerate(c):
                x = -0.75 + i * 0.85
                g.add(RoundedRectangle(width=0.68, height=0.8, corner_radius=0.1, fill_color="#020617",
                                       fill_opacity=1, stroke_width=0).move_to([x, Y_XPDR, 0]),
                      T(ch, size=56, color=col, weight=HEAVY, font=F_TIT).move_to([x, Y_XPDR, 0]))
            g.add(Dot([2.35, Y_XPDR, 0], radius=0.07, color=C_76 if c != "7700" else C_77))
            return g
        return always_redraw(dib)

    def codigo_tarjeta(self, cod, nombre, color, ancho=7.0):
        fondo = RoundedRectangle(width=ancho, height=1.05, corner_radius=0.22, fill_color="#141E31",
                                 fill_opacity=1, stroke_color=color, stroke_width=4)
        n = T(cod, size=58, color=color, weight=HEAVY, font=F_TIT)
        t = T(nombre, size=36, color=TEXTO, weight=BOLD)
        fila = VGroup(n, t).arrange(RIGHT, buff=0.45)
        if fila.width > ancho - 0.5:
            fila.scale_to_fit_width(ancho - 0.5)
        return VGroup(fondo, fila.move_to(fondo))

    # ---------- escena ----------
    def construct(self):
        self.iniciar()
        reloj = ValueTracker(0.0)
        reloj.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(reloj)
        emerg = ValueTracker(0.0)
        estado = {"cod": "7700", "radar0": "4521"}
        rad = self.radar(reloj, emerg, lambda: estado["radar0"])
        xp = self.xpdr(lambda: estado["cod"], lambda: C_77 if estado["cod"] == "7700" else TEXTO)
        fondo = brillo(RC, C_RAD, 3.6, 0.8)
        preg, dest = self.gancho_texto("¿Qué significa", "7700?", C_77, 110)
        sello = self.sello("TRANSPONDEDOR", C_RAD, DOWN * 3.95, size=54)

        # ---------- Gancho ----------
        self.portada(fondo, rad, xp, preg)
        self.wait(0.15)
        self.poner_sello(sello)
        self.pulso(dest, 1.12)
        self.hasta(0, 2.6)

        # ---------- 1. Código de cuatro cifras ----------
        t0, d = self.voz("b1")
        self.play(self.poner_cabecera("EL TRANSPONDEDOR", 3), run_time=0.01)
        self.dejar(preg, sello)
        barra, tit, fr, dt = self.bloque_ajustado(0, "Responde al radar", "Un código de cuatro cifras, del 0 al 7",
                                                  C_RAD, dato="4096 combinaciones posibles",
                                                  resaltar=["cuatro", "cifras"])
        estado["cod"] = "4521"
        self.abrir_bloque(barra, C_RAD, tit, fr, dt)
        # interrogación y respuesta con la traza propia
        p0 = RC + RR * 0.6 * np.array([np.cos(np.radians(75)), np.sin(np.radians(75)), 0])
        anillo = VGroup(*[Circle(radius=0.2, stroke_color=C_RAD, stroke_width=5).move_to(p0) for _ in range(2)])
        self.hasta(t0, d * 0.35)
        self.sonido("pop", -9)
        self.play(*[a.animate(rate_func=rate_functions.ease_out_cubic).scale(4).set_stroke(opacity=0) for a in anillo],
                  run_time=0.8)
        self.remove(anillo)
        caja = SurroundingRectangle(xp[2:10], color=C_RAD, buff=0.1, corner_radius=0.12)
        self.play(Create(caja), run_time=0.5)
        self.hasta(t0, d * 0.7)
        self.pulso(caja, 1.06)
        self.rellenar(t0, d)

        # ---------- 2. Los tres códigos ----------
        t0, d = self.voz("b2")
        rad.clear_updaters()
        self.dejar(tit, fr, dt, rad, caja, fondo)
        barra, tit, fr, dt = self.bloque_ajustado(1, "Tres especiales", "Códigos que piden ayuda sin hablar",
                                                  C_77, dato="códigos de la OACI, iguales en todo el mundo",
                                                  resaltar=["ayuda"])
        tjs = VGroup(self.codigo_tarjeta("7500", "Interferencia ilícita", C_75),
                     self.codigo_tarjeta("7600", "Fallo de radio", C_76),
                     self.codigo_tarjeta("7700", "Emergencia general", C_77)
                     ).arrange(DOWN, buff=0.3).move_to([0, 0.6, 0])
        self.abrir_bloque(barra, C_77, tit, fr, dt)
        for i, (cod, f) in enumerate((("7500", 0.2), ("7600", 0.47), ("7700", 0.7))):
            self.hasta(t0, d * f)
            estado["cod"] = cod
            self.sonido("tic", -8)
            self.play(FadeIn(tjs[i], shift=RIGHT * 0.5), run_time=0.4)
            self.pulso(tjs[i], 1.05)
        self.rellenar(t0, d)

        # ---------- 3. Prioridad ----------
        t0, d = self.voz("b3")
        self.dejar(tit, fr, dt, tjs)
        barra, tit, fr, dt = self.bloque_ajustado(2, "Prioridad", "El avión se resalta en la pantalla del controlador",
                                                  C_77, dato="el controlador lo ve al instante",
                                                  resaltar=["resalta"])
        estado["radar0"] = "7700"
        rad2 = self.radar(reloj, emerg, lambda: estado["radar0"])
        fondo2 = brillo(RC, C_77, 3.6, 0.6)
        self.abrir_bloque(barra, C_77, tit, fr, dt, FadeIn(rad2), FadeIn(fondo2))
        self.sonido("golpe", -12)
        self.play(emerg.animate.set_value(1.0), run_time=0.6)
        eme = self.etiqueta("EMERGENCIA", C_77, RC + DOWN * (RR - 0.45), size=24)
        self.play(FadeIn(eme, scale=1.2), run_time=0.3)
        self.hasta(t0, d * 0.75)
        self.pulso(eme, 1.12)
        self.rellenar(t0, d)

        # ---------- Cierre ----------
        t0, d = self.voz("cierre")
        rad2.clear_updaters()
        self.dejar(tit, fr, dt, rad2, eme, fondo2, self.tema, self.barras)
        regla = VGroup(self.codigo_tarjeta("75", "Secuestro", C_75),
                       self.codigo_tarjeta("76", "Sin radio", C_76),
                       self.codigo_tarjeta("77", "Socorro", C_77)).arrange(DOWN, buff=0.3).move_to([0, 2.6, 0])
        nota = self.hud(T("regla para recordarlos (no oficial)", size=26, color=TEXTO_SEC, weight=MEDIUM)
                        .next_to(regla, UP, buff=0.3))
        preg2 = self.hud(frase_cinetica("¿Los conocías?", size=72, resaltar=["conocías?"],
                                        color_resalte=C_77).move_to(DOWN * 3.6))
        self.cambio(LaggedStart(*[FadeIn(x, shift=RIGHT * 0.4) for x in regla], lag_ratio=0.25),
                    FadeIn(nota), FadeIn(preg2, shift=UP * 0.3), run_time=0.8)
        self.hasta(t0, d * 0.22)
        estado["cod"] = "7500"
        self.pulso(regla[0], 1.05)
        self.hasta(t0, d * 0.42)
        estado["cod"] = "7600"
        self.pulso(regla[1], 1.05)
        self.hasta(t0, d * 0.6)
        estado["cod"] = "7700"
        self.pulso(regla[2], 1.05)
        self.hasta(t0, d * 0.78)
        self.pulso(preg2, 1.06)
        self.hasta(t0, d - 0.75)
        rad3 = self.radar(reloj, ValueTracker(0.0), lambda: "4521")
        fondo3 = brillo(RC, C_RAD, 3.6, 0.8)
        preg, _ = self.gancho_texto("¿Qué significa", "7700?", C_77, 110)
        self.dejar(regla, nota, preg2)
        self.cambio(FadeIn(rad3), FadeIn(fondo3), FadeIn(preg), run_time=0.45, desplazar=UP * 0.6)
        self.wait(0.3)

"""
Short 32 (narrado): número de Reynolds. Re = V·L/ν (ν ≈ 1,5·10⁻⁵ m²/s).
Avión: 70 m/s × 4 m → ≈ 2·10⁷. Mosquito: 1 m/s × 1 mm → ≈ 70. Escala logarítmica.
Insectos: batido rápido con un remolino de borde de ataque pegado al ala (dibujo cualitativo).
Render:  manim -qh --fps 60 shorts/32_reynolds/escena.py Reynolds
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403
from lib.modos import ModoBase, flecha  # noqa: E402

C_AV, C_MOS, C_RE = C_CABECEO, C_ALABEO, C_GUINADA


def mosquito(escala=1.0, aleteo=0.0):
    """Mosquito vectorial de perfil (cabeza a la derecha). `aleteo`: ángulo de las alas (rad)."""
    g = VGroup()
    cuerpo = Ellipse(width=1.5, height=0.24, fill_color="#94A3B8", fill_opacity=1, stroke_width=0)
    torax = Ellipse(width=0.5, height=0.38, fill_color="#CBD5E1", fill_opacity=1,
                    stroke_width=0).shift(RIGHT * 0.75 + UP * 0.05)
    cabeza = Circle(radius=0.13, fill_color="#E2E8F0", fill_opacity=1, stroke_width=0).shift(RIGHT * 1.1 + UP * 0.02)
    trompa = Line([1.2, 0.0, 0], [1.75, -0.25, 0], color="#CBD5E1", stroke_width=3)
    patas = VGroup(*[Line([0.6 + 0.12 * k, -0.08, 0], [0.2 + 0.35 * k, -0.75, 0], color="#94A3B8",
                          stroke_width=2) for k in range(3)])
    ala = Ellipse(width=1.3, height=0.32, fill_color=C_MOS, fill_opacity=0.35, stroke_color=C_MOS,
                  stroke_width=2).shift(RIGHT * 0.1 + UP * 0.1)
    ala.rotate(0.35 + aleteo, about_point=[0.75, 0.15, 0])
    g.add(patas, cuerpo, torax, cabeza, trompa, ala)
    return g.scale(escala)


class Reynolds(ModoBase):
    VOZ_JSON = Path(__file__).parent / "voz.json"

    def portada_mobs(self, reloj):
        av = self.avion3d(campo=40, alto_px=520, centro=(-0.9, 2.0), colores_mando=False,
                          azimut=-125, elevacion=14)
        mos = always_redraw(lambda: mosquito(1.5, 0.5 * np.sin(reloj.get_value() * 25)).move_to([1.6, -0.6, 0]))
        vs = T("vs", size=48, color=TEXTO_SEC, weight=HEAVY).move_to([-1.6, -0.4, 0])
        fondo = brillo([0, 1.0, 0], C_RE, 3.8, 0.8)
        preg, dest = self.gancho_texto("¿Un mosquito vuela", "COMO UN AVIÓN?", C_MOS, 88)
        return av, mos, vs, fondo, preg, dest

    def construct(self):
        self.iniciar()
        reloj = ValueTracker(0.0)
        reloj.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(reloj)
        av, mos, vs, fondo, preg, dest = self.portada_mobs(reloj)
        sello = self.sello("NÚMERO DE REYNOLDS", C_RE, DOWN * 3.95, size=50)

        # ---------- Gancho ----------
        self.portada(fondo, av, mos, vs, preg)
        self.wait(0.15)
        self.poner_sello(sello)
        self.pulso(dest, 1.06)
        self.hasta(0, 2.25)

        # ---------- 1. La cifra ----------
        t0, d = self.voz("b1")
        self.play(self.poner_cabecera("NÚMERO DE REYNOLDS", 3), run_time=0.01)
        self.dejar(preg, sello, av, mos, vs)
        barra, tit, fr, dt = self.bloque_ajustado(0, "Una cifra", "Inercia del aire frente a viscosidad",
                                                  C_RE, dato="viscosidad: lo «pegajoso» del aire",
                                                  resaltar=["inercia", "viscosidad"])
        f_re = T("Re", size=110, color=C_RE, weight=HEAVY, font=F_TIT)
        f_eq = T("=", size=90, color=TEXTO, weight=HEAVY)
        num = T("V · L", size=90, color=TEXTO, weight=HEAVY, font=F_TIT)
        den = T("ν", size=90, color=TEXTO, weight=HEAVY, font=F_TIT)
        raya = Line(LEFT * 1.3, RIGHT * 1.3, color=TEXTO, stroke_width=6)
        frac = VGroup(num, raya, den).arrange(DOWN, buff=0.18)
        formula = VGroup(f_re, f_eq, frac).arrange(RIGHT, buff=0.4).move_to([0, 1.2, 0])
        leyenda = VGroup(
            self.etiqueta("V: velocidad", TEXTO, ORIGIN, size=24),
            self.etiqueta("L: tamaño (cuerda del ala)", TEXTO, ORIGIN, size=24),
            self.etiqueta("ν: viscosidad del aire", TEXTO, ORIGIN, size=24)).arrange(DOWN, buff=0.15).move_to([0, -1.2, 0])
        self.abrir_bloque(barra, C_RE, tit, fr, dt, FadeIn(formula, scale=1.2))
        self.play(LaggedStart(*[FadeIn(x, shift=UP * 0.2) for x in leyenda], lag_ratio=0.4), run_time=1.2)
        self.hasta(t0, d * 0.6)
        self.play(Indicate(num, color=C_AV), run_time=0.7)
        self.play(Indicate(den, color=C_MOS), run_time=0.7)
        self.rellenar(t0, d, margen=-0.15)

        # ---------- 2. Millones frente a decenas ----------
        t0, d = self.voz("b2")
        self.dejar(tit, fr, dt, formula, leyenda)
        barra, tit, fr, dt = self.bloque_ajustado(1, "Distinta escala", "Avión: millones · mosquito: decenas",
                                                  C_AV, dato="Re ≈ 2·10⁷ (70 m/s, 4 m) · Re ≈ 70 (1 m/s, 1 mm)",
                                                  resaltar=["millones", "decenas"])
        ax = NumberLine(x_range=[1, 8, 1], length=7.4, include_tip=False, include_numbers=False,
                        color="#64748B", stroke_width=4).move_to([0, -0.4, 0])
        nums = VGroup(*[T(f"10{s}", size=24, color=TEXTO_SEC, weight=MEDIUM)
                        .next_to(ax.n2p(k), DOWN, buff=0.18)
                        for k, s in zip(range(1, 9), ["", "²", "³", "⁴", "⁵", "⁶", "⁷", "⁸"])])
        nums[0].become(T("10", size=24, color=TEXTO_SEC, weight=MEDIUM).next_to(ax.n2p(1), DOWN, buff=0.18))
        zona_v = Rectangle(width=ax.n2p(3.2)[0] - ax.n2p(1)[0], height=0.25, stroke_width=0,
                           fill_color=C_MOS, fill_opacity=0.35).move_to([(ax.n2p(1)[0] + ax.n2p(3.2)[0]) / 2, -0.4, 0])
        zona_i = Rectangle(width=ax.n2p(8)[0] - ax.n2p(5)[0], height=0.25, stroke_width=0,
                           fill_color=C_AV, fill_opacity=0.35).move_to([(ax.n2p(5)[0] + ax.n2p(8)[0]) / 2, -0.4, 0])
        e_v = self.etiqueta("MANDA LA VISCOSIDAD", C_MOS, [ax.n2p(2.1)[0], -1.4, 0], size=20)
        e_i = self.etiqueta("MANDA LA INERCIA", C_AV, [ax.n2p(6.5)[0], -1.4, 0], size=20)
        p_m = np.log10(70)
        p_a = np.log10(2e7)
        mark_m = VGroup(Triangle(fill_color=C_MOS, fill_opacity=1, stroke_width=0).scale(0.14).rotate(PI)
                        .move_to(ax.n2p(p_m) + UP * 0.32), mosquito(0.8).move_to(ax.n2p(p_m) + UP * 1.15))
        av_mini = self.avion3d(campo=30, alto_px=420, ancho_pantalla=4.0, centro=(ax.n2p(p_a)[0] - 0.6, 1.0),
                               colores_mando=False, azimut=-125, elevacion=14)
        mark_a = Triangle(fill_color=C_AV, fill_opacity=1, stroke_width=0).scale(0.14).rotate(PI).move_to(ax.n2p(p_a) + UP * 0.32)
        self.abrir_bloque(barra, C_AV, tit, fr, dt, FadeIn(ax), FadeIn(nums), FadeIn(zona_v), FadeIn(zona_i))
        self.sonido("pop", -9)
        self.play(FadeIn(mark_a, shift=DOWN * 0.3), FadeIn(av_mini), FadeIn(e_i), run_time=0.5)
        self.hasta(t0, d * 0.55)
        self.sonido("pop", -9)
        self.play(FadeIn(mark_m, shift=DOWN * 0.3), FadeIn(e_v), run_time=0.5)
        miel = self.etiqueta("el aire, casi como miel", C_MOS, [ax.n2p(2.2)[0], 1.85, 0], size=22)
        self.play(FadeIn(miel), run_time=0.3)
        self.pulso(mark_m, 1.15)
        self.rellenar(t0, d, margen=-0.15)

        # ---------- 3. Remolinos ----------
        t0, d = self.voz("b3")
        self.dejar(tit, fr, dt, ax, nums, zona_v, zona_i, e_v, e_i, mark_m, mark_a, av_mini, miel)
        barra, tit, fr, dt = self.bloque_ajustado(2, "Batir y girar", "Remolinos que los sostienen",
                                                  C_MOS, dato="remolino de borde de ataque (dibujo cualitativo)",
                                                  resaltar=["remolinos"])
        piv = np.array([-2.0, 0.6, 0])

        def batido():
            tt = reloj.get_value()
            a = 0.9 * np.sin(tt * 6.0)
            dirv = np.array([np.cos(a), np.sin(a), 0])
            ala = Ellipse(width=3.6, height=0.55, fill_color=C_MOS, fill_opacity=0.35,
                          stroke_color=C_MOS, stroke_width=4).rotate(a).move_to(piv + dirv * 1.8)
            pc = piv + dirv * 2.4 + np.array([-dirv[1], dirv[0], 0]) * 0.45 * np.sign(np.cos(tt * 6.0))
            remol = espiral(pc, 0.6, fase=tt * 8, sentido=1, color=C_RE, ancho=5, opacidad=0.9)
            raiz = Dot(piv, radius=0.14, color=TEXTO)
            return VGroup(ala, raiz, remol)
        bt = always_redraw(batido)
        eb = VGroup(self.etiqueta("REMOLINO PEGADO AL ALA", C_RE, [0.9, -1.55, 0], size=22), T("ala de insecto, vista de lado", size=20, color=TEXTO_SEC, weight=MEDIUM).move_to([0.9, -2.0, 0]))
        self.abrir_bloque(barra, C_MOS, tit, fr, dt, FadeIn(bt))
        self.play(FadeIn(eb), run_time=0.3)
        self.hasta(t0, d * 0.7)
        self.pulso(eb, 1.08)
        self.rellenar(t0, d, margen=-0.15)

        # ---------- Cierre ----------
        t0, d = self.voz("cierre")
        bt.clear_updaters()
        self.dejar(tit, fr, dt, bt, eb, self.tema, self.barras)
        tj = self.tarjeta("Misma física, distinta escala", C_RE).move_to([0, 2.6, 0])
        preg2 = self.cta("¿Quién tiene un Reynolds más alto: una mosca o un colibrí?", ["mosca", "colibrí?"], C_MOS, y=-0.6, size=54)
        self.cambio(FadeIn(tj, shift=DOWN * 0.3), FadeIn(preg2, shift=UP * 0.3), run_time=0.7)
        self.hasta(t0, d * 0.32)
        self.pulso(tj, 1.05)
        self.hasta(t0, d * 0.64)
        self.pulso(preg2, 1.05)
        self.hasta(t0, d - 0.75)
        av, mos, vs, fondo, preg, _ = self.portada_mobs(reloj)
        self.dejar(tj, preg2)
        self.cambio(*[FadeIn(m) for m in (fondo, av, mos, vs, preg)], run_time=0.45, desplazar=UP * 0.6)
        self.wait(0.3)

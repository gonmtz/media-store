"""
Short 11 (texto, sin voz): ¿para qué son las "antenitas" del borde del ala?
Descargadores de estática (static wicks):
- Al volar entre lluvia, nieve, hielo o polvo el avión acumula carga (P-static).
- Las cargas se escapan por puntas y bordes (descarga de corona); los descargadores dan puntos
  de salida controlados, repartidos y de baja intensidad, en los bordes de salida de alas y cola.
- Sin ellos, la descarga mete ruido en radios de comunicación y navegación.
- No protegen contra rayos (el rayo recorre la piel conductora del avión de un extremo a otro).
Fuentes: Aeromach, "What is an aircraft static wick…"; AviationPros, "Precipitation static".
Número y posición de los descargadores del dibujo: ilustrativos.
Render:  manim -qh --fps 30 shorts/11_descargadores/escena.py Descargadores
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403

C_CARGA, C_DESC, C_RADIO = C_CABECEO, C_GUINADA, C_ALABEO
ESC, Y_AV = 0.92, 0.1
rng = np.random.default_rng(7)
PARTICULAS = [(rng.uniform(-4.2, 4.2), rng.uniform(0, 1), rng.uniform(0.7, 1.3)) for _ in range(46)]
SITIOS = [(-2.6, -0.5), (-1.7, -0.1), (-0.9, 0.3), (0.9, 0.3), (1.7, -0.1), (2.6, -0.5),
          (0, 2.0), (0, 0.9), (0, -0.6), (0, -1.9), (-1.0, -3.05), (1.0, -3.05),
          (-3.2, -0.95), (3.2, -0.95), (-2.1, -0.75), (2.1, -0.75)]


def en_pantalla(p):
    return np.array([p[0] * ESC, p[1] * ESC + Y_AV, 0.0])


class Descargadores(ShortBase):
    def construct(self):
        self.iniciar()
        reloj = ValueTracker(0.0)
        reloj.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(reloj)

        av, _, _ = avion_superior()
        av.scale(ESC, about_point=ORIGIN).shift(UP * Y_AV)
        wicks = [(en_pantalla(b), d) for b, d in puntas_descargadores_superior()]
        varillas = VGroup(*[descargador(b, d, largo=0.3 * ESC) for b, d in wicks]).set_z_index(5)
        puntas = [b + d / np.linalg.norm(d) * 0.3 * ESC for b, d in wicks]

        # ---------- capas animadas ----------
        viento = ValueTracker(0.0)      # visibilidad de las partículas (lluvia, hielo, polvo)

        def particulas():
            g = VGroup()
            a = viento.get_value()
            if a <= 0.01:
                return g
            t = reloj.get_value()
            for x, fase, v in PARTICULAS:
                y = 3.6 - ((fase + t * 0.45 * v) % 1.0) * 8.6
                g.add(Line([x, y, 0], [x, y - 0.28, 0], color="#94A3B8", stroke_width=3)
                      .set_opacity(0.55 * a))
            return g
        lluvia = always_redraw(particulas)

        n_cargas = ValueTracker(0.0)    # cuántas cargas hay en la piel
        fuga = ValueTracker(0.0)        # 0 = en su sitio, 1 = salieron por los descargadores

        def cargas():
            g = VGroup()
            k = n_cargas.get_value()
            f = fuga.get_value()
            for i, s in enumerate(SITIOS):
                if i >= k:
                    break
                p = en_pantalla(s)
                q = min(puntas, key=lambda w: np.linalg.norm(w - p))
                ff = np.clip(f * 1.6 - (i % 5) * 0.12, 0, 1)
                pos = p + (q - p) * ff
                op = 1.0 if ff < 0.85 else max(0.0, (1 - ff) / 0.15)
                if op > 0.02:
                    g.add(carga(pos, "−", C_CARGA, radio=0.15).set_opacity(op))
            return g.set_z_index(8)
        capa_cargas = always_redraw(cargas).set_z_index(8)

        chispa_on = ValueTracker(0.0)

        def chispas():
            g = VGroup()
            a = chispa_on.get_value()
            if a <= 0.01:
                return g
            t = reloj.get_value()
            for i, q in enumerate(puntas):
                ph = (t * 1.7 + i * 0.37) % 1.0
                g.add(Circle(radius=0.05 + 0.22 * ph, stroke_color=C_DESC, stroke_width=3)
                      .move_to(q).set_stroke(opacity=a * (1 - ph)))
            return g.set_z_index(6)
        capa_chispas = always_redraw(chispas).set_z_index(6)

        # ---------- Gancho (portada en t = 0) ----------
        l1 = T("¿Para qué son estas", size=60, weight=HEAVY, font=F_TIT)
        pal = T("«ANTENITAS»?", size=96, color=BG, weight=HEAVY, font=F_TIT)
        caja = RoundedRectangle(width=pal.width + 0.7, height=pal.height + 0.5, corner_radius=0.3,
                                fill_color=C_DESC, fill_opacity=1, stroke_width=0).move_to(pal)
        destacado = VGroup(caja, pal).rotate(-3 * DEGREES)
        preg = VGroup(l1, destacado).arrange(DOWN, buff=0.3).move_to(UP * 4.65)
        anillo = Circle(radius=0.75, stroke_color=C_DESC, stroke_width=6)
        anillo.move_to(en_pantalla((3.45, -1.3)))
        self.portada(av, varillas, preg, anillo)
        self.wait(0.4)
        self.play(anillo.animate.scale(1.25), rate_func=there_and_back, run_time=0.6)
        self.play(varillas.animate.set_color(WHITE), rate_func=there_and_back, run_time=0.5)
        self.pulso(destacado, 1.08)
        self.hasta(0, 3.4)

        # ---------- 1. El avión se carga ----------
        self.dejar(preg, anillo)
        self.play(self.poner_cabecera("DESCARGADORES DE ESTÁTICA", 3), run_time=0.01)
        barra, tit, fr, dt, etq, ctl = self.textos_bloque(
            0, "Carga", "El avión se electriza", "al chocar con lluvia, nieve, hielo y polvo",
            "ELECTRICIDAD", "ESTÁTICA", C_CARGA)
        for m in (etq, ctl):
            m.shift(DOWN * 1.1)
        self.add(lluvia, capa_cargas)
        self.bring_to_back(lluvia)
        self.cambio(viento.animate.set_value(1.0))
        self.entrar_textos(barra, C_CARGA, tit, fr, dt)
        self.play(n_cargas.animate.set_value(len(SITIOS)), run_time=2.2, rate_func=linear)
        self.play(FadeIn(etq), FadeIn(ctl, scale=0.9), run_time=0.4)
        self.wait(0.6)
        self.pulso(ctl)
        self.hasta(0, 9.2)
        self.dejar(tit, fr, dt, etq, ctl)

        # ---------- 2. Descarga por las puntas ----------
        barra, tit, fr, dt, etq, ctl = self.textos_bloque(
            1, "Descarga", "Las puntas la sueltan poco a poco", "en los bordes de salida de alas y cola",
            "SE LLAMAN", "DESCARGADORES", C_DESC)
        for m in (etq, ctl):
            m.shift(DOWN * 1.1)
        self.add(capa_chispas)
        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.15), barra.animate.set_fill(C_DESC),
                    chispa_on.animate.set_value(1.0))
        self.play(FadeIn(fr, shift=UP * 0.2), FadeIn(dt), run_time=0.4)
        self.play(fuga.animate.set_value(1.0), run_time=2.6, rate_func=linear)
        self.play(FadeIn(etq), FadeIn(ctl, scale=0.9), run_time=0.4)
        self.wait(0.5)
        self.pulso(ctl)
        self.hasta(0, 14.6)
        self.dejar(tit, fr, dt, etq, ctl)

        # ---------- 3. Para qué: la radio ----------
        barra, tit, fr, dt, etq, ctl = self.textos_bloque(
            2, "Radio", "Sin ellos, ruido en la radio", "las descargas sin control interfieren",
            "", "", C_RADIO)
        panel = RoundedRectangle(width=7.4, height=3.9, corner_radius=0.3, fill_color=PANEL,
                                 fill_opacity=0.96, stroke_color=C_RADIO, stroke_width=2,
                                 stroke_opacity=0.5).move_to(DOWN * 0.2).set_z_index(20)
        ruido_rng = np.random.default_rng(3)
        picos = ruido_rng.normal(0, 1, 600)

        def onda(ruidosa, y):
            t = reloj.get_value()
            xs = np.linspace(-3.2, 3.2, 200)
            ys = 0.35 * np.sin(4 * xs - 6 * t)
            if ruidosa:
                k = int(t * 30) % 300
                ys = ys + np.clip(0.25 * picos[k:k + 200], -0.4, 0.4) * (np.abs(picos[k + 50:k + 250]) > 1.1)
            return VMobject().set_points_smoothly([[x, y + v, 0] for x, v in zip(xs, ys)]) \
                .set_stroke(C_RADIO if ruidosa else C_CARGA, 4).set_z_index(21)
        o1 = always_redraw(lambda: onda(True, 0.55))
        o2 = always_redraw(lambda: onda(False, -1.3))
        r1 = T("SIN DESCARGADORES", size=24, color=C_RADIO, weight=HEAVY).move_to([0, 1.45, 0])
        r2 = T("CON DESCARGADORES", size=24, color=C_CARGA, weight=HEAVY).move_to([0, -0.6, 0])
        VGroup(r1, r2).set_z_index(22)
        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.15), barra.animate.set_fill(C_RADIO),
                    FadeIn(panel), FadeIn(r1), FadeIn(o1))
        self.play(FadeIn(fr, shift=UP * 0.2), FadeIn(dt), run_time=0.4)
        self.wait(1.0)
        self.play(FadeIn(r2), FadeIn(o2), run_time=0.5)
        self.wait(1.2)
        txt = T("NO SON PARARRAYOS", size=52, color=C_RADIO, weight=HEAVY, font=F_TIT)
        marco = RoundedRectangle(width=txt.width + 0.6, height=txt.height + 0.5,
                                 corner_radius=0.2, stroke_color=C_RADIO, stroke_width=8,
                                 fill_color=BG, fill_opacity=0.9)
        sello = VGroup(marco, txt.move_to(marco)).rotate(4 * DEGREES).move_to(DOWN * 3.6)
        sub = T("el rayo recorre la piel del avión y sale por otro extremo", size=24,
                color=TEXTO_SEC, weight=MEDIUM).move_to(DOWN * 4.6)
        VGroup(sello, sub).set_z_index(30)
        self.play(FadeIn(sello, scale=1.4), rate_func=rate_functions.ease_out_back, run_time=0.35)
        self.play(FadeIn(sub), run_time=0.3)
        self.wait(1.0)
        self.pulso(sello, 1.08)
        self.hasta(0, 21.6)
        self.dejar(tit, fr, dt, panel, r1, r2, o1, o2, sello, sub, self.tema, self.barras)

        # ---------- Cierre (vuelve a la portada) ----------
        c1 = T("Búscalos en tu próximo vuelo:", size=52, weight=HEAVY, font=F_TIT)
        c2 = T("¿cuántos cuentas?", size=64, color=C_DESC, weight=HEAVY, font=F_TIT)
        cierre = VGroup(c1, c2).arrange(DOWN, buff=0.18).move_to(UP * 4.65)
        self.cambio(FadeIn(cierre, shift=DOWN * 0.3), viento.animate.set_value(0.0),
                    chispa_on.animate.set_value(0.0), FadeIn(anillo))
        self.hasta(0, 24.0)
        self.dejar(cierre)
        self.cambio(FadeIn(preg), run_time=0.3, desplazar=UP * 0.6)
        self.wait(0.3)

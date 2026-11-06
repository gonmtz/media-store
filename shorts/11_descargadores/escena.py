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
Render:  manim -qh --fps 60 shorts/11_descargadores/escena.py Descargadores
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403

from lib import avion as A  # noqa: E402
from lib.avion2d import superior_2d  # noqa: E402

C_CARGA, C_DESC, C_RADIO = C_CABECEO, C_GUINADA, C_ALABEO
Y_AV = -0.5
VISTA = superior_2d(7.3, (0, Y_AV))
rng = np.random.default_rng(7)
PARTICULAS = [(rng.uniform(-4.2, 4.2), rng.uniform(0, 1), rng.uniform(0.7, 1.3)) for _ in range(46)]


def P(X, Y):
    """Metros (construcción: X desde el morro, Y a la izquierda) → pantalla."""
    return VISTA.a_pantalla(X, Y, 0.0)


def _estab_bs(yy):
    e = A.ESTAB
    u = (yy - e["y_raiz"]) / (e["y_punta"] - e["y_raiz"])
    cu = e["cuerda_raiz"] + (e["cuerda_punta"] - e["cuerda_raiz"]) * u
    return e["x_ba_raiz"] + (yy - e["y_raiz"]) * np.tan(np.radians(e["flecha"])) + cu


def descargadores_m():
    """(base, dirección) en metros: bordes de salida cerca de las puntas del ala y del
    estabilizador, y la punta de la deriva. Dirección hacia atrás y un poco hacia fuera."""
    res = []
    for s in (1, -1):
        for yy in (13.4, 14.7, 15.9):
            res.append(((A.geometria_ala_en(yy, 1.0)[0], s * yy), (1.0, s * 0.25)))
        res.append(((A.geometria_ala_en(16.9, 0.92)[0], s * 17.05), (1.0, s * 0.6)))
        for yy in (4.6, 5.8):
            res.append(((_estab_bs(yy), s * yy), (1.0, s * 0.2)))
    d = A.DERIVA
    res.append(((d["x_ba_raiz"] + (d["z_punta"] - d["z_raiz"]) * np.tan(np.radians(d["flecha"]))
                 + d["cuerda_punta"], 0.0), (1.0, 0.0)))
    return res


LARGO = 1.25    # m
WICKS = []
for (X, Y), (dx, dy) in descargadores_m():
    n = np.hypot(dx, dy)
    WICKS.append((P(X, Y), P(X + dx / n * LARGO, Y + dy / n * LARGO)))
SITIOS = [(A.geometria_ala_en(yy, 0.45)[0], s * yy) for s in (1, -1) for yy in (5.0, 9.0, 13.0)]
SITIOS += [(X, 0.0) for X in (5.5, 11.0, 20.0, 27.0)]
SITIOS += [(_estab_bs(3.2) - 1.6, s * 3.2) for s in (1, -1)]
SITIOS += [(A.geometria_ala_en(15.8, 0.55)[0], s * 15.8) for s in (1, -1)]


class Descargadores(ShortBase):
    def construct(self):
        self.iniciar()
        reloj = ValueTracker(0.0)
        reloj.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(reloj)

        av = superior_2d(7.3, (0, Y_AV))
        varillas = VGroup(*[VGroup(Line(a, b, color=C_DESC, stroke_width=4),
                                   Dot(b, radius=0.032, color=C_DESC)) for a, b in WICKS])
        puntas = [b for _, b in WICKS]

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
                p = P(*s)
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
        preg = self.hud(VGroup(l1, destacado).arrange(DOWN, buff=0.3).move_to(UP * 4.65))
        punta_ala = P(A.geometria_ala_en(15.6, 0.95)[0], -15.6)
        anillo = Circle(radius=0.75, stroke_color=C_DESC, stroke_width=6).move_to(punta_ala)
        fondo = brillo(UP * Y_AV, C_CARGA, 4.0, 0.8)
        self.portada(fondo, av, varillas, preg, anillo)
        self.wait(0.4)
        self.sonido("pop", -8)
        self.play(anillo.animate.scale(1.25), rate_func=there_and_back, run_time=0.5)
        self.enfocar(punta_ala + LEFT * 0.35 + DOWN * 0.2, 2.8, run_time=1.0)
        self.sonido("tic", -6)
        self.play(varillas.animate.set_color(WHITE), rate_func=there_and_back, run_time=0.5)
        self.hasta(0, 3.0)
        self.vista_general(run_time=0.7)

        # ---------- 1. El avión se carga ----------
        self.dejar(preg, anillo)
        self.play(self.poner_cabecera("DESCARGADORES DE ESTÁTICA", 3), run_time=0.01)
        barra, tit, fr, dt = self.bloque(0, "Carga", "La lluvia y el hielo lo electrizan", C_CARGA,
                                         dato="electricidad estática", resaltar=["electrizan"])
        self.add(lluvia, capa_cargas)
        self.bring_to_back(lluvia)
        self.cambio(viento.animate.set_value(1.0), FadeIn(tit, shift=DOWN * 0.3, scale=1.2),
                    barra.animate.set_fill(C_CARGA))
        self.entrar_palabras(fr)
        self.play(FadeIn(dt), run_time=0.3)
        for _ in range(4):
            self.sonido("tic", -14)
            self.play(n_cargas.animate.increment_value(len(SITIOS) / 4), run_time=0.55,
                      rate_func=linear)
        self.wait(0.6)
        self.hasta(0, 10.0)

        # ---------- 2. Descarga por las puntas ----------
        self.dejar(tit, fr, dt)
        barra, tit, fr, dt = self.bloque(1, "Descarga", "Sus puntas la sueltan poco a poco", C_DESC,
                                         dato="se llaman descargadores de estática",
                                         resaltar=["puntas"])
        self.add(capa_chispas)
        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.2), barra.animate.set_fill(C_DESC),
                    chispa_on.animate.set_value(1.0))
        self.entrar_palabras(fr)
        self.play(FadeIn(dt), run_time=0.3)
        self.enfocar(punta_ala + LEFT * 0.9 + UP * 0.2, 2.0, run_time=0.9)
        for k in range(4):
            self.sonido("chispa", -10)
            self.play(fuga.animate.set_value((k + 1) / 4), run_time=0.65, rate_func=linear)
        self.wait(0.4)
        self.vista_general(run_time=0.8)
        self.hasta(0, 16.8)

        # ---------- 3. Para qué: la radio ----------
        self.dejar(tit, fr, dt)
        barra, tit, fr, dt = self.bloque(2, "Radio", "Sin ellos, ruido en la radio", C_RADIO,
                                         resaltar=["ruido"])
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
                ys = ys + np.clip(0.25 * picos[k:k + 200], -0.4, 0.4) * \
                    (np.abs(picos[k + 50:k + 250]) > 1.1)
            return VMobject().set_points_smoothly([[x, y + v, 0] for x, v in zip(xs, ys)]) \
                .set_stroke(C_RADIO if ruidosa else C_CARGA, 4).set_z_index(21)
        o1 = always_redraw(lambda: onda(True, 0.55))
        o2 = always_redraw(lambda: onda(False, -1.3))
        r1 = T("SIN DESCARGADORES", size=24, color=C_RADIO, weight=HEAVY).move_to([0, 1.45, 0])
        r2 = T("CON DESCARGADORES", size=24, color=C_CARGA, weight=HEAVY).move_to([0, -0.6, 0])
        VGroup(r1, r2).set_z_index(22)
        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.2), barra.animate.set_fill(C_RADIO),
                    FadeIn(panel, scale=0.95), FadeIn(r1), FadeIn(o1))
        self.entrar_palabras(fr)
        self.sonido("chispa", -12)
        self.wait(1.0)
        self.sonido("pop", -10)
        self.play(FadeIn(r2), FadeIn(o2), run_time=0.5)
        self.wait(1.0)
        sello = self.sello("NO SON PARARRAYOS", C_RADIO, DOWN * 3.6, size=52)
        sub = self.hud(T("el rayo recorre la piel del avión y sale por otro extremo", size=24,
                         color=TEXTO_SEC, weight=MEDIUM).move_to(DOWN * 4.6).set_z_index(30))
        self.poner_sello(sello)
        self.play(FadeIn(sub), run_time=0.3)
        self.wait(0.9)
        self.pulso(sello, 1.08)
        self.hasta(0, 23.6)

        # ---------- Cierre (vuelve a la portada) ----------
        self.dejar(tit, fr, panel, r1, r2, o1, o2, sello, sub, self.tema, self.barras)
        cierre = self.hud(frase_cinetica("Búscalos en tu próximo vuelo: ¿cuántos cuentas?",
                                         size=54, resaltar=["cuántos", "cuentas?"],
                                         color_resalte=C_DESC).move_to(UP * 4.65))
        self.cambio(viento.animate.set_value(0.0), chispa_on.animate.set_value(0.0),
                    FadeIn(anillo))
        self.entrar_palabras(cierre)
        self.hasta(0, 26.0)
        self.dejar(cierre)
        self.cambio(FadeIn(preg), run_time=0.3, desplazar=UP * 0.6)
        self.wait(0.25)

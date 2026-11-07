"""
Short 38 (narrado): ¿por qué las ventanillas son redondas?
- Presurización: Δp ≈ 75 kPa (cabina a ~2400 m) − 23 kPa (fuera, ~11 km) ≈ 52 kPa ≈ 5,3 t/m².
- Concentración de tensiones en una chapa con tracción (la dirección de la tensión
  circunferencial del fuselaje, vertical en la vista lateral). Agujero circular: solución de Kirsch
  (tensión principal máxima; Kt = 3). Agujero cuadrado: mapa ILUSTRATIVO con picos en las esquinas
  (rotulado en pantalla).
- Comet, 1954: la investigación situó el origen de la fatiga en la esquina de una abertura del techo
  (ventana de la antena ADF). Desde entonces, aberturas con esquinas redondeadas.
Render:  manim -qh --fps 60 shorts/38_ventanillas/escena.py Ventanillas
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403
from lib.modos import ModoBase, flecha  # noqa: E402
from lib import avion as A  # noqa: E402

C_PRES, C_TENS, C_OK = C_CABECEO, C_ALABEO, "#34D399"
PIEL_A, PIEL_B = "#E2E8F0", "#94A3B8"
ESCALA = ["#1E3A5F", "#2563EB", "#38BDF8", "#FBBF24", "#F97316", "#EF4444"]


# ---------- ventanilla 2D ----------
def ventanilla(c, w=1.5, h=2.1, rc=0.6, piel=True):
    """Trozo de fuselaje visto de lado con una ventanilla (rc = radio de las esquinas)."""
    c = np.array([*c, 0]) if len(c) == 2 else np.array(c)
    g = VGroup()
    if piel:
        panel = RoundedRectangle(width=4.6, height=3.6, corner_radius=0.3, stroke_width=0,
                                 fill_color=PIEL_A, fill_opacity=1).move_to(c)
        panel.set_sheen_direction(DOWN).set_fill([PIEL_A, PIEL_B])
        g.add(panel)
        for x in (-2.0, 2.0):
            for y in np.linspace(-1.5, 1.5, 9):
                g.add(Dot(c + np.array([x, y, 0]), radius=0.03, color="#64748B"))
        g.add(Line(c + np.array([-2.3, -1.25, 0]), c + np.array([2.3, -1.25, 0]), color=C_PRES, stroke_width=10))
    marco = RoundedRectangle(width=w + 0.36, height=h + 0.36, corner_radius=min(rc + 0.18, (w + 0.36) / 2),
                             stroke_color="#64748B", stroke_width=3, fill_color="#CBD5E1", fill_opacity=1).move_to(c)
    vidrio = RoundedRectangle(width=w, height=h, corner_radius=max(rc, 0.001), stroke_width=0,
                              fill_color="#0F2742", fill_opacity=1).move_to(c)
    vidrio.set_sheen_direction(UR).set_fill(["#0B1C33", "#38BDF8"])
    brillo_v = Polygon(c + np.array([-w * 0.32, h * 0.38, 0]), c + np.array([-w * 0.05, h * 0.38, 0]),
                       c + np.array([-w * 0.38, -h * 0.05, 0]), c + np.array([-w * 0.42, h * 0.1, 0]),
                       stroke_width=0, fill_color=WHITE, fill_opacity=0.18)
    g.add(marco, vidrio, brillo_v)
    return g


# ---------- mapas de tensión ----------
def _kirsch(x, y, a):
    """Tensión principal máxima / S alrededor de un agujero circular de radio a con tracción
    vertical S (Kirsch). x, y relativos al centro."""
    r = np.hypot(x, y)
    th = np.arctan2(x, y)                 # ángulo desde el eje de la carga (vertical)
    q2, q4 = (a / r) ** 2, (a / r) ** 4
    srr = 0.5 * (1 - q2) + 0.5 * (1 - 4 * q2 + 3 * q4) * np.cos(2 * th)
    stt = 0.5 * (1 + q2) - 0.5 * (1 + 3 * q4) * np.cos(2 * th)
    srt = -0.5 * (1 + 2 * q2 - 3 * q4) * np.sin(2 * th)
    return (srr + stt) / 2 + np.sqrt(((srr - stt) / 2) ** 2 + srt ** 2)


def mapa(c, forma, lado=3.3, a=0.62, n=50, rc=0.0):
    """Chapa con tracción vertical. forma: 'circulo' (Kirsch) o 'cuadrado' (ilustrativo, esquinas
    con radio rc)."""
    c = np.array([*c, 0]) if len(c) == 2 else np.array(c)
    paso = lado / n
    g = VGroup()
    for i in range(n):
        for j in range(n):
            x = -lado / 2 + (i + 0.5) * paso
            y = -lado / 2 + (j + 0.5) * paso
            if forma == "circulo":
                if np.hypot(x, y) < a:
                    continue
                s = _kirsch(x, y, a)
            else:
                ax, ay = abs(x), abs(y)
                if ax < a and ay < a and not (ax > a - rc and ay > a - rc and
                                               np.hypot(ax - (a - rc), ay - (a - rc)) > rc):
                    continue
                s = _kirsch(x, y, a * 1.05)
                # picos en las esquinas (ilustrativo): más altos cuanto más viva la esquina
                pico = 4.5 * 0.06 / (rc + 0.06)
                d = np.hypot(ax - (a - rc), ay - (a - rc)) - rc
                s += pico * np.exp(-max(d, 0) / 0.18)
            k = np.clip((s - 0.6) / 4.0, 0, 1) * (len(ESCALA) - 1)
            i0 = int(min(k, len(ESCALA) - 2))
            col = interpolate_color(ManimColor(ESCALA[i0]), ManimColor(ESCALA[i0 + 1]), k - i0)
            g.add(Square(paso * 1.02, stroke_width=0, fill_color=col, fill_opacity=1).move_to(c + np.array([x, y, 0])))
    borde = Square(lado, stroke_color="#475569", stroke_width=2).move_to(c)
    if forma == "circulo":
        hueco = Circle(radius=a, stroke_color="#CBD5E1", stroke_width=3, fill_color=BG, fill_opacity=1).move_to(c)
    else:
        hueco = RoundedRectangle(width=2 * a, height=2 * a, corner_radius=max(rc, 0.001), stroke_color="#CBD5E1",
                                 stroke_width=3, fill_color=BG, fill_opacity=1).move_to(c)
    return VGroup(g, borde, hueco)


def tirones(c, lado=3.3, color=TEXTO_SEC):
    c = np.array([*c, 0]) if len(c) == 2 else np.array(c)
    g = VGroup()
    for x in (-1.0, 0.0, 1.0):
        g.add(flecha(c + np.array([x, lado / 2 + 0.08, 0]), c + np.array([x, lado / 2 + 0.55, 0]), color, 6),
              flecha(c + np.array([x, -lado / 2 - 0.08, 0]), c + np.array([x, -lado / 2 - 0.55, 0]), color, 6))
    return g


class Ventanillas(ModoBase):
    VOZ_JSON = Path(__file__).parent / "voz.json"

    def portada_grupo(self):
        av = self.avion3d(campo=34, alto_px=520, centro=(0.3, 2.35), azimut=-90, elevacion=4,
                          colores_mando=False, ancho_pantalla=7.6)
        p = av.a_pantalla([A.a_cuerpo(15.0, 0, 1.0)])[0]
        ve = ventanilla((0, -0.35), rc=0.6)
        zoom = VGroup(DashedLine(p, ve[0].get_corner(UL), color=TEXTO_SEC, stroke_width=2, dash_length=0.08),
                      DashedLine(p, ve[0].get_corner(UR), color=TEXTO_SEC, stroke_width=2, dash_length=0.08),
                      Circle(radius=0.12, stroke_color=TEXTO, stroke_width=3).move_to(p))
        return av, ve, zoom

    def construct(self):
        self.iniciar()
        av, ve, zoom = self.portada_grupo()
        fondo = brillo([0, 0.3, 0], C_PRES, 3.6, 0.7)
        preg, dest = self.gancho_texto("¿Por qué las ventanillas", "SON REDONDAS?", C_PRES, 88)
        sello = self.sello("PRESIÓN Y FATIGA", C_PRES, DOWN * 3.95, size=52)

        # ---------- Gancho ----------
        self.portada(fondo, zoom, ve, av, preg)
        self.wait(0.15)
        self.poner_sello(sello)
        self.pulso(ve, 1.05)
        self.hasta(0, 2.2)

        # ---------- 1. Presurización ----------
        t0, d = self.voz("b1")
        self.play(self.poner_cabecera("VENTANILLAS REDONDAS", 3), run_time=0.01)
        self.dejar(preg, sello, av, ve, zoom)
        barra, tit, fr, dt = self.bloque_ajustado(0, "Presurizada", "El aire de dentro empuja hacia fuera",
                                                  C_PRES, dato="≈ 75 kPa dentro − 23 kPa fuera (crucero)",
                                                  resaltar=["hacia", "fuera"])
        cc = np.array([0, 0.45, 0])
        sec = VGroup(Circle(radius=2.05, stroke_color=PIEL_B, stroke_width=10, fill_color="#16263D",
                            fill_opacity=1).move_to(cc),
                     Line(cc + np.array([-1.85, -0.75, 0]), cc + np.array([1.85, -0.75, 0]), color="#475569", stroke_width=5),
                     T("CABINA", size=24, color=TEXTO_SEC, weight=HEAVY).move_to(cc + UP * 0.25))
        k = ValueTracker(0.0)

        def empuje():
            g = VGroup()
            kk = k.get_value()
            if kk < 0.03:
                return g
            for a in np.linspace(0, TAU, 12, endpoint=False):
                u = np.array([np.cos(a), np.sin(a), 0])
                g.add(flecha(cc + u * 1.12, cc + u * (1.12 + 0.78 * kk), C_PRES, 7))
            return g
        em = always_redraw(empuje)
        self.abrir_bloque(barra, C_PRES, tit, fr, dt, FadeIn(sec, scale=0.9))
        self.add(em)
        self.avanzar(t0 + d * 0.5, k.animate.set_value(1.0))
        cifra = VGroup(T("≈ 5 t", size=64, color=TEXTO, weight=HEAVY, font=F_TIT),
                       T("por m²", size=32, color=TEXTO_SEC, weight=BOLD)
                       ).arrange(DOWN, buff=0.06).move_to(cc)
        self.sonido("golpe", -12)
        self.play(FadeOut(sec[2]), FadeIn(cifra, scale=1.2), run_time=0.4)
        self.hasta(t0, d * 0.8)
        self.pulso(cifra, 1.08)
        self.rellenar(t0, d)

        # ---------- 2. Esquinas ----------
        t0, d = self.voz("b2")
        em.clear_updaters()
        self.dejar(tit, fr, dt, sec, em, cifra)
        barra, tit, fr, dt = self.bloque_ajustado(1, "Las esquinas", "La tensión se concentra en el ángulo recto",
                                                  C_TENS, dato="mapa de tensiones ilustrativo",
                                                  resaltar=["concentra"])
        cq, cr = np.array([-1.85, 0.45, 0]), np.array([1.85, 0.45, 0])
        mq, mr = mapa(cq, "cuadrado"), mapa(cr, "circulo")
        tq, tr = tirones(cq), tirones(cr)
        eq = self.etiqueta("ESQUINA VIVA", C_TENS, cq + np.array([0, -1.32, 0]), size=20)
        ercl = self.etiqueta("REDONDA", C_OK, cr + np.array([0, -1.32, 0]), size=20)
        self.abrir_bloque(barra, C_TENS, tit, fr, dt, FadeIn(mq), FadeIn(mr), FadeIn(tq), FadeIn(tr), FadeIn(eq),
                          FadeIn(ercl), run_time=0.7)
        esq = Circle(radius=0.32, stroke_color=TEXTO, stroke_width=4).move_to(cq + np.array([0.62, 0.62, 0]))
        self.sonido("pop", -9)
        self.play(Create(esq), run_time=0.4)
        self.hasta(t0, d * 0.5)
        # grieta por fatiga que crece con los vuelos
        lg = ValueTracker(0.0)
        quiebros = np.array([[0, 0], [0.12, 0.04], [0.25, -0.02], [0.4, 0.05], [0.55, 0.0], [0.7, 0.06], [0.88, 0.02], [1.0, 0.06]])

        def grieta():
            L = lg.get_value()
            if L < 0.01:
                return VGroup()
            p0 = cq + np.array([0.62, 0.62, 0])
            pts = [p0 + np.array([x, y, 0]) for x, y in quiebros if x <= L + 1e-6]
            if len(pts) < 2:
                pts.append(p0 + np.array([L, 0, 0]))
            return VMobject(stroke_color=WHITE, stroke_width=7).set_points_as_corners(pts)
        gr = always_redraw(grieta)
        nv = ValueTracker(0)
        cont = always_redraw(lambda: T(f"vuelos: {int(nv.get_value()):,}".replace(",", " "), size=26,
                                       color=TEXTO, weight=HEAVY).move_to(cq + np.array([0, -2.35, 0])))
        self.add(gr, cont)
        self.sonido("tic", -8)
        self.avanzar(t0 + d - 0.15, lg.animate.set_value(1.0), nv.animate.set_value(8000))

        # ---------- 3. Comet ----------
        t0, d = self.voz("b3")
        gr.clear_updaters()
        cont.clear_updaters()
        self.dejar(tit, fr, dt, mr, tr, esq, cont, eq, ercl)
        barra, tit, fr, dt = self.bloque_ajustado(2, "Comet, 1954", "La fatiga empezó en la esquina de una abertura",
                                                  C_TENS, dato="abertura del techo del fuselaje",
                                                  resaltar=["esquina"])
        grupo_q = VGroup(mq, tq, gr)
        self.abrir_bloque(barra, C_TENS, tit, fr, dt, grupo_q.animate.move_to([0, 0.45, 0]), run_time=0.7)
        self.hasta(t0, d * 0.3)
        self.pulso(gr, 1.25)
        self.hasta(t0, d * 0.55)
        mrd = mapa((0, 0.45), "cuadrado", rc=0.35)
        tq2 = tirones((0, 0.45))
        self.sonido("chispa", -8)
        self.play(FadeOut(VGroup(mq, gr)), FadeIn(mrd), FadeIn(tq2), FadeOut(tq), run_time=0.8)
        er = self.etiqueta("DESDE ENTONCES: ESQUINAS REDONDEADAS", C_OK, [0, -1.75, 0], size=22)
        self.play(FadeIn(er, shift=UP * 0.2), run_time=0.3)
        self.hasta(t0, d * 0.82)
        self.pulso(er, 1.08)
        self.rellenar(t0, d)

        # ---------- Cierre ----------
        t0, d = self.voz("cierre")
        self.dejar(tit, fr, dt, mrd, tq2, er, self.tema, self.barras)
        ve2 = ventanilla((0, 0.8), rc=0.6)
        tj = self.tarjeta("Curva suave: el esfuerzo se reparte", C_OK, size=36).move_to([0, -1.75, 0])
        preg2 = self.cta("¿En qué otra parte del avión se redondean las esquinas?", ["redondean"], C_PRES, y=-3.7, size=54)
        self.cambio(FadeIn(ve2, scale=0.9), FadeIn(tj, shift=UP * 0.2), FadeIn(preg2, shift=UP * 0.3), run_time=0.7)
        self.hasta(t0, d * 0.45)
        self.pulso(ve2, 1.04)
        self.hasta(t0, d * 0.7)
        self.pulso(preg2, 1.06)
        self.hasta(t0, d - 0.75)
        av3, ve3, zoom3 = self.portada_grupo()
        preg, _ = self.gancho_texto("¿Por qué las ventanillas", "SON REDONDAS?", C_PRES, 88)
        self.dejar(ve2, tj, preg2)
        self.cambio(FadeIn(av3), FadeIn(ve3), FadeIn(zoom3), FadeIn(preg), run_time=0.45, desplazar=UP * 0.6)
        self.wait(0.3)

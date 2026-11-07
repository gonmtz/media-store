"""
Short 39 (ficha): las seis básicas, los instrumentos de vuelo en "T" (anemómetro, horizonte
artificial, altímetro; coordinador de giro, indicador de rumbo y variómetro). Imagen fija sin voz.
Dibujos vectoriales propios (no son de un fabricante concreto). Las lecturas son de ejemplo.
Render de la imagen:  manim -qh -s shorts/39_seis_basicas/escena.py SeisBasicas
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403

R = 1.18
CARA, BISEL = "#0A0F1A", "#334155"
CIELO, TIERRA = "#2563EB", "#92400E"


def caja(c):
    c = np.array([*c, 0])
    return VGroup(RoundedRectangle(width=2 * R + 0.36, height=2 * R + 0.36, corner_radius=0.3,
                                   fill_color="#1E293B", fill_opacity=1, stroke_color="#475569", stroke_width=2).move_to(c),
                  Circle(radius=R + 0.06, fill_color=BISEL, fill_opacity=1, stroke_width=0).move_to(c),
                  Circle(radius=R - 0.04, fill_color=CARA, fill_opacity=1, stroke_width=0).move_to(c))


def u(ang):
    """Vector unitario; ang en grados desde las 12 en sentido horario."""
    a = np.radians(ang)
    return np.array([np.sin(a), np.cos(a), 0])


def aguja(c, ang, largo, ancho=6, color=WHITE):
    return VGroup(Line(c, c + u(ang) * largo, color=color, stroke_width=ancho),
                  Circle(radius=0.08, fill_color="#94A3B8", fill_opacity=1, stroke_width=0).move_to(c))


def marcas(c, a0, a1, n, largo=0.14, r=R - 0.08, ancho=3, cada=None):
    g = VGroup()
    for i, a in enumerate(np.linspace(a0, a1, n)):
        l = largo * (1.6 if cada and i % cada == 0 else 1.0)
        g.add(Line(c + u(a) * r, c + u(a) * (r - l), color=WHITE, stroke_width=ancho))
    return g


def anemometro(c):
    c = np.array([*c, 0])
    g = caja(c[:2])
    a_v = lambda v: -150 + v / 200 * 300                     # 0–200 kt en 300°
    for v0, v1, col, rr in ((50, 85, WHITE, R - 0.24), (60, 130, "#22C55E", R - 0.12), (130, 165, "#FBBF24", R - 0.12)):
        g.add(Arc(radius=rr, start_angle=np.radians(90 - a_v(v0)), angle=-np.radians(a_v(v1) - a_v(v0)),
                  arc_center=c, color=col, stroke_width=7))
    g.add(Line(c + u(a_v(165)) * (R - 0.04), c + u(a_v(165)) * (R - 0.3), color="#EF4444", stroke_width=7))
    g.add(marcas(c, a_v(0), a_v(200), 21, cada=2))
    for v in (40, 80, 120, 160, 200):
        g.add(T(str(v), size=16, color=WHITE, weight=BOLD).move_to(c + u(a_v(v)) * (R - 0.5)))
    g.add(T("NUDOS", size=13, color=TEXTO_SEC, weight=BOLD).move_to(c + DOWN * 0.33 + LEFT * 0.38))
    g.add(aguja(c, a_v(112), R - 0.2))
    return g


def horizonte(c, alabeo=12, cabeceo=0.12):
    c = np.array([*c, 0])
    g = caja(c[:2])
    rr = R - 0.04
    cielo = Circle(radius=rr, fill_color=CIELO, fill_opacity=1, stroke_width=0).move_to(c)
    ang = np.linspace(0, PI, 60)
    tierra = Polygon(*[c + np.array([rr * np.cos(a + PI), rr * np.sin(a + PI), 0]) for a in ang] +
                     [c + np.array([-rr, 0, 0])], fill_color=TIERRA, fill_opacity=1, stroke_width=0)
    lin = Line(c + LEFT * rr, c + RIGHT * rr, color=WHITE, stroke_width=4)
    esc = VGroup(*[Line(c + UP * (0.25 * k) + LEFT * (0.22 if k % 2 else 0.4), c + UP * (0.25 * k) + RIGHT * (0.22 if k % 2 else 0.4),
                        color=WHITE, stroke_width=2) for k in (-2, -1, 1, 2)])
    mov = VGroup(cielo, tierra, lin, esc).shift(DOWN * cabeceo).rotate(np.radians(alabeo), about_point=c)
    g[2].become(Circle(radius=rr, fill_color=CARA, fill_opacity=1, stroke_width=0).move_to(c))
    g.add(mov)
    g.add(marcas(c, -60, 60, 5, largo=0.12, r=rr - 0.02, ancho=3))
    g.add(Triangle(fill_color=WHITE, fill_opacity=1, stroke_width=0).scale(0.08).rotate(PI).move_to(c + UP * (rr - 0.2)))
    av = VGroup(Line(c + LEFT * 0.62, c + LEFT * 0.2, color="#FBBF24", stroke_width=8),
                Line(c + RIGHT * 0.2, c + RIGHT * 0.62, color="#FBBF24", stroke_width=8),
                Dot(c, radius=0.07, color="#FBBF24"))
    g.add(av)
    return g


def altimetro(c):
    c = np.array([*c, 0])
    g = caja(c[:2])
    g.add(marcas(c, 0, 360 - 7.2, 50, cada=5))
    for k in range(10):
        g.add(T(str(k), size=22, color=WHITE, weight=HEAVY).move_to(c + u(k * 36) * (R - 0.42)))
    kol = VGroup(Rectangle(width=0.62, height=0.24, fill_color="#111827", fill_opacity=1, stroke_color="#64748B",
                           stroke_width=1.5), T("1013", size=14, color=WHITE, weight=BOLD)).move_to(c + RIGHT * 0.55)
    g.add(kol, T("PIES", size=13, color=TEXTO_SEC, weight=BOLD).move_to(c + LEFT * 0.5))
    g.add(Line(c, c + u(4.3 * 36) * (R * 0.5), color=WHITE, stroke_width=10))   # miles: 4 500 ft
    g.add(aguja(c, 3 * 36, R - 0.18, ancho=5))                                    # centenas
    return g


def coordinador(c, giro=-20):
    c = np.array([*c, 0])
    g = caja(c[:2])
    for a in (-90, -110, 90, 110):
        g.add(Line(c + u(a) * (R - 0.08), c + u(a) * (R - 0.32), color=WHITE, stroke_width=6))
    g.add(T("L", size=20, color=WHITE, weight=HEAVY).move_to(c + u(-100) * (R - 0.42)),
          T("R", size=20, color=WHITE, weight=HEAVY).move_to(c + u(100) * (R - 0.42)))
    av = VGroup(Line(c + LEFT * 0.75, c + RIGHT * 0.75, color=WHITE, stroke_width=7),
                Circle(radius=0.13, fill_color=WHITE, fill_opacity=1, stroke_width=0).move_to(c),
                Line(c, c + UP * 0.3, color=WHITE, stroke_width=5)).rotate(np.radians(giro), about_point=c)
    g.add(av)
    tubo = RoundedRectangle(width=1.1, height=0.26, corner_radius=0.13, fill_color="#1F2937", fill_opacity=1,
                            stroke_color="#94A3B8", stroke_width=1.5).move_to(c + DOWN * 0.66)
    g.add(tubo, Line(tubo.get_center() + LEFT * 0.16 + UP * 0.13, tubo.get_center() + LEFT * 0.16 + DOWN * 0.13, color=WHITE, stroke_width=2),
          Line(tubo.get_center() + RIGHT * 0.16 + UP * 0.13, tubo.get_center() + RIGHT * 0.16 + DOWN * 0.13, color=WHITE, stroke_width=2),
          Circle(radius=0.1, fill_color=BLACK, fill_opacity=1, stroke_color=WHITE, stroke_width=1.5).move_to(tubo))
    g.add(T("2 MIN", size=12, color=TEXTO_SEC, weight=BOLD).move_to(c + DOWN * 0.95))
    return g


def rumbo(c, rumbo_=30):
    c = np.array([*c, 0])
    g = caja(c[:2])
    for k in range(72):
        a = k * 5 - rumbo_
        l = 0.2 if k % 2 == 0 else 0.11
        g.add(Line(c + u(a) * (R - 0.06), c + u(a) * (R - 0.06 - l), color=WHITE, stroke_width=2.5))
    for k, txt in enumerate(["N", "3", "6", "E", "12", "15", "S", "21", "24", "W", "30", "33"]):
        a = k * 30 - rumbo_
        t = T(txt, size=19 if len(txt) > 1 else 22, color=WHITE if txt not in "NESW" else "#FBBF24", weight=HEAVY)
        g.add(t.rotate(-np.radians(a)).move_to(c + u(a) * (R - 0.42)))
    g.add(Triangle(fill_color="#FBBF24", fill_opacity=1, stroke_width=0).scale(0.09).rotate(PI).move_to(c + UP * (R + 0.02)))
    av = VGroup(Line(c + DOWN * 0.4, c + UP * 0.42, color="#FBBF24", stroke_width=6),
                Line(c + LEFT * 0.4 + UP * 0.05, c + RIGHT * 0.4 + UP * 0.05, color="#FBBF24", stroke_width=6),
                Line(c + LEFT * 0.17 + DOWN * 0.35, c + RIGHT * 0.17 + DOWN * 0.35, color="#FBBF24", stroke_width=5))
    g.add(av)
    return g


def variometro(c):
    c = np.array([*c, 0])
    g = caja(c[:2])
    a_v = lambda v: -90 + v / 2000 * 160
    for v in range(-2000, 2001, 500):
        a = a_v(v)
        g.add(Line(c + u(a) * (R - 0.06), c + u(a) * (R - 0.3 if v % 1000 == 0 else R - 0.18), color=WHITE, stroke_width=3))
    for v, txt in ((0, "0"), (1000, "1"), (2000, "2"), (-1000, "1"), (-2000, "2")):
        a = a_v(v)
        g.add(T(txt, size=20, color=WHITE, weight=HEAVY).move_to(c + u(a) * (R - 0.5)))
    g.add(T("SUBE", size=13, color=TEXTO_SEC, weight=BOLD).move_to(c + UP * 0.4 + RIGHT * 0.3),
          T("BAJA", size=13, color=TEXTO_SEC, weight=BOLD).move_to(c + DOWN * 0.4 + RIGHT * 0.3))
    g.add(aguja(c, a_v(500), R - 0.2))
    return g


class SeisBasicas(ShortBase):
    def construct(self):
        self.add(rejilla())
        xs = (-2.9, 0.0, 2.9)
        y1, y2 = 1.95, -1.95
        insts = [(anemometro, "Anemómetro", "velocidad respecto al aire"),
                 (horizonte, "Horizonte artificial", "cabeceo y alabeo"),
                 (altimetro, "Altímetro", "altitud (por la presión)"),
                 (coordinador, "Coordinador de giro", "giro y derrape"),
                 (rumbo, "Indicador de rumbo", "hacia dónde apunta el morro"),
                 (variometro, "Variómetro", "si sube o baja (×1000 ft/min)")]
        grupo = VGroup()
        for i, (f, nombre, que) in enumerate(insts):
            c = (xs[i % 3], y1 if i < 3 else y2)
            ins = f(c)
            n = T(nombre, size=22, color=TEXTO, weight=HEAVY)
            q = T(que, size=18, color=TEXTO_SEC, weight=MEDIUM)
            for t in (n, q):
                if t.width > 2.7:
                    t.scale_to_fit_width(2.7)
            et = VGroup(n, q).arrange(DOWN, buff=0.06).next_to(ins, DOWN, buff=0.14)
            grupo.add(ins, et)
        marco = RoundedRectangle(width=8.85, height=8.5, corner_radius=0.4, fill_color="#111827", fill_opacity=0.7,
                                 stroke_color="#334155", stroke_width=2).move_to([0, -0.25, 0])
        sup = T("LOS INSTRUMENTOS DE CABINA", size=30, color=TEXTO_SEC, weight=SEMIBOLD)
        tit = T("LAS SEIS BÁSICAS", size=80, weight=HEAVY, font=F_TIT)
        cab = VGroup(sup, tit).arrange(DOWN, buff=0.12).move_to(UP * 5.05)
        nota = T("Dispuestas en «T»: la vista vuelve siempre al horizonte · lecturas de ejemplo",
                 size=19, color=TEXTO_SEC, weight=MEDIUM).move_to(DOWN * 4.4)
        if nota.width > 8.4:
            nota.scale_to_fit_width(8.4)
        pie = T("@porquevuela · Guárdalo", size=26, color=TEXTO_SEC, weight=SEMIBOLD).move_to(DOWN * 5.6)
        reto = T("¿Cuál te costaría más leer? Escríbelo en comentarios ↓", size=28, color=C_CABECEO, weight=HEAVY).move_to(DOWN * 5.0)
        if reto.width > 8.4:
            reto.scale_to_fit_width(8.4)
        self.add(brillo([0, 0, 0], C_CABECEO, 4.6, 0.6), marco, grupo, cab, nota, reto, pie)
        self.wait(0.1)

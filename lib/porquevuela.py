"""
Biblioteca visual de "Por Qué Vuela": formato vertical, estilo, aviones, subtítulos
y la clase base ShortBase con la sincronía a la voz en off.
Uso en un short:  from lib.porquevuela import *
"""
from manim import *
import numpy as np
import json
from pathlib import Path

# ---------- Configuración vertical ----------
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_height = 16
config.frame_width = 9
config.frame_rate = 30

# ---------- Estilo del canal ----------
BG = "#0B1220"
PANEL = "#141E31"
FUS_A = "#F8FAFC"      # luz
FUS_B = "#B9C4D6"      # sombra
OSCURO = "#1E293B"
BORDE = "#64748B"
TEXTO = "#F8FAFC"
TEXTO_SEC = "#8FA0B8"
C_CABECEO = "#38BDF8"
C_ALABEO = "#FB7185"
C_GUINADA = "#FBBF24"
F_TIT = "Inter Display"
F_TXT = "Inter"

config.background_color = BG


# ---------- Utilidades de texto ----------
ANCHO_MAX = 7.4  # ancho útil dentro de las zonas seguras


def T(txt, size=48, color=TEXTO, weight=BOLD, font=F_TXT, **kw):
    t = Text(txt, font=font, font_size=size, color=color, weight=weight, **kw)
    if t.width > ANCHO_MAX:
        t.scale_to_fit_width(ANCHO_MAX)
    return t


def pastilla(texto_mob, color, relleno=0.16, pad_x=0.45, pad_y=0.28):
    alto = texto_mob.height + 2 * pad_y
    caja = RoundedRectangle(width=texto_mob.width + 2 * pad_x, height=alto,
                            corner_radius=alto / 2, fill_color=color, fill_opacity=relleno,
                            stroke_color=color, stroke_width=3).move_to(texto_mob)
    return VGroup(caja, texto_mob)


# ---------- Utilidades de dibujo ----------
def P(*pts):
    return [np.array([x, y, 0.0]) for x, y in pts]


def curva(pts, fill=(FUS_A, FUS_B), sheen=DOWN):
    v = VMobject()
    p = P(*pts)
    v.set_points_smoothly(p + [p[0]])
    v.set_fill(color=list(fill), opacity=1)
    v.set_sheen_direction(sheen)
    v.set_stroke(BORDE, width=1.5)
    return v


def poli(pts, radio=0.08, fill=(FUS_A, FUS_B), sheen=DOWN):
    v = Polygon(*P(*pts)).round_corners(radius=radio)
    v.set_fill(color=list(fill), opacity=1)
    v.set_sheen_direction(sheen)
    v.set_stroke(BORDE, width=1.5)
    return v


def resplandor(color, centro, rmax=4.0):
    return VGroup(*[Circle(radius=r, stroke_width=0, fill_color=color, fill_opacity=0.022)
                    for r in np.linspace(0.6, rmax, 12)]).move_to(centro)


def simbolo_eje(color):
    return VGroup(Circle(radius=0.2, color=color, stroke_width=5).set_fill(BG, 1),
                  Dot(radius=0.07, color=color))


def flecha_giro(centro, radio, inicio, angulo, color):
    arco = Arc(radius=radio, start_angle=inicio, angle=angulo, arc_center=centro,
               color=color, stroke_width=8)
    arco.add_tip(tip_length=0.32, tip_width=0.32)
    return arco


def rejilla():
    pts = VGroup(*[Dot([x, y, 0], radius=0.014, color="#334155")
                   for x in np.arange(-4.2, 4.3, 0.6) for y in np.arange(-7.8, 7.9, 0.6)])
    return pts.set_opacity(0.55)


# ---------- Aviones ----------
def avion_lateral():
    """Vista de lado, morro a la derecha. Devuelve (grupo, elevador, bisagra)."""
    aleta = poli([(-2.25, 0.45), (-3.05, 1.85), (-3.5, 1.85), (-3.45, 0.32)], radio=0.12,
                 sheen=RIGHT)
    fus = curva([(3.55, -0.02), (3.35, 0.24), (2.9, 0.44), (2.0, 0.52), (-1.5, 0.52),
                 (-2.7, 0.44), (-3.5, 0.33), (-3.62, 0.27), (-3.35, 0.08), (-2.4, -0.26),
                 (-1.4, -0.46), (2.0, -0.46), (2.95, -0.38), (3.4, -0.2)])
    franja = Line([-3.0, 0.02, 0], [3.0, 0.02, 0], color=C_CABECEO, stroke_width=3,
                  stroke_opacity=0.6)
    cabina = poli([(2.88, 0.27), (3.2, 0.2), (3.28, 0.11), (2.95, 0.12)], radio=0.03,
                  fill=(OSCURO, OSCURO))
    ventanas = VGroup(*[Circle(radius=0.042, stroke_width=0, fill_color=OSCURO, fill_opacity=0.85)
                        .move_to([x, 0.22, 0]) for x in np.arange(-2.1, 2.5, 0.22)])
    ala = curva([(1.05, -0.17), (0.5, -0.08), (-0.8, -0.1), (-0.85, -0.2), (0.4, -0.26)],
                fill=("#94A3B8", "#64748B"))
    motor = RoundedRectangle(width=1.15, height=0.4, corner_radius=0.2).move_to([0.75, -0.55, 0])
    motor.set_fill(color=["#E2E8F0", "#94A3B8"], opacity=1).set_sheen_direction(DOWN)
    motor.set_stroke(BORDE, width=1.5)
    toma = Ellipse(width=0.12, height=0.36, fill_color=OSCURO, fill_opacity=1,
                   stroke_width=0).move_to([1.3, -0.55, 0])
    pilon = Polygon(*P((0.4, -0.38), (0.9, -0.38), (0.7, -0.22), (0.3, -0.22)),
                    fill_color="#94A3B8", fill_opacity=1, stroke_width=0)
    estab = curva([(-2.85, 0.33), (-3.1, 0.38), (-3.42, 0.37), (-3.42, 0.27), (-3.1, 0.27)],
                  fill=("#CBD5E1", "#94A3B8"))
    bisagra = np.array([-3.4, 0.32, 0])
    elevador = poli([(-3.4, 0.36), (-3.85, 0.33), (-3.85, 0.31), (-3.4, 0.27)], radio=0.02,
                    fill=(C_CABECEO, C_CABECEO))
    grupo = VGroup(aleta, estab, elevador, fus, franja, ventanas, cabina, pilon, motor, toma, ala)
    return grupo, elevador, bisagra


def avion_trasero():
    """Vista desde atrás. Devuelve (grupo, alerón izq., alerón der.)."""
    pend = np.tan(6.5 * DEGREES)

    def ala(s):
        return poli([(s * 0.4, -0.08), (s * 3.75, -0.08 + 3.35 * pend),
                     (s * 3.75, -0.2 + 3.35 * pend), (s * 0.4, -0.3)], radio=0.05,
                    fill=(FUS_A, "#CBD5E1"))

    def winglet(s):
        x, y = s * 3.75, -0.08 + 3.35 * pend
        return poli([(x - s * 0.06, y), (x + s * 0.06, y + 0.55), (x + s * 0.13, y + 0.55),
                     (x + s * 0.06, y - 0.08)], radio=0.03, fill=(FUS_A, "#CBD5E1"))

    def motor(s):
        c = np.array([s * 1.45, -0.55, 0])
        anillo = Circle(radius=0.32).move_to(c)
        anillo.set_fill(color=["#E2E8F0", "#94A3B8"], opacity=1).set_sheen_direction(DOWN)
        anillo.set_stroke(BORDE, width=1.5)
        tobera = Circle(radius=0.17, fill_color=OSCURO, fill_opacity=1, stroke_width=0).move_to(c)
        pilon = Rectangle(width=0.12, height=0.25, fill_color="#94A3B8", fill_opacity=1,
                          stroke_width=0).move_to(c + UP * 0.33)
        return VGroup(pilon, anillo, tobera)

    def aleron(s):
        x = s * 3.0
        y = -0.14 + (3.0 - 0.4) * pend
        r = RoundedRectangle(width=0.9, height=0.1, corner_radius=0.05, fill_color=C_ALABEO,
                             fill_opacity=1, stroke_width=0).move_to([x, y, 0])
        return r.rotate(s * 6.5 * DEGREES)

    estab = poli([(-1.7, 0.42), (1.7, 0.42), (1.7, 0.34), (-1.7, 0.3)], radio=0.03,
                 fill=("#CBD5E1", "#94A3B8"))
    aleta = poli([(-0.11, 0.5), (-0.05, 2.1), (0.05, 2.1), (0.11, 0.5)], radio=0.04,
                 fill=(FUS_A, "#CBD5E1"), sheen=RIGHT)
    fus = Circle(radius=0.58).set_fill(color=[FUS_A, FUS_B], opacity=1)
    fus.set_sheen_direction(DOWN).set_stroke(BORDE, width=1.5)
    cono = Circle(radius=0.16, fill_color="#CBD5E1", fill_opacity=1, stroke_width=0)
    a_i, a_d = aleron(-1), aleron(1)
    grupo = VGroup(estab, aleta, ala(-1), ala(1), winglet(-1), winglet(1), motor(-1), motor(1),
                   fus, cono, a_i, a_d)
    return grupo, a_i, a_d


def avion_superior():
    """Vista desde arriba, morro hacia arriba. Devuelve (grupo, timón, bisagra)."""
    def ala(s):
        return poli([(s * 0.35, 0.75), (s * 3.7, -0.85), (s * 3.78, -1.15), (s * 3.45, -1.22),
                     (s * 0.35, -0.55)], radio=0.1, fill=(FUS_A, "#CBD5E1"), sheen=RIGHT * s)

    def motor(s):
        m = RoundedRectangle(width=0.36, height=0.95, corner_radius=0.17).move_to([s * 1.35, 0.45, 0])
        m.set_fill(color=["#E2E8F0", "#94A3B8"], opacity=1).set_sheen_direction(RIGHT * s)
        return m.set_stroke(BORDE, width=1.5)

    def estab(s):
        return poli([(s * 0.12, -2.45), (s * 1.55, -3.05), (s * 1.6, -3.25), (s * 0.1, -3.05)],
                    radio=0.06, fill=("#E2E8F0", "#CBD5E1"), sheen=RIGHT * s)

    fus = curva([(0, 3.35), (0.24, 3.05), (0.37, 2.4), (0.4, 1.0), (0.37, -1.8), (0.22, -2.95),
                 (0.06, -3.45), (-0.06, -3.45), (-0.22, -2.95), (-0.37, -1.8), (-0.4, 1.0),
                 (-0.37, 2.4), (-0.24, 3.05)], sheen=RIGHT)
    cabina = poli([(-0.2, 2.98), (0.2, 2.98), (0.13, 3.12), (-0.13, 3.12)], radio=0.03,
                  fill=(OSCURO, OSCURO))
    aleta = RoundedRectangle(width=0.1, height=1.1, corner_radius=0.05, fill_color="#94A3B8",
                             fill_opacity=1, stroke_width=0).move_to([0, -2.85, 0])
    bisagra = np.array([0, -3.4, 0])
    timon = RoundedRectangle(width=0.1, height=0.42, corner_radius=0.05, fill_color=C_GUINADA,
                             fill_opacity=1, stroke_width=0).move_to(bisagra + DOWN * 0.2)
    grupo = VGroup(motor(-1), motor(1), ala(-1), ala(1), estab(-1), estab(1), fus, cabina,
                   aleta, timon)
    return grupo, timon, bisagra


# ---------- Subtítulos ----------
SUB_Y = -2.75  # franja reservada para subtítulos (entre la ilustración y el control)


def trozos(texto, max_chars=24):
    """Divide una frase en bloques cortos de lectura rápida."""
    palabras, bloques, actual = texto.split(), [], ""
    for p in palabras:
        prueba = (actual + " " + p).strip()
        if len(prueba) > max_chars and actual:
            bloques.append(actual)
            actual = p
        else:
            actual = prueba
    bloques.append(actual)
    return bloques


def subtitulos(frases):
    """Crea los bloques con sus tiempos (reparto proporcional a la longitud del texto)."""
    items = []
    for ini, fin, texto in frases:
        bl = trozos(texto)
        total = sum(len(b) for b in bl)
        t = ini
        for b in bl:
            dur = (fin - ini) * len(b) / total
            txt = T(b, size=46, weight=BOLD)
            fondo = RoundedRectangle(width=txt.width + 0.5, height=txt.height + 0.32,
                                     corner_radius=0.18, fill_color="#05080F", fill_opacity=0.82,
                                     stroke_width=0).move_to(txt)
            items.append((t, t + dur, VGroup(fondo, txt).move_to([0, SUB_Y, 0])))
            t += dur
    return items




# ---------- Clase base para cada short ----------
class ShortBase(Scene):
    """Carga voz.json (junto al archivo de la escena), reproduce la narración completa,
    añade la rejilla de fondo y la capa de subtítulos sincronizados.
    voz.json: {"completo": "voz.mp3", "segmentos": {clave: {inicio, duracion}},
               "frases": [[inicio, fin, texto], ...]}  (rutas relativas a voz.json)."""
    VOZ_JSON = None          # la subclase define Path(__file__).parent / "voz.json"
    SIN_SUBS_DESDE = None    # clave de segmento a partir de la cual no hay subtítulos

    def setup(self):
        p = Path(self.VOZ_JSON) if self.VOZ_JSON else None
        self.VOZ = json.loads(p.read_text()) if p and p.exists() else {}
        if "completo" in self.VOZ:
            self.VOZ["completo"] = str((p.parent / self.VOZ["completo"]).resolve())

    def iniciar(self):
        V = self.VOZ
        if "completo" in V:
            self.add_sound(V["completo"])
        self.add(rejilla())
        if "frases" in V:
            fin = V.get("segmentos", {}).get(self.SIN_SUBS_DESDE, {}).get("inicio", 1e9)
            items = subtitulos([f for f in V["frases"] if f[0] < fin - 0.05])
            capa = VGroup(*[m for _, _, m in items]).set_z_index(50)
            capa.reloj = 0.0

            def actualizar(grupo, dt):
                grupo.reloj += dt
                for (a, b, m) in items:
                    m.set_opacity(1.0 if a <= grupo.reloj < b else 0.0)

            capa.add_updater(actualizar)
            self.add(capa)

    def voz(self, clave):
        """Espera al inicio del segmento y devuelve (inicio, duración)."""
        seg = self.VOZ.get("segmentos", {}).get(clave)
        if not seg:
            return self.renderer.time, 0.0
        self.hasta(0.0, seg["inicio"])
        return seg["inicio"], seg["duracion"]

    def hasta(self, t0, t):
        resto = t0 + t - self.renderer.time
        if resto > 0.05:
            self.wait(resto)

    def rellenar(self, t0, dur, margen=-0.4, minimo=0.1):
        """Espera hasta el final del segmento; por defecto deja 0.4 s para la transición."""
        resto = t0 + dur + margen - self.renderer.time
        self.wait(max(minimo, resto))

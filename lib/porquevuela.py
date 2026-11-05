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
# fps: lo fija la línea de comandos (--fps 30 narrado; --fps 60 para desenfoque de movimiento)

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


def rejilla(ancho=4.2, alto=7.8):
    """Rejilla de puntos del fondo. Con cámara (zoom y paneo) conviene ampliarla, por ejemplo
    `rejilla(6.6, 10.2)`, para que no se vean los bordes al moverse."""
    pts = VGroup(*[Dot([x, y, 0], radius=0.014, color="#334155")
                   for x in np.arange(-ancho, ancho + 0.1, 0.6)
                   for y in np.arange(-alto, alto + 0.1, 0.6)])
    return pts.set_opacity(0.55)


# ---------- Acabado (sombra, brillo, luces) ----------
def sombra(centro, ancho, alto=None, opacidad=0.35, capas=8):
    """Sombra suave (elipses concéntricas) bajo un objeto: lo despega del fondo."""
    alto = alto if alto is not None else ancho * 0.18
    return VGroup(*[Ellipse(width=ancho * f, height=alto * f, stroke_width=0,
                            fill_color="#000000", fill_opacity=opacidad / capas)
                    for f in np.linspace(1.0, 0.35, capas)]).move_to(centro)


def brillo(centro, color=C_CABECEO, radio=3.2, intensidad=1.0):
    """Halo de color muy suave detrás de la ilustración (profundidad sin distraer)."""
    return VGroup(*[Circle(radius=r, stroke_width=0, fill_color=color,
                           fill_opacity=0.018 * intensidad)
                    for r in np.linspace(0.5, radio, 14)]).move_to(centro)


LUZ_ROJA, LUZ_VERDE, LUZ_BLANCA = "#F43F5E", "#22C55E", "#F8FAFC"


def luz(pos, color, radio=0.05):
    """Luz de navegación con halo (roja = ala izquierda del avión, verde = derecha,
    blanca = cola)."""
    return VGroup(Dot(pos, radius=radio * 3.2, color=color).set_opacity(0.18),
                  Dot(pos, radius=radio * 1.8, color=color).set_opacity(0.35),
                  Dot(pos, radius=radio, color=color))


# ---------- Tipografía cinética ----------
def frase_cinetica(texto, size=56, color=TEXTO, weight=HEAVY, font=F_TIT, ancho=ANCHO_MAX,
                   resaltar=(), color_resalte=C_GUINADA, interlinea=1.22):
    """Frase con salto de línea automático, partida en palabras para que entren una a una
    (`ShortBase.entrar_palabras`). Cada línea se compone como un solo Text, así se conservan
    el interletraje y la línea base. `resaltar`: palabras (sin signos) en `color_resalte`."""
    resaltar = {w.lower().strip("¿?¡!,.:;«»()") for w in resaltar}
    lineas, actual = [], []
    for w in texto.split():
        cand = " ".join(actual + [w])
        if actual and Text(cand, font=font, font_size=size, weight=weight).width > ancho:
            lineas.append(actual)
            actual = [w]
        else:
            actual.append(w)
    lineas.append(actual)
    g = VGroup()
    for ln in lineas:
        t = Text(" ".join(ln), font=font, font_size=size, weight=weight, color=color)
        glifos = list(t.submobjects)
        fila = VGroup()
        if len(glifos) != sum(len(w) for w in ln):      # ligaduras: la línea va entera
            fila.add(t)
        else:
            k = 0
            for w in ln:
                pal = VGroup(*glifos[k:k + len(w)])
                k += len(w)
                if w.lower().strip("¿?¡!,.:;«»()") in resaltar:
                    pal.set_color(color_resalte)
                fila.add(pal)
        g.add(fila)
    alto = Text("Hg", font=font, font_size=size, weight=weight).height
    g.arrange(DOWN, buff=alto * (interlinea - 1) + 0.05)
    if g.width > ancho:
        g.scale_to_fit_width(ancho)
    return g


def palabras(frase):
    """Lista plana de las palabras de una `frase_cinetica`."""
    return [p for fila in frase for p in fila]


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
    # detalles: puertas, línea de paneles, aspas del motor y luces (anticolisión y cola)
    puertas = VGroup(*[RoundedRectangle(width=0.16, height=0.36, corner_radius=0.04,
                                        stroke_color="#94A3B8", stroke_width=1.5, fill_opacity=0)
                       .move_to([x, 0.13, 0]) for x in (2.62, -2.28)])
    paneles = VGroup(*[Line([x, 0.48, 0], [x, -0.4, 0], color="#CBD5E1", stroke_width=0.8,
                            stroke_opacity=0.7) for x in (-1.0, 0.9, 1.9)])
    aspas = VGroup(*[Line([1.3, -0.55 + d, 0], [1.3, -0.55 - d * 0.2, 0], color="#475569",
                          stroke_width=1.2) for d in (0.12, 0.06, -0.06)])
    luces = VGroup(luz([0.2, 0.55, 0], LUZ_ROJA, 0.035), luz([-3.62, 0.27, 0], LUZ_BLANCA, 0.03))
    grupo = VGroup(aleta, estab, elevador, fus, paneles, franja, ventanas, puertas, cabina,
                   pilon, motor, toma, aspas, ala, luces)
    return grupo, elevador, bisagra


def avion_trasero(winglets=True):
    """Vista desde atrás. Devuelve (grupo, alerón izq., alerón der.).
    La punta del ala derecha (a la derecha de la pantalla) está en PUNTA_TRASERO."""
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
    grupo = VGroup(estab, aleta, ala(-1), ala(1), motor(-1), motor(1), fus, cono, a_i, a_d)
    if winglets:
        grupo.add(winglet(-1), winglet(1))
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
    def detalles(s):
        # flaps y alerón (líneas paralelas al borde de salida), toma del motor, luz de punta
        a, b = np.array([s * 3.45, -1.22, 0]), np.array([s * 0.35, -0.55, 0])
        sub = lambda f: a + (b - a) * f + UP * 0.2       # noqa: E731
        flaps = VGroup(Line(sub(0.32), sub(0.95), color="#94A3B8", stroke_width=1.6),
                       Line(sub(0.06), sub(0.3), color=C_ALABEO, stroke_width=1.6,
                            stroke_opacity=0.6))
        toma = Ellipse(width=0.3, height=0.1, fill_color=OSCURO, fill_opacity=1,
                       stroke_width=0).move_to([s * 1.35, 0.9, 0])
        color = LUZ_VERDE if s > 0 else LUZ_ROJA          # vista desde arriba, morro arriba
        return VGroup(flaps, toma, luz([s * 3.74, -1.0, 0], color, 0.045))

    paneles = VGroup(*[Line([-0.36, y, 0], [0.36, y, 0], color="#CBD5E1", stroke_width=0.8,
                            stroke_opacity=0.8) for y in (2.2, 1.2, -0.9, -2.0)])
    grupo = VGroup(motor(-1), motor(1), ala(-1), ala(1), estab(-1), estab(1), fus, paneles,
                   cabina, aleta, timon, detalles(-1), detalles(1),
                   luz([0, -3.45, 0], LUZ_BLANCA, 0.04))
    return grupo, timon, bisagra


PUNTA_TRASERO = np.array([3.75, -0.14 + 3.35 * np.tan(6.5 * DEGREES), 0.0])


def winglet_trasero(s=1):
    """Winglet suelto (vista desde atrás) para hacerlo aparecer sobre avion_trasero(False)."""
    pend = np.tan(6.5 * DEGREES)
    x, y = s * 3.75, -0.08 + 3.35 * pend
    return poli([(x - s * 0.06, y), (x + s * 0.06, y + 0.55), (x + s * 0.13, y + 0.55),
                 (x + s * 0.06, y - 0.08)], radio=0.03, fill=(FUS_A, "#CBD5E1"))


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




# ---------- Aerodinámica: perfil alar y flujo ----------
class Perfil:
    """Perfil de Joukowski en flujo potencial 2D con condición de Kutta (flujo ideal:
    sin viscosidad ni estela). Es una simplificación, pero da campos de velocidad y presión
    físicamente coherentes: el aire de arriba llega antes al borde de salida, hay
    deflexión hacia abajo detrás del ala y la presión es menor arriba que abajo.

    El viento llega horizontal desde la izquierda (velocidad U = 1 en unidades del
    perfil); el ala aparece con la nariz levantada `alfa` grados. Cuerda ≈ 4·escala.
    Todas las salidas están en coordenadas de pantalla."""

    def __init__(self, alfa=7.0, mu=complex(-0.09, 0.11), escala=1.45, centro=(0.0, 0.5)):
        self.alfa = np.radians(alfa)
        self.mu = mu
        self.R = abs(1 - mu)
        beta = -np.angle(1 - mu)
        self.gamma = 4 * np.pi * self.R * np.sin(self.alfa + beta)   # Kutta
        self.escala = escala
        self.c = complex(*centro)
        self._rot = np.exp(-1j * self.alfa)

    # --- transformaciones ---
    def _pant(self, z):
        w = self.c + self.escala * self._rot * np.asarray(z)
        return np.stack([w.real, w.imag, np.zeros_like(w.real)], axis=-1)

    def _desde_pant(self, x, y):
        return (complex(x, y) - self.c) / (self.escala * self._rot)

    def _zeta(self, z):
        r = np.sqrt(z * z - 4)
        a, b = (z + r) / 2, (z - r) / 2
        return a if abs(a - self.mu) >= abs(b - self.mu) else b

    def _dw(self, zeta):
        """Derivada del potencial complejo respecto a zeta (flujo alrededor del círculo)."""
        zp = zeta - self.mu
        a = self.alfa
        return (np.exp(-1j * a) - self.R ** 2 * np.exp(1j * a) / zp ** 2
                + 1j * self.gamma / (2 * np.pi * zp))

    def velocidad(self, zeta):
        """Velocidad física (vector complejo en ejes del perfil) en el punto zeta."""
        return np.conj(self._dw(zeta) / (1 - 1 / zeta ** 2))

    # --- geometría ---
    def puntos_contorno(self, n=240):
        th = np.linspace(0, 2 * np.pi, n, endpoint=False)
        zeta = self.mu + self.R * np.exp(1j * th)
        return self._pant(zeta + 1 / zeta)

    def borde_ataque(self):
        p = self.puntos_contorno(720)
        return p[np.argmin(p[:, 0])]

    def borde_salida(self):
        return self._pant(np.array([2.0 + 0j]))[0]

    def contorno(self, color_borde=BORDE):
        v = VMobject()
        pts = list(self.puntos_contorno())
        v.set_points_as_corners(pts + [pts[0]])
        v.make_smooth()
        v.set_fill(color=[FUS_A, "#94A3B8"], opacity=1).set_sheen_direction(DOWN)
        return v.set_stroke(color_borde, width=2)

    # --- líneas de corriente con tiempo de paso ---
    def linea(self, y, x_ini=-6.5, x_fin=6.5, paso=0.015):
        """Línea de corriente que entra a altura de pantalla `y` por x_ini.
        Devuelve (puntos Nx3 en pantalla, tiempos N): el tiempo que tarda una partícula en
        llegar a cada punto (unidades del perfil, U = 1)."""
        zeta = self._zeta(self._desde_pant(x_ini, y))

        def dir_(q):
            v = np.conj(self._dw(q))
            return v / (abs(v) + 1e-12)

        zs = [zeta]
        for _ in range(20000):
            k1 = dir_(zeta)
            k2 = dir_(zeta + paso / 2 * k1)
            k3 = dir_(zeta + paso / 2 * k2)
            k4 = dir_(zeta + paso * k3)
            zeta = zeta + paso / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
            zs.append(zeta)
            if self._pant(zeta + 1 / zeta)[0] > x_fin:
                break
        zs = np.array(zs)
        pts = self._pant(zs + 1 / zs)
        mid = (zs[1:] + zs[:-1]) / 2
        rapidez = np.abs(self.velocidad(mid)) * self.escala   # en unidades de pantalla
        ds = np.linalg.norm(np.diff(pts, axis=0), axis=1)
        t = np.concatenate([[0.0], np.cumsum(ds / np.maximum(rapidez, 1e-3))])
        return pts, t

    def cp_contorno(self, n=160, margen=0.03):
        """Puntos del contorno (sin el borde de salida), normal exterior y Cp = 1 − (V/U)²."""
        th = np.linspace(margen, 2 * np.pi - margen, n)
        zeta = self.mu + self.R * np.exp(1j * th)
        pts = self._pant(zeta + 1 / zeta)
        cp = 1 - np.abs(self.velocidad(zeta)) ** 2
        tang = np.gradient(pts, axis=0)
        nrm = np.stack([tang[:, 1], -tang[:, 0], np.zeros(n)], axis=1)  # contorno antihorario
        nrm /= np.linalg.norm(nrm, axis=1, keepdims=True)
        return pts, nrm, cp


def en_tiempo(pts, tiempos, t):
    """Posición sobre una línea de corriente en el instante t (interpolación lineal)."""
    if t <= tiempos[0]:
        return pts[0]
    if t >= tiempos[-1]:
        return pts[-1]
    i = np.searchsorted(tiempos, t)
    f = (t - tiempos[i - 1]) / (tiempos[i] - tiempos[i - 1])
    return pts[i - 1] + f * (pts[i] - pts[i - 1])


def trazo(pts, color="#475569", ancho=2.5, opacidad=0.9):
    v = VMobject().set_points_smoothly(list(pts[::4]) + [pts[-1]])
    return v.set_stroke(color, width=ancho, opacity=opacidad)


def trazadores(lineas, reloj, color, cada=0.6, radio=0.045, velocidad=1.0):
    """Puntos que avanzan por cada línea de corriente a su velocidad real
    (más rápido donde el aire va más rápido). `reloj` es un ValueTracker en segundos."""
    grupo = VGroup()
    for pts, tt in lineas:
        n = int(tt[-1] / cada) + 1
        for k in range(n):
            d = Dot(radius=radio, color=color)
            d.datos = (pts, tt, k * cada)
            grupo.add(d)

    def mover(g):
        tr = reloj.get_value() * velocidad
        for d in g:
            pts, tt, fase = d.datos
            t = (tr + fase) % (tt[-1])
            d.move_to(en_tiempo(pts, tt, t))
    grupo.add_updater(mover)
    mover(grupo)
    return grupo


def vector(inicio, fin, color, ancho=10, punta=0.32):
    """Flecha de fuerza o de flujo con proporciones constantes."""
    inicio, fin = np.array(inicio, dtype=float), np.array(fin, dtype=float)
    return Arrow(inicio, fin, buff=0, color=color, stroke_width=ancho,
                 max_tip_length_to_length_ratio=punta / max(np.linalg.norm(fin - inicio), 1e-3),
                 max_stroke_width_to_length_ratio=100)


def flechas_presion(perfil, color_menos, color_mas, k=0.55, lmax=1.0, cada=6):
    """Flechas de la fuerza de presión sobre el contorno: donde la presión es menor que la
    del aire libre (Cp < 0) tiran hacia fuera; donde es mayor (Cp > 0) empujan hacia dentro.
    Devuelve (flechas de succión, flechas de empuje)."""
    pts, nrm, cp = perfil.cp_contorno()
    menos, mas = VGroup(), VGroup()
    for p, n_, c in list(zip(pts, nrm, cp))[::cada]:
        L = min(abs(c) * k, lmax)
        if L < 0.12:
            continue
        if c < 0:
            menos.add(vector(p + n_ * 0.05, p + n_ * (0.05 + L), color_menos, ancho=5, punta=0.16))
        else:
            mas.add(vector(p + n_ * (0.05 + L), p + n_ * 0.05, color_mas, ancho=5, punta=0.16))
    return menos, mas


# ---------- Pérdida: curvas típicas, familias de líneas y flujo separado ----------
ALFA_CRIT = 15.0   # orden de magnitud del ángulo crítico de un perfil típico (grados)


def cl_tipico(alfa, pendiente=0.1, cl0=0.2, alfa_crit=ALFA_CRIT, caida=0.55, escala_caida=1.2):
    """Coeficiente de sustentación de una curva TÍPICA (forma genérica, no datos de un perfil
    concreto): lineal (≈ 0,1/grado), redondeo hasta el máximo en `alfa_crit` y caída brusca
    después (pérdida). `alfa` en grados; acepta escalar o array."""
    a = np.asarray(alfa, dtype=float)
    k = pendiente / 8.0
    a1 = alfa_crit - 4.0
    clmax = pendiente * a1 + cl0 + 2 * pendiente
    lin = cl0 + pendiente * a
    red = clmax - k * (a - alfa_crit) ** 2
    post = clmax - caida * (1 - np.exp(-(a - alfa_crit) / escala_caida))
    return np.where(a <= a1, lin, np.where(a <= alfa_crit, red, post))


def cd_tipico(alfa, alfa_crit=ALFA_CRIT):
    """Coeficiente de resistencia típico (forma genérica): crece suave con el ángulo y se
    dispara al separarse el flujo."""
    a = np.asarray(alfa, dtype=float)
    salto = np.where(a > alfa_crit, 0.18 * (1 - np.exp(-(a - alfa_crit) / 1.5)), 0.0)
    return 0.012 + 0.0006 * a ** 2 + salto


class GraficaCl(VGroup):
    """Gráfica de coeficiente de sustentación frente a ángulo de ataque con la curva típica
    (`cl_tipico`), rotulada como tal. `self.punto(alfa)` da la posición en pantalla;
    `self.curva_hasta(alfa)` devuelve el trazo de la curva desde 0 hasta `alfa`."""

    def __init__(self, ancho=6.4, alto=2.3, alfa_max=21, cl_max=1.7, color=C_CABECEO,
                 nota="curva típica, no de un perfil concreto", **kw):
        super().__init__(**kw)
        self.color = color
        self.alfa_max = alfa_max
        self.ejes = Axes(x_range=[0, alfa_max, 5], y_range=[0, cl_max, 0.5], x_length=ancho,
                         y_length=alto, tips=False,
                         axis_config={"color": BORDE, "stroke_width": 3, "include_ticks": False})
        marcas = VGroup()
        for a in range(0, alfa_max, 5):
            p = self.ejes.c2p(a, 0)
            marcas.add(Line(p, p + DOWN * 0.1, color=BORDE, stroke_width=3))
            marcas.add(T(f"{a}°", size=20, color=TEXTO_SEC, weight=MEDIUM)
                       .next_to(p, DOWN, buff=0.14))
        self.x_txt = T("α", size=30, color=TEXTO_SEC, weight=BOLD)
        self.x_txt.next_to(self.ejes.c2p(alfa_max, 0), RIGHT, buff=0.15)
        self.y_txt = T("sustentación", size=22, color=TEXTO_SEC, weight=SEMIBOLD).rotate(PI / 2)
        self.y_txt.next_to(self.ejes.c2p(0, cl_max / 2), LEFT, buff=0.15)
        self.nota = T(nota, size=19, color=TEXTO_SEC, weight=MEDIUM)
        self.nota.next_to(self.ejes.c2p(alfa_max, cl_max), UP, buff=0.12).align_to(
            self.ejes.c2p(alfa_max, 0), RIGHT)
        self.guia = self.ejes.plot(lambda a: float(cl_tipico(a)), x_range=[0, alfa_max - 0.5],
                                   color=color, stroke_width=3).set_stroke(opacity=0.22)
        self.add(self.ejes, marcas, self.x_txt, self.y_txt, self.nota, self.guia)

    def punto(self, alfa):
        return self.ejes.c2p(alfa, float(cl_tipico(alfa)))

    def curva_hasta(self, alfa, ancho=7):
        a = np.linspace(0, max(alfa, 0.05), 120)
        v = VMobject().set_points_smoothly([self.punto(x) for x in a])
        return v.set_stroke(self.color, width=ancho)

    def marca_critico(self, alfa=ALFA_CRIT, texto="≈ 15°", color=TEXTO):
        p = self.punto(alfa)
        lin = DashedLine(self.ejes.c2p(alfa, 0), p, color=color, stroke_width=3,
                         dash_length=0.08)
        txt = T(texto, size=24, color=color, weight=BOLD)
        txt.next_to(self.ejes.c2p(alfa, 0.3 * float(cl_tipico(alfa))), LEFT, buff=0.12)
        return VGroup(lin, txt)


def remuestrear(pts, tiempos, n=220):
    """Remuestrea una línea de corriente a n puntos equiespaciados en longitud."""
    s = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))])
    u = np.linspace(0, s[-1], n)
    nuevo = np.stack([np.interp(u, s, pts[:, i]) for i in range(3)], axis=1)
    return nuevo, np.interp(u, s, tiempos)


class LineasPorAlfa:
    """Familia de líneas de corriente (flujo ideal, `Perfil`) precalculadas para varios
    ángulos de ataque e interpoladas entre ellos, para animar el ala girando con el flujo
    pegado. `perfil(alfa)` construye el Perfil; `en(alfa)` → [(pts, tiempos), ...]."""

    def __init__(self, perfil, alfas, ys, x_ini=-4.6, x_fin=4.6, n=220, paso=0.02):
        self.alfas = np.array(alfas, dtype=float)
        self.datos = []
        for a in self.alfas:
            P = perfil(a)
            self.datos.append([remuestrear(*P.linea(y, x_ini=x_ini, x_fin=x_fin, paso=paso), n=n)
                               for y in ys])

    def en(self, alfa):
        a = float(np.clip(alfa, self.alfas[0], self.alfas[-1]))
        i = int(np.clip(np.searchsorted(self.alfas, a) - 1, 0, len(self.alfas) - 2))
        f = (a - self.alfas[i]) / (self.alfas[i + 1] - self.alfas[i])
        return [((1 - f) * p0 + f * p1, (1 - f) * t0 + f * t1)
                for (p0, t0), (p1, t1) in zip(self.datos[i], self.datos[i + 1])]


def trazadores_variables(fuente, reloj, color, cada=0.6, radio=0.045, velocidad=1.0):
    """Como `trazadores`, pero las líneas cambian con el tiempo: `fuente()` devuelve la
    lista [(pts, tiempos), ...] actual (por ejemplo, LineasPorAlfa.en(alfa))."""
    lineas = fuente()
    grupo = VGroup()
    for j, (_, tt) in enumerate(lineas):
        for k in range(int(tt[-1] / cada) + 1):
            d = Dot(radius=radio, color=color)
            d.datos = (j, k * cada)
            grupo.add(d)

    def mover(g):
        ls = fuente()
        tr = reloj.get_value() * velocidad
        for d in g:
            j, fase = d.datos
            pts, tt = ls[j]
            d.move_to(en_tiempo(pts, tt, (tr + fase) % tt[-1]))
    grupo.add_updater(mover)
    mover(grupo)
    return grupo


def flujo_separado(perfil, ys, x_ini=-4.6, x_fin=4.6, sep=0.12, relajacion=1.6, rapidez=0.9,
                   paso=0.02):
    """ILUSTRACIÓN CUALITATIVA del flujo separado (el flujo potencial no puede separarse).
    Las líneas de debajo del ala siguen el modelo ideal; las de encima lo siguen hasta la
    vertical del punto de separación (fracción `sep` de la cuerda desde el borde de ataque)
    y desde ahí siguen casi rectas, girando poco a poco hacia la horizontal: dejan entre
    ellas y el extradós una zona de aire revuelto. Devuelve (líneas [(pts, t)], capa límite
    [(pts)], punto de separación)."""
    le, te = perfil.borde_ataque(), perfil.borde_salida()
    cont = perfil.puntos_contorno(720)
    x_s = le[0] + sep * (te[0] - le[0])
    arriba = cont[(np.abs(cont[:, 0] - x_s) < 0.05)]
    p_sep = arriba[np.argmax(arriba[:, 1])]
    lineas = []
    for y in ys:
        pts, tt = perfil.linea(y, x_ini=x_ini, x_fin=x_fin, paso=paso)
        i = np.argmax(pts[:, 0] >= x_s)
        if pts[i, 1] < p_sep[1] - 0.02:          # pasa por debajo: flujo pegado
            lineas.append((pts, tt))
            continue
        d0 = pts[i] - pts[max(i - 6, 0)]
        th0 = np.arctan2(d0[1], d0[0])
        if pts[i, 1] - p_sep[1] < 0.25:          # la más cercana sale del punto de separación
            th0 = max(th0, np.radians(-4))
        nuevo, t_n = [pts[i]], [tt[i]]
        s, ds = 0.0, 0.03
        while nuevo[-1][0] < x_fin:
            s += ds
            th = th0 * np.exp(-s / relajacion)
            nuevo.append(nuevo[-1] + ds * np.array([np.cos(th), np.sin(th), 0.0]))
            t_n.append(t_n[-1] + ds / (rapidez * perfil.escala))
        lineas.append((np.vstack([pts[:i], np.array(nuevo)]),
                       np.concatenate([tt[:i], np.array(t_n)])))
    return lineas, p_sep


def remolinos(perfil, p_sep, techo, reloj, color="#CBD5E1", n=7, largo=None, vel=0.55,
              radio=(0.1, 0.22), giro=-3.0, visible=None):
    """Remolinos (sentido horario: arriba el aire sigue, junto al ala vuelve) que nacen tras el
    punto de separación y se van con la estela. `techo(x)` da la altura de la línea separada
    más baja. Ilustración cualitativa. `reloj`: ValueTracker en segundos; `visible`:
    ValueTracker opcional (0–1) para hacerlos aparecer sin animar el grupo (que se redibuja
    entero en cada fotograma)."""
    te = perfil.borde_salida()
    le = perfil.borde_ataque()
    cont = perfil.puntos_contorno(720)
    sup = cont[cont[:, 1] >= np.interp(cont[:, 0], [le[0], te[0]], [le[1], te[1]])]
    sup = sup[np.argsort(sup[:, 0])]
    x0 = p_sep[0] + 0.35
    x1 = te[0] + (largo if largo is not None else 2.6)
    xs = np.linspace(x0, x1, 200)
    suelo = np.where(xs <= te[0], np.interp(xs, sup[:, 0], sup[:, 1]),
                     te[1] - 0.12 * (xs - te[0]))
    cielo = np.array([techo(x) for x in xs])
    medio = (suelo + cielo) / 2
    hueco = np.clip(cielo - suelo, 0.1, None)
    L = x1 - x0
    grupo = VGroup(*[VMobject() for _ in range(n)])
    for k, e in enumerate(grupo):
        e.fase = k * L / n

    def mover(g):
        t = reloj.get_value()
        vis = visible.get_value() if visible is not None else 1.0
        for e in g:
            s = (t * vel + e.fase) % L
            x = x0 + s
            y = np.interp(x, xs, medio)
            r = np.clip(0.38 * np.interp(x, xs, hueco), *radio) * (0.6 + 0.4 * min(s / 0.6, 1))
            arco = Arc(radius=r, start_angle=giro * t + e.fase * 2.0, angle=-1.6 * PI,
                       arc_center=[x, y, 0], color=color, stroke_width=4)
            arco.add_tip(tip_length=0.12, tip_width=0.12)
            op = 0.8 * vis * max(min(1.0, s / 0.5, (L - s) / 0.8), 0)
            arco.set_stroke(opacity=op)
            arco.tip.set_fill(opacity=op).set_stroke(opacity=op)
            e.become(arco)
    grupo.add_updater(mover)
    mover(grupo)
    return grupo


def angulo_entre(vertice, ang_ref, ang, radio, color, ancho=5):
    """Arco entre dos direcciones (en radianes) desde `vertice`."""
    return Arc(radius=radio, start_angle=ang_ref, angle=ang - ang_ref, arc_center=vertice,
               color=color, stroke_width=ancho)


# ---------- Perfiles NACA (geometría exacta de las ecuaciones publicadas) ----------
_NACA5 = {1: (0.05, 0.0580, 361.40), 2: (0.10, 0.1260, 51.640), 3: (0.15, 0.2025, 15.957),
          4: (0.20, 0.2900, 6.643), 5: (0.25, 0.3910, 3.230)}   # p, r, k1 (Cl de diseño 0,3)


def naca_espesor(x, t, cerrado=True):
    """Semiespesor de la familia NACA (x y resultado en fracción de cuerda)."""
    a4 = -0.1036 if cerrado else -0.1015
    return 5 * t * (0.2969 * np.sqrt(x) - 0.1260 * x - 0.3516 * x ** 2 + 0.2843 * x ** 3
                    + a4 * x ** 4)


def naca_linea_media(codigo, x):
    """Línea media (yc, dyc/dx) de un perfil NACA de 4 cifras ('2412') o de 5 cifras con
    línea media normal ('23012'). Acepta también parámetros continuos para animar:
    codigo = ('4', m, p) o ('5', cl_diseno, digito_p)."""
    x = np.asarray(x, dtype=float)
    if isinstance(codigo, str):
        if len(codigo) == 4:
            codigo = ("4", int(codigo[0]) / 100, int(codigo[1]) / 10)
        elif len(codigo) == 5:
            if codigo[2] != "0":
                raise ValueError("solo línea media normal (tercera cifra 0)")
            codigo = ("5", int(codigo[0]) * 0.15, int(codigo[1]))
    if codigo[0] == "4":
        _, m, p = codigo
        if m == 0 or p == 0:
            return np.zeros_like(x), np.zeros_like(x)
        yc = np.where(x < p, m / p ** 2 * (2 * p * x - x ** 2),
                      m / (1 - p) ** 2 * ((1 - 2 * p) + 2 * p * x - x ** 2))
        dy = np.where(x < p, 2 * m / p ** 2 * (p - x), 2 * m / (1 - p) ** 2 * (p - x))
        return yc, dy
    _, cl, dp = codigo
    _, r, k1 = _NACA5[int(dp)]
    f = cl / 0.3
    yc = np.where(x < r, k1 / 6 * (x ** 3 - 3 * r * x ** 2 + r ** 2 * (3 - r) * x),
                  k1 * r ** 3 / 6 * (1 - x))
    dy = np.where(x < r, k1 / 6 * (3 * x ** 2 - 6 * r * x + r ** 2 * (3 - r)), -k1 * r ** 3 / 6)
    return f * yc, f * dy


def naca_puntos(codigo, t, n=160):
    """Contorno (extradós e intradós) de un perfil NACA con espesor t (fracción de cuerda).
    Devuelve (x_sup, y_sup, x_inf, y_inf, x, yc) en fracción de cuerda."""
    beta = np.linspace(0, np.pi, n)
    x = (1 - np.cos(beta)) / 2          # más puntos cerca de los bordes
    yt = naca_espesor(x, t)
    yc, dy = naca_linea_media(codigo, x)
    th = np.arctan(dy)
    return (x - yt * np.sin(th), yc + yt * np.cos(th), x + yt * np.sin(th),
            yc - yt * np.cos(th), x, yc)


class PerfilNACA:
    """Perfil NACA dibujado a escala real (sin exagerar) entre `inicio` y `inicio + cuerda`
    en pantalla. `codigo`: '2412', '0012', '23012' o tupla de parámetros continuos (ver
    naca_linea_media); `t`: espesor (fracción de cuerda), por defecto el del código."""

    def __init__(self, codigo, t=None, cuerda=7.0, inicio=(-3.5, 0.0)):
        if t is None:
            t = int(codigo[-2:]) / 100
        self.codigo, self.t, self.cuerda = codigo, t, cuerda
        self.o = np.array([inicio[0], inicio[1], 0.0])
        self.xs, self.ys, self.xi, self.yi, self.x, self.yc = naca_puntos(codigo, t)

    def p(self, x, y):
        return self.o + self.cuerda * np.array([x, y, 0.0])

    def contorno(self, color_borde=BORDE):
        sup = [self.p(a, b) for a, b in zip(self.xs, self.ys)]
        inf = [self.p(a, b) for a, b in zip(self.xi, self.yi)]
        v = VMobject().set_points_as_corners(sup[::-1] + inf[1:] + [sup[-1]])
        v.set_fill(color=[FUS_A, "#94A3B8"], opacity=1).set_sheen_direction(DOWN)
        return v.set_stroke(color_borde, width=2)

    def linea_media(self, color, ancho=4):
        v = VMobject().set_points_as_corners([self.p(a, b) for a, b in zip(self.x, self.yc)])
        return v.set_stroke(color, width=ancho)

    def cuerda_linea(self, color=TEXTO_SEC):
        return DashedLine(self.p(0, 0), self.p(1, 0), color=color, stroke_width=3,
                          dash_length=0.1)

    def max_curvatura(self):
        i = int(np.argmax(self.yc))
        return self.x[i], self.yc[i]

    def max_espesor(self):
        e = self.ys - np.interp(self.xs, self.xi, self.yi)
        i = int(np.argmax(e))
        return self.xs[i], np.interp(self.xs[i], self.xi, self.yi), self.ys[i]


# ---------- Vórtices de punta ----------
def espiral(centro, radio, fase=0.0, sentido=1, vueltas=1.6, color=TEXTO, ancho=4, opacidad=1.0,
            punta=True):
    """Brazo de espiral que se enrolla hacia el centro. sentido=+1: giro antihorario (en el
    plano de la pantalla), −1: horario. La punta de flecha indica el sentido del giro."""
    th = np.linspace(0, vueltas * TAU, 90)
    r = radio * (0.12 + 0.88 * th / th[-1])
    ang = fase + sentido * th
    pts = [np.array(centro) + np.array([ri * np.cos(a), ri * np.sin(a), 0]) for ri, a in zip(r, ang)]
    v = VMobject().set_points_smoothly(pts)
    v.set_stroke(color, width=ancho, opacity=opacidad)
    if punta:
        # el aire avanza en el sentido del giro: punta al final exterior
        a = ang[-1]
        t = sentido * np.array([-np.sin(a), np.cos(a), 0])
        tri = Triangle(fill_color=color, fill_opacity=opacidad, stroke_width=0).scale(0.09 * ancho / 4)
        tri.rotate(np.arctan2(t[1], t[0]) - PI / 2).move_to(pts[-1] + t * 0.05)
        return VGroup(v, tri)
    return VGroup(v)


def vortice(centro, reloj, radio=0.6, sentido=1, color=TEXTO, brazos=2, vel=2.5, ancho=4,
            visible=None, escala=None):
    """Vórtice visto de frente (eje perpendicular a la pantalla) que gira con `reloj`.
    sentido=+1 antihorario, −1 horario. Visto desde atrás de un avión, el vórtice de la punta
    derecha gira en sentido antihorario y el de la izquierda en horario. `centro` puede ser un
    callable (para que se mueva); `visible` y `escala`, ValueTracker opcionales."""
    g = VGroup()

    def dib(m):
        c = centro() if callable(centro) else centro
        op = visible.get_value() if visible is not None else 1.0
        r = radio * (escala.get_value() if escala is not None else 1.0)
        nuevo = VGroup(*[espiral(c, r, fase=sentido * vel * reloj.get_value() + k * TAU / brazos,
                                 sentido=sentido, color=color, ancho=ancho, opacidad=op)
                         for k in range(brazos)])
        m.become(nuevo)
    g.add_updater(dib)
    dib(g)
    return g


def rodeo_punta(punta, sentido=1, color=TEXTO, ancho=6):
    """Flecha curva que sube por fuera de la punta del ala: del intradós (abajo) al extradós
    (arriba). sentido=+1 para la punta derecha, −1 para la izquierda."""
    p = np.array(punta)
    a = p + np.array([-sentido * 0.45, -0.45, 0])
    b = p + np.array([-sentido * 0.45, 0.5, 0])
    arco = ArcBetweenPoints(a, b, angle=sentido * 1.15 * PI, color=color, stroke_width=ancho)
    arco.add_tip(tip_length=0.22, tip_width=0.22)
    return arco


def estela_superior(p_izq, p_der, largo, reloj, color=TEXTO, amplitud=0.12, onda=0.9, vel=1.5,
                    ancho=4, visible=None):
    """Vista desde arriba: dos estelas helicoidales (vórtices) que salen de las puntas hacia
    atrás (hacia abajo en pantalla). Ilustración: la hélice representa el giro del vórtice."""
    g = VGroup()

    def dib(m):
        op = visible.get_value() if visible is not None else 1.0
        lineas = VGroup()
        for p, s in ((np.array(p_izq), -1), (np.array(p_der), 1)):
            ys = np.linspace(0, largo, 160)
            for fase in (0, PI):
                xs = s * amplitud * np.sin(TAU * ys / onda + s * vel * reloj.get_value() + fase)
                fade = np.clip(1 - ys / largo, 0, 1)
                pts = [p + np.array([x, -y, 0]) for x, y in zip(xs, ys)]
                v = VMobject().set_points_smoothly(pts)
                v.set_stroke(color, width=ancho, opacity=op * (0.9 if fase == 0 else 0.45))
                lineas.add(v)
        m.become(lineas)
    g.add_updater(dib)
    dib(g)
    return g


# ---------- Hélices: velocidad por sección, triángulo de velocidades y torsión ----------
def angulo_flujo(v_avance, omega, r):
    """Ángulo φ (grados) entre el viento relativo de una sección de pala y el plano de giro:
    tan φ = V / (ω·r). Simplificación: sin la velocidad inducida por la propia hélice
    (que aumenta un poco φ) ni la rotación de la estela."""
    return float(np.degrees(np.arctan2(v_avance, omega * r)))


def pala_frontal(radio, raiz=0.32, cuerda=(0.2, 0.34, 0.16), color=(FUS_A, "#94A3B8")):
    """Silueta de una pala vista de frente, desde el centro (origen) hacia +Y hasta `radio`:
    estrecha en la raíz, más ancha hacia el medio y redondeada en la punta."""
    c0, c1, c2 = cuerda
    der = [(c0 / 2, raiz), (c1 / 2, 0.45 * radio), (c1 / 2 * 0.92, 0.75 * radio),
           (c2 / 2, 0.97 * radio)]
    izq = [(-x * 0.85, y) for x, y in der[::-1]]
    pts = der + [(0.0, radio)] + izq
    return curva(pts, fill=color, sheen=RIGHT)


class HeliceFrontal(VGroup):
    """Hélice vista de frente (desde delante del avión), con `palas` palas y buje.
    `self.angulo` (ValueTracker, radianes) gira el conjunto con un updater: ángulo positivo,
    sentido antihorario en pantalla. La pala 0 apunta hacia arriba con ángulo 0.
    `self.punto(r)` da la posición en pantalla del punto a distancia r sobre la pala 0."""

    def __init__(self, centro=(0.0, 0.0), radio=2.8, palas=2, **kw):
        super().__init__(**kw)
        self.c = np.array([centro[0], centro[1], 0.0])
        self.radio = radio
        self.angulo = ValueTracker(0.0)
        self.palas = VGroup(*[pala_frontal(radio).rotate(k * TAU / palas, about_point=ORIGIN)
                              for k in range(palas)])
        buje = Circle(radius=0.36).set_fill(color=["#E2E8F0", "#64748B"], opacity=1)
        buje.set_sheen_direction(DR).set_stroke(BORDE, width=2)
        self.add(self.palas, buje)
        self.shift(self.c)
        self._ang = 0.0

        def girar(m):
            a = self.angulo.get_value()
            m.palas.rotate(a - m._ang, about_point=m.c)
            m._ang = a
        self.add_updater(girar)

    def punto(self, r):
        a = self.angulo.get_value()
        return self.c + r * np.array([-np.sin(a), np.cos(a), 0.0])

    def tangente(self, signo=1):
        """Dirección del movimiento de la pala 0 (signo=+1 si gira antihorario)."""
        a = self.angulo.get_value()
        return signo * np.array([-np.cos(a), -np.sin(a), 0.0])


def seccion_pala(le, beta, cuerda=1.3, codigo="4412", color_borde=BORDE):
    """Sección de pala (perfil NACA a escala) vista desde la punta: el borde de ataque en `le`,
    el trozo se mueve hacia la izquierda y el avión avanza hacia arriba de la pantalla. La
    cuerda baja hacia la derecha formando el ángulo de pala `beta` (grados) con el plano de
    giro (horizontal); el extradós mira hacia delante (arriba)."""
    p = PerfilNACA(codigo, cuerda=cuerda, inicio=(0.0, 0.0))
    v = p.contorno(color_borde)
    v.rotate(-beta * DEGREES, about_point=ORIGIN).shift(np.array(le, dtype=float))
    return v


def triangulo_velocidades(punto, u, v, escala, c_giro, c_avance, c_rel, ancho=8, punta=0.24):
    """Viento relativo que recibe una sección de pala (vista desde la punta, como
    `seccion_pala`): componente por el giro `u` = ω·r (hacia la derecha), por el avance `v`
    (hacia abajo) y su suma, que llega a `punto` (el borde de ataque). Devuelve un dict con
    las flechas 'giro', 'avance', 'relativo', el 'origen' y el ángulo 'phi' (radianes)."""
    p = np.array(punto, dtype=float)
    s = p + np.array([-u, v, 0.0]) * escala
    esq = s + np.array([u, 0.0, 0.0]) * escala
    return {"giro": vector(s, esq, c_giro, ancho=ancho * 0.7, punta=punta),
            "avance": vector(esq, p, c_avance, ancho=ancho * 0.7, punta=punta),
            "relativo": vector(s, p, c_rel, ancho=ancho, punta=punta),
            "origen": s, "phi": float(np.arctan2(v, u))}


def pala_torcida(centro, betas, cuerda=1.5, colores=None, codigo="4412", opacidad=1.0):
    """Varias secciones de una pala superpuestas tal como se ven desde la punta, todas con el
    mismo punto de referencia (25 % de la cuerda) en `centro` y girada cada una su ángulo de
    pala: muestra la torsión de un vistazo."""
    g = VGroup()
    c = np.array([centro[0], centro[1], 0.0])
    colores = colores or [TEXTO] * len(betas)
    for b, col in zip(betas, colores):
        ref = 0.25 * cuerda * np.array([np.cos(-b * DEGREES), np.sin(-b * DEGREES), 0])
        s = seccion_pala(c - ref, b, cuerda=cuerda, codigo=codigo, color_borde=col)
        s.set_fill(opacity=0.0).set_stroke(col, width=5, opacity=opacidad)
        g.add(s)
    return g


# ---------- Ala volante (sin cola) ----------
def ala_volante_superior():
    """Ala volante genérica vista desde arriba, morro hacia arriba (no reproduce ningún avión
    concreto). Devuelve (grupo, punta izq., punta der.): las puntas son el extremo del borde de
    salida de cada ala, donde van los frenos partidos (`freno_partido`)."""
    def semi(s):
        return [(0.0, 1.75), (s * 0.55, 1.35), (s * 3.75, -0.95), (s * 3.62, -1.3),
                (s * 2.3, -0.62), (s * 0.45, -0.3), (0.0, -0.55)]
    d = semi(1)
    pts = d + [(x * -1, y) for x, y in d[::-1]][1:-1]
    cuerpo = poli(pts, radio=0.08, fill=(FUS_A, "#CBD5E1"), sheen=DOWN)
    lomo = curva([(0, 1.45), (0.3, 1.0), (0.38, 0.1), (0.25, -0.45), (0, -0.55), (-0.25, -0.45),
                  (-0.38, 0.1), (-0.3, 1.0)], fill=("#E2E8F0", "#B9C4D6"), sheen=RIGHT)
    cabina = poli([(-0.2, 1.2), (0.2, 1.2), (0.12, 1.36), (-0.12, 1.36)], radio=0.03,
                  fill=(OSCURO, OSCURO))
    grupo = VGroup(cuerpo, lomo, cabina)
    return grupo, np.array([-3.66, -1.2, 0.0]), np.array([3.66, -1.2, 0.0])


def freno_partido(punta, s=1, color=C_GUINADA, apertura=1.0):
    """Freno partido de punta (vista desde arriba): dos placas que se abren hacia arriba y
    hacia abajo del ala; desde arriba se ve como una superficie que asoma por detrás del borde de
    salida. `apertura` 0–1. s=+1 punta derecha, −1 izquierda."""
    p = np.array(punta, dtype=float)
    largo = 0.75 * max(apertura, 0.02)
    a = p + np.array([-s * 0.85, 0.32, 0])
    b = p + np.array([-s * 0.05, 0.0, 0])
    atras = np.array([0, -largo * 0.55, 0])
    placa = Polygon(a, b, b + atras, a + atras * 0.7, fill_color=color, fill_opacity=0.9,
                    stroke_color=color, stroke_width=2)
    return placa


# ---------- Matrícula (short 09) ----------
def matricula_lateral(texto, x=-1.75, y=-0.2, alto=0.2, color=OSCURO):
    """Matrícula pintada en el fuselaje de `avion_lateral` (parte trasera, bajo las ventanas)."""
    t = Text(texto, font=F_TIT, weight=HEAVY, color=color)
    return t.scale_to_fit_height(alto).move_to([x, y, 0])


# ---------- Ala que se dobla (short 10) ----------
RAIZ_FRONTAL, PUNTA_FRONTAL = 0.45, 3.75     # semienvergadura en pantalla: 3,3 unidades


def avion_frontal_flexible(flex=0.0, diedro=0.18):
    """Avión visto de frente con las alas dobladas: la punta sube `flex` unidades respecto
    al ala recta (flecha de una viga en voladizo, ~ (x/b)²; negativo = cuelga en tierra).
    Devuelve (grupo, función y(x) del ala) para colocar flechas y cargas encima."""
    b = PUNTA_FRONTAL - RAIZ_FRONTAL

    def y_ala(x):
        u = np.clip((abs(x) - RAIZ_FRONTAL) / b, 0, 1)
        return -0.15 + diedro * u + flex * u ** 2

    def ala(s):
        xs = np.linspace(RAIZ_FRONTAL, PUNTA_FRONTAL, 24)
        esp = np.linspace(0.24, 0.09, 24)
        arriba = [(s * x, y_ala(x) + e / 2) for x, e in zip(xs, esp)]
        abajo = [(s * x, y_ala(x) - e / 2) for x, e in zip(xs[::-1], esp[::-1])]
        return poli(arriba + abajo, radio=0.03, fill=(FUS_A, "#CBD5E1"))

    def motor(s):
        x = 1.45
        c = np.array([s * x, y_ala(x) - 0.42, 0])
        anillo = Circle(radius=0.3).move_to(c)
        anillo.set_fill(color=["#E2E8F0", "#94A3B8"], opacity=1).set_sheen_direction(DOWN)
        anillo.set_stroke(BORDE, width=1.5)
        toma = Circle(radius=0.2, fill_color=OSCURO, fill_opacity=1, stroke_width=0).move_to(c)
        aspas = VGroup(*[Line(c, c + 0.19 * np.array([np.cos(a), np.sin(a), 0]),
                              color="#64748B", stroke_width=1.4)
                         for a in np.linspace(0, 2 * np.pi, 12, endpoint=False)])
        cono = Circle(radius=0.055, fill_color="#CBD5E1", fill_opacity=1,
                      stroke_width=0).move_to(c)
        pilon = Rectangle(width=0.12, height=0.2, fill_color="#94A3B8", fill_opacity=1,
                          stroke_width=0).move_to(c + UP * 0.32)
        return VGroup(pilon, anillo, toma, aspas, cono)

    estab = poli([(-1.6, 0.5), (1.6, 0.5), (1.6, 0.42), (-1.6, 0.38)], radio=0.03,
                 fill=("#CBD5E1", "#94A3B8"))
    aleta = poli([(-0.1, 0.55), (-0.05, 2.0), (0.05, 2.0), (0.1, 0.55)], radio=0.04,
                 fill=(FUS_A, "#CBD5E1"), sheen=RIGHT)
    fus = Circle(radius=0.6).set_fill(color=[FUS_A, FUS_B], opacity=1)
    fus.set_sheen_direction(DOWN).set_stroke(BORDE, width=1.5)
    cabina = VGroup(*[RoundedRectangle(width=0.2, height=0.12, corner_radius=0.04,
                                       fill_color=OSCURO, fill_opacity=1, stroke_width=0)
                      .move_to([s * 0.13, 0.22, 0]) for s in (-1, 1)])
    # visto de frente: el ala izquierda del avión queda a la derecha de la pantalla (roja)
    luces = VGroup(luz([PUNTA_FRONTAL, y_ala(PUNTA_FRONTAL), 0], LUZ_ROJA, 0.045),
                   luz([-PUNTA_FRONTAL, y_ala(PUNTA_FRONTAL), 0], LUZ_VERDE, 0.045))
    radomo = Circle(radius=0.2, fill_color="#E2E8F0", fill_opacity=0.6,
                    stroke_width=0).move_to([0, -0.08, 0])
    grupo = VGroup(estab, aleta, ala(-1), ala(1), motor(-1), motor(1), fus, radomo, cabina, luces)
    return grupo, y_ala


# ---------- Descargadores de estática (short 11) ----------
def descargador(base, direccion=DOWN, largo=0.32, color=C_GUINADA, ancho=4):
    """Varilla fina que sale del borde de salida, con la punta marcada."""
    d = np.array(direccion, dtype=float)
    d = d / np.linalg.norm(d)
    base = np.array(base, dtype=float)
    punta = base + d * largo
    return VGroup(Line(base, punta, color=color, stroke_width=ancho),
                  Dot(punta, radius=0.035, color=color))


def puntas_descargadores_superior():
    """Bases y direcciones de los descargadores sobre `avion_superior` (bordes de salida cerca
    de las puntas de ala y del estabilizador, y en el timón). Devuelve [(base, dirección)]."""
    res = []
    for s in (-1, 1):
        a, b = np.array([s * 3.45, -1.22, 0]), np.array([s * 0.35, -0.55, 0])   # borde de salida
        for f in (0.05, 0.16, 0.27):
            res.append((a + (b - a) * f, np.array([s * 0.25, -1, 0])))
        res.append((np.array([s * 3.78, -1.15, 0]), np.array([s * 0.8, -1, 0])))  # punta
        e1, e2 = np.array([s * 1.6, -3.25, 0]), np.array([s * 0.1, -3.05, 0])     # estabilizador
        for f in (0.08, 0.3):
            res.append((e1 + (e2 - e1) * f, np.array([s * 0.2, -1, 0])))
    res.append((np.array([0, -3.62, 0]), DOWN))                                    # timón
    return res


def carga(pos, signo="−", color=C_CABECEO, radio=0.13):
    """Carga eléctrica dibujada como círculo con signo."""
    c = Circle(radius=radio, stroke_color=color, stroke_width=3, fill_color=BG, fill_opacity=0.9)
    t = Text(signo, font=F_TIT, weight=HEAVY, color=color).scale_to_fit_height(radio * 0.9)
    return VGroup(c, t.move_to(c)).move_to(pos)


# ---------- Pseudo-3D: avión con caras proyectadas y sombreado plano ----------
def _norm(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-12 else v


def _rot(eje, ang):
    """Matriz de rotación (regla de la mano derecha) alrededor de 'x', 'y' o 'z'."""
    c, s = np.cos(ang), np.sin(ang)
    if eje == "x":
        return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    if eje == "y":
        return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


class Avion3D:
    """Avión de línea genérico en 3D (no reproduce ningún modelo) dibujado como caras
    planas proyectadas en perspectiva, con sombreado según la luz y orden del pintor.
    Ejes del avión: x hacia el morro, y hacia el ala izquierda, z hacia arriba.
    Ángulos en grados: alabeo > 0 = ala derecha abajo; cabeceo > 0 = morro arriba;
    guiñada > 0 = morro a la derecha. Deflexiones de mando (grados): `aleron` > 0 alabea a la
    derecha (alerón derecho arriba, izquierdo abajo), `elevador` > 0 sube el morro (borde de
    salida arriba), `timon` > 0 guiña a la derecha (borde de salida a la derecha).
    Uso: `always_redraw(lambda: avion.dibujar(alabeo=a.get_value(), ...))`."""

    LUZ = _norm(np.array([0.35, 0.45, 0.85]))

    def __init__(self, escala=1.0, colores=None):
        self.escala = escala
        self.col = {"fus": ("#5B6B84", "#F8FAFC"), "ala": ("#55657E", "#E2E8F0"),
                    "motor": ("#475569", "#CBD5E1"), "toma": ("#0F172A", "#1E293B"),
                    "aleron": ("#9F1239", C_ALABEO), "elevador": ("#075985", C_CABECEO),
                    "timon": ("#92400E", C_GUINADA), "cabina": ("#0F172A", "#334155")}
        if colores:
            self.col.update(colores)
        self._caras = []          # (puntos 3D, clave de color, cerrada, centro de la pieza)
        self._fuselaje()
        for s in (1, -1):
            self._ala(s)
            self._motor(s)

    # --- geometría (coordenadas del avión) ---
    def _cara(self, pts, color, cerrada=False, centro=None, bisagra=None):
        self._caras.append((np.array(pts, dtype=float), color, cerrada, centro, bisagra))

    def _fuselaje(self, n=16):
        xs = np.linspace(-3.6, 3.55, 26)

        def perfil(x):
            R = 0.42
            if x > 2.55:
                r = R * np.sqrt(max(0.0, 1 - ((x - 2.55) / 1.0) ** 2))
                return max(r, 0.02), 0.0
            if x < -1.7:
                u = (-1.7 - x) / 1.9
                return R * (1 - u) + 0.07 * u, 0.24 * u
            return R, 0.0
        anillos = []
        for x in xs:
            r, zc = perfil(x)
            anillos.append([(x, r * np.cos(a), zc + r * np.sin(a) * 0.95)
                            for a in np.linspace(0, 2 * np.pi, n, endpoint=False)])
        for i in range(len(xs) - 1):
            r0, zc0 = perfil(xs[i])
            centro = (xs[i], 0, zc0)
            for j in range(n):
                k = (j + 1) % n
                pts = [anillos[i][j], anillos[i][k], anillos[i + 1][k], anillos[i + 1][j]]
                color = "fus"
                if 2.75 < xs[i] < 3.1 and 1 <= j <= 3:
                    color = "cabina"
                if 2.75 < xs[i] < 3.1 and n - 4 <= j <= n - 2:
                    color = "cabina"
                self._cara(pts, color, True, centro)
        # deriva y timón
        self._superficie([(-2.55, 0, 0.36), (-3.45, 0, 0.36), (-3.62, 0, 1.75), (-3.3, 0, 1.75)],
                         "ala", corte=0.62, color_mando="timon", eje="vertical")
        # estabilizador horizontal y elevador
        for s in (1, -1):
            self._superficie([(-2.95, s * 0.12, 0.22), (-3.55, s * 0.12, 0.22),
                              (-3.78, s * 1.55, 0.3), (-3.45, s * 1.55, 0.3)],
                             "ala", corte=0.6, color_mando="elevador", eje="horizontal", lado=s)

    def _superficie(self, pts, color, corte=None, color_mando=None, eje="horizontal", lado=1,
                    esp=0.05):
        """Superficie fina (cara de arriba y de abajo). `pts`: borde de ataque raíz, borde de
        salida raíz, borde de salida punta, borde de ataque punta. Con `corte` (0–1 de la
        cuerda) la parte de atrás es una superficie de mando que gira sobre la bisagra."""
        le_r, te_r, te_p, le_p = [np.array(p, dtype=float) for p in pts]
        n = np.array([0, 0, 1.0]) if eje == "horizontal" else np.array([0, 1.0, 0])
        if corte is None:
            partes = [((le_r, te_r, te_p, le_p), color, None)]
        else:
            h_r = le_r + (te_r - le_r) * corte
            h_p = le_p + (te_p - le_p) * corte
            partes = [((le_r, h_r, h_p, le_p), color, None),
                      ((h_r, te_r, te_p, h_p), color_mando, (h_r, h_p, eje, lado))]
        tramos = 4      # tiras a lo largo de la envergadura: el orden del pintor falla menos
        for (a, b, c, d), col, bis in partes:
            for i in range(tramos):
                u0, u1 = i / tramos, (i + 1) / tramos
                q = [a + (d - a) * u0, b + (c - b) * u0, b + (c - b) * u1, a + (d - a) * u1]
                for sgn in (1, -1):
                    off = n * esp / 2 * sgn
                    self._cara([p + off for p in q], col, False, None, bis)

    def _ala(self, s):
        y0, y1 = 0.38, 3.85
        diedro = np.tan(np.radians(6))

        def z(y):
            return -0.18 + (y - y0) * diedro
        le_r, te_r = (0.95, s * y0, z(y0)), (-0.75, s * y0, z(y0))
        le_m, te_m = (-0.6, s * 2.3, z(2.3)), (-1.45, s * 2.3, z(2.3))
        le_p, te_p = (-1.45, s * y1, z(y1)), (-1.95, s * y1, z(y1))
        self._superficie([le_r, te_r, te_m, le_m], "ala", esp=0.09)
        self._superficie([le_m, te_m, te_p, le_p], "ala", corte=0.62, color_mando="aleron",
                         lado=s, esp=0.06)

    def _motor(self, s, n=12):
        y, z, r = s * 1.45, -0.62, 0.24
        x0, x1 = 0.55, 1.65
        anillo = [(np.cos(a), np.sin(a)) for a in np.linspace(0, 2 * np.pi, n, endpoint=False)]
        centro = (1.1, y, z)
        for j in range(n):
            k = (j + 1) % n
            p = [(x0, y + r * anillo[j][0], z + r * anillo[j][1]),
                 (x0, y + r * anillo[k][0], z + r * anillo[k][1]),
                 (x1, y + r * anillo[k][0], z + r * anillo[k][1]),
                 (x1, y + r * anillo[j][0], z + r * anillo[j][1])]
            self._cara(p, "motor", True, centro)
        self._cara([(x1, y + r * c, z + r * sn) for c, sn in anillo], "toma", True, centro)
        self._cara([(x0, y + r * 0.8 * c, z + r * 0.8 * sn) for c, sn in anillo], "motor", True,
                   centro)
        # pilón
        self._cara([(1.2, y, z + r), (0.6, y, z + r), (0.3, y, -0.2), (0.9, y, -0.2)], "ala")

    # --- proyección ---
    def dibujar(self, alabeo=0, cabeceo=0, guinada=0, aleron=0, elevador=0, timon=0,
                azimut=-35, elevacion=18, distancia=14, centro=ORIGIN, contorno=False):
        """VGroup con las caras visibles, ya proyectadas y ordenadas. `azimut`/`elevacion`
        (grados) dicen desde dónde se mira: azimut 0 = de frente al morro, −90 = desde la
        derecha del avión, 180 = desde atrás."""
        R = (_rot("z", np.radians(-guinada)) @ _rot("y", np.radians(-cabeceo))
             @ _rot("x", np.radians(alabeo)))
        az, el = np.radians(azimut), np.radians(elevacion)
        d = np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])
        f = -d
        der = _norm(np.cross(f, [0, 0, 1.0]))
        arr = np.cross(der, f)
        defl = {"aleron": aleron, "elevador": elevador, "timon": timon}
        caras = []
        for pts, col, cerrada, cpieza, bis in self._caras:
            P_ = pts.copy()
            if bis is not None:
                h0, h1, eje, lado = bis
                ang = np.radians(defl[col])
                u = _norm(h1 - h0)
                if col == "aleron":
                    ang, u = -ang * lado, u * lado   # derecho (lado −1) arriba con aleron > 0
                elif col == "elevador":
                    u = u * lado                     # los dos lados: borde de salida arriba
                # timón: con ángulo > 0 el borde de salida va a la derecha
                K = np.array([[0, -u[2], u[1]], [u[2], 0, -u[0]], [-u[1], u[0], 0]])
                Rb = np.eye(3) + np.sin(ang) * K + (1 - np.cos(ang)) * K @ K
                P_ = (P_ - h0) @ Rb.T + h0
            W = P_ @ R.T * self.escala
            n = _norm(np.cross(W[1] - W[0], W[2] - W[0]))
            cen = W.mean(axis=0)
            if cerrada and cpieza is not None:
                cp = (R @ np.array(cpieza)) * self.escala
                if np.dot(n, cen - cp) < 0:
                    n = -n
                if np.dot(n, d) <= 0:
                    continue                    # cara de espaldas
            elif np.dot(n, d) < 0:
                n = -n                          # superficie fina: se ve la cara de este lado
            luzv = 0.32 + 0.68 * max(0.0, float(np.dot(n, self.LUZ)))
            oscuro, claro = self.col[col]
            color = interpolate_color(ManimColor(oscuro), ManimColor(claro), min(1.0, luzv))
            prof = W @ d
            esc = distancia / (distancia - prof)
            pant = [np.array([w @ der * e, w @ arr * e, 0]) + centro for w, e in zip(W, esc)]
            caras.append((cen @ d, Polygon(*pant, fill_color=color, fill_opacity=1,
                                           stroke_color=color if not contorno else BORDE,
                                           stroke_width=0.8)))
        caras.sort(key=lambda t: t[0])
        return VGroup(*[p for _, p in caras])


# ---------- Clase base para cada short ----------
SFX = Path(__file__).resolve().parents[1] / "sfx"     # tools/sfx.py los genera


class ShortBase(MovingCameraScene):
    """Carga voz.json (junto al archivo de la escena), reproduce la narración completa,
    añade la rejilla de fondo y la capa de subtítulos sincronizados.
    voz.json: {"completo": "voz.mp3", "segmentos": {clave: {inicio, duracion}},
               "frases": [[inicio, fin, texto], ...]}  (rutas relativas a voz.json).

    Cámara: la ilustración vive en el «mundo» y la cámara puede acercarse (`enfocar`) y volver
    (`vista_general`). Los textos de pantalla (cabecera, títulos, pastillas, subtítulos) se
    registran con `hud(...)` y se quedan fijos en pantalla aunque la cámara se mueva.
    Regla: no mover la cámara mientras entra o sale un texto del HUD (durante una animación
    sus updaters se suspenden)."""
    VOZ_JSON = None          # la subclase define Path(__file__).parent / "voz.json"
    SIN_SUBS_DESDE = None    # clave de segmento a partir de la cual no hay subtítulos
    SUBS_DESDE = None        # clave de segmento antes de la cual no hay subtítulos (gancho)
    EFECTOS = True           # efectos de sonido automáticos (cambio, bloques, cámara)

    def setup(self):
        p = Path(self.VOZ_JSON) if self.VOZ_JSON else None
        self.VOZ = json.loads(p.read_text()) if p and p.exists() else {}
        if "completo" in self.VOZ:
            self.VOZ["completo"] = str((p.parent / self.VOZ["completo"]).resolve())

    def iniciar(self):
        V = self.VOZ
        if "completo" in V:
            self.add_sound(V["completo"])
        self.add(rejilla(6.6, 10.2))
        # velo oscuro arriba (HUD): los textos se leen aunque la cámara acerque la ilustración
        velo = VGroup(*[Rectangle(width=config.frame_width + 0.2, height=0.32, stroke_width=0,
                                  fill_color=BG, fill_opacity=a).move_to([0, y, 0])
                        for y, a in zip(np.arange(3.45, 8.2, 0.3),
                                        np.clip(np.linspace(0.12, 1.6, 16), 0, 0.78))])
        self.add(self.hud(velo))
        velo.set_z_index(15)
        if "frases" in V:
            seg = V.get("segmentos", {})
            fin = seg.get(self.SIN_SUBS_DESDE, {}).get("inicio", 1e9)
            ini = seg.get(self.SUBS_DESDE, {}).get("inicio", -1.0)
            items = subtitulos([f for f in V["frases"] if ini - 0.05 <= f[0] < fin - 0.05])
            capa = VGroup(*[m for _, _, m in items]).set_z_index(50)
            escena = self

            def actualizar(grupo):
                # reloj de la escena (no sumar dt: cada play pierde un fotograma y se desfasa)
                t = escena.renderer.time
                for (a, b, m) in items:
                    m.set_opacity(1.0 if a <= t < b else 0.0)

            capa.add_updater(actualizar)
            actualizar(capa)   # sin esto, el primer fotograma (la portada) muestra todos
            self.hud(capa)
            self.add(capa)

    # ---------- Cámara y HUD ----------
    def _mapa(self):
        f = self.camera.frame
        return f.get_center().copy(), f.width / config.frame_width

    def hud(self, *mobs):
        """Fija objetos a la pantalla (coordenadas de pantalla por defecto, aunque la cámara
        esté acercada o desplazada). Devuelve el primero."""
        escena = self

        def seguir(m):
            c2, s2 = escena._mapa()
            c, s = m._mapa_hud
            if abs(s2 - s) < 1e-9 and np.allclose(c, c2):
                return
            m.shift(-c).scale(s2 / s, about_point=ORIGIN).shift(c2)
            m._mapa_hud = (c2, s2)

        for m in mobs:
            if getattr(m, "_mapa_hud", None) is not None:
                continue
            c, s = self._mapa()
            m.scale(s, about_point=ORIGIN).shift(c)
            m._mapa_hud = (c, s)
            if m.z_index < 16:          # por encima del velo y de la ilustración
                m.set_z_index(16)
            m.add_updater(seguir)
        return mobs[0] if mobs else None

    def enfocar(self, punto, zoom=2.0, run_time=1.0, sonido=True, *extra):
        """Acerca la cámara a `punto` (coordenadas del mundo). zoom 2 = todo el doble de grande."""
        if sonido:
            self.sonido("whoosh_suave", -10)
        f = self.camera.frame
        self.play(f.animate.move_to(punto).set(width=config.frame_width / zoom), *extra,
                  run_time=run_time, rate_func=rate_functions.ease_in_out_cubic)

    def vista_general(self, run_time=0.9, sonido=True, *extra):
        self.enfocar(ORIGIN, 1.0, run_time, sonido, *extra)

    # ---------- Efectos de sonido ----------
    def sonido(self, nombre, ganancia=-6, retraso=0.0):
        """Efecto de `sfx/` en el instante actual (+ retraso). Ganancia en dB."""
        p = SFX / f"{nombre}.wav"
        if self.EFECTOS and p.exists():
            self.add_sound(str(p), time_offset=retraso, gain=ganancia)

    # ---------- Bloque compacto (menos texto: título + una frase) ----------
    def bloque(self, idx, titulo, frase, color, dato=None, resaltar=()):
        """Título y UNA frase que entra palabra a palabra (`entrar_bloque`); dato opcional.
        Todo va al HUD. Devuelve (barra, título, frase, dato o None)."""
        tit = T(titulo, size=100, color=color, weight=HEAVY, font=F_TIT).move_to(UP * 5.35)
        fr = frase_cinetica(frase, size=44, weight=BOLD, font=F_TXT, resaltar=resaltar, ancho=7.6,
                            color_resalte=color)
        fr.next_to(tit, DOWN, buff=0.3)
        dt = None
        if dato:
            dt = T(dato, size=27, color=TEXTO_SEC, weight=MEDIUM).next_to(fr, DOWN, buff=0.2)
            self.hud(dt)
        self.hud(tit, fr)
        return self.barras[idx], tit, fr, dt

    def entrar_palabras(self, frase, run_time=None, lag=0.11):
        ps = palabras(frase)
        run_time = run_time or max(0.5, 0.25 + lag * len(ps))
        # la frase entera tiene que estar en la escena: si solo entran las palabras, el
        # updater del HUD (que vive en la frase) no se ejecuta y se quedan atrás al mover la cámara
        self.add(frase)
        self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.18, scale=1.12) for p in ps],
                              lag_ratio=lag * len(ps) / run_time if run_time else 0.1),
                  run_time=run_time, rate_func=linear)

    def entrar_bloque(self, barra, color, tit, fr, dt=None, *extra):
        self.sonido("pop", -8)
        self.play(barra.animate.set_fill(color),
                  FadeIn(tit, shift=DOWN * 0.3, scale=1.2, rate_func=rate_functions.ease_out_back),
                  *extra, run_time=0.5)
        self.entrar_palabras(fr)
        if dt is not None:
            self.play(FadeIn(dt), run_time=0.3)

    def sello(self, texto, color, pos, size=48, angulo=4):
        """Sello con marco (golpe de sonido incluido en `poner_sello`). Va al HUD."""
        txt = T(texto, size=size, color=color, weight=HEAVY, font=F_TIT)
        marco = RoundedRectangle(width=txt.width + 0.6, height=txt.height + 0.5,
                                 corner_radius=0.2, stroke_color=color, stroke_width=8,
                                 fill_color=BG, fill_opacity=0.9)
        s = VGroup(marco, txt.move_to(marco)).rotate(angulo * DEGREES).move_to(pos)
        return self.hud(s.set_z_index(40))

    def poner_sello(self, sello):
        self.sonido("golpe", -4)
        self.play(FadeIn(sello, scale=1.5), rate_func=rate_functions.ease_out_back,
                  run_time=0.35)

    def portada(self, *mobs):
        """Pone el gancho en pantalla desde el primer fotograma, sin fundido: Instagram y
        TikTok usan ese fotograma como miniatura del perfil. Actualiza antes los
        `always_redraw` para que no salgan con su estado inicial."""
        for m in mobs:
            m.update()
        self.add(*mobs)

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

    # ---------- Plantilla de bloque (común a los shorts 02–07) ----------
    # Uso típico de un bloque, sin pantalla vacía entre bloques:
    #     t0, d = self.voz("clave")
    #     barra, tit, fr, dt, etq, ctl = self.textos_bloque(0, "Título", "Frase", "dato",
    #                                                       "SE CONTROLA CON", "ELEVADOR", color)
    #     self.cambio(FadeIn(ilustracion))          # sale lo del bloque anterior a la vez
    #     self.entrar_textos(barra, color, tit, fr, dt)
    #     ...
    #     self.rellenar(t0, d, margen=-0.05)
    #     self.dejar(tit, fr, dt, etq, ctl, ilustracion)   # saldrán al entrar el siguiente
    def poner_cabecera(self, tema, n_bloques=3):
        """Tema arriba y barras de progreso (una por bloque). Devuelve la animación de entrada."""
        self.tema = T(tema, size=28, color=TEXTO_SEC, weight=SEMIBOLD).move_to(UP * 6.85)
        self.barras = VGroup(*[RoundedRectangle(width=0.7, height=0.12, corner_radius=0.06,
                                                fill_color="#334155", fill_opacity=1,
                                                stroke_width=0) for _ in range(n_bloques)])
        self.barras.arrange(RIGHT, buff=0.15).move_to(UP * 6.4)
        self.hud(self.tema, self.barras)
        return AnimationGroup(FadeIn(self.tema, shift=DOWN * 0.2), FadeIn(self.barras))

    def textos_bloque(self, idx, nombre, frase, dato, etiqueta, clave, color):
        """Título grande, frase intuitiva, dato técnico y pastilla «etiqueta / clave»."""
        tit = T(nombre, size=116, color=color, weight=HEAVY, font=F_TIT).move_to(UP * 5.3)
        if tit.width > ANCHO_MAX:
            tit.scale_to_fit_width(ANCHO_MAX)
        fr = T(frase, size=48, weight=BOLD).next_to(tit, DOWN, buff=0.28)
        dt = T(dato, size=28, color=TEXTO_SEC, weight=MEDIUM).next_to(fr, DOWN, buff=0.16)
        etq = T(etiqueta, size=28, color=TEXTO_SEC, weight=SEMIBOLD).move_to(DOWN * 3.6)
        ctl = pastilla(T(clave, size=52, color=color, weight=HEAVY, font=F_TIT), color)
        ctl.next_to(etq, DOWN, buff=0.2)
        self.hud(tit, fr, dt, etq, ctl)
        return self.barras[idx], tit, fr, dt, etq, ctl

    def entrar_textos(self, barra, color, tit, fr, dt, *extra):
        self.play(barra.animate.set_fill(color), FadeIn(tit, shift=DOWN * 0.3, scale=1.15),
                  *extra, run_time=0.6)
        self.play(FadeIn(fr, shift=UP * 0.2), FadeIn(dt), run_time=0.45)

    def etiqueta(self, texto, color, pos, size=26):
        """Rótulo con fondo semitransparente, legible sobre la ilustración."""
        t = T(texto, size=size, color=color, weight=BOLD)
        fondo = RoundedRectangle(width=t.width + 0.36, height=t.height + 0.24, corner_radius=0.14,
                                 fill_color=BG, fill_opacity=0.85, stroke_width=0)
        return VGroup(fondo, t).move_to(pos).set_z_index(30)

    def salir(self, *mobs, run_time=0.4, **kw):
        """Salida inmediata (deja la pantalla vacía si no entra nada: preferir dejar/cambio)."""
        self.play(*[FadeOut(m, shift=LEFT * 0.6) for m in mobs], run_time=run_time, **kw)

    # ---------- Transiciones sin pantalla vacía ----------
    def dejar(self, *mobs):
        """Marca objetos para que salgan en el próximo `cambio`, a la vez que entra lo nuevo.
        Así nunca hay un fotograma con solo el fondo (tools/revisar.py lo comprueba)."""
        if not hasattr(self, "_pendientes"):
            self._pendientes = []
        self._pendientes += [m for m in mobs if m is not None]

    def cambio(self, *entradas, run_time=0.5, desplazar=LEFT * 0.8):
        """Fundido cruzado: sale lo marcado con `dejar` y entran `entradas` en el mismo play.
        Los objetos con updaters se congelan antes de salir (ver nota de FadeIn en CLAUDE.md)."""
        salen = getattr(self, "_pendientes", [])
        for m in salen:
            m.clear_updaters()
        anims = [FadeOut(m, shift=desplazar) for m in salen] + list(entradas)
        self._pendientes = []
        if anims:
            if salen:
                self.sonido("whoosh", -9)
            self.play(*anims, run_time=run_time)

    def pulso(self, mob, escala=1.1, run_time=0.5):
        """Micro-cambio para tramos largos sin movimiento (≤ 3 s sin cambios)."""
        self.play(mob.animate.scale(escala), rate_func=there_and_back, run_time=run_time)

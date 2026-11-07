"""
Avión de línea genérico de "Por Qué Vuela": UNA geometría paramétrica (en metros) de la que
salen la malla 3D (render real con iluminación, `Avion3DReal`) y las vistas 2D vectoriales
(`lateral_2d`, `superior_2d`, `frontal_2d`). No reproduce ningún modelo concreto: proporciones
de un bimotor de pasillo único (unos 37,6 m de largo y 34 m de envergadura).

Ejes de construcción (metros): X desde la punta del morro hacia la cola, Y hacia el ala
izquierda, Z hacia arriba. Ejes del avión para los giros (como `Avion3D`): x hacia el morro,
y hacia el ala izquierda, z arriba, con origen en el centro de gravedad (X = X_CG).
"""
import os
from functools import lru_cache

import numpy as np

# ---------------------------------------------------------------- geometría (metros)
L = 37.6            # largo del fuselaje
R_Y, R_Z = 1.98, 2.05
L_MORRO = 5.8       # longitud del morro
X_COLA = 26.5       # empieza el cono de cola
X_CG = 16.8

ALA = dict(y_raiz=1.9, y_punta=17.0, x_ba_raiz=13.6, cuerda_raiz=6.6, cuerda_punta=1.55,
           flecha=27.0, diedro=5.5, z_raiz=-1.15, torsion_raiz=2.5, torsion_punta=-0.5,
           t_raiz=0.135, t_punta=0.105, aleron=(11.8, 15.9), corte_aleron=0.74)
ESTAB = dict(y_raiz=0.4, y_punta=6.2, x_ba_raiz=31.2, cuerda_raiz=3.7, cuerda_punta=1.4,
             flecha=30.0, diedro=6.0, z_raiz=0.55, t=0.10, mando=(0.9, 6.0), corte=0.70)
DERIVA = dict(z_raiz=1.75, z_punta=7.9, x_ba_raiz=28.6, cuerda_raiz=5.4, cuerda_punta=1.9,
              flecha=38.0, t=0.10, mando=(2.2, 7.5), corte=0.68)
MOTOR = dict(y=5.75, largo=4.4, radio=1.06, adelanto=2.5, hueco=0.32)
WINGLET = dict(alto=2.0, cant=12.0, cuerda_raiz=1.5, cuerda_punta=0.62, flecha=38.0)

# colores (sRGB)
BLANCO = "#F1F5F9"
GRIS_PANZA = "#B8C2D0"
GRIS_ALA = "#D3DAE3"
GRIS_MOTOR = "#C7D0DB"
OSCURO_VIDRIO = "#152238"
OSCURO = "#1E293B"
AZUL = "#38BDF8"
ROSA = "#FB7185"
AMARILLO = "#FBBF24"
ROJA, VERDE = "#F43F5E", "#22C55E"


def hex_rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)])


# ---------------------------------------------------------------- fuselaje
def seccion(X):
    """(semieje Y, semieje Z, centro Z) de la sección del fuselaje en la estación X."""
    X = float(np.clip(X, 0.0, L))
    if X < L_MORRO:
        u = X / L_MORRO
        f = (1 - (1 - u) ** 2.3) ** (1 / 2.3)
        return R_Y * f, R_Z * f, -0.55 * (1 - u) ** 2
    if X > X_COLA:
        u = (X - X_COLA) / (L - X_COLA)
        arriba = R_Z - (R_Z - 1.35) * u ** 2.2
        abajo = -R_Z + (R_Z + 0.68) * u ** 1.45
        ry = 0.33 + (R_Y - 0.33) * (1 - u ** 1.8) ** 0.85
        return ry, (arriba - abajo) / 2, (arriba + abajo) / 2
    return R_Y, R_Z, 0.0


def punto_fuselaje(X, th, offset=0.0):
    """Punto de la piel en la estación X y el ángulo th (rad; 0 = lado izquierdo,
    π/2 = arriba). `offset` lo separa hacia fuera (para ventanillas y pintura)."""
    ry, rz, zc = seccion(X)
    p = np.array([X, ry * np.cos(th), zc + rz * np.sin(th)])
    if offset:
        n = np.array([0.0, np.cos(th) / max(ry, 1e-3), np.sin(th) / max(rz, 1e-3)])
        p = p + offset * n / np.linalg.norm(n)
    return p


def estaciones_fuselaje(n=140):
    u = np.linspace(0, 1, n)
    # más estaciones en el morro y en la cola
    return L * (0.5 - 0.5 * np.cos(np.pi * u)) * 0.35 + L * u * 0.65


# zonas pintadas (X0, X1, th0, th1 en grados; lado izquierdo; el derecho es el espejo)
# parabrisas: cuatro esquinas por panel (lado izquierdo; el derecho es el espejo), en orden
# abajo-delante, abajo-detrás, arriba-detrás, arriba-delante. Cada esquina es ("z", X, Z)
# (altura en la piel del lado) o ("t", X, ángulo en grados; 86 = junto al poste central).
# Los bordes comparten los postes: banda baja y estrecha, como en un avión de línea.
PARABRISAS = [
    [("t", 0.80, 86.0), ("z", 3.25, 0.48), ("z", 3.66, 1.25), ("t", 1.85, 86.0)],   # frontal
    [("z", 3.42, 0.50), ("z", 4.22, 0.52), ("z", 4.18, 1.18), ("z", 3.82, 1.22)],   # lateral 1
    [("z", 4.34, 0.52), ("z", 4.95, 0.55), ("z", 4.78, 1.08), ("z", 4.30, 1.17)],   # lateral 2
]


def _esquina(c):
    """(X, ángulo en grados) de una esquina de parabrisas."""
    tipo, X, v = c
    if tipo == "t":
        return X, v
    ry, rz, zc = seccion(X)
    return X, float(np.degrees(np.arcsin(np.clip((v - zc) / rz, -1, 1))))


def _bilineal(esq, a, b):
    (x0, t0), (x1, t1), (x2, t2), (x3, t3) = esq
    x = (1 - a) * (1 - b) * x0 + a * (1 - b) * x1 + a * b * x2 + (1 - a) * b * x3
    t = (1 - a) * (1 - b) * t0 + a * (1 - b) * t1 + a * b * t2 + (1 - a) * b * t3
    return x, t


def parche_cuad(esquinas, color, offset=0.03, n=12, mat="vidrio", espejo=False):
    """Parche de cuatro esquinas (X, grados) que sigue la piel."""
    esq = [_esquina(c) for c in esquinas]
    v, f = [], []
    for i in range(n):
        for j in range(n):
            X, t = _bilineal(esq, i / (n - 1), j / (n - 1))
            th = np.radians(t)
            v.append(punto_fuselaje(X, np.pi - th if espejo else th, offset))
    for i in range(n - 1):
        for j in range(n - 1):
            a, b, c, d = i * n + j, i * n + j + 1, (i + 1) * n + j + 1, (i + 1) * n + j
            f += [[a, b, c], [a, c, d]]
    m = Malla(v, f, color, mat)
    m.orient = "piel"
    return m


def contorno_parabrisas(esquinas, espejo=False, n=10, offset=0.03):
    """Puntos 3D del borde de un panel (para las vistas 2D)."""
    esq = [_esquina(c) for c in esquinas]
    pts = []
    for (a0, b0), (a1, b1) in (((0, 0), (1, 0)), ((1, 0), (1, 1)), ((1, 1), (0, 1)),
                               ((0, 1), (0, 0))):
        for u in np.linspace(0, 1, n, endpoint=False):
            X, t = _bilineal(esq, a0 + (a1 - a0) * u, b0 + (b1 - b0) * u)
            th = np.radians(t)
            pts.append(punto_fuselaje(X, np.pi - th if espejo else th, offset))
    return np.array(pts)


def ventanillas_X():
    xs = np.arange(7.6, 26.2, 0.53)
    puertas = [(6.0, 7.2), (13.9, 14.6), (15.5, 16.2), (24.7, 25.9)]
    return [x for x in xs if not any(a - 0.15 < x < b + 0.15 for a, b in puertas)]


PUERTAS = [(6.15, 6.98, -26, 29), (13.95, 14.55, -14, 22), (15.55, 16.15, -14, 22),
           (24.85, 25.7, -26, 29)]
TH_VENTANILLA = 21.0


# ---------------------------------------------------------------- perfiles
def naca(m, p, t, n=34):
    """Perfil NACA de 4 cifras (x/c de 0 a 1). Devuelve (extradós, intradós) desde el borde de
    ataque al de salida, cada uno (n, 2)."""
    b = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, n))
    yt = 5 * t * (0.2969 * np.sqrt(b) - 0.126 * b - 0.3516 * b ** 2 + 0.2843 * b ** 3
                  - 0.1036 * b ** 4)
    if m > 0:
        yc = np.where(b < p, m / p ** 2 * (2 * p * b - b ** 2),
                      m / (1 - p) ** 2 * ((1 - 2 * p) + 2 * p * b - b ** 2))
        dy = np.where(b < p, 2 * m / p ** 2 * (p - b), 2 * m / (1 - p) ** 2 * (p - b))
    else:
        yc, dy = np.zeros_like(b), np.zeros_like(b)
    th = np.arctan(dy)
    sup = np.column_stack([b - yt * np.sin(th), yc + yt * np.cos(th)])
    inf = np.column_stack([b + yt * np.sin(th), yc - yt * np.cos(th)])
    return sup, inf


def contorno_perfil(m, p, t, x0=0.0, x1=1.0, n=34):
    """Contorno cerrado (sentido: extradós BA→BS, intradós BS→BA) recortado a x/c ∈ [x0, x1]."""
    sup, inf = naca(m, p, t, n)
    def recorte(c):
        xs = np.linspace(x0, x1, max(6, int(n * (x1 - x0)) + 2))
        return np.column_stack([xs, np.interp(xs, c[:, 0], c[:, 1])])
    s, i = recorte(sup), recorte(inf)
    return np.vstack([s, i[::-1][1:-1]])


# ---------------------------------------------------------------- mallas (numpy)
class Malla:
    def __init__(self, v, f, color, mat="pintura", nombre=""):
        self.v, self.f = np.asarray(v, float), np.asarray(f, int)
        self.color, self.mat, self.nombre = color, mat, nombre
        self.bisagra = None          # (p0, p1) en coordenadas de construcción

    def unir(self, otra):
        self.f = np.vstack([self.f, otra.f + len(self.v)])
        self.v = np.vstack([self.v, otra.v])
        return self


def loft(secciones, cerrar_ext=True):
    """Superficie que une secciones (cada una (n, 3), mismo n, contorno cerrado)."""
    S = np.asarray(secciones)
    k, n, _ = S.shape
    v = S.reshape(-1, 3)
    f = []
    for i in range(k - 1):
        for j in range(n):
            a, b = i * n + j, i * n + (j + 1) % n
            c, d = (i + 1) * n + (j + 1) % n, (i + 1) * n + j
            f += [[a, b, c], [a, c, d]]
    if cerrar_ext:
        for idx, inv in ((0, True), (k - 1, False)):
            cen = S[idx].mean(axis=0)
            ci = len(v)
            v = np.vstack([v, cen])
            for j in range(n):
                a, b = idx * n + j, idx * n + (j + 1) % n
                f.append([ci, b, a] if inv else [ci, a, b])
    return np.asarray(v), np.asarray(f)


def malla_fuselaje():
    n = 64
    ths = np.linspace(0, 2 * np.pi, n, endpoint=False)
    secs = [[punto_fuselaje(X, th) for th in ths] for X in estaciones_fuselaje()]
    secs[0] = [punto_fuselaje(1e-3, th) for th in ths]
    v, f = loft(secs)
    return Malla(v, f, BLANCO, "pintura", "fuselaje")


def colores_fuselaje(v):
    """Color por vértice: panza gris y línea azul bajo las ventanillas."""
    col = np.tile(hex_rgb(BLANCO), (len(v), 1))
    for i, (X, Y, Z) in enumerate(v):
        ry, rz, zc = seccion(X)
        s = (Z - zc) / max(rz, 1e-3)
        if s < -0.62:
            col[i] = hex_rgb(GRIS_PANZA)
    return col


def parche(X0, X1, th0, th1, color, offset=0.025, n=7, mat="vidrio", espejo=False,
           sesgo=0.0, X0b=None, X1b=None, nx=None):
    """Parche que sigue la piel (ventanillas, puertas). Ángulos en grados. `sesgo` inclina
    los bordes delanteros/traseros (parabrisas)."""
    v, f = [], []
    nx = nx or n
    X0b = X0 if X0b is None else X0b         # bordes a th1 (trapecio)
    X1b = X1 if X1b is None else X1b
    for i in range(nx):
        for j in range(n):
            a, b = i / (nx - 1), j / (n - 1)
            xa = X0 + (X0b - X0) * b
            xb = X1 + (X1b - X1) * b
            X = xa + (xb - xa) * a + sesgo * (b - 0.5)
            th = np.radians(th0 + (th1 - th0) * b)
            if espejo:
                th = np.pi - th
            v.append(punto_fuselaje(X, th, offset))
    for i in range(nx - 1):
        for j in range(n - 1):
            a, b, c, d = i * n + j, i * n + j + 1, (i + 1) * n + j + 1, (i + 1) * n + j
            f += [[a, b, c], [a, c, d]] if not espejo else [[a, c, b], [a, d, c]]
    m = Malla(v, f, color, mat)
    m.orient = "piel"
    return m


def malla_superficie(sec_fn, ys, m, p, t_fn, corte=None, parte="todo"):
    """Ala/estabilizador/deriva por tramos. `sec_fn(y, contorno2d)` coloca el perfil (x/c, z/c)
    en 3D. `parte`: 'todo', 'fijo' (hasta el corte) o 'mando' (desde el corte)."""
    secs = []
    for y in ys:
        t = t_fn(y)
        if parte == "todo":
            c2 = contorno_perfil(m, p, t, 0, 1, 40)
        elif parte == "fijo":
            c2 = contorno_perfil(m, p, t, 0, corte, 40)
        else:
            c2 = contorno_perfil(m, p, t, corte, 1, 40)
        secs.append(sec_fn(y, c2))
    n = min(len(s) for s in secs)
    secs = [s[:n] for s in secs]
    return loft(secs)


def _ala_en(y, c2, a=ALA):
    s = 1 if y >= 0 else -1
    yy = abs(y)
    u = (yy - a["y_raiz"]) / (a["y_punta"] - a["y_raiz"])
    cuerda = a["cuerda_raiz"] + (a["cuerda_punta"] - a["cuerda_raiz"]) * u
    xba = a["x_ba_raiz"] + (yy - a["y_raiz"]) * np.tan(np.radians(a["flecha"]))
    z0 = a["z_raiz"] + (yy - a["y_raiz"]) * np.tan(np.radians(a["diedro"]))
    tw = np.radians(a["torsion_raiz"] + (a["torsion_punta"] - a["torsion_raiz"]) * u)
    xc, zc = c2[:, 0] - 0.25, c2[:, 1]
    xr = xc * np.cos(tw) + zc * np.sin(tw)       # incidencia > 0: borde de ataque arriba
    zr = -xc * np.sin(tw) + zc * np.cos(tw)
    return np.column_stack([xba + (xr + 0.25) * cuerda, np.full(len(xr), s * yy),
                            z0 + zr * cuerda])


def geometria_ala_en(yy, xc=0.25, a=ALA):
    """(X, Z) de la línea media del ala a la distancia yy y la fracción de cuerda xc."""
    u = (yy - a["y_raiz"]) / (a["y_punta"] - a["y_raiz"])
    cuerda = a["cuerda_raiz"] + (a["cuerda_punta"] - a["cuerda_raiz"]) * u
    xba = a["x_ba_raiz"] + (yy - a["y_raiz"]) * np.tan(np.radians(a["flecha"]))
    z0 = a["z_raiz"] + (yy - a["y_raiz"]) * np.tan(np.radians(a["diedro"]))
    return xba + xc * cuerda, z0, cuerda


C_SLAT = 0.13                       # cuerda del slat (fracción)
SLAT_Y = (2.8, 16.6)                # tramo con slats
FLAP_Y = (1.9, 11.8)                # flaps: de la raíz hasta el alerón
SPOILERS = [(4.2, 5.6), (6.0, 7.4), (7.6, 9.0), (9.2, 10.4), (10.6, 11.6)]
SPOILER_C = (0.58, 0.73)


def _tramo_ala(s, ys, x0, x1, t_fn, n=40):
    secs = [_ala_en(s * y, contorno_perfil(0.02, 0.4, t_fn(y), x0, x1, n)) for y in ys]
    k = min(len(c) for c in secs)
    return loft([c[:k] for c in secs])


def _ys(y0, y1, paso=0.6):
    return np.linspace(y0, y1, max(3, int(np.ceil((y1 - y0) / paso)) + 1))


def mallas_ala(s):
    """Ala con alerón, flap (Fowler), slat y spoilers como piezas móviles (`imagen(flap=,
    slat=, spoiler=)`). En reposo forman el mismo perfil que el ala entera."""
    a = ALA
    t_fn = lambda y: a["t_raiz"] + (a["t_punta"] - a["t_raiz"]) * (abs(y) - a["y_raiz"]) / (  # noqa
        a["y_punta"] - a["y_raiz"])
    y0, y1 = a["aleron"]
    cc = a["corte_aleron"]
    res = []
    # cajón fijo del ala (por tramos de cuerda)
    for (ya, yb, xa, xb) in ((a["y_raiz"], SLAT_Y[0], 0.0, cc), (SLAT_Y[0], y1, C_SLAT, cc),
                             (y1, SLAT_Y[1], C_SLAT, 1.0), (SLAT_Y[1], a["y_punta"], 0.0, 1.0)):
        v, f = _tramo_ala(s, _ys(ya, yb), xa, xb, t_fn)
        res.append(Malla(v, f, GRIS_ALA, "pintura", "ala"))
    # slat (borde de ataque móvil)
    v, f = _tramo_ala(s, _ys(*SLAT_Y), 0.0, C_SLAT, t_fn, 60)
    sl = Malla(v, f, GRIS_ALA, "pintura", "slat")
    sl.bisagra = (_ala_en(s * SLAT_Y[0], np.array([[C_SLAT, 0.0]]))[0],
                  _ala_en(s * SLAT_Y[1], np.array([[C_SLAT, 0.0]]))[0])
    sl.lado = s
    res.append(sl)
    # flap (borde de salida interior)
    v, f = _tramo_ala(s, _ys(*FLAP_Y), cc, 1.0, t_fn)
    fl = Malla(v, f, GRIS_ALA, "pintura", "flap")
    fl.bisagra = (_ala_en(s * FLAP_Y[0], np.array([[cc, 0.0]]))[0],
                  _ala_en(s * FLAP_Y[1], np.array([[cc, 0.0]]))[0])
    fl.lado = s
    res.append(fl)
    # alerón
    v, f = _tramo_ala(s, _ys(y0 + 0.03, y1 - 0.03), cc, 1.0, t_fn)
    ale = Malla(v, f, GRIS_ALA, "pintura", "aleron")
    ale.bisagra = (_ala_en(s * y0, np.array([[cc, 0.0]]))[0],
                   _ala_en(s * y1, np.array([[cc, 0.0]]))[0])
    ale.lado = s
    res.append(ale)
    # spoilers: placas finas sobre el extradós, con la bisagra delante
    for (ya, yb) in SPOILERS:
        secs = []
        for y in np.linspace(ya, yb, 4):
            t = t_fn(y)
            sup, _ = naca(0.02, 0.4, t, 30)
            xs = np.linspace(SPOILER_C[0], SPOILER_C[1], 8)
            zs = np.interp(xs, sup[:, 0], sup[:, 1])
            c2 = np.vstack([np.column_stack([xs, zs + 0.004]),
                            np.column_stack([xs[::-1], zs[::-1] - 0.006])])
            secs.append(_ala_en(s * y, c2))
        v, f = loft(secs)
        sp = Malla(v, f, "#C3CBD6", "pintura", "spoiler")
        sup0 = lambda y: naca(0.02, 0.4, t_fn(y), 30)[0]
        zA = np.interp(SPOILER_C[0], sup0(ya)[:, 0], sup0(ya)[:, 1])
        zB = np.interp(SPOILER_C[0], sup0(yb)[:, 0], sup0(yb)[:, 1])
        sp.bisagra = (_ala_en(s * ya, np.array([[SPOILER_C[0], zA]]))[0],
                      _ala_en(s * yb, np.array([[SPOILER_C[0], zB]]))[0])
        sp.lado = s
        res.append(sp)
    # winglet: perfil simétrico, sube desde la punta con un poco de cant hacia fuera
    w = WINGLET
    Xt, Zt, ct = geometria_ala_en(a["y_punta"], 0.0)
    secs = []
    for u in np.linspace(0, 1, 7):
        cu = ct * (1 - u) + w["cuerda_punta"] * u if u > 0 else ct
        cu = w["cuerda_raiz"] + (w["cuerda_punta"] - w["cuerda_raiz"]) * u if u > 0.15 else \
            ct + (w["cuerda_raiz"] - ct) * u / 0.15
        z = Zt + w["alto"] * u
        yy = a["y_punta"] + w["alto"] * u * np.tan(np.radians(w["cant"]))
        xba = Xt + w["alto"] * u * np.tan(np.radians(w["flecha"])) + (ct - cu) * 0.6 * min(1, u / 0.15)
        c2 = contorno_perfil(0, 0.4, 0.09, 0, 1, 30)
        secs.append(np.column_stack([xba + c2[:, 0] * cu, s * (yy + c2[:, 1] * cu), np.full(len(c2), z)]))
    v, f = loft(secs)
    res.append(Malla(v, f, AZUL if False else GRIS_ALA, "pintura", "winglet"))
    return res


def mallas_estabilizador(s):
    a = ESTAB

    def en(y, c2):
        yy = abs(y)
        u = (yy - a["y_raiz"]) / (a["y_punta"] - a["y_raiz"])
        cu = a["cuerda_raiz"] + (a["cuerda_punta"] - a["cuerda_raiz"]) * u
        xba = a["x_ba_raiz"] + (yy - a["y_raiz"]) * np.tan(np.radians(a["flecha"]))
        z0 = a["z_raiz"] + (yy - a["y_raiz"]) * np.tan(np.radians(a["diedro"]))
        return np.column_stack([xba + c2[:, 0] * cu, np.full(len(c2), s * yy), z0 + c2[:, 1] * cu])
    t_fn = lambda y: a["t"]  # noqa: E731
    y0, y1 = a["mando"]
    res = []
    for ys, parte in [(np.linspace(a["y_raiz"], y0, 3), "todo"), (np.linspace(y0, y1, 8), "fijo"),
                      (np.linspace(y1, a["y_punta"], 3), "todo")]:
        v, f = malla_superficie(en, s * ys, 0, 0.4, t_fn, a["corte"], parte)
        res.append(Malla(v, f, BLANCO, "pintura", "estabilizador"))
    v, f = malla_superficie(en, s * np.linspace(y0 + 0.03, y1 - 0.03, 8), 0, 0.4, t_fn,
                            a["corte"], "mando")
    el = Malla(v, f, BLANCO, "pintura", "elevador")
    el.bisagra = (en(s * y0, np.array([[a["corte"], 0.0]]))[0], en(s * y1, np.array([[a["corte"], 0.0]]))[0])
    el.lado = s
    res.append(el)
    return res


def mallas_deriva():
    a = DERIVA

    def en(z, c2):
        u = (z - a["z_raiz"]) / (a["z_punta"] - a["z_raiz"])
        cu = a["cuerda_raiz"] + (a["cuerda_punta"] - a["cuerda_raiz"]) * u
        xba = a["x_ba_raiz"] + (z - a["z_raiz"]) * np.tan(np.radians(a["flecha"]))
        return np.column_stack([xba + c2[:, 0] * cu, c2[:, 1] * cu, np.full(len(c2), z)])
    t_fn = lambda z: a["t"]  # noqa: E731
    z0, z1 = a["mando"]
    res = []
    for zs, parte in [(np.linspace(a["z_raiz"] - 0.6, z0, 4), "todo"),
                      (np.linspace(z0, z1, 8), "fijo"), (np.linspace(z1, a["z_punta"], 3), "todo")]:
        v, f = malla_superficie(en, zs, 0, 0.4, t_fn, a["corte"], parte)
        res.append(Malla(v, f, BLANCO, "pintura", "deriva"))
    v, f = malla_superficie(en, np.linspace(z0 + 0.03, z1 - 0.03, 8), 0, 0.4, t_fn, a["corte"],
                            "mando")
    ti = Malla(v, f, BLANCO, "pintura", "timon")
    ti.bisagra = (en(z0, np.array([[a["corte"], 0.0]]))[0], en(z1, np.array([[a["corte"], 0.0]]))[0])
    ti.lado = 1
    res.append(ti)
    return res


def revolucion(perfil, eje_x0, centro, n=40):
    """Superficie de revolución alrededor de un eje paralelo a X. `perfil`: [(dx, r), ...]."""
    ths = np.linspace(0, 2 * np.pi, n, endpoint=False)
    secs = []
    for dx, r in perfil:
        secs.append([(eje_x0 + dx, centro[0] + r * np.cos(t), centro[1] + r * np.sin(t)) for t in ths])
    return loft(secs, cerrar_ext=False)


def datos_motor(s):
    m = MOTOR
    Xba, Zala, c = geometria_ala_en(m["y"], 0.0)
    X0 = Xba - m["adelanto"]
    # cara inferior del ala en esa estación (aprox.: 5 % de la cuerda bajo la línea media)
    z_inf = Zala - 0.055 * c
    zc = z_inf - m["hueco"] - m["radio"]
    return X0, np.array([s * m["y"], zc]), Xba, z_inf, c


def mallas_motor(s):
    m = MOTOR
    X0, c, Xba, z_inf, cu = datos_motor(s)
    R = m["radio"]
    ext = [(0.0, 0.84 * R), (0.03, 0.93 * R), (0.12, 0.985 * R), (0.35, R), (1.4, 1.0 * R),
           (2.6, 0.95 * R), (3.6, 0.8 * R), (4.4, 0.6 * R)]
    corte = 2.5                       # el capó trasero se desliza hacia atrás (reversa)
    ext_del = [p for p in ext if p[0] < corte] + [(corte, 0.965 * R)]
    ext_tras = [(corte, 0.965 * R)] + [p for p in ext if p[0] > corte]
    v, f = revolucion(ext_del, X0, c)
    gondola = Malla(v, f, GRIS_MOTOR, "metal", "gondola")
    gondola.orient, gondola.eje = "radial", c
    v, f = revolucion(ext_tras, X0, c)
    capo = Malla(v, f, GRIS_MOTOR, "metal", "reversa")
    capo.orient, capo.eje = "radial", c
    # cascadas de la reversa (oscuras): quedan tapadas por el capó cuando está cerrado
    v, f = revolucion([(corte - 0.05, 0.94 * R), (corte + 0.9, 0.86 * R)], X0, c)
    cascada = Malla(v, f, "#3B4352", "oscuro", "cascada")
    cascada.orient, cascada.eje = "radial", c
    lab = [(0.0, 0.84 * R), (0.25, 0.8 * R), (0.62, 0.78 * R)]
    v, f = revolucion(lab, X0, c)
    labio = Malla(v, f, "#94A3B8", "metal")
    labio.orient, labio.eje = "adentro", c
    # cara del fan, cono (spinner) y álabes
    v, f = revolucion([(0.62, 0.78 * R), (0.62, 0.02)], X0, c)
    fan = Malla(v, f, OSCURO, "oscuro")
    fan.orient = "frente"
    v, f = revolucion([(0.36, 0.0), (0.45, 0.12), (0.62, 0.27), (0.68, 0.28)], X0, c, 28)
    cono = Malla(v, f, "#E2E8F0", "metal")
    cono.orient, cono.eje = "radial", c
    alabes = None
    for k in range(22):
        a = 2 * np.pi * k / 22
        d = np.array([np.cos(a), np.sin(a)])
        t = np.array([-np.sin(a), np.cos(a)])
        r0, r1 = 0.28, 0.77 * R
        q = []
        for r, giro in ((r0, 0.10), (r1, 0.05)):
            p = c + d * r
            q += [(X0 + 0.6, *(p + t * giro)), (X0 + 0.66, *(p - t * giro))]
        pv = np.array([q[0], q[1], q[3], q[2]])
        mb = Malla(pv, [[0, 1, 2], [0, 2, 3], [0, 2, 1], [0, 3, 2]], "#64748B", "metal")
        mb.orient = "nada"
        alabes = mb if alabes is None else alabes.unir(mb)
    # tobera y cono de escape
    v, f = revolucion([(4.4, 0.6 * R), (4.35, 0.5 * R)], X0, c)
    tob = Malla(v, f, OSCURO, "oscuro")
    tob.orient, tob.eje = "adentro", c
    v, f = revolucion([(4.3, 0.47 * R), (4.9, 0.3 * R), (5.3, 0.04)], X0, c, 28)
    esc = Malla(v, f, "#94A3B8", "metal")
    esc.orient, esc.eje = "radial", c
    # pilón: prisma con frente redondeado que entra en el ala
    y = c[0]
    zt = c[1] + R * 0.92
    perfil = [(X0 + 1.1, zt - 0.05), (X0 + 4.8, zt - 0.05), (Xba + 0.62 * cu, z_inf + 0.25),
              (Xba - 0.25, z_inf + 0.25), (X0 + 1.0, zt + 0.25)]
    v, f = [], []
    w = 0.17
    for dy in (-w, w):
        for (x, z) in perfil:
            v.append((x, y + dy, z))
    n = len(perfil)
    for i in range(n):
        j = (i + 1) % n
        f += [[i, j, n + j], [i, n + j, n + i]]
    f += [[0, i, i + 1] for i in range(1, n - 1)] + [[n, n + i + 1, n + i] for i in range(1, n - 1)]
    pilon = Malla(v, f, GRIS_MOTOR, "metal", "pilon")
    for m in (gondola, labio, fan, cono, tob, esc):
        m.nombre = "motor"
    alabes.nombre = "alabes"
    alabes.eje = c
    return [gondola, capo, cascada, labio, fan, cono, alabes, tob, esc, pilon]


Z_SUELO = -4.4       # altura del suelo con el tren fuera (avión nivelado)
TREN = dict(x_principal=19.0, y_principal=3.8, r_principal=0.57, x_morro=4.9, r_morro=0.38)


def cilindro(p0, p1, r, n=16, tapas=True):
    """Cilindro entre p0 y p1 (coordenadas de construcción)."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    eje = p1 - p0
    e = eje / np.linalg.norm(eje)
    a = np.cross(e, [0, 0, 1.0]) if abs(e[2]) < 0.9 else np.cross(e, [1.0, 0, 0])
    a /= np.linalg.norm(a)
    b = np.cross(e, a)
    ths = np.linspace(0, 2 * np.pi, n, endpoint=False)
    anillo = [np.cos(t) * a + np.sin(t) * b for t in ths]
    secs = [[p0 + r * u for u in anillo], [p1 + r * u for u in anillo]]
    return loft(secs, cerrar_ext=tapas)


def mallas_tren():
    t = TREN
    piezas = []
    # principal: pata desde el ala y dos ruedas por lado
    for s in (1, -1):
        y = s * t["y_principal"]
        ze = Z_SUELO + t["r_principal"]
        v, f = cilindro((t["x_principal"], y, -1.25), (t["x_principal"], y, ze), 0.12)
        piezas.append(Malla(v, f, "#94A3B8", "metal", "tren"))
        v, f = cilindro((t["x_principal"], y - 0.55, ze), (t["x_principal"], y + 0.55, ze), 0.06)
        piezas.append(Malla(v, f, "#94A3B8", "metal", "tren"))
        for dy in (-0.45, 0.45):
            v, f = cilindro((t["x_principal"], y + dy - 0.17, ze), (t["x_principal"], y + dy + 0.17, ze),
                            t["r_principal"], 24)
            piezas.append(Malla(v, f, "#1F2937", "oscuro", "tren"))
            v, f = cilindro((t["x_principal"], y + dy - 0.18, ze), (t["x_principal"], y + dy + 0.18, ze),
                            t["r_principal"] * 0.55, 20)
            piezas.append(Malla(v, f, "#CBD5E1", "metal", "tren"))
    # morro
    ze = Z_SUELO + t["r_morro"]
    v, f = cilindro((t["x_morro"], 0, -1.6), (t["x_morro"], 0, ze), 0.09)
    piezas.append(Malla(v, f, "#94A3B8", "metal", "tren"))
    for dy in (-0.24, 0.24):
        v, f = cilindro((t["x_morro"], dy - 0.12, ze), (t["x_morro"], dy + 0.12, ze), t["r_morro"], 20)
        piezas.append(Malla(v, f, "#1F2937", "oscuro", "tren"))
    for m in piezas:
        m.orient = "volumen"
    return piezas


def flexion(y_abs, flex):
    """Subida (m) del ala a la distancia |y| para una flecha `flex` en la punta (viga en
    voladizo: ~ u²)."""
    u = np.clip((np.asarray(y_abs) - ALA["y_raiz"]) / (ALA["y_punta"] - ALA["y_raiz"]), 0, 1)
    return flex * u ** 2


def malla_carenado():
    """Carenado ventral (une las alas con el fuselaje por abajo)."""
    n, k = 40, 24
    v, f = [], []
    for i in range(k):
        u = -1 + 2 * i / (k - 1)
        for j in range(n):
            t = 2 * np.pi * j / n
            r = np.sqrt(max(0.0, 1 - u ** 2))
            v.append((17.4 + 6.4 * u, 1.85 * r * np.cos(t), -1.35 + 0.62 * r * np.sin(t)))
    for i in range(k - 1):
        for j in range(n):
            a, b = i * n + j, i * n + (j + 1) % n
            c, d = (i + 1) * n + (j + 1) % n, (i + 1) * n + j
            f += [[a, b, c], [a, c, d]]
    m = Malla(v, f, GRIS_PANZA, "pintura", "carenado")
    m.orient, m.eje = "radial", (0.0, -1.35)
    return m


def _normales(v, f):
    a, b, c = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
    return np.cross(b - a, c - a), (a + b + c) / 3


def orientar(m, modo):
    """Pone las caras hacia fuera. modo: 'volumen' (pieza cerrada), 'radial' (superficie de
    revolución de un motor; `m.eje` = (y, z) del eje), 'adentro' (labio interior), 'frente'
    (cara del fan, mira hacia −X), 'piel' (parches sobre el fuselaje)."""
    n, cen = _normales(m.v, m.f)
    if modo == "volumen":
        a, b, c = m.v[m.f[:, 0]], m.v[m.f[:, 1]], m.v[m.f[:, 2]]
        signo = np.sum(np.einsum("ij,ij->i", a, np.cross(b, c)))
    elif modo in ("radial", "adentro"):
        r = cen.copy()
        r[:, 0] = 0
        r[:, 1] -= m.eje[0]
        r[:, 2] -= m.eje[1]
        signo = np.sum(np.einsum("ij,ij->i", n, r)) * (1 if modo == "radial" else -1)
    elif modo == "frente":
        signo = -np.sum(n[:, 0])
    else:      # piel
        r = np.array([[0.0, y, z - seccion(X)[2]] for X, y, z in cen])
        signo = np.sum(np.einsum("ij,ij->i", n, r))
    if signo < 0:
        m.f = m.f[:, ::-1]
    return m


@lru_cache(maxsize=1)
def mallas_avion():
    """Todas las piezas (en coordenadas de construcción)."""
    piezas = [malla_fuselaje(), malla_carenado()]
    for s in (1, -1):
        piezas += mallas_ala(s) + mallas_estabilizador(s) + mallas_motor(s)
        for esq in PARABRISAS:
            piezas.append(parche_cuad(esq, OSCURO_VIDRIO, 0.03, 12, "vidrio", s < 0))
        for X in ventanillas_X():
            piezas.append(parche(X - 0.1, X + 0.1, TH_VENTANILLA - 3.6, TH_VENTANILLA + 3.6,
                                 OSCURO_VIDRIO, 0.02, 3, "vidrio", s < 0))
        # línea azul bajo las ventanillas (parche liso a lo largo del fuselaje)
        piezas.append(parche(6.0, 27.6, 4.5, 7.5, AZUL, 0.012, 3, "pintura", s < 0, nx=60))
        for (X0, X1, t0, t1) in PUERTAS:
            for (a, b, c, d) in ((X0, X0 + 0.05, t0, t1), (X1 - 0.05, X1, t0, t1),
                                 (X0, X1, t0, t0 + 1.4), (X0, X1, t1 - 1.4, t1)):
                piezas.append(parche(a, b, c, d, "#9AA6B6", 0.035, 4, "pintura", s < 0))
    piezas += mallas_deriva()
    piezas += mallas_tren()
    for m in piezas:
        modo = getattr(m, "orient", None)
        if modo is None:
            modo = "piel" if m.mat in ("vidrio",) or m.nombre == "" and m.color == "#94A3B8" \
                else "volumen"
        if modo != "nada":
            orientar(m, modo)
    return piezas


# ---------------------------------------------------------------- render 3D (pyrender + EGL)
class Avion3DReal:
    """Render 3D con iluminación real (pyrender + EGL por software). Devuelve imágenes RGBA
    con fondo transparente, supermuestreadas (bordes suaves).
    Ángulos en grados (como `Avion3D`): alabeo > 0 ala derecha abajo; cabeceo > 0 morro
    arriba; guiñada > 0 morro a la derecha; aleron > 0 alabea a la derecha; elevador > 0 sube
    el morro; timon > 0 guiña a la derecha. azimut 0 = de frente, −90 = desde la derecha,
    180 = desde atrás; elevacion > 0 = desde arriba."""

    def __init__(self, ancho=1400, alto=1400, ss=2, campo=26.0, colores_mando=True):
        os.environ.setdefault("PYOPENGL_PLATFORM", "egl")
        os.environ.setdefault("EGL_PLATFORM", "surfaceless")
        import pyrender
        import trimesh
        self.pr, self.tm = pyrender, trimesh
        self.ancho, self.alto, self.ss, self.campo = ancho, alto, ss, campo
        self.r = pyrender.OffscreenRenderer(ancho * ss, alto * ss)
        self.colores_mando = colores_mando
        self._mats = {}
        self._base = []
        for m in mallas_avion():
            v = m.v.copy()
            v[:, 0] = X_CG - v[:, 0]                   # x hacia el morro, origen en el CG
            pieza = dict(v=v, f=m.f[:, ::-1], color=m.color, mat=m.mat, nombre=m.nombre,
                         bisagra=None, lado=getattr(m, "lado", 1))
            if m.bisagra is not None:
                p0, p1 = [np.array(p, float) for p in m.bisagra]
                p0[0], p1[0] = X_CG - p0[0], X_CG - p1[0]
                pieza["bisagra"] = (p0, p1)
            if m.nombre == "fuselaje":
                pieza["colores"] = colores_fuselaje(m.v)
            if m.nombre == "alabes":
                pieza["eje"] = np.array(m.eje, float)       # (y, z) del eje del motor
            self._base.append(pieza)
        self._fijas = None

    def _material(self, color, mat):
        clave = (color if isinstance(color, str) else tuple(np.round(color, 3)), mat)
        if clave not in self._mats:
            rgb = hex_rgb(color) if isinstance(color, str) else np.asarray(color, float)
            lin = rgb ** 2.2
            met, rug = {"pintura": (0.05, 0.42), "metal": (0.55, 0.32), "vidrio": (0.0, 0.08),
                        "oscuro": (0.2, 0.6)}[mat]
            self._mats[clave] = self.pr.MetallicRoughnessMaterial(
                baseColorFactor=[*lin, 1.0], metallicFactor=met, roughnessFactor=rug)
        return self._mats[clave]

    def _malla_pr(self, v, f, color, mat, colores=None):
        t = self.tm.Trimesh(v, f, process=False)
        if colores is not None:
            # una primitiva por color (normales de la malla completa: sin costuras); los
            # colores por vértice de pyrender salen transparentes con EGL
            normales = t.vertex_normals.astype(np.float32)
            cf = colores[f].mean(axis=1)
            prims = []
            for c in np.unique(np.round(cf, 3), axis=0):
                sel = np.all(np.abs(np.round(cf, 3) - c) < 1e-6, axis=1)
                prims.append(self.pr.Primitive(
                    positions=t.vertices.astype(np.float32), normals=normales,
                    indices=f[sel].astype(np.uint32),
                    material=self._material(c, mat)))
            return self.pr.Mesh(prims)
        return self.pr.Mesh.from_trimesh(t, smooth=(mat != "vidrio"),
                                         material=self._material(color, mat))

    def _color_mando(self, nombre):
        if not self.colores_mando:
            return None
        return {"aleron": ROSA, "elevador": AZUL, "timon": AMARILLO}.get(nombre)

    @staticmethod
    def _rot(eje, ang):
        u = eje / np.linalg.norm(eje)
        K = np.array([[0, -u[2], u[1]], [u[2], 0, -u[0]], [-u[1], u[0], 0]])
        return np.eye(3) + np.sin(ang) * K + (1 - np.cos(ang)) * K @ K

    # --- cámara y giros (compartido por imagen y proyectar)
    def _poses(self, alabeo, cabeceo, guinada, azimut, elevacion, distancia, campo, mirar):
        Rz = self._rot(np.array([0, 0, 1.0]), np.radians(-guinada))
        Ry = self._rot(np.array([0, 1.0, 0]), np.radians(-cabeceo))
        Rx = self._rot(np.array([1.0, 0, 0]), np.radians(alabeo))
        R = Rz @ Ry @ Rx
        az, el = np.radians(azimut), np.radians(elevacion)
        d = np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])
        yfov = np.radians(30)
        campo = campo or self.campo
        dist = distancia or (campo / 2) / np.tan(yfov / 2)
        objetivo = R @ np.asarray(mirar, float)
        pos = objetivo + d * dist
        f = -d
        der = np.cross(f, [0, 0, 1.0])
        der = der / np.linalg.norm(der) if np.linalg.norm(der) > 1e-6 else np.array([0, -1.0, 0])
        arr = np.cross(der, f)
        C = np.eye(4)
        C[:3, 0], C[:3, 1], C[:3, 2], C[:3, 3] = der, arr, -f, pos
        return R, C, yfov, campo

    def proyectar(self, puntos, alabeo=0, cabeceo=0, guinada=0, azimut=-35, elevacion=18,
                  distancia=None, campo=None, mirar=(0.0, 0.0, 0.0), flex=0.0, en_ala=False,
                  ortografica=False, **_):
        """Píxeles (x, y; origen arriba a la izquierda) de puntos del avión (metros, ejes del
        avión: x morro, y izquierda, z arriba, desde el CG) con los mismos parámetros que
        `imagen`. `en_ala=True` aplica la flexión del ala a esos puntos."""
        R, C, yfov, campo = self._poses(alabeo, cabeceo, guinada, azimut, elevacion, distancia,
                                        campo, mirar)
        P = np.atleast_2d(np.asarray(puntos, float)).copy()
        if en_ala and flex:
            P[:, 2] += flexion(np.abs(P[:, 1]), flex)
        W = P @ R.T
        Ci = np.linalg.inv(C)
        q = (Ci[:3, :3] @ W.T).T + Ci[:3, 3]
        asp = self.ancho / self.alto
        if ortografica:
            xn = q[:, 0] / (campo / 2 * asp)
            yn = q[:, 1] / (campo / 2)
        else:
            t = np.tan(yfov / 2)
            xn = q[:, 0] / (-q[:, 2]) / t / asp
            yn = q[:, 1] / (-q[:, 2]) / t
        return np.column_stack([(xn + 1) / 2 * self.ancho, (1 - yn) / 2 * self.alto])

    def imagen(self, alabeo=0, cabeceo=0, guinada=0, aleron=0, elevador=0, timon=0,
               azimut=-35, elevacion=18, distancia=None, ortografica=False, luces=True,
               campo=None, mirar=(0.0, 0.0, 0.0), flex=0.0, tren=False, fan=0.0,
               baliza=0.0, estrobo=0.0, noche=0.0, motores=True, flap=0.0, slat=0.0,
               spoiler=0.0, reversa=0.0, resaltar=None):
        """`campo`: metros que caben en vertical (más pequeño = más cerca); `mirar`: punto del
        avión (x hacia el morro, y izquierda, z arriba; metros desde el CG) al que apunta la
        cámara, ya girado con el avión. `flex`: subida de la punta del ala (m). `tren`: tren de
        aterrizaje fuera. `fan`: giro de los álabes (grados). `baliza`/`estrobo`: brillo 0–1 de
        las luces anticolisión (rojas arriba y abajo) y de los destellos blancos de las puntas.
        `noche`: 0–1 apaga la luz del sol (para ver las luces). `flap`: grados (hacia abajo,
        con desplazamiento Fowler hacia atrás); `slat`: 0–1 (sale hacia delante y abajo);
        `spoiler`: grados (hacia arriba); `reversa`: 0–1 (el capó trasero se desliza y deja
        ver las cascadas). `resaltar`: {nombre de pieza: color} para pintar piezas."""
        pr = self.pr
        k = 1 - 0.88 * noche
        escena = pr.Scene(bg_color=[0, 0, 0, 0],
                          ambient_light=[0.33 * k + 0.03, 0.35 * k + 0.035, 0.4 * k + 0.05])
        raiz = pr.Node(name="avion")
        escena.add_node(raiz)
        dz_motor = float(flexion(MOTOR["y"], flex))
        for p in self._base:
            n = p["nombre"]
            if n == "tren" and not tren:
                continue
            v = p["v"]
            color = p["color"]
            if flex and n in ("ala", "aleron", "flap", "slat", "spoiler"):
                v = v.copy()
                v[:, 2] += flexion(np.abs(v[:, 1]), flex)
            elif flex and n == "winglet":
                v = v.copy()
                v[:, 2] += flex
            elif flex and n in ("motor", "alabes", "pilon", "reversa", "cascada"):
                v = v.copy()
                v[:, 2] += dz_motor
            if n == "alabes" and fan:
                ey, ez = p["eje"]
                eje_c = np.array([0.0, ey, ez + dz_motor])
                v = (v - eje_c) @ self._rot(np.array([1.0, 0, 0]), np.radians(fan)).T + eje_c
            if n == "reversa" and reversa:
                v = v.copy()
                v[:, 0] -= 0.95 * reversa
            if p["bisagra"] is not None:
                p0, p1 = [q.copy() for q in p["bisagra"]]
                if flex and n in ("aleron", "flap", "slat", "spoiler"):
                    p0[2] += flexion(abs(p0[1]), flex)
                    p1[2] += flexion(abs(p1[1]), flex)
                eje = p1 - p0
                # eje orientado hacia +y (alerones, elevador) o +z (timón): con ángulo > 0 el
                # borde de salida sube (o va a la derecha, en el timón)
                if n in ("aleron", "elevador", "flap", "slat", "spoiler") and eje[1] < 0:
                    eje = -eje
                if n == "timon" and eje[2] < 0:
                    eje = -eje
                if n == "aleron":
                    ang = np.radians(aleron) * (1 if p["lado"] < 0 else -1)
                elif n == "elevador":
                    ang = np.radians(elevador)
                elif n == "flap":
                    ang = -np.radians(flap)
                elif n == "slat":
                    ang = np.radians(20.0 * slat)
                elif n == "spoiler":
                    ang = np.radians(spoiler)
                else:
                    ang = np.radians(timon)
                Rb = self._rot(eje, ang)
                v = (v - p0) @ Rb.T + p0
                if n == "flap" and flap:        # Fowler: el flap también retrocede y baja
                    v[:, 0] -= 0.015 * flap
                    v[:, 2] -= 0.006 * flap
                if n == "slat" and slat:
                    v[:, 0] += 0.45 * slat
                    v[:, 2] -= 0.12 * slat
                color = self._color_mando(n) or color
            if resaltar and n in resaltar:
                color = resaltar[n]
            nodo = pr.Node(mesh=self._malla_pr(v, p["f"], color, p["mat"], p.get("colores")))
            escena.add_node(nodo, parent_node=raiz)
        if luces:
            Xp, Zp, _ = geometria_ala_en(ALA["y_punta"], 0.15)
            Xe, Ze, _ = geometria_ala_en(ALA["y_punta"], 0.85)
            lista = [((X_CG - Xp, 17.15, Zp + flex), ROJA, 1.0, 0.16),
                     ((X_CG - Xp, -17.15, Zp + flex), VERDE, 1.0, 0.16),
                     ((X_CG - L - 0.05, 0.0, 1.0), "#FFFFFF", 1.0, 0.16)]
            if baliza > 0.01:
                lista += [((X_CG - 15.8, 0.0, R_Z + 0.08), ROJA, baliza, 0.2),
                          ((X_CG - 17.5, 0.0, -R_Z - 0.1), ROJA, baliza, 0.2)]
            if estrobo > 0.01:
                lista += [((X_CG - Xe, 17.2, Ze + flex), "#FFFFFF", estrobo, 0.18),
                          ((X_CG - Xe, -17.2, Ze + flex), "#FFFFFF", estrobo, 0.18)]
            for pos, col, brillo_l, r in lista:
                esf = self.tm.creation.icosphere(subdivisions=2, radius=r)
                esf.apply_translation(pos)
                lin = hex_rgb(col) ** 2.2
                mat = pr.MetallicRoughnessMaterial(baseColorFactor=[*(lin * brillo_l), 1],
                                                   emissiveFactor=list(lin * 4 * brillo_l))
                escena.add_node(pr.Node(mesh=pr.Mesh.from_trimesh(esf, material=mat)),
                                parent_node=raiz)
        R, C, yfov, campo = self._poses(alabeo, cabeceo, guinada, azimut, elevacion, distancia,
                                        campo, mirar)
        M = np.eye(4)
        M[:3, :3] = R
        escena.set_pose(raiz, M)
        if ortografica:
            cam = pr.OrthographicCamera(xmag=campo / 2 * self.ancho / self.alto,
                                        ymag=campo / 2, znear=0.3, zfar=400)
        else:
            cam = pr.PerspectiveCamera(yfov=yfov, aspectRatio=self.ancho / self.alto,
                                       znear=0.3, zfar=400)
        escena.add(cam, pose=C)
        # luces: clave arriba-izquierda de la cámara, relleno frío desde abajo, contraluz
        for dir_cam, inten, col in (((-0.5, 0.75, 0.45), 3.4 * k, (1.0, 0.98, 0.95)),
                                    ((0.6, -0.5, 0.6), 1.1 * k + 0.15, (0.75, 0.85, 1.0)),
                                    ((0.2, 0.3, -1.0), 1.6 * k, (0.9, 0.95, 1.0))):
            if inten <= 0.01:
                continue
            dc = np.array(dir_cam, float)
            dw = C[:3, :3] @ (dc / np.linalg.norm(dc))      # hacia dónde mira la luz: −dw
            zl = dw
            xl = np.cross([0, 0, 1.0], zl)
            xl = xl / np.linalg.norm(xl) if np.linalg.norm(xl) > 1e-6 else np.array([1.0, 0, 0])
            yl = np.cross(zl, xl)
            P = np.eye(4)
            P[:3, 0], P[:3, 1], P[:3, 2] = xl, yl, zl
            escena.add(pr.DirectionalLight(color=col, intensity=inten), pose=P)
        img, _ = self.r.render(escena, flags=pr.RenderFlags.RGBA | pr.RenderFlags.SKIP_CULL_FACES)
        return self._reducir(img)

    def _reducir(self, img):
        from PIL import Image
        if self.ss == 1:
            return img
        im = Image.fromarray(img, "RGBA").convert("RGBa")
        im = im.resize((self.ancho, self.alto), Image.LANCZOS).convert("RGBA")
        return np.asarray(im)


def punto_ala(yy, s=1, xc=0.4, dz=0.0):
    """Punto del ala en ejes del avión (x morro, y izquierda, z arriba, desde el CG):
    distancia `yy` (m) desde el eje, lado s (+1 izquierda, −1 derecha), fracción de cuerda xc."""
    X, Z, _ = geometria_ala_en(yy, xc)
    return np.array([X_CG - X, s * yy, Z + dz])


def a_cuerpo(X, Y, Z):
    """De coordenadas de construcción (X desde el morro) a ejes del avión."""
    return np.array([X_CG - X, Y, Z])

"""
Avión supersónico de ala en ojiva tipo Concorde (proporciones aproximadas, sin librea ni logos):
unos 61,7 m de largo y 25,6 m de envergadura, ala delta en ojiva muy fina, deriva sin
estabilizador horizontal, cuatro motores en dos góndolas bajo el ala y morro afilado (en
crucero, sin abatir). Se dibuja con el mismo render que `lib/avion.py` (`Concorde3D` hereda de
`Avion3DReal`): mismos ejes (X desde el morro, Y izquierda, Z arriba; x morro, origen en el CG).
"""
from functools import lru_cache

import numpy as np

from lib import avion as A

L = 61.7                 # largo
R_F = 1.45               # radio del fuselaje
X_CG = 33.0              # centro de gravedad aproximado (desde el morro)
SEMI = 12.8              # semienvergadura
X_ALA0, X_ALA1 = 14.5, 58.6     # el ala empieza (raíz del borde de ataque) y acaba (borde de salida)
Z_ALA = -0.55
BLANCO, GRIS = "#F1F5F9", "#D9E0E8"


def radio(X):
    """Radio del fuselaje (sección circular) en la estación X."""
    if X <= 11.0:                                   # morro en ojiva larga y afilada
        u = X / 11.0
        return R_F * (1 - (1 - u) ** 2) ** 0.62
    if X <= 51.0:
        return R_F
    u = (X - 51.0) / (L - 51.0)                     # cono de cola
    return R_F * (1 - 0.82 * u ** 1.4)


def z_eje(X):
    """Centro de la sección: la cola sube un poco."""
    return 0.0 if X <= 51.0 else 0.55 * ((X - 51.0) / (L - 51.0)) ** 1.6


def fuselaje():
    n = 48
    ths = np.linspace(0, 2 * np.pi, n, endpoint=False)
    Xs = np.concatenate([np.linspace(0.02, 11, 40), np.linspace(11.5, 50.5, 30), np.linspace(51, L, 24)])
    secs = [[(X, radio(X) * np.cos(t), z_eje(X) + radio(X) * np.sin(t)) for t in ths] for X in Xs]
    v, f = A.loft(secs)
    return A.Malla(v, f, BLANCO, "pintura", "fuselaje")


def borde_ataque(y):
    t = np.clip((y - R_F) / (SEMI - R_F), 0, 1)
    return X_ALA0 + (X_ALA1 - 2.2 - X_ALA0) * t ** 0.55


def borde_salida(y):
    t = np.clip((y - R_F) / (SEMI - R_F), 0, 1)
    return X_ALA1 - 0.9 * t


def ala(s):
    """Ala en ojiva muy fina (perfil simétrico, 3 % → 2,2 %), con leve caída en la punta."""
    secs = []
    for y in np.linspace(R_F - 0.3, SEMI, 26):
        xle, xte = borde_ataque(y), borde_salida(y)
        c = max(xte - xle, 0.6)
        t_rel = 0.03 - 0.008 * (y / SEMI)
        cont = A.contorno_perfil(0, 0.4, t_rel, n=34)
        caida = -0.35 * (max(y - 6.0, 0) / (SEMI - 6.0)) ** 2
        secs.append([(xle + px * c, s * y, Z_ALA + caida + pz * c) for px, pz in cont])
    v, f = A.loft(secs)
    m = A.Malla(v, f, GRIS, "pintura", "ala")
    return m


def deriva():
    secs = []
    for z in np.linspace(R_F - 0.2, 8.6, 14):
        u = max((z - R_F) / (8.6 - R_F), 0.0)
        xle = 48.5 + (57.2 - 48.5) * u ** 0.9
        xte = 60.6 - 0.3 * u
        c = xte - xle
        cont = A.contorno_perfil(0, 0.4, 0.04, n=30)
        secs.append([(xle + px * c, pz * c, z + z_eje(xle)) for px, pz in cont])
    v, f = A.loft(secs)
    return A.Malla(v, f, BLANCO, "pintura", "deriva")


def gondola(s):
    """Góndola con dos motores, bajo el ala: sección rectangular redondeada, toma inclinada."""
    y0, y1, ztop, zbot = 2.9, 6.6, Z_ALA - 0.05, Z_ALA - 1.75
    yc, zc = (y0 + y1) / 2, (ztop + zbot) / 2
    hw, hh, r = (y1 - y0) / 2, (ztop - zbot) / 2, 0.35
    n = 40
    contorno = []
    for k in range(n):                                   # rectángulo redondeado (superelipse)
        a = 2 * np.pi * k / n
        c, si = np.cos(a), np.sin(a)
        contorno.append((hw * np.sign(c) * abs(c) ** 0.3, hh * np.sign(si) * abs(si) ** 0.3))
    secs = []
    for X in np.linspace(38.5, 59.4, 12):
        k = 0.92 if X < 39.5 else 1.0
        secs.append([(X + (0.9 if dz < 0 else 0.0) * (X < 39), s * (yc + dy * k), zc + dz * k)
                     for dy, dz in contorno])
    v, f = A.loft(secs)
    m = A.Malla(v, f, "#C9D2DC", "pintura", "gondola")
    piezas = [m]
    # bocas de las tomas y toberas (oscuras)
    for yy in (yc - hw / 2, yc + hw / 2):
        for X, largo in ((38.45, 0.06), (59.4, 0.9)):
            cv, cf = A.cilindro(np.array([X, s * yy, zc]), np.array([X + largo, s * yy, zc]), 0.62, n=20)
            piezas.append(A.Malla(cv, cf, "#1F2937", "oscuro", "tobera"))
    return piezas


def ventanillas(s):
    """Fila de ventanillas pequeñas y cabina (cuadriláteros oscuros sobre el fuselaje)."""
    v, f = [], []
    th = np.radians(18)
    for X in np.arange(13.0, 46.0, 0.9):
        q = []
        for dX, dth in ((-0.12, -0.07), (0.12, -0.07), (0.12, 0.07), (-0.12, 0.07)):
            r = R_F + 0.02
            q.append((X + dX, s * r * np.cos(th + dth), r * np.sin(th + dth)))
        i = len(v)
        v += q
        f += [[i, i + 1, i + 2], [i, i + 2, i + 3]]
    for X0, X1, t0, t1 in ((8.4, 9.3, 28, 40), (9.4, 10.3, 28, 40)):
        q = []
        for X, t in ((X0, t0), (X1, t0), (X1, t1), (X0, t1)):
            r = radio(X) + 0.03
            q.append((X, s * r * np.cos(np.radians(t)), r * np.sin(np.radians(t))))
        i = len(v)
        v += q
        f += [[i, i + 1, i + 2], [i, i + 2, i + 3]]
    return A.Malla(np.array(v), np.array(f), A.OSCURO_VIDRIO, "vidrio", "ventanillas")


@lru_cache(maxsize=1)
def mallas_concorde():
    piezas = [fuselaje(), deriva()]
    for s in (1, -1):
        piezas += [ala(s), ventanillas(s)] + gondola(s)
    for m in piezas:
        if m.mat != "vidrio":
            A.orientar(m, "volumen")
    return piezas


class Concorde3D(A.Avion3DReal):
    """Como `Avion3DReal`, con la malla del supersónico. Sin luces de navegación por defecto;
    los mandos (alerones, flaps…) no existen en esta malla."""

    def __init__(self, ancho=1400, alto=1400, ss=2, campo=40.0):
        import os
        os.environ.setdefault("PYOPENGL_PLATFORM", "egl")
        os.environ.setdefault("EGL_PLATFORM", "surfaceless")
        import pyrender
        import trimesh
        self.pr, self.tm = pyrender, trimesh
        self.ancho, self.alto, self.ss, self.campo = ancho, alto, ss, campo
        self.r = pyrender.OffscreenRenderer(ancho * ss, alto * ss)
        self.colores_mando = False
        self._mats = {}
        self._base = []
        for m in mallas_concorde():
            v = m.v.copy()
            v[:, 0] = X_CG - v[:, 0]
            self._base.append(dict(v=v, f=m.f[:, ::-1], color=m.color, mat=m.mat, nombre=m.nombre,
                                   bisagra=None, lado=1))
        self._fijas = None

    def imagen(self, **kw):
        kw.setdefault("luces", False)
        return super().imagen(**kw)


def a_cuerpo(X, Y, Z):
    """Construcción → ejes del avión (origen en el CG del supersónico)."""
    return np.array([X_CG - X, Y, Z])

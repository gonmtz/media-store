"""
Genera los efectos de sonido del canal en sfx/*.wav, sintetizados con numpy (sonidos propios:
sin licencias ni atribución). 48 kHz, mono, pico a -3 dBFS.

Uso:  python tools/sfx.py
Efectos:
  whoosh         barrido de ruido (transiciones entre bloques)
  whoosh_suave   barrido más lento y grave (movimientos de cámara)
  pop            golpecito tonal (entra un título o una pastilla)
  tic            clic corto (entra una palabra o una ficha)
  golpe          impacto grave (sello, dato importante)
  chispa         chisporroteo (electricidad)
  subida         barrido tonal ascendente (algo crece o sube)
"""
import wave
from pathlib import Path

import numpy as np

SR = 48000
RAIZ = Path(__file__).resolve().parents[1] / "sfx"
rng = np.random.default_rng(1)


def t_(d):
    return np.arange(int(SR * d)) / SR


def pasabajos(x, fc):
    """Filtro de un polo con frecuencia de corte variable (fc: escalar o array)."""
    fc = np.broadcast_to(np.asarray(fc, dtype=float), x.shape)
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.zeros_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = (1 - a[i]) * x[i] + a[i] * acc
        y[i] = acc
    return y


def envolvente(n, ataque, caida):
    t = np.linspace(0, 1, n)
    e = np.where(t < ataque, t / ataque, np.exp(-(t - ataque) / caida))
    return e


def whoosh(d=0.5, f0=400, f1=3500, f2=600):
    n = int(SR * d)
    ruido = rng.normal(0, 1, n)
    u = np.linspace(0, 1, n)
    fc = np.where(u < 0.45, f0 + (f1 - f0) * (u / 0.45) ** 1.5, f1 + (f2 - f1) * ((u - 0.45) / 0.55))
    banda = pasabajos(ruido, fc) - pasabajos(ruido, fc * 0.25)
    return banda * np.sin(np.pi * u) ** 1.6


def pop(d=0.11):
    t = t_(d)
    f = 520 * np.exp(-t * 18) + 260
    fase = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(fase) * envolvente(len(t), 0.03, 0.22)


def tic(d=0.035):
    t = t_(d)
    return np.sin(2 * np.pi * 2200 * t) * envolvente(len(t), 0.05, 0.25)


def golpe(d=0.45):
    t = t_(d)
    f = 110 * np.exp(-t * 6) + 45
    fase = 2 * np.pi * np.cumsum(f) / SR
    cuerpo = np.sin(fase) * envolvente(len(t), 0.01, 0.35)
    ataque = pasabajos(rng.normal(0, 1, len(t)), 2500) * envolvente(len(t), 0.002, 0.03)
    return cuerpo + 0.6 * ataque


def chispa(d=0.5):
    n = int(SR * d)
    x = np.zeros(n)
    for _ in range(38):
        i = rng.integers(0, n - 400)
        largo = rng.integers(60, 300)
        x[i:i + largo] += rng.normal(0, 1, largo) * np.exp(-np.arange(largo) / (largo / 4))
    agudo = x - pasabajos(x, 1800)
    return agudo * np.sin(np.pi * np.linspace(0, 1, n)) ** 0.5


def subida(d=0.6):
    t = t_(d)
    f = 300 * 2 ** (t / d * 1.6)
    fase = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(fase) * 0.5 + 0.3 * np.sin(2 * fase)) * np.sin(np.pi * t / d) ** 1.2


def guardar(nombre, x):
    x = x / (np.max(np.abs(x)) + 1e-9) * 10 ** (-3 / 20)
    RAIZ.mkdir(exist_ok=True)
    with wave.open(str(RAIZ / f"{nombre}.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    guardar("whoosh", whoosh())
    guardar("whoosh_suave", whoosh(0.8, 200, 1400, 300) * 0.8)
    guardar("pop", pop())
    guardar("tic", tic())
    guardar("golpe", golpe())
    guardar("chispa", chispa())
    guardar("subida", subida())
    print("efectos en", RAIZ)

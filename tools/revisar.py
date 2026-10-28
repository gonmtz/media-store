"""
Revisión automática de un short antes de publicarlo.

Uso: python tools/revisar.py shorts/NN_tema [--video otro.mp4]

Comprueba (ERROR = no publicar; AVISO = mirar y decidir):
  - Video: 1080×1920, 30 fps, duración 30–45 s.
  - Sonoridad integrada −14 ± 1 LUFS.
  - Portada (tools/portada.py): gancho completo en t = 0 y dentro del recorte 3:4.
  - Retención (voz.json): gancho hablado ≤ 3,5 s y bloques ≤ 10 s.
  - Ritmo (fotogramas): algo cambia antes de 1 s, ningún tramo sin cambios de más de 3 s
    y ningún fotograma vacío (solo fondo) en las transiciones.
  - Bucle: parecido entre el último fotograma y el primero (informativo).
  - publicacion.json, si existe: título de TikTok, pregunta, hashtags y atribución de la
    música (CC BY). Campos: {"titulo_tiktok", "texto", "musica"}.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
W, H, FPS_MUESTRA = 270, 480, 10          # muestreo reducido para el análisis de ritmo
UMBRAL_CONTENIDO = 0.02                   # como tools/portada.py
UMBRAL_CAMBIO = 0.004                     # fracción de píxeles que cambian entre muestras

errores, avisos, info = [], [], []


def ffprobe(video):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height,r_frame_rate:format=duration", "-of", "json",
                        str(video)], capture_output=True, text=True, check=True)
    d = json.loads(r.stdout)
    s = d["streams"][0]
    num, den = s["r_frame_rate"].split("/")
    return s["width"], s["height"], float(num) / float(den), float(d["format"]["duration"])


def lufs(video):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(video), "-af",
                        "ebur128", "-f", "null", "-"], capture_output=True, text=True)
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
    return float(m[-1]) if m else None


def fotogramas(video):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(video), "-vf",
                        f"fps={FPS_MUESTRA},scale={W}:{H},format=gray", "-f", "rawvideo", "-"],
                       capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.uint8).reshape(-1, H, W).astype(np.int16)


def contenido(f):
    return float(np.mean(np.abs(f - 18) > 60))   # #0B1220 en gris ≈ 18


def tramos(mascara, minimo):
    """Devuelve [(inicio, fin)] en segundos de las rachas True de al menos `minimo` s."""
    res, ini = [], None
    for i, v in enumerate(list(mascara) + [False]):
        if v and ini is None:
            ini = i
        elif not v and ini is not None:
            if (i - ini) / FPS_MUESTRA >= minimo:
                res.append((ini / FPS_MUESTRA, i / FPS_MUESTRA))
            ini = None
    return res


def revisar_video(video):
    w, h, fps, dur = ffprobe(video)
    if (w, h) != (1080, 1920):
        errores.append(f"resolución {w}×{h}; debe ser 1080×1920")
    if abs(fps - 30) > 0.01:
        errores.append(f"{fps:.2f} fps; deben ser 30")
    (errores if not 30 <= dur <= 45 else info).append(f"duración {dur:.1f} s (30–45 s)")

    i = lufs(video)
    if i is None:
        errores.append("no se pudo medir la sonoridad (¿sin audio?)")
    elif abs(i + 14) > 1:
        errores.append(f"sonoridad {i:.1f} LUFS; debe ser −14 ± 1")
    else:
        info.append(f"sonoridad {i:.1f} LUFS")

    r = subprocess.run([sys.executable, str(AQUI / "portada.py"), str(video)],
                       capture_output=True, text=True)
    for linea in r.stdout.splitlines():
        (errores if linea.startswith("ERROR") else info).append("portada: " + linea)

    F = fotogramas(video)
    c = np.array([contenido(f) for f in F])
    cambio = np.r_[1.0, [float(np.mean(np.abs(F[k] - F[k - 1]) > 25)) for k in range(1, len(F))]]

    primero = next((k for k in range(1, len(F)) if cambio[k] > UMBRAL_CAMBIO), None)
    if primero is None or primero / FPS_MUESTRA > 1.0:
        t = "nunca" if primero is None else f"en {primero / FPS_MUESTRA:.1f} s"
        avisos.append(f"el primer cambio visual llega {t}: conviene antes de 1 s")
    for a, b in tramos(c < UMBRAL_CONTENIDO, 0.2):
        errores.append(f"pantalla vacía entre {a:.1f} y {b:.1f} s (solo fondo)")
    for a, b in tramos(cambio < UMBRAL_CAMBIO, 3.0):
        avisos.append(f"sin cambios visuales entre {a:.1f} y {b:.1f} s ({b - a:.1f} s)")
    a, b = np.abs(F[0] - 18) > 60, np.abs(F[-1] - 18) > 60      # solo el contenido, sin fondo
    union = np.sum(a | b)
    pareci = float(np.sum(a & b) / union) if union else 0.0
    info.append(f"bucle: el contenido del último fotograma coincide en un {100 * pareci:.0f} % "
                "con el del primero (cuanto más, mejor enlaza al repetirse)")


def revisar_voz(carpeta):
    p = carpeta / "voz.json"
    if not p.exists():
        avisos.append("no hay voz.json")
        return
    seg = json.loads(p.read_text()).get("segmentos", {})
    for k, v in seg.items():
        d = v["duracion"]
        if k == "gancho" and d > 3.5:
            avisos.append(f"gancho hablado de {d:.1f} s: la meta es ≤ 3 s")
        elif k not in ("gancho", "cierre") and d > 10:
            avisos.append(f"bloque «{k}» de {d:.1f} s: más de 10 s seguidos con un concepto")


def revisar_publicacion(carpeta):
    p = carpeta / "publicacion.json"
    if not p.exists():
        avisos.append("no hay publicacion.json: revisar a mano título de TikTok, pregunta, "
                      "hashtags y atribución de la música")
        return
    d = json.loads(p.read_text())
    texto = d.get("texto", "")
    if not d.get("titulo_tiktok"):
        errores.append("falta titulo_tiktok (Metricool rechaza la publicación sin él)")
    if "?" not in texto:
        avisos.append("el texto no tiene pregunta a la audiencia")
    if "#" not in texto:
        avisos.append("el texto no tiene hashtags")
    if "Música:" not in texto or "creativecommons.org/licenses/by" not in texto:
        errores.append("falta la atribución de la música (Música: … licencia CC BY 4.0 + enlace)")
    if d.get("musica") and d["musica"].split(" ")[0].lower() not in texto.lower():
        avisos.append(f"la atribución no nombra la pista {d['musica']!r}")


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(2)
    carpeta = Path(args[0])
    video = Path(args[args.index("--video") + 1]) if "--video" in args else carpeta / "final.mp4"
    if not video.exists():
        errores.append(f"no existe {video}")
    else:
        revisar_video(video)
    revisar_voz(carpeta)
    revisar_publicacion(carpeta)
    print(f"== {carpeta}")
    for t, lista in (("OK   ", info), ("AVISO", avisos), ("ERROR", errores)):
        for x in lista:
            print(f"{t} {x}")
    sys.exit(1 if errores else 0)


if __name__ == "__main__":
    main()

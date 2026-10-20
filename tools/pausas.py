"""
Lista las pausas de una narración para fijar los tiempos de voz.json
(segmentos por párrafo del guion y frases para subtítulos).

Uso: python tools/pausas.py shorts/NN_tema/voz.mp3 [umbral_dB=-38] [min_pausa_s=0.25]
Imprime los tramos de habla (inicio, fin). Cada párrafo del guion termina en una
pausa larga (>0.6 s aprox.); cada frase o coma marcada, en una pausa corta.
"""
import re
import subprocess
import sys

ruta = sys.argv[1]
umbral = sys.argv[2] if len(sys.argv) > 2 else "-38"
minimo = sys.argv[3] if len(sys.argv) > 3 else "0.25"
dur = float(subprocess.check_output(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", ruta]))
log = subprocess.run(["ffmpeg", "-i", ruta, "-af", f"silencedetect=noise={umbral}dB:d={minimo}",
                      "-f", "null", "-"], capture_output=True, text=True).stderr
ini = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
fin = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
habla, t = [], 0.0
for a, b in zip(ini, fin):
    if a - t > 0.05:
        habla.append((t, a, b - a))
    t = b
if dur - t > 0.05:
    habla.append((t, dur, 0.0))
print(f"duración total {dur:.2f} s")
for i, (a, b, pausa) in enumerate(habla, 1):
    print(f"{i:2d}  {a:6.2f} – {b:6.2f}   pausa después {pausa:.2f} s")

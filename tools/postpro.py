"""
Mezcla final de un short: imagen (desenfoque de movimiento + viñeta) y audio (música,
efectos de sonido, voz con ducking) normalizado a -14 LUFS en dos pasadas.

Uso (desde la raíz del repo):
  python tools/postpro.py shorts/NN_tema/render.mp4 musica/<pista>.mp3 shorts/NN_tema/final.mp4 [inicio]

Imagen:
  - Si el render va a 60 fps, se mezcla cada par de fotogramas y sale a 30 fps: desenfoque de
    movimiento (obturador de 180°). Renderizar con `manim -qh --fps 60`.
  - Viñeta suave en los bordes (no toca el centro).
Audio:
  - Narrado (hay voz.json junto al render): música bajo la voz con ducking. Los efectos de
    sonido de la escena van en la misma pista que la voz.
  - Sin voz con efectos (formato "texto"): música + efectos, sin ducking.
  - Sin audio (formato "ficha"): solo música.
  Sin voz, la música no lleva fundido de entrada (para que el bucle enlace).
`inicio` (s) elige desde dónde arranca la pista (por defecto 0).
"""
import json
import subprocess
import sys
from pathlib import Path

VIÑETA = "vignette=angle=0.42"
MUSICA_CON_EFECTOS_DB = -6      # la música baja un poco para que se oigan los efectos
EFECTOS_DB = 5                  # y los efectos suben (picos de la pista de efectos ≈ −12 dBFS)


def sonda(video):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "stream=codec_type,r_frame_rate:format=duration", "-of", "json", video],
                       capture_output=True, text=True, check=True)
    d = json.loads(r.stdout)
    audio = any(s["codec_type"] == "audio" for s in d["streams"])
    v = next(s for s in d["streams"] if s["codec_type"] == "video")
    num, den = v["r_frame_rate"].split("/")
    return float(d["format"]["duration"]), float(num) / float(den), audio


def dos_pasadas(entradas, cadena_audio, cadena_video, salida, dur):
    """Mide la sonoridad de `cadena_audio` (termina en la etiqueta [pre]) y la normaliza."""
    medir = cadena_audio + ";[pre]loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json[a]"
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", *entradas, "-filter_complex",
                        medir, "-map", "[a]", "-f", "null", "-"],
                       capture_output=True, text=True, check=True)
    m = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    filtro = (cadena_audio + ";[pre]loudnorm=I=-14:TP=-1.5:LRA=11:linear=true:"
              f"measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
              f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
              f"offset={m['target_offset']}[a];" + cadena_video)
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", *entradas, "-filter_complex", filtro,
        "-map", "[v]", "-map", "[a]", "-r", "30",
        "-c:v", "libx264", "-crf", "18", "-preset", "medium",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-t", str(dur), "-movflags", "+faststart", salida], check=True)


def main(video, musica, salida, inicio="0"):
    dur, fps, audio = sonda(video)
    ini = float(inicio)
    narrado = (Path(video).parent / "voz.json").exists()
    if fps > 45:
        cadena_video = f"[0:v]tmix=frames=2:weights='1 1',fps=30,{VIÑETA}[v]"
    else:
        cadena_video = f"[0:v]{VIÑETA}[v]"
    entradas = ["-i", video, "-i", musica]

    if narrado:
        cadena_audio = (
            f"[1:a]atrim={ini}:{ini + dur},asetpts=N/SR/TB,volume=-18dB,"
            f"afade=t=in:d=0.4,afade=t=out:st={dur - 1.8}:d=1.8[mus];"
            f"[0:a]apad,atrim=0:{dur},asplit=2[voz][sc];"   # sin atrim, apad no acaba nunca
            "[mus][sc]sidechaincompress=threshold=0.02:ratio=5:attack=20:release=450[duck];"
            "[voz][duck]amix=inputs=2:duration=first:normalize=0[pre]")
    else:
        sal = min(0.6, dur / 6)
        mus = (f"[1:a]atrim={ini}:{ini + dur},asetpts=N/SR/TB,afade=t=in:d=0.05,"
               f"afade=t=out:st={dur - sal}:d={sal}")
        if audio:
            cadena_audio = (mus + f",volume={MUSICA_CON_EFECTOS_DB}dB[mus];"
                            f"[0:a]apad,atrim=0:{dur},volume={EFECTOS_DB}dB[fx];"
                            "[mus][fx]amix=inputs=2:duration=first:normalize=0[pre]")
        else:
            cadena_audio = mus + "[pre]"
    dos_pasadas(entradas, cadena_audio, cadena_video, salida, dur)


if __name__ == "__main__":
    main(*sys.argv[1:5])

"""
Mezcla final de un short: música bajo la voz (ducking) + normalización a -14 LUFS.
Los subtítulos los dibuja la escena de Manim; aquí solo se trata el audio.

Uso (desde la raíz del repo):
  python tools/postpro.py shorts/NN_tema/render.mp4 musica/<pista>.mp3 shorts/NN_tema/final.mp4 [inicio]

Si el render no tiene audio (formatos "texto" y "ficha", sin voz), la música va sola, sin
fundido de entrada largo (para que el bucle enlace) y con un fundido de salida corto.
`inicio` (s) elige desde dónde arranca la pista (por defecto 0).
"""
import json
import subprocess
import sys


def tiene_audio(video):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
                        "stream=index", "-of", "csv=p=0", video], capture_output=True, text=True)
    return bool(r.stdout.strip())


def main(video, musica, salida, inicio="0"):
    dur = float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video]))
    ini = float(inicio)
    if not tiene_audio(video):
        sal = min(0.6, dur / 6)
        base = (f"[1:a]atrim={ini}:{ini + dur},asetpts=N/SR/TB,afade=t=in:d=0.05,"
                f"afade=t=out:st={dur - sal}:d={sal}")
        # dos pasadas: en un clip corto, loudnorm de una pasada se queda corto (~ -15,7 LUFS)
        r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", video, "-i", musica,
                            "-filter_complex", base + ",loudnorm=I=-14:TP=-1.5:LRA=11:"
                            "print_format=json[a]", "-map", "[a]", "-f", "null", "-"],
                           capture_output=True, text=True, check=True)
        m = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
        filtro = (base + ",loudnorm=I=-14:TP=-1.5:LRA=11:linear=true:"
                  f"measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
                  f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
                  f"offset={m['target_offset']}[a]")
        subprocess.run([
            "ffmpeg", "-v", "error", "-y", "-i", video, "-i", musica,
            "-filter_complex", filtro, "-map", "0:v", "-map", "[a]",
            "-c:v", "libx264", "-crf", "18", "-preset", "medium",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-t", str(dur), "-movflags", "+faststart", salida], check=True)
        return
    filtro = (
        f"[1:a]atrim=0:{dur},asetpts=N/SR/TB,volume=-18dB,"
        f"afade=t=in:d=0.4,afade=t=out:st={dur - 1.8}:d=1.8[mus];"
        "[0:a]apad,asplit=2[voz][sc];"
        "[mus][sc]sidechaincompress=threshold=0.02:ratio=5:attack=20:release=450[duck];"
        "[voz][duck]amix=inputs=2:duration=first:normalize=0,"
        "loudnorm=I=-14:TP=-1.5:LRA=11[a]"
    )
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-i", video, "-i", musica,
        "-filter_complex", filtro, "-map", "0:v", "-map", "[a]",
        "-c:v", "libx264", "-crf", "18", "-preset", "medium",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-t", str(dur), "-movflags", "+faststart", salida], check=True)


if __name__ == "__main__":
    main(*sys.argv[1:5])

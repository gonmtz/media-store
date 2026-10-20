"""
Mezcla final de un short: música bajo la voz (ducking) + normalización a -14 LUFS.
Los subtítulos los dibuja la escena de Manim; aquí solo se trata el audio.

Uso (desde la raíz del repo):
  python tools/postpro.py shorts/NN_tema/render.mp4 musica/<pista>.mp3 shorts/NN_tema/final.mp4
"""
import subprocess
import sys


def main(video, musica, salida):
    dur = float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video]))
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
    main(*sys.argv[1:4])

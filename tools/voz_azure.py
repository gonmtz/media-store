"""Voz con Azure Speech (TTS neuronal).

La clave NUNCA va al repo (es público): se lee de ~/.config/porquevuela/azure.env
    AZURE_SPEECH_KEY=...
    AZURE_SPEECH_REGION=eastus

Uso:
    python tools/voz_azure.py voces [es-MX es-US es-CO]       # lista voces
    python tools/voz_azure.py decir VOZ guion.txt salida.mp3 [velocidad]
        guion.txt: párrafos separados por línea en blanco (pausa de 700 ms entre ellos).
        velocidad: p. ej. "+5%" (por defecto "0%").
"""
import os
import sys
import json
import urllib.request
from xml.sax.saxutils import escape

ENV = os.path.expanduser("~/.config/porquevuela/azure.env")


def credenciales():
    datos = {}
    with open(ENV) as f:
        for linea in f:
            if "=" in linea and not linea.lstrip().startswith("#"):
                k, v = linea.strip().split("=", 1)
                datos[k] = v.strip().strip('"')
    return datos["AZURE_SPEECH_KEY"], datos.get("AZURE_SPEECH_REGION", "eastus")


def voces(locales=("es-MX", "es-US", "es-CO")):
    clave, region = credenciales()
    req = urllib.request.Request(
        f"https://{region}.tts.speech.microsoft.com/cognitiveservices/voices/list",
        headers={"Ocp-Apim-Subscription-Key": clave})
    lista = json.load(urllib.request.urlopen(req, timeout=30))
    return [v for v in lista if v["Locale"] in locales]


def ssml(voz, texto, velocidad="0%", pausa_ms=700):
    locale = "-".join(voz.split("-")[:2])
    parrafos = [p.strip().replace("\n", " ") for p in texto.split("\n\n") if p.strip()]
    cuerpo = f'<break time="{pausa_ms}ms"/>'.join(escape(p) for p in parrafos)
    return (f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{locale}">'
            f'<voice name="{voz}"><prosody rate="{velocidad}">{cuerpo}</prosody></voice></speak>')


def decir(voz, texto, salida, velocidad="0%"):
    clave, region = credenciales()
    req = urllib.request.Request(
        f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1",
        data=ssml(voz, texto, velocidad).encode("utf-8"),
        headers={"Ocp-Apim-Subscription-Key": clave,
                 "Content-Type": "application/ssml+xml",
                 "X-Microsoft-OutputFormat": "audio-48khz-192kbitrate-mono-mp3",
                 "User-Agent": "porquevuela-tts"})
    with open(salida, "wb") as f:
        f.write(urllib.request.urlopen(req, timeout=60).read())


VOZ_CANAL = "es-MX-JorgeMultilingualNeural"   # elegida por el dueño el 6-nov-2026


def _dur(ruta):
    import subprocess
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries",
                                          "format=duration", "-of", "csv=p=0", str(ruta)]))


def _habla(ruta, umbral=-38, minimo=0.18):
    """Tramos de habla (ini, fin) de un audio."""
    import re
    import subprocess
    log = subprocess.run(["ffmpeg", "-i", str(ruta), "-af",
                          f"silencedetect=noise={umbral}dB:d={minimo}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    ini = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
    fin = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
    dur, tramos, t = _dur(ruta), [], 0.0
    for a, b in zip(ini, fin):
        if a - t > 0.05:
            tramos.append([t, a])
        t = b
    if dur - t > 0.05:
        tramos.append([t, dur])
    return tramos


def guion(carpeta, claves, voz=VOZ_CANAL, velocidad="0%", pausa=0.45):
    """Genera voz.mp3 y voz.json de un short a partir de los párrafos de `## Guion` de guion.md.
    Un párrafo por segmento (claves en orden). Cada párrafo se sintetiza aparte y se unen con
    `pausa` s de silencio, así los inicios de segmento son exactos. Las frases (subtítulos) se
    alinean con los tramos de habla si coinciden en número; si no, reparto por caracteres."""
    import re
    import subprocess
    from pathlib import Path
    c = Path(carpeta)
    txt = (c / "guion.md").read_text(encoding="utf-8")
    cuerpo = re.split(r"^## ", txt, flags=re.M)
    cuerpo = next(s for s in cuerpo if s.startswith("Guion")).split("\n", 1)[1]
    parrafos = [p.strip().replace("\n", " ") for p in cuerpo.split("\n\n") if p.strip()]
    assert len(parrafos) == len(claves), f"{len(parrafos)} párrafos y {len(claves)} claves"
    tmp = c / "_voz_tmp"
    tmp.mkdir(exist_ok=True)
    segmentos, frases, lista, t = {}, [], [], 0.0
    silencio = tmp / "silencio.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
                    "anullsrc=r=48000:cl=mono", "-t", str(pausa), silencio], check=True)
    for i, (clave, p) in enumerate(zip(claves, parrafos)):
        mp3 = tmp / f"{i}_{clave}.mp3"
        decir(voz, p, mp3, velocidad)
        wav = tmp / f"{i}_{clave}.wav"
        # recorta el silencio del principio y del final (Azure deja ~0,1–0,6 s)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", mp3, "-af",
                        "silenceremove=start_periods=1:start_threshold=-45dB,"
                        "areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse",
                        "-ar", "48000", "-ac", "1", wav], check=True)
        d = _dur(wav)
        ini = t
        lista.append(wav)
        t += d
        if i < len(parrafos) - 1:
            lista.append(silencio)
            t += pausa
        segmentos[clave] = {"inicio": round(ini, 3), "duracion": round(t - ini, 3)}
        oraciones = [o.strip() for o in re.split(r"(?<=[.?!:;])\s+", p) if o.strip()]
        tramos = _habla(wav)
        if len(tramos) == len(oraciones):
            for (a, b), o in zip(tramos, oraciones):
                frases.append([round(ini + a, 2), round(ini + b, 2), o])
        else:
            tot = sum(len(o) for o in oraciones)
            a = ini
            for o in oraciones:
                b = a + d * len(o) / tot
                frases.append([round(a, 2), round(b, 2), o])
                a = b
    con = tmp / "lista.txt"
    con.write_text("".join(f"file '{Path(w).resolve()}'\n" for w in lista))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", con,
                    "-c:a", "libmp3lame", "-b:a", "192k", c / "voz.mp3"], check=True)
    (c / "voz.json").write_text(json.dumps({"completo": "voz.mp3", "voz": voz,
                                            "segmentos": segmentos, "frases": frases},
                                           ensure_ascii=False, indent=1))
    for f in tmp.iterdir():
        f.unlink()
    tmp.rmdir()
    return segmentos, frases


if __name__ == "__main__":
    if sys.argv[1] == "guion":
        # python tools/voz_azure.py guion shorts/NN_tema gancho,b1,b2,b3,cierre [velocidad]
        vel = sys.argv[4] if len(sys.argv) > 4 else "0%"
        seg, fr = guion(sys.argv[2], sys.argv[3].split(","), velocidad=vel)
        for k, v in seg.items():
            print(f'{k:10} {v["inicio"]:6.2f}  {v["duracion"]:5.2f} s')
        for f in fr:
            print(f"   {f[0]:6.2f}–{f[1]:6.2f}  {f[2]}")
        sys.exit()
    if sys.argv[1] == "voces":
        for v in voces(tuple(sys.argv[2:]) or ("es-MX", "es-US", "es-CO")):
            print(f'{v["ShortName"]:32} {v["Gender"]:7} {v.get("VoiceType", "")}'
                  f'  estilos={",".join(v.get("StyleList", []))}')
    elif sys.argv[1] == "decir":
        vel = sys.argv[5] if len(sys.argv) > 5 else "0%"
        decir(sys.argv[2], open(sys.argv[3], encoding="utf-8").read(), sys.argv[4], vel)
        print("ok", sys.argv[4])

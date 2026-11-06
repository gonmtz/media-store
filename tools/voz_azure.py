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


if __name__ == "__main__":
    if sys.argv[1] == "voces":
        for v in voces(tuple(sys.argv[2:]) or ("es-MX", "es-US", "es-CO")):
            print(f'{v["ShortName"]:32} {v["Gender"]:7} {v.get("VoiceType", "")}'
                  f'  estilos={",".join(v.get("StyleList", []))}')
    elif sys.argv[1] == "decir":
        vel = sys.argv[5] if len(sys.argv) > 5 else "0%"
        decir(sys.argv[2], open(sys.argv[3], encoding="utf-8").read(), sys.argv[4], vel)
        print("ok", sys.argv[4])

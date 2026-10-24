# Por Qué Vuela: pipeline de shorts

Canal de divulgación de aviación en español, solo videos cortos verticales.
Redes: YouTube @porquevuela, Instagram @porquevuela, TikTok "Por Qué Vuela".
Lema: "La aviación, explicada en un minuto". Este repositorio es público y sirve
de almacén de videos (Metricool los descarga por URL) y de memoria del proyecto.

## Reglas del canal (no negociables)

- **Anónimo.** Nunca mencionar autor, "un ingeniero", equipos, universidades ni datos
  personales, ni en videos, textos, descripciones ni en este repositorio.
- **Rigor:** simplificar sin falsear. Si algo es una simplificación, decirlo en una frase.
  Unidades del SI. Revisar cada afirmación técnica antes de producir.
- Español neutro. Términos ya fijados: "elevador", "alerones", "timón",
  "cabeceo / alabeo / guiñada".
- **Nada se publica sin la aprobación explícita del dueño del canal.**

## Formato de cada short

- Vertical 1080×1920, 30 fps, de 30 a 45 s.
- Estructura: **gancho** (pregunta o dato llamativo, máx. 4 s) → **2-3 bloques** (concepto
  + mecanismo + animación) → **cierre** con resumen y una pregunta a la audiencia.
- Título grande del bloque, frase intuitiva, dato técnico secundario y pastilla
  "SE CONTROLA CON / …" (o equivalente).
- Subtítulos en la franja `SUB_Y`, entre la ilustración y la pastilla. Se omiten donde
  el texto ya está en pantalla (gancho y cierre).
- Estilo: fondo `#0B1220` con rejilla de puntos, aviones con degradado, un color por
  concepto (azul `#38BDF8`, rosa `#FB7185`, amarillo `#FBBF24`), fuentes Inter / Inter Display.
  Todo está en `lib/porquevuela.py`.

## Estructura

```
lib/porquevuela.py      estilo, aviones (lateral, trasero, superior), subtítulos, ShortBase,
                        perfil alar con flujo calculado (Perfil), líneas de corriente, vectores
shorts/NN_tema/         escena.py, guion.md, voz.mp3, voz.json, final.mp4
tools/pausas.py         tramos de habla de la narración (para fijar tiempos)
tools/postpro.py        música con ducking + normalización a -14 LUFS
musica/                 pistas con licencia (ver "Música")
marca/                  avatar, banner y branding.py
```

## Producción de un short nuevo

1. **Guion** en `shorts/NN_tema/guion.md`: un párrafo por segmento (gancho, bloques,
   cierre). Unos 450–550 caracteres, entre 35 y 40 s con la voz de Brian. Revisar
   la exactitud técnica.
2. **Voz** con vidIQ (`vidiq_voiceover_generate`): voz **Brian**, voiceId
   `nPczCjzI2devNBz1zQrb`. Generar el guion **completo en una sola llamada**, con los
   párrafos separados por línea en blanco. Cuesta 14 créditos por cada 1000 caracteres;
   el plan da 150 al mes. Descargar el MP3 de `ai-voiceovers.s3.us-east-1.amazonaws.com`
   (dominio ya permitido) a `shorts/NN_tema/voz.mp3`.
3. **Tiempos**: `python tools/pausas.py shorts/NN_tema/voz.mp3`. Las pausas largas
   (> 0,6 s aprox.) separan párrafos; las cortas, frases. Escribir `voz.json`:
   `{"completo": "voz.mp3", "segmentos": {clave: {"inicio", "duracion"}}, "frases": [[ini, fin, texto], ...]}`.
   El inicio de cada segmento coincide con el final de la pausa anterior.
4. **Escena** en `shorts/NN_tema/escena.py`, con una clase que herede de `ShortBase`
   (ver `shorts/01_ejes`). En cada bloque: `t0, d = self.voz("clave")`; usar
   `self.hasta(t0, d*f)` para sincronizar las animaciones con lo que se narra y cerrar
   con `self.rellenar(t0, d)`.
5. **Render**: `manim -qh --fps 30 shorts/NN_tema/escena.py Clase`
   (para iterar, `-ql`). Revisar fotogramas: texto dentro del ancho seguro (7,4 unidades),
   sin solapes y con el sentido físico de cada giro correcto.
6. **Mezcla**: `python tools/postpro.py <render.mp4> musica/<pista>.mp3 shorts/NN_tema/final.mp4`.
   Comprobar que la sonoridad integrada quede en -14 ± 1 LUFS.
7. Commit y push. URL pública del video:
   `https://raw.githubusercontent.com/gonmtz/media-store/main/shorts/NN_tema/final.mp4`
8. **Publicar con Metricool** (marca `blogId` 7528654, zona horaria America/Mexico_City)
   en youtube, instagram y tiktok, solo tras aprobación:
   - youtubeData: type `short`, `madeForKids` false, category `EDUCATION`,
     `isAiGeneratedContent` false (animación no realista).
   - instagramData: type `REEL`, `isAiGenerated` true (voz sintética).
   - tiktokData: `isAigc` true.
   - Texto: descripción breve + pregunta + hashtags + atribución de la música.
   - No enviar `videoCoverMilliseconds`: el canal de YouTube no está verificado y Metricool
     rechazaría la publicación.

## Entorno (sesión nueva)

```
apt-get install -y libpango1.0-dev libcairo2-dev pkg-config ffmpeg
python3 -m venv mvenv && . mvenv/bin/activate && pip install -U pip setuptools wheel && pip install -r requirements.txt
```

Si pip falla compilando `srt` fuera de un venv, usar el venv.

## Música

Las pistas de `musica/` son de la Biblioteca de audio de YouTube y tienen licencia
Creative Commons Atribución 4.0 (confirmar en la ficha de cada pista). Hay que incluir
la atribución en cada publicación, por ejemplo:
`Música: "Hypnothis" de Kevin MacLeod (incompetech.com), licencia CC BY 4.0 https://creativecommons.org/licenses/by/4.0/`
Rotar las pistas entre shorts. Usadas: 01 → Hypnothis, 02 → Down With That, 03 → Dreamy Flashback, 04 → Hypnothis, 05 → Down With That (repetidas:
no quedan pistas sin usar; incompetech.com está bloqueado desde el entorno, así que hay que
añadir pistas nuevas a mano).
Ojo: `Darkest_Child_-_Kevin_MacLeod.mp3` es el mismo archivo que Hypnothis (mismo md5); hay que
volver a descargar la pista correcta antes de usarla.

## Registro de shorts

| # | Tema | Música | Estado |
|---|------|--------|--------|
| 01 | Los 3 giros (ejes de referencia) | Hypnothis | publicado 2026-10-20 23:05 (CDMX) en YT, IG y TikTok (adelantado a petición del dueño) |
| 02 | Sustentación: el mito del tiempo de tránsito igual | Down With That | publicado 2026-10-21 12:00 (CDMX) en YT, IG y TikTok |
| 03 | Pérdida (stall): caer con los motores funcionando | Dreamy Flashback | publicado 2026-10-21 19:08 (CDMX) en YT, IG y TikTok (adelantado a petición del dueño) |
| 04 | Perfiles NACA: qué significan sus cifras (4 y 5 cifras) | Hypnothis | programado 2026-10-23 12:00 (CDMX) en YT, IG y TikTok |
| 05 | Winglets y vórtices de punta | Down With That | producido 2026-10-24; pendiente de aprobación |

## Banco de ideas (siguientes, en orden)

1. ~~Sustentación: el mito del "tiempo de tránsito igual"~~ (hecho: short 02)
2. ~~Pérdida (stall): caer con los motores funcionando~~ (hecho: short 03)
3. ~~Winglets y vórtices de punta~~ (hecho: short 05)
4. ¿Por qué las hélices están torcidas?
5. Mach y el estampido sónico que se arrastra
6. Reynolds: por qué un insecto no vuela con un ala de avión
7. Motor a reacción: el motor que se traga la lluvia
8. ¿Por qué el Concorde bajaba la nariz?
9. Diedro: por qué las alas forman una V
10. Flaps y slats: volar lento sin caer

Hecho fuera del banco: perfiles NACA (short 04, a petición del dueño).

Piezas aerodinámicas ya disponibles: `Perfil` (Joukowski + flujo potencial 2D con Kutta:
contorno, `linea` con tiempos de paso, `cp_contorno`), `en_tiempo`, `trazo`, `trazadores`,
`vector`, `flechas_presion`. Para la pérdida (short 03): `cl_tipico` / `cd_tipico` (curvas
típicas, no de un perfil concreto), `GraficaCl` (Cl–α rotulada como curva típica, con
`punto`, `curva_hasta`, `marca_critico`), `LineasPorAlfa` + `trazadores_variables` (flujo
pegado mientras gira el ala), `flujo_separado` y `remolinos` (ilustración cualitativa: el
flujo potencial no se separa; rotularla en pantalla) y `angulo_entre`.
Ojo: los grupos con updater que guardan estado (rotación acumulada) se descuadran si se
animan con FadeIn; redibujar desde cero en cada fotograma o usar un ValueTracker de
visibilidad. Perfiles NACA (short 04): `PerfilNACA` (4 cifras y 5 cifras con línea media
normal, geometría exacta a escala real; acepta parámetros continuos para animar),
`naca_espesor`, `naca_linea_media`, `naca_puntos`. Vórtices (short 05): `avion_trasero(winglets=False)`,
`PUNTA_TRASERO`, `winglet_trasero`, `espiral`, `vortice` (visto de frente, con sentido de giro y
`visible`/`escala`), `rodeo_punta`, `estela_superior` (vista desde arriba). Voz: escribir las
siglas en minúsculas ("Naca", "Nasa") o la voz las deletrea. `ShortBase.SUBS_DESDE` omite los
subtítulos del gancho.

Estos temas reutilizan las piezas que ya hay en la biblioteca (perfil, vectores y flujo):
construir y añadir a `lib/porquevuela.py` lo que pueda volver a usarse.

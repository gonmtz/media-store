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

- Tres formatos (campo `formato` de `publicacion.json`; `tools/revisar.py` ajusta sus reglas):
  **narrado** (voz + animación, 30–45 s; lo de abajo), **texto** (sin voz: texto animado en
  pantalla + música, 12–30 s; bloques fijados por tiempo con `self.hasta(0, t)`, sin
  subtítulos; ver `shorts/09_matriculas`) y **ficha** (una imagen fija + música, 3–10 s; ver
  `shorts/08_ficha_formulas`). Desde el 6-nov-2026 hay voz (Azure, ver Producción, paso 2): los shorts 21–22 son narrados.
- Vertical 1080×1920, 30 fps, de 30 a 45 s (narrado).
- Estructura: **gancho** (pregunta o dato llamativo, máx. 4 s) → **2-3 bloques** (concepto
  + mecanismo + animación) → **cierre** con resumen y una pregunta a la audiencia.
- Título grande del bloque, frase intuitiva, dato técnico secundario y pastilla
  "SE CONTROLA CON / …" (o equivalente).
- **Nunca empezar con el fondo vacío.** El primer fotograma es la portada en el perfil de
  Instagram y TikTok: el gancho (texto grande + ilustración) tiene que estar completo desde
  t = 0, sin fundidos de entrada (`self.portada(...)` en `ShortBase`), dentro del recorte 3:4
  de la cuadrícula (nada en los 240 px de arriba y de abajo). La animación del gancho empieza
  después (un pulso, un giro, el sello), no antes. Comprobar con `python tools/portada.py
  shorts/NN_tema/final.mp4` (falla si la portada está vacía o recortada).
- **Retención (desde el 28-oct-2026):** gancho hablado de 3 s como máximo (los shorts 01–06 iban
  de 4,4 a 6,3 s) y algún cambio en pantalla antes de 1 s; bloques de 10 s como máximo; nunca más
  de 3 s sin que algo se mueva (`self.pulso(...)`). **Sin pantalla vacía entre bloques:** al acabar
  un bloque, `self.dejar(...)` en vez de `salir`, y el siguiente entra con `self.cambio(...)`
  (fundido cruzado). Los shorts 01–06 tenían de 3 a 5 huecos de 0,4–0,8 s con solo el fondo.
  Cerrar con una imagen parecida a la del gancho, para que el bucle enlace.
- Plantilla en `ShortBase`: `poner_cabecera`, `textos_bloque`, `entrar_textos`, `etiqueta`,
  `dejar`/`cambio`, `pulso`. No volver a copiarlas en cada escena.
- **Calidad de animación (desde el 5-nov-2026; ver `shorts/09_matriculas`, `10`, `11`):**
  1. **Cámara**: `ShortBase` es una `MovingCameraScene`. `self.enfocar(punto, zoom)` acerca la
     cámara a un detalle (descargadores, matrícula, punta del ala) y `self.vista_general()`
     vuelve. Los textos de pantalla van al HUD con `self.hud(...)` (lo hacen solos
     `poner_cabecera`, `bloque`, `textos_bloque`, `sello`) y se quedan fijos. No mover la
     cámara mientras entra o sale un texto. Un velo oscuro arriba mantiene legibles los títulos.
  2. **Menos texto**: `self.bloque(idx, título, frase, color, dato=None, resaltar=[...])` +
     `self.entrar_bloque(...)`: título y UNA frase (≤ 2 líneas) que entra palabra a palabra
     (`frase_cinetica`, `entrar_palabras`). Pastilla solo si aporta; el remate va en `sello`.
  3. **Efectos de sonido** propios, sintetizados (`python tools/sfx.py` → `sfx/*.wav`, sin
     licencia): `cambio` → whoosh, `entrar_bloque` → pop, `enfocar` → whoosh suave,
     `poner_sello` → golpe; a mano: `self.sonido("tic" | "chispa" | "subida", ganancia_dB)`.
  4. **Acabado**: `brillo` (halo de color detrás de la ilustración), `sombra`, rebote al entrar
     (ease_out_back) y, en `tools/postpro.py`, viñeta y desenfoque de movimiento si se
     renderiza a 60 fps (`manim -qh --fps 60`; sale a 30 fps).
  5. **Aviones con detalle**: luces de navegación (roja = ala izquierda, verde = derecha,
     blanca = cola), puertas, paneles, flaps, tomas y álabes del motor (`luz`, `LUZ_*`).
  6. **Avión refinado (5-nov-2026, demo en `shorts/demo_avion`)**: una sola geometría
     paramétrica en metros (`lib/avion.py`: fuselaje con morro y cono de cola, alas con perfil
     NACA, flecha, diedro y torsión, winglets, motores con pilón, fan y cono, cabina, ventanillas,
     puertas, línea azul, luces) de la que salen:
     - **3D real** `Avion3DReal(ancho, alto, ss, campo).imagen(alabeo, cabeceo, guinada, aleron,
       elevador, timon, azimut, elevacion, campo, mirar)`: pyrender + EGL por software, luz
       clave/relleno/contraluz, supermuestreo, fondo transparente (~0,5 s por imagen). En Manim:
       `capa_3d(render, ancho_pantalla, centro, **params)` de `lib/avion2d.py` (acepta
       ValueTrackers o funciones; desactiva la caché de Manim y parchea un fallo de Manim 0.22 con
       Pillow al dibujar imágenes). `mirar` + `campo` pequeño = primer plano (cabina, motor).
     - **2D vectorial** `lateral_2d`, `superior_2d`, `frontal_2d` (`lib/avion2d.py`): las mismas
       proporciones; `vista.partes[...]` y `vista.a_pantalla(X, Y, Z)` para colocar cosas encima.
       `colores_mando=True` pinta alerones, elevador y timón con los colores de cada giro.
     El `Avion3D` de caras planas queda obsoleto (su demo se borró). Los dibujos antiguos
     (`avion_lateral`, `avion_superior`, `avion_frontal_flexible`) siguen para los shorts 01–11.
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
tools/postpro.py        música (+ efectos o voz con ducking), viñeta, desenfoque de movimiento, -14 LUFS
tools/portada.py        comprueba el primer fotograma (portada del perfil)
tools/revisar.py        revisión completa antes de publicar (formato, LUFS, portada, ritmo, texto)
tools/sfx.py            genera los efectos de sonido (sfx/*.wav, sintetizados, sin licencia)
musica/                 pistas con licencia (ver "Música")
marca/                  avatar, banner y branding.py
```

## Producción de un short nuevo

1. **Guion** en `shorts/NN_tema/guion.md`: un párrafo por segmento (gancho, bloques,
   cierre). Unos 450–550 caracteres, entre 35 y 40 s con la voz de Brian. Revisar
   la exactitud técnica.
2. **Voz** con Azure Speech (F0 gratis, región `eastus`): voz **es-MX-JorgeMultilingualNeural**
   (elegida por el dueño el 6-nov-2026 entre 12 muestras). La clave nunca va al repo (es público):
   pedirla al dueño al empezar la sesión y guardarla en `~/.config/porquevuela/azure.env`
   (`AZURE_SPEECH_KEY=…`, `AZURE_SPEECH_REGION=eastus`, permisos 600; `*.env` está en `.gitignore`).
   `python tools/voz_azure.py guion shorts/NN_tema gancho,b1,b2,b3,cierre [velocidad]` lee los
   párrafos de `## Guion` de `guion.md` (uno por segmento), sintetiza cada uno, los une con 0,45 s
   de silencio y escribe `voz.mp3` y `voz.json` (segmentos exactos y frases para subtítulos), así
   que el paso 3 ya no hace falta. Unos 14 caracteres/s: gancho ≤ 40 caracteres (≤ 3 s), bloques
   ≤ 130 (≤ 10 s). `python tools/voz_azure.py voces` lista las voces. vidIQ (Brian) queda descartado.
3. **Tiempos** (solo si la voz no sale de `voz_azure.py guion`): `python tools/pausas.py shorts/NN_tema/voz.mp3`. Las pausas largas
   (> 0,6 s aprox.) separan párrafos; las cortas, frases. Escribir `voz.json`:
   `{"completo": "voz.mp3", "segmentos": {clave: {"inicio", "duracion"}}, "frases": [[ini, fin, texto], ...]}`.
   El inicio de cada segmento coincide con el final de la pausa anterior.
4. **Escena** en `shorts/NN_tema/escena.py`, con una clase que herede de `ShortBase`
   (ver `shorts/01_ejes`). En cada bloque: `t0, d = self.voz("clave")`; usar
   `self.hasta(t0, d*f)` para sincronizar las animaciones con lo que se narra y cerrar
   con `self.rellenar(t0, d)`.
5. **Portada**: ver "Nunca empezar con el fondo vacío" en Formato. Tras la mezcla, ejecutar
   `python tools/portada.py shorts/NN_tema/final.mp4` y mirar `portada.png`. Las portadas de los shorts 01–06 están
   en `marca/portadas/` (para cambiarlas a mano en Instagram: Editar → portada; en TikTok, solo
   en los 7 días siguientes a la publicación).
6. **Render**: `manim -qh --fps 60 shorts/NN_tema/escena.py Clase` (60 fps para el desenfoque de
   movimiento; tarda varios minutos, lanzarlo en segundo plano). Para iterar, `-ql` (15 fps).
   `lib/porquevuela.py` ya no fija los fps: los decide la línea de comandos. Revisar fotogramas: texto dentro del ancho seguro (7,4 unidades),
   sin solapes y con el sentido físico de cada giro correcto.
7. **Mezcla**: `python tools/postpro.py <render.mp4> musica/<pista>.mp3 shorts/NN_tema/final.mp4 [inicio_s]`.
   Si el render no tiene audio (texto y ficha), pone solo la música, sin fundido de entrada (para
   el bucle) y normaliza en dos pasadas. Una ficha se renderiza con `manim -qh -s` y se
   convierte en video con `ffmpeg -loop 1 -framerate 30 -i imagen.png -t 3 … render.mp4`.
   Comprobar que la sonoridad integrada quede en -14 ± 1 LUFS.
8. **Texto y revisión**: escribir `shorts/NN_tema/publicacion.json` con
   `{"titulo_tiktok", "texto", "musica"}` (texto = descripción + pregunta + hashtags + atribución) y
   ejecutar `python tools/revisar.py shorts/NN_tema`. Con un ERROR no se publica; los AVISOS se
   comentan con el dueño.
9. Commit y push. URL pública del video:
   `https://raw.githubusercontent.com/gonmtz/media-store/main/shorts/NN_tema/final.mp4`
10. **Publicar con Metricool** (marca `blogId` 7528654, zona horaria America/Mexico_City)
   en youtube, instagram y tiktok, solo tras aprobación:
   - youtubeData: type `short`, `madeForKids` false, category `EDUCATION`,
     `isAiGeneratedContent` false (animación no realista).
   - instagramData: type `REEL`, `isAiGenerated` true si tiene voz sintética (narrado); false sin voz.
   - tiktokData: `isAigc` true si tiene voz sintética, y `title` (obligatorio; si falta, Metricool rechaza la publicación).
   - Texto: descripción breve + pregunta + hashtags + atribución de la música.
   - No enviar `videoCoverMilliseconds`: el canal de YouTube no está verificado y Metricool
     rechazaría la publicación.
   - Comprobar la hora devuelta: el 2026-10-24 Metricool guardó 20:00 al pedir 18:00 (CDMX) y
     `updateScheduledPost` no cambió la hora. Si vuelve a pasar, corregirla en la web de Metricool.

## Entorno (sesión nueva)

```
apt-get install -y libpango1.0-dev libcairo2-dev pkg-config ffmpeg
python3 -m venv mvenv && . mvenv/bin/activate && pip install -U pip setuptools wheel && pip install -r requirements.txt
```

Si pip falla compilando `srt` fuera de un venv, usar el venv. Para el 3D real:
`apt-get install -y libegl1 libegl-mesa0 libgl1-mesa-dri` (pyrender usa EGL por software;
OSMesa no funciona con este PyOpenGL).

## Música

Las pistas de `musica/` son de la Biblioteca de audio de YouTube y tienen licencia
Creative Commons Atribución 4.0 (confirmar en la ficha de cada pista). Hay que incluir
la atribución en cada publicación, por ejemplo:
`Música: "Hypnothis" de Kevin MacLeod (incompetech.com), licencia CC BY 4.0 https://creativecommons.org/licenses/by/4.0/`
Rotar las pistas entre shorts. Usadas: 01 → Hypnothis, 02 → Down With That, 03 → Dreamy Flashback, 04 → Hypnothis, 05 → Down With That, 06 → Dreamy Flashback, 08 → Hypnothis, 09 → Down With That, 10 → Dreamy Flashback, 11 → Hypnothis, 12 → Down With That, 13 → Dreamy Flashback (desde 20 s), 14 → Hypnothis, 15 → Down With That, 16 → Dreamy Flashback, 17 → Hypnothis, 18 → Down With That (desde 30 s), 19 → Dreamy Flashback, 20 → Hypnothis, 21 → Down With That, 22 → Dreamy Flashback, 23 → Hypnothis, 24 → Down With That, 25 → Dreamy Flashback, 26 → Hypnothis, 27 → Down With That, 28 → Dreamy Flashback, 29 → Hypnothis, 30 → Down With That, 31 → Dreamy Flashback, 32 → Hypnothis, 33 → Down With That, 34 → Dreamy Flashback, 35 → Hypnothis, 36 → Down With That, 37 → Dreamy Flashback, 38 → Hypnothis, 39 → Down With That, 40 → Dreamy Flashback, 41 → Hypnothis (repetidas:
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
| 04 | Perfiles NACA: qué significan sus cifras (4 y 5 cifras) | Hypnothis | publicado 2026-10-23 12:00 (CDMX) en YT, IG y TikTok |
| 05 | Winglets y vórtices de punta | Down With That | publicado 2026-10-24 20:00 (CDMX) en YT, IG y TikTok (portada vacía: cambiarla a mano) |
| 06 | ¿Por qué las hélices están torcidas? | Dreamy Flashback | publicado 2026-10-27 12:00 (CDMX) en YT, IG y TikTok con la portada vacía; `final.mp4` del repo ya es la versión corregida |
| 07 | Alas volantes: ¿cómo vuela un avión sin cola? | — | boceto sin voz (a petición del dueño); falta revisión técnica, voz y mezcla |
| 08 | Ficha: lo que debes saber de ingeniería aeroespacial (6 fórmulas, imagen fija sin voz) | Hypnothis (0–3 s) | publicado 2026-11-03 03:50 (CDMX) en YT, IG y TikTok (a petición del dueño: "súbelo ya"); sin voz → sin marca de IA en las tres redes |
| 09 | Matrículas: ¿qué significan las letras de un avión? (texto, 24 s) | Down With That | programado 2026-11-06 12:00 (CDMX) en YT, IG y TikTok (Metricool id 418490362); sin voz → sin marca de IA |
| 10 | ¿Por qué el ala se dobla en vuelo? (texto, 26 s) | Dreamy Flashback | programado 2026-11-16 12:00 (CDMX) en YT, IG y TikTok (Metricool id 419464101); sin voz → sin marca de IA |
| 11 | Descargadores de estática: las «antenitas» del ala (texto, 27 s) | Hypnothis (desde 40 s) | no aprobado por el dueño (6-nov); no publicar |
| 12 | Ficha: alfabeto aeronáutico (3 s) | Down With That (desde 30 s) | rehecho con el avión 3D y la matrícula XA-ABC (6-nov); programado 2026-11-15 12:00 (CDMX) (Metricool id 419464076); sin marca de IA |
| 13 | Luces de navegación: ¿por qué la roja va a la izquierda? (texto, 27 s, 3D de noche) | Dreamy Flashback (desde 20 s) | programado 2026-11-14 12:00 (CDMX) en YT, IG y TikTok (Metricool id 419464050); sin marca de IA |
| 14 | Ficha: las partes de un avión (3 s, 3D con rótulos) | Hypnothis | programado 2026-11-17 12:00 (CDMX) (Metricool id 419464132); sin marca de IA |
| 15 | ¿Cómo gira un avión? No es con el timón (texto, 26 s, 3D) | Down With That | no aprobado por el dueño (6-nov); no publicar |
| 16 | ¿Qué hay dentro de un motor? (texto, 26 s, 3D + corte 2D) | Dreamy Flashback | programado 2026-11-19 12:00 (CDMX) (Metricool id 419464158); sin marca de IA |
| 17 | ¿Por qué despegan contra el viento? (texto, 26 s, 3D) | Hypnothis | rehecho con el avión 3D de lado (6-nov); programado 2026-11-18 12:00 (CDMX) (Metricool id 419471020); sin marca de IA |
| 18 | ¿Por qué aterriza con el morro arriba? (texto, 25 s, 2D) | Down With That (desde 30 s) | no aprobado por el dueño (6-nov); no publicar |
| 19 | ¿Y si se apagan todos los motores? Planeo y Gimli 1983 (texto, 26 s, 2D) | Dreamy Flashback | no aprobado por el dueño (6-nov); no publicar |
| 20 | Diedro: ¿por qué las alas forman una V? (texto, 25 s, 3D de frente) | Hypnothis | programado 2026-11-20 12:00 (CDMX) (Metricool id 419464180); sin marca de IA |
| 21 | Estabilidad estática: canica, gráfica Cm–α y CG/punto neutro (narrado, 34 s, voz Jorge Multilingual) | Down With That | programado 2026-11-07 12:00 (CDMX) en YT, IG y TikTok (Metricool id 419245918); voz sintética → marca de IA en IG y TikTok |
| 22 | Estabilidad dinámica: respuesta en el tiempo, fugoide y balanceo holandés (narrado, 32 s) | Dreamy Flashback | programado 2026-11-08 12:00 (CDMX) (Metricool id 419245962); marca de IA en IG y TikTok |
| 23 | Modos dinámicos 1: periodo corto (muelle y amortiguador) (narrado, 32 s, avión 3D) | Hypnothis | programado 2026-11-09 12:00 (CDMX) en YT, IG y TikTok (Metricool id 419429209); marca de IA en IG y TikTok |
| 24 | Modos dinámicos 2: fugoide (narrado, 30 s, avión 3D) | Down With That | programado 2026-11-10 12:00 (CDMX) en YT, IG y TikTok (Metricool id 419451490); marca de IA en IG y TikTok |
| 25 | Modos dinámicos 3: convergencia en alabeo (narrado, 30 s, avión 3D) | Dreamy Flashback | programado 2026-11-11 12:00 (CDMX) en YT, IG y TikTok (Metricool id 419429225); marca de IA en IG y TikTok |
| 26 | Modos dinámicos 4: modo espiral (narrado, 32 s, avión 3D) | Hypnothis | programado 2026-11-12 12:00 (CDMX) en YT, IG y TikTok (Metricool id 419443313); marca de IA en IG y TikTok |
| 27 | Modos dinámicos 5: balanceo holandés (narrado, 30 s, avión 3D) | Down With That | programado 2026-11-13 12:00 (CDMX) en YT, IG y TikTok (Metricool id 419420385); marca de IA en IG y TikTok |
| 28 | Flaps y slats: volar lento sin caer (narrado, 31 s, 3D + perfil 2D) | Dreamy Flashback | listo (7-nov); pendiente de aprobación del dueño: no publicar |
| 29 | ¿Cómo frena un avión? Spoilers, frenos y reversas (narrado, 31 s, 3D) | Hypnothis | listo (7-nov); pendiente de aprobación del dueño: no publicar |
| 30 | Flecha y Mach crítico: ¿por qué las alas van hacia atrás? (narrado, 31 s, 3D + perfil) | Down With That | listo (7-nov); pendiente de aprobación del dueño: no publicar |
| 31 | Estampido sónico: el cono de Mach que barre el suelo (narrado, 33 s) | Dreamy Flashback | listo (7-nov); pendiente de aprobación del dueño: no publicar |
| 32 | Reynolds: ¿un mosquito vuela como un avión? (narrado, 31 s) | Hypnothis | listo (7-nov); pendiente de aprobación del dueño: no publicar |
| 33 | Efecto suelo: ¿por qué flota antes de tocar la pista? (narrado, 31 s, 3D) | Down With That | listo (7-nov); pendiente de aprobación del dueño: no publicar |
| 34 | Transpondedor: 7500, 7600 y 7700 (narrado, 35 s, radar 2D) | Dreamy Flashback | listo (7-nov); pendiente de aprobación del dueño: no publicar |
| 35 | V1, VR y V2 (narrado, 32 s, 3D en la pista) | Hypnothis | listo (7-nov); pendiente de aprobación del dueño: no publicar |
| 36 | Números de pista: ¿por qué se llama 27? (narrado, 33 s, 3D desde arriba) | Down With That | listo (7-nov); pendiente de aprobación del dueño: no publicar |
| 37 | Estela turbulenta (narrado, 30 s, 3D desde atrás) | Dreamy Flashback | listo (7-nov); pendiente de aprobación del dueño: no publicar |
| 38 | ¿Por qué las ventanillas son redondas? (narrado, 31 s, mapas de tensión) | Hypnothis | listo (7-nov); pendiente de aprobación del dueño: no publicar |
| 39 | Ficha: las seis básicas (instrumentos, 5 s) | Down With That | listo (7-nov); pendiente de aprobación del dueño: no publicar |
| 40 | Ficha: las luces de la torre (OACI, 5 s) | Dreamy Flashback | listo (7-nov); pendiente de aprobación del dueño: no publicar |
| 41 | Ficha: unidades de la aviación (5 s, 3D) | Hypnothis | listo (7-nov); pendiente de aprobación del dueño: no publicar |

Los shorts 01–06 se publicaron con la portada vacía (fondo oscuro); las portadas correctas están
en `marca/portadas/` para cambiarlas a mano.

## Banco de ideas (siguientes, en orden)

1. ~~Sustentación: el mito del "tiempo de tránsito igual"~~ (hecho: short 02)
2. ~~Pérdida (stall): caer con los motores funcionando~~ (hecho: short 03)
3. ~~Winglets y vórtices de punta~~ (hecho: short 05)
4. ~~¿Por qué las hélices están torcidas?~~ (hecho: short 06)
5. ~~Mach y el estampido sónico que se arrastra~~ (hecho: short 31)
6. ~~Reynolds: por qué un insecto no vuela con un ala de avión~~ (hecho: short 32)
7. Motor a reacción: el motor que se traga la lluvia
8. ¿Por qué el Concorde bajaba la nariz?
9. ~~Diedro: por qué las alas forman una V~~ (hecho: short 20)
10. ~~Flaps y slats: volar lento sin caer~~ (hecho: short 28)

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
`visible`/`escala`), `rodeo_punta`, `estela_superior` (vista desde arriba). Hélices (short 06):
`angulo_flujo` (tan φ = V/ω·r, sin velocidad inducida), `pala_frontal`, `HeliceFrontal` (vista de
frente, `angulo` ValueTracker, `punto(r)`), `seccion_pala` (perfil NACA visto desde la punta con
ángulo de pala β; el trozo va hacia la izquierda y el avión avanza hacia arriba),
`triangulo_velocidades` (giro, avance, aire que llega y φ) y `pala_torcida` (secciones superpuestas).
Alas volantes (boceto 07): `ala_volante_superior` (silueta genérica, devuelve las puntas) y
`freno_partido` (freno de punta visto desde arriba, `apertura` 0–1). Voz: escribir las
siglas en minúsculas ("Naca", "Nasa") o la voz las deletrea. `ShortBase.SUBS_DESDE` omite los
subtítulos del gancho.

Avión refinado (shorts 09–20): `lib/avion.py` añade `flexion(y, flex)` (ala doblada, short 10), tren de aterrizaje (`TREN`, `Z_SUELO`, `tren=True` en `imagen` y `lateral_2d`), `punto_ala(yy, s, xc, dz)` y `a_cuerpo(X, Y, Z)` (puntos en ejes del avión), `proyectar(...)` y, en Manim, `capa.a_pantalla(puntos, en_ala)` para poner flechas, halos y rótulos sobre el render 3D (13, 14, 15, 20); `imagen(noche=, baliza=, estrobo=, fan=)` para luces y fan girando (13, 16). Para colocar el avión 2D sobre el suelo: `v.shift(-v.a_pantalla(A.TREN["x_principal"], 0, A.Z_SUELO))` (17, 18). Ojo con el ancho: el avión entero tiene que caber en ±4,5 unidades durante toda la animación.

Sin voz (shorts 09–11, dibujos antiguos): `matricula_lateral` (matrícula pintada en `avion_lateral`),
`avion_frontal_flexible(flex)` (vista de frente con el ala doblada como viga en voladizo; devuelve
también y(x) del ala), `descargador`, `puntas_descargadores_superior` (posiciones sobre
`avion_superior`) y `carga` (círculo con signo). Ojo: las capas `always_redraw` pierden el
`z_index` al redibujarse; para que queden encima, añadirlas después del avión y no darle
`z_index` al avión.

Modos dinámicos (shorts 23–27): `lib/modos.py` (`ModoBase`: avión arriba + gráfica respuesta–tiempo abajo movidos por un mismo reloj, `lateral`/`frontal`/`superior` con funciones de actitud, `grafica`, `traza`, `avanzar(t_fin, ...)` para animar hasta un instante, `tarjeta`). 3D (6-nov, los cinco rehechos a petición del dueño): `avion3d(centro, campo, **params)` (capa 3D de 1080 px; `centro` puede ser una función para mover el avión por la pantalla, como en 24 y 26) y `flecha3d(capa, p0, v, color)` (flecha pegada a un punto del avión, en metros y ejes del avión). Convenio del 3D: alabeo + = ala derecha abajo, guiñada + = morro a la derecha, cabeceo + = morro arriba; azimut 0 = de frente, 180 = desde atrás, −90 = de lado con el morro a la derecha (al animar el azimut, ir de 180 a 200, no a −160, o la cámara da la vuelta larga). Render 3D a 60 fps: unos 13 min por short (~2,3 fotogramas/s). Para cambiar el video de una publicación ya programada: `updateScheduledPost` con la misma info y la URL del repo (conserva día y hora; cambia el id, no el uuid). Convenio de signos de las vistas 2D: de frente, alabeo + baja el ala que queda a la izquierda de la pantalla (ala derecha del avión); desde arriba (morro arriba), guiñada + gira en sentido horario.

Estos temas reutilizan las piezas que ya hay en la biblioteca (perfil, vectores y flujo):
construir y añadir a `lib/porquevuela.py` lo que pueda volver a usarse.

Shorts 28–41 (7-nov): `lib/avion.py` tiene flaps Fowler (`flap` en grados), slats (`slat` 0–1), spoilers (`spoiler` en grados), reversas de cascadas (`reversa` 0–1) y `resaltar={pieza: color}` en `imagen`; `capa_3d` acepta `centro` como función. Patrones reutilizables: pista que se desplaza (29, 35), cinta de velocidad vertical (35), radar con barrido (34), vórtices sobre las puntas con `a_pantalla` (33, 37), mapas de tensión de Kirsch (38), pista vista desde arriba con brújula (36). Para rotar alrededor de las ruedas (35): recalcular el centro con `render.proyectar([CONTACTO], cabeceo=...)` en cada fotograma.

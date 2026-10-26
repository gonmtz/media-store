# 06 · ¿Por qué las hélices están torcidas?

## Guion (voz: Brian)

¿Por qué las hélices están torcidas? No es un defecto.

Al girar, la punta recorre un círculo mucho mayor que la raíz, así que va mucho más rápido.

Pero el avión también avanza: el aire llega a cada trozo con un ángulo distinto, muy inclinado cerca del centro y casi en el plano de giro en la punta.

Sin torsión, la raíz empujaría al revés y la punta entraría en pérdida. La torsión gira cada trozo para que todos tengan un ángulo de ataque parecido.

Una pala, muchos ángulos. ¿Te habías fijado alguna vez?

## Revisión técnica

- **Velocidad de cada sección:** al girar con velocidad angular ω, una sección a distancia r
  del eje se mueve a ω·r: la punta va mucho más rápido que la raíz ("the tip of the blade is
  traveling much faster than the inner portion of the blade", FAA). Ejemplo del video (no es
  una hélice concreta): pala de 0,95 m (hélice de 1,9 m) a ω = 240 rad/s (≈ 2300 rpm):
  60 m/s a 0,25 m, 132 m/s a 0,55 m y 228 m/s en la punta. En pantalla se redondea a
  60 / 130 / 230 m/s.
- **Viento relativo:** cada sección recibe el aire combinando el avance del avión (V, a lo
  largo del eje) y su propio giro (ω·r, en el plano de giro); cada punto sigue una hélice y el
  ángulo de esa trayectoria cambia a lo largo de la pala: 90° en el eje y cada vez menor hacia
  fuera (Kitplanes). Con V = 50 m/s (180 km/h): tan φ = V / (ω·r) → φ ≈ 40° (raíz), 21°
  (mitad) y 12° (punta).
- **Ángulo de ataque:** α = β − φ, con β el ángulo de la pala (entre la cuerda de la sección y
  el plano de giro) (MathWorks, teoría del elemento de pala; FAA define el ángulo de pala y el
  ángulo de ataque con el viento relativo y da como eficiente un α de 2–4°). El video usa
  α ≈ 4° como objetivo.
- **Sin torsión (ejemplo):** misma β = 30° en toda la pala → α ≈ −10° en la raíz (sección con
  sustentación negativa: su componente de tracción apunta hacia atrás, "empuja al revés") y
  α ≈ 18° en la punta, por encima del ángulo crítico típico (≈ 15°, ver short 03): en pérdida.
  Es un ejemplo; con otra β fija el problema se reparte distinto, pero no hay ninguna β única
  que sirva a la vez para φ = 40° y φ = 12°. Kitplanes describe el mismo efecto: con una
  torsión que no corresponde a la condición de vuelo, las secciones interiores pueden trabajar
  con ángulo de ataque negativo y las puntas, demasiado cargadas.
- **Con torsión:** β = φ + 4° → unos 44° en la raíz, 25° en la mitad y 16° en la punta.
  "Pitch distribution is the twist in the blade from the shank to the blade tip" (FAA). El
  reparto exacto de torsión depende de la condición de diseño (Kitplanes: unos 8° de torsión
  en una hélice lenta, unos 42° en una rápida).
- **Simplificaciones declaradas:** triángulo de velocidades sin la velocidad inducida por la
  propia hélice (que acelera el aire y aumenta un poco φ) ni la rotación de la estela; secciones
  2D (perfil NACA 4412 como ilustración); números redondeados de un ejemplo. En pantalla:
  "ejemplo" en cada dato.
- **Fuentes:**
  - FAA, *Aviation Maintenance Technician Handbook – Powerplant*, cap. 7 "Propellers":
    https://www.faa.gov/sites/faa.gov/files/09_amtp_ch7.pdf
  - Kitplanes, "Wind Tunnel: Blade Inflow Angle":
    https://www.kitplanes.com/wind-tunnel-53/
  - MathWorks, Blade Element Theory (α = θ − φ, φ = atan(Up/Ut)):
    https://www.mathworks.com/help/aeroblks/bladeelementtheory.html

## Plan visual

- **Gancho:** "¿Por qué las hélices están TORCIDAS?" + tres secciones de la pala superpuestas
  vistas desde la punta que se abren de 30° a sus ángulos reales (`pala_torcida`, nueva) y sello
  "NO ES UN DEFECTO".
- **1 · Velocidad (azul):** hélice de frente girando (`HeliceFrontal`, `pala_frontal`, nuevas),
  círculos que recorren raíz, mitad y punta y flechas ω·r (`vector`) con 60 / 130 / 230 m/s.
  Pastilla "CRECE CON EL RADIO / VELOCIDAD = ω·r".
- **2 · Viento (rosa):** tres filas (punta, mitad, raíz) vistas desde la punta: sección
  (`seccion_pala` sobre `PerfilNACA`, nueva), triángulo de velocidades (`triangulo_velocidades`,
  nuevo: giro, avance y aire que llega) y arco φ (`angulo_entre`). Valores φ = 12°, 21°, 40°
  (`angulo_flujo`, nueva). Pastilla "LO QUE CAMBIA / ÁNGULO DEL AIRE φ".
- **3 · Torsión (amarillo):** misma pala a 30°: α = 18° ("en pérdida"), 9°, −10° ("empuja al
  revés"); luego cada sección gira hasta β = φ + 4° y los tres α pasan a 4° ("trabaja bien").
  Pastilla "LO RESUELVE / LA TORSIÓN".
- **Cierre:** tarjetas Velocidad (ω·r), Viento (φ), Torsión (α ≈ 4°), lema y pregunta.

## Producción

- Voz: Brian (vidIQ), una sola llamada, 509 caracteres facturados, 35,97 s. Cortes con
  `tools/pausas.py` (umbral -38 dB y, para las comas, -32 dB / 0,1 s).
- Música: "Dreamy Flashback" de Kevin MacLeod (repetida: la menos reciente). Mezcla: -14,4 LUFS.
  Duración 37,5 s.

## Publicación (propuesta)

**Título (YouTube):** ¿Por qué las hélices están torcidas? ✈️🌀 #shorts

**Texto:**

La punta de una hélice va mucho más rápido que la raíz y, como el avión también avanza, el aire llega a cada trozo de la pala con un ángulo distinto. La torsión compensa esa diferencia para que toda la pala trabaje con un ángulo de ataque parecido; sin ella, la raíz empujaría al revés y la punta entraría en pérdida. Números de ejemplo y modelo simplificado.

¿Te habías fijado alguna vez? 👇

#aviacion #aerodinamica #avion #helice #fisica #shorts

Música: "Dreamy Flashback" de Kevin MacLeod (incompetech.com), licencia CC BY 4.0 https://creativecommons.org/licenses/by/4.0/

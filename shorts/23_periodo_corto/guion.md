# 23 · Modo de periodo corto

## Guion (voz: Azure es-MX-JorgeMultilingualNeural)

¿Por qué el morro rebota tras una ráfaga?

Es el periodo corto, el modo rápido del cabeceo: el morro sube y baja, cambia el ángulo de ataque, y la velocidad casi no varía.

La estabilidad estática hace de muelle: tira del morro de vuelta. La cola hace de amortiguador: frena cada giro.

Por eso dura pocos segundos y se apaga en una o dos oscilaciones. Sin ese amortiguador, sería muy difícil de pilotar.

Muelle y amortiguador, como en un coche. ¿Lo has sentido en un vuelo con turbulencia?

## Notas técnicas

- Modo longitudinal rápido: oscilación de α y de la velocidad de cabeceo q a velocidad casi constante.
- "Muelle": rigidez en cabeceo por estabilidad estática (Cm_α < 0). "Amortiguador": amortiguamiento
  en cabeceo (Cm_q < 0), sobre todo del estabilizador horizontal: al girar el avión, la cola sube o
  baja y cambia su ángulo de ataque local, lo que crea una fuerza que se opone al giro.
- Periodo típico de pocos segundos (≈ 1–5 s según el avión y la velocidad); amortiguamiento alto
  (factor de amortiguamiento típico ≈ 0,3–0,8). Analogía con la suspensión de un coche: cualitativa.
- Curvas del video: ilustrativas, no de un avión concreto.

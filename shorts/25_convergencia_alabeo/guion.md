# 25 · Convergencia en alabeo

## Guion (voz: Azure es-MX-JorgeMultilingualNeural)

¿Por qué el avión no sigue rodando?

Si una ráfaga lo hace rodar, el ala que baja recibe el aire más de frente: gana ángulo de ataque y sube su sustentación.

El ala que sube pierde sustentación. Juntas crean un momento que frena el giro en cerca de un segundo.

Es una convergencia, sin oscilar. Frena la velocidad de alabeo, pero no endereza: el avión se queda inclinado.

Por eso los alerones mandan velocidad de alabeo, no ángulo: para dejar de girar, se centran. ¿Lo sabías?

## Notas técnicas

- Modo lateral rápido y aperiódico (no oscila): amortiguamiento en alabeo (L_p < 0). Con velocidad
  de alabeo p, una sección a distancia y del eje ve una velocidad vertical p·y: el ala que baja
  tiene más ángulo de ataque y el ala que sube, menos.
- Constante de tiempo típica del orden de 1 s (de décimas de segundo a algo más de 1 s).
- Con alerones fijos se alcanza una velocidad de alabeo constante (p ≈ −L_δa·δa / L_p).
- El ángulo de alabeo no tiene "muelle" propio: tras la perturbación queda donde está (lo que pase
  después lo decide el modo espiral, short 26).

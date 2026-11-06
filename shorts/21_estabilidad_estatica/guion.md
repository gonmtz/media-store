# 21 · Estabilidad estática

## Guion (voz: Azure es-MX-JorgeMultilingualNeural)

Si una ráfaga sube el morro, ¿vuelve solo?

La estabilidad estática mira solo la primera reacción. Como una canica: en un cuenco vuelve, en una mesa se queda y en una colina se escapa.

En la gráfica: si al subir el ángulo de ataque aparece un momento que baja el morro, la pendiente es negativa. Es estable.

Depende del centro de gravedad: por delante del punto neutro, estable; justo encima, neutro; por detrás, inestable.

Vuelve, se queda o se escapa. ¿Sabías que algunos cazas se diseñan inestables a propósito?

## Notas técnicas

- Estabilidad estática longitudinal: signo de dCm/dα alrededor del centro de gravedad (CG).
  dCm/dα < 0 → estable; = 0 → neutra; > 0 → inestable. Para poder volar equilibrado con α > 0
  hace falta además Cm0 > 0 (la recta corta Cm = 0 en el ángulo de equilibrio).
- Punto neutro: posición del CG con la que dCm/dα = 0. Margen estático = (x_PN − x_CG)/c.
- Simplificación (se dice en pantalla): solo se muestra el cabeceo; en guiñada y alabeo existe lo
  mismo (efecto veleta, diedro del short 20).
- La estática no dice cómo vuelve (eso es la dinámica, short 22).
- Cazas con estabilidad relajada (F-16, por ejemplo): ligeramente inestables en cabeceo a
  velocidad subsónica; el control por computadora (fly-by-wire) los mantiene.

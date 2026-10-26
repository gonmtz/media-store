# 07 · Alas volantes: ¿cómo vuela un avión sin cola? (BOCETO)

Boceto sin voz para ver la idea (no gastar créditos). Tiempos de `voz.json` estimados a
14,1 caracteres/s; con la voz real hay que rehacerlos con `tools/pausas.py`.

## Guion provisional (439 caracteres: ampliar a 450–550)

Este avión no tiene cola. ¿Por qué no da vueltas?

En un avión normal, la cola equilibra el ala: si la nariz sube, la cola la devuelve a su sitio.

Un ala volante lo hace sola: las puntas quedan detrás del centro de gravedad y llevan menos ángulo, así que funcionan como una cola repartida.

Y sin timón, para girar abre unos frenos partidos en una punta: esa punta se retrasa y el avión gira.

Menos resistencia, pero muy poco margen. ¿Volarías en uno?

## Pendiente antes de producir

- Revisión técnica con fuentes sólidas (NASA / texto de estabilidad): estabilidad en cabeceo
  sin cola (centro de gravedad por delante del punto neutro, flecha + torsión, perfil reflex),
  frenos partidos del B-2. Consultado de momento: https://en.wikipedia.org/wiki/Flying_wing
- Añadir al guion que el centro de gravedad va por delante del punto neutro.
- La silueta (`ala_volante_superior`) es genérica: no reproduce ningún avión concreto.

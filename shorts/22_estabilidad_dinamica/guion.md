# 22 · Estabilidad dinámica

## Guion (voz: Azure es-MX-JorgeMultilingualNeural)

Volver no basta. ¿Cómo vuelve?

La estabilidad dinámica mira la respuesta en el tiempo. Si se apaga, directa o oscilando cada vez menos, es estable.

Si oscila siempre igual, es neutra. Si cada vaivén crece, es inestable, aunque sea estable estáticamente.

Cada avión tiene sus modos: el fugoide sube y baja en ciclos lentos; el balanceo holandés guiña y alabea en pocos segundos.

Estática: hacia dónde va. Dinámica: cómo llega. ¿Qué modo quieres ver en detalle?

## Notas técnicas

- Respuesta a una perturbación x(t) = A·e^(σt)·cos(ωt): σ < 0 estable (amortiguada), σ = 0 neutra,
  σ > 0 inestable. Sin oscilación (ω = 0): convergencia o divergencia directa (aperiódica).
- La estabilidad estática es necesaria pero no suficiente: se puede tender a volver y aun así
  pasarse cada vez más (oscilación divergente).
- Fugoide: intercambio de altura y velocidad a ángulo de ataque casi constante; periodo de
  decenas de segundos a más de un minuto en un avión de línea; poco amortiguado.
- Balanceo holandés: oscilación acoplada de guiñada y alabeo; periodo de pocos segundos; el
  amortiguador de guiñada (yaw damper) lo corrige.
- No se mencionan (para no pasar de 45 s): periodo corto, convergencia en alabeo, modo espiral.

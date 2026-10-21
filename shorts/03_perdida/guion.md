# 03 · Pérdida (stall): caer con los motores funcionando

## Guion (voz: Brian)

¿Un avión puede caer con los motores a toda potencia? Sí: es la pérdida.

Todo depende del ángulo de ataque: cuánto se inclina el ala frente al aire. Más ángulo, más sustentación, hasta unos quince grados.

Más allá, el aire se despega de la parte de arriba. La sustentación cae de golpe y la resistencia sube.

No es cosa del motor: puede ocurrir a cualquier velocidad y con cualquier inclinación de la nariz. Para salir, hay que bajarla, aunque parezca al revés.

La pérdida es del ala, no del motor. ¿Sabías que se sale bajando la nariz?

## Revisión técnica

- **Ángulo de ataque (α):** ángulo entre la cuerda del ala y el viento relativo (la dirección
  del aire que le llega, opuesta a la trayectoria). No es la inclinación de la nariz respecto
  al horizonte (actitud). "Cuánto se inclina el ala frente al aire" es la versión intuitiva.
- **Ángulo crítico:** en un perfil típico sin dispositivos hipersustentadores el coeficiente de
  sustentación crece casi lineal (≈ 0,1 por grado) hasta un máximo hacia 12–18°. "Unos quince
  grados" se da como orden de magnitud; en pantalla: "≈ 15°" sobre la curva rotulada "curva
  típica, no de un perfil concreto", y "límite ≈ 15° (típico)" en el cierre. Varía con el perfil, el número de Reynolds, los flaps y el estado del ala.
- **Pérdida:** al superar el ángulo crítico, el flujo se separa del extradós; la sustentación
  cae bruscamente y la resistencia aumenta mucho (estela turbulenta ancha).
- **Independiente de la velocidad y de la actitud:** la pérdida solo depende de α. La
  "velocidad de pérdida" del manual vale en vuelo nivelado a 1 g; en un viraje cerrado o en un
  tirón brusco el ala entra en pérdida a más velocidad. Con la nariz baja, si se tira fuerte,
  también puede ocurrir. No tiene relación con la parada del motor: con plena potencia el
  avión puede entrar en pérdida (lo que en inglés se llama "compressor stall" es un fenómeno
  del motor, distinto).
- **Recuperación:** reducir α (empujar, bajar la nariz) para que el flujo vuelva a adherirse;
  después, potencia y nivelar. Tirar hacia atrás para "subir" aumenta α y empeora la pérdida.
- **Lo que se ve en la animación:**
  - Hasta 15°, flujo adherido calculado con `Perfil` (Joukowski + flujo potencial 2D con
    Kutta), rotulado "flujo ideal en 2D". La flecha de sustentación sigue la curva típica.
  - El flujo separado NO sale del modelo (el flujo potencial no puede separarse): es una
    ilustración cualitativa (`flujo_separado`), rotulada "ilustración simplificada".
  - La gráfica Cl–α (`GraficaCl`) es una curva típica de forma genérica, rotulada como tal;
    no son datos de un perfil concreto.
  - Bloque del avión: actitud 15° nariz arriba, trayectoria descendiendo 10° → α ≈ 25° (en
    pérdida aunque la nariz apunte arriba). Al bajar la nariz a −5° con la misma trayectoria,
    α ≈ 5°. Simplificación: se mide α respecto al eje del fuselaje.

## Producción

- Voz: Brian (vidIQ), una sola llamada, 540 caracteres, 37,4 s. Cortes fijados con
  `tools/pausas.py` y recuento de sílabas por tramo de habla (picos de energía).
- Música: "Dreamy Flashback" de Kevin MacLeod. Mezcla: -14,5 LUFS integrados. Duración 38,9 s.

## Publicación

**Título (YouTube):** ¿Un avión puede caer con los motores a toda potencia? ✈️ #shorts

**Texto:**

Sí: se llama pérdida (stall) y no tiene nada que ver con el motor. Al pasar el ángulo de ataque crítico (del orden de 15° en un perfil típico), el aire se despega de la parte de arriba del ala: la sustentación cae de golpe y la resistencia sube. Puede ocurrir a cualquier velocidad y con la nariz en cualquier posición. Para salir hay que bajar la nariz. Animación simplificada: flujo ideal en 2D, flujo separado ilustrado y curva de sustentación típica.

¿Sabías que se sale bajando la nariz? 👇

#aviacion #aerodinamica #avion #piloto #fisica #shorts

Música: "Dreamy Flashback" de Kevin MacLeod (incompetech.com), licencia CC BY 4.0 https://creativecommons.org/licenses/by/4.0/

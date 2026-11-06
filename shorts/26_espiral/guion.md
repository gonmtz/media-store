# 26 · Modo espiral

## Guion (voz: Azure es-MX-JorgeMultilingualNeural)

Inclinado y sin tocar nada, ¿qué pasa?

Empieza el modo espiral. Si el avión se queda inclinado, resbala hacia el ala baja, y dos efectos compiten.

El diedro tiende a nivelar las alas. La deriva gira el morro hacia el giro: el ala de fuera va más rápido y lo inclina más.

Si gana la deriva, la inclinación crece despacio y el morro baja: una espiral que se cierra. Tarda decenas de segundos.

Es tan lento que se corrige sin esfuerzo, pero sin ver el horizonte es traicionero. ¿Lo conocías?

## Notas técnicas

- Modo lateral lento y aperiódico. Estable si domina el efecto diedro (L_β), divergente si domina
  la estabilidad direccional (N_β) junto con el alabeo por guiñada (L_r).
- Muchos aviones son ligeramente inestables en espiral; las normas lo admiten si la divergencia es
  lenta (tiempo para doblar la inclinación de varias decenas de segundos).
- Peligro real: en nubes, sin referencias visuales, el piloto puede no notarlo (desorientación espacial).
- Simplificación: se describe el efecto diedro y la deriva; también influyen la flecha y la posición del ala.

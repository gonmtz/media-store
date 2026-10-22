# 04 · Perfiles NACA: qué significan sus cifras

## Guion (voz: Brian)

NACA dos cuatro uno dos: parece una contraseña, pero es un ala.

NACA, la antecesora de la NASA, numeró así sus perfiles. La primera cifra es la curvatura máxima: dos por ciento de la cuerda. La segunda dice dónde está: al cuarenta por ciento.

Las dos últimas son el espesor: doce por ciento. Si empieza por cero cero, el perfil es simétrico.

La serie de cinco cifras, como el dos tres cero uno dos, lleva la curvatura máxima más adelante: al quince por ciento.

Cuatro cifras, un ala entera. ¿Qué perfil quieres que descifremos?

(Las cifras se escriben con palabras para que la voz las lea una a una.)

## Revisión técnica

- **NACA** (National Advisory Committee for Aeronautics, 1915–1958) es la antecesora de la NASA.
- **Serie de 4 cifras (MPXX), por ejemplo 2412:** M = curvatura máxima en % de la cuerda (2 %);
  P = posición de la curvatura máxima en décimas de cuerda desde el borde de ataque (40 %);
  XX = espesor máximo en % de la cuerda (12 %). 00XX = perfil simétrico (sin curvatura).
  Comprobado con la geometría generada: el 2412 tiene la curvatura máxima de 2,0 % en x ≈ 0,40
  y el espesor máximo de 12 % en x ≈ 0,30.
- **Cuerda:** la recta del borde de ataque al borde de salida (dato en pantalla).
- **Serie de 5 cifras (LPSTT), por ejemplo 23012:** L × 0,15 = coeficiente de sustentación de
  diseño (0,3); P / 20 = posición de la curvatura máxima (15 %); S = 0 línea media normal, 1
  "reflex"; TT = espesor (12 %). Por decisión editorial el video no desglosa cada cifra: solo
  dice que la serie lleva la curvatura máxima más adelante (al 15 % en la serie 230). Geometría:
  23012 con curvatura máxima de ≈ 1,8 % en x ≈ 0,15.
- **Dibujo:** los perfiles salen de las ecuaciones publicadas (espesor NACA y líneas medias de 4
  y 5 cifras con la tabla r, k1), con `PerfilNACA` en `lib/porquevuela.py`, a escala real (sin
  exagerar curvatura ni espesor; rotulado "dibujado a escala real"). Borde de salida cerrado
  (coeficiente −0,1036). Las variaciones animadas (por ejemplo 6412, 2424) son perfiles reales de
  la misma familia.
- Fuente: https://en.wikipedia.org/wiki/NACA_airfoil (definiciones de las series y tabla de la
  serie de 5 cifras).

## Producción

- Voz: Brian (vidIQ), una sola llamada, 531 caracteres, 40,0 s. Cortes fijados con
  `tools/pausas.py` y recuento de sílabas por tramo de habla.
- Música: "Hypnothis" de Kevin MacLeod (reutilizada: no queda ninguna pista sin usar en
  `musica/` y no se pudo descargar una nueva). Mezcla: -14,4 LUFS. Duración 41,5 s.

## Publicación

**Título (YouTube):** ¿Qué significa NACA 2412? El código secreto de las alas ✈️ #shorts

**Texto:**

NACA 2412 no es una contraseña: es la receta de un ala. En la serie de 4 cifras, la primera es la curvatura máxima (2 % de la cuerda), la segunda dice dónde está (al 40 %) y las dos últimas son el espesor (12 %). Si empieza por 00, el perfil es simétrico. La serie de 5 cifras, como el 23012, lleva la curvatura máxima más adelante: al 15 % de la cuerda. Perfiles dibujados a escala real con las ecuaciones de NACA.

¿Qué perfil quieres que descifremos? 👇

#aviacion #aerodinamica #avion #ingenieria #NACA #shorts

Música: "Hypnothis" de Kevin MacLeod (incompetech.com), licencia CC BY 4.0 https://creativecommons.org/licenses/by/4.0/

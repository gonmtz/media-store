# 02 · Sustentación: el mito del tiempo de tránsito igual

## Guion (voz: Brian)

¿El aire de arriba del ala corre más para llegar a la vez que el de abajo? Es un mito.

Arriba sí va más rápido, pero nada lo obliga a reencontrarse. De hecho, llega antes al borde de salida.

La clave: el ala desvía el aire hacia abajo. Si lo empuja hacia abajo, el aire empuja al ala hacia arriba. Tercera ley de Newton.

Para curvar así el flujo, la presión encima del ala queda más baja que debajo. Es la misma fuerza, vista de otra forma.

Newton y Bernoulli no se pelean: son dos caras de lo mismo. ¿Qué otro mito de aviación te contaron?

## Revisión técnica

- Lo falso es la premisa del "tiempo de tránsito igual", no Bernoulli: arriba el aire sí va
  más rápido y la presión es menor, pero no hay ninguna ley que obligue a las dos partículas
  a reencontrarse. El aire de arriba llega antes al borde de salida.
- Desviación hacia abajo (Newton) y diferencia de presiones (Bernoulli/Euler) describen la
  misma fuerza: el aire solo sigue una trayectoria curva si hay un gradiente de presión.
- La animación no es ilustrativa a mano: sale de un perfil de Joukowski (α = 6°, curvatura
  moderada, Cl ≈ 1,1) en flujo potencial 2D con condición de Kutta (`Perfil` en
  `lib/porquevuela.py`). Con la línea de partículas que salen a la vez, la partícula de arriba
  llega al borde de salida en t ≈ 4,4 y la de abajo en t ≈ 5,7 (≈ 30 % más tarde).
  Simplificación declarada en pantalla: "flujo ideal en 2D" (sin viscosidad ni estela).
- Las flechas de presión son Cp = 1 − (V/U)² sobre el contorno, recortadas a una longitud
  máxima cerca del borde de ataque.

## Publicación

**Título (YouTube):** El mito de la sustentación que te enseñaron ✈️ #shorts

**Texto:**

¿El aire de arriba del ala llega a la vez que el de abajo? No: llega antes. El ala vuela porque desvía el aire hacia abajo (3.ª ley de Newton) y eso crea menos presión arriba que abajo: dos caras del mismo fenómeno. Animación simplificada: flujo ideal en 2D.

¿Qué otro mito de aviación te contaron? 👇

#aviacion #aerodinamica #avion #fisica #sustentacion #shorts

Música: "Down With That" de Twin Musicom (twinmusicom.org), licencia CC BY 4.0 https://creativecommons.org/licenses/by/4.0/

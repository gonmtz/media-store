"""
Short 10 (texto, sin voz): ¿por qué el ala se dobla hacia arriba?
- En tierra el ala cuelga un poco por su peso, el del combustible y el de los motores.
- En vuelo, la sustentación se reparte a lo largo del ala y el peso está sobre todo en el
  fuselaje: el ala trabaja como una viga en voladizo y la punta sube.
- Prueba de carga última del 787 (Boeing, 28-mar-2010): 150 % de las fuerzas más extremas
  esperadas en servicio; las alas subieron unos 7,6 m (25 ft).
Dibujo: semienvergadura de 3,3 unidades; 7,6 m sobre unos 30 m de semiala → ~0,85 unidades.
Las flexiones en tierra y en vuelo del dibujo son ilustrativas (no de un avión concreto).
Render:  manim -qh --fps 60 shorts/10_ala_dobla/escena.py AlaDobla
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403

C_TIERRA, C_VUELO, C_PRUEBA = C_CABECEO, C_ALABEO, C_GUINADA
F_TIERRA, F_VUELO, F_PRUEBA = -0.14, 0.38, 0.85
Y_AVION = -0.3
ESC = 0.9            # el ala termina en x = ±3,4 (dentro del ancho seguro)


class AlaDobla(ShortBase):
    def construct(self):
        self.iniciar()
        flex = ValueTracker(F_PRUEBA)

        def dibujo():
            g, _ = avion_frontal_flexible(flex.get_value())
            return g.scale(ESC, about_point=ORIGIN).shift(UP * Y_AVION)
        avion = always_redraw(dibujo)

        def y_ala(x):
            """Altura del ala en la x del mundo."""
            _, f = avion_frontal_flexible(flex.get_value())
            return ESC * f(x / ESC) + Y_AVION

        fondo = brillo(UP * Y_AVION, C_VUELO, 3.8, 0.9)

        # ---------- Gancho (portada en t = 0) ----------
        l1 = T("¿El ala se está", size=64, weight=HEAVY, font=F_TIT)
        pal = T("ROMPIENDO?", size=104, color=BG, weight=HEAVY, font=F_TIT)
        caja = RoundedRectangle(width=pal.width + 0.7, height=pal.height + 0.5, corner_radius=0.3,
                                fill_color=C_VUELO, fill_opacity=1, stroke_width=0).move_to(pal)
        destacado = VGroup(caja, pal).rotate(-3 * DEGREES)
        preg = self.hud(VGroup(l1, destacado).arrange(DOWN, buff=0.3).move_to(UP * 4.5))
        sello = self.sello("NO: ESTÁ HECHA PARA DOBLARSE", C_PRUEBA, DOWN * 3.3, size=44)
        self.portada(fondo, avion, preg)
        self.wait(0.35)
        self.sonido("whoosh_suave", -12)
        self.play(flex.animate.set_value(F_PRUEBA - 0.35), rate_func=there_and_back, run_time=1.0)
        self.poner_sello(sello)
        self.pulso(destacado, 1.08)
        self.hasta(0, 3.4)

        # ---------- 1. En tierra ----------
        self.dejar(preg, sello)
        self.play(self.poner_cabecera("ALAS QUE SE DOBLAN", 3), run_time=0.01)
        barra, tit, fr, dt = self.bloque(0, "En tierra", "El ala cuelga por su propio peso",
                                         C_TIERRA, dato="ala + combustible + motores",
                                         resaltar=["cuelga"])
        self.cambio(flex.animate.set_value(F_TIERRA), FadeIn(tit, shift=DOWN * 0.3, scale=1.2),
                    barra.animate.set_fill(C_TIERRA), run_time=0.8)
        self.entrar_palabras(fr)
        self.play(FadeIn(dt), run_time=0.3)
        pesos = VGroup(*[vector([s * x, y_ala(s * x) - 0.15, 0], [s * x, y_ala(s * x) - 1.0, 0],
                                C_TIERRA, ancho=7, punta=0.22)
                         for s in (-1, 1) for x in (1.3, 2.2, 3.0)])
        self.sonido("tic", -8)
        self.play(LaggedStart(*[GrowArrow(p) for p in pesos], lag_ratio=0.1), run_time=0.7)
        self.enfocar([2.1, Y_AVION - 0.4, 0], 1.9, run_time=0.9)
        self.wait(0.7)
        self.vista_general(run_time=0.8)
        self.hasta(0, 9.4)

        # ---------- 2. En vuelo ----------
        self.dejar(tit, fr, dt, pesos)
        barra, tit, fr, dt = self.bloque(1, "En vuelo", "La sustentación empuja el ala hacia arriba",
                                         C_VUELO, dato="a lo largo del ala; el peso va sobre todo en el fuselaje",
                                         resaltar=["arriba"])

        def sust():
            return VGroup(*[vector([s * x, y_ala(s * x) + 0.15, 0],
                                   [s * x, y_ala(s * x) + 0.9, 0], C_VUELO, ancho=7, punta=0.22)
                            for s in (-1, 1) for x in (0.8, 1.55, 2.3, 3.0)])
        flechas = always_redraw(sust)
        peso = vector([0, Y_AVION - 0.7, 0], [0, Y_AVION - 2.0, 0], C_TIERRA, ancho=10, punta=0.3)
        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.2), barra.animate.set_fill(C_VUELO))
        self.entrar_palabras(fr)
        self.play(FadeIn(dt), run_time=0.3)
        self.play(FadeIn(flechas), GrowArrow(peso), run_time=0.45)
        self.sonido("subida", -8)
        self.play(flex.animate.set_value(F_VUELO), run_time=1.3)
        self.wait(0.5)
        self.play(flex.animate.set_value(F_VUELO + 0.14), rate_func=there_and_back, run_time=0.9)
        self.wait(0.4)
        self.play(peso.animate.scale(1.12, about_edge=UP), rate_func=there_and_back, run_time=0.5)
        self.hasta(0, 15.6)

        # ---------- 3. La prueba ----------
        self.dejar(tit, fr, dt, flechas, peso)
        barra, tit, fr, dt = self.bloque(2, "La prueba", "Hasta 1,5 veces lo peor esperado",
                                         C_PRUEBA, dato="Boeing 787, 2010", resaltar=["1,5"])
        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.2), barra.animate.set_fill(C_PRUEBA))
        self.entrar_palabras(fr)
        self.play(FadeIn(dt), run_time=0.3)
        self.sonido("subida", -6)
        self.play(flex.animate.set_value(F_PRUEBA), run_time=1.4)
        _, f = avion_frontal_flexible(F_PRUEBA)
        y0 = ESC * (-0.15 + 0.18) + Y_AVION          # punta del ala sin doblar
        y1 = ESC * f(3.75) + Y_AVION
        xt = ESC * 3.75
        recta = DashedLine([0.9, y0, 0], [xt + 0.15, y0, 0], dash_length=0.08, color=C_PRUEBA,
                           stroke_width=3)
        flecha = DoubleArrow([xt, y0, 0], [xt, y1 + 0.05, 0], color=C_PRUEBA, buff=0,
                             stroke_width=5, tip_length=0.12)
        e = self.etiqueta("≈ 7,6 m", C_PRUEBA, ORIGIN, size=28).scale(0.6)
        e.next_to(flecha, LEFT, buff=0.12)
        self.enfocar([xt - 0.6, (y0 + y1) / 2, 0], 2.4, run_time=0.9)
        self.play(Create(recta), GrowFromCenter(flecha), run_time=0.5)
        self.sonido("pop", -8)
        self.play(FadeIn(e, scale=1.3), run_time=0.3)
        self.wait(1.0)
        self.vista_general(run_time=0.8)
        sello2 = self.sello("DOBLARSE NO ES FALLAR", C_PRUEBA, DOWN * 3.6, size=46)
        self.poner_sello(sello2)
        self.wait(0.6)
        self.pulso(sello2, 1.06)
        self.hasta(0, 22.6)

        # ---------- Cierre (vuelve a la portada) ----------
        self.dejar(tit, fr, dt, recta, flecha, e, sello2, self.tema, self.barras)
        cierre = self.hud(frase_cinetica("¿Lo has visto desde la ventanilla?", size=58,
                                         resaltar=["ventanilla?"], color_resalte=C_VUELO)
                          .move_to(UP * 4.5))
        nota = self.hud(T("Flexión a escala del ensayo; en vuelo es bastante menor", size=28,
                          color=TEXTO_SEC, weight=MEDIUM).move_to(DOWN * 3.3))
        self.cambio(FadeIn(nota))
        self.entrar_palabras(cierre)
        self.hasta(0, 25.0)
        self.dejar(cierre, nota)
        self.cambio(FadeIn(preg), run_time=0.3, desplazar=UP * 0.6)
        self.wait(0.25)

"""
Short 10 (texto, sin voz): ¿por qué el ala se dobla hacia arriba?
- En tierra el ala cuelga un poco por su peso, el del combustible y el de los motores.
- En vuelo, la sustentación se reparte a lo largo del ala y el peso está sobre todo en el
  fuselaje: el ala trabaja como una viga en voladizo y la punta sube.
- Prueba de carga última del 787 (Boeing, 28-mar-2010): 150 % de las fuerzas más extremas
  esperadas en servicio; las alas subieron unos 7,6 m (25 ft).
Dibujo: semienvergadura de 3,3 unidades; 7,6 m sobre unos 30 m de semiala → ~0,85 unidades.
Las flexiones en tierra y en vuelo del dibujo son ilustrativas (no de un avión concreto).
Render:  manim -qh --fps 30 shorts/10_ala_dobla/escena.py AlaDobla
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
        self.flex = flex

        def dibujo():
            g, _ = avion_frontal_flexible(flex.get_value())
            return g.scale(ESC, about_point=ORIGIN).shift(UP * Y_AVION)
        avion = always_redraw(dibujo)

        def y_ala(x):
            """Altura en pantalla del ala en la x de pantalla."""
            _, f = avion_frontal_flexible(flex.get_value())
            return ESC * f(x / ESC) + Y_AVION

        # ---------- Gancho (portada en t = 0) ----------
        l1 = T("¿El ala se está", size=64, weight=HEAVY, font=F_TIT)
        pal = T("ROMPIENDO?", size=104, color=BG, weight=HEAVY, font=F_TIT)
        caja = RoundedRectangle(width=pal.width + 0.7, height=pal.height + 0.5, corner_radius=0.3,
                                fill_color=C_VUELO, fill_opacity=1, stroke_width=0).move_to(pal)
        destacado = VGroup(caja, pal).rotate(-3 * DEGREES)
        preg = VGroup(l1, destacado).arrange(DOWN, buff=0.3).move_to(UP * 4.5)
        txt = T("NO: ESTÁ HECHA PARA DOBLARSE", size=44, color=C_PRUEBA, weight=HEAVY, font=F_TIT)
        marco = RoundedRectangle(width=txt.width + 0.6, height=txt.height + 0.5, corner_radius=0.2,
                                 stroke_color=C_PRUEBA, stroke_width=8, fill_opacity=0)
        sello = VGroup(marco, txt.move_to(marco)).rotate(4 * DEGREES).move_to(DOWN * 3.3)
        self.portada(preg, avion)
        self.wait(0.4)
        self.play(flex.animate.set_value(F_PRUEBA - 0.3), rate_func=there_and_back, run_time=1.0)
        self.play(FadeIn(sello, scale=1.4), rate_func=rate_functions.ease_out_back, run_time=0.35)
        self.pulso(destacado, 1.08)
        self.hasta(0, 3.6)

        # ---------- 1. En tierra ----------
        self.dejar(preg, sello)
        self.play(self.poner_cabecera("ALAS QUE SE DOBLAN", 3), run_time=0.01)
        barra, tit, fr, dt, etq, ctl = self.textos_bloque(
            0, "En tierra", "El ala cuelga un poco", "su peso + combustible + motores",
            "LA CARGA VA", "HACIA ABAJO", C_TIERRA)
        self.cambio(flex.animate.set_value(F_TIERRA), run_time=0.9)
        self.entrar_textos(barra, C_TIERRA, tit, fr, dt)
        pesos = VGroup(*[vector([s * x, y_ala(s * x) - 0.15, 0], [s * x, y_ala(s * x) - 1.0, 0],
                                C_TIERRA, ancho=7, punta=0.22)
                         for s in (-1, 1) for x in (1.3, 2.2, 3.0)])
        self.play(LaggedStart(*[GrowArrow(p) for p in pesos], lag_ratio=0.1), run_time=0.8)
        self.play(FadeIn(etq), FadeIn(ctl, scale=0.9), run_time=0.4)
        self.wait(0.8)
        self.pulso(ctl)
        self.hasta(0, 9.0)
        self.dejar(tit, fr, dt, etq, ctl, pesos)

        # ---------- 2. En vuelo ----------
        barra, tit, fr, dt, etq, ctl = self.textos_bloque(
            1, "En vuelo", "La sustentación la empuja arriba", "a lo largo del ala; el peso va sobre todo en el fuselaje",
            "TRABAJA COMO", "UN TRAMPOLÍN", C_VUELO)
        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.15), barra.animate.set_fill(C_VUELO))
        self.play(FadeIn(fr, shift=UP * 0.2), FadeIn(dt), run_time=0.4)
        flex_v = F_VUELO

        def sust():
            return VGroup(*[vector([s * x, y_ala(s * x) + 0.15, 0],
                                   [s * x, y_ala(s * x) + 0.15 + 0.75, 0], C_VUELO, ancho=7,
                                   punta=0.22)
                            for s in (-1, 1) for x in (0.8, 1.55, 2.3, 3.0)])
        flechas = always_redraw(sust)
        peso = vector([0, Y_AVION - 0.7, 0], [0, Y_AVION - 2.0, 0], C_TIERRA, ancho=10, punta=0.3)
        self.play(FadeIn(flechas), GrowArrow(peso), run_time=0.5)
        self.play(flex.animate.set_value(flex_v), run_time=1.4)
        self.play(FadeIn(etq), FadeIn(ctl, scale=0.9), run_time=0.4)
        self.wait(0.6)
        self.play(flex.animate.set_value(flex_v + 0.12), rate_func=there_and_back, run_time=0.9)
        self.wait(0.5)
        self.pulso(ctl)
        self.hasta(0, 15.0)
        self.dejar(tit, fr, dt, etq, ctl, flechas, peso)

        # ---------- 3. La prueba ----------
        barra, tit, fr, dt, etq, ctl = self.textos_bloque(
            2, "La prueba", "Hasta 1,5 veces lo peor esperado", "787, 2010: las puntas subieron unos 7,6 m",
            "DOBLARSE NO ES", "FALLAR", C_PRUEBA)
        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.15), barra.animate.set_fill(C_PRUEBA))
        self.play(FadeIn(fr, shift=UP * 0.2), FadeIn(dt), run_time=0.4)
        self.play(flex.animate.set_value(F_PRUEBA), run_time=1.6)
        _, f = avion_frontal_flexible(F_PRUEBA)
        y0 = ESC * (-0.15 + 0.18) + Y_AVION          # punta del ala sin doblar
        y1 = ESC * f(3.75) + Y_AVION
        xt = ESC * 3.75
        cota = VGroup(DashedLine([0.9, y0, 0], [xt + 0.15, y0, 0], dash_length=0.1,
                                 color=C_PRUEBA, stroke_width=3),
                      DoubleArrow([xt, y0, 0], [xt, y1 + 0.05, 0], color=C_PRUEBA, buff=0,
                                  stroke_width=5, tip_length=0.18))
        e = self.etiqueta("≈ 7,6 m", C_PRUEBA, [xt - 0.2, y1 + 0.55, 0], size=32)
        self.play(Create(cota), FadeIn(e), run_time=0.5)
        self.play(FadeIn(etq), FadeIn(ctl, scale=0.9), run_time=0.4)
        self.wait(0.8)
        self.pulso(e, 1.15)
        self.wait(0.6)
        self.pulso(ctl)
        self.hasta(0, 21.5)
        self.dejar(tit, fr, dt, etq, ctl, cota, e, self.tema, self.barras)

        # ---------- Cierre (vuelve a la portada) ----------
        c1 = T("¿Lo has visto desde", size=58, weight=HEAVY, font=F_TIT)
        c2 = T("la ventanilla?", size=58, color=C_VUELO, weight=HEAVY, font=F_TIT)
        cierre = VGroup(c1, c2).arrange(DOWN, buff=0.18).move_to(UP * 4.5)
        nota = T("Flexión a escala del ensayo; en vuelo es bastante menor", size=28,
                 color=TEXTO_SEC, weight=MEDIUM).move_to(DOWN * 3.2)
        self.cambio(FadeIn(cierre, shift=DOWN * 0.3), FadeIn(nota))
        self.hasta(0, 24.4)
        self.dejar(cierre, nota)
        self.cambio(FadeIn(preg), run_time=0.3, desplazar=UP * 0.6)
        self.wait(0.3)

"""
Short 19 (texto, sin voz): ¿qué pasa si se apagan todos los motores? El avión planea.
- Sin empuje, el avión sigue volando hacia delante y abajo: cambia altura por velocidad.
- Relación de planeo de un avión de línea: del orden de 15 a 1 o más (por cada metro que baja,
  avanza unos 15). Desde 10 km de altura, unos 150 km sin viento (simplificación).
- 23-jul-1983, vuelo 143 de Air Canada (Boeing 767): se quedó sin combustible a unos 12 500 m
  y planeó hasta la antigua base de Gimli (Manitoba, Canadá); no hubo víctimas mortales.
Dibujo con la escala vertical exagerada.
Render:  manim -qh --fps 60 shorts/19_planeo/escena.py Planeo
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403
from lib.avion2d import lateral_2d  # noqa: E402

C_ALT, C_DIST, C_HIST = C_CABECEO, C_GUINADA, C_ALABEO
P0 = np.array([-3.0, 1.7, 0])       # inicio del planeo (10 km)
P1 = np.array([3.2, -2.3, 0])       # suelo (150 km)
Y_SUELO = -2.3


class Planeo(ShortBase):
    def construct(self):
        self.iniciar()
        base = lateral_2d(2.3, (0, 0))
        u = ValueTracker(0.12)                        # 0–1 a lo largo del planeo
        ang = np.arctan2(P1[1] - P0[1], P1[0] - P0[0])

        def avion():
            g = base.copy().rotate(ang * 0.35, about_point=ORIGIN)
            return g.move_to(P0 + (P1 - P0) * u.get_value() + UP * 0.25)
        av = always_redraw(avion)
        suelo = Line([-4.6, Y_SUELO, 0], [4.6, Y_SUELO, 0], color="#475569", stroke_width=6)
        senda = DashedLine(P0, P1, color=C_DIST, stroke_width=3, dash_length=0.12).set_opacity(0.7)

        def recorrido():
            p = P0 + (P1 - P0) * u.get_value()
            return VGroup(Line(P0, p, color=C_DIST, stroke_width=6),
                          DashedLine(p, [p[0], Y_SUELO, 0], color=C_ALT, stroke_width=3,
                                     dash_length=0.08))
        traza = always_redraw(recorrido)

        def lecturas():
            uu = u.get_value()
            alt = 10.0 * (1 - uu)
            dist = 150.0 * uu
            filas = VGroup()
            for nombre, txt, col in (("ALTURA", f"{alt:.1f} km".replace(".", ","), C_ALT),
                                     ("AVANZA", f"{dist:.0f} km", C_DIST)):
                filas.add(VGroup(T(nombre, size=26, color=col, weight=HEAVY),
                                 T(txt, size=40, color=col, weight=HEAVY, font=F_TIT))
                          .arrange(RIGHT, buff=0.25))
            return filas.arrange(DOWN, buff=0.15, aligned_edge=LEFT).move_to([0, -3.6, 0])
        panel = always_redraw(lecturas)
        nota = T("escala vertical exagerada", size=22, color=TEXTO_SEC, weight=MEDIUM)
        nota.move_to([2.6, Y_SUELO - 0.35, 0])

        # ---------- Gancho (portada en t = 0) ----------
        l1 = T("¿Y si se apagan", size=64, weight=HEAVY, font=F_TIT)
        pal = T("TODOS LOS MOTORES?", size=72, color=BG, weight=HEAVY, font=F_TIT)
        caja = RoundedRectangle(width=pal.width + 0.6, height=pal.height + 0.45, corner_radius=0.3,
                                fill_color=C_HIST, fill_opacity=1, stroke_width=0).move_to(pal)
        destacado = VGroup(caja, pal).rotate(-3 * DEGREES)
        preg = self.hud(VGroup(l1, destacado).arrange(DOWN, buff=0.3).move_to(UP * 4.5))
        sello = self.sello("NO SE CAE: PLANEA", C_DIST, [0, -3.6, 0], size=50)
        self.portada(suelo, senda, av, preg)
        self.wait(0.15)
        self.play(u.animate.set_value(0.26), run_time=0.8, rate_func=rate_functions.ease_in_sine)
        self.poner_sello(sello)
        self.pulso(destacado, 1.06)
        self.hasta(0, 3.4)

        # ---------- 1. Planea ----------
        self.dejar(preg, sello)
        self.play(self.poner_cabecera("SIN MOTORES", 3), run_time=0.01)
        barra, tit, fr, dt = self.bloque(0, "Planea", "Sin motores, sigue volando como un velero",
                                         C_ALT, dato="cambia altura por velocidad: baja poco a poco",
                                         resaltar=["velero"])
        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.2), barra.animate.set_fill(C_ALT),
                    u.animate.set_value(0.0), FadeIn(nota))
        self.entrar_palabras(fr)
        self.play(FadeIn(dt), run_time=0.3)
        self.add(traza, panel)
        self.sonido("whoosh_suave", -10)
        self.play(u.animate.set_value(0.3), run_time=2.6, rate_func=linear)
        self.hasta(0, 9.6)

        # ---------- 2. 15 a 1 ----------
        self.dejar(tit, fr, dt)
        barra, tit, fr, dt = self.bloque(1, "15 a 1", "Por cada metro que baja, avanza unos 15",
                                         C_DIST, dato="desde 10 km de altura: unos 150 km (sin viento)",
                                         resaltar=["15"])
        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.2), barra.animate.set_fill(C_DIST))
        self.entrar_palabras(fr)
        self.play(FadeIn(dt), run_time=0.3)
        self.play(u.animate.set_value(1.0), run_time=3.6, rate_func=linear)
        self.sonido("pop", -8)
        s1 = self.sello("≈ 150 km", C_DIST, [2.0, 0.5, 0], size=56)
        self.poner_sello(s1)
        self.hasta(0, 16.4)

        # ---------- 3. Pasó en 1983 ----------
        self.dejar(tit, fr, dt)
        barra, tit, fr, dt = self.bloque(2, "Pasó en 1983", "Un 767 sin combustible planeó hasta Gimli (Canadá)",
                                         C_HIST, dato="aterrizó sin víctimas mortales",
                                         resaltar=["planeó"])
        marca = VGroup(Dot([P1[0], Y_SUELO, 0], radius=0.1, color=C_HIST),
                       self.etiqueta("GIMLI", C_HIST, [P1[0] - 0.5, Y_SUELO + 0.5, 0], size=28))
        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.2), barra.animate.set_fill(C_HIST))
        self.entrar_palabras(fr)
        self.play(FadeIn(dt), FadeIn(marca, scale=1.3), run_time=0.4)
        self.wait(0.6)
        self.play(marca.animate.scale(1.12), rate_func=there_and_back, run_time=0.6)
        self.wait(0.3)
        self.pulso(tit, 1.06)
        self.wait(0.3)
        self.pulso(marca, 1.15)
        self.hasta(0, 22.8)

        # ---------- Cierre (vuelve a la portada) ----------
        self.dejar(tit, fr, dt, self.tema, self.barras)
        cierre = self.hud(frase_cinetica("¿Te lo imaginabas?", size=64,
                                         resaltar=["imaginabas?"], color_resalte=C_DIST)
                          .move_to(UP * 4.5))
        self.cambio(u.animate.set_value(0.2), run_time=0.4)
        self.entrar_palabras(cierre)
        self.dejar(s1, marca, panel, traza, nota)
        self.hasta(0, 25.4)
        self.dejar(cierre)
        self.cambio(FadeIn(preg), run_time=0.3, desplazar=UP * 0.6)
        self.wait(0.25)

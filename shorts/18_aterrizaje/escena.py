"""
Short 18 (texto, sin voz): ¿por qué el avión aterriza con el morro arriba? (la recogida o
"flare").
- En la aproximación baja por una senda de unos 3°: a unos 70 m/s (≈ 250 km/h, ejemplo) eso
  son unos 3,5 m/s de bajada (70 · sen 3° ≈ 3,7).
- Cerca del suelo el piloto sube el morro (recogida): el avión casi deja de bajar (del orden de
  1 m/s o menos al tocar) y toca primero con las ruedas principales, que están hechas para
  aguantar el impacto; la rueda del morro baja después. Actitud al tocar: unos pocos grados.
Simplificación: senda y ángulos exagerados en el dibujo para que se vean.
Render:  manim -qh --fps 60 shorts/18_aterrizaje/escena.py Aterrizaje
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403
from lib import avion as A  # noqa: E402
from lib.avion2d import lateral_2d  # noqa: E402

Y_PISTA = -1.6
C_BAJA, C_MORRO, C_RUEDA = C_CABECEO, C_GUINADA, C_ALABEO


def avion_base():
    v = lateral_2d(4.2, (0, 0), tren=True)
    v.shift(-v.a_pantalla(A.TREN["x_principal"], 0, A.Z_SUELO))
    return v


class Aterrizaje(ShortBase):
    def construct(self):
        self.iniciar()
        base = avion_base()
        x = ValueTracker(-2.0)
        h = ValueTracker(2.6)
        cab = ValueTracker(2.0)
        baja = ValueTracker(3.5)

        def avion():
            g = base.copy()
            g.rotate(1.8 * cab.get_value() * DEGREES, about_point=ORIGIN)   # exagerado
            return g.shift([x.get_value(), Y_PISTA + h.get_value(), 0])
        av = always_redraw(avion)
        pista = VGroup(Line([-4.6, Y_PISTA, 0], [4.6, Y_PISTA, 0], color="#475569", stroke_width=6),
                       DashedLine([-4.6, Y_PISTA - 0.25, 0], [4.6, Y_PISTA - 0.25, 0],
                                  dash_length=0.3, color="#64748B", stroke_width=3))
        senda = DashedLine([-3.6, Y_PISTA + 3.6, 0], [1.6, Y_PISTA - 0.05, 0], color=C_BAJA,
                           stroke_width=3, dash_length=0.12).set_opacity(0.6)

        def lecturas():
            filas = VGroup()
            for nombre, txt, col in (("BAJA", f"{baja.get_value():.1f} m/s".replace(".", ","), C_BAJA),
                                     ("MORRO", f"{cab.get_value():.0f}°", C_MORRO)):
                filas.add(VGroup(T(nombre, size=26, color=col, weight=HEAVY),
                                 T(txt, size=40, color=col, weight=HEAVY, font=F_TIT))
                          .arrange(RIGHT, buff=0.25))
            return filas.arrange(DOWN, buff=0.15, aligned_edge=LEFT).move_to([0, -3.5, 0])
        panel = always_redraw(lecturas)

        # ---------- Gancho (portada en t = 0) ----------
        preg = self.hud(frase_cinetica("¿Por qué aterriza con el morro arriba?", size=60,
                                       resaltar=["morro", "arriba?"], color_resalte=C_MORRO)
                        .move_to(UP * 4.6))
        x.set_value(0.8)
        h.set_value(0.05)
        cab.set_value(7)
        self.portada(pista, av, preg)
        self.wait(0.4)
        self.pulso(preg, 1.06)
        self.play(cab.animate.set_value(5), rate_func=there_and_back, run_time=1.2)
        self.hasta(0, 3.2)

        # ---------- 1. Aproximación ----------
        self.dejar(preg)
        self.play(self.poner_cabecera("EL ATERRIZAJE", 3), run_time=0.01)
        barra, tit, fr, dt = self.bloque(0, "Bajando", "Baja unos 3,5 m/s por una senda de 3°",
                                         C_BAJA, dato="a unos 250 km/h (ejemplo) · ángulos exagerados en el dibujo",
                                         resaltar=["3,5", "m/s"])
        self.add(panel)
        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.2), barra.animate.set_fill(C_BAJA),
                    x.animate.set_value(-2.0), h.animate.set_value(2.6), cab.animate.set_value(2),
                    FadeIn(senda))
        self.entrar_palabras(fr)
        self.play(FadeIn(dt), run_time=0.3)
        self.sonido("whoosh_suave", -10)
        self.play(x.animate.set_value(-0.6), h.animate.set_value(1.3), run_time=3.2, rate_func=linear)
        self.hasta(0, 9.6)

        # ---------- 2. La recogida ----------
        self.dejar(tit, fr, dt)
        barra, tit, fr, dt = self.bloque(1, "La recogida", "Sube el morro para casi dejar de bajar",
                                         C_MORRO, dato="de unos 3,5 m/s a 1 m/s o menos al tocar",
                                         resaltar=["morro"])
        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.2), barra.animate.set_fill(C_MORRO))
        self.entrar_palabras(fr)
        self.play(FadeIn(dt), run_time=0.3)
        self.sonido("subida", -10)
        self.play(x.animate.set_value(0.4), h.animate.set_value(0.25), run_time=1.6,
                  rate_func=linear)
        self.play(x.animate.set_value(1.2), h.animate.set_value(0.0), cab.animate.set_value(6),
                  baja.animate.set_value(0.8), run_time=1.8,
                  rate_func=rate_functions.ease_out_sine)
        self.sonido("golpe", -14)
        self.hasta(0, 16.0)

        # ---------- 3. Primero las ruedas principales ----------
        self.dejar(tit, fr, dt)
        barra, tit, fr, dt = self.bloque(2, "Primero atrás", "Tocan primero las ruedas principales",
                                         C_RUEDA, dato="aguantan el golpe; la rueda del morro baja después",
                                         resaltar=["principales"])
        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.2), barra.animate.set_fill(C_RUEDA))
        self.entrar_palabras(fr)
        self.play(FadeIn(dt), run_time=0.3)
        anillo = Circle(radius=0.45, stroke_color=C_RUEDA, stroke_width=5)
        anillo.move_to([x.get_value(), Y_PISTA + 0.12, 0])
        self.sonido("pop", -8)
        self.play(Create(anillo), run_time=0.4)
        self.play(anillo.animate.scale(1.2), rate_func=there_and_back, run_time=0.5)
        self.play(FadeOut(anillo), x.animate.set_value(2.2), cab.animate.set_value(0),
                  baja.animate.set_value(0.0), run_time=1.6, rate_func=rate_functions.ease_in_out_sine)
        self.sonido("golpe", -16)
        s1 = self.sello("ATERRIZAJE SUAVE", C_RUEDA, [0, 1.6, 0], size=46)
        self.poner_sello(s1)
        self.hasta(0, 22.6)

        # ---------- Cierre (vuelve a la portada) ----------
        self.dejar(tit, fr, dt, self.tema, self.barras)
        cierre = self.hud(frase_cinetica("¿Lo has notado al aterrizar?", size=60,
                                         resaltar=["aterrizar?"], color_resalte=C_MORRO)
                          .move_to(UP * 4.6))
        self.cambio(x.animate.set_value(0.8), h.animate.set_value(0.05), cab.animate.set_value(7),
                    run_time=0.8)
        self.entrar_palabras(cierre)
        self.dejar(s1, panel, senda)
        self.hasta(0, 25.2)
        self.dejar(cierre)
        self.cambio(FadeIn(preg), run_time=0.3, desplazar=UP * 0.6)
        self.wait(0.25)

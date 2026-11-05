"""
Ejemplo de pseudo-3D (no es un short para publicar): `Avion3D` gira de verdad en el espacio.
Avión genérico hecho de caras planas, proyectado en perspectiva y sombreado según la luz.
Muestra los tres giros con su superficie de mando (mismos colores que el short 01).
Render:  manim -qh --fps 30 shorts/demo_3d/escena.py Demo3D
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403

Y_AV = -0.2


class Demo3D(ShortBase):
    EFECTOS = True

    def construct(self):
        self.iniciar()
        av = Avion3D(escala=1.0)
        t = {k: ValueTracker(v) for k, v in dict(alabeo=0, cabeceo=0, guinada=0, aleron=0,
                                                   elevador=0, timon=0, azimut=-35,
                                                   elevacion=20).items()}
        dibujo = always_redraw(lambda: av.dibujar(**{k: v.get_value() for k, v in t.items()},
                                                  centro=UP * Y_AV))
        fondo = brillo(UP * Y_AV, C_CABECEO, 4.2, 0.9)
        sombra_av = sombra([0, Y_AV - 2.6, 0], 5.5, opacidad=0.4)
        titulo = self.hud(frase_cinetica("Pseudo-3D: el avión gira de verdad", size=54,
                                         resaltar=["3D:", "verdad"], color_resalte=C_GUINADA)
                          .move_to(UP * 4.7))
        self.portada(fondo, sombra_av, dibujo, titulo)
        self.wait(0.3)
        self.sonido("whoosh_suave", -8)
        self.play(t["azimut"].animate.set_value(-35 + 360), run_time=4.0,
                  rate_func=rate_functions.ease_in_out_sine)

        def giro(nombre, color, mando, eje, ang, defl, frase):
            barra_txt = self.hud(T(nombre, size=96, color=color, weight=HEAVY, font=F_TIT)
                                 .move_to(UP * 5.2))
            fr = self.hud(frase_cinetica(frase, size=44, weight=BOLD, font=F_TXT)
                          .next_to(barra_txt, DOWN, buff=0.3))
            self.cambio(FadeIn(barra_txt, shift=DOWN * 0.3, scale=1.2))
            self.entrar_palabras(fr)
            self.sonido("subida", -10)
            self.play(t[mando].animate.set_value(defl), run_time=0.5)
            self.play(t[eje].animate.set_value(ang), run_time=1.4,
                      rate_func=rate_functions.ease_in_out_sine)
            self.play(t[mando].animate.set_value(-defl), run_time=0.5)
            self.play(t[eje].animate.set_value(0), run_time=1.2,
                      rate_func=rate_functions.ease_in_out_sine)
            self.play(t[mando].animate.set_value(0), run_time=0.4)
            self.dejar(barra_txt, fr)

        self.dejar(titulo)
        giro("Alabeo", C_ALABEO, "aleron", "alabeo", 35, 20, "Los alerones lo inclinan")
        giro("Cabeceo", C_CABECEO, "elevador", "cabeceo", 20, 20, "El elevador sube el morro")
        giro("Guiñada", C_GUINADA, "timon", "guinada", 30, 25, "El timón gira el morro")
        self.cambio(FadeIn(titulo))
        self.play(t["azimut"].animate.set_value(-35 + 360 + 40), t["elevacion"].animate.set_value(30),
                  run_time=1.5)
        self.wait(0.3)

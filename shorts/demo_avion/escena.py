"""
Demo del avión refinado (no es un short para publicar): la misma geometría (lib/avion.py) en
3D con iluminación real (pyrender por software) y en 2D vectorial (lib/avion2d.py).
Render:  manim -qh --fps 30 shorts/demo_avion/escena.py DemoAvion
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403
from lib.avion import Avion3DReal  # noqa: E402
from lib.avion2d import capa_3d, lateral_2d, superior_2d, frontal_2d  # noqa: E402

Y_AV = -0.3


class DemoAvion(ShortBase):
    def construct(self):
        self.iniciar()
        r = Avion3DReal(1080, 1080, 2, campo=38)
        t = {k: ValueTracker(v) for k, v in dict(alabeo=0, cabeceo=0, guinada=0, aleron=0,
                                                   elevador=0, timon=0, azimut=-35,
                                                   elevacion=16, campo=38).items()}
        mirar_x = ValueTracker(0.0)

        capa = capa_3d(r, 9.0, (0, Y_AV), mirar=lambda: (mirar_x.get_value(), 0.0, 0.0), **t)
        fondo = brillo(UP * Y_AV, C_CABECEO, 4.4, 1.0)
        titulo = self.hud(frase_cinetica("Un avión 3D de verdad", size=58,
                                         resaltar=["3D"], color_resalte=C_GUINADA)
                          .move_to(UP * 4.9))
        self.portada(fondo, capa, titulo)
        self.wait(0.3)
        self.sonido("whoosh_suave", -8)
        self.play(t["azimut"].animate.set_value(-35 + 360), run_time=4.5,
                  rate_func=rate_functions.ease_in_out_sine)
        # primer plano de la cabina: se ve de los dos lados
        self.dejar(titulo)
        sub = self.hud(frase_cinetica("La cabina, de los dos lados", size=50).move_to(UP * 4.9))
        self.cambio(FadeIn(sub, shift=DOWN * 0.2))
        self.sonido("whoosh_suave", -8)
        self.play(t["campo"].animate.set_value(13), mirar_x.animate.set_value(13.0),
                  t["azimut"].animate.set_value(-35 + 360 - 15), run_time=1.4)
        self.play(t["azimut"].animate.set_value(-35 + 360 + 75), run_time=2.6,
                  rate_func=rate_functions.ease_in_out_sine)
        self.play(t["campo"].animate.set_value(38), mirar_x.animate.set_value(0.0),
                  t["azimut"].animate.set_value(-35 + 360), run_time=1.3)

        def giro(nombre, color, mando, eje, ang, defl, frase):
            tit = self.hud(T(nombre, size=96, color=color, weight=HEAVY, font=F_TIT)
                           .move_to(UP * 5.2))
            fr = self.hud(frase_cinetica(frase, size=44, weight=BOLD, font=F_TXT)
                          .next_to(tit, DOWN, buff=0.3))
            self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.2))
            self.entrar_palabras(fr)
            self.sonido("subida", -10)
            self.play(t[mando].animate.set_value(defl), run_time=0.4)
            self.play(t[eje].animate.set_value(ang), run_time=1.2,
                      rate_func=rate_functions.ease_in_out_sine)
            self.play(t[mando].animate.set_value(-defl), t[eje].animate.set_value(0),
                      run_time=1.2, rate_func=rate_functions.ease_in_out_sine)
            self.play(t[mando].animate.set_value(0), run_time=0.3)
            self.dejar(tit, fr)

        self.dejar(sub)
        giro("Alabeo", C_ALABEO, "aleron", "alabeo", 30, 18, "Los alerones lo inclinan")
        giro("Cabeceo", C_CABECEO, "elevador", "cabeceo", 15, 18, "El elevador sube el morro")
        giro("Guiñada", C_GUINADA, "timon", "guinada", 25, 22, "El timón gira el morro")

        # la misma geometría en 2D vectorial
        tit2 = self.hud(frase_cinetica("El mismo avión, en 2D", size=58, resaltar=["2D"],
                                       color_resalte=C_CABECEO).move_to(UP * 5.2))
        lat = lateral_2d(8.2, (0, 2.3))
        sup = superior_2d(5.6, (-0.0, -2.3))
        self.cambio(FadeIn(tit2), FadeOut(capa), FadeIn(lat, shift=LEFT * 0.5))
        self.play(FadeIn(sup, shift=UP * 0.4), run_time=0.6)
        self.wait(1.6)
        fr = frontal_2d(8.2, (0, -2.0))
        self.play(FadeOut(sup), FadeIn(fr, shift=UP * 0.3), run_time=0.6)
        self.wait(1.6)

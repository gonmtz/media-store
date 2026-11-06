"""
Short 15 (texto, sin voz): ¿cómo gira un avión? (viraje coordinado), con el avión 3D.
- Para girar, el piloto inclina el avión con los alerones (alabeo).
- La sustentación es perpendicular a las alas: al inclinarse, una parte tira hacia el centro de
  la curva y es la que hace girar al avión. La otra parte sigue sosteniendo el peso.
- El timón no es lo que hace girar: coordina el giro (evita que el avión derrape). Con el
  elevador se tira un poco para no perder altura (hace falta más sustentación total).
Simplificación: no se dibujan la resistencia ni el empuje.
Render:  manim -qh --fps 30 shorts/15_giro/escena.py Giro
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403
from lib import avion as A  # noqa: E402
from lib.avion2d import capa_3d  # noqa: E402

Y_AV = -0.4
C_SUST, C_HOR = C_CABECEO, C_GUINADA


class Giro(ShortBase):
    def construct(self):
        self.iniciar()
        r = A.Avion3DReal(1080, 1080, 2, campo=38, colores_mando=True)
        t = {k: ValueTracker(v) for k, v in dict(alabeo=28, aleron=0, guinada=0, timon=0,
                                                   elevador=0, azimut=180, elevacion=14,
                                                   campo=38).items()}
        capa = capa_3d(r, 9.0, (0, Y_AV), **t)
        fondo = brillo(UP * Y_AV, C_CABECEO, 4.4, 0.9)

        def a_cuerpo_mundo(w):
            """Vector del mundo → ejes del avión (para proyectar flechas fijas en el mundo)."""
            rot = A.Avion3DReal._rot
            R = (rot(np.array([0, 0, 1.0]), np.radians(-t["guinada"].get_value()))
                 @ rot(np.array([1.0, 0, 0]), np.radians(t["alabeo"].get_value())))
            return R.T @ np.asarray(w, float)

        L = 13.0    # largo de la flecha de sustentación (m en el dibujo)

        def fuerzas():
            phi = np.radians(t["alabeo"].get_value())
            o = np.array([0, 0, 1.0])
            sust = o + np.array([0, 0, L])                         # en ejes del avión
            vert = o + a_cuerpo_mundo([0, 0, L * np.cos(phi)])
            hor = o + a_cuerpo_mundo([0, -L * np.sin(phi), 0])     # hacia la derecha (−y)
            p = capa.a_pantalla([o, sust, vert, hor])
            g = VGroup(vector(p[0], p[1], C_SUST, ancho=10, punta=0.3))
            if abs(phi) > np.radians(4):
                g.add(DashedLine(p[1], p[2], color=TEXTO_SEC, stroke_width=2, dash_length=0.08),
                      vector(p[0], p[3], C_HOR, ancho=9, punta=0.28))
            return g

        # ---------- Gancho (portada en t = 0) ----------
        preg = self.hud(frase_cinetica("¿Cómo gira un avión?", size=66,
                                       resaltar=["gira"], color_resalte=C_GUINADA)
                        .move_to(UP * 4.7))
        sello = self.sello("NO ES CON EL TIMÓN", C_ALABEO, DOWN * 4.3, size=48)
        self.portada(fondo, capa, preg)
        self.wait(0.3)
        self.sonido("whoosh_suave", -10)
        self.play(t["guinada"].animate.set_value(25), run_time=1.2,
                  rate_func=rate_functions.ease_in_out_sine)
        self.poner_sello(sello)
        self.pulso(preg, 1.06)
        self.hasta(0, 3.4)

        # ---------- 1. Se inclina ----------
        self.dejar(preg, sello)
        self.play(self.poner_cabecera("CÓMO GIRA UN AVIÓN", 3), run_time=0.01)
        barra, tit, fr, dt = self.bloque(0, "Se inclina", "Los alerones lo inclinan hacia el giro",
                                         C_ALABEO, dato="un alerón sube y el otro baja",
                                         resaltar=["alerones"])
        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.2), barra.animate.set_fill(C_ALABEO),
                    t["alabeo"].animate.set_value(0), t["guinada"].animate.set_value(0),
                    run_time=0.8)
        self.entrar_palabras(fr)
        self.play(FadeIn(dt), run_time=0.3)
        self.sonido("subida", -10)
        self.play(t["aleron"].animate.set_value(18), run_time=0.4)
        self.play(t["alabeo"].animate.set_value(30), run_time=1.6,
                  rate_func=rate_functions.ease_in_out_sine)
        self.play(t["aleron"].animate.set_value(0), run_time=0.4)
        self.wait(0.8)
        self.hasta(0, 9.6)

        # ---------- 2. La sustentación tira hacia un lado ----------
        self.dejar(tit, fr, dt)
        barra, tit, fr, dt = self.bloque(1, "La clave", "Inclinada, la sustentación también tira hacia el lado",
                                         C_SUST, dato="esa parte es la que lo hace girar",
                                         resaltar=["tira"])
        flechas = always_redraw(fuerzas)
        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.2), barra.animate.set_fill(C_SUST))
        self.entrar_palabras(fr)
        self.play(FadeIn(dt), FadeIn(flechas), run_time=0.4)
        e1 = self.etiqueta("SUSTENTACIÓN", C_SUST, ORIGIN, size=26)
        e2 = self.etiqueta("TIRA HACIA EL CENTRO DE LA CURVA", C_HOR, ORIGIN, size=24)
        p = capa.a_pantalla([[0, 0, 1 + L], a_cuerpo_mundo([0, -L * np.sin(np.radians(30)), 0])
                             + np.array([0, 0, 1.0])])
        e1.next_to(p[0], UP, buff=0.15)
        e2.next_to(p[1], DOWN, buff=0.25).shift(LEFT * 0.6)
        self.sonido("pop", -8)
        self.play(FadeIn(e1), run_time=0.3)
        self.sonido("pop", -8)
        self.play(FadeIn(e2), run_time=0.3)
        self.play(e2.animate.scale(1.08), rate_func=there_and_back, run_time=0.6)
        self.wait(0.4)
        self.play(t["alabeo"].animate.set_value(34), rate_func=there_and_back, run_time=1.1)
        self.hasta(0, 16.4)

        # ---------- 3. Y gira ----------
        self.dejar(tit, fr, dt, flechas, e1, e2)
        barra, tit, fr, dt = self.bloque(2, "Y gira", "El timón solo coordina el giro",
                                         C_GUINADA, dato="y el elevador tira un poco para no perder altura",
                                         resaltar=["coordina"])
        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.2), barra.animate.set_fill(C_GUINADA),
                    t["azimut"].animate.set_value(150), t["elevacion"].animate.set_value(30))
        self.entrar_palabras(fr)
        self.play(FadeIn(dt), run_time=0.3)
        self.sonido("whoosh_suave", -10)
        self.play(t["guinada"].animate.set_value(70), t["timon"].animate.set_value(6),
                  t["elevador"].animate.set_value(6), run_time=3.0, rate_func=linear)
        self.play(t["timon"].animate.set_value(0), t["elevador"].animate.set_value(0),
                  run_time=0.4)
        self.hasta(0, 22.8)

        # ---------- Cierre (vuelve a la portada) ----------
        self.dejar(tit, fr, dt, self.tema, self.barras)
        cierre = self.hud(frase_cinetica("¿Lo habías notado en un viraje?", size=58,
                                         resaltar=["viraje?"], color_resalte=C_GUINADA)
                          .move_to(UP * 4.7))
        self.cambio(t["azimut"].animate.set_value(180), t["elevacion"].animate.set_value(14),
                    t["guinada"].animate.set_value(0), t["alabeo"].animate.set_value(28),
                    run_time=1.0)
        self.entrar_palabras(cierre)
        self.hasta(0, 25.4)
        self.dejar(cierre)
        self.cambio(FadeIn(preg), run_time=0.3, desplazar=UP * 0.6)
        self.wait(0.25)

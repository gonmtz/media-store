"""
Short 20 (texto, sin voz): ¿por qué las alas forman una V? (diedro), con el avión 3D de frente.
- Diedro: las alas suben de la raíz a la punta. En muchos aviones de línea, unos 5-7° (el modelo
  usa 5,5°).
- Si una ráfaga inclina el avión, este resbala hacia el ala baja (el aire le llega un poco de
  lado). Por la V, el ala baja recibe ese aire con más ángulo de ataque y sustenta más que la
  alta: aparece un momento que lo devuelve hacia el nivel (estabilidad lateral).
Simplificación: solo se dibujan las sustentaciones de cada ala; la flecha y la posición del ala
también influyen.
Render:  manim -qh --fps 30 shorts/20_diedro/escena.py Diedro
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403
from lib import avion as A  # noqa: E402
from lib.avion2d import capa_3d  # noqa: E402

Y_AV = -0.5
C_V, C_RAFAGA, C_SUST = C_GUINADA, C_ALABEO, C_CABECEO
YY = 10.0                      # m desde el eje: donde se dibujan las sustentaciones


class Diedro(ShortBase):
    def construct(self):
        self.iniciar()
        r = A.Avion3DReal(1080, 1080, 2, campo=40)
        t = {k: ValueTracker(v) for k, v in dict(alabeo=0, azimut=0, elevacion=2,
                                                   campo=40).items()}
        capa = capa_3d(r, 9.2, (0, Y_AV), **t)
        fondo = brillo(UP * Y_AV, C_V, 4.4, 0.9)

        # líneas de la V (sobre el borde de ataque de cada ala) y referencia horizontal
        v_on = ValueTracker(0.0)

        def lineas_v():
            g = VGroup()
            a = v_on.get_value()
            if a < 0.01:
                return g
            for s in (1, -1):
                p0 = A.punto_ala(A.ALA["y_raiz"] + 0.3, s, 0.15, 0.25)
                p1 = A.punto_ala(A.ALA["y_punta"], s, 0.15, 0.25)
                a0, a1 = capa.a_pantalla([p0, p1])
                d = (a1 - a0) / np.linalg.norm(a1 - a0)
                g.add(Line(a0 - d * 0.2, a1 + d * 0.5, color=C_V, stroke_width=6).set_opacity(a))
                g.add(DashedLine(a0, [a1[0] + np.sign(d[0]) * 0.5, a0[1], 0], color=TEXTO_SEC,
                                 stroke_width=2.5, dash_length=0.08).set_opacity(0.8 * a))
            return g
        capa_v = always_redraw(lineas_v)

        # sustentación de cada ala (perpendicular a ella, en ejes del avión)
        s_on = ValueTracker(0.0)
        extra = ValueTracker(0.0)     # 0 nivelado; 1: el ala baja sustenta más

        def sustentaciones():
            g = VGroup()
            a = s_on.get_value()
            if a < 0.01:
                return g
            pts = {s: A.punto_ala(YY, s, 0.4, 0.3) for s in (1, -1)}
            pant = {s: capa.a_pantalla([pts[s]])[0] for s in (1, -1)}
            baja = min((1, -1), key=lambda s: pant[s][1])
            for s in (1, -1):
                largo = 7.0 * (1 + (0.45 if s == baja else -0.25) * extra.get_value())
                p0, p1 = capa.a_pantalla([pts[s], pts[s] + np.array([0, 0, largo])])
                g.add(vector(p0, p1, C_SUST, ancho=9, punta=0.26).set_opacity(a))
            return g
        capa_s = always_redraw(sustentaciones)

        # ráfaga que sube bajo un ala
        raf_on = ValueTracker(0.0)

        def rafaga():
            g = VGroup()
            a = raf_on.get_value()
            if a < 0.01:
                return g
            x0 = capa.a_pantalla([A.punto_ala(13.0, -1, 0.4)])[0][0]
            for k, dx in enumerate((-0.45, 0.0, 0.45)):
                y0 = Y_AV - 2.6 + 0.9 * a
                g.add(Arrow([x0 + dx, y0, 0], [x0 + dx, y0 + 1.1, 0], buff=0, color=C_RAFAGA,
                            stroke_width=6, max_tip_length_to_length_ratio=0.3).set_opacity(a))
            return g
        capa_r = always_redraw(rafaga)

        # ---------- Gancho (portada en t = 0) ----------
        preg = self.hud(frase_cinetica("¿Por qué las alas forman una V?", size=62,
                                       resaltar=["V?"], color_resalte=C_V).move_to(UP * 4.7))
        v_on.set_value(1.0)
        self.portada(fondo, capa, capa_v, preg)
        self.wait(0.4)
        self.pulso(preg, 1.06)
        self.play(t["alabeo"].animate.set_value(6), rate_func=there_and_back, run_time=1.4)
        self.hasta(0, 3.2)

        # ---------- 1. El diedro ----------
        self.dejar(preg)
        self.play(self.poner_cabecera("EL DIEDRO", 3), run_time=0.01)
        barra, tit, fr, dt = self.bloque(0, "La V", "Las alas suben de la raíz a la punta",
                                         C_V, dato="en muchos aviones de línea, unos 5-7°",
                                         resaltar=["suben"])
        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.2), barra.animate.set_fill(C_V))
        self.entrar_palabras(fr)
        self.play(FadeIn(dt), run_time=0.3)
        e1 = self.etiqueta("≈ 5°", C_V, capa.a_pantalla([A.punto_ala(15.5, -1, 0.15)])[0]
                           + UP * 0.55, size=30)
        self.sonido("pop", -8)
        self.play(FadeIn(e1, scale=1.3), run_time=0.4)
        self.play(v_on.animate.set_value(0.5), rate_func=there_and_back, run_time=1.0)
        self.pulso(e1, 1.25)
        self.play(t["elevacion"].animate.set_value(7), rate_func=there_and_back, run_time=1.2)
        self.hasta(0, 9.6)

        # ---------- 2. Una ráfaga ----------
        self.dejar(tit, fr, dt, e1)
        barra, tit, fr, dt = self.bloque(1, "Una ráfaga", "Lo inclina y resbala hacia el ala baja",
                                         C_RAFAGA, dato="resbalar: el aire le llega un poco de lado",
                                         resaltar=["ráfaga", "resbala"])
        self.add(capa_r)
        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.2), barra.animate.set_fill(C_RAFAGA),
                    v_on.animate.set_value(0.0))
        self.entrar_palabras(fr)
        self.play(FadeIn(dt), run_time=0.3)
        self.sonido("whoosh_suave", -10)
        self.play(raf_on.animate.set_value(1.0), run_time=0.5)
        self.play(t["alabeo"].animate.set_value(-20), raf_on.animate.set_value(0.0),
                  run_time=1.6, rate_func=rate_functions.ease_out_sine)
        self.play(t["alabeo"].animate.set_value(-16), rate_func=there_and_back, run_time=1.6)
        self.hasta(0, 16.0)

        # ---------- 3. Se endereza ----------
        self.dejar(tit, fr, dt)
        barra, tit, fr, dt = self.bloque(2, "Se endereza", "El ala baja ataca el aire con más ángulo y sustenta más",
                                         C_SUST, dato="simplificado: solo se dibuja la sustentación",
                                         resaltar=["sustenta", "más"])
        self.add(capa_s)
        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.2), barra.animate.set_fill(C_SUST),
                    s_on.animate.set_value(1.0))
        self.entrar_palabras(fr)
        self.play(FadeIn(dt), run_time=0.3)
        self.sonido("subida", -10)
        self.play(extra.animate.set_value(1.0), run_time=0.7)
        self.play(t["alabeo"].animate.set_value(0), extra.animate.set_value(0.0), run_time=2.2,
                  rate_func=rate_functions.ease_in_out_sine)
        s1 = self.sello("ESTABILIDAD", C_SUST, [0, -3.4, 0], size=50)
        self.poner_sello(s1)
        self.hasta(0, 22.6)

        # ---------- Cierre (vuelve a la portada) ----------
        self.dejar(tit, fr, dt, self.tema, self.barras)
        cierre = self.hud(frase_cinetica("¿Te habías fijado en la V?", size=62,
                                         resaltar=["V?"], color_resalte=C_V).move_to(UP * 4.7))
        self.cambio(s_on.animate.set_value(0.0), v_on.animate.set_value(1.0), run_time=0.8)
        self.entrar_palabras(cierre)
        self.dejar(s1)
        self.hasta(0, 25.2)
        self.dejar(cierre)
        self.cambio(FadeIn(preg), run_time=0.3, desplazar=UP * 0.6)
        self.wait(0.25)

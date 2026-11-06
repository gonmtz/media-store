"""
Short 10 (texto, sin voz): ¿por qué el ala se dobla hacia arriba? — con el avión 3D.
- En tierra el ala cuelga un poco por su peso, el del combustible y el de los motores.
- En vuelo, la sustentación se reparte a lo largo del ala y el peso está sobre todo en el
  fuselaje: el ala trabaja como una viga en voladizo y la punta sube.
- Prueba de carga última del 787 (Boeing, 28-mar-2010): 150 % de las fuerzas más extremas
  esperadas en servicio; las alas subieron unos 7,6 m (25 ft) con una semiala de unos 30 m.
Avión genérico de 17 m de semiala: la flexión del ensayo se dibuja a escala (7,6/30 ≈ 25 %
de la semiala → 4,3 m). Las flexiones en tierra y en vuelo son ilustrativas.
Render:  manim -qh --fps 30 shorts/10_ala_dobla/escena.py AlaDobla
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403
from lib import avion as A  # noqa: E402
from lib.avion2d import capa_3d  # noqa: E402

C_TIERRA, C_VUELO, C_PRUEBA = C_CABECEO, C_ALABEO, C_GUINADA
F_TIERRA, F_VUELO, F_PRUEBA = -0.35, 1.4, 4.3
Y_AV = -0.2


class AlaDobla(ShortBase):
    def construct(self):
        self.iniciar()
        r = A.Avion3DReal(1080, 1080, 2, campo=36, colores_mando=False)
        t = {k: ValueTracker(v) for k, v in dict(flex=F_PRUEBA, azimut=-14, elevacion=6,
                                                   campo=36).items()}
        tren = {"v": False}
        capa = capa_3d(r, 9.0, (0, Y_AV), tren=lambda: tren["v"], **t)
        fondo = brillo(UP * Y_AV, C_VUELO, 4.4, 0.9)

        def flechas(ys, desde, hasta, color, ancho=8):
            def f():
                g = VGroup()
                for s in (1, -1):
                    for yy in ys:
                        p0 = A.punto_ala(yy, s, 0.45, desde)
                        p1 = A.punto_ala(yy, s, 0.45, hasta)
                        a, b = capa.a_pantalla([p0, p1], en_ala=True)
                        g.add(vector(a, b, color, ancho=ancho, punta=0.2))
                return g
            return always_redraw(f)

        # ---------- Gancho (portada en t = 0) ----------
        l1 = T("¿El ala se está", size=64, weight=HEAVY, font=F_TIT)
        pal = T("ROMPIENDO?", size=104, color=BG, weight=HEAVY, font=F_TIT)
        caja = RoundedRectangle(width=pal.width + 0.7, height=pal.height + 0.5, corner_radius=0.3,
                                fill_color=C_VUELO, fill_opacity=1, stroke_width=0).move_to(pal)
        destacado = VGroup(caja, pal).rotate(-3 * DEGREES)
        preg = self.hud(VGroup(l1, destacado).arrange(DOWN, buff=0.3).move_to(UP * 4.6))
        sello = self.sello("NO: ESTÁ HECHA PARA DOBLARSE", C_PRUEBA, DOWN * 4.3, size=44)
        self.portada(fondo, capa, preg)
        self.wait(0.3)
        self.sonido("whoosh_suave", -12)
        self.play(t["flex"].animate.set_value(F_PRUEBA - 1.4), rate_func=there_and_back,
                  run_time=1.0)
        self.poner_sello(sello)
        self.pulso(destacado, 1.08)
        self.hasta(0, 3.4)

        # ---------- 1. En tierra ----------
        self.dejar(preg, sello)
        self.play(self.poner_cabecera("ALAS QUE SE DOBLAN", 3), run_time=0.01)
        barra, tit, fr, dt = self.bloque(0, "En tierra", "El ala cuelga por su propio peso",
                                         C_TIERRA, dato="ala + combustible + motores",
                                         resaltar=["cuelga"])
        tren["v"] = True
        suelo = always_redraw(lambda: Line(
            capa.a_pantalla([[0, 30, A.Z_SUELO]])[0] * [1, 1, 0] + LEFT * 0,
            capa.a_pantalla([[0, -30, A.Z_SUELO]])[0], color="#334155", stroke_width=4))
        self.cambio(t["flex"].animate.set_value(F_TIERRA), t["azimut"].animate.set_value(0),
                    t["elevacion"].animate.set_value(3), FadeIn(suelo),
                    FadeIn(tit, shift=DOWN * 0.3, scale=1.2), barra.animate.set_fill(C_TIERRA),
                    run_time=0.9)
        self.entrar_palabras(fr)
        self.play(FadeIn(dt), run_time=0.3)
        pesos = flechas((7.0, 11.0, 15.0), -0.3, -2.8, C_TIERRA, 7)
        self.sonido("tic", -8)
        self.play(FadeIn(pesos), run_time=0.5)
        self.play(t["flex"].animate.set_value(F_TIERRA - 0.25), rate_func=there_and_back,
                  run_time=1.0)
        self.pulso(pesos, 1.12)
        self.hasta(0, 9.2)

        # ---------- 2. En vuelo ----------
        self.dejar(tit, fr, dt, pesos, suelo)
        barra, tit, fr, dt = self.bloque(1, "En vuelo", "La sustentación empuja el ala hacia arriba",
                                         C_VUELO, dato="a lo largo del ala; el peso va sobre todo en el fuselaje",
                                         resaltar=["arriba"])
        sust = flechas((4.5, 8.0, 11.5, 15.0), 0.35, 3.2, C_VUELO, 7)

        def flecha_peso():
            a, b = capa.a_pantalla([[0, 0, -2.3], [0, 0, -7.0]])
            return vector(a, b, C_TIERRA, ancho=10, punta=0.28)
        peso = always_redraw(flecha_peso)
        tren["v"] = False
        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.2), barra.animate.set_fill(C_VUELO))
        self.entrar_palabras(fr)
        self.play(FadeIn(dt), run_time=0.3)
        self.play(FadeIn(sust), FadeIn(peso), run_time=0.4)
        self.sonido("subida", -8)
        self.play(t["flex"].animate.set_value(F_VUELO), run_time=1.3)
        self.play(t["flex"].animate.set_value(F_VUELO + 0.6), rate_func=there_and_back,
                  run_time=1.0)
        self.wait(0.5)
        self.hasta(0, 15.4)

        # ---------- 3. La prueba ----------
        self.dejar(tit, fr, dt, sust, peso)
        barra, tit, fr, dt = self.bloque(2, "La prueba", "Hasta 1,5 veces lo peor esperado",
                                         C_PRUEBA, dato="Boeing 787, 2010 · dibujado a escala",
                                         resaltar=["1,5"])
        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.2), barra.animate.set_fill(C_PRUEBA),
                    t["azimut"].animate.set_value(-10), t["elevacion"].animate.set_value(4),
                    run_time=0.7)
        self.entrar_palabras(fr)
        self.play(FadeIn(dt), run_time=0.3)
        self.sonido("subida", -6)
        self.play(t["flex"].animate.set_value(F_PRUEBA), run_time=1.4)
        punta = A.punto_ala(A.ALA["y_punta"], -1, 0.6)

        def cota():
            a = capa.a_pantalla([punta])[0]
            b = capa.a_pantalla([punta], en_ala=True)[0]
            linea = DashedLine(a + RIGHT * 1.4, a + LEFT * 0.25, dash_length=0.08,
                               color=C_PRUEBA, stroke_width=3)
            fl = DoubleArrow(a, b, color=C_PRUEBA, buff=0, stroke_width=5, tip_length=0.16)
            return VGroup(linea, fl)
        cot = always_redraw(cota)
        e = self.etiqueta("≈ 7,6 m en un 787", C_PRUEBA, ORIGIN, size=30)
        self.play(FadeIn(cot), run_time=0.4)
        self.sonido("pop", -8)
        b = capa.a_pantalla([punta], en_ala=True)[0]
        e.next_to(b, UP, buff=0.25).shift(RIGHT * 1.9)
        self.play(FadeIn(e, scale=1.2), run_time=0.3)
        self.wait(0.6)
        sello2 = self.sello("DOBLARSE NO ES FALLAR", C_PRUEBA, DOWN * 4.4, size=46)
        self.poner_sello(sello2)
        self.wait(0.8)
        self.pulso(sello2, 1.06)
        self.hasta(0, 22.6)

        # ---------- Cierre (vuelve a la portada) ----------
        self.dejar(tit, fr, dt, cot, e, sello2, self.tema, self.barras)
        cierre = self.hud(frase_cinetica("¿Lo has visto desde la ventanilla?", size=58,
                                         resaltar=["ventanilla?"], color_resalte=C_VUELO)
                          .move_to(UP * 4.6))
        nota = self.hud(T("Flexión a escala del ensayo; en vuelo es bastante menor", size=28,
                          color=TEXTO_SEC, weight=MEDIUM).move_to(DOWN * 4.3))
        self.cambio(FadeIn(nota), t["azimut"].animate.set_value(-14),
                    t["elevacion"].animate.set_value(6))
        self.entrar_palabras(cierre)
        self.hasta(0, 25.0)
        self.dejar(cierre, nota)
        self.cambio(FadeIn(preg), run_time=0.3, desplazar=UP * 0.6)
        self.wait(0.25)

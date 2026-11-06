"""
Short 09 (texto, sin voz): ¿qué significan las letras de un avión? (matrículas).
Fuentes: OACI, Anexo 7 y prefijos de nacionalidad; México: Ley de Aviación Civil, art. 44
(XA servicio al público de transporte aéreo; XB servicios a terceros y uso particular;
XC aeronaves de Estado distintas de las militares). La matrícula XA-ABC es un ejemplo.
Render:  manim -qh --fps 60 shorts/09_matriculas/escena.py Matriculas
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403
from lib import avion as A  # noqa: E402
from lib.avion2d import lateral_2d  # noqa: E402

C_PAIS, C_AVION, C_USO = C_CABECEO, C_ALABEO, C_GUINADA
PREFIJOS = [("N", "EE. UU."), ("C", "Canadá"), ("XA", "México"), ("EC", "España"),
            ("LV", "Argentina"), ("CC", "Chile"), ("HK", "Colombia"), ("PR", "Brasil"),
            ("OB", "Perú"), ("YV", "Venezuela"), ("HC", "Ecuador"), ("CX", "Uruguay")]


def avion_con_matricula():
    """Avión lateral (lib/avion2d) con la matrícula pintada en la parte trasera del fuselaje."""
    v = lateral_2d(8.6, (0.15, 0.7))
    k = 8.6 / A.L
    mat = Text("XA-ABC", font=F_TIT, weight=HEAVY, color=OSCURO).scale_to_fit_height(0.62 * k)
    mat.move_to(v.a_pantalla(28.6, 0, 0.9))
    g = VGroup(sombra([0.3, -0.75, 0], 7.0, opacidad=0.45), v, mat)
    return g, mat


def placa_grande():
    grande = T("XA-ABC", size=120, weight=HEAVY, font=F_TIT)
    caja = RoundedRectangle(width=grande.width + 0.7, height=grande.height + 0.5,
                            corner_radius=0.3, fill_color=C_GUINADA, fill_opacity=1, stroke_width=0)
    grande.set_color(BG).move_to(caja)
    return VGroup(caja, grande).rotate(-3 * DEGREES).move_to(DOWN * 2.9)


class Matriculas(ShortBase):
    def construct(self):
        self.iniciar()
        # ---------- Gancho (portada en t = 0) ----------
        preg = frase_cinetica("¿Qué significan las letras de un avión?", size=54,
                              resaltar=["letras"], color_resalte=C_GUINADA)
        preg.move_to(UP * 4.5)
        self.hud(preg)
        fondo = brillo(UP * 0.7, C_PAIS, 3.6)
        avion, mat = avion_con_matricula()
        placa = self.hud(placa_grande())
        self.portada(fondo, avion, preg, placa)
        self.wait(0.45)
        self.sonido("pop", -8)
        self.pulso(placa, 1.12)
        # la cámara se acerca a la matrícula pintada en el fuselaje
        self.dejar(placa)
        self.cambio(run_time=0.35)
        self.enfocar(mat.get_center() + DOWN * 0.05, 4.2, run_time=1.1)
        self.hasta(0, 2.7)

        # ---------- 1. La matrícula: país + avión ----------
        self.dejar(preg)
        self.play(self.poner_cabecera("MATRÍCULAS", 3), run_time=0.01)
        barra, tit, fr, dt = self.bloque(0, "Matrícula", "Es la placa del avión", C_PAIS,
                                         dato="prefijo del país + letras de cada avión")
        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.2), barra.animate.set_fill(C_PAIS))
        self.entrar_palabras(fr)
        self.play(FadeIn(dt), run_time=0.3)
        # colorear la matrícula pintada: país (XA) y avión (ABC)
        c = mat.get_center()
        e_pais = self.etiqueta("PAÍS", C_PAIS, ORIGIN, size=28).scale(0.2)
        e_pais.next_to(VGroup(*mat[0:2]), DOWN, buff=0.05).align_to(VGroup(*mat[0:2]), RIGHT)
        e_avion = self.etiqueta("ESTE AVIÓN", C_AVION, ORIGIN, size=28).scale(0.2)
        e_avion.next_to(VGroup(*mat[3:6]), DOWN, buff=0.05).align_to(VGroup(*mat[3:6]), LEFT)
        self.sonido("tic", -6)
        self.play(VGroup(*mat[0:2]).animate.set_color(C_PAIS), FadeIn(e_pais, shift=UP * 0.05),
                  run_time=0.4)
        self.sonido("tic", -6)
        self.play(VGroup(*mat[3:6]).animate.set_color(C_AVION), FadeIn(e_avion, shift=UP * 0.05),
                  run_time=0.4)
        self.wait(0.9)
        self.play(e_pais.animate.scale(1.25), rate_func=there_and_back, run_time=0.5)
        self.hasta(0, 7.4)
        self.play(FadeOut(e_pais), FadeOut(e_avion), run_time=0.25)
        self.vista_general(run_time=0.8)
        self.hasta(0, 8.4)

        # ---------- 2. Cada país, su prefijo ----------
        self.dejar(tit, fr, dt, avion, fondo)
        barra, tit, fr, dt = self.bloque(1, "Prefijos", "Cada país tiene el suyo", C_AVION,
                                         dato="los asigna la OACI (Anexo 7)")
        fichas = VGroup()
        for i, (p, pais) in enumerate(PREFIJOS):
            col = [C_PAIS, C_AVION, C_USO][i % 3]
            pr = T(p, size=64, color=col, weight=HEAVY, font=F_TIT)
            ps = T(pais, size=26, color=TEXTO, weight=SEMIBOLD)
            g = VGroup(pr, ps).arrange(DOWN, buff=0.08)
            caja = RoundedRectangle(width=2.3, height=1.3, corner_radius=0.2, fill_color=PANEL,
                                    fill_opacity=1, stroke_color=col, stroke_width=2,
                                    stroke_opacity=0.5)
            fichas.add(VGroup(caja, g.move_to(caja)))
        fichas.arrange_in_grid(rows=4, cols=3, buff=(0.22, 0.22)).move_to(DOWN * 0.6)
        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.2), barra.animate.set_fill(C_AVION))
        self.entrar_palabras(fr)
        self.play(FadeIn(dt), run_time=0.3)
        for i, f in enumerate(fichas):
            self.sonido("tic", -10, retraso=0.0)
            self.play(FadeIn(f, scale=0.7, rate_func=rate_functions.ease_out_back), run_time=0.17)
        self.wait(0.5)
        self.sonido("pop", -10)
        self.play(fichas[2].animate.scale(1.15).set_z_index(5), run_time=0.3)
        self.wait(0.9)
        self.play(fichas[2].animate.scale(1 / 1.15), run_time=0.3)
        self.hasta(0, 14.6)

        # ---------- 3. México: la segunda letra dice el uso ----------
        self.dejar(tit, fr, dt, fichas)
        barra, tit, fr, dt = self.bloque(2, "En México", "La segunda letra dice el uso", C_USO,
                                         dato="Ley de Aviación Civil, art. 44", resaltar=["uso"])
        usos = [("XA", "Aerolíneas", "transporte aéreo al público"),
                ("XB", "Privados", "uso particular y servicios a terceros"),
                ("XC", "Del Estado", "gobierno (no militares)")]
        filas = VGroup()
        for p, nom, det in usos:
            x = T(p[0], size=104, color=TEXTO_SEC, weight=HEAVY, font=F_TIT)
            y = T(p[1], size=104, color=C_USO, weight=HEAVY, font=F_TIT)
            pr = VGroup(x, y).arrange(RIGHT, buff=0.03)
            n = T(nom, size=50, weight=HEAVY, font=F_TIT)
            d = T(det, size=27, color=TEXTO_SEC, weight=MEDIUM)
            txt = VGroup(n, d).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
            filas.add(VGroup(pr, txt).arrange(RIGHT, buff=0.45))
        filas.arrange(DOWN, buff=0.6, aligned_edge=LEFT)
        if filas.width > 7.0:
            filas.scale_to_fit_width(7.0)
        filas.move_to(DOWN * 0.7)
        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.2), barra.animate.set_fill(C_USO))
        self.entrar_palabras(fr)
        self.play(FadeIn(dt), run_time=0.3)
        for f in filas:
            self.sonido("tic", -6)
            self.play(FadeIn(f, shift=RIGHT * 0.5), run_time=0.4)
            self.play(f[0][1].animate.scale(1.25), rate_func=there_and_back, run_time=0.35)
            self.wait(0.25)
        self.wait(0.9)
        self.play(Indicate(filas[0][0][1], color=C_USO, scale_factor=1.2), run_time=0.6)
        self.hasta(0, 21.0)

        # ---------- Cierre (vuelve a la portada para el bucle) ----------
        self.dejar(tit, fr, dt, filas, self.tema, self.barras)
        cierre = frase_cinetica("¿Cuál es el prefijo de tu país?", size=54,
                                resaltar=["país?"], color_resalte=C_GUINADA).move_to(UP * 4.5)
        self.hud(cierre)
        fondo2 = brillo(UP * 0.7, C_PAIS, 3.6)
        avion2, _ = avion_con_matricula()
        placa2 = self.hud(placa_grande())
        self.cambio(FadeIn(fondo2), FadeIn(avion2, shift=LEFT * 0.6), FadeIn(placa2, scale=0.9))
        self.entrar_palabras(cierre)
        self.hasta(0, 23.6)
        self.dejar(cierre)
        self.cambio(FadeIn(preg), run_time=0.3, desplazar=UP * 0.6)
        self.wait(0.25)

"""
Short 09 (texto, sin voz): ¿qué significan las letras de un avión? (matrículas).
Fuentes: OACI, Anexo 7 y prefijos de nacionalidad; México: Ley de Aviación Civil, art. 44
(XA servicio al público de transporte aéreo; XB servicios a terceros y uso particular;
XC aeronaves de Estado distintas de las militares). La matrícula XA-ABC es un ejemplo.
Render:  manim -qh --fps 30 shorts/09_matriculas/escena.py Matriculas
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403

C_PAIS, C_AVION, C_USO = C_CABECEO, C_ALABEO, C_GUINADA
PREFIJOS = [("N", "EE. UU."), ("C", "Canadá"), ("XA", "México"), ("EC", "España"),
            ("LV", "Argentina"), ("CC", "Chile"), ("HK", "Colombia"), ("PR", "Brasil"),
            ("OB", "Perú"), ("YV", "Venezuela"), ("HC", "Ecuador"), ("CX", "Uruguay")]


class Matriculas(ShortBase):
    def construct(self):
        self.iniciar()
        # ---------- Gancho (portada en t = 0) ----------
        l1 = T("¿Qué significan las", size=58, weight=HEAVY, font=F_TIT)
        l2 = T("letras de un avión?", size=58, weight=HEAVY, font=F_TIT)
        preg = VGroup(l1, l2).arrange(DOWN, buff=0.18).move_to(UP * 4.4)
        av, _, _ = avion_lateral()
        mat = matricula_lateral("XA-ABC")
        avion = VGroup(av, mat).scale(1.12).move_to(UP * 0.9)
        grande = T("XA-ABC", size=120, weight=HEAVY, font=F_TIT)
        caja = RoundedRectangle(width=grande.width + 0.7, height=grande.height + 0.5,
                                corner_radius=0.3, fill_color=C_GUINADA, fill_opacity=1,
                                stroke_width=0)
        grande.set_color(BG).move_to(caja)
        placa = VGroup(caja, grande).rotate(-3 * DEGREES).move_to(DOWN * 2.6)
        self.portada(preg, avion, placa)
        self.wait(0.5)
        self.pulso(placa, 1.12)
        self.play(avion.animate.shift(RIGHT * 0.25), rate_func=there_and_back, run_time=0.9)
        self.hasta(0, 2.6)

        # ---------- 1. La matrícula: país + avión ----------
        self.dejar(preg, placa)
        self.play(self.poner_cabecera("MATRÍCULAS", 3), run_time=0.01)
        barra, tit, fr, dt, etq, ctl = self.textos_bloque(
            0, "Matrícula", "Es la placa del avión", "prefijo del país + letras de cada avión",
            "EL PREFIJO DICE", "DE QUÉ PAÍS ES", C_PAIS)
        xa = T("XA", size=130, color=C_PAIS, weight=HEAVY, font=F_TIT)
        guion = T("–", size=130, color=TEXTO_SEC, weight=HEAVY, font=F_TIT)
        abc = T("ABC", size=130, color=C_AVION, weight=HEAVY, font=F_TIT)
        partes = VGroup(xa, guion, abc).arrange(RIGHT, buff=0.25).move_to(DOWN * 1.0)
        e_pais = self.etiqueta("PAÍS", C_PAIS, xa.get_bottom() + DOWN * 0.55, size=30)
        e_avion = self.etiqueta("ESTE AVIÓN", C_AVION, abc.get_bottom() + DOWN * 0.55, size=30)
        self.cambio(avion.animate.scale(0.8).move_to(UP * 1.75),
                    ReplacementTransform(mat.copy(), partes))
        self.entrar_textos(barra, C_PAIS, tit, fr, dt)
        self.play(FadeIn(e_pais, shift=UP * 0.2), run_time=0.35)
        self.play(FadeIn(e_avion, shift=UP * 0.2), run_time=0.35)
        self.play(FadeIn(etq), FadeIn(ctl, scale=0.9), run_time=0.4)
        self.wait(0.8)
        self.pulso(xa, 1.15)
        self.hasta(0, 8.0)
        self.dejar(tit, fr, dt, etq, ctl, partes, e_pais, e_avion, avion)

        # ---------- 2. Cada país, su prefijo ----------
        barra, tit, fr, dt, etq, ctl = self.textos_bloque(
            1, "Prefijos", "Cada país tiene el suyo", "los asigna la OACI (Anexo 7)",
            "SE ASIGNA POR", "PAÍS", C_AVION)
        fichas = VGroup()
        for i, (p, pais) in enumerate(PREFIJOS):
            col = [C_PAIS, C_AVION, C_USO][i % 3]
            pr = T(p, size=60, color=col, weight=HEAVY, font=F_TIT)
            ps = T(pais, size=26, color=TEXTO, weight=SEMIBOLD)
            g = VGroup(pr, ps).arrange(DOWN, buff=0.08)
            fondo = RoundedRectangle(width=2.3, height=1.25, corner_radius=0.2, fill_color=PANEL,
                                     fill_opacity=1, stroke_color=col, stroke_width=2,
                                     stroke_opacity=0.5)
            fichas.add(VGroup(fondo, g.move_to(fondo)))
        fichas.arrange_in_grid(rows=4, cols=3, buff=(0.22, 0.2)).move_to(DOWN * 0.15)
        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.15), barra.animate.set_fill(C_AVION))
        self.play(FadeIn(fr, shift=UP * 0.2), FadeIn(dt), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(f, scale=0.85) for f in fichas], lag_ratio=0.18),
                  run_time=2.2)
        self.wait(0.6)
        self.pulso(fichas[2], 1.12)
        self.wait(0.8)
        self.pulso(fichas[0], 1.12)
        self.hasta(0, 14.0)
        self.dejar(tit, fr, dt, fichas)

        # ---------- 3. México: la segunda letra dice el uso ----------
        barra, tit, fr, dt, etq, ctl = self.textos_bloque(
            2, "En México", "La segunda letra dice el uso", "Ley de Aviación Civil, art. 44",
            "", "", C_USO)
        usos = [("XA", "Aerolíneas", "transporte aéreo al público"),
                ("XB", "Privados", "uso particular y servicios a terceros"),
                ("XC", "Del Estado", "gobierno (no militares)")]
        filas = VGroup()
        for p, nom, det in usos:
            pr = T(p, size=96, color=C_USO, weight=HEAVY, font=F_TIT)
            n = T(nom, size=46, weight=HEAVY, font=F_TIT)
            d = T(det, size=26, color=TEXTO_SEC, weight=MEDIUM)
            txt = VGroup(n, d).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
            filas.add(VGroup(pr, txt).arrange(RIGHT, buff=0.45))
        filas.arrange(DOWN, buff=0.55, aligned_edge=LEFT)
        if filas.width > 7.0:
            filas.scale_to_fit_width(7.0)
        filas.move_to(DOWN * 0.4)
        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.15), barra.animate.set_fill(C_USO))
        self.play(FadeIn(fr, shift=UP * 0.2), FadeIn(dt), run_time=0.4)
        for f in filas:
            self.play(FadeIn(f, shift=RIGHT * 0.4), run_time=0.45)
            self.wait(0.55)
        self.wait(0.8)
        self.pulso(filas[0][0], 1.15)
        self.hasta(0, 20.0)
        self.dejar(tit, fr, dt, filas, self.tema, self.barras)

        # ---------- Cierre (vuelve a la portada para el bucle) ----------
        c1 = T("No hay dos iguales:", size=58, weight=HEAVY, font=F_TIT)
        c2 = T("¿cuál es la de tu país?", size=58, color=C_GUINADA, weight=HEAVY, font=F_TIT)
        cierre = VGroup(c1, c2).arrange(DOWN, buff=0.18).move_to(UP * 4.4)
        av2, _, _ = avion_lateral()
        avion2 = VGroup(av2, matricula_lateral("XA-ABC")).scale(1.12).move_to(UP * 0.9)
        placa2 = placa.copy()
        self.cambio(FadeIn(cierre, shift=DOWN * 0.3), FadeIn(avion2), FadeIn(placa2, scale=0.9))
        self.hasta(0, 22.6)
        self.dejar(cierre)
        self.cambio(FadeIn(preg), run_time=0.3, desplazar=UP * 0.6)
        self.wait(0.3)

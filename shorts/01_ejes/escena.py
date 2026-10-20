"""
Short 01: "Un avión solo puede girar de 3 formas" (cabeceo, alabeo, guiñada).
Render (desde la raíz del repo):
  manim -qh --fps 30 shorts/01_ejes/escena.py EjesAvion
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403


class EjesAvion(ShortBase):
    VOZ_JSON = Path(__file__).parent / "voz.json"
    SIN_SUBS_DESDE = "cierre"   # la pregunta final ya está escrita en pantalla

    def construct(self):
        self.iniciar()
        self.gancho()

        self.cabecera = T("LOS 3 GIROS DE UN AVIÓN", size=28, color=TEXTO_SEC,
                          weight=SEMIBOLD).move_to(UP * 6.85)
        self.barras = VGroup(*[RoundedRectangle(width=0.7, height=0.12, corner_radius=0.06,
                                                fill_color="#334155", fill_opacity=1,
                                                stroke_width=0) for _ in range(3)])
        self.barras.arrange(RIGHT, buff=0.15).move_to(UP * 6.4)
        self.play(FadeIn(self.cabecera, shift=DOWN * 0.2), FadeIn(self.barras), run_time=0.4)

        self.seccion_cabeceo()
        self.seccion_alabeo()
        self.seccion_guinada()
        self.cierre()

    # ---------- Gancho ----------
    def gancho(self):
        l1 = T("Un avión solo puede", size=60, weight=HEAVY, font=F_TIT)
        l2 = T("girar de", size=60, weight=HEAVY, font=F_TIT)
        num = T("3 FORMAS", size=128, color=BG, weight=HEAVY, font=F_TIT)
        caja = RoundedRectangle(width=num.width + 0.7, height=num.height + 0.55, corner_radius=0.3,
                                fill_color=C_GUINADA, fill_opacity=1, stroke_width=0).move_to(num)
        destacado = VGroup(caja, num)
        sub = T("y cada una tiene nombre", size=44, color=TEXTO_SEC, weight=MEDIUM)
        bloque = VGroup(l1, l2, destacado, sub).arrange(DOWN, buff=0.38).move_to(UP * 1.2)
        destacado.rotate(-3 * DEGREES)
        t0, d = self.voz("gancho")

        self.play(FadeIn(l1, shift=UP * 0.3), run_time=0.35)
        self.play(FadeIn(l2, shift=UP * 0.3), run_time=0.3)
        self.play(GrowFromCenter(caja), FadeIn(num, scale=1.6),
                  rate_func=rate_functions.ease_out_back, run_time=0.5)
        self.play(FadeIn(sub, shift=UP * 0.2), run_time=0.35)
        self.rellenar(t0, d, margen=-0.8)
        self.play(FadeOut(bloque, shift=UP * 0.6), run_time=0.4)

    # ---------- Bloques de texto por sección ----------
    def textos(self, idx, nombre, frase, eje, control, color):
        barra = self.barras[idx]
        tit = T(nombre, size=128, color=color, weight=HEAVY, font=F_TIT).move_to(UP * 5.2)
        fr = T(frase, size=50, weight=BOLD).next_to(tit, DOWN, buff=0.3)
        ej = T(eje, size=30, color=TEXTO_SEC, weight=MEDIUM).next_to(fr, DOWN, buff=0.18)
        etq = T("SE CONTROLA CON", size=28, color=TEXTO_SEC, weight=SEMIBOLD).move_to(DOWN * 3.6)
        ctl = pastilla(T(control, size=52, color=color, weight=HEAVY, font=F_TIT), color)
        ctl.next_to(etq, DOWN, buff=0.2)
        return barra, tit, fr, ej, etq, ctl

    def entrar(self, barra, color, avion, glow, tit, fr, ej, eje):
        self.play(barra.animate.set_fill(color), FadeIn(glow),
                  FadeIn(tit, shift=DOWN * 0.3, scale=1.15), FadeIn(avion, shift=UP * 0.4),
                  run_time=0.6)
        self.play(FadeIn(fr, shift=UP * 0.2), FadeIn(ej), GrowFromCenter(eje), run_time=0.45)

    def salir(self, *mobs):
        self.play(*[FadeOut(m, shift=LEFT * 0.6) for m in mobs], run_time=0.4)

    # ---------- 1. Cabeceo ----------
    def seccion_cabeceo(self):
        t0, d = self.voz("cabeceo")
        cg = np.array([0.1, 0.9, 0])
        avion, elevador, bis = avion_lateral()
        avion.shift(cg + LEFT * 0.1)
        bis = bis + cg + LEFT * 0.1
        barra, tit, fr, ej, etq, ctl = self.textos(0, "Cabeceo", "Sube o baja la nariz",
                                                   "giro alrededor del eje lateral",
                                                   "EL ELEVADOR", C_CABECEO)
        eje = simbolo_eje(C_CABECEO).move_to(cg)
        glow = resplandor(C_CABECEO, cg)

        self.entrar(barra, C_CABECEO, avion, glow, tit, fr, ej, eje)
        self.hasta(t0, d * 0.44)
        self.play(FadeIn(etq), FadeIn(ctl, scale=0.8),
                  Indicate(elevador, color=C_CABECEO, scale_factor=1.5), run_time=0.6)
        fantasma = avion.copy().set_opacity(0.12)
        self.add(fantasma)
        self.bring_to_front(avion, eje)
        flecha = flecha_giro(cg, 3.4, -0.1, 0.5, C_CABECEO)
        self.hasta(t0, d * 0.72)
        self.play(Rotate(elevador, -24 * DEGREES, about_point=bis), run_time=0.45)
        self.play(Rotate(avion, 14 * DEGREES, about_point=cg), Create(flecha),
                  rate_func=rate_functions.ease_in_out_cubic, run_time=1.1)
        self.rellenar(t0, d)
        self.salir(avion, fantasma, eje, flecha, glow, tit, fr, ej, etq, ctl)

    # ---------- 2. Alabeo ----------
    def seccion_alabeo(self):
        t0, d = self.voz("alabeo")
        cg = np.array([0, 0.5, 0])
        avion, a_i, a_d = avion_trasero()
        avion.scale(0.92, about_point=ORIGIN).shift(cg)
        barra, tit, fr, ej, etq, ctl = self.textos(1, "Alabeo", "Inclina las alas",
                                                   "giro alrededor del eje longitudinal",
                                                   "LOS ALERONES", C_ALABEO)
        eje = simbolo_eje(C_ALABEO).move_to(cg)
        glow = resplandor(C_ALABEO, cg)
        vista = T("vista desde atrás", size=26, color=TEXTO_SEC,
                  weight=MEDIUM).move_to(cg + DOWN * 1.7)

        self.entrar(barra, C_ALABEO, avion, glow, tit, fr, ej, eje)
        self.hasta(t0, d * 0.33)
        self.play(FadeIn(etq), FadeIn(ctl, scale=0.8), FadeIn(vista),
                  Indicate(VGroup(a_i, a_d), color=C_ALABEO, scale_factor=1.4), run_time=0.6)

        kw = dict(color=C_ALABEO, buff=0, stroke_width=9, max_tip_length_to_length_ratio=0.45,
                  max_stroke_width_to_length_ratio=12)
        sube = Arrow(ORIGIN, UP * 1.0, **kw).next_to(a_d, UP, buff=0.12)
        baja = Arrow(ORIGIN, DOWN * 1.0, **kw).next_to(a_i, DOWN, buff=0.12)
        self.hasta(t0, d * 0.5)
        self.play(a_d.animate.shift(UP * 0.1), a_i.animate.shift(DOWN * 0.1),
                  GrowArrow(sube), GrowArrow(baja), run_time=0.5)
        self.wait(0.3)
        self.play(FadeOut(sube), FadeOut(baja), run_time=0.2)

        fantasma = avion.copy().set_opacity(0.12)
        self.add(fantasma)
        self.bring_to_front(avion, eje)
        flecha = flecha_giro(cg, 2.3, 1.95, -0.8, C_ALABEO)
        self.hasta(t0, d * 0.72)
        self.play(Rotate(avion, -25 * DEGREES, about_point=cg), Create(flecha),
                  rate_func=rate_functions.ease_in_out_cubic, run_time=1.1)
        self.rellenar(t0, d)
        self.salir(avion, fantasma, eje, flecha, glow, tit, fr, ej, etq, ctl, vista)

    # ---------- 3. Guiñada ----------
    def seccion_guinada(self):
        t0, d = self.voz("guinada")
        cg = np.array([0, 0.35, 0])
        avion, timon, bis = avion_superior()
        avion.scale(0.72, about_point=ORIGIN).shift(cg)
        bis = bis * 0.72 + cg
        barra, tit, fr, ej, etq, ctl = self.textos(2, "Guiñada", "Mueve la nariz a los lados",
                                                   "giro alrededor del eje vertical",
                                                   "EL TIMÓN", C_GUINADA)
        eje = simbolo_eje(C_GUINADA).move_to(cg)
        glow = resplandor(C_GUINADA, cg)

        self.entrar(barra, C_GUINADA, avion, glow, tit, fr, ej, eje)
        self.hasta(t0, d * 0.58)
        self.play(FadeIn(etq), FadeIn(ctl, scale=0.8),
                  Indicate(timon, color=C_GUINADA, scale_factor=1.6), run_time=0.6)
        fantasma = avion.copy().set_opacity(0.12)
        self.add(fantasma)
        self.bring_to_front(avion, eje)
        flecha = flecha_giro(cg, 2.6, PI / 2 + 0.35, -0.7, C_GUINADA)
        self.hasta(t0, d * 0.66)
        self.play(Rotate(timon, 24 * DEGREES, about_point=bis), run_time=0.45)
        self.play(Rotate(avion, -15 * DEGREES, about_point=cg), Create(flecha),
                  rate_func=rate_functions.ease_in_out_cubic, run_time=1.1)
        self.rellenar(t0, d)
        self.salir(avion, fantasma, eje, flecha, glow, tit, fr, ej, etq, ctl)

    # ---------- Cierre ----------
    def cierre(self):
        datos = [("Cabeceo", "nariz arriba / abajo", "elevador", C_CABECEO),
                 ("Alabeo", "inclinar las alas", "alerones", C_ALABEO),
                 ("Guiñada", "nariz a los lados", "timón", C_GUINADA)]
        tarjetas = VGroup()
        for nom, desc, ctl, col in datos:
            fondo = RoundedRectangle(width=7.2, height=1.55, corner_radius=0.25, fill_color=PANEL,
                                     fill_opacity=1, stroke_color="#24324A", stroke_width=2)
            acento = RoundedRectangle(width=0.14, height=1.05, corner_radius=0.07, fill_color=col,
                                      fill_opacity=1, stroke_width=0)
            acento.move_to(fondo.get_left() + RIGHT * 0.35)
            n = T(nom, size=60, color=col, weight=HEAVY, font=F_TIT)
            d = T(desc, size=30, color=TEXTO_SEC, weight=MEDIUM)
            txt = VGroup(n, d).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
            txt.next_to(acento, RIGHT, buff=0.35)
            c = pastilla(T(ctl, size=28, color=col, weight=BOLD), col, relleno=0.12,
                         pad_x=0.22, pad_y=0.12)
            c.move_to(fondo.get_right() + LEFT * (c.width / 2 + 0.3))
            tarjetas.add(VGroup(fondo, acento, txt, c))
        tarjetas.arrange(DOWN, buff=0.3).move_to(UP * 2.75 + LEFT * 0.2)

        p1 = T("¿Cuál de los tres", size=60, weight=HEAVY, font=F_TIT)
        p2 = T("no conocías?", size=60, color=C_GUINADA, weight=HEAVY, font=F_TIT)
        preg = VGroup(p1, p2).arrange(DOWN, buff=0.15).move_to(DOWN * 0.95 + LEFT * 0.2)
        com = T("Te leo en comentarios", size=32, color=TEXTO_SEC, weight=MEDIUM)
        com.next_to(preg, DOWN, buff=0.25)

        t0, d = self.voz("cierre")
        self.play(LaggedStart(*[FadeIn(t, shift=RIGHT * 0.5) for t in tarjetas], lag_ratio=0.25),
                  run_time=1.1)
        self.play(FadeIn(preg, shift=UP * 0.3, scale=1.1), run_time=0.5)
        self.play(FadeIn(com), run_time=0.3)
        self.rellenar(t0, d, margen=1.5)

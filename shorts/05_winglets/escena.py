"""
Short 05: "Winglets y vórtices de punta".
Ilustración cualitativa (no calculada): vórtices de punta vistos desde atrás con el sentido de
giro correcto (punta derecha antihorario, izquierda horario), estela vista desde arriba y
consumo comparado con la cifra publicada por la NASA (4–6 %).
Render (desde la raíz del repo):
  manim -qh --fps 30 shorts/05_winglets/escena.py Winglets
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403

C_PRES, C_EST, C_WING = C_CABECEO, C_ALABEO, C_GUINADA
C_VORT = "#E2E8F0"


class Winglets(ShortBase):
    VOZ_JSON = Path(__file__).parent / "voz.json"
    SUBS_DESDE = "presion"      # el gancho ya está escrito en pantalla
    SIN_SUBS_DESDE = "cierre"   # el cierre también

    def construct(self):
        self.iniciar()
        self.reloj = ValueTracker(0.0)
        self.reloj.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(self.reloj)
        self.gancho()

        self.cabecera = T("VÓRTICES DE PUNTA", size=28, color=TEXTO_SEC,
                          weight=SEMIBOLD).move_to(UP * 6.85)
        self.barras = VGroup(*[RoundedRectangle(width=0.7, height=0.12, corner_radius=0.06,
                                                fill_color="#334155", fill_opacity=1,
                                                stroke_width=0) for _ in range(3)])
        self.barras.arrange(RIGHT, buff=0.15).move_to(UP * 6.4)
        self.play(FadeIn(self.cabecera, shift=DOWN * 0.2), FadeIn(self.barras), run_time=0.4)

        self.seccion_presion()
        self.seccion_estela()
        self.seccion_winglet()
        self.cierre()

    # ---------- utilidades ----------
    def avion_atras(self, escala, centro, winglets=True):
        av, _, _ = avion_trasero(winglets)
        ref = av.get_center()
        c = np.array([centro[0], centro[1], 0.0])
        av.scale(escala, about_point=ref).shift(c - ref)
        punta = (PUNTA_TRASERO - ref) * escala + c
        punta_i = punta * np.array([-1, 1, 1]) + np.array([2 * c[0], 0, 0])
        return av, punta_i, punta

    def par_vortices(self, p_izq, p_der, radio, visible, escala=None):
        # visto desde atrás: punta derecha antihorario (+1), izquierda horario (−1)
        vi = vortice(p_izq, self.reloj, radio=radio, sentido=-1, color=C_VORT, visible=visible,
                     escala=escala)
        vd = vortice(p_der, self.reloj, radio=radio, sentido=1, color=C_VORT, visible=visible,
                     escala=escala)
        return VGroup(vi, vd).set_z_index(15)

    def textos(self, idx, nombre, frase, dato, etiqueta, clave, color):
        tit = T(nombre, size=116, color=color, weight=HEAVY, font=F_TIT).move_to(UP * 5.3)
        fr = T(frase, size=48, weight=BOLD).next_to(tit, DOWN, buff=0.28)
        dt = T(dato, size=28, color=TEXTO_SEC, weight=MEDIUM).next_to(fr, DOWN, buff=0.16)
        etq = T(etiqueta, size=28, color=TEXTO_SEC, weight=SEMIBOLD).move_to(DOWN * 3.6)
        ctl = pastilla(T(clave, size=52, color=color, weight=HEAVY, font=F_TIT), color)
        ctl.next_to(etq, DOWN, buff=0.2)
        return self.barras[idx], tit, fr, dt, etq, ctl

    def entrar_textos(self, barra, color, tit, fr, dt, *extra):
        self.play(barra.animate.set_fill(color), FadeIn(tit, shift=DOWN * 0.3, scale=1.15),
                  *extra, run_time=0.6)
        self.play(FadeIn(fr, shift=UP * 0.2), FadeIn(dt), run_time=0.45)

    def etiqueta(self, texto, color, pos, size=26):
        t = T(texto, size=size, color=color, weight=BOLD)
        fondo = RoundedRectangle(width=t.width + 0.36, height=t.height + 0.24, corner_radius=0.14,
                                 fill_color=BG, fill_opacity=0.85, stroke_width=0)
        return VGroup(fondo, t).move_to(pos).set_z_index(30)

    def nota(self, texto, pos):
        return T(texto, size=22, color=TEXTO_SEC, weight=MEDIUM).move_to(pos).set_z_index(30)

    # ---------- Gancho ----------
    def gancho(self):
        l1 = T("Cada avión deja detrás", size=60, weight=HEAVY, font=F_TIT)
        num = T("2 REMOLINOS", size=110, color=BG, weight=HEAVY, font=F_TIT)
        caja = RoundedRectangle(width=num.width + 0.7, height=num.height + 0.55, corner_radius=0.3,
                                fill_color=C_EST, fill_opacity=1, stroke_width=0).move_to(num)
        destacado = VGroup(caja, num)
        l3 = T("como pequeños tornados", size=52, color=TEXTO_SEC, weight=BOLD, font=F_TIT)
        bloque = VGroup(l1, destacado, l3).arrange(DOWN, buff=0.35).move_to(UP * 3.6)
        destacado.rotate(-3 * DEGREES)
        av, pi, pd = self.avion_atras(0.95, (0, -1.6))
        vis = ValueTracker(0.0)
        vort = self.par_vortices(pi, pd, 0.75, vis)
        vista = self.nota("visto desde atrás", [0, -3.9, 0])

        t0, d = self.voz("gancho")
        self.play(FadeIn(l1, shift=UP * 0.3), FadeIn(av, shift=UP * 0.3), run_time=0.4)
        self.add(vort)
        self.play(GrowFromCenter(caja), FadeIn(num, scale=1.6), vis.animate.set_value(1),
                  FadeIn(vista), rate_func=rate_functions.ease_out_back, run_time=0.6)
        self.hasta(0, 3.3)
        self.play(FadeIn(l3, shift=UP * 0.2), run_time=0.4)
        self.rellenar(t0, d, margen=-0.4)
        self.play(FadeOut(VGroup(bloque, av, vista), shift=UP * 0.6), vis.animate.set_value(0),
                  run_time=0.35)
        self.remove(vort)

    # ---------- 1. Presión: de abajo hacia arriba por la punta ----------
    def seccion_presion(self):
        t0, d = self.voz("presion")
        barra, tit, fr, dt, etq, ctl = self.textos(
            0, "Presión", "Más abajo que arriba",
            "el aire va de donde hay más presión a donde hay menos", "LO CAUSA",
            "DIFERENCIA DE PRESIÓN", C_PRES)
        av, pi, pd = self.avion_atras(0.95, (0, 0.3))
        vista = self.nota("visto desde atrás · ilustración", [0, -1.75, 0])
        menos = VGroup(*[self.etiqueta("−  menos presión", C_PRES, [s * 1.95, 1.55, 0], size=24)
                         for s in (-1, 1)])
        mas = VGroup(*[self.etiqueta("+  más presión", "#FDE68A", [s * 2.65, -1.05, 0], size=24)
                       for s in (-1, 1)])
        self.entrar_textos(barra, C_PRES, tit, fr, dt, FadeIn(av, shift=UP * 0.3), FadeIn(vista))
        # "Debajo del ala la presión es mayor que encima"
        self.play(LaggedStart(FadeIn(mas, shift=UP * 0.2), FadeIn(menos, shift=DOWN * 0.2),
                              lag_ratio=0.4), run_time=0.8)
        # "En la punta, el aire se escapa hacia arriba"
        self.hasta(t0, 3.4)
        rodeos = VGroup(rodeo_punta(pi, -1, C_PRES), rodeo_punta(pd, 1, C_PRES)).set_z_index(20)
        self.play(FadeOut(menos), FadeOut(mas), *[Create(r) for r in rodeos], run_time=0.9)
        # "y, al avanzar, se enrolla en un remolino"
        self.hasta(t0, 6.0)
        vis, esc = ValueTracker(0.0), ValueTracker(0.3)
        vort = self.par_vortices(pi + UP * 0.05, pd + UP * 0.05, 0.85, vis, escala=esc)
        self.add(vort)
        self.play(vis.animate.set_value(1), esc.animate.set_value(1), FadeOut(rodeos),
                  run_time=1.0)
        giro = VGroup(self.etiqueta("antihorario", C_VORT, pd + DOWN * 1.25 + LEFT * 0.35, size=22),
                      self.etiqueta("horario", C_VORT, pi + DOWN * 1.25 + RIGHT * 0.2, size=22))
        self.play(FadeIn(giro), FadeIn(etq), FadeIn(ctl, scale=0.8), run_time=0.45)
        self.rellenar(t0, d)
        self.play(*[FadeOut(m, shift=LEFT * 0.6) for m in (tit, fr, dt, etq, ctl, av, vista, giro)],
                  vis.animate.set_value(0), run_time=0.4)
        self.remove(vort)

    # ---------- 2. Estela: duran y bajan → separación ----------
    def seccion_estela(self):
        t0, d = self.voz("estela")
        barra, tit, fr, dt, etq, ctl = self.textos(
            1, "Estela", "Duran de 1 a 3 minutos", "y van bajando poco a poco",
            "POR ESO HAY", "DISTANCIA MÍNIMA", C_EST)
        av, _, _ = avion_superior()
        av.scale(0.36).move_to([0.6, 1.95, 0]).set_z_index(10)
        esc = 0.36
        c = av.get_center()
        # puntas del ala de avion_superior: (±3.78, −1.0) en sus coordenadas
        ref, _, _ = avion_superior()
        r0 = ref.get_center()
        p_d = (np.array([3.78, -1.15, 0]) - r0) * esc + c
        p_i = (np.array([-3.78, -1.15, 0]) - r0) * esc + c
        vis = ValueTracker(0.0)
        estela = estela_superior(p_i, p_d, 2.9, self.reloj, color=C_VORT, amplitud=0.1,
                                 visible=vis).set_z_index(5)
        vista = self.nota("visto desde arriba · ilustración", [0.6, -1.95, 0])
        reloj_txt = self.etiqueta("1–3 min", C_EST, [p_d[0] + 0.95, p_d[1] - 1.5, 0], size=30)
        sigue, _, _ = avion_superior()
        sigue.scale(0.2).move_to([0.6, -1.25 + 0.0, 0]).set_z_index(10)
        top = av.get_bottom()[1] - 0.05
        bot = sigue.get_top()[1] + 0.05
        llave = BraceBetweenPoints([-1.15, bot, 0], [-1.15, top, 0], direction=LEFT, color=C_EST)
        llave_txt = T("distancia\nmínima", size=26, color=C_EST, weight=BOLD)
        llave_txt.next_to(llave, LEFT, buff=0.15)
        self.entrar_textos(barra, C_EST, tit, fr, dt, FadeIn(av, shift=UP * 0.3), FadeIn(vista))
        self.add(estela)
        self.play(vis.animate.set_value(1), FadeIn(reloj_txt), run_time=0.7)
        # "Por eso hay una distancia mínima entre aviones que aterrizan"
        self.hasta(t0, 3.0)
        self.play(FadeIn(sigue, shift=UP * 0.3), GrowFromCenter(llave), FadeIn(llave_txt),
                  run_time=0.6)
        self.hasta(t0, 4.4)
        self.play(FadeIn(etq), FadeIn(ctl, scale=0.8), run_time=0.4)
        self.rellenar(t0, d)
        self.play(*[FadeOut(m, shift=LEFT * 0.6) for m in
                    (tit, fr, dt, etq, ctl, av, vista, reloj_txt, sigue, llave, llave_txt)],
                  vis.animate.set_value(0), run_time=0.4)
        self.remove(estela)

    # ---------- 3. Winglet: menos resistencia ----------
    def seccion_winglet(self):
        t0, d = self.voz("winglet")
        barra, tit, fr, dt, etq, ctl = self.textos(
            2, "Winglet", "No lo elimina: reduce la resistencia",
            "4–6 % menos combustible, según la NASA", "AHORRA", "4–6 % DE COMBUSTIBLE", C_WING)
        esc = 1.55
        av, _, pd = self.avion_atras(esc, (-2.3, 1.15), winglets=False)
        av.set_z_index(10)
        wl = winglet_trasero(1)
        ref = avion_trasero(False)[0].get_center()
        wl.scale(esc, about_point=ref).shift(np.array([-2.3, 1.15, 0.0]) - ref)
        wl.set_fill(color=[C_WING, "#F59E0B"]).set_z_index(11)
        vis, esc_v = ValueTracker(0.0), ValueTracker(1.0)
        pos = ValueTracker(0.0)
        tope = wl.get_top()

        def centro():
            return pd + (tope - pd) * pos.get_value() + UP * 0.05
        vort = vortice(centro, self.reloj, radio=0.7, sentido=1, color=C_VORT, visible=vis,
                       escala=esc_v).set_z_index(15)
        vista = self.nota("vista desde atrás · ilustración", [2.35, -0.5, 0]).scale(0.9)
        self.add(vort)
        self.entrar_textos(barra, C_WING, tit, fr, dt, FadeIn(av, shift=UP * 0.3),
                           vis.animate.set_value(1), FadeIn(vista))
        # "El winglet no los elimina"
        self.play(GrowFromEdge(wl, DOWN), pos.animate.set_value(1), esc_v.animate.set_value(0.85),
                  run_time=0.7)
        sigue = self.etiqueta("el remolino sigue ahí", C_VORT, tope + LEFT * 2.6 + UP * 0.2,
                              size=24)
        self.play(FadeIn(sigue), run_time=0.3)

        # "pero reduce la resistencia que generan: ahorra entre un 4 y un 6 %"
        x0, y1, y2, L = -0.6, -1.4, -1.95, 4.2
        b1 = Rectangle(width=L, height=0.42, fill_color="#475569", fill_opacity=1, stroke_width=0)
        b1.move_to([x0 + L / 2, y1, 0])
        b2 = Rectangle(width=L, height=0.42, fill_color=C_WING, fill_opacity=1, stroke_width=0)
        b2.move_to([x0 + L / 2, y2, 0])
        e1 = T("consumo sin winglet", size=22, color=TEXTO_SEC, weight=SEMIBOLD).next_to(b1, LEFT, buff=0.15)
        e2 = T("con winglet", size=22, color=C_WING, weight=SEMIBOLD).next_to(b2, LEFT, buff=0.15)
        v1 = T("100 %", size=24, color=TEXTO, weight=BOLD).move_to(b1).align_to(b1, RIGHT).shift(LEFT * 0.1)
        barras = VGroup(b1, b2, e1, e2, v1)
        self.hasta(t0, 2.35)
        self.play(FadeIn(barras, shift=UP * 0.2), run_time=0.5)
        self.hasta(t0, 4.9)
        v2 = T("95 %", size=24, color=BG, weight=BOLD)
        self.play(b2.animate.stretch_to_fit_width(L * 0.95, about_edge=LEFT), run_time=0.8)
        v2.move_to(b2).align_to(b2, RIGHT).shift(LEFT * 0.1)
        aho = self.etiqueta("−4 a −6 %", C_WING, [x0 + 1.0, y2, 0], size=24)
        self.play(FadeIn(v2), FadeIn(aho, scale=1.2), run_time=0.35)
        self.hasta(t0, 6.6)
        self.play(FadeIn(etq), FadeIn(ctl, scale=0.8), run_time=0.4)
        self.rellenar(t0, d)
        self.play(*[FadeOut(m, shift=LEFT * 0.6) for m in
                    (tit, fr, dt, etq, ctl, av, wl, sigue, barras, v2, aho, vista)],
                  vis.animate.set_value(0), run_time=0.4)
        self.remove(vort)

    # ---------- Cierre ----------
    def cierre(self):
        datos = [("Presión", "más abajo que arriba", "origen", C_PRES),
                 ("Estela", "dura de 1 a 3 min", "separación", C_EST),
                 ("Winglet", "menos resistencia", "−4–6 %", C_WING)]
        tarjetas = VGroup()
        for nom, desc, ctl, col in datos:
            fondo = RoundedRectangle(width=7.2, height=1.55, corner_radius=0.25, fill_color=PANEL,
                                     fill_opacity=1, stroke_color="#24324A", stroke_width=2)
            acento = RoundedRectangle(width=0.14, height=1.05, corner_radius=0.07, fill_color=col,
                                      fill_opacity=1, stroke_width=0)
            acento.move_to(fondo.get_left() + RIGHT * 0.35)
            n = T(nom, size=56, color=col, weight=HEAVY, font=F_TIT)
            dd = T(desc, size=30, color=TEXTO_SEC, weight=MEDIUM)
            txt = VGroup(n, dd).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
            txt.next_to(acento, RIGHT, buff=0.35)
            c = pastilla(T(ctl, size=28, color=col, weight=BOLD), col, relleno=0.12,
                         pad_x=0.22, pad_y=0.12)
            c.move_to(fondo.get_right() + LEFT * (c.width / 2 + 0.3))
            tarjetas.add(VGroup(fondo, acento, txt, c))
        tarjetas.arrange(DOWN, buff=0.3).move_to(UP * 3.3)

        lema = T("Dos remolinos en cada vuelo", size=36, color=TEXTO,
                 weight=SEMIBOLD).next_to(tarjetas, DOWN, buff=0.45)
        p1 = T("¿Los habías visto", size=60, weight=HEAVY, font=F_TIT)
        p2 = T("alguna vez?", size=60, color=C_EST, weight=HEAVY, font=F_TIT)
        preg = VGroup(p1, p2).arrange(DOWN, buff=0.15).next_to(lema, DOWN, buff=0.7)
        com = T("Te leo en comentarios", size=32, color=TEXTO_SEC, weight=MEDIUM)
        com.next_to(preg, DOWN, buff=0.25)

        t0, d = self.voz("cierre")
        self.play(LaggedStart(*[FadeIn(t, shift=RIGHT * 0.5) for t in tarjetas], lag_ratio=0.25),
                  run_time=1.0)
        self.play(FadeIn(lema, shift=UP * 0.2), run_time=0.4)
        self.hasta(t0, 2.3)
        self.play(FadeIn(preg, shift=UP * 0.3, scale=1.1), run_time=0.5)
        self.play(FadeIn(com), run_time=0.3)
        self.rellenar(t0, d, margen=1.5)

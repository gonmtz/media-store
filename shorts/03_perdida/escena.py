"""
Short 03: "Pérdida (stall): caer con los motores funcionando".
Flujo pegado: calculado con `Perfil` (flujo ideal 2D, rotulado). Flujo separado: ilustración
cualitativa (`flujo_separado`, `remolinos`), rotulada. Gráfica: curva típica Cl–α (`GraficaCl`).
Render (desde la raíz del repo):
  manim -qh --fps 30 shorts/03_perdida/escena.py Perdida
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403

C_ANG, C_SEP, C_REC = C_CABECEO, C_ALABEO, C_GUINADA
C_SUST = "#E2E8F0"
CENTRO = (0.3, 1.62)
ESCALA = 1.05
MU = complex(-0.08, 0.05)
ALFA_SEP = 18.0
YS = [0.4, 0.8, 1.2, 1.6, 2.0, 2.4, 2.8]


def perfil(alfa):
    return Perfil(alfa=alfa, mu=MU, escala=ESCALA, centro=CENTRO)


class Perdida(ShortBase):
    VOZ_JSON = Path(__file__).parent / "voz.json"
    SUBS_DESDE = "angulo"       # el gancho ya está escrito en pantalla
    SIN_SUBS_DESDE = "cierre"   # el cierre también

    def construct(self):
        self.iniciar()
        self.gancho()

        self.cabecera = T("PÉRDIDA (STALL)", size=28, color=TEXTO_SEC,
                          weight=SEMIBOLD).move_to(UP * 6.85)
        self.barras = VGroup(*[RoundedRectangle(width=0.7, height=0.12, corner_radius=0.06,
                                                fill_color="#334155", fill_opacity=1,
                                                stroke_width=0) for _ in range(3)])
        self.barras.arrange(RIGHT, buff=0.15).move_to(UP * 6.4)
        self.play(FadeIn(self.cabecera, shift=DOWN * 0.2), FadeIn(self.barras), run_time=0.4)

        self.seccion_angulo()
        self.seccion_separacion()
        self.seccion_motor()
        self.cierre()

    # ---------- Gancho ----------
    def gancho(self):
        l1 = T("¿Un avión puede caer", size=62, weight=HEAVY, font=F_TIT)
        l2 = T("con los motores al", size=62, weight=HEAVY, font=F_TIT)
        num = T("100 %", size=130, color=BG, weight=HEAVY, font=F_TIT)
        caja = RoundedRectangle(width=num.width + 0.8, height=num.height + 0.55, corner_radius=0.3,
                                fill_color=C_REC, fill_opacity=1, stroke_width=0).move_to(num)
        destacado = VGroup(caja, num)
        l3 = T("de potencia?", size=62, weight=HEAVY, font=F_TIT)
        bloque = VGroup(l1, l2, destacado, l3).arrange(DOWN, buff=0.34).move_to(UP * 2.4)
        destacado.rotate(-3 * DEGREES)
        txt = T("SÍ: PÉRDIDA", size=96, color=C_SEP, weight=HEAVY, font=F_TIT)
        marco = RoundedRectangle(width=txt.width + 0.6, height=txt.height + 0.5,
                                 corner_radius=0.2, stroke_color=C_SEP, stroke_width=10,
                                 fill_opacity=0)
        sello = VGroup(marco, txt.move_to(marco)).rotate(6 * DEGREES).move_to(DOWN * 1.6)

        t0, d = self.voz("gancho")
        self.play(FadeIn(l1, shift=UP * 0.3), run_time=0.35)
        self.play(FadeIn(l2, shift=UP * 0.3), run_time=0.3)
        self.play(GrowFromCenter(caja), FadeIn(num, scale=1.6),
                  rate_func=rate_functions.ease_out_back, run_time=0.5)
        self.play(FadeIn(l3, shift=UP * 0.2), run_time=0.35)
        self.hasta(0, 3.55)
        self.play(FadeIn(sello, scale=2.2), rate_func=rate_functions.ease_out_back, run_time=0.35)
        self.rellenar(t0, d, margen=-0.5)
        self.play(FadeOut(VGroup(bloque, sello), shift=UP * 0.6), run_time=0.35)

    # ---------- Textos de cada bloque ----------
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

    def salir(self, *mobs, **kw):
        self.play(*[FadeOut(m, shift=LEFT * 0.6) for m in mobs], run_time=0.4, **kw)

    def etiqueta(self, texto, color, pos, size=26):
        t = T(texto, size=size, color=color, weight=BOLD)
        fondo = RoundedRectangle(width=t.width + 0.36, height=t.height + 0.24, corner_radius=0.14,
                                 fill_color=BG, fill_opacity=0.85, stroke_width=0)
        return VGroup(fondo, t).move_to(pos).set_z_index(30)

    def nota(self, texto):
        t = T(texto, size=22, color=TEXTO_SEC, weight=MEDIUM)
        fondo = RoundedRectangle(width=t.width + 0.3, height=t.height + 0.18, corner_radius=0.1,
                                 fill_color=BG, fill_opacity=0.85, stroke_width=0)
        return VGroup(fondo, t).move_to([0, 0.3, 0]).set_z_index(30)

    # ---------- 1. Ángulo de ataque ----------
    def seccion_angulo(self):
        t0, d = self.voz("angulo")
        barra, tit, fr, dt, etq, ctl = self.textos(
            0, "Ángulo", "El ala frente al aire que llega",
            "ángulo de ataque: entre el ala y el viento relativo", "LO QUE MANDA",
            "ÁNGULO DE ATAQUE", C_ANG)

        self.alfa = ValueTracker(0.0)
        alfa = self.alfa
        self.familia = LineasPorAlfa(perfil, list(range(0, 16)), YS, x_ini=-4.4, x_fin=4.4)
        self.reloj = ValueTracker(0.0)
        self.reloj.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(self.reloj)

        def ala():
            return perfil(alfa.get_value()).contorno().set_z_index(10)
        self.ala = always_redraw(ala)

        def lineas():
            return VGroup(*[trazo(p, ancho=2.5) for p, _ in self.familia.en(alfa.get_value())]) \
                .set_z_index(1)
        self.lineas = always_redraw(lineas)
        self.puntos = trazadores_variables(lambda: self.familia.en(alfa.get_value()), self.reloj,
                                           "#E2E8F0", cada=0.9, velocidad=1.5).set_z_index(2)
        self.n_ideal = self.nota("simplificación: flujo ideal en 2D")

        # indicador del ángulo: viento (horizontal) y cuerda
        def indicador():
            P = perfil(alfa.get_value())
            le, te = P.borde_ataque(), P.borde_salida()
            u = (te - le) / np.linalg.norm(te - le)
            ref = DashedLine(le + LEFT * 1.6, le, color=C_ANG, stroke_width=3, dash_length=0.1)
            cuerda = DashedLine(le - u * 1.6, le, color=TEXTO, stroke_width=3, dash_length=0.1)
            a = alfa.get_value()
            arco = angulo_entre(le, PI, PI - a * DEGREES, 1.35, C_ANG, ancho=6)
            t = T(f"α = {a:.0f}°", size=36, color=C_ANG, weight=HEAVY, font=F_TIT)
            fondo = RoundedRectangle(width=t.width + 0.3, height=t.height + 0.2,
                                     corner_radius=0.12, fill_color=BG, fill_opacity=0.85,
                                     stroke_width=0).move_to(t)
            txt = VGroup(fondo, t).move_to(le + np.array([-1.75, 0.62, 0]))
            return VGroup(ref, cuerda, arco, txt).set_z_index(20)
        self.indicador = always_redraw(indicador)
        viento = VGroup(vector([-4.3, 0.55, 0], [-3.1, 0.55, 0], C_ANG, ancho=8, punta=0.25),
                        T("aire", size=26, color=C_ANG, weight=BOLD))
        viento[1].next_to(viento[0], DOWN, buff=0.1)
        self.viento = viento.set_z_index(20)

        # gráfica típica Cl–α y fuerza de sustentación
        self.graf = GraficaCl(ancho=6.0, alto=1.5, color=C_ANG)
        self.graf.shift(np.array([-2.75, -1.9, 0]) - self.graf.ejes.c2p(0, 0))
        g = self.graf
        self.traza = always_redraw(lambda: g.curva_hasta(alfa.get_value()).set_z_index(5))
        self.pto = always_redraw(lambda: Dot(g.punto(alfa.get_value()), radius=0.11,
                                             color=TEXTO).set_z_index(6))

        def sustentacion():
            P = perfil(alfa.get_value())
            le, te = P.borde_ataque(), P.borde_salida()
            base = le + 0.3 * (te - le) + UP * 0.3
            L = 0.62 * float(cl_tipico(alfa.get_value()))
            return vector(base, base + UP * max(L, 0.05), self.col_sust, ancho=12, punta=0.3) \
                .set_z_index(25)
        self.col_sust = C_SUST
        self.sust = always_redraw(sustentacion)
        def sust_txt():
            e = self.etiqueta("sustentación", self.col_sust, ORIGIN, size=24)
            return e.next_to(self.sust, RIGHT, buff=0.08).align_to(self.sust, UP).set_z_index(26)
        self.sust_txt = always_redraw(sust_txt)

        self.entrar_textos(barra, C_ANG, tit, fr, dt, FadeIn(self.ala, shift=UP * 0.3),
                           FadeIn(self.lineas), FadeIn(self.puntos), FadeIn(self.n_ideal),
                           FadeIn(self.viento))
        self.play(FadeIn(self.graf), run_time=0.5)
        # "cuánto se inclina el ala frente al aire"
        self.hasta(t0, 2.3)
        self.play(FadeIn(self.indicador), FadeIn(self.traza), FadeIn(self.pto),
                  FadeIn(self.sust), run_time=0.4)
        self.play(alfa.animate.set_value(6), rate_func=smooth, run_time=1.6)
        self.play(FadeIn(self.sust_txt), run_time=0.3)
        # "más ángulo, más sustentación"
        self.hasta(t0, 4.85)
        self.play(alfa.animate.set_value(12), rate_func=smooth, run_time=2.1)
        # "hasta unos quince grados"
        self.hasta(t0, 7.3)
        self.critico = g.marca_critico().set_z_index(7)
        self.play(alfa.animate.set_value(ALFA_CRIT), FadeIn(self.critico), rate_func=smooth,
                  run_time=1.2)
        self.play(FadeIn(etq), FadeIn(ctl, scale=0.8), run_time=0.4)
        self.rellenar(t0, d)
        self.salir(tit, fr, dt, etq, ctl)

    # ---------- 2. Separación ----------
    def seccion_separacion(self):
        t0, d = self.voz("separacion")
        alfa = self.alfa
        barra, tit, fr, dt, etq, ctl = self.textos(
            1, "Separación", "El aire se despega del ala",
            "la sustentación cae de golpe y la resistencia sube", "AL PASAR EL LÍMITE",
            "FLUJO SEPARADO", C_SEP)
        P = perfil(ALFA_SEP)
        sep_lineas, p_sep = flujo_separado(P, YS, x_ini=-4.4, x_fin=4.4)
        tr_sep = VGroup(*[trazo(p, ancho=2.5) for p, _ in sep_lineas]).set_z_index(1)
        pt_sep = trazadores(sep_lineas, self.reloj, "#E2E8F0", cada=0.9,
                            velocidad=1.5).set_z_index(2)
        # techo de la zona revuelta: la primera línea separada por encima del ala
        cont = P.puntos_contorno(720)
        y_sup_sep = p_sep[1]
        altas = [p for p, _ in sep_lineas if np.interp(p_sep[0], p[:, 0], p[:, 1]) >= y_sup_sep - 0.02]
        baja = min(altas, key=lambda p: np.interp(p_sep[0] + 1.0, p[:, 0], p[:, 1]))
        orden = np.argsort(baja[:, 0])

        def techo(x):
            return np.interp(x, baja[orden, 0], baja[orden, 1]) - 0.08
        self.vis_rem = ValueTracker(0.0)
        rem = remolinos(P, p_sep, techo, self.reloj, color="#FDA4AF", n=7,
                        visible=self.vis_rem).set_z_index(3)
        n_sep = self.nota("ilustración simplificada: flujo separado")
        punto_sep = Dot(p_sep, radius=0.08, color=C_SEP).set_z_index(22)

        self.entrar_textos(barra, C_SEP, tit, fr, dt)
        # "el aire se despega de la parte de arriba"
        self.hasta(t0, 0.95)
        self.play(FadeOut(self.indicador), FadeOut(self.viento), run_time=0.3)
        self.puntos.clear_updaters()
        self.play(alfa.animate.set_value(ALFA_SEP), FadeOut(self.lineas), FadeOut(self.puntos),
                  FadeOut(self.n_ideal), FadeIn(tr_sep), FadeIn(pt_sep), FadeIn(n_sep),
                  rate_func=smooth, run_time=1.2)
        self.add(rem)
        self.play(self.vis_rem.animate.set_value(1.0), FadeIn(punto_sep, scale=2), run_time=0.5)
        # "la sustentación cae de golpe"
        self.hasta(t0, 3.6)
        cae = self.etiqueta("¡cae!", C_SEP, self.graf.punto(ALFA_SEP) + DOWN * 0.45 + LEFT * 0.1)
        self.col_sust = C_SEP
        self.play(FadeIn(cae, scale=1.4), Flash(self.pto, color=C_SEP), run_time=0.45)
        # "y la resistencia sube"
        self.hasta(t0, 5.55)
        le, te = P.borde_ataque(), P.borde_salida()
        base = le + 0.3 * (te - le) + UP * 0.3
        res = vector(base, base + RIGHT * 3.6 * float(cd_tipico(ALFA_SEP)), C_SEP, ancho=12,
                     punta=0.3).set_z_index(25)
        res_txt = self.etiqueta("resistencia", C_SEP, ORIGIN, size=24).next_to(res, RIGHT, buff=0.08)
        self.play(GrowArrow(res), FadeIn(res_txt), FadeIn(etq), FadeIn(ctl, scale=0.8),
                  run_time=0.5)
        self.rellenar(t0, d)
        for m in (pt_sep, rem):
            m.clear_updaters()
        self.salir(tit, fr, dt, etq, ctl, tr_sep, pt_sep, rem, n_sep, punto_sep, cae, res,
                   res_txt, self.ala, self.sust, self.sust_txt, self.graf, self.traza, self.pto,
                   self.critico)

    # ---------- 3. No es el motor: bajar la nariz ----------
    def seccion_motor(self):
        t0, d = self.voz("motor")
        barra, tit, fr, dt, etq, ctl = self.textos(
            2, "No es el motor", "Pasa a cualquier velocidad",
            "y con la nariz en cualquier posición", "SE SALE CON", "BAJAR LA NARIZ", C_REC)

        cg = np.array([-0.75, 1.15, 0])
        tray = -10.0                       # trayectoria (grados)
        theta = ValueTracker(15.0)         # actitud: nariz arriba
        avion, _, _ = avion_lateral()
        avion.scale(0.74).move_to(ORIGIN)
        avion.shift(cg - avion.get_center()).set_z_index(10)
        avion.rotate(15 * DEGREES, about_point=cg)
        avion.ang = 15.0

        def girar(m):
            a = theta.get_value()
            m.rotate((a - m.ang) * DEGREES, about_point=cg)
            m.ang = a
        avion.add_updater(girar)

        d_tray = np.array([np.cos(tray * DEGREES), np.sin(tray * DEGREES), 0])
        linea_tray = DashedLine(cg - d_tray * 3.3, cg + d_tray * 5.0, color=TEXTO_SEC,
                                stroke_width=3, dash_length=0.12).set_z_index(4)
        v = vector(cg + d_tray * 3.3, cg + d_tray * 4.6, TEXTO, ancho=9, punta=0.28).set_z_index(5)
        v_txt = T("trayectoria", size=24, color=TEXTO, weight=BOLD)
        v_txt.move_to(cg + d_tray * 3.6 + DOWN * 0.42).set_z_index(5)
        horiz = DashedLine([-4.2, cg[1], 0], [-2.6, cg[1], 0], color="#475569", stroke_width=2,
                           dash_length=0.1)

        def angulo():
            a = theta.get_value()
            u = np.array([np.cos(a * DEGREES), np.sin(a * DEGREES), 0])
            eje = DashedLine(cg + u * 2.4, cg + u * 3.5, color=C_REC, stroke_width=3,
                             dash_length=0.1)
            arco = angulo_entre(cg, tray * DEGREES, a * DEGREES, 3.3, C_REC, ancho=6)
            al = a - tray
            col = C_SEP if al > ALFA_CRIT else C_REC
            txt = T(f"α ≈ {al:.0f}°", size=36, color=col, weight=HEAVY, font=F_TIT)
            p = cg + 3.5 * u + UP * 0.45
            p[0] = min(p[0], ANCHO_MAX / 2 - txt.width / 2)
            txt.move_to(p)
            return VGroup(eje, arco, txt).set_z_index(20)
        ang = always_redraw(angulo)

        motores = self.etiqueta("motores: 100 % de potencia", C_REC, [-1.0, 3.05, 0], size=28)
        estado = always_redraw(lambda: self.etiqueta(
            "EN PÉRDIDA" if theta.get_value() + 10 > ALFA_CRIT else "FLUJO PEGADO",
            C_SEP if theta.get_value() + 10 > ALFA_CRIT else C_REC, [0.9, -0.85, 0], size=32))
        nota = T("el «stall» de un motor es otro fenómeno", size=22, color=TEXTO_SEC,
                 weight=MEDIUM).move_to([0, -1.6, 0])

        self.entrar_textos(barra, C_REC, tit, fr, dt)
        self.hasta(t0, 1.15)
        self.play(FadeIn(avion, shift=UP * 0.3), Create(linea_tray), FadeIn(horiz),
                  FadeIn(motores), FadeIn(nota), run_time=0.6)
        # "puede ocurrir a cualquier velocidad y con cualquier inclinación de la nariz"
        self.hasta(t0, 1.75)
        self.play(GrowArrow(v), FadeIn(v_txt), FadeIn(ang), FadeIn(estado), run_time=0.5)
        self.play(Indicate(estado, color=C_SEP, scale_factor=1.1), run_time=0.8)
        # "para salir, hay que bajarla"
        self.hasta(t0, 6.6)
        self.play(theta.animate.set_value(-5.0), rate_func=smooth, run_time=1.6)
        # "aunque parezca al revés"
        self.hasta(t0, 8.25)
        self.play(FadeIn(etq), FadeIn(ctl, scale=0.8), run_time=0.4)
        self.rellenar(t0, d)
        avion.clear_updaters()
        self.salir(tit, fr, dt, etq, ctl, avion, linea_tray, v, v_txt, horiz, ang, motores,
                   estado, nota)

    # ---------- Cierre ----------
    def cierre(self):
        datos = [("Ángulo", "límite ≈ 15° (típico)", "manda", C_ANG),
                 ("Separación", "el aire se despega", "cae", C_SEP),
                 ("Salir", "bajar la nariz", "menos α", C_REC)]
        tarjetas = VGroup()
        for nom, desc, ctl, col in datos:
            fondo = RoundedRectangle(width=7.2, height=1.55, corner_radius=0.25, fill_color=PANEL,
                                     fill_opacity=1, stroke_color="#24324A", stroke_width=2)
            acento = RoundedRectangle(width=0.14, height=1.05, corner_radius=0.07, fill_color=col,
                                      fill_opacity=1, stroke_width=0)
            acento.move_to(fondo.get_left() + RIGHT * 0.35)
            n = T(nom, size=60, color=col, weight=HEAVY, font=F_TIT)
            dd = T(desc, size=30, color=TEXTO_SEC, weight=MEDIUM)
            txt = VGroup(n, dd).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
            txt.next_to(acento, RIGHT, buff=0.35)
            c = pastilla(T(ctl, size=28, color=col, weight=BOLD), col, relleno=0.12,
                         pad_x=0.22, pad_y=0.12)
            c.move_to(fondo.get_right() + LEFT * (c.width / 2 + 0.3))
            tarjetas.add(VGroup(fondo, acento, txt, c))
        tarjetas.arrange(DOWN, buff=0.3).move_to(UP * 3.3)

        lema = T("La pérdida es del ala, no del motor", size=36, color=TEXTO,
                 weight=SEMIBOLD).next_to(tarjetas, DOWN, buff=0.45)
        p1 = T("¿Sabías que se sale", size=60, weight=HEAVY, font=F_TIT)
        p2 = T("bajando la nariz?", size=60, color=C_REC, weight=HEAVY, font=F_TIT)
        preg = VGroup(p1, p2).arrange(DOWN, buff=0.15).next_to(lema, DOWN, buff=0.7)
        com = T("Te leo en comentarios", size=32, color=TEXTO_SEC, weight=MEDIUM)
        com.next_to(preg, DOWN, buff=0.25)

        t0, d = self.voz("cierre")
        self.play(LaggedStart(*[FadeIn(t, shift=RIGHT * 0.5) for t in tarjetas], lag_ratio=0.25),
                  run_time=1.1)
        self.play(FadeIn(lema, shift=UP * 0.2), run_time=0.4)
        self.hasta(t0, 2.55)
        self.play(FadeIn(preg, shift=UP * 0.3, scale=1.1), run_time=0.5)
        self.play(FadeIn(com), run_time=0.3)
        self.rellenar(t0, d, margen=1.5)

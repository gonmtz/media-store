"""
Short 07 (BOCETO sin voz): "Alas volantes: ¿cómo vuela un avión sin cola?".
Tiempos estimados en voz.json (sin audio). Ilustración cualitativa: fuerzas sin escala.
Render (desde la raíz del repo):
  manim -qh --fps 30 shorts/07_ala_volante/escena.py AlaVolante
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403

C_COLA, C_ALA, C_GIRO = C_CABECEO, C_ALABEO, C_GUINADA
C_FUERZA = "#E2E8F0"


class AlaVolante(ShortBase):
    VOZ_JSON = Path(__file__).parent / "voz.json"
    SUBS_DESDE = "cola"
    SIN_SUBS_DESDE = "cierre"

    def construct(self):
        self.iniciar()
        self.gancho()
        self.cabecera = T("ALAS VOLANTES", size=28, color=TEXTO_SEC,
                          weight=SEMIBOLD).move_to(UP * 6.85)
        self.barras = VGroup(*[RoundedRectangle(width=0.7, height=0.12, corner_radius=0.06,
                                                fill_color="#334155", fill_opacity=1,
                                                stroke_width=0) for _ in range(3)])
        self.barras.arrange(RIGHT, buff=0.15).move_to(UP * 6.4)
        self.play(FadeIn(self.cabecera, shift=DOWN * 0.2), FadeIn(self.barras), run_time=0.4)
        self.seccion_cola()
        self.seccion_ala()
        self.seccion_giro()
        self.cierre()

    # ---------- utilidades ----------
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

    def cg(self, p):
        """Símbolo de centro de gravedad."""
        c = Circle(radius=0.17, stroke_color=BG, stroke_width=2).set_fill(TEXTO, 1).move_to(p)
        q1 = AnnularSector(inner_radius=0, outer_radius=0.17, angle=PI / 2, start_angle=0,
                           fill_color=BG, fill_opacity=1).move_to(p, aligned_edge=DL)
        q2 = AnnularSector(inner_radius=0, outer_radius=0.17, angle=PI / 2, start_angle=PI,
                           fill_color=BG, fill_opacity=1).move_to(p, aligned_edge=UR)
        return VGroup(c, q1, q2).set_z_index(25)

    def ala_volante(self, escala, centro):
        av, pi, pd = ala_volante_superior()
        c = np.array([centro[0], centro[1], 0.0])
        av.scale(escala, about_point=ORIGIN).shift(c)
        return av, pi * escala + c, pd * escala + c

    # ---------- Gancho ----------
    def gancho(self):
        av, _, _ = self.ala_volante(1.0, (0, 0.3))
        av.set_z_index(5)
        l1 = T("Este avión", size=66, weight=HEAVY, font=F_TIT)
        l2 = T("no tiene", size=66, weight=HEAVY, font=F_TIT)
        pal = T("COLA", size=130, color=BG, weight=HEAVY, font=F_TIT)
        caja = RoundedRectangle(width=pal.width + 0.8, height=pal.height + 0.5, corner_radius=0.3,
                                fill_color=C_GIRO, fill_opacity=1, stroke_width=0).move_to(pal)
        destacado = VGroup(caja, pal)
        bloque = VGroup(VGroup(l1, l2).arrange(DOWN, buff=0.2), destacado).arrange(DOWN, buff=0.35)
        bloque.move_to(UP * 4.6)
        destacado.rotate(-3 * DEGREES)
        tacha = Cross(stroke_color=C_ALA, stroke_width=10).scale(0.45).move_to([0, -1.7, 0])
        hueco = DashedVMobject(RoundedRectangle(width=1.3, height=1.0, corner_radius=0.2),
                               num_dashes=20).set_stroke(TEXTO_SEC, 3).move_to([0, -1.7, 0])
        preg = T("¿Por qué no da vueltas?", size=60, color=C_GIRO, weight=HEAVY, font=F_TIT)
        preg.move_to(DOWN * 3.4)

        t0, d = self.voz("gancho")
        self.play(FadeIn(av, shift=UP * 0.5, scale=0.9), FadeIn(l1, shift=UP * 0.3), run_time=0.45)
        self.play(FadeIn(l2, shift=UP * 0.3), run_time=0.3)
        self.play(GrowFromCenter(caja), FadeIn(pal, scale=1.6), Create(hueco),
                  rate_func=rate_functions.ease_out_back, run_time=0.5)
        self.play(Create(tacha), run_time=0.3)
        self.hasta(0, 2.05)
        self.play(FadeIn(preg, scale=1.4), rate_func=rate_functions.ease_out_back, run_time=0.4)
        self.play(av.animate.rotate(4 * DEGREES), rate_func=there_and_back, run_time=0.8)
        self.rellenar(t0, d, margen=-0.5)
        self.play(FadeOut(VGroup(bloque, av, tacha, hueco, preg), shift=UP * 0.6), run_time=0.35)

    # ---------- 1. La cola ----------
    def seccion_cola(self):
        t0, d = self.voz("cola")
        barra, tit, fr, dt, etq, ctl = self.textos(
            0, "La cola", "Equilibra el ala y la estabiliza",
            "ilustración: fuerzas sin escala", "EN UN AVIÓN NORMAL",
            "ESTABILIZADOR", C_COLA)
        cgp = np.array([0.15, 0.9, 0])
        theta = ValueTracker(0.0)
        avion, _, _ = avion_lateral()
        avion.scale(0.95).move_to(cgp + LEFT * 0.1).set_z_index(10)
        avion.ang = 0.0

        def girar(m):
            a = theta.get_value()
            m.rotate((a - m.ang) * DEGREES, about_point=cgp)
            m.ang = a
        avion.add_updater(girar)
        cola_p0 = cgp + np.array([-3.3, 0.3, 0])

        def rot(p):
            a = theta.get_value() * DEGREES
            v = p - cgp
            return cgp + np.array([v[0] * np.cos(a) - v[1] * np.sin(a),
                                   v[0] * np.sin(a) + v[1] * np.cos(a), 0])

        def fuerza_cola():
            p = rot(cola_p0)
            k = theta.get_value() / 10.0          # 0 en equilibrio, >0 con la nariz arriba
            L = -0.55 + 1.9 * k                  # equilibrio: un poco hacia abajo
            col = C_COLA
            return vector(p, p + UP * L if abs(L) > 0.05 else p + UP * 0.05, col, ancho=10,
                          punta=0.26).set_z_index(20)
        fc = always_redraw(fuerza_cola)
        sust = always_redraw(lambda: vector(rot(cgp + RIGHT * 0.25 + UP * 0.1),
                                            rot(cgp + RIGHT * 0.25 + UP * 1.5), C_FUERZA,
                                            ancho=10, punta=0.26).set_z_index(20))
        sim = always_redraw(lambda: self.cg(rot(cgp)))
        e_ala = self.etiqueta("ala", C_FUERZA, cgp + RIGHT * 0.95 + UP * 1.4, size=24)
        e_cola = self.etiqueta("cola", C_COLA, cgp + np.array([-3.3, -0.85, 0]), size=24)
        horiz = DashedLine([-4.0, cgp[1], 0], [4.0, cgp[1], 0], color="#475569",
                           stroke_width=2, dash_length=0.1)
        nota = self.etiqueta("la nariz sube → la cola sube → la nariz baja", C_COLA,
                             [0, -1.6, 0], size=24)

        self.entrar_textos(barra, C_COLA, tit, fr, dt, FadeIn(avion, shift=UP * 0.3),
                           FadeIn(horiz))
        # "la cola equilibra el ala"
        self.hasta(t0, 1.6)
        self.play(GrowArrow(sust), FadeIn(sim), FadeIn(e_ala), run_time=0.4)
        self.play(FadeIn(fc), FadeIn(e_cola), run_time=0.4)
        # "si la nariz sube"
        self.hasta(t0, 3.7)
        self.play(theta.animate.set_value(10), rate_func=smooth, run_time=1.0)
        # "la cola la devuelve a su sitio"
        self.hasta(t0, 5.2)
        self.play(FadeIn(nota), run_time=0.3)
        self.play(theta.animate.set_value(0), rate_func=smooth, run_time=1.3)
        self.play(FadeIn(etq), FadeIn(ctl, scale=0.8), run_time=0.4)
        self.rellenar(t0, d)
        avion.clear_updaters()
        for m in (fc, sust, sim):
            m.clear_updaters()
        self.salir(tit, fr, dt, etq, ctl, avion, fc, sust, sim, e_ala, e_cola, horiz, nota)

    # ---------- 2. El ala hace de cola ----------
    def seccion_ala(self):
        t0, d = self.voz("ala")
        barra, tit, fr, dt, etq, ctl = self.textos(
            1, "Flecha", "Las puntas hacen de cola",
            "flecha + torsión (menos ángulo en las puntas)", "LA COLA VA",
            "REPARTIDA EN EL ALA", C_ALA)
        c = np.array([0, 1.55, 0])
        av, pi, pd = self.ala_volante(0.95, c)
        av.set_z_index(5)
        cgp = c + UP * 0.25
        sim = self.cg(cgp)
        linea = DashedLine([-3.9, cgp[1], 0], [3.9, cgp[1], 0], color=TEXTO_SEC,
                           stroke_width=3, dash_length=0.1).set_z_index(6)
        e_cg = self.etiqueta("centro de gravedad", TEXTO, cgp + UP * 0.55 + RIGHT * 1.9, size=22)
        brillo = VGroup(*[Circle(radius=0.45, color=C_ALA, stroke_width=5).move_to(p + UP * 0.25)
                          for p in (pi, pd)]).set_z_index(8)
        detras = VGroup(*[vector(np.array([p[0], cgp[1], 0]), p + UP * 0.6, C_ALA, ancho=6,
                                 punta=0.2) for p in (pi, pd)]).set_z_index(9)
        e_det = self.etiqueta("puntas detrás", C_ALA, [0, pd[1] - 0.15, 0], size=24)

        # secciones: raíz y punta (torsión), dibujadas a escala real
        def seccion(x0, ang, nombre, col):
            p = PerfilNACA("2410", cuerda=2.2, inicio=(0, 0)).contorno()
            p.rotate(-ang * DEGREES, about_point=ORIGIN)
            p.shift(np.array([x0, -1.05, 0]))
            ref = DashedLine([x0 - 0.3, -1.05, 0], [x0 + 2.4, -1.05, 0], color="#475569",
                             stroke_width=2, dash_length=0.08)
            txt = T(nombre, size=24, color=col, weight=BOLD).move_to([x0 + 1.1, -0.45, 0])
            return VGroup(ref, p, txt)
        raiz = seccion(-3.5, 5, "raíz: más ángulo", TEXTO)
        punta = seccion(0.95, 0, "punta: menos ángulo", C_ALA)

        self.entrar_textos(barra, C_ALA, tit, fr, dt, FadeIn(av, shift=UP * 0.3))
        # "las puntas quedan detrás del centro de gravedad"
        self.hasta(t0, 2.2)
        self.play(FadeIn(sim, scale=1.5), Create(linea), FadeIn(e_cg), run_time=0.5)
        self.play(Create(brillo), GrowArrow(detras[0]), GrowArrow(detras[1]), FadeIn(e_det),
                  run_time=0.6)
        # "y llevan menos ángulo"
        self.hasta(t0, 5.3)
        self.play(FadeIn(raiz, shift=UP * 0.2), FadeIn(punta, shift=UP * 0.2), run_time=0.6)
        # "así que funcionan como una cola repartida"
        self.hasta(t0, 7.5)
        self.play(Indicate(brillo, color=C_ALA, scale_factor=1.2), FadeIn(etq),
                  FadeIn(ctl, scale=0.8), run_time=0.8)
        self.rellenar(t0, d)
        self.salir(tit, fr, dt, etq, ctl, sim, linea, e_cg, brillo, detras, e_det, raiz, punta)
        self.av, self.c = av, c

    # ---------- 3. Girar sin timón ----------
    def seccion_giro(self):
        t0, d = self.voz("giro")
        barra, tit, fr, dt, etq, ctl = self.textos(
            2, "Sin timón", "Frena una punta para girar",
            "frenos partidos: se abren hacia arriba y hacia abajo", "SE CONTROLA CON",
            "FRENOS EN LA PUNTA", C_GIRO)
        av, c = self.av, self.c
        cgp = c + UP * 0.25
        ang = ValueTracker(0.0)
        aper = ValueTracker(0.0)
        pd0 = np.array([3.66, -1.2, 0]) * 0.95 + c

        def rot(p):
            a = ang.get_value() * DEGREES
            v = p - cgp
            return cgp + np.array([v[0] * np.cos(a) - v[1] * np.sin(a),
                                   v[0] * np.sin(a) + v[1] * np.cos(a), 0])

        av.ang = 0.0

        def girar(m):
            a = ang.get_value()
            m.rotate((a - m.ang) * DEGREES, about_point=cgp)
            m.ang = a
        av.add_updater(girar)

        def freno():
            f = freno_partido(pd0, s=1, apertura=aper.get_value())
            f.rotate(ang.get_value() * DEGREES, about_point=cgp)
            return f.set_z_index(7)
        fr_m = always_redraw(freno)

        def arrastre():
            p = rot(pd0 + LEFT * 0.4)
            a = ang.get_value() * DEGREES
            atras = np.array([np.sin(a), -np.cos(a), 0])
            L = 1.5 * aper.get_value()
            return vector(p, p + atras * max(L, 0.05), C_GIRO, ancho=10, punta=0.28).set_z_index(9)
        arr = always_redraw(arrastre)
        e_arr = self.etiqueta("más resistencia", C_GIRO, [2.45, -1.35, 0], size=24)
        giro = flecha_giro(cgp, 2.3, -PI / 2 + 0.55, -1.1, C_GIRO).set_z_index(9)
        e_giro = self.etiqueta("guiñada", C_GIRO, [0, -1.15, 0], size=24)
        cerrado = self.etiqueta("frenos partidos: dos placas que se abren", TEXTO_SEC,
                                [0, -1.85, 0], size=22)

        self.entrar_textos(barra, C_GIRO, tit, fr, dt)
        self.add(fr_m)
        # "para girar abre unos frenos partidos en una punta"
        self.hasta(t0, 1.2)
        self.play(aper.animate.set_value(1.0), FadeIn(cerrado), run_time=0.8)
        self.add(arr)
        self.play(FadeIn(e_arr), run_time=0.3)
        # "esa punta se retrasa y el avión gira"
        self.hasta(t0, 5.0)
        self.play(ang.animate.set_value(-18), Create(giro), FadeIn(e_giro), rate_func=smooth,
                  run_time=1.6)
        self.play(FadeIn(etq), FadeIn(ctl, scale=0.8), run_time=0.4)
        self.rellenar(t0, d)
        av.clear_updaters()
        fr_m.clear_updaters()
        arr.clear_updaters()
        self.salir(tit, fr, dt, etq, ctl, av, fr_m, arr, e_arr, giro, e_giro, cerrado)

    # ---------- Cierre ----------
    def cierre(self):
        datos = [("La cola", "equilibra y estabiliza", "cabeceo", C_COLA),
                 ("Flecha", "las puntas hacen de cola", "torsión", C_ALA),
                 ("Sin timón", "frena una punta", "guiñada", C_GIRO)]
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
        lema = T("Menos resistencia, muy poco margen", size=36, color=TEXTO,
                 weight=SEMIBOLD).next_to(tarjetas, DOWN, buff=0.45)
        p1 = T("¿Volarías", size=66, weight=HEAVY, font=F_TIT)
        p2 = T("en uno?", size=66, color=C_GIRO, weight=HEAVY, font=F_TIT)
        preg = VGroup(p1, p2).arrange(DOWN, buff=0.15).next_to(lema, DOWN, buff=0.7)
        com = T("Te leo en comentarios", size=32, color=TEXTO_SEC, weight=MEDIUM)
        com.next_to(preg, DOWN, buff=0.25)

        t0, d = self.voz("cierre")
        self.play(LaggedStart(*[FadeIn(t, shift=RIGHT * 0.5) for t in tarjetas], lag_ratio=0.25),
                  run_time=1.0)
        self.play(FadeIn(lema, shift=UP * 0.2), run_time=0.4)
        self.hasta(t0, 3.3)
        self.play(FadeIn(preg, shift=UP * 0.3, scale=1.1), run_time=0.5)
        self.play(FadeIn(com), run_time=0.3)
        self.rellenar(t0, d, margen=1.2)

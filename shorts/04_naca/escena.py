"""
Short 04: "Perfiles NACA: qué significan sus cifras".
Los perfiles se dibujan con las ecuaciones publicadas de la familia NACA (`PerfilNACA`),
a escala real (sin exagerar la curvatura ni el espesor).
Render (desde la raíz del repo):
  manim -qh --fps 30 shorts/04_naca/escena.py Naca
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403

C_CURV, C_ESP, C_CINCO = C_CABECEO, C_ALABEO, C_GUINADA
Y_CUERDA = -0.1
INICIO = (-3.5, Y_CUERDA)
Y_COD = 2.3


class Naca(ShortBase):
    VOZ_JSON = Path(__file__).parent / "voz.json"
    SUBS_DESDE = "curvatura"    # el gancho ya está escrito en pantalla
    SIN_SUBS_DESDE = "cierre"   # el cierre también

    def construct(self):
        self.iniciar()
        # estado del perfil (en las unidades del código): curvatura %, posición en décimas, espesor %
        self.m = ValueTracker(2.0)
        self.p = ValueTracker(4.0)
        self.t = ValueTracker(12.0)
        self.cinco = False
        self.resalte = {}          # índice de cifra -> color
        self.gancho()

        self.cabecera = T("PERFILES NACA", size=28, color=TEXTO_SEC,
                          weight=SEMIBOLD).move_to(UP * 6.85)
        self.barras = VGroup(*[RoundedRectangle(width=0.7, height=0.12, corner_radius=0.06,
                                                fill_color="#334155", fill_opacity=1,
                                                stroke_width=0) for _ in range(3)])
        self.barras.arrange(RIGHT, buff=0.15).move_to(UP * 6.4)
        self.play(FadeIn(self.cabecera, shift=DOWN * 0.2), FadeIn(self.barras), run_time=0.4)

        self.seccion_curvatura()
        self.seccion_espesor()
        self.seccion_cinco()
        self.cierre()

    # ---------- piezas que siguen a los trackers ----------
    def cifras(self):
        if self.cinco:
            return "23012"
        return f"{round(self.m.get_value())}{round(self.p.get_value())}" \
               f"{round(self.t.get_value()):02d}"

    def perfil(self):
        if self.cinco:
            return PerfilNACA("23012", cuerda=7.0, inicio=INICIO)
        m, p = self.m.get_value() / 100, self.p.get_value() / 10
        return PerfilNACA(("4", m, p), t=self.t.get_value() / 100, cuerda=7.0, inicio=INICIO)

    def codigo(self, tam=96):
        naca = T("NACA", size=tam, color=TEXTO_SEC, weight=HEAVY, font=F_TIT)
        digs = VGroup()
        for i, c in enumerate(self.cifras()):
            col = self.resalte.get(i, TEXTO)
            d = T(c, size=tam, color=BG if i in self.resalte else TEXTO, weight=HEAVY,
                  font=F_TIT)
            caja = RoundedRectangle(width=0.86 * tam / 96, height=1.15 * tam / 96,
                                    corner_radius=0.14, stroke_width=0, fill_color=col,
                                    fill_opacity=1 if i in self.resalte else 0)
            digs.add(VGroup(caja, d.move_to(caja)))
        digs.arrange(RIGHT, buff=0.04)
        return VGroup(naca, digs).arrange(RIGHT, buff=0.35).move_to([0, Y_COD, 0])

    def ala(self):
        return self.perfil().contorno().set_z_index(10)

    # ---------- Gancho ----------
    def gancho(self):
        campo = RoundedRectangle(width=7.4, height=1.7, corner_radius=0.25, fill_color=PANEL,
                                 fill_opacity=1, stroke_color="#334155", stroke_width=3)
        etq = T("contraseña:", size=34, color=TEXTO_SEC, weight=SEMIBOLD)
        etq.next_to(campo, UP, buff=0.2).align_to(campo, LEFT)
        cod = self.codigo(tam=92).move_to(campo)
        puntos = T("• • • • • • • •", size=80, color=TEXTO_SEC, weight=HEAVY).move_to(campo)
        grupo = VGroup(campo, etq).move_to(UP * 2.6)
        cod.move_to(campo)
        puntos.move_to(campo)
        P = PerfilNACA("2412", cuerda=7.0, inicio=(-3.5, -0.6))
        ala = P.contorno().set_z_index(10)
        txt = T("ES UN ALA", size=96, color=C_CINCO, weight=HEAVY, font=F_TIT)
        marco = RoundedRectangle(width=txt.width + 0.6, height=txt.height + 0.5,
                                 corner_radius=0.2, stroke_color=C_CINCO, stroke_width=10,
                                 fill_opacity=0)
        sello = VGroup(marco, txt.move_to(marco)).rotate(5 * DEGREES).move_to(DOWN * 2.6)

        t0, d = self.voz("gancho")
        self.play(FadeIn(grupo, shift=UP * 0.3), FadeIn(puntos), run_time=0.4)
        self.play(FadeOut(puntos, scale=0.8), FadeIn(cod, scale=1.2), run_time=0.45)
        self.hasta(0, 4.3)
        self.play(DrawBorderThenFill(ala), FadeIn(sello, scale=2.0), run_time=0.6)
        self.rellenar(t0, d, margen=-0.5)
        self.play(FadeOut(VGroup(grupo, cod, sello, ala), shift=UP * 0.6), run_time=0.35)

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

    def salir(self, *mobs):
        self.play(*[FadeOut(m, shift=LEFT * 0.6) for m in mobs], run_time=0.4)

    def etiqueta(self, texto, color, pos, size=26):
        t = T(texto, size=size, color=color, weight=BOLD)
        fondo = RoundedRectangle(width=t.width + 0.36, height=t.height + 0.24, corner_radius=0.14,
                                 fill_color=BG, fill_opacity=0.85, stroke_width=0)
        return VGroup(fondo, t).move_to(pos).set_z_index(30)

    # ---------- 1. Curvatura (cifras 1 y 2) ----------
    def seccion_curvatura(self):
        t0, d = self.voz("curvatura")
        barra, tit, fr, dt, etq, ctl = self.textos(
            0, "Curvatura", "Las dos primeras cifras",
            "cuerda: la recta del borde de ataque al de salida", "1.ª Y 2.ª CIFRA",
            "2 % · AL 40 %", C_CURV)

        self.cod = always_redraw(lambda: self.codigo())
        self.ala_m = always_redraw(self.ala)
        P0 = self.perfil()
        self.cuerda = P0.cuerda_linea().set_z_index(11)
        regla = VGroup(T("0 %", size=24, color=TEXTO_SEC, weight=SEMIBOLD)
                       .move_to(P0.p(0, 0) + DOWN * 0.95 + RIGHT * 0.2),
                       T("100 %", size=24, color=TEXTO_SEC, weight=SEMIBOLD)
                       .move_to(P0.p(1, 0) + DOWN * 0.95 + LEFT * 0.35),
                       T("cuerda", size=24, color=TEXTO_SEC, weight=SEMIBOLD)
                       .move_to([0, Y_CUERDA - 1.4, 0]))
        self.regla = regla
        escala = T("dibujado a escala real", size=22, color=TEXTO_SEC, weight=MEDIUM).move_to([2.3, Y_CUERDA - 1.85, 0])
        self.escala = escala
        nasa = self.etiqueta("NACA (1915–1958): antecesora de la NASA", TEXTO, [0, 1.3, 0], size=26)

        self.entrar_textos(barra, C_CURV, tit, fr, dt, FadeIn(self.cod, shift=DOWN * 0.2),
                           FadeIn(self.ala_m, shift=UP * 0.3))
        self.play(Create(self.cuerda), FadeIn(regla), FadeIn(escala), run_time=0.5)
        self.hasta(t0, 0.3)
        self.play(FadeIn(nasa, shift=UP * 0.2), run_time=0.4)

        # "La primera cifra es la curvatura máxima"
        self.hasta(t0, 5.15)
        self.resalte = {0: C_CURV}

        def media():
            return self.perfil().linea_media(C_CURV, ancho=5).set_z_index(12)
        self.media = always_redraw(media)

        def punto_max():
            P = self.perfil()
            x, y = P.max_curvatura()
            pt = P.p(x, y)
            dot = Dot(pt, radius=0.08, color=C_CURV)
            guia = Line(pt, [pt[0], 1.12, 0], color=C_CURV, stroke_width=3)
            lab = self.etiqueta(f"curvatura máx.: {self.m.get_value():.0f} % de la cuerda",
                                C_CURV, [0, 1.3, 0], size=26)
            lab.move_to([np.clip(pt[0], -3.7 + lab.width / 2, 3.7 - lab.width / 2), 1.3, 0])
            return VGroup(guia, dot, lab).set_z_index(20)
        self.pmax = always_redraw(punto_max)
        self.play(FadeOut(nasa), FadeIn(self.media), run_time=0.35)
        self.play(FadeIn(self.pmax), run_time=0.3)
        self.play(self.m.animate.set_value(6), rate_func=smooth, run_time=1.0)
        self.play(self.m.animate.set_value(2), rate_func=smooth, run_time=0.9)

        # "La segunda dice dónde está: al 40 %"
        self.hasta(t0, 9.8)
        self.resalte = {1: C_CURV}

        def marca_pos():
            P = self.perfil()
            x, y = P.max_curvatura()
            pt = P.p(x, y)
            lin = DashedLine([pt[0], Y_CUERDA - 0.62, 0], pt, color=C_CURV, stroke_width=3,
                             dash_length=0.08)
            lab = T(f"{10 * self.p.get_value():.0f} %", size=34, color=C_CURV, weight=HEAVY,
                    font=F_TIT).move_to([pt[0], Y_CUERDA - 0.95, 0])
            fondo = BackgroundRectangle(lab, color=BG, fill_opacity=1, buff=0.08)
            return VGroup(lin, fondo, lab).set_z_index(21)
        self.mpos = always_redraw(marca_pos)
        self.play(FadeIn(self.mpos), run_time=0.3)
        self.play(self.p.animate.set_value(2), rate_func=smooth, run_time=0.8)
        self.play(self.p.animate.set_value(6), rate_func=smooth, run_time=1.0)
        self.play(self.p.animate.set_value(4), rate_func=smooth, run_time=0.7)
        self.hasta(t0, 12.4)
        self.resalte = {0: C_CURV, 1: C_CURV}
        self.play(FadeIn(etq), FadeIn(ctl, scale=0.8), run_time=0.4)
        self.rellenar(t0, d)
        self.salir(tit, fr, dt, etq, ctl, self.pmax, self.mpos)
        self.remove(self.pmax, self.mpos)

    # ---------- 2. Espesor (cifras 3 y 4) ----------
    def seccion_espesor(self):
        t0, d = self.voz("espesor")
        barra, tit, fr, dt, etq, ctl = self.textos(
            1, "Espesor", "Las dos últimas cifras", "en el punto más grueso del perfil",
            "3.ª Y 4.ª CIFRA", "12 % DE ESPESOR", C_ESP)
        self.resalte = {2: C_ESP, 3: C_ESP}

        def cota():
            P = self.perfil()
            x, yi, ys = P.max_espesor()
            a, b = P.p(x, yi), P.p(x, ys)
            flecha = DoubleArrow(a + DOWN * 0.02, b + UP * 0.02, buff=0, color=C_ESP,
                                 stroke_width=5, tip_length=0.14,
                                 max_tip_length_to_length_ratio=0.45)
            lab = self.etiqueta(f"{self.t.get_value():.0f} %", C_ESP, b + UP * 0.45, size=32)
            return VGroup(flecha, lab).set_z_index(22)
        self.cota = always_redraw(cota)
        self.entrar_textos(barra, C_ESP, tit, fr, dt, FadeIn(self.cota))
        # "12 %"
        self.play(self.t.animate.set_value(24), rate_func=smooth, run_time=0.9)
        self.play(self.t.animate.set_value(6), rate_func=smooth, run_time=0.9)
        self.play(self.t.animate.set_value(12), rate_func=smooth, run_time=0.6)
        # "Si empieza por 00, el perfil es simétrico"
        self.hasta(t0, 3.5)
        self.resalte = {0: C_ESP, 1: C_ESP}
        self.play(self.m.animate.set_value(0), self.p.animate.set_value(0), rate_func=smooth,
                  run_time=0.8)
        sim = self.etiqueta("SIMÉTRICO: igual arriba que abajo", C_ESP, [0, 1.3, 0], size=28)
        self.hasta(t0, 5.35)
        self.play(FadeIn(sim, scale=1.2), run_time=0.35)
        self.hasta(t0, 5.9)
        self.play(FadeIn(etq), FadeIn(ctl, scale=0.8), run_time=0.4)
        self.rellenar(t0, d)
        self.salir(tit, fr, dt, etq, ctl, self.cota, sim)
        self.remove(self.cota)

    # ---------- 3. Serie de cinco cifras ----------
    def seccion_cinco(self):
        t0, d = self.voz("cinco")
        barra, tit, fr, dt, etq, ctl = self.textos(
            2, "5 cifras", "La curvatura, más adelante",
            "serie 230: curvatura máxima al 15 % de la cuerda", "EN LA SERIE DE 5 CIFRAS",
            "CURVATURA AL 15 %", C_CINCO)
        # 2412 como referencia (fantasma) y paso a 23012
        ref = PerfilNACA("2412", cuerda=7.0, inicio=INICIO)
        fantasma = ref.contorno().set_fill(opacity=0).set_stroke(C_CURV, width=3, opacity=0.8)
        fantasma.set_z_index(13)
        x4, y4 = ref.max_curvatura()
        m4 = ref.linea_media(C_CURV, ancho=3).set_stroke(opacity=0.7).set_z_index(12)
        lab4 = T("2412: 40 %", size=26, color=C_CURV, weight=BOLD)
        lab4.move_to([ref.p(x4, 0)[0], Y_CUERDA - 0.95, 0]).set_z_index(21)
        lin4 = DashedLine([ref.p(x4, 0)[0], Y_CUERDA - 0.62, 0], ref.p(x4, y4), color=C_CURV,
                          stroke_width=3, dash_length=0.08).set_z_index(21)

        self.m.set_value(2)
        self.cinco = True
        self.resalte = {}
        self.entrar_textos(barra, C_CINCO, tit, fr, dt, FadeOut(self.media))
        nuevo = PerfilNACA("23012", cuerda=7.0, inicio=INICIO)
        m5 = nuevo.linea_media(C_CINCO, ancho=5).set_z_index(12)
        x5, y5 = nuevo.max_curvatura()
        lin5 = DashedLine([nuevo.p(x5, 0)[0], Y_CUERDA - 0.62, 0], nuevo.p(x5, y5),
                          color=C_CINCO, stroke_width=3, dash_length=0.08).set_z_index(21)
        lab5 = T("15 %", size=34, color=C_CINCO, weight=HEAVY, font=F_TIT)
        lab5.move_to([nuevo.p(x5, 0)[0], Y_CUERDA - 0.95, 0]).set_z_index(21)
        dot5 = Dot(nuevo.p(x5, y5), radius=0.08, color=C_CINCO).set_z_index(22)
        leyenda = VGroup(self.etiqueta("— 2412", C_CURV, ORIGIN, size=24),
                         self.etiqueta("— 23012", C_CINCO, ORIGIN, size=24)).arrange(RIGHT, buff=0.3)
        leyenda.move_to([0, 1.3, 0])

        # "como el 23012"
        self.hasta(t0, 1.75)
        self.add(fantasma, m4)
        self.play(FadeIn(fantasma), FadeIn(m4), FadeIn(m5), FadeIn(leyenda), FadeOut(self.regla),
                  run_time=0.5)
        # "lleva la curvatura máxima más adelante: al 15 %"
        self.hasta(t0, 3.95)
        self.play(Create(lin4), FadeIn(lab4), run_time=0.4)
        flecha = Arrow([ref.p(x4, 0)[0], Y_CUERDA - 1.35, 0],
                       [nuevo.p(x5, 0)[0], Y_CUERDA - 1.35, 0], buff=0, color=C_CINCO,
                       stroke_width=7, max_tip_length_to_length_ratio=0.18).set_z_index(21)
        self.play(GrowArrow(flecha), run_time=0.6)
        self.hasta(t0, 6.8)
        self.play(Create(lin5), FadeIn(lab5, scale=1.3), FadeIn(dot5), run_time=0.4)
        self.play(FadeIn(etq), FadeIn(ctl, scale=0.8), run_time=0.4)
        self.rellenar(t0, d)
        self.salir(tit, fr, dt, etq, ctl, fantasma, m4, m5, lin4, lab4, lin5, lab5, dot5, flecha,
                   leyenda, self.ala_m, self.cuerda, self.cod, self.escala)
        self.remove(self.ala_m, self.cod)

    # ---------- Cierre ----------
    def cierre(self):
        datos = [("1.ª y 2.ª", "curvatura y dónde", "2 % · 40 %", C_CURV),
                 ("3.ª y 4.ª", "espesor máximo", "12 %", C_ESP),
                 ("5 cifras", "curvatura más adelante", "15 %", C_CINCO)]
        tarjetas = VGroup()
        for nom, desc, ctl, col in datos:
            fondo = RoundedRectangle(width=7.2, height=1.55, corner_radius=0.25, fill_color=PANEL,
                                     fill_opacity=1, stroke_color="#24324A", stroke_width=2)
            acento = RoundedRectangle(width=0.14, height=1.05, corner_radius=0.07, fill_color=col,
                                      fill_opacity=1, stroke_width=0)
            acento.move_to(fondo.get_left() + RIGHT * 0.35)
            n = T(nom, size=50, color=col, weight=HEAVY, font=F_TIT)
            dd = T(desc, size=30, color=TEXTO_SEC, weight=MEDIUM)
            txt = VGroup(n, dd).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
            txt.next_to(acento, RIGHT, buff=0.35)
            c = pastilla(T(ctl, size=28, color=col, weight=BOLD), col, relleno=0.12,
                         pad_x=0.22, pad_y=0.12)
            c.move_to(fondo.get_right() + LEFT * (c.width / 2 + 0.3))
            tarjetas.add(VGroup(fondo, acento, txt, c))
        tarjetas.arrange(DOWN, buff=0.3).move_to(UP * 3.3)

        lema = T("NACA 2412: cuatro cifras, un ala entera", size=34, color=TEXTO,
                 weight=SEMIBOLD).next_to(tarjetas, DOWN, buff=0.45)
        p1 = T("¿Qué perfil quieres", size=60, weight=HEAVY, font=F_TIT)
        p2 = T("que descifremos?", size=60, color=C_CINCO, weight=HEAVY, font=F_TIT)
        preg = VGroup(p1, p2).arrange(DOWN, buff=0.15).next_to(lema, DOWN, buff=0.7)
        com = T("Te leo en comentarios", size=32, color=TEXTO_SEC, weight=MEDIUM)
        com.next_to(preg, DOWN, buff=0.25)

        t0, d = self.voz("cierre")
        self.play(LaggedStart(*[FadeIn(t, shift=RIGHT * 0.5) for t in tarjetas], lag_ratio=0.25),
                  run_time=1.0)
        self.play(FadeIn(lema, shift=UP * 0.2), run_time=0.4)
        self.hasta(t0, 2.45)
        self.play(FadeIn(preg, shift=UP * 0.3, scale=1.1), run_time=0.5)
        self.play(FadeIn(com), run_time=0.3)
        self.rellenar(t0, d, margen=1.5)

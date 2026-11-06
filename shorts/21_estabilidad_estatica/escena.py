"""
Short 21 (narrado, voz Azure es-MX-JorgeMultilingualNeural): estabilidad estática.
- Estática = primera reacción tras una perturbación (hacia dónde tiende), no cómo vuelve.
- Canica: cuenco (estable), mesa (neutra), colina (inestable).
- Cabeceo: Cm frente a α. dCm/dα < 0 → estable (al subir α aparece un momento que baja el morro).
  El equilibrio está donde la recta corta Cm = 0 (hace falta Cm0 > 0).
- Depende del centro de gravedad (CG) respecto al punto neutro (PN): CG delante → estable;
  CG en el PN → neutro; CG detrás → inestable. Posiciones dibujadas como esquema.
Simplificación dicha en pantalla: solo cabeceo (en alabeo y guiñada existe lo mismo).
Render:  manim -qh --fps 60 shorts/21_estabilidad_estatica/escena.py EstabilidadEstatica
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403
from lib import avion as A  # noqa: E402
from lib.avion2d import lateral_2d  # noqa: E402

C_EST, C_NEU, C_INE = C_CABECEO, C_GUINADA, C_ALABEO
C_RAFAGA = "#CBD5E1"


def simbolo_cg(radio=0.17):
    """Símbolo clásico del centro de gravedad (círculo en cuartos blanco y negro)."""
    g = VGroup()
    for i in range(4):
        g.add(Sector(radius=radio, angle=PI / 2, start_angle=i * PI / 2,
                     fill_color=TEXTO if i % 2 == 0 else "#0F172A", fill_opacity=1,
                     stroke_width=0))
    g.add(Circle(radius=radio, stroke_color=TEXTO, stroke_width=2.5))
    return g


def rafaga(origen, dx=1.7, dy=1.3, color=C_RAFAGA):
    """Ráfaga ascendente: tres flechas cortas en diagonal."""
    g = VGroup()
    for k in range(3):
        o = np.array(origen) + np.array([0.6 * k, -0.33 * k, 0])
        g.add(Arrow(o, o + np.array([dx * 0.55, dy * 0.55, 0]), buff=0, color=color,
                    stroke_width=9, max_tip_length_to_length_ratio=0.3).set_opacity(0.85))
    return g


class Canica:
    """Panel con una superficie (cuenco, mesa o colina) y una canica que se mueve sobre ella."""
    def __init__(self, tipo, centro, color, ancho=2.3, k=0.55, r=0.17):
        self.tipo, self.color, self.a = tipo, color, ancho
        self.c = np.array([*centro[:2], 0.0])
        self.k = {"cuenco": k, "mesa": 0.0, "colina": -k}[tipo]
        self.u = ValueTracker(0.0)            # posición horizontal (−1 … 1, fracción de medio ancho)
        self.r = r

    def y(self, x):
        return self.k * (x / (self.a / 2)) ** 2 * (self.a / 2) * 0.55

    def dy(self, x):
        return 2 * self.k * x / (self.a / 2) * 0.55

    def superficie(self):
        xs = np.linspace(-self.a / 2, self.a / 2, 60)
        pts = [self.c + np.array([x, self.y(x), 0]) for x in xs]
        base = VMobject().set_points_smoothly(pts).set_stroke("#94A3B8", 8)
        return base

    def punto(self, u=None):
        x = (self.u.get_value() if u is None else u) * self.a / 2
        n = np.array([-self.dy(x), 1.0, 0])
        n /= np.linalg.norm(n)
        return self.c + np.array([x, self.y(x), 0]) + n * self.r

    def canica(self):
        return always_redraw(lambda: Circle(radius=self.r).set_fill(self.color, 1)
                             .set_stroke(TEXTO, 2).set_sheen(0.4, UL).move_to(self.punto()))

    def flecha(self):
        """Tendencia: hacia abajo de la pendiente (nada en la mesa)."""
        def f():
            x = self.u.get_value() * self.a / 2
            if self.tipo == "mesa" or abs(x) < 0.08:
                return VGroup()
            t = np.array([1.0, self.dy(x), 0])
            t /= np.linalg.norm(t)
            s = -np.sign(self.dy(x))
            p = self.punto() + np.array([0, self.r + 0.2, 0])
            return Arrow(p, p + t * s * 1.0, buff=0, color=self.color, stroke_width=10,
                         max_tip_length_to_length_ratio=0.4)
        return always_redraw(f)


class EstabilidadEstatica(ShortBase):
    VOZ_JSON = Path(__file__).parent / "voz.json"
    SUBS_DESDE = "b1"          # el gancho ya está escrito en pantalla
    SIN_SUBS_DESDE = "cierre"  # la pregunta final también

    def avion_cabeceo(self, ancho, centro, theta):
        """Avión de lado que cabecea `theta` (grados, ValueTracker) alrededor de su CG."""
        base = lateral_2d(ancho, (0, 0))
        c = np.array([*centro, 0])
        return always_redraw(lambda: base.copy().rotate(theta.get_value() * DEGREES,
                                                         about_point=ORIGIN).shift(c))

    def portada_mobs(self, theta):
        av = self.avion_cabeceo(6.6, (0.2, 0.2), theta)
        fondo = brillo(UP * 0.2, C_EST, 4.0, 0.9)
        raf = rafaga([-3.6, -2.2, 0])
        l1 = T("Si una ráfaga sube el morro,", size=48, weight=HEAVY, font=F_TIT)
        pal = T("¿VUELVE SOLO?", size=92, color=BG, weight=HEAVY, font=F_TIT)
        caja = RoundedRectangle(width=pal.width + 0.6, height=pal.height + 0.45, corner_radius=0.3,
                                fill_color=C_EST, fill_opacity=1, stroke_width=0).move_to(pal)
        dest = VGroup(caja, pal).rotate(-3 * DEGREES)
        preg = self.hud(VGroup(l1, dest).arrange(DOWN, buff=0.32).move_to(UP * 4.35))
        return fondo, av, raf, preg, dest

    def construct(self):
        self.iniciar()
        theta = ValueTracker(9.0)

        # ---------- Gancho (portada completa en t = 0) ----------
        fondo, av, raf, preg, dest = self.portada_mobs(theta)
        sello = self.sello("ESTABILIDAD ESTÁTICA", C_EST, DOWN * 3.9, size=50)
        self.portada(fondo, av, raf, preg)
        self.wait(0.2)
        self.sonido("whoosh_suave", -10)
        self.play(theta.animate.set_value(14), raf.animate.shift(UR * 0.25), run_time=0.7,
                  rate_func=rate_functions.ease_out_sine)
        self.poner_sello(sello)
        self.pulso(dest, 1.06)
        self.play(theta.animate.set_value(9), run_time=0.7, rate_func=rate_functions.ease_in_out_sine)

        # ---------- 1. Primera reacción (canicas) ----------
        t0, d = self.voz("b1")
        self.dejar(preg, sello, av, raf, fondo)
        self.play(self.poner_cabecera("ESTABILIDAD ESTÁTICA", 3), run_time=0.01)
        barra, tit, fr, dt = self.bloque(0, "¿Hacia dónde?", "Solo mira la primera reacción",
                                         C_EST, dato="justo después de la perturbación",
                                         resaltar=["primera"])
        kw = dict(ancho=2.55, k=0.8, r=0.25)
        cs = [Canica("cuenco", (-2.85, 0.5), C_EST, **kw), Canica("mesa", (0, 0.5), C_NEU, **kw),
              Canica("colina", (2.85, 0.5), C_INE, **kw)]
        sup = VGroup(*[c.superficie() for c in cs])
        bolas = [c.canica() for c in cs]
        flechas = [c.flecha() for c in cs]
        nombres = [("ESTABLE", "vuelve"), ("NEUTRA", "se queda"), ("INESTABLE", "se escapa")]
        rot = VGroup()
        for c, (n, v) in zip(cs, nombres):
            rot.add(VGroup(T(n, size=36, color=c.color, weight=HEAVY, font=F_TIT),
                           T(v, size=30, color=TEXTO_SEC, weight=MEDIUM))
                    .arrange(DOWN, buff=0.1).move_to(c.c + DOWN * 1.55))
        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.2), barra.animate.set_fill(C_EST),
                    FadeIn(sup, shift=UP * 0.3), *[FadeIn(b) for b in bolas], run_time=0.6)
        self.add(*flechas)
        self.entrar_palabras(fr)
        self.play(FadeIn(dt), run_time=0.3)
        # «Como una canica»: todas reciben el mismo empujón
        self.hasta(t0, d * 0.36)
        self.sonido("tic", -8)
        self.play(*[c.u.animate.set_value(0.55) for c in cs], run_time=0.5,
                  rate_func=rate_functions.ease_out_cubic)
        # «en un cuenco vuelve»
        self.hasta(t0, d * 0.5)
        self.sonido("pop", -9)
        self.play(FadeIn(rot[0], shift=UP * 0.2), cs[0].u.animate.set_value(0.0), run_time=0.9,
                  rate_func=rate_functions.ease_in_out_sine)
        # «en una mesa se queda»
        self.hasta(t0, d * 0.66)
        self.sonido("pop", -9)
        self.play(FadeIn(rot[1], shift=UP * 0.2), run_time=0.4)
        self.pulso(bolas[1], 1.2, 0.4)
        # «en una colina se escapa»
        self.hasta(t0, d * 0.8)
        self.sonido("pop", -9)
        self.play(FadeIn(rot[2], shift=UP * 0.2), cs[2].u.animate.set_value(0.85), run_time=0.8,
                  rate_func=rate_functions.ease_in_quad)
        self.rellenar(t0, d, margen=-0.1)

        # ---------- 2. La gráfica Cm–α ----------
        t0, d = self.voz("b2")
        self.dejar(tit, fr, dt, sup, *bolas, *flechas, rot)
        barra, tit, fr, dt = self.bloque(1, "La gráfica", "Pendiente negativa: estable",
                                         C_EST, dato="Cm: momento de cabeceo · α: ángulo de ataque",
                                         resaltar=["negativa"])
        ax = Axes(x_range=[-2, 14, 2], y_range=[-1, 1, 0.5], x_length=7.4, y_length=4.4,
                  tips=True, axis_config=dict(color="#64748B", stroke_width=3,
                                              include_ticks=False, tip_length=0.2))
        ax.move_to([0.0, 0.25, 0])
        ex = T("α", size=40, color=TEXTO, weight=BOLD).next_to(ax.x_axis.get_end(), DOWN, buff=0.15)
        ey = T("Cm", size=34, color=TEXTO, weight=BOLD).next_to(ax.y_axis.get_end(), LEFT, buff=0.15)
        sube = T("morro arriba", size=24, color=TEXTO_SEC, weight=MEDIUM)
        sube.next_to(ax.c2p(0, 0.85), RIGHT, buff=0.25)
        baja = T("morro abajo", size=24, color=TEXTO_SEC, weight=MEDIUM)
        baja.next_to(ax.c2p(0, -0.85), RIGHT, buff=0.25)
        A_EQ, K = 5.0, 0.1
        recta = ax.plot(lambda a: K * (A_EQ - a), x_range=[-2, 13.5], color=C_EST, stroke_width=8)
        alfa = ValueTracker(A_EQ)
        punto = always_redraw(lambda: Dot(ax.c2p(alfa.get_value(), K * (A_EQ - alfa.get_value())),
                                          radius=0.13, color=TEXTO).set_stroke(C_EST, 4))
        guia = always_redraw(lambda: DashedLine(
            ax.c2p(alfa.get_value(), 0), ax.c2p(alfa.get_value(), K * (A_EQ - alfa.get_value())),
            color=TEXTO_SEC, stroke_width=3, dash_length=0.07))
        eq = self.etiqueta("EQUILIBRIO", TEXTO, ax.c2p(A_EQ, 0) + UP * 0.45 + RIGHT * 0.3, size=22)
        # avioncito en la zona vacía de la gráfica: cabecea con el momento
        th2 = ValueTracker(0.0)
        mini = self.avion_cabeceo(2.5, tuple(ax.c2p(10.3, 0.55)[:2]), th2)

        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.2), barra.animate.set_fill(C_EST),
                    FadeIn(ax), FadeIn(ex), FadeIn(ey), FadeIn(sube), FadeIn(baja), run_time=0.6)
        self.sonido("subida", -12)
        self.play(Create(recta), run_time=0.8)
        self.add(guia, punto)
        self.play(FadeIn(eq, scale=1.2), FadeIn(mini), run_time=0.35)
        # «si al subir el ángulo de ataque…»
        self.hasta(t0, d * 0.22)
        self.sonido("whoosh_suave", -12)
        self.play(alfa.animate.set_value(10.5), th2.animate.set_value(10), run_time=1.3,
                  rate_func=rate_functions.ease_in_out_sine)
        # «…aparece un momento que baja el morro»
        cm = self.etiqueta("Cm < 0: BAJA EL MORRO", C_EST, ax.c2p(9.0, -1.0), size=26)
        giro = always_redraw(lambda: flecha_giro(ax.c2p(10.3, 0.55), 1.45, 0.45, -0.75, C_EST))
        self.sonido("pop", -8)
        self.play(FadeIn(cm, shift=UP * 0.15), Create(giro), run_time=0.45)
        self.play(th2.animate.set_value(0), alfa.animate.set_value(A_EQ), run_time=1.1,
                  rate_func=rate_functions.ease_in_out_sine)
        # «la pendiente es negativa. Es estable.»
        self.entrar_palabras(fr)
        self.play(FadeIn(dt), Indicate(recta, color=C_EST, scale_factor=1.04), run_time=0.5)
        self.rellenar(t0, d, margen=-0.1)

        # ---------- 3. Centro de gravedad y punto neutro ----------
        t0, d = self.voz("b3")
        self.dejar(tit, fr, dt, ax, ex, ey, sube, baja, recta, punto, guia, eq, mini, cm, giro)
        barra, tit, fr, dt = self.bloque(2, "El CG manda", "CG delante del punto neutro: estable",
                                         C_NEU, dato="esquema · solo cabeceo; en alabeo y guiñada pasa igual",
                                         resaltar=["delante"])
        Y_AV = 1.0
        av = lateral_2d(7.2, (0.0, Y_AV))
        X_PN = A.X_CG + 1.6
        x_cg = ValueTracker(A.X_CG - 1.0)          # metros desde el morro (menos = más adelante)
        p_pn = av.a_pantalla(X_PN, 0, -0.2)
        pn = VGroup(Triangle(fill_color=C_NEU, fill_opacity=1, stroke_width=0).scale(0.16)
                    .rotate(PI).move_to(p_pn + DOWN * 1.15),
                    DashedLine(p_pn + UP * 0.6, p_pn + DOWN * 1.0, color=C_NEU, stroke_width=3,
                               dash_length=0.08))
        pn_txt = T("PUNTO NEUTRO", size=24, color=C_NEU, weight=HEAVY).next_to(pn[0], DOWN, buff=0.1)
        cg = always_redraw(lambda: simbolo_cg().move_to(av.a_pantalla(x_cg.get_value(), 0, 0.4)))
        cg_txt = always_redraw(lambda: self.etiqueta("CG", TEXTO, ORIGIN, size=26)
                               .next_to(av.a_pantalla(x_cg.get_value(), 0, 0.4), UP, buff=0.75))

        def estado():
            m = X_PN - x_cg.get_value()            # > 0: CG delante del PN
            if m > 0.3:
                return "ESTABLE", C_EST
            if m > -0.3:
                return "NEUTRO", C_NEU
            return "INESTABLE", C_INE

        # gráfica pequeña: la pendiente de Cm–α sigue al margen estático
        ax2 = Axes(x_range=[-1, 1, 1], y_range=[-1, 1, 1], x_length=3.0, y_length=1.5, tips=False,
                   axis_config=dict(color="#64748B", stroke_width=2.5, include_ticks=False))
        ax2.move_to([-1.9, -1.55, 0])
        l2 = VGroup(T("Cm", size=22, color=TEXTO_SEC, weight=BOLD).next_to(ax2.y_axis.get_top(), LEFT, buff=0.08),
                    T("α", size=26, color=TEXTO_SEC, weight=BOLD).next_to(ax2.x_axis, RIGHT, buff=0.08))

        def recta2():
            m = X_PN - x_cg.get_value()
            pend = -np.clip(m / 2.2, -1, 1) * 0.85
            _, col = estado()
            return Line(ax2.c2p(-0.95, -0.95 * pend), ax2.c2p(0.95, 0.95 * pend),
                        color=col, stroke_width=7)
        r2 = always_redraw(recta2)

        def rotulo():
            n, col = estado()
            return pastilla(T(n, size=40, color=col, weight=HEAVY, font=F_TIT), col).move_to([1.95, -1.55, 0])
        rot2 = always_redraw(rotulo)

        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.2), barra.animate.set_fill(C_NEU),
                    FadeIn(av, shift=UP * 0.3), run_time=0.6)
        self.play(FadeIn(pn), FadeIn(pn_txt), FadeIn(cg, scale=1.4), FadeIn(cg_txt), run_time=0.4)
        self.entrar_palabras(fr)
        self.play(FadeIn(dt), FadeIn(ax2), FadeIn(l2), FadeIn(r2), FadeIn(rot2), run_time=0.4)
        # «por delante del punto neutro, estable» (ya está delante)
        self.hasta(t0, d * 0.3)
        self.pulso(cg, 1.3, 0.4)
        # «justo encima, neutro»
        self.hasta(t0, d * 0.58)
        self.sonido("tic", -8)
        self.play(x_cg.animate.set_value(X_PN), run_time=0.8, rate_func=rate_functions.ease_in_out_sine)
        # «por detrás, inestable»
        self.hasta(t0, d * 0.76)
        self.sonido("tic", -8)
        self.play(x_cg.animate.set_value(X_PN + 1.3), run_time=0.8,
                  rate_func=rate_functions.ease_in_out_sine)
        self.rellenar(t0, d, margen=-0.1)

        # ---------- Cierre ----------
        t0, d = self.voz("cierre")
        self.dejar(tit, fr, dt, av, pn, pn_txt, cg, cg_txt, ax2, l2, r2, rot2, self.tema, self.barras)
        resumen = VGroup()
        for (n, v), col, sim in zip(nombres, (C_EST, C_NEU, C_INE), ("cuenco", "mesa", "colina")):
            cc = Canica(sim, (0, 0), col, ancho=2.2, k=0.7, r=0.22)
            cc.u.set_value({"cuenco": 0.0, "mesa": 0.0, "colina": 0.7}[sim])
            icono = VGroup(cc.superficie(), Circle(radius=0.22).set_fill(col, 1).set_stroke(TEXTO, 2)
                           .move_to(cc.punto()))
            resumen.add(VGroup(icono, T(v.upper(), size=36, color=col, weight=HEAVY, font=F_TIT))
                        .arrange(DOWN, buff=0.25))
        resumen.arrange(RIGHT, buff=0.5).move_to([0, 1.9, 0])
        preg2 = self.hud(frase_cinetica("¿Sabías que algunos cazas son inestables a propósito?",
                                        size=56, resaltar=["inestables"], color_resalte=C_INE)
                         .move_to(DOWN * 1.0))
        nota = self.hud(T("los mantiene en el aire la computadora de vuelo", size=28,
                          color=TEXTO_SEC, weight=MEDIUM).next_to(preg2, DOWN, buff=0.35))
        self.cambio(LaggedStart(*[FadeIn(r, shift=UP * 0.3) for r in resumen], lag_ratio=0.3),
                    FadeIn(preg2, shift=UP * 0.3, scale=1.1), run_time=0.7)
        self.play(FadeIn(nota), run_time=0.3)
        self.pulso(resumen[2], 1.1)
        self.hasta(t0, d * 0.62)
        self.pulso(preg2, 1.05)
        # vuelve a la imagen del gancho (el bucle enlaza)
        self.hasta(t0, d - 0.75)
        theta.set_value(9.0)
        fondo, av0, raf0, preg0, _ = self.portada_mobs(theta)
        self.dejar(resumen, preg2, nota)
        self.cambio(FadeIn(fondo), FadeIn(av0), FadeIn(raf0), FadeIn(preg0), run_time=0.45,
                    desplazar=UP * 0.6)
        self.wait(0.3)

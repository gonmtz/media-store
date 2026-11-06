"""
Short 22 (narrado, voz Azure es-MX-JorgeMultilingualNeural): estabilidad dinámica.
- Dinámica = cómo evoluciona la respuesta con el tiempo, x(t) = A·e^(σt)·cos(ωt).
  σ < 0: estable (directa si ω = 0, oscilación amortiguada si no); σ = 0: neutra;
  σ > 0: inestable. Se puede ser estable estáticamente e inestable dinámicamente.
- Modos del avión: fugoide (altura ↔ velocidad, periodo de decenas de segundos, poco amortiguado)
  y balanceo holandés (guiñada + alabeo acoplados, periodo de pocos segundos).
Curvas ilustrativas (formas típicas, no de un avión concreto); el avión cabecea con la curva.
Render:  manim -qh --fps 60 shorts/22_estabilidad_dinamica/escena.py EstabilidadDinamica
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403
from lib.avion2d import lateral_2d, superior_2d, frontal_2d  # noqa: E402

C_EST, C_NEU, C_INE = C_CABECEO, C_GUINADA, C_ALABEO
W = 2.2                      # rad/s de las curvas de ejemplo
T_MAX = 10.0
Y_AV, Y_GR = 2.05, -0.5     # avión y gráfica (iguales en la portada y en los bloques)


def amortiguada(t):
    return 0.85 * np.exp(-0.32 * t) * np.cos(W * t)


def directa(t):
    return 0.85 * np.exp(-0.75 * t)


def neutra(t):
    return 0.6 * np.cos(W * t)


def creciente(t):
    return 0.25 * np.exp(0.15 * t) * np.cos(W * t)


class EstabilidadDinamica(ShortBase):
    VOZ_JSON = Path(__file__).parent / "voz.json"
    SUBS_DESDE = "b1"
    SIN_SUBS_DESDE = "cierre"

    # ---------- piezas comunes ----------
    def grafica(self):
        ax = Axes(x_range=[0, T_MAX, 1], y_range=[-1.2, 1.2, 0.5], x_length=7.6, y_length=3.3,
                  tips=True, axis_config=dict(color="#64748B", stroke_width=3,
                                              include_ticks=False, tip_length=0.2))
        ax.move_to([0.0, Y_GR, 0])
        et = VGroup(T("tiempo", size=24, color=TEXTO_SEC, weight=MEDIUM)
                    .next_to(ax.x_axis.get_end(), DOWN, buff=0.12).shift(LEFT * 0.4),
                    T("perturbación", size=24, color=TEXTO_SEC, weight=MEDIUM)
                    .next_to(ax.y_axis.get_top(), RIGHT, buff=0.15))
        return ax, et

    def traza(self, ax, f, color, tt, ancho=7):
        def dib():
            t = max(tt.get_value(), 0.02)
            c = ax.plot(f, x_range=[0, t, 0.02], color=color, stroke_width=ancho)
            punta = Dot(ax.c2p(t, f(t)), radius=0.1, color=TEXTO).set_stroke(color, 4)
            return VGroup(c, punta)
        return always_redraw(dib)

    def avion(self, f, tt, ancho=4.4):
        base = lateral_2d(ancho, (0, 0))
        c = np.array([0.0, Y_AV, 0])
        return always_redraw(lambda: base.copy()
                             .rotate(13 * f(tt.get_value()) * DEGREES, about_point=ORIGIN).shift(c))

    def portada_mobs(self):
        ax, et = self.grafica()
        tt = ValueTracker(T_MAX * 0.62)
        tr = self.traza(ax, amortiguada, C_EST, tt)
        av = self.avion(amortiguada, tt)
        fondo = brillo([0, Y_AV - 0.6, 0], C_EST, 3.4, 0.9)
        l1 = T("Volver no basta.", size=54, weight=HEAVY, font=F_TIT)
        pal = T("¿CÓMO VUELVE?", size=92, color=BG, weight=HEAVY, font=F_TIT)
        caja = RoundedRectangle(width=pal.width + 0.6, height=pal.height + 0.45, corner_radius=0.3,
                                fill_color=C_NEU, fill_opacity=1, stroke_width=0).move_to(pal)
        dest = VGroup(caja, pal).rotate(-3 * DEGREES)
        preg = self.hud(VGroup(l1, dest).arrange(DOWN, buff=0.3).move_to(UP * 4.45))
        return dict(ax=ax, et=et, tt=tt, tr=tr, av=av, fondo=fondo, preg=preg, dest=dest)

    def ajustar_titulo(self, tit):
        if tit.width > ANCHO_MAX:
            tit.scale_to_fit_width(ANCHO_MAX)
        return tit

    # ---------- escena ----------
    def construct(self):
        self.iniciar()
        P = self.portada_mobs()
        ax, et, tt = P["ax"], P["et"], P["tt"]

        # ---------- Gancho (portada completa en t = 0) ----------
        sello = self.sello("ESTABILIDAD DINÁMICA", C_EST, DOWN * 3.95, size=50)
        self.portada(P["fondo"], ax, et, P["tr"], P["av"], P["preg"])
        self.wait(0.15)
        self.play(tt.animate.set_value(T_MAX * 0.8), run_time=0.8, rate_func=linear)
        self.poner_sello(sello)
        self.pulso(P["dest"], 1.06)
        self.play(tt.animate.set_value(T_MAX), run_time=0.6, rate_func=linear)

        # ---------- 1. Estable ----------
        t0, d = self.voz("b1")
        self.dejar(P["preg"], sello, P["tr"], P["av"])
        self.play(self.poner_cabecera("ESTABILIDAD DINÁMICA", 3), run_time=0.01)
        barra, tit, fr, dt = self.bloque(0, "Estable", "La perturbación se apaga", C_EST,
                                         dato="directa o oscilando cada vez menos",
                                         resaltar=["apaga"])
        t1 = ValueTracker(0.0)
        dir_ = self.traza(ax, directa, C_EST, t1, ancho=5)
        av = self.avion(directa, t1)
        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.2), barra.animate.set_fill(C_EST),
                    FadeIn(av), run_time=0.6)
        self.add(dir_)
        self.entrar_palabras(fr)
        # «mira la respuesta en el tiempo»: primero la directa (sin oscilar)
        self.sonido("subida", -12)
        self.play(t1.animate.set_value(T_MAX), run_time=1.6, rate_func=linear)
        e1 = self.etiqueta("DIRECTA", C_EST, ax.c2p(2.3, 0.75), size=24)
        self.play(FadeIn(e1, scale=1.2), run_time=0.3)
        # «directa o oscilando cada vez menos»
        self.hasta(t0, d * 0.48)
        t2 = ValueTracker(0.0)
        osc = self.traza(ax, amortiguada, C_EST, t2)
        env = VGroup(*[ax.plot(lambda t, s=s: s * 0.85 * np.exp(-0.32 * t), x_range=[0, T_MAX],
                               color=C_EST, stroke_width=3).set_opacity(0.0) for s in (1, -1)])
        env_d = VGroup(*[DashedVMobject(e.copy().set_stroke(opacity=0.55).set_fill(opacity=0), num_dashes=40) for e in env])
        av2 = self.avion(amortiguada, t2)
        dir_.clear_updaters()
        self.play(FadeOut(av), FadeIn(av2), dir_.animate.set_stroke(opacity=0.35),
                  FadeIn(dt), run_time=0.35)
        self.add(osc)
        self.play(t2.animate.set_value(T_MAX), Create(env_d), run_time=2.6, rate_func=linear)
        e2 = self.etiqueta("OSCILANDO CADA VEZ MENOS", C_EST, ax.c2p(6.2, -0.95), size=24)
        self.sonido("pop", -9)
        self.play(FadeIn(e2, scale=1.2), run_time=0.3)
        self.rellenar(t0, d, margen=-0.1)

        # ---------- 2. Neutra e inestable ----------
        t0, d = self.voz("b2")
        self.dejar(tit, fr, dt, dir_, osc, env_d, e1, e2, av2)
        barra, tit, fr, dt = self.bloque(1, "Neutra o inestable", "Siempre igual… o cada vez más",
                                         C_INE, dato="ser estable estáticamente no basta",
                                         resaltar=["más"])
        self.ajustar_titulo(tit)
        t3 = ValueTracker(0.0)
        neu = self.traza(ax, neutra, C_NEU, t3)
        av3 = self.avion(neutra, t3)
        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.2), barra.animate.set_fill(C_INE),
                    FadeIn(av3), run_time=0.6)
        self.add(neu)
        self.play(t3.animate.set_value(T_MAX), run_time=1.6, rate_func=linear)
        e3 = self.etiqueta("NEUTRA: SIEMPRE IGUAL", C_NEU, ax.c2p(3.3, 1.12), size=24)
        self.sonido("pop", -9)
        self.play(FadeIn(e3, scale=1.2), run_time=0.3)
        # «si cada vaivén crece, es inestable…»
        self.hasta(t0, d * 0.32)
        t4 = ValueTracker(0.0)
        ine = self.traza(ax, creciente, C_INE, t4, ancho=8)
        av4 = self.avion(creciente, t4)
        neu.clear_updaters()
        self.play(FadeOut(av3), FadeIn(av4), neu.animate.set_stroke(opacity=0.3), FadeOut(e3), run_time=0.3)
        self.add(ine)
        self.entrar_palabras(fr)
        self.play(t4.animate.set_value(T_MAX), run_time=2.4, rate_func=rate_functions.ease_in_sine)
        e4 = self.etiqueta("INESTABLE: CRECE", C_INE, ax.c2p(5.0, -1.05), size=24)
        self.sonido("golpe", -10)
        self.play(FadeIn(e4, scale=1.3), FadeIn(dt), run_time=0.35)
        self.rellenar(t0, d, margen=-0.1)

        # ---------- 3. Los modos del avión ----------
        t0, d = self.voz("b3")
        self.dejar(tit, fr, dt, neu, ine, e4, av4, ax, et, P["fondo"])
        barra, tit, fr, dt = self.bloque(2, "Sus modos", "Cada avión tiene los suyos", C_NEU,
                                         dato="los dos más conocidos (hay más)",
                                         resaltar=["suyos"])
        # fugoide: trayectoria ondulada lenta, a la vez cambia altura y velocidad
        Y_F, AMP, XF = 2.45, 0.4, 3.3
        s = ValueTracker(0.0)

        def y_tray(x):
            return Y_F + AMP * np.sin(2 * PI * (x + XF) / (2 * XF))
        tray = DashedVMobject(FunctionGraph(y_tray, x_range=[-XF - 0.6, XF + 0.6], color=C_NEU,
                                            stroke_width=3), num_dashes=45).set_opacity(0.6)
        base_f = lateral_2d(1.9, (0, 0))

        def av_fugoide():
            x = -XF + 2 * XF * s.get_value()
            pend = AMP * PI / XF * np.cos(2 * PI * (x + XF) / (2 * XF))
            return base_f.copy().rotate(np.arctan(pend) * 0.8, about_point=ORIGIN).move_to([x, y_tray(x), 0])
        avf = always_redraw(av_fugoide)
        r_f = VGroup(T("FUGOIDE", size=34, color=C_NEU, weight=HEAVY, font=F_TIT),
                     T("altura ↔ velocidad · ciclos de decenas de segundos", size=22,
                       color=TEXTO_SEC, weight=MEDIUM)).arrange(DOWN, buff=0.08).move_to([0, 1.4, 0])
        # balanceo holandés: guiñada y alabeo a la vez, rápido
        ph = ValueTracker(0.0)
        sup = superior_2d(2.25, (0, 0))
        fro = frontal_2d(3.3, (0, 0))
        c_sup, c_fro = np.array([-2.0, -1.05, 0]), np.array([1.85, -1.0, 0])
        av_s = always_redraw(lambda: sup.copy().rotate(10 * np.sin(ph.get_value()) * DEGREES,
                                                       about_point=ORIGIN).shift(c_sup))
        av_r = always_redraw(lambda: fro.copy().rotate(14 * np.sin(ph.get_value() - PI / 2) * DEGREES,
                                                       about_point=ORIGIN).shift(c_fro))
        r_h = VGroup(T("BALANCEO HOLANDÉS", size=34, color=C_INE, weight=HEAVY, font=F_TIT),
                     T("guiñada + alabeo · pocos segundos", size=22, color=TEXTO_SEC,
                       weight=MEDIUM)).arrange(DOWN, buff=0.08).move_to([0, 0.45, 0])
        vistas = VGroup(T("desde arriba", size=20, color=TEXTO_SEC, weight=MEDIUM).move_to(c_sup + DOWN * 1.05),
                        T("de frente", size=20, color=TEXTO_SEC, weight=MEDIUM).move_to(c_fro + DOWN * 1.05))

        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.2), barra.animate.set_fill(C_NEU),
                    FadeIn(tray), FadeIn(avf), FadeIn(r_f, shift=UP * 0.2), run_time=0.6)
        self.entrar_palabras(fr)
        # «el fugoide sube y baja en ciclos lentos»
        self.hasta(t0, d * 0.2)
        self.play(s.animate.set_value(1.0), run_time=2.6, rate_func=linear)
        # «el balanceo holandés guiña y alabea en pocos segundos»
        self.hasta(t0, d * 0.54)
        self.sonido("whoosh_suave", -12)
        self.play(FadeIn(av_s), FadeIn(av_r), FadeIn(r_h, shift=UP * 0.2),
                  FadeIn(dt), s.animate.set_value(0.0), tray.animate.set_opacity(0.25),
                  r_f.animate.set_opacity(0.45), run_time=0.4)
        self.play(ph.animate.set_value(6 * PI), run_time=3.0, rate_func=linear)
        self.rellenar(t0, d, margen=-0.1)

        # ---------- Cierre ----------
        t0, d = self.voz("cierre")
        self.dejar(tit, fr, dt, tray, avf, r_f, av_s, av_r, r_h, self.tema, self.barras)
        tarjetas = VGroup()
        for nom, txt, col in (("ESTÁTICA", "hacia dónde va", C_NEU), ("DINÁMICA", "cómo llega", C_EST)):
            fondo = RoundedRectangle(width=7.4, height=1.5, corner_radius=0.25, fill_color=PANEL,
                                     fill_opacity=1, stroke_color="#24324A", stroke_width=2)
            n = T(nom, size=52, color=col, weight=HEAVY, font=F_TIT)
            t_ = T(txt, size=36, color=TEXTO, weight=BOLD)
            fila = VGroup(n, t_).arrange(RIGHT, buff=0.4).move_to(fondo)
            tarjetas.add(VGroup(fondo, fila))
        tarjetas.arrange(DOWN, buff=0.3).move_to([0, 2.3, 0])
        preg2 = self.hud(frase_cinetica("¿Qué modo quieres ver en detalle?", size=60,
                                        resaltar=["modo"], color_resalte=C_NEU).move_to(DOWN * 1.1))
        self.cambio(LaggedStart(FadeIn(tarjetas[0], shift=RIGHT * 0.4),
                                FadeIn(tarjetas[1], shift=RIGHT * 0.4), lag_ratio=0.5), run_time=0.7)
        self.entrar_palabras(preg2)
        self.hasta(t0, d * 0.4)
        self.pulso(tarjetas[1], 1.05)
        # vuelve a la imagen del gancho (el bucle enlaza)
        self.hasta(t0, d - 0.7)
        Q = self.portada_mobs()
        self.dejar(tarjetas, preg2)
        self.cambio(FadeIn(Q["fondo"]), FadeIn(Q["ax"]), FadeIn(Q["et"]), FadeIn(Q["tr"]),
                    FadeIn(Q["av"]), FadeIn(Q["preg"]), run_time=0.45, desplazar=UP * 0.6)
        self.wait(0.3)

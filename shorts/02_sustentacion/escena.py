"""
Short 02: "Sustentación: el mito del tiempo de tránsito igual".
El flujo se calcula (perfil de Joukowski, flujo potencial 2D con condición de Kutta):
las partículas, las líneas de corriente y las flechas de presión salen del modelo.
Render (desde la raíz del repo):
  manim -qh --fps 30 shorts/02_sustentacion/escena.py Sustentacion
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403

C_MITO, C_NEWTON, C_PRESION = C_CABECEO, C_ALABEO, C_GUINADA
LINEA = "#475569"


class Sustentacion(ShortBase):
    VOZ_JSON = Path(__file__).parent / "voz.json"
    SUBS_DESDE = "mito"         # el gancho ya está escrito en pantalla
    SIN_SUBS_DESDE = "cierre"   # la pregunta final también

    def construct(self):
        self.iniciar()
        self.perfil = Perfil(alfa=6, mu=complex(-0.09, 0.06), escala=1.45, centro=(0.0, 0.5))
        self.te = self.perfil.borde_salida()
        self.le = self.perfil.borde_ataque()
        self.gancho()

        self.cabecera = T("EL MITO DE LA SUSTENTACIÓN", size=28, color=TEXTO_SEC,
                          weight=SEMIBOLD).move_to(UP * 6.85)
        self.barras = VGroup(*[RoundedRectangle(width=0.7, height=0.12, corner_radius=0.06,
                                                fill_color="#334155", fill_opacity=1,
                                                stroke_width=0) for _ in range(3)])
        self.barras.arrange(RIGHT, buff=0.15).move_to(UP * 6.4)
        self.ala = self.perfil.contorno().set_z_index(10)
        self.nota = T("simplificación: flujo ideal en 2D", size=24, color=TEXTO_SEC,
                      weight=MEDIUM).move_to(DOWN * 1.95)
        self.play(FadeIn(self.cabecera, shift=DOWN * 0.2), FadeIn(self.barras), run_time=0.4)

        self.seccion_mito()
        self.seccion_newton()
        self.seccion_presion()
        self.cierre()

    # ---------- Gancho ----------
    def gancho(self):
        l1 = T("¿El aire de arriba", size=62, weight=HEAVY, font=F_TIT)
        l2 = T("llega", size=62, weight=HEAVY, font=F_TIT)
        num = T("A LA VEZ", size=120, color=BG, weight=HEAVY, font=F_TIT)
        caja = RoundedRectangle(width=num.width + 0.7, height=num.height + 0.55, corner_radius=0.3,
                                fill_color=C_MITO, fill_opacity=1, stroke_width=0).move_to(num)
        destacado = VGroup(caja, num)
        l3 = T("que el de abajo?", size=62, weight=HEAVY, font=F_TIT)
        bloque = VGroup(l1, l2, destacado, l3).arrange(DOWN, buff=0.34).move_to(UP * 2.3)
        destacado.rotate(-3 * DEGREES)
        txt = T("ES UN MITO", size=96, color=C_NEWTON, weight=HEAVY, font=F_TIT)
        marco = RoundedRectangle(width=txt.width + 0.6, height=txt.height + 0.5,
                                 corner_radius=0.2, stroke_color=C_NEWTON, stroke_width=10,
                                 fill_opacity=0)
        sello = VGroup(marco, txt.move_to(marco)).rotate(6 * DEGREES).move_to(DOWN * 1.6)

        t0, d = self.voz("gancho")
        self.play(FadeIn(l1, shift=UP * 0.3), run_time=0.35)
        self.play(FadeIn(l2, shift=UP * 0.3), run_time=0.3)
        self.play(GrowFromCenter(caja), FadeIn(num, scale=1.6),
                  rate_func=rate_functions.ease_out_back, run_time=0.5)
        self.play(FadeIn(l3, shift=UP * 0.2), run_time=0.35)
        self.hasta(0, 4.65)
        self.play(FadeIn(sello, scale=2.2), rate_func=rate_functions.ease_out_back, run_time=0.35)
        self.rellenar(t0, d, margen=-0.5)
        self.play(FadeOut(VGroup(bloque, sello), shift=UP * 0.6), run_time=0.35)

    # ---------- Textos de cada bloque ----------
    def textos(self, idx, nombre, frase, dato, etiqueta, clave, color):
        tit = T(nombre, size=128, color=color, weight=HEAVY, font=F_TIT).move_to(UP * 5.2)
        fr = T(frase, size=50, weight=BOLD).next_to(tit, DOWN, buff=0.3)
        dt = T(dato, size=30, color=TEXTO_SEC, weight=MEDIUM).next_to(fr, DOWN, buff=0.18)
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

    def etiqueta(self, texto, color, pos, size=28):
        t = T(texto, size=size, color=color, weight=BOLD)
        fondo = RoundedRectangle(width=t.width + 0.36, height=t.height + 0.24, corner_radius=0.14,
                                 fill_color=BG, fill_opacity=0.85, stroke_width=0)
        return VGroup(fondo, t).move_to(pos).set_z_index(30)

    # ---------- 1. El mito: tiempo de tránsito ----------
    def seccion_mito(self):
        t0, d = self.voz("mito")
        P = self.perfil
        barra, tit, fr, dt, etq, ctl = self.textos(
            0, "El mito", "El aire de arriba llega antes", "nada lo obliga a llegar a la vez",
            "LA REALIDAD", "LLEGA ANTES", C_MITO)
        self.entrar_textos(barra, C_MITO, tit, fr, dt, FadeIn(self.ala, shift=UP * 0.3),
                           FadeIn(self.nota))

        # Línea de partículas que salen a la vez (línea de tiempo)
        # la línea divisoria (la que acaba en el punto de remanso) está entre -0.12 y 0.03
        ys = [round(y, 2) for y in sorted(list(np.arange(-1.45, -0.2, 0.15)) + [-0.12, 0.03]
                                          + list(np.arange(0.18, 1.65, 0.15)))]
        y_arr, y_abj = 0.33, -0.4           # una partícula sobre el extradós y otra bajo el intradós
        lineas = {y: P.linea(y, x_ini=-4.2, x_fin=6.0, paso=0.01) for y in ys}
        tau = ValueTracker(0.0)
        arriba = [y for y in ys if y >= 0.03]
        abajo = [y for y in ys if y <= -0.12]

        def puntos(grupo_y):
            return [en_tiempo(*lineas[y], tau.get_value()) for y in grupo_y]

        def polilinea(grupo_y, color):
            def f():
                v = VMobject().set_points_as_corners(puntos(grupo_y))
                return v.set_stroke(color, width=4, opacity=0.9)
            return always_redraw(f)

        lin_arr = polilinea(arriba, C_MITO).set_z_index(5)
        lin_abj = polilinea(abajo, "#CBD5E1").set_z_index(5)
        puntos_m = VGroup(*[Dot(radius=0.05, color=C_MITO if y >= 0.03 else "#CBD5E1")
                            for y in ys]).set_z_index(6)

        def mover(g):
            for dot, y in zip(g, ys):
                dot.move_to(en_tiempo(*lineas[y], tau.get_value()))
        puntos_m.add_updater(mover)
        mover(puntos_m)
        p_arr = Dot(radius=0.13, color=C_MITO).set_z_index(20)
        p_abj = Dot(radius=0.13, color=TEXTO).set_z_index(20)
        p_arr.add_updater(lambda m: m.move_to(en_tiempo(*lineas[y_arr], tau.get_value())))
        p_abj.add_updater(lambda m: m.move_to(en_tiempo(*lineas[y_abj], tau.get_value())))

        meta = DashedLine(self.te + UP * 1.9, self.te + DOWN * 1.75, color=TEXTO_SEC,
                          stroke_width=3, dash_length=0.12).set_z_index(4)
        meta_txt = T("borde de salida", size=24, color=TEXTO_SEC,
                     weight=SEMIBOLD).next_to(meta, UP, buff=0.1).shift(LEFT * 0.4)

        def llegada(y):
            pts, tt = lineas[y]
            return tt[np.argmax(pts[:, 0] >= self.te[0] - 0.02)]
        t_arr, t_abj = llegada(y_arr), llegada(y_abj)
        tau_fin = t_abj + 0.9
        dur = 4.3
        self.hasta(t0, d * 0.22)
        self.play(FadeIn(puntos_m), FadeIn(lin_arr), FadeIn(lin_abj), FadeIn(p_arr),
                  FadeIn(p_abj), Create(meta), FadeIn(meta_txt), run_time=0.5)
        self.add(tau)
        # avanzar hasta que llega la partícula de arriba
        self.play(tau.animate.set_value(t_arr), rate_func=linear, run_time=dur * t_arr / tau_fin)
        ya = self.etiqueta("¡ya llegó!", C_MITO, [1.75, 1.2, 0])
        aun = self.etiqueta("aún no", TEXTO, p_abj.get_center() + LEFT * 0.95)
        aun.add_updater(lambda m: m.move_to(p_abj.get_center() + LEFT * 0.95))
        self.play(FadeIn(ya, scale=1.3), FadeIn(aun), Flash(p_arr, color=C_MITO), run_time=0.4)
        resto = tau_fin - t_arr
        self.play(tau.animate.set_value(tau_fin), rate_func=linear, run_time=dur * resto / tau_fin)
        aun.clear_updaters()
        self.play(FadeIn(etq), FadeIn(ctl, scale=0.8), FadeOut(aun), run_time=0.45)
        self.rellenar(t0, d)
        for m in (puntos_m, p_arr, p_abj):
            m.clear_updaters()
        self.salir(tit, fr, dt, etq, ctl, puntos_m, lin_arr, lin_abj, p_arr, p_abj, meta,
                   meta_txt, ya)

    # ---------- 2. Newton: el ala desvía el aire hacia abajo ----------
    def seccion_newton(self):
        t0, d = self.voz("newton")
        P = self.perfil
        barra, tit, fr, dt, etq, ctl = self.textos(
            1, "Newton", "El ala empuja el aire hacia abajo",
            "y el aire empuja al ala hacia arriba", "LA CLAVE", "3.ª LEY DE NEWTON", C_NEWTON)
        self.entrar_textos(barra, C_NEWTON, tit, fr, dt)

        ys = [-1.4, -1.0, -0.6, -0.25, 0.1, 0.45, 0.8, 1.15, 1.55, 2.0]
        self.lineas = [P.linea(y, x_ini=-5.2, x_fin=5.4) for y in ys]
        self.trazos = VGroup(*[trazo(p) for p, _ in self.lineas]).set_z_index(1)
        self.reloj = ValueTracker(0.0)
        self.reloj.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(self.reloj)
        self.puntos = trazadores(self.lineas, self.reloj, "#E2E8F0", cada=0.55,
                                 velocidad=1.6).set_z_index(2)
        self.hasta(t0, d * 0.11)
        self.play(LaggedStart(*[Create(t) for t in self.trazos], lag_ratio=0.06),
                  FadeIn(self.puntos), run_time=1.1)

        # el aire, siguiendo el ala, sale hacia abajo (línea de corriente real)
        pts, _ = P.linea(0.35, x_ini=-5.2, x_fin=4.4)
        tramo = pts[pts[:, 0] >= -1.2]
        desvio = VMobject().set_points_smoothly(list(tramo[::6]) + [tramo[-1]])
        desvio.set_stroke(C_NEWTON, width=12)
        punta = Triangle(fill_color=C_NEWTON, fill_opacity=1, stroke_width=0).scale(0.2)
        dirf = tramo[-1] - tramo[-8]
        punta.rotate(np.arctan2(dirf[1], dirf[0]) - PI / 2).move_to(tramo[-1])
        flujo = VGroup(desvio, punta).set_z_index(15)
        flujo_txt = self.etiqueta("aire desviado hacia abajo", C_NEWTON,
                                  [2.0, -0.5, 0], size=28)
        self.hasta(t0, d * 0.34)
        self.play(Create(desvio), run_time=0.9)
        self.play(FadeIn(punta, scale=0.5), FadeIn(flujo_txt), run_time=0.3)

        x_cp = self.le[0] + 0.3 * (self.te[0] - self.le[0])
        base = np.array([x_cp, 0.95, 0])
        self.sust = vector(base, base + UP * 1.55, C_NEWTON, ancho=14, punta=0.38).set_z_index(25)
        self.sust_txt = self.etiqueta("fuerza sobre el ala", C_NEWTON,
                                      base + UP * 1.2 + RIGHT * 2.05)
        self.hasta(t0, d * 0.55)
        self.play(GrowArrow(self.sust), FadeIn(self.sust_txt, shift=RIGHT * 0.2), run_time=0.6)
        self.hasta(t0, d * 0.8)
        self.play(FadeIn(etq), FadeIn(ctl, scale=0.8), run_time=0.5)
        self.rellenar(t0, d)
        self.play(FadeOut(VGroup(tit, fr, dt, etq, ctl), shift=LEFT * 0.6),
                  FadeOut(flujo), FadeOut(flujo_txt), FadeOut(self.sust), FadeOut(self.sust_txt),
                  self.trazos.animate.set_stroke(opacity=0.35),
                  self.puntos.animate.set_opacity(0.35), run_time=0.4)

    # ---------- 3. Presión: la otra cara ----------
    def seccion_presion(self):
        t0, d = self.voz("presion")
        barra, tit, fr, dt, etq, ctl = self.textos(
            2, "Presión", "Menos arriba, más abajo", "la misma fuerza, vista de otra forma",
            "LA OTRA CARA", "DIFERENCIA DE PRESIÓN", C_PRESION)
        self.entrar_textos(barra, C_PRESION, tit, fr, dt)

        menos, mas = flechas_presion(self.perfil, C_PRESION, "#FDE68A", k=0.55, lmax=1.0, cada=5)
        menos.set_z_index(12)
        mas.set_z_index(12)
        t_menos = self.etiqueta("−  menos presión", C_PRESION, [1.75, 2.0, 0])
        t_mas = self.etiqueta("+  más presión", "#FDE68A", [0.3, -1.15, 0])
        self.hasta(t0, d * 0.2)
        self.play(LaggedStart(*[GrowArrow(a) for a in menos], lag_ratio=0.04),
                  FadeIn(t_menos), run_time=0.9)
        self.play(LaggedStart(*[GrowArrow(a) for a in mas], lag_ratio=0.04),
                  FadeIn(t_mas), run_time=0.8)

        x_cp = self.le[0] + 0.3 * (self.te[0] - self.le[0])
        base = np.array([x_cp, 0.95, 0])
        sust = vector(base, base + UP * 1.55, C_PRESION, ancho=14, punta=0.38).set_z_index(25)
        sust_txt = self.etiqueta("sustentación", C_PRESION, base + UP * 1.2 + RIGHT * 1.55)
        self.hasta(t0, d * 0.63)
        self.play(FadeOut(t_menos), FadeIn(etq), FadeIn(ctl, scale=0.8), run_time=0.4)
        self.play(GrowArrow(sust), FadeIn(sust_txt), run_time=0.5)
        self.rellenar(t0, d)
        self.puntos.clear_updaters()
        self.salir(tit, fr, dt, etq, ctl, menos, mas, t_mas, sust, sust_txt, self.trazos,
                   self.puntos, self.ala, self.nota)

    # ---------- Cierre ----------
    def cierre(self):
        datos = [("El mito", "llegar a la vez", "falso", C_MITO),
                 ("Newton", "aire hacia abajo", "reacción", C_NEWTON),
                 ("Presión", "menos arriba", "otra cara", C_PRESION)]
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

        lema = T("Newton y Bernoulli: dos caras de lo mismo", size=34, color=TEXTO,
                 weight=SEMIBOLD).next_to(tarjetas, DOWN, buff=0.45)
        p1 = T("¿Qué otro mito", size=60, weight=HEAVY, font=F_TIT)
        p2 = T("te contaron?", size=60, color=C_PRESION, weight=HEAVY, font=F_TIT)
        preg = VGroup(p1, p2).arrange(DOWN, buff=0.15).next_to(lema, DOWN, buff=0.7)
        com = T("Te leo en comentarios", size=32, color=TEXTO_SEC, weight=MEDIUM)
        com.next_to(preg, DOWN, buff=0.25)

        t0, d = self.voz("cierre")
        self.play(LaggedStart(*[FadeIn(t, shift=RIGHT * 0.5) for t in tarjetas], lag_ratio=0.25),
                  run_time=1.1)
        self.play(FadeIn(lema, shift=UP * 0.2), run_time=0.4)
        self.hasta(t0, 4.3)
        self.play(FadeIn(preg, shift=UP * 0.3, scale=1.1), run_time=0.5)
        self.play(FadeIn(com), run_time=0.3)
        self.rellenar(t0, d, margen=1.5)

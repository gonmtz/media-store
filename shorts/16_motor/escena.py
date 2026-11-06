"""
Short 16 (texto, sin voz): ¿qué hay dentro de un motor? (turbofán), con el avión 3D y un
corte 2D esquemático.
- El fan (ventilador) mueve casi todo el aire; la mayor parte rodea el núcleo (flujo
  secundario): de unas 5 a más de 10 veces el aire que entra al núcleo, según el motor.
- Núcleo: compresor → cámara de combustión → turbina → tobera. Los gases superan los 1500 °C.
- La turbina toma energía de los gases y, por ejes, mueve el compresor y el fan.
- En un turbofán moderno, la mayor parte del empuje la da el aire que mueve el fan.
Corte simplificado (sin escala; un solo eje dibujado; los motores reales tienen dos o tres).
Render:  manim -qh --fps 30 shorts/16_motor/escena.py Motor
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403
from lib import avion as A  # noqa: E402
from lib.avion2d import capa_3d  # noqa: E402

Y_AV = -1.0
C_FRIO, C_FUEGO, C_EJE = C_CABECEO, "#FB923C", C_GUINADA
X0, CM, *_ = A.datos_motor(-1)
MIRAR = A.a_cuerpo(X0 + 1.2, CM[0], CM[1])
YC = -0.6           # centro del corte en pantalla
rng = np.random.default_rng(5)
PART_BY = [(rng.uniform(0, 1), rng.choice([-1, 1]), rng.uniform(1.12, 1.55)) for _ in range(40)]
PART_NU = [(rng.uniform(0, 1), rng.uniform(-0.42, 0.42)) for _ in range(28)]


def corte():
    """Corte esquemático de un turbofán (aire de izquierda a derecha)."""
    g = VGroup()
    # góndola (arriba y abajo)
    for s in (1, -1):
        g.add(Polygon(*[np.array([x, YC + s * y, 0]) for x, y in
                        [(-3.6, 1.62), (-3.3, 1.78), (1.2, 1.78), (2.6, 1.55), (2.6, 1.45),
                         (-3.2, 1.62)]],
                      fill_color="#CBD5E1", fill_opacity=1, stroke_color=BORDE, stroke_width=1.5))
    # carcasa del núcleo
    for s in (1, -1):
        g.add(Polygon(*[np.array([x, YC + s * y, 0]) for x, y in
                        [(-2.55, 0.62), (-2.4, 0.95), (1.4, 0.98), (3.0, 0.62), (3.0, 0.52),
                         (1.3, 0.85), (-2.3, 0.82)]],
                      fill_color="#94A3B8", fill_opacity=1, stroke_color=BORDE, stroke_width=1.2))
    # cono central y eje
    g.add(Polygon(*[np.array(p) for p in [(-3.75, YC, 0), (-3.1, YC + 0.38, 0), (-3.1, YC - 0.38, 0)]],
                  fill_color="#E2E8F0", fill_opacity=1, stroke_width=0))
    g.add(Polygon(*[np.array(p) for p in [(2.6, YC + 0.45, 0), (3.7, YC, 0), (2.6, YC - 0.45, 0)]],
                  fill_color="#64748B", fill_opacity=1, stroke_width=0))
    return g


def fan():
    g = VGroup()
    for s in (1, -1):
        for k in range(3):
            g.add(RoundedRectangle(width=0.1, height=1.38, corner_radius=0.05, fill_color=C_FRIO,
                                   fill_opacity=1, stroke_width=0)
                  .move_to([-3.12 + 0.13 * k, YC + s * 0.98, 0]))
    return g


def compresor():
    g = VGroup()
    for i, x in enumerate(np.linspace(-2.1, -0.35, 7)):
        h = 0.78 - i * 0.05
        for s in (1, -1):
            g.add(Line([x, YC + s * 0.12, 0], [x, YC + s * h, 0], color=C_FRIO, stroke_width=5))
    return g


def camara():
    g = VGroup()
    for s in (1, -1):
        g.add(RoundedRectangle(width=0.85, height=0.42, corner_radius=0.15, fill_color=C_FUEGO,
                               fill_opacity=0.9, stroke_width=0).move_to([0.2, YC + s * 0.45, 0]))
    return g


def turbina():
    g = VGroup()
    for i, x in enumerate(np.linspace(0.85, 1.9, 4)):
        h = 0.62 + i * 0.07
        for s in (1, -1):
            g.add(Line([x, YC + s * 0.12, 0], [x, YC + s * h, 0], color=C_ALABEO, stroke_width=6))
    return g


def eje():
    return Line([-3.1, YC, 0], [2.6, YC, 0], color=C_EJE, stroke_width=7)


class Motor(ShortBase):
    def construct(self):
        self.iniciar()
        reloj = ValueTracker(0.0)
        reloj.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(reloj)
        r = A.Avion3DReal(1080, 1080, 2, campo=9.5, colores_mando=False)
        t = {k: ValueTracker(v) for k, v in dict(azimut=-16, elevacion=4, campo=9.5).items()}
        capa = capa_3d(r, 9.0, (0, Y_AV), mirar=tuple(MIRAR),
                       fan=lambda: (reloj.get_value() * 140.0) % 360, **t)
        fondo = brillo(UP * Y_AV, C_FRIO, 4.0, 0.9)

        # ---------- Gancho (portada en t = 0) ----------
        preg = self.hud(frase_cinetica("¿Qué hay dentro de un motor?", size=62,
                                       resaltar=["dentro"], color_resalte=C_FUEGO)
                        .move_to(UP * 4.7))
        self.portada(fondo, capa, preg)
        self.wait(0.5)
        self.sonido("whoosh_suave", -10)
        self.play(t["campo"].animate.set_value(7.0), t["azimut"].animate.set_value(-6),
                  run_time=2.0, rate_func=rate_functions.ease_in_out_sine)
        self.pulso(preg, 1.06)
        self.hasta(0, 3.4)

        # ---------- corte 2D ----------
        flujo_on = ValueTracker(0.0)
        nucleo_on = ValueTracker(0.0)

        def flujo():
            g = VGroup()
            tt = reloj.get_value()
            a = flujo_on.get_value()
            if a > 0.01:
                for f, s, y in PART_BY:
                    x = -3.5 + ((f + tt * 0.45) % 1.0) * 6.3
                    g.add(Line([x, YC + s * y, 0], [x + 0.28, YC + s * y, 0], color=C_FRIO,
                               stroke_width=3).set_opacity(0.85 * a))
            b = nucleo_on.get_value()
            if b > 0.01:
                for f, y in PART_NU:
                    u = (f + tt * 0.35) % 1.0
                    x = -2.4 + u * 6.0
                    yy = YC + y * (0.9 if x < 0 else 0.7)
                    col = C_FRIO if x < -0.2 else (C_FUEGO if x < 1.0 else C_ALABEO)
                    g.add(Dot([x, yy, 0], radius=0.05 + 0.03 * (x > -0.2), color=col)
                          .set_opacity(b))
            return g
        capa_flujo = always_redraw(flujo)
        dib = corte()
        f_, c_, k_, tu_, e_ = fan(), compresor(), camara(), turbina(), eje()

        # ---------- 1. Fan ----------
        self.dejar(preg)
        self.play(self.poner_cabecera("DENTRO DE UN TURBOFÁN", 3), run_time=0.01)
        barra, tit, fr, dt = self.bloque(0, "El fan", "Mueve casi todo el aire", C_FRIO,
                                         dato="la mayor parte rodea el núcleo: de 5 a más de 10 veces",
                                         resaltar=["casi", "todo"])
        self.add(capa_flujo)
        self.cambio(FadeOut(capa), FadeOut(fondo), FadeIn(dib), FadeIn(f_),
                    FadeIn(tit, shift=DOWN * 0.3, scale=1.2), barra.animate.set_fill(C_FRIO),
                    run_time=0.7)
        self.entrar_palabras(fr)
        self.play(FadeIn(dt), flujo_on.animate.set_value(1.0), run_time=0.5)
        e1 = self.etiqueta("FAN", C_FRIO, [-3.05, YC + 2.15, 0], size=26)
        e2 = self.etiqueta("AIRE QUE RODEA EL NÚCLEO", C_FRIO, [0.0, YC - 2.15, 0], size=24)
        self.sonido("pop", -8)
        self.play(FadeIn(e1), FadeIn(e2), run_time=0.4)
        self.wait(2.0)
        self.hasta(0, 9.8)

        # ---------- 2. Núcleo ----------
        self.dejar(tit, fr, dt, e1, e2)
        barra, tit, fr, dt = self.bloque(1, "El núcleo", "Comprime el aire, quema combustible y lo expulsa",
                                         C_FUEGO, dato="los gases superan los 1500 °C",
                                         resaltar=["quema"])
        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.2), barra.animate.set_fill(C_FUEGO),
                    FadeIn(c_), nucleo_on.animate.set_value(1.0))
        self.entrar_palabras(fr)
        self.play(FadeIn(dt), run_time=0.3)
        n1 = self.etiqueta("COMPRESOR", C_FRIO, [-1.2, YC + 2.15, 0], size=22)
        self.sonido("tic", -6)
        self.play(FadeIn(n1), run_time=0.3)
        n2 = self.etiqueta("COMBUSTIÓN", C_FUEGO, [0.25, YC - 2.15, 0], size=22)
        self.sonido("golpe", -10)
        self.play(FadeIn(k_, scale=0.7), FadeIn(n2), run_time=0.4)
        self.play(k_.animate.set_opacity(1.0).scale(1.08), rate_func=there_and_back, run_time=0.5)
        self.wait(1.6)
        self.hasta(0, 16.4)

        # ---------- 3. Turbina ----------
        self.dejar(tit, fr, dt, n1, n2)
        barra, tit, fr, dt = self.bloque(2, "La turbina", "Mueve el fan y el compresor",
                                         C_ALABEO, dato="los gases la hacen girar; un eje la une con el resto",
                                         resaltar=["fan", "compresor"])
        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.2), barra.animate.set_fill(C_ALABEO),
                    FadeIn(tu_))
        self.entrar_palabras(fr)
        self.play(FadeIn(dt), run_time=0.3)
        n3 = self.etiqueta("TURBINA", C_ALABEO, [1.4, YC + 2.15, 0], size=22)
        n4 = self.etiqueta("EJE", C_EJE, [-1.0, YC - 2.15, 0], size=22)
        self.sonido("tic", -6)
        self.play(FadeIn(n3), Create(e_), FadeIn(n4), run_time=0.6)
        self.play(e_.animate.set_stroke(width=12), rate_func=there_and_back, run_time=0.6)
        self.wait(1.6)
        self.hasta(0, 22.8)

        # ---------- Cierre (vuelve a la portada) ----------
        self.dejar(tit, fr, dt, n3, n4, dib, f_, c_, k_, tu_, e_, capa_flujo, self.tema,
                   self.barras)
        cierre = self.hud(frase_cinetica("¿Lo habías visto por dentro?", size=58,
                                         resaltar=["dentro?"], color_resalte=C_FUEGO)
                          .move_to(UP * 4.7))
        capa2 = capa_3d(r, 9.0, (0, Y_AV), mirar=tuple(MIRAR),
                        fan=lambda: (reloj.get_value() * 140.0) % 360, azimut=-16, elevacion=4,
                        campo=9.5)
        self.cambio(FadeIn(capa2), FadeIn(fondo))
        self.entrar_palabras(cierre)
        self.hasta(0, 25.6)
        self.dejar(cierre)
        self.cambio(FadeIn(preg), run_time=0.3, desplazar=UP * 0.6)
        self.wait(0.25)

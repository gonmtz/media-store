"""
Short 36 (narrado): los números de pista. Vista desde arriba con la pista vertical en pantalla:
arriba es el sentido de aterrizaje (oeste para la 27); la brújula pequeña lo indica (norte a la
derecha de la pantalla).
- Designador = rumbo magnético / 10, redondeado; los dos extremos difieren en 18 (180°).
- El número se pinta en el umbral, legible para el avión que llega.
- Paralelas: mirando hacia el oeste, la derecha es el norte → 27R a la derecha de la pantalla;
  para 09 (hacia el este) esa misma pista es la 09L.
- La declinación magnética cambia: ejemplo de rumbo 274° → 276° que pasa de 27 a 28.
Render:  manim -qh --fps 60 shorts/36_numeros_pista/escena.py NumerosPista
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403
from lib.modos import ModoBase, flecha  # noqa: E402

C_27, C_09, C_N, C_PAR = C_CABECEO, C_GUINADA, C_ALABEO, "#34D399"
XP, YP = 0.0, 0.55           # centro de la pista
LP, AP = 4.6, 1.15           # largo y ancho
BRUJ = (3.2, 2.15)


def pista(x=XP, num_a="27", num_b="", ancho=AP, color_a=C_27, color_b="#64748B", escala=1.0):
    """Pista vertical vista desde arriba. num_a se pinta en el umbral de ABAJO (se aterriza
    hacia arriba) y num_b en el de arriba, girado 180° (legible para quien llega al revés)."""
    c = np.array([x, YP, 0])
    g = VGroup(Rectangle(width=ancho, height=LP, stroke_width=0, fill_color="#1F2937",
                         fill_opacity=1).move_to(c))
    for y in np.arange(-LP / 2 + 1.35, LP / 2 - 1.35, 0.5):          # eje discontinuo
        g.add(Line(c + UP * y, c + UP * (y + 0.27), color="#E5E7EB", stroke_width=3 * escala))
    for s in (-1, 1):                                                 # umbrales (piano)
        yb = s * (LP / 2 - 0.1)
        for k in range(6):
            xx = -ancho / 2 + 0.1 + k * (ancho - 0.2) / 5
            g.add(Line(c + np.array([xx, yb, 0]), c + np.array([xx, yb - s * 0.32, 0]), color="#E5E7EB",
                       stroke_width=5 * escala))
    n_a = T(num_a, size=int(48 * escala), color=color_a, weight=HEAVY, font=F_TIT).move_to(c + DOWN * (LP / 2 - 0.75))
    g.add(n_a)
    n_b = None
    if num_b:
        n_b = T(num_b, size=int(48 * escala), color=color_b, weight=HEAVY, font=F_TIT).rotate(PI).move_to(c + UP * (LP / 2 - 0.75))
        g.add(n_b)
    g.n_a, g.n_b = n_a, n_b
    return g


def brujula(giro=90.0, centro=BRUJ, r=0.62):
    """Brújula pequeña; giro=90 pone el oeste arriba (norte a la derecha)."""
    c = np.array([*centro, 0])
    g = VGroup(Circle(radius=r, stroke_color="#475569", stroke_width=3, fill_color="#0F172A",
                      fill_opacity=0.9).move_to(c))
    for a in range(0, 360, 30):
        u = np.array([np.sin(np.radians(a + giro)), np.cos(np.radians(a + giro)), 0])
        g.add(Line(c + u * r, c + u * (r - 0.1), stroke_color="#64748B", stroke_width=2))
    for a, txt in ((0, "N"), (90, "E"), (180, "S"), (270, "O")):
        u = np.array([np.sin(np.radians(a + giro)), np.cos(np.radians(a + giro)), 0])
        g.add(T(txt, size=24 if txt == "N" else 20, color=C_N if txt == "N" else TEXTO_SEC,
                weight=HEAVY).move_to(c + u * (r - 0.27)))
    un = np.array([np.sin(np.radians(giro)), np.cos(np.radians(giro)), 0])
    g.add(Triangle(fill_color=C_N, fill_opacity=1, stroke_width=0).scale(0.08)
          .rotate(np.arctan2(un[1], un[0]) - PI / 2).move_to(c + un * (r + 0.12)))
    return g


class NumerosPista(ModoBase):
    VOZ_JSON = Path(__file__).parent / "voz.json"

    def avion(self, x, y, ancho=1.9):
        return self.avion3d(campo=40, alto_px=1080, centro=lambda: (x, y.get_value()), azimut=180,
                            elevacion=89.5, colores_mando=False, ancho_pantalla=ancho)

    def construct(self):
        self.iniciar()
        y_av = ValueTracker(-2.1)
        av = self.avion(XP, y_av)
        br = brujula()
        pi = pista()
        fondo = brillo([0, YP, 0], C_27, 3.4, 0.7)
        preg, dest = self.gancho_texto("¿Por qué esa pista", "SE LLAMA 27?", C_27, 88)
        sello = self.sello("NÚMEROS DE PISTA", C_27, DOWN * 3.95, size=52)

        # ---------- Gancho ----------
        self.portada(fondo, pi, br, av, preg)
        self.wait(0.15)
        self.poner_sello(sello)
        self.pulso(pi.n_a, 1.3)
        self.hasta(0, 2.4)

        # ---------- 1. Rumbo magnético ----------
        t0, d = self.voz("b1")
        self.play(self.poner_cabecera("NÚMEROS DE PISTA", 3), run_time=0.01)
        self.dejar(preg, sello)
        barra, tit, fr, dt = self.bloque_ajustado(0, "Es un rumbo", "El rumbo magnético, sin el último cero",
                                                  C_27, dato="redondeado a la decena",
                                                  resaltar=["rumbo", "magnético"])
        rumbo = flecha([1.05, YP - 1.6, 0], [1.05, YP + 1.6, 0], C_27, 9)
        er = self.etiqueta("RUMBO 270°", C_27, [2.4, YP, 0], size=22)
        eo = self.etiqueta("HACIA EL OESTE", TEXTO_SEC, [2.4, YP - 0.45, 0], size=18)
        self.abrir_bloque(barra, C_27, tit, fr, dt, GrowArrow(rumbo), FadeIn(er), FadeIn(eo),
                          y_av.animate.set_value(-2.0))
        cuenta = T("270°", size=72, color=TEXTO, weight=HEAVY, font=F_TIT).move_to([-2.55, YP, 0])
        self.hasta(t0, d * 0.42)
        self.sonido("pop", -9)
        self.play(FadeIn(cuenta, scale=1.2), y_av.animate.set_value(-1.97), run_time=0.4)
        cero = cuenta[2:]
        tacha = Line(cero.get_corner(DL), cero.get_corner(UR), color=C_N, stroke_width=8)
        self.play(Create(tacha), run_time=0.3)
        res = T("27", size=80, color=C_27, weight=HEAVY, font=F_TIT).move_to([-2.55, YP, 0])
        self.hasta(t0, d * 0.68)
        self.play(FadeOut(VGroup(cero, tacha), shift=RIGHT * 0.3), ReplacementTransform(cuenta[:2], res),
                  run_time=0.5)
        self.pulso(pi.n_a, 1.3)
        self.avanzar(t0 + d - 0.15, y_av.animate.set_value(-1.85))

        # ---------- 2. Dos extremos ----------
        t0, d = self.voz("b2")
        self.dejar(tit, fr, dt, res)
        barra, tit, fr, dt = self.bloque_ajustado(1, "Dos extremos", "El otro extremo es la 09",
                                                  C_09, dato="siempre se diferencian en 18 (180°)",
                                                  resaltar=["09"])
        self.abrir_bloque(barra, C_09, tit, fr, dt, y_av.animate.set_value(-0.3), run_time=0.7)
        self.avanzar(t0 + d * 0.38, y_av.animate.set_value(1.2))
        # damos la vuelta a la vista: ahora se aterriza hacia el este
        self.sonido("whoosh", -10)
        giro = ValueTracker(0.0)
        bv = always_redraw(lambda: brujula(90 + 180 * giro.get_value()))
        self.remove(br)
        self.add(bv)
        self.play(FadeOut(av), FadeOut(rumbo), FadeOut(er), FadeOut(eo),
                  Rotate(pi, PI, about_point=np.array([XP, YP, 0])), giro.animate.set_value(1.0),
                  run_time=1.0)
        bv.clear_updaters()
        rumbo2 = flecha([1.05, YP - 1.6, 0], [1.05, YP + 1.6, 0], C_09, 9)
        er2 = self.etiqueta("RUMBO 090°", C_09, [2.4, YP, 0], size=22)
        ee = self.etiqueta("HACIA EL ESTE", TEXTO_SEC, [2.4, YP - 0.45, 0], size=18)
        n09 = T("09", size=48, color=C_09, weight=HEAVY, font=F_TIT).move_to([XP, YP - (LP / 2 - 0.75), 0])
        self.play(GrowArrow(rumbo2), FadeIn(er2), FadeIn(ee), FadeIn(n09, scale=1.3), run_time=0.5)
        self.pulso(n09, 1.3)
        dif = VGroup(T("27", size=60, color=C_27, weight=HEAVY, font=F_TIT),
                     T("− 09", size=60, color=C_09, weight=HEAVY, font=F_TIT),
                     T("= 18", size=60, color=TEXTO, weight=HEAVY, font=F_TIT)
                     ).arrange(DOWN, buff=0.15, aligned_edge=RIGHT).move_to([-2.55, YP, 0])
        self.hasta(t0, d * 0.75)
        self.sonido("pop", -9)
        self.play(FadeIn(dif, shift=UP * 0.2), run_time=0.4)
        self.hasta(t0, d * 0.88)
        self.pulso(dif[2], 1.12)
        self.rellenar(t0, d)

        # ---------- 3. Paralelas ----------
        t0, d = self.voz("b3")
        self.dejar(tit, fr, dt, pi, n09, bv, rumbo2, er2, ee, dif)
        barra, tit, fr, dt = self.bloque_ajustado(2, "Paralelas", "Se añade L, C o R",
                                                  C_PAR, dato="izquierda, centro y derecha en inglés",
                                                  resaltar=["L,", "C", "R"])
        tres = VGroup(*[pista(x, a, b, ancho=0.8, color_a=C_PAR, color_b="#475569", escala=0.68)
                        for x, a, b in ((-1.65, "27L", ""), (0.0, "27C", ""), (1.65, "27R", ""))])
        br2 = brujula()
        y2 = ValueTracker(-2.8)
        av2 = self.avion(0.0, y2, ancho=2.4)
        self.abrir_bloque(barra, C_PAR, tit, fr, dt, LaggedStart(*[FadeIn(p, shift=UP * 0.3) for p in tres],
                                                                 lag_ratio=0.2), FadeIn(br2), run_time=0.8)
        self.add(av2)
        self.play(y2.animate.set_value(-1.95), run_time=0.6)
        der = self.etiqueta("DERECHA →", C_PAR, [3.15, -0.2, 0], size=20)
        izq = self.etiqueta("← IZQUIERDA", C_PAR, [-3.1, -0.2, 0], size=20)
        self.sonido("pop", -9)
        self.play(FadeIn(der, shift=RIGHT * 0.2), FadeIn(izq, shift=LEFT * 0.2), run_time=0.4)
        self.hasta(t0, d * 0.55)
        self.pulso(VGroup(*[p.n_a for p in tres]), 1.15)
        self.avanzar(t0 + d - 0.15, y2.animate.set_value(0.6))

        # ---------- Cierre ----------
        t0, d = self.voz("cierre")
        self.dejar(tit, fr, dt, tres, br2, av2, der, izq, self.tema, self.barras)
        giro2 = ValueTracker(0.0)
        bc = always_redraw(lambda: brujula(90 + giro2.get_value(), centro=(3.25, 1.9), r=0.8))
        rumbo_n = ValueTracker(274.0)
        pi3 = pista()

        def lect():
            r = rumbo_n.get_value()
            return VGroup(T(f"rumbo {r:.0f}°", size=40, color=TEXTO_SEC, weight=HEAVY),
                          T(f"→  {int(round(r / 10)):02d}", size=56, color=C_27, weight=HEAVY, font=F_TIT)
                          ).arrange(RIGHT, buff=0.3).move_to([0, 3.15, 0])
        le = always_redraw(lect)
        en = self.etiqueta("EL NORTE MAGNÉTICO SE MUEVE (ejemplo)", C_N, [0, 3.95, 0], size=22)
        preg2 = self.cta("¿Qué número tiene la pista de tu ciudad?", ["tu", "ciudad?"], C_27, y=-4.4, size=56)
        y4 = ValueTracker(-2.1)
        av4 = self.avion(XP, y4)
        self.cambio(FadeIn(bc), FadeIn(pi3), FadeIn(le), FadeIn(en), FadeIn(preg2, shift=UP * 0.3), run_time=0.6)
        self.play(giro2.animate.set_value(-12.0), rumbo_n.animate.set_value(276.0), run_time=1.6)
        n28 = T("28", size=48, color=C_27, weight=HEAVY, font=F_TIT).move_to(pi3.n_a)
        self.sonido("tic", -8)
        self.play(Transform(pi3.n_a, n28), run_time=0.4)
        le.clear_updaters()
        bc.clear_updaters()
        self.play(FadeIn(av4), y4.animate.set_value(-1.9), run_time=0.5)
        self.hasta(t0, d * 0.6)
        self.pulso(preg2, 1.06)
        self.hasta(t0, d * 0.85)
        self.pulso(le, 1.08)
        self.hasta(t0, d - 0.75)
        y3 = ValueTracker(-2.1)
        av3 = self.avion(XP, y3)
        br3, pi4 = brujula(), pista()
        preg, _ = self.gancho_texto("¿Por qué esa pista", "SE LLAMA 27?", C_27, 88)
        self.dejar(bc, pi3, le, en, preg2, av4)
        self.cambio(FadeIn(br3), FadeIn(pi4), FadeIn(av3), FadeIn(preg), run_time=0.45, desplazar=UP * 0.6)
        self.wait(0.3)

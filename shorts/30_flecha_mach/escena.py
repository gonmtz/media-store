"""
Short 30 (narrado): ¿por qué las alas van hacia atrás? Flecha y Mach crítico.
- Cerca de M ≈ 0,8, el aire que acelera sobre el extradós llega a M = 1: onda de choque y
  aumento brusco de la resistencia (dibujo cualitativo de la zona supersónica).
- Teoría del ala en flecha (ala infinita, simplificación): cuenta la componente normal V·cos Λ.
  cos 25° ≈ 0,906 → casi un 10 % menos. (El ala del modelo tiene 27° en el borde de ataque.)
Render:  manim -qh --fps 60 shorts/30_flecha_mach/escena.py FlechaMach
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403
from lib.modos import ModoBase, flecha  # noqa: E402
from lib import avion as A  # noqa: E402

C_V, C_N, C_T, C_CHOQUE = TEXTO, C_CABECEO, "#64748B", C_ALABEO
P_ALA = A.punto_ala(10.0, s=-1, xc=0.0)          # borde de ataque del ala derecha
LE1, LE2 = A.punto_ala(4.0, s=-1, xc=0.0), A.punto_ala(16.0, s=-1, xc=0.0)


def perfil_2d(ancho=6.6, centro=(0.0, 0.9)):
    pts = A.contorno_perfil(0.02, 0.4, 0.12, 0, 1, 80)
    c0 = np.array([centro[0] - ancho / 2, centro[1]])
    return Polygon(*[np.array([*(c0 + p * ancho), 0]) for p in pts], fill_color="#E2E8F0",
                   fill_opacity=1, stroke_color="#0B1220", stroke_width=2), c0


class FlechaMach(ModoBase):
    VOZ_JSON = Path(__file__).parent / "voz.json"

    def base(self):
        t = {k: ValueTracker(v) for k, v in dict(azimut=180, elevacion=89.5, campo=56).items()}
        av = self.avion3d(campo=t["campo"], alto_px=900, centro=(0, 0.8), colores_mando=False,
                          azimut=t["azimut"], elevacion=t["elevacion"], cabeceo=0)
        fondo = brillo([0, 1.0, 0], C_N, 3.8, 0.8)
        return t, av, fondo

    def lineas_flecha(self, av):
        """Borde de ataque, perpendicular al fuselaje y el ángulo de flecha (ala derecha)."""
        q = av.a_pantalla([LE1, LE2])
        d = (q[1] - q[0]) / np.linalg.norm(q[1] - q[0])
        borde = DashedLine(q[0] - d * 0.4, q[1] + d * 0.6, color=C_N, stroke_width=4, dash_length=0.1)
        perp = DashedLine(q[0], q[0] + RIGHT * 3.0, color=TEXTO_SEC, stroke_width=3, dash_length=0.1)
        ang = np.arctan2(d[1], d[0])
        arco = Arc(radius=1.6, start_angle=ang, angle=-ang, arc_center=q[0], color=C_N, stroke_width=5)
        et = T("≈ 25°", size=30, color=C_N, weight=HEAVY).move_to(q[0] + np.array([1.95, -0.35, 0]))
        return VGroup(borde, perp, arco, et)

    def construct(self):
        self.iniciar()
        t, av, fondo = self.base()
        lf = self.lineas_flecha(av)
        preg, dest = self.gancho_texto("¿Por qué las alas", "VAN HACIA ATRÁS?", C_N, 84)
        sello = self.sello("FLECHA Y MACH", C_N, DOWN * 3.95, size=54)

        # ---------- Gancho ----------
        self.portada(fondo, av, lf, preg)
        self.wait(0.15)
        self.poner_sello(sello)
        self.pulso(lf[3], 1.3)
        self.hasta(0, 2.2)

        # ---------- 1. El choque ----------
        t0, d = self.voz("b1")
        self.play(self.poner_cabecera("¿POR QUÉ LA FLECHA?", 3), run_time=0.01)
        self.dejar(preg, sello, lf, av, fondo)
        barra, tit, fr, dt = self.bloque_ajustado(0, "Onda de choque", "Sobre el ala, el aire llega a Mach 1",
                                                  C_CHOQUE, dato="aunque el avión vuele a Mach 0,78 (dibujo cualitativo)",
                                                  resaltar=["Mach", "1"])
        perf, c0 = perfil_2d()
        k = ValueTracker(0.0)          # tamaño de la zona supersónica (0–1)

        def burbuja():
            kk = k.get_value()
            if kk < 0.02:
                return VGroup()
            xs = np.linspace(0.12, 0.62, 30)
            sup, _ = A.naca(0.02, 0.4, 0.12, 80)
            zs = np.interp(xs, sup[:, 0], sup[:, 1])
            alto = 0.22 * kk * np.sin(np.pi * (xs - 0.12) / 0.5) ** 0.7
            arriba = [np.array([*(c0 + np.array([x, z + h]) * 6.6), 0]) for x, z, h in zip(xs, zs, alto)]
            abajo = [np.array([*(c0 + np.array([x, z]) * 6.6), 0]) for x, z in zip(xs[::-1], zs[::-1])]
            zona = Polygon(*arriba, *abajo, fill_color=C_CHOQUE, fill_opacity=0.35, stroke_width=0)
            xch = c0[0] + 0.62 * 6.6
            zch = c0[1] + np.interp(0.62, sup[:, 0], sup[:, 1]) * 6.6
            choque = Line([xch, zch, 0], [xch, zch + 1.45 * kk, 0], color=C_CHOQUE, stroke_width=8)
            return VGroup(zona, choque)
        bur = always_redraw(burbuja)
        # corriente: líneas que llegan al perfil
        corr = VGroup(*[flecha([-4.3, y, 0], [-3.4, y, 0], "#CBD5E1", 6) for y in (0.4, 0.9, 1.4)])
        ein = self.etiqueta("M 0,78", "#CBD5E1", [-3.85, 1.95, 0], size=24)
        self.abrir_bloque(barra, C_CHOQUE, tit, fr, dt, FadeIn(perf, shift=UP * 0.3), FadeIn(corr),
                          FadeIn(ein))
        self.add(bur)
        self.avanzar(t0 + d * 0.55, k.animate.set_value(0.6))
        ech = self.etiqueta("ONDA DE CHOQUE", C_CHOQUE, [2.4, 2.3, 0], size=24)
        ezs = self.etiqueta("M > 1", C_CHOQUE, [-0.9, 1.75, 0], size=24)
        self.sonido("golpe", -12)
        self.play(FadeIn(ech, scale=1.2), FadeIn(ezs, scale=1.2), k.animate.set_value(0.8), run_time=0.4)
        self.avanzar(t0 + d - 0.15, k.animate.set_value(1.0))

        # ---------- 2. La flecha ----------
        t0, d = self.voz("b2")
        bur.clear_updaters()
        self.dejar(tit, fr, dt, perf, bur, corr, ein, ech, ezs)
        barra, tit, fr, dt = self.bloque_ajustado(1, "La flecha", "El ala nota la velocidad perpendicular",
                                                  C_N, dato="simplificado: ala infinita",
                                                  resaltar=["perpendicular"])
        t2, av2, fondo2 = self.base()
        q = av2.a_pantalla([P_ALA, LE2])
        dle = (q[1] - q[0]) / np.linalg.norm(q[1] - q[0])
        nrm = np.array([dle[1], -dle[0], 0])            # perpendicular al borde, hacia atrás
        if nrm[1] > 0:
            nrm = -nrm
        L = 2.6
        Vv = DOWN * L                                    # aire relativo: del morro hacia la cola
        Vn = nrm * L * np.dot(DOWN, nrm)
        Vt = Vv - Vn
        p0 = np.array([2.75, 3.0, 0])
        vecs = VGroup(flecha(p0, p0 + Vv, C_V, 9), flecha(p0, p0 + Vn, C_N, 10), flecha(p0 + Vn, p0 + Vv, C_T, 7))
        ev = self.etiqueta("V (aire)", C_V, p0 + Vv + DOWN * 0.35, size=24)
        en = self.etiqueta("V · cos Λ", C_N, p0 + Vn + LEFT * 1.1, size=24)
        lf2 = self.lineas_flecha(av2)
        self.abrir_bloque(barra, C_N, tit, fr, dt, FadeIn(av2), FadeIn(fondo2), FadeIn(lf2[0]))
        self.sonido("pop", -9)
        self.play(GrowArrow(vecs[0]), FadeIn(ev), run_time=0.5)
        self.hasta(t0, d * 0.5)
        self.sonido("pop", -9)
        self.play(GrowArrow(vecs[1]), Create(vecs[2]), FadeIn(en), run_time=0.6)
        self.wait(0.5)
        self.pulso(en, 1.15)
        self.avanzar(t0 + d - 0.15, t2["azimut"].animate.set_value(182))

        # ---------- 3. 25 grados ----------
        t0, d = self.voz("b3")
        self.dejar(tit, fr, dt)
        barra, tit, fr, dt = self.bloque_ajustado(2, "Casi 10 % menos", "Más rápido antes del choque",
                                                  C_N, dato="cos 25° ≈ 0,91 · el ala del dibujo tiene ≈ 25°",
                                                  resaltar=["rápido"])
        self.abrir_bloque(barra, C_N, tit, fr, dt, FadeIn(lf2[1:]))
        cuenta = VGroup(T("V = 900 km/h", size=26, color=C_V, weight=HEAVY),
                        T("V · cos Λ ≈ 816 km/h", size=26, color=C_N, weight=HEAVY)
                        ).arrange(DOWN, buff=0.12, aligned_edge=LEFT).move_to([-2.4, -1.5, 0])
        self.sonido("pop", -9)
        self.play(FadeIn(cuenta[0], shift=UP * 0.2), run_time=0.4)
        self.hasta(t0, d * 0.45)
        self.play(FadeIn(cuenta[1], shift=UP * 0.2), run_time=0.4)
        self.pulso(cuenta[1], 1.08)
        self.avanzar(t0 + d - 0.15, t2["azimut"].animate.set_value(180))

        # ---------- Cierre ----------
        t0, d = self.voz("cierre")
        self.dejar(tit, fr, dt, cuenta, vecs, ev, en, self.tema, self.barras)
        tj = VGroup(self.tarjeta("Reactores: vuelan rápido, alas en flecha", C_N, size=34),
                    self.tarjeta("Avionetas: lentas, alas rectas", C_GUINADA, size=34)
                    ).arrange(DOWN, buff=0.22).move_to([0, -1.1, 0])
        preg2 = self.hud(frase_cinetica("¿Lo habías notado?", size=64, resaltar=["notado?"],
                                        color_resalte=C_N).move_to(DOWN * 3.7))
        self.cambio(LaggedStart(*[FadeIn(x, shift=RIGHT * 0.4) for x in tj], lag_ratio=0.3),
                    FadeIn(preg2, shift=UP * 0.3), run_time=0.8)
        self.avanzar(t0 + d * 0.45, t2["azimut"].animate.set_value(178))
        self.pulso(tj, 1.03)
        self.avanzar(t0 + d - 0.75, t2["azimut"].animate.set_value(180))
        preg, _ = self.gancho_texto("¿Por qué las alas", "VAN HACIA ATRÁS?", C_N, 84)
        self.dejar(tj, preg2)
        self.cambio(FadeIn(preg), FadeIn(lf2[2:]), run_time=0.45, desplazar=UP * 0.6)
        self.wait(0.3)

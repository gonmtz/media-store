"""
Short 28 (narrado): flaps y slats, con el avión 3D (piezas móviles de lib/avion.py) y un corte
del perfil que se mueve igual que el 3D. L = ½ρV²·S·CL: a menor V, más CL·S.
Flap Fowler: baja y retrocede (más curvatura y superficie). Slat: se adelanta y abre una rendija
(el aire con energía mantiene el flujo pegado: más ángulo de ataque antes de la pérdida).
"Cerca de un 30 % más despacio": orden de magnitud (CLmáx ≈ 1,5 → ≈ 2,8–3).
Render:  manim -qh --fps 60 shorts/28_flaps_slats/escena.py FlapsSlats
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403
from lib.modos import ModoBase, Y_AV, flecha  # noqa: E402
from lib import avion as A  # noqa: E402

C_FLAP, C_SLAT, C_AIRE = C_GUINADA, C_CABECEO, "#CBD5E1"
RES = {"flap": C_FLAP, "slat": C_SLAT}
T_PERF = 0.12


def _rot(pts, c, ang):
    a = np.radians(ang)
    R = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
    return (pts - c) @ R.T + c


def seccion(flap, slat, ancho=6.4, centro=(0.0, -0.9)):
    """Corte del ala (x hacia atrás = derecha de la pantalla) con slat y flap móviles."""
    k = ancho
    c0 = np.array([*centro]) - np.array([0.45 * k, 0.0])
    piezas = []
    for x0, x1, col in ((0.0, 0.13, C_SLAT), (0.13, 0.74, "#E2E8F0"), (0.74, 1.0, C_FLAP)):
        pts = A.contorno_perfil(0.02, 0.4, T_PERF, x0, x1, 60)
        if x0 == 0.0:
            pts = _rot(pts, np.array([0.13, 0.0]), 20.0 * slat) + np.array([-0.11, -0.03]) * slat
        if x0 == 0.74:
            pts = _rot(pts, np.array([0.74, 0.0]), -flap) + np.array([0.0037, -0.0015]) * flap
        pp = [np.array([*(c0 + p * k), 0.0]) for p in pts]
        piezas.append(Polygon(*pp, fill_color=col, fill_opacity=1, stroke_color="#0B1220",
                              stroke_width=2))
    return VGroup(*piezas)


class FlapsSlats(ModoBase):
    VOZ_JSON = Path(__file__).parent / "voz.json"

    def base(self, flap0=30.0, slat0=1.0):
        t = {k: ValueTracker(v) for k, v in dict(flap=flap0, slat=slat0, azimut=150, elevacion=26,
                                                   campo=46, mx=0.0, my=0.0, mz=0.0, cy=1.25).items()}
        av = self.avion3d(campo=t["campo"], alto_px=760, centro=lambda: (0, t["cy"].get_value()), colores_mando=False,
                          flap=t["flap"], slat=t["slat"], azimut=t["azimut"],
                          elevacion=t["elevacion"], cabeceo=4, resaltar=RES,
                          mirar=lambda: (t["mx"].get_value(), t["my"].get_value(), t["mz"].get_value()))
        fondo = brillo([0, 1.4, 0], C_FLAP, 3.8, 0.8)
        return t, av, fondo

    def construct(self):
        self.iniciar()
        t, av, fondo = self.base()
        preg, dest = self.gancho_texto("¿Cómo vuela tan lento", "AL ATERRIZAR?", C_FLAP, 88)
        sello = self.sello("FLAPS Y SLATS", C_FLAP, DOWN * 3.95, size=54)

        # ---------- Gancho ----------
        self.portada(fondo, av, preg)
        self.wait(0.15)
        self.poner_sello(sello)
        self.avanzar(2.25, t["azimut"].animate.set_value(160))

        # ---------- 1. Cambia de forma ----------
        t0, d = self.voz("b1")
        self.play(self.poner_cabecera("FLAPS Y SLATS", 3), run_time=0.01)
        self.dejar(preg, sello)
        barra, tit, fr, dt = self.bloque_ajustado(0, "Cambia de forma", "Lento, el ala necesita ayuda",
                                                  C_FLAP, dato="L = ½·ρ·V²·S·CL: si V baja, S·CL tiene que subir",
                                                  resaltar=["ayuda"])
        sec = always_redraw(lambda: seccion(t["flap"].get_value(), t["slat"].get_value()))
        etq = VGroup(self.etiqueta("SLAT", C_SLAT, [-2.9, -0.15, 0], size=22),
                     self.etiqueta("FLAP", C_FLAP, [2.9, -0.15, 0], size=22))
        self.abrir_bloque(barra, C_FLAP, tit, fr, dt, t["flap"].animate.set_value(0),
                          t["slat"].animate.set_value(0))
        self.add(sec)
        self.play(FadeIn(etq), run_time=0.3)
        self.avanzar(t0 + d * 0.62, t["azimut"].animate.set_value(170))
        # «salen los flaps y los slats»
        self.sonido("subida", -10)
        self.play(t["slat"].animate.set_value(1.0), t["flap"].animate.set_value(30), run_time=1.6,
                  rate_func=rate_functions.ease_in_out_sine)
        self.avanzar(t0 + d - 0.15, t["azimut"].animate.set_value(175))

        # ---------- 2. Flaps ----------
        t0, d = self.voz("b2")
        sec.clear_updaters()
        self.dejar(tit, fr, dt, etq, sec)
        barra, tit, fr, dt = self.bloque_ajustado(1, "Flaps", "Más curvatura y más superficie",
                                                  C_FLAP, dato="flap Fowler: baja y retrocede",
                                                  resaltar=["curvatura", "superficie"])
        sec2 = always_redraw(lambda: seccion(t["flap"].get_value(), t["slat"].get_value()))
        P = A.punto_ala(8.0, s=-1, xc=0.85)
        self.abrir_bloque(barra, C_FLAP, tit, fr, dt, FadeIn(sec2), t["flap"].animate.set_value(0),
                          t["azimut"].animate.set_value(-140), t["elevacion"].animate.set_value(12),
                          t["mx"].animate.set_value(P[0]), t["my"].animate.set_value(P[1]),
                          t["mz"].animate.set_value(P[2]), t["campo"].animate.set_value(33), t["cy"].animate.set_value(1.0),
                          run_time=0.9)
        self.sonido("whoosh_suave", -12)
        self.avanzar(t0 + d * 0.62, t["flap"].animate.set_value(40))
        cur = self.etiqueta("MÁS CURVATURA", C_FLAP, [2.0, -1.5, 0], size=22)
        self.sonido("pop", -9)
        self.play(FadeIn(cur, scale=1.2), run_time=0.3)
        self.avanzar(t0 + d - 0.15, t["flap"].animate.set_value(30))

        # ---------- 3. Slats ----------
        t0, d = self.voz("b3")
        sec2.clear_updaters()
        self.dejar(tit, fr, dt, cur)
        barra, tit, fr, dt = self.bloque_ajustado(2, "Slats", "Abren una rendija y el aire sigue pegado",
                                                  C_SLAT, dato="retrasan la pérdida: más ángulo de ataque",
                                                  resaltar=["rendija", "pegado"])
        reloj = ValueTracker(0.0)
        reloj.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(reloj)
        k, cx, cy = 6.4, 0.0, -0.9
        c0 = np.array([cx - 0.45 * k, cy])

        def ps(x, z):
            return np.array([*(c0 + np.array([x, z]) * k), 0.0])
        # recorrido (en cuerdas) del aire que entra por la rendija y sigue el extradós
        camino = [(-0.18, -0.07), (-0.07, -0.06), (0.03, -0.02), (0.10, 0.03), (0.16, 0.075),
                  (0.35, 0.095), (0.6, 0.075), (0.85, 0.03), (1.05, -0.04)]
        curva = VMobject().set_points_smoothly([ps(*p) for p in camino])

        def particulas():
            g = VGroup()
            for i in range(9):
                u = (reloj.get_value() * 0.45 + i / 9) % 1.0
                g.add(Dot(curva.point_from_proportion(u), radius=0.055, color=C_SLAT)
                      .set_opacity(0.95))
            return g
        part = always_redraw(particulas)
        Q = A.punto_ala(9.0, s=-1, xc=0.05)
        self.abrir_bloque(barra, C_SLAT, tit, fr, dt, t["mx"].animate.set_value(Q[0]),
                          t["my"].animate.set_value(Q[1]), t["mz"].animate.set_value(Q[2]),
                          t["azimut"].animate.set_value(-35), t["elevacion"].animate.set_value(18),
                          t["campo"].animate.set_value(36), run_time=0.8)
        self.add(part, curva.set_stroke(C_SLAT, 3, opacity=0.35))
        ren = self.etiqueta("RENDIJA", C_SLAT, ps(0.02, -0.16), size=22)
        self.play(FadeIn(ren, scale=1.2), run_time=0.3)
        self.avanzar(t0 + d - 0.15, t["azimut"].animate.set_value(-45))

        # ---------- Cierre ----------
        t0, d = self.voz("cierre")
        reloj.clear_updaters()
        self.dejar(tit, fr, dt, ren, part, curva, sec2, self.tema, self.barras)
        tj = self.tarjeta("Casi un 30 % más lento sin entrar en pérdida", C_FLAP).move_to([0, -1.25, 0])
        preg2 = self.cta("¿Qué otra pieza del ala se levanta al aterrizar?", ["levanta"], C_FLAP, y=-3.5, size=54)
        self.cambio(FadeIn(tj, shift=UP * 0.3), FadeIn(preg2, shift=UP * 0.3),
                    t["mx"].animate.set_value(0), t["my"].animate.set_value(0),
                    t["mz"].animate.set_value(0), t["azimut"].animate.set_value(150),
                    t["elevacion"].animate.set_value(26), t["campo"].animate.set_value(46),
                    t["cy"].animate.set_value(1.25), run_time=0.9)
        self.avanzar(t0 + d * 0.32, t["azimut"].animate.set_value(153))
        self.pulso(tj, 1.05)
        self.avanzar(t0 + d * 0.64, t["azimut"].animate.set_value(156))
        self.pulso(preg2, 1.05)
        self.avanzar(t0 + d - 0.75, t["azimut"].animate.set_value(150))
        preg, _ = self.gancho_texto("¿Cómo vuela tan lento", "AL ATERRIZAR?", C_FLAP, 88)
        self.dejar(tj, preg2)
        self.cambio(FadeIn(preg), run_time=0.45, desplazar=UP * 0.6)
        self.wait(0.3)

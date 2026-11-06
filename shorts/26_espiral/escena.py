"""
Short 26 (narrado): modo espiral, con el avión 3D (render real).
Con el avión inclinado, resbala hacia el ala baja; el efecto diedro tiende a nivelarlo y la
estabilidad direccional (deriva) gira el morro hacia el giro, con lo que el ala de fuera va más
rápido y genera más sustentación (alabeo por guiñada). Si domina la deriva, la inclinación crece
despacio y el morro baja (divergencia en espiral, decenas de segundos). Curvas ilustrativas.
Vista desde atrás: alabeo a la derecha = baja el ala de la derecha de la pantalla.
Render:  manim -qh --fps 60 shorts/26_espiral/escena.py Espiral
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403
from lib.modos import ModoBase, Y_AV, flecha  # noqa: E402
from lib import avion as A  # noqa: E402

C_ESP, C_DIE, C_DER = C_ALABEO, C_CABECEO, C_GUINADA
TM = 60.0
IZQ, DER = A.punto_ala(16.5, s=1, xc=0.3), A.punto_ala(16.5, s=-1, xc=0.3)


def phi_ine(t):
    return 0.18 * np.exp(t / 26.0)


def phi_est(t):
    return 0.18 * np.exp(-t / 14.0)


class Espiral(ModoBase):
    VOZ_JSON = Path(__file__).parent / "voz.json"

    def base(self, r0):
        r = ValueTracker(r0)
        cam = {k: ValueTracker(v) for k, v in dict(azimut=180, elevacion=14, guinada=0).items()}
        av = self.avion3d(centro=(0, Y_AV + 0.1), campo=36, azimut=cam["azimut"],
                          elevacion=cam["elevacion"], guinada=cam["guinada"],
                          alabeo=lambda: 14 + 25 * phi_ine(r.get_value()))
        ax, et = self.grafica(TM, y_rango=(-0.1, 1.2), etiqueta_y="inclinación",
                              etiqueta_x="tiempo (s)")
        tr = self.traza(ax, phi_ine, C_ESP, r)
        fondo = brillo([0, Y_AV - 0.4, 0], C_ESP, 3.6, 0.8)
        return r, cam, av, ax, et, tr, fondo

    def construct(self):
        self.iniciar()
        r, cam, av, ax, et, tr, fondo = self.base(4.0)
        preg, dest = self.gancho_texto("Inclinado y sin tocar nada…", "¿QUÉ PASA?", C_ESP, 96)

        # ---------- Gancho ----------
        sello = self.sello("MODO ESPIRAL", C_ESP, DOWN * 3.95, size=54)
        self.portada(fondo, ax, et, tr, av, preg)
        self.wait(0.15)
        self.poner_sello(sello)
        self.avanzar(2.9, r.animate.set_value(14.0))

        # ---------- 1. Resbala ----------
        t0, d = self.voz("b1")
        self.play(self.poner_cabecera("MODOS DINÁMICOS · 4", 3), run_time=0.01)
        self.dejar(preg, sello)
        barra, tit, fr, dt = self.bloque_ajustado(0, "Resbala", "Se va hacia el ala baja",
                                                  C_ESP, dato="visto desde atrás",
                                                  resaltar=["ala", "baja"])
        res = flecha([-0.3, Y_AV - 1.25, 0], [2.7, Y_AV - 1.25, 0], C_ESP, 11)
        eres = self.etiqueta("RESBALA", C_ESP, [1.2, Y_AV - 1.62, 0], size=24)
        self.abrir_bloque(barra, C_ESP, tit, fr, dt, r.animate.set_value(15.0))
        self.sonido("whoosh_suave", -12)
        self.play(GrowArrow(res), FadeIn(eres), r.animate.set_value(16.0), run_time=0.5)
        self.play(res.animate.shift(RIGHT * 0.25), rate_func=there_and_back, run_time=0.6)
        self.avanzar(t0 + d * 0.65, r.animate.set_value(22.0))
        duelo = VGroup(pastilla(T("DIEDRO", size=34, color=C_DIE, weight=HEAVY, font=F_TIT), C_DIE),
                       T("vs", size=30, color=TEXTO_SEC, weight=BOLD),
                       pastilla(T("DERIVA", size=34, color=C_DER, weight=HEAVY, font=F_TIT), C_DER)
                       ).arrange(RIGHT, buff=0.35).move_to([0.6, -0.75, 0])
        self.sonido("golpe", -12)
        self.play(FadeIn(duelo, scale=1.3), r.animate.set_value(23.0), run_time=0.4,
                  rate_func=rate_functions.ease_out_back)
        self.avanzar(t0 + d - 0.15, r.animate.set_value(26.0))

        # ---------- 2. Los dos efectos, en el mismo avión ----------
        t0, d = self.voz("b2")
        tr.clear_updaters()
        self.dejar(tit, fr, dt, res, eres, duelo, ax, et, tr)
        barra, tit, fr, dt = self.bloque_ajustado(1, "Dos efectos", "El diedro nivela; la deriva lo inclina más",
                                                  C_DER, dato="la cámara sube para ver la guiñada",
                                                  resaltar=["nivela", "más"])
        g = ValueTracker(28.0)
        av2 = self.avion3d(centro=(0, 0.45), campo=64, alto_px=1000, azimut=cam["azimut"],
                           elevacion=cam["elevacion"], guinada=cam["guinada"],
                           alabeo=lambda: g.get_value())
        die = always_redraw(lambda: flecha_giro([0, 0.45, 0], 2.1, -0.25, 0.9, C_DIE))
        edie = self.etiqueta("DIEDRO: TIENDE A NIVELAR", C_DIE, [2.2, -1.25, 0], size=22)
        self.abrir_bloque(barra, C_DER, tit, fr, dt, FadeOut(av), FadeIn(av2),
                          r.animate.set_value(26.0))
        self.add(die)
        self.play(FadeIn(edie, shift=UP * 0.2), g.animate.set_value(24.0), run_time=0.5)
        self.avanzar(t0 + d * 0.33, g.animate.set_value(18.0))
        # «La deriva gira el morro hacia el giro»: la cámara sube y el morro gira a la derecha
        eder = self.etiqueta("DERIVA: MORRO HACIA EL GIRO", C_DER, [-1.9, -1.6, 0], size=22)
        self.sonido("whoosh_suave", -10)
        self.play(FadeOut(die), FadeOut(edie), cam["elevacion"].animate.set_value(48),
                  cam["azimut"].animate.set_value(200), run_time=1.0,
                  rate_func=rate_functions.ease_in_out_cubic)
        self.play(FadeIn(eder), cam["guinada"].animate.set_value(22), run_time=0.9)
        # «el ala de fuera va más rápido y lo inclina más»
        vel = VGroup(self.flecha3d(av2, IZQ, np.array([9.0, 0, 0]), C_DER, 10),
                     self.flecha3d(av2, DER, np.array([4.0, 0, 0]), C_DER, 10))
        def _efu():
            q = av2.a_pantalla([IZQ + np.array([9.0, 0, 0])])[0]
            q[1] = min(q[1] + 0.35, 2.45)
            return self.etiqueta("ALA DE FUERA: MÁS RÁPIDA", C_DER, q, size=20)
        efu = always_redraw(_efu)
        self.sonido("pop", -9)
        self.add(vel)
        self.play(FadeIn(efu), g.animate.set_value(26.0), run_time=0.5)
        self.avanzar(t0 + d - 0.15, g.animate.set_value(36.0))

        # ---------- 3. La espiral ----------
        t0, d = self.voz("b3")
        efu.clear_updaters()
        self.dejar(tit, fr, dt, av2, eder, vel, efu)
        barra, tit, fr, dt = self.bloque_ajustado(2, "La espiral", "Si gana la deriva, se cierra poco a poco",
                                                  C_ESP, dato="muchos aviones son un poco inestables en espiral",
                                                  resaltar=["deriva", "cierra"])
        # trayectoria vista desde arriba: giro a la derecha = sentido horario
        CS = np.array([0.0, 1.55, 0])
        s3 = ValueTracker(0.0)

        def punto(th):
            rr = 1.7 * np.exp(-0.1 * th)
            return CS + np.array([-rr * np.cos(th), 0.62 * rr * np.sin(th), 0])
        ths = np.linspace(0, 4 * PI, 300)
        camino = VMobject().set_points_smoothly([punto(t) for t in ths]).set_stroke(C_ESP, 3, opacity=0.45)
        av3 = self.avion3d(centro=lambda: tuple(punto(s3.get_value())[:2]), campo=130, azimut=180,
                           elevacion=60, guinada=lambda: np.degrees(s3.get_value()),
                           alabeo=lambda: 28 + 3 * s3.get_value(),
                           cabeceo=lambda: -1.2 * s3.get_value())
        r2 = ValueTracker(0.5)
        ax2, et2 = self.grafica(TM, y_rango=(-0.1, 1.2), etiqueta_y="inclinación", etiqueta_x="tiempo (s)")
        ti = self.traza(ax2, phi_ine, C_ESP, r2)
        te = self.traza(ax2, phi_est, C_DIE, r2, ancho=5)
        marcas_t = VGroup(*[self.etiqueta(f"{s} s", TEXTO_SEC, ax2.c2p(s, -0.04), size=18) for s in (20, 40)])
        self.abrir_bloque(barra, C_ESP, tit, fr, dt, FadeIn(camino), FadeIn(av3), FadeIn(ax2),
                          FadeIn(et2), FadeIn(marcas_t))
        self.add(ti, te)
        l1 = self.etiqueta("GANA LA DERIVA: CRECE", C_ESP, ax2.c2p(30, 1.05), size=22)
        l2 = self.etiqueta("GANA EL DIEDRO: SE NIVELA", C_DIE, ax2.c2p(30, 0.32), size=22)
        self.avanzar(t0 + d * 0.3, s3.animate.set_value(1.5 * PI), r2.animate.set_value(22))
        self.sonido("pop", -9)
        self.play(FadeIn(l1, scale=1.2), FadeIn(l2, scale=1.2), run_time=0.3)
        self.avanzar(t0 + d - 0.15, s3.animate.set_value(4 * PI), r2.animate.set_value(TM))

        # ---------- Cierre ----------
        t0, d = self.voz("cierre")
        for m in (ti, te):
            m.clear_updaters()
        self.dejar(tit, fr, dt, camino, av3, ax2, et2, marcas_t, ti, te, l1, l2, self.tema, self.barras)
        tj = VGroup(self.tarjeta("Lento: se corrige sin esfuerzo", C_DIE),
                    self.tarjeta("Sin ver el horizonte, traicionero", C_ESP)).arrange(DOWN, buff=0.3).move_to([0, 2.2, 0])
        preg2 = self.hud(frase_cinetica("¿Lo conocías?", size=76, resaltar=["conocías?"],
                                        color_resalte=C_ESP).move_to(DOWN * 0.8))
        self.cambio(LaggedStart(*[FadeIn(x, shift=RIGHT * 0.4) for x in tj], lag_ratio=0.4),
                    FadeIn(preg2, shift=UP * 0.3), run_time=0.8)
        self.hasta(t0, d * 0.35)
        self.pulso(tj[0], 1.04)
        self.hasta(t0, d * 0.6)
        self.pulso(tj[1], 1.04)
        self.hasta(t0, d * 0.85)
        self.pulso(preg2, 1.08)
        self.hasta(t0, d - 0.7)
        r, cam, av, ax, et, tr, fondo = self.base(4.0)
        preg, _ = self.gancho_texto("Inclinado y sin tocar nada…", "¿QUÉ PASA?", C_ESP, 96)
        self.dejar(tj, preg2)
        self.cambio(*[FadeIn(m) for m in (fondo, ax, et, tr, av, preg)], run_time=0.45,
                    desplazar=UP * 0.6)
        self.wait(0.3)

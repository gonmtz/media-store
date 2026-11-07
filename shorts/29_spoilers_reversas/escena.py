"""
Short 29 (narrado): cómo frena un avión al aterrizar: spoilers, frenos de rueda y reversas.
Avión 3D en la pista (tren fuera); spoilers que se levantan al tocar, flechas de sustentación
y de peso sobre las ruedas; frenos (discos que se calientan); reversa de cascadas: el capó trasero
retrocede y el aire del fan sale hacia delante (el fan sigue girando en el mismo sentido).
Render:  manim -qh --fps 60 shorts/29_spoilers_reversas/escena.py SpoilersReversas
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403
from lib.modos import ModoBase, flecha  # noqa: E402
from lib import avion as A  # noqa: E402

C_SPO, C_FRE, C_REV, C_SUST = C_ALABEO, C_GUINADA, C_CABECEO, C_CABECEO
RES = {"spoiler": C_SPO, "cascada": C_REV}
X0M, CM = A.datos_motor(-1)[:2]
MOTOR_C = A.a_cuerpo(X0M + 2.2, CM[0], CM[1])
RUEDA = A.a_cuerpo(A.TREN["x_principal"], -A.TREN["y_principal"], A.Z_SUELO + 0.6)
CONTACTO = A.a_cuerpo(A.TREN["x_principal"], 0, A.Z_SUELO)
Y_PISTA = -0.35


class SpoilersReversas(ModoBase):
    VOZ_JSON = Path(__file__).parent / "voz.json"

    def base(self):
        t = {k: ValueTracker(v) for k, v in dict(spoiler=0, reversa=0, cabeceo=4.0, azimut=-122,
                                                   elevacion=17, campo=34, mx=0.0, my=0.0, mz=0.0,
                                                   x=0.0, sust=1.0, freno=0.0, v=250.0, cy=0.95).items()}
        av = self.avion3d(campo=t["campo"], alto_px=760, centro=lambda: (0, t["cy"].get_value()), colores_mando=False,
                          tren=True, spoiler=t["spoiler"], reversa=t["reversa"],
                          cabeceo=t["cabeceo"], azimut=t["azimut"], elevacion=t["elevacion"],
                          resaltar=RES, fan=lambda: 25 * t["x"].get_value(),
                          mirar=lambda: (t["mx"].get_value(), t["my"].get_value(), t["mz"].get_value()))
        def pista():
            y_suelo = av.a_pantalla([CONTACTO])[0][1]
            off = (t["x"].get_value() * 2.2) % 1.6
            g = VGroup(Line([-4.8, y_suelo, 0], [4.8, y_suelo, 0], color="#475569", stroke_width=6))
            for k in range(8):
                x0 = 4.8 - off - 1.6 * k
                g.add(Line([x0, y_suelo - 0.22, 0], [x0 - 0.7, y_suelo - 0.22, 0],
                           color="#94A3B8", stroke_width=4).set_opacity(0.8))
            return g
        pi = always_redraw(pista)
        fondo = brillo([0, 1.2, 0], C_SPO, 3.8, 0.8)
        return t, av, pi, fondo

    def velocidad(self, t):
        def lect():
            g = VGroup(T("VELOCIDAD", size=24, color=TEXTO_SEC, weight=HEAVY),
                       T(f"{t['v'].get_value():.0f} km/h", size=46, color=TEXTO, weight=HEAVY, font=F_TIT))
            return g.arrange(RIGHT, buff=0.3).move_to([0, -1.75, 0])
        return always_redraw(lect)

    def construct(self):
        self.iniciar()
        t, av, pi, fondo = self.base()
        preg, dest = self.gancho_texto("¿Cómo frena un avión", "AL ATERRIZAR?", C_SPO, 88)
        sello = self.sello("SPOILERS Y REVERSAS", C_SPO, DOWN * 3.95, size=48)

        # ---------- Gancho ----------
        self.portada(fondo, pi, av, preg)
        self.wait(0.15)
        self.poner_sello(sello)
        self.avanzar(2.2, t["x"].animate.set_value(1.2), t["cabeceo"].animate.set_value(2.5))

        # ---------- 1. Spoilers ----------
        t0, d = self.voz("b1")
        self.play(self.poner_cabecera("CÓMO FRENA AL ATERRIZAR", 3), run_time=0.01)
        self.dejar(preg, sello)
        barra, tit, fr, dt = self.bloque_ajustado(0, "Spoilers", "Rompen la sustentación del ala",
                                                  C_SPO, dato="y el peso pasa a las ruedas",
                                                  resaltar=["sustentación"])
        CG = np.array([0.0, 0.0, 0.0])
        sust = self.flecha3d(av, np.array([0.0, 0.0, 1.5]),
                             lambda: np.array([0, 0, 1.0 + 11.0 * t["sust"].get_value()]), C_SUST, 10)
        peso = self.flecha3d(av, RUEDA + np.array([0, 0, 3.0]),
                             lambda: np.array([0, 0, -(0.5 + 3.5 * (1 - t["sust"].get_value()))]), C_FRE, 10)
        es = always_redraw(lambda: self.etiqueta("SUSTENTACIÓN", C_SUST, ORIGIN, size=20)
                           .next_to(av.a_pantalla([np.array([0, 0, 2.5 + 11 * t["sust"].get_value()])])[0], RIGHT, buff=0.15))
        ep = always_redraw(lambda: self.etiqueta("PESO EN LAS RUEDAS", C_FRE, ORIGIN, size=20)
                           .next_to(av.a_pantalla([RUEDA])[0], LEFT, buff=0.35))
        vel = self.velocidad(t)
        self.abrir_bloque(barra, C_SPO, tit, fr, dt, t["x"].animate.set_value(2.0),
                          t["cabeceo"].animate.set_value(0.0))
        self.add(sust, peso, vel)
        self.play(FadeIn(es), FadeIn(ep), t["x"].animate.set_value(2.4), run_time=0.4, rate_func=linear)
        self.sonido("golpe", -12)
        self.play(t["spoiler"].animate.set_value(50), t["sust"].animate.set_value(0.08),
                  t["x"].animate.set_value(3.6), t["v"].animate.set_value(235), run_time=1.0,
                  rate_func=rate_functions.ease_out_cubic)
        self.avanzar(t0 + d - 0.15, t["x"].animate.set_value(5.5), t["v"].animate.set_value(215))

        # ---------- 2. Frenos ----------
        t0, d = self.voz("b2")
        for m in (es, ep):
            m.clear_updaters()
        self.dejar(tit, fr, dt, es, ep, sust)
        barra, tit, fr, dt = self.bloque_ajustado(1, "Frenos", "Las ruedas hacen la mayor parte",
                                                  C_FRE, dato="con el peso encima, agarran de verdad",
                                                  resaltar=["ruedas"])

        def calor():
            p = av.a_pantalla([RUEDA])[0]
            k = t["freno"].get_value()
            return VGroup(*[Circle(radius=r, stroke_width=0, fill_color="#F97316",
                                   fill_opacity=0.10 * k).move_to(p) for r in (0.18, 0.3, 0.45)])
        cal = always_redraw(calor)
        ef = always_redraw(lambda: self.etiqueta("FRENOS", C_FRE, ORIGIN, size=22)
                           .next_to(av.a_pantalla([RUEDA])[0], DOWN, buff=0.55))
        self.abrir_bloque(barra, C_FRE, tit, fr, dt, t["x"].animate.set_value(6.2))
        self.add(cal)
        self.play(FadeIn(ef), t["freno"].animate.set_value(1.0), t["x"].animate.set_value(6.8),
                  run_time=0.5, rate_func=linear)
        self.avanzar(t0 + d - 0.15, t["x"].animate.set_value(9.0), t["v"].animate.set_value(170))

        # ---------- 3. Reversas ----------
        t0, d = self.voz("b3")
        for m in (ef, cal):
            m.clear_updaters()
        self.dejar(tit, fr, dt, ef, cal, peso)
        barra, tit, fr, dt = self.bloque_ajustado(2, "Reversas", "Desvían el chorro hacia delante",
                                                  C_REV, dato="el fan gira igual: solo cambia la dirección del aire",
                                                  resaltar=["delante"])
        self.abrir_bloque(barra, C_REV, tit, fr, dt, t["mx"].animate.set_value(MOTOR_C[0]),
                          t["my"].animate.set_value(MOTOR_C[1]), t["mz"].animate.set_value(MOTOR_C[2]),
                          t["campo"].animate.set_value(13), t["azimut"].animate.set_value(-125),
                          t["elevacion"].animate.set_value(12), t["cy"].animate.set_value(0.4),
                          FadeOut(pi), run_time=0.9)
        self.sonido("whoosh", -10)
        self.play(t["reversa"].animate.set_value(1.0), t["x"].animate.set_value(10.0), run_time=1.0)

        def chorros():
            g = VGroup()
            k = t["reversa"].get_value()
            if k < 0.3:
                return g
            fase = (t["x"].get_value() * 1.5) % 1.0
            for ang in (-50, 0, 50):
                a = np.radians(ang)
                r = 1.25
                base = MOTOR_C + np.array([-0.3, r * np.sin(a) * 0.9, r * np.cos(a) * 0.9 - 0.2])
                dirv = np.array([3.0, 1.2 * np.sin(a), 1.2 * np.cos(a)]) * (0.6 + 0.4 * fase)
                q = av.a_pantalla([base, base + dirv])
                g.add(flecha(q[0], q[1], C_REV, 8))
            ent = av.a_pantalla([MOTOR_C + np.array([6.0, 0, 0]), MOTOR_C + np.array([3.0, 0, 0])])
            g.add(flecha(ent[0], ent[1], "#CBD5E1", 7))
            return g
        ch = always_redraw(chorros)
        self.add(ch)
        er = self.etiqueta("EL AIRE SALE HACIA DELANTE", C_REV, [0, -1.0, 0], size=24)
        self.play(FadeIn(er), run_time=0.3)
        self.avanzar(t0 + d - 0.15, t["x"].animate.set_value(13.0), t["v"].animate.set_value(110))

        # ---------- Cierre ----------
        t0, d = self.voz("cierre")
        ch.clear_updaters()
        self.dejar(tit, fr, dt, ch, er, vel, self.tema, self.barras)
        tj = VGroup(self.tarjeta("Spoilers: el peso pasa a las ruedas", C_SPO, size=34),
                    self.tarjeta("Frenos: la mayor parte del trabajo", C_FRE, size=34),
                    self.tarjeta("Reversas: ayuda extra (más en pista mojada)", C_REV, size=34)
                    ).arrange(DOWN, buff=0.22).move_to([0, -1.75, 0])
        preg2 = self.hud(frase_cinetica("¿Has oído ese rugido al aterrizar?", size=54,
                                        resaltar=["rugido"], color_resalte=C_SPO).move_to(DOWN * 4.75))
        self.cambio(LaggedStart(*[FadeIn(x, shift=RIGHT * 0.4) for x in tj], lag_ratio=0.3),
                    t["mx"].animate.set_value(0), t["my"].animate.set_value(0),
                    t["mz"].animate.set_value(0), t["campo"].animate.set_value(34),
                    t["azimut"].animate.set_value(-122), t["elevacion"].animate.set_value(17),
                    t["cy"].animate.set_value(1.9), FadeIn(pi),
                    t["reversa"].animate.set_value(0.0), run_time=1.0)
        self.play(FadeIn(preg2, shift=UP * 0.3), run_time=0.4)
        self.avanzar(t0 + d * 0.45, t["x"].animate.set_value(14.0))
        self.pulso(tj, 1.03)
        self.avanzar(t0 + d * 0.75, t["x"].animate.set_value(14.8))
        self.pulso(preg2, 1.05)
        self.avanzar(t0 + d - 0.75, t["x"].animate.set_value(15.4), t["spoiler"].animate.set_value(0),
                     t["cabeceo"].animate.set_value(4.0))
        preg, _ = self.gancho_texto("¿Cómo frena un avión", "AL ATERRIZAR?", C_SPO, 88)
        self.dejar(tj, preg2)
        self.cambio(FadeIn(preg), t["cy"].animate.set_value(0.95), run_time=0.45, desplazar=UP * 0.6)
        self.wait(0.3)

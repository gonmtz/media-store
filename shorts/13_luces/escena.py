"""
Short 13 (texto, sin voz): ¿por qué la luz roja va a la izquierda? Luces de un avión.
- Luces de navegación: roja en la punta del ala izquierda, verde en la derecha (cada una se ve
  desde delante hasta 110° hacia su lado) y blanca en la cola (hacia atrás). Igual que en los
  barcos. Con ellas se sabe hacia dónde va otro avión de noche.
- Anticolisión: baliza roja que destella (arriba y abajo del fuselaje) y destellos blancos
  (estroboscópicos) en las puntas de las alas.
Fuentes: OACI Anexo 2 (luces de las aeronaves); FAA 14 CFR 25.1385–25.1401.
Render:  manim -qh --fps 30 shorts/13_luces/escena.py Luces
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403
from lib import avion as A  # noqa: E402
from lib.avion2d import capa_3d  # noqa: E402

ROJA, VERDE = A.ROJA, A.VERDE
Y_AV = -0.3
Xp, Zp, _ = A.geometria_ala_en(A.ALA["y_punta"], 0.15)
Xe, Ze, _ = A.geometria_ala_en(A.ALA["y_punta"], 0.85)
NAV = [((A.X_CG - Xp, 17.15, Zp), ROJA, (-5, 110)),
       ((A.X_CG - Xp, -17.15, Zp), VERDE, (-110, 5)),
       ((A.X_CG - A.L - 0.05, 0.0, 1.0), "#FFFFFF", None)]
BALIZAS = [(A.X_CG - 15.8, 0.0, A.R_Z + 0.08), (A.X_CG - 17.5, 0.0, -A.R_Z - 0.1)]
ESTROBOS = [(A.X_CG - Xe, 17.2, Ze), (A.X_CG - Xe, -17.2, Ze)]
rng = np.random.default_rng(3)
ESTRELLAS = [(rng.uniform(-6, 6), rng.uniform(-9, 9), rng.uniform(0.008, 0.03)) for _ in range(140)]


def visible_nav(sector, az, el=0.0):
    """Cada luz de navegación se ve en su sector horizontal; desde muy arriba, todas."""
    if el > 45:
        return True
    az = (az + 180) % 360 - 180
    if sector is None:
        return abs(az) >= 108
    return sector[0] <= az <= sector[1]


def halo(p, color, intensidad, r=0.5):
    g = VGroup(*[Dot(p, radius=r * f, color=color).set_opacity(0.10 * intensidad)
                 for f in (1.0, 0.65, 0.4)])
    g.add(Dot(p, radius=r * 0.16, color=color).set_opacity(min(1, intensidad)))
    return g


class Luces(ShortBase):
    def construct(self):
        self.iniciar()
        self.add(VGroup(*[Dot([x, y, 0], radius=r, color=WHITE).set_opacity(0.5)
                          for x, y, r in ESTRELLAS]))
        reloj = ValueTracker(0.0)
        reloj.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(reloj)
        anticol = ValueTracker(0.0)          # 0 = apagadas, 1 = destellando

        def baliza():
            t = reloj.get_value() % 1.0
            return anticol.get_value() * (1.0 if t < 0.12 else 0.0)

        def estrobo():
            t = reloj.get_value() % 1.2
            return anticol.get_value() * (1.0 if (0.4 < t < 0.46 or 0.56 < t < 0.62) else 0.0)
        r = A.Avion3DReal(1080, 1080, 2, campo=38, colores_mando=False)
        t = {k: ValueTracker(v) for k, v in dict(azimut=180, elevacion=72, campo=43).items()}
        capa = capa_3d(r, 9.0, (0, Y_AV), noche=1.0, baliza=baliza, estrobo=estrobo, **t)

        def halos():
            g = VGroup()
            az = t["azimut"].get_value()
            for p, col, sector in NAV:
                if visible_nav(sector, az, t["elevacion"].get_value()):
                    g.add(halo(capa.a_pantalla([p])[0], col, 1.0, 0.55))
            b = baliza()
            if b > 0:
                for p in BALIZAS:
                    g.add(halo(capa.a_pantalla([p])[0], ROJA, 1.2, 0.75))
            e = estrobo()
            if e > 0:
                for p in ESTROBOS:
                    g.add(halo(capa.a_pantalla([p])[0], "#FFFFFF", 1.5, 0.9))
            return g
        capa_halos = always_redraw(halos)

        # ---------- Gancho (portada en t = 0) ----------
        preg = self.hud(frase_cinetica("¿Por qué la luz roja va a la izquierda?", size=58,
                                       resaltar=["roja", "izquierda?"], color_resalte=ROJA)
                        .move_to(UP * 4.6))
        self.portada(capa, capa_halos, preg)
        self.wait(0.4)
        self.sonido("pop", -8)
        self.pulso(preg, 1.06)
        self.play(t["elevacion"].animate.set_value(62), run_time=1.6,
                  rate_func=rate_functions.ease_in_out_sine)
        self.hasta(0, 3.4)

        # ---------- 1. Navegación ----------
        self.dejar(preg)
        self.play(self.poner_cabecera("LUCES DE UN AVIÓN", 3), run_time=0.01)
        barra, tit, fr, dt = self.bloque(0, "Navegación", "Roja a la izquierda, verde a la derecha y blanca en la cola",
                                         C_CABECEO, dato="igual que en los barcos",
                                         resaltar=["roja", "verde", "blanca"])
        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.2), barra.animate.set_fill(C_CABECEO))
        self.entrar_palabras(fr)
        self.play(FadeIn(dt), run_time=0.3)
        self.sonido("whoosh_suave", -10)
        self.play(t["azimut"].animate.set_value(90), t["elevacion"].animate.set_value(8),
                  run_time=2.2, rate_func=rate_functions.ease_in_out_sine)
        self.play(t["azimut"].animate.set_value(-25), run_time=2.0,
                  rate_func=rate_functions.ease_in_out_sine)
        self.hasta(0, 10.2)

        # ---------- 2. Hacia dónde va ----------
        self.dejar(tit, fr, dt)
        barra, tit, fr, dt = self.bloque(1, "¿Viene o va?", "Mira de qué lado está cada color",
                                         C_GUINADA, dato="roja y verde se ven de frente y de lado; la blanca, por detrás")
        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.2), barra.animate.set_fill(C_GUINADA),
                    t["azimut"].animate.set_value(0), t["elevacion"].animate.set_value(4))
        self.entrar_palabras(fr)
        self.play(FadeIn(dt), run_time=0.3)
        s1 = self.sello("VERDE A TU IZQUIERDA: VIENE HACIA TI", VERDE, DOWN * 4.4, size=34, angulo=2)
        self.poner_sello(s1)
        self.wait(1.2)
        self.play(FadeOut(s1), run_time=0.3)
        self.sonido("whoosh_suave", -10)
        self.play(t["azimut"].animate.set_value(180), t["elevacion"].animate.set_value(6), run_time=1.4,
                  rate_func=rate_functions.ease_in_out_sine)
        s2 = self.sello("SOLO VES LA BLANCA: SE ALEJA", "#FFFFFF", DOWN * 4.4, size=34, angulo=-2)
        self.poner_sello(s2)
        self.wait(1.1)
        self.hasta(0, 17.6)

        # ---------- 3. Anticolisión ----------
        self.dejar(tit, fr, dt, s2)
        barra, tit, fr, dt = self.bloque(2, "Destellos", "Rojos y blancos: «¡aquí estoy!»",
                                         C_ALABEO, dato="luces anticolisión: se ven desde muy lejos",
                                         resaltar=["rojos", "blancos:"])
        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.2), barra.animate.set_fill(C_ALABEO),
                    t["azimut"].animate.set_value(-40), t["elevacion"].animate.set_value(18))
        self.entrar_palabras(fr)
        self.play(FadeIn(dt), anticol.animate.set_value(1.0), run_time=0.4)
        self.wait(2.8)
        self.play(t["azimut"].animate.set_value(-70), run_time=1.6)
        self.hasta(0, 23.6)

        # ---------- Cierre (vuelve a la portada) ----------
        self.dejar(tit, fr, dt, self.tema, self.barras)
        cierre = self.hud(frase_cinetica("¿Las habías visto de noche?", size=58,
                                         resaltar=["noche?"], color_resalte=VERDE)
                          .move_to(UP * 4.6))
        self.cambio(t["azimut"].animate.set_value(180), t["elevacion"].animate.set_value(72),
                    anticol.animate.set_value(0.0), run_time=1.0)
        self.entrar_palabras(cierre)
        self.hasta(0, 26.4)
        self.dejar(cierre)
        self.cambio(FadeIn(preg), run_time=0.3, desplazar=UP * 0.6)
        self.wait(0.25)

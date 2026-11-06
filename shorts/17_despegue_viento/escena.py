"""
Short 17 (texto, sin voz): ¿por qué los aviones despegan contra el viento? Avión 3D de lado.
- Al ala solo le importa la velocidad respecto al aire. Ejemplo: necesita unos 270 km/h de
  aire para despegar (orden de magnitud de un bimotor de pasillo único; no es un dato oficial).
- Con 36 km/h de viento de frente basta con 234 km/h respecto al suelo; con viento de cola hacen
  falta 306 km/h. Con aceleración constante, la pista usada va con el cuadrado de la velocidad
  respecto al suelo: (234/270)² ≈ 0,75 → ≈ 25 % menos; (306/270)² ≈ 1,28 → ≈ 28 % más.
Simplificación: aceleración constante, sin rozamiento ni cambios de empuje.
Render:  manim -qh --fps 60 shorts/17_despegue_viento/escena.py Despegue
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403
from lib import avion as A  # noqa: E402
from lib.avion2d import capa_3d  # noqa: E402

V_DESP = 270.0           # km/h de aire para despegar (ejemplo)
VIENTO = 36.0            # km/h
Y_PISTA = -1.4
X_INI = -2.6
LARGO = 4.0              # pantalla: pista usada sin viento
C_AIRE, C_SUELO, C_VIENTO = C_CABECEO, C_GUINADA, "#94A3B8"
rng = np.random.default_rng(11)
RAFAGAS = [(rng.uniform(0, 1), rng.uniform(-0.9, 2.9), rng.uniform(0.7, 1.3)) for _ in range(26)]


RENDER = None
CONTACTO = A.a_cuerpo(A.TREN["x_principal"], 0, A.Z_SUELO)   # apoyo de las ruedas principales


def avion_3d(punto, cabeceo):
    """Avión 3D de lado (morro a la derecha, tren fuera). `punto()` es dónde va en pantalla el
    apoyo de las ruedas principales; `cabeceo()` en grados."""
    global RENDER
    if RENDER is None:
        RENDER = A.Avion3DReal(1080, 720, 2, campo=63, colores_mando=False)
    ref = capa_3d(RENDER, 9.0, (0, 0), azimut=-90, elevacion=4, tren=True)
    off = ref.a_pantalla([CONTACTO])[0]          # posición del apoyo con el centro en (0, 0)

    def centro():
        p = punto()
        return (p[0] - off[0], p[1] - off[1])
    return capa_3d(RENDER, 9.0, centro, azimut=-90, elevacion=4, tren=True, cabeceo=cabeceo)


class Despegue(ShortBase):
    def construct(self):
        self.iniciar()
        reloj = ValueTracker(0.0)
        reloj.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(reloj)
        pos = ValueTracker(0.0)          # 0–1 de la carrera de este caso
        cabeceo = ValueTracker(0.0)
        subida = ValueTracker(0.0)
        largo = ValueTracker(LARGO)      # pista que usa este caso (pantalla)
        viento = ValueTracker(0.0)       # km/h; > 0 de frente, < 0 de cola
        v_suelo_fin = ValueTracker(V_DESP)

        av = avion_3d(lambda: (X_INI + largo.get_value() * pos.get_value(),
                               Y_PISTA + subida.get_value()),
                      lambda: cabeceo.get_value())

        pista = VGroup(Line([-4.6, Y_PISTA, 0], [4.6, Y_PISTA, 0], color="#475569", stroke_width=6),
                       DashedLine([-4.6, Y_PISTA - 0.25, 0], [4.6, Y_PISTA - 0.25, 0],
                                  dash_length=0.3, color="#64748B", stroke_width=3))

        def usada():
            x1 = X_INI + largo.get_value() * pos.get_value()
            return Line([X_INI, Y_PISTA - 0.55, 0], [max(x1, X_INI + 0.01), Y_PISTA - 0.55, 0],
                        color=C_SUELO, stroke_width=10)
        barra_pista = always_redraw(usada)
        ref = DashedLine([X_INI + LARGO, Y_PISTA - 0.35, 0], [X_INI + LARGO, Y_PISTA - 0.8, 0],
                         color=TEXTO_SEC, stroke_width=3, dash_length=0.06)

        def rafagas():
            g = VGroup()
            w = viento.get_value()
            if abs(w) < 1:
                return g
            tt = reloj.get_value()
            s = -1 if w > 0 else 1        # de frente: el aire va hacia la izquierda
            for f, y, v in RAFAGAS:
                x = ((f + s * tt * 0.35 * v) % 1.0) * 9.6 - 4.8
                g.add(Line([x, y, 0], [x - s * 0.5, y, 0], color=C_VIENTO, stroke_width=3)
                      .set_opacity(0.55))
            return g
        capa_viento = always_redraw(rafagas)

        def lecturas():
            vs = v_suelo_fin.get_value() * np.sqrt(np.clip(pos.get_value(), 0, 1))
            va = vs + viento.get_value()
            filas = VGroup()
            for nombre, valor, col in (("AIRE", va, C_AIRE), ("SUELO", vs, C_SUELO)):
                n = T(nombre, size=26, color=col, weight=HEAVY)
                num = T(f"{max(0, valor):.0f} km/h", size=40, color=col, weight=HEAVY, font=F_TIT)
                filas.add(VGroup(n, num).arrange(RIGHT, buff=0.25))
            filas.arrange(DOWN, buff=0.15, aligned_edge=LEFT).move_to([0, -3.4, 0])
            return filas
        panel = always_redraw(lecturas)

        def carrera(v_suelo, w, rt=2.8):
            """Un despegue: viento w (km/h, + de frente), v_suelo final."""
            self.play(pos.animate.set_value(0), cabeceo.animate.set_value(0),
                      subida.animate.set_value(0), run_time=0.01)
            viento.set_value(w)
            v_suelo_fin.set_value(v_suelo)
            largo.set_value(LARGO * (v_suelo / V_DESP) ** 2)
            self.sonido("whoosh_suave", -10)
            self.play(pos.animate.set_value(1.0), run_time=rt, rate_func=lambda u: u ** 2)
            self.sonido("subida", -10)
            self.play(cabeceo.animate.set_value(9), run_time=0.5)
            self.play(subida.animate.set_value(0.6), run_time=0.6)

        # ---------- Gancho (portada en t = 0) ----------
        preg = self.hud(frase_cinetica("¿Por qué despegan contra el viento?", size=60,
                                       resaltar=["contra", "viento?"], color_resalte=C_AIRE)
                        .move_to(UP * 4.6))
        viento.set_value(VIENTO)
        pos.set_value(0.35)
        self.portada(pista, capa_viento, av, preg)
        self.wait(0.4)
        self.pulso(preg, 1.06)
        self.wait(1.2)
        self.hasta(0, 3.2)

        # ---------- 1. Lo que cuenta es el aire ----------
        self.dejar(preg)
        self.play(self.poner_cabecera("DESPEGAR CONTRA EL VIENTO", 3), run_time=0.01)
        barra, tit, fr, dt = self.bloque(0, "Sin viento", "Al ala solo le importa el aire que la cruza",
                                         C_AIRE, dato="ejemplo: despega con 270 km/h de aire",
                                         resaltar=["aire"])
        self.add(panel)        # (sin FadeIn: su número de glifos cambia en cada fotograma)
        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.2), barra.animate.set_fill(C_AIRE),
                    FadeIn(barra_pista), viento.animate.set_value(0), pos.animate.set_value(0))
        self.entrar_palabras(fr)
        self.play(FadeIn(dt), run_time=0.3)
        carrera(V_DESP, 0)
        self.play(FadeIn(ref), run_time=0.3)
        self.hasta(0, 10.0)

        # ---------- 2. Viento de frente ----------
        self.dejar(tit, fr, dt)
        barra, tit, fr, dt = self.bloque(1, "De frente", "Con 36 km/h de viento basta con 234 sobre la pista",
                                         C_SUELO, dato="≈ 25 % menos pista (aceleración constante)",
                                         resaltar=["234"])
        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.2), barra.animate.set_fill(C_SUELO))
        self.entrar_palabras(fr)
        self.play(FadeIn(dt), run_time=0.3)
        carrera(V_DESP - VIENTO, VIENTO)
        s1 = self.sello("MENOS PISTA", C_SUELO, [0, 1.6, 0], size=44)
        self.poner_sello(s1)
        self.hasta(0, 17.0)

        # ---------- 3. Viento de cola ----------
        self.dejar(tit, fr, dt, s1)
        barra, tit, fr, dt = self.bloque(2, "De cola", "Necesitaría 306 km/h sobre la pista",
                                         C_ALABEO, dato="≈ 28 % más pista: por eso se evita",
                                         resaltar=["306"])
        self.cambio(FadeIn(tit, shift=DOWN * 0.3, scale=1.2), barra.animate.set_fill(C_ALABEO))
        self.entrar_palabras(fr)
        self.play(FadeIn(dt), run_time=0.3)
        carrera(V_DESP + VIENTO, -VIENTO, 3.0)
        self.hasta(0, 23.4)

        # ---------- Cierre (vuelve a la portada) ----------
        self.dejar(tit, fr, dt, self.tema, self.barras)
        cierre = self.hud(frase_cinetica("Por eso se despega contra el viento", size=58,
                                         resaltar=["contra", "viento"], color_resalte=C_AIRE)
                          .move_to(UP * 4.6))
        self.cambio(pos.animate.set_value(0.35), cabeceo.animate.set_value(0),
                    subida.animate.set_value(0), largo.animate.set_value(LARGO),
                    viento.animate.set_value(VIENTO), run_time=0.8)
        self.entrar_palabras(cierre)
        self.dejar(panel, barra_pista, ref)
        self.hasta(0, 26.0)
        self.dejar(cierre)
        self.cambio(FadeIn(preg), run_time=0.3, desplazar=UP * 0.6)
        self.wait(0.25)

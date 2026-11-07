"""
Short 35 (narrado): V1, VR y V2. Avión 3D de lado en la pista; cinta de velocidad vertical con
las tres marcas. Velocidades de ejemplo (orden de magnitud de un bimotor de pasillo único; cambian
con el peso, la pista, la temperatura, la altitud y el viento): V1 270, VR 280, V2 295 km/h.
V2: velocidad de seguridad en el despegue, a alcanzar a 35 ft (10,7 m) sobre la pista.
El avión gira alrededor de las ruedas principales al rotar (la cola no toca: dibujo a escala).
Render:  manim -qh --fps 60 shorts/35_v1_vr_v2/escena.py Velocidades
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403
from lib.modos import ModoBase, flecha  # noqa: E402
from lib import avion as A  # noqa: E402
from lib.avion2d import capa_3d  # noqa: E402

C_V1, C_VR, C_V2 = C_ALABEO, C_GUINADA, C_CABECEO
V1, VR, V2 = 270, 280, 295
Y_PISTA, X_AV = -1.25, 0.95
VMIN, VMAX, Y0C, Y1C, XC = 220, 310, -0.45, 2.35, -2.95     # cinta de velocidad
CONTACTO = A.a_cuerpo(A.TREN["x_principal"], 0, A.Z_SUELO)
ANCHO, CAMPO = 8.2, 60


def y_vel(v):
    return Y0C + (v - VMIN) / (VMAX - VMIN) * (Y1C - Y0C)


class Velocidades(ModoBase):
    VOZ_JSON = Path(__file__).parent / "voz.json"

    def avion(self, cab, sub):
        ss = 2 if config.pixel_height >= 1000 else 1
        if not hasattr(self, "_render"):
            self._render = A.Avion3DReal(1080, 720, ss, campo=CAMPO, colores_mando=False)
        r = self._render
        k = ANCHO / r.ancho

        def centro():
            px = r.proyectar([CONTACTO], cabeceo=cab.get_value(), azimut=-90, elevacion=4, campo=CAMPO)[0]
            dx, dy = (px[0] - r.ancho / 2) * k, (r.alto / 2 - px[1]) * k
            return (X_AV - dx, Y_PISTA + sub.get_value() - dy)
        return capa_3d(r, ANCHO, centro, azimut=-90, elevacion=4, tren=True, cabeceo=cab, flap=10,
                       fan=lambda: 30 * self.renderer.time)

    def pista(self, dist):
        def dib():
            off = (dist.get_value() * 2.4) % 1.6
            g = VGroup(Rectangle(width=9.8, height=0.55, stroke_width=0, fill_color="#1E293B",
                                 fill_opacity=1).move_to([0, Y_PISTA - 0.28, 0]),
                       Line([-4.9, Y_PISTA, 0], [4.9, Y_PISTA, 0], color="#475569", stroke_width=6))
            for i in range(8):
                x0 = 4.8 - off - 1.6 * i
                g.add(Line([x0, Y_PISTA - 0.28, 0], [x0 - 0.7, Y_PISTA - 0.28, 0], color="#94A3B8",
                           stroke_width=4).set_opacity(0.8))
            return g
        return always_redraw(dib)

    def cinta(self, v, zonas):
        """Cinta vertical de velocidad (km/h): marcas V1, VR, V2 a la izquierda y lectura a la
        derecha, junto al puntero."""
        fijo = VGroup(RoundedRectangle(width=0.9, height=Y1C - Y0C + 0.5, corner_radius=0.12,
                                       fill_color="#0F172A", fill_opacity=0.95, stroke_color="#334155",
                                       stroke_width=2).move_to([XC, (Y0C + Y1C) / 2, 0]))
        for vv in range(VMIN, VMAX + 1, 10):
            y = y_vel(vv)
            largo = 0.22 if vv % 20 == 0 else 0.12
            fijo.add(Line([XC + 0.45 - largo, y, 0], [XC + 0.45, y, 0], color=TEXTO_SEC, stroke_width=2))
            if vv % 20 == 0:
                fijo.add(T(str(vv), size=17, color=TEXTO_SEC, weight=BOLD).move_to([XC - 0.1, y, 0]))
        for nombre, vv, col in (("V1", V1, C_V1), ("VR", VR, C_VR), ("V2", V2, C_V2)):
            y = y_vel(vv)
            fijo.add(Line([XC - 0.45, y, 0], [XC - 0.68, y, 0], color=col, stroke_width=6),
                     T(nombre, size=20, color=col, weight=HEAVY).next_to([XC - 0.68, y, 0], LEFT, buff=0.06))
        fijo.add(T("km/h", size=18, color=TEXTO_SEC, weight=BOLD).move_to([XC, Y0C - 0.45, 0]))

        def zona():
            k = zonas.get_value()
            g = VGroup()
            if k > 0.01:
                g.add(Rectangle(width=0.1, height=y_vel(V1) - Y0C, stroke_width=0, fill_color=C_V1,
                                fill_opacity=0.8 * k).move_to([XC - 0.4, (Y0C + y_vel(V1)) / 2, 0]),
                      Rectangle(width=0.1, height=Y1C - y_vel(V1), stroke_width=0, fill_color="#34D399",
                                fill_opacity=0.8 * k).move_to([XC - 0.4, (Y1C + y_vel(V1)) / 2, 0]))
            return g

        def puntero():
            vv = v.get_value()
            y = y_vel(min(max(vv, VMIN), VMAX))
            tri = Triangle(fill_color=TEXTO, fill_opacity=1, stroke_width=0).scale(0.11).rotate(PI / 2) \
                .move_to([XC + 0.55, y, 0])
            caja = RoundedRectangle(width=1.1, height=0.46, corner_radius=0.08, fill_color="#020617",
                                    fill_opacity=1, stroke_color=TEXTO, stroke_width=2).move_to([XC + 1.2, y, 0])
            num = T(f"{vv:.0f}", size=28, color=TEXTO, weight=HEAVY, font=F_TIT).move_to(caja)
            return VGroup(tri, caja, num)
        return VGroup(fijo, always_redraw(zona), always_redraw(puntero))

    def construct(self):
        self.iniciar()
        t = {k: ValueTracker(v) for k, v in dict(v=236, dist=0, cab=0, sub=0, zonas=0).items()}
        av = self.avion(t["cab"], t["sub"])
        pi = self.pista(t["dist"])
        ci = self.cinta(t["v"], t["zonas"])
        fondo = brillo([0.6, 0.6, 0], C_V2, 3.6, 0.8)
        preg, dest = self.gancho_texto("¿Qué son", "V1, VR Y V2?", C_VR, 96)
        sello = self.sello("VELOCIDADES DE DESPEGUE", C_VR, DOWN * 3.95, size=46)

        def rodar(t_fin, v_fin, *extra):
            """Avanza hasta t_fin: la distancia crece con la velocidad media."""
            rt = t_fin - self.renderer.time
            if rt < 0.3:
                return
            vm = (t["v"].get_value() + v_fin) / 2
            self.play(t["v"].animate.set_value(v_fin), t["dist"].animate.set_value(t["dist"].get_value() + vm / 100 * rt),
                      *extra, run_time=rt, rate_func=linear)

        # ---------- Gancho ----------
        self.portada(fondo, pi, av, ci, preg)
        self.wait(0.15)
        self.poner_sello(sello)
        rodar(2.65, 240)

        # ---------- 1. V1 ----------
        t0, d = self.voz("b1")
        self.play(self.poner_cabecera("VELOCIDADES DE DESPEGUE", 3), run_time=0.01)
        self.dejar(preg, sello)
        barra, tit, fr, dt = self.bloque_ajustado(0, "V1: decisión", "Pasada V1, sigue aunque falle un motor",
                                                  C_V1, dato="antes de V1 se frena · velocidades de ejemplo",
                                                  resaltar=["sigue"])
        self.abrir_bloque(barra, C_V1, tit, fr, dt, t["zonas"].animate.set_value(1.0), run_time=0.6)
        ea = self.etiqueta("ANTES: FRENAR", C_V1, [XC + 1.6, y_vel(V1) - 1.0, 0], size=20)
        ec = self.etiqueta("DESPUÉS: SEGUIR", "#34D399", [XC + 1.75, y_vel(V1) + 0.75, 0], size=20)
        self.play(FadeIn(ea), FadeIn(ec), run_time=0.3)
        rodar(t0 + d * 0.62, V1)
        self.sonido("golpe", -12)
        anillo = Circle(radius=0.35, stroke_color=C_V1, stroke_width=6).move_to([XC - 0.9, y_vel(V1), 0])
        self.play(anillo.animate.scale(2.2).set_stroke(opacity=0), t["v"].animate.set_value(V1 + 1),
                  run_time=0.6, rate_func=rate_functions.ease_out_cubic)
        self.remove(anillo)
        rodar(t0 + d - 0.15, V1 + 6)

        # ---------- 2. VR ----------
        t0, d = self.voz("b2")
        self.dejar(tit, fr, dt, ea, ec)
        barra, tit, fr, dt = self.bloque_ajustado(1, "VR: rotación", "El morro sube y el ala gana ángulo de ataque",
                                                  C_VR, dato="el avión gira sobre las ruedas principales",
                                                  resaltar=["morro", "sube"])
        self.abrir_bloque(barra, C_VR, tit, fr, dt, t["zonas"].animate.set_value(0.0))
        rodar(t0 + d * 0.3, VR)
        self.sonido("subida", -10)
        rodar(t0 + d * 0.55, VR + 4, t["cab"].animate(rate_func=smooth).set_value(9))
        q = av.a_pantalla([A.a_cuerpo(28.0, 0, 0.0), A.a_cuerpo(0.5, 0, 0.0)])
        dn = (q[1] - q[0]) / np.linalg.norm(q[1] - q[0])
        pn = q[1] + dn * 0.1
        eje = Line(pn, pn + dn * 1.25, color=C_VR, stroke_width=5)
        horiz = DashedLine(pn, pn + RIGHT * 1.25, color=TEXTO_SEC, stroke_width=3, dash_length=0.08)
        arco = Arc(radius=1.0, start_angle=0, angle=np.arctan2(dn[1], dn[0]), arc_center=pn, color=C_VR, stroke_width=6)
        ean = self.etiqueta("≈ 9°", C_VR, pn + np.array([0.75, 0.55, 0]), size=24)
        self.play(Create(horiz), Create(eje), Create(arco), FadeIn(ean), run_time=0.4)
        rodar(t0 + d * 0.8, VR + 7)
        self.dejar(horiz, eje, arco, ean)
        self.cambio(t["sub"].animate.set_value(0.25), run_time=0.4)
        rodar(t0 + d - 0.15, VR + 9, t["sub"].animate.set_value(0.55))

        # ---------- 3. V2 ----------
        t0, d = self.voz("b3")
        self.dejar(tit, fr, dt)
        barra, tit, fr, dt = self.bloque_ajustado(2, "V2: ascenso seguro", "La mínima para subir con margen sin un motor",
                                                  C_V2, dato="se alcanza a 10,7 m (35 ft) sobre la pista",
                                                  resaltar=["subir", "margen"])
        y35 = Y_PISTA + 1.25
        lin35 = DashedLine([-2.6, y35, 0], [4.6, y35, 0], color=C_V2, stroke_width=3, dash_length=0.12)
        e35 = self.etiqueta("10,7 m (escala no real)", C_V2, [2.6, y35 - 0.32, 0], size=18)
        self.abrir_bloque(barra, C_V2, tit, fr, dt, Create(lin35), FadeIn(e35))
        rodar(t0 + d * 0.6, V2, t["sub"].animate.set_value(1.6), t["cab"].animate.set_value(12))
        self.sonido("pop", -9)
        anillo = Circle(radius=0.35, stroke_color=C_V2, stroke_width=6).move_to([XC - 0.9, y_vel(V2), 0])
        self.play(anillo.animate.scale(2.2).set_stroke(opacity=0), t["v"].animate.set_value(V2 + 1),
                  t["sub"].animate.set_value(1.75), run_time=0.6)
        self.remove(anillo)
        rodar(t0 + d - 0.15, V2 + 3, t["sub"].animate.set_value(2.3))

        # ---------- Cierre ----------
        t0, d = self.voz("cierre")
        self.dejar(tit, fr, dt, lin35, e35, ci, av, pi, self.tema, self.barras)
        tj = VGroup(self.tarjeta("V1: decidir (frenar o seguir)", C_V1, size=36),
                    self.tarjeta("VR: rotar", C_VR, size=36),
                    self.tarjeta("V2: subir con margen", C_V2, size=36)).arrange(DOWN, buff=0.25).move_to([0, 1.3, 0])
        preg2 = self.cta("Si falla un motor justo antes de V1, ¿qué hace el piloto?", ["antes", "V1,"], C_VR, y=-3.7, size=54)
        self.cambio(LaggedStart(*[FadeIn(x, shift=RIGHT * 0.4) for x in tj], lag_ratio=0.3),
                    FadeIn(preg2, shift=UP * 0.3), run_time=0.8)
        self.hasta(t0, d * 0.33)
        self.pulso(tj, 1.03)
        self.hasta(t0, d * 0.66)
        self.pulso(preg2, 1.05)
        self.hasta(t0, d - 0.75)
        t2 = {k: ValueTracker(v) for k, v in dict(v=236, dist=0, cab=0, sub=0, zonas=0).items()}
        av2, pi2, ci2 = self.avion(t2["cab"], t2["sub"]), self.pista(t2["dist"]), self.cinta(t2["v"], t2["zonas"])
        preg, _ = self.gancho_texto("¿Qué son", "V1, VR Y V2?", C_VR, 96)
        self.dejar(tj, preg2)
        self.cambio(FadeIn(pi2), FadeIn(av2), FadeIn(ci2), FadeIn(preg), run_time=0.45, desplazar=UP * 0.6)
        self.wait(0.3)

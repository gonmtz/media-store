"""
Short 06: "¿Por qué las hélices están torcidas?".
Ejemplo numérico (no de una hélice concreta): avance V = 50 m/s (180 km/h), ω = 240 rad/s
(≈ 2300 rpm), pala de 0,95 m. Triángulo de velocidades por sección (tan φ = V / ω·r) sin la
velocidad inducida por la hélice. Sin torsión: 30° en toda la pala. Con torsión: β = φ + 4°.
Render (desde la raíz del repo):
  manim -qh --fps 30 shorts/06_helices/escena.py Helices
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403

C_VEL, C_VIENTO, C_TOR = C_CABECEO, C_ALABEO, C_GUINADA
C_MAL = C_ALABEO

V_AVANCE = 50.0          # m/s
OMEGA = 240.0            # rad/s
R_PALA = 0.95            # m
ALFA_BUENO = 4.0         # grados
BETA_FIJO = 30.0         # pala sin torsión (ejemplo)
# (nombre, radio en m, y del borde de ataque en pantalla)
SECCIONES = [("PUNTA", 0.95, 2.2), ("MITAD", 0.55, 0.55), ("RAÍZ", 0.25, -1.1)]
X_LE = 0.9
ESC_TRI = 0.012          # unidades de pantalla por m/s
X_VALOR = 2.95


def redondo(x):
    return int(np.round(x))


class Helices(ShortBase):
    VOZ_JSON = Path(__file__).parent / "voz.json"
    SUBS_DESDE = "velocidad"    # el gancho ya está escrito en pantalla
    SIN_SUBS_DESDE = "cierre"   # el cierre también

    def construct(self):
        self.iniciar()
        self.gancho()

        self.cabecera = T("HÉLICES", size=28, color=TEXTO_SEC,
                          weight=SEMIBOLD).move_to(UP * 6.85)
        self.barras = VGroup(*[RoundedRectangle(width=0.7, height=0.12, corner_radius=0.06,
                                                fill_color="#334155", fill_opacity=1,
                                                stroke_width=0) for _ in range(3)])
        self.barras.arrange(RIGHT, buff=0.15).move_to(UP * 6.4)
        self.play(FadeIn(self.cabecera, shift=DOWN * 0.2), FadeIn(self.barras), run_time=0.4)

        self.seccion_velocidad()
        self.seccion_viento()
        self.seccion_torsion()
        self.cierre()

    # ---------- utilidades ----------
    def textos(self, idx, nombre, frase, dato, etiqueta, clave, color):
        tit = T(nombre, size=116, color=color, weight=HEAVY, font=F_TIT).move_to(UP * 5.3)
        fr = T(frase, size=48, weight=BOLD).next_to(tit, DOWN, buff=0.28)
        dt = T(dato, size=28, color=TEXTO_SEC, weight=MEDIUM).next_to(fr, DOWN, buff=0.16)
        etq = T(etiqueta, size=28, color=TEXTO_SEC, weight=SEMIBOLD).move_to(DOWN * 3.6)
        ctl = pastilla(T(clave, size=52, color=color, weight=HEAVY, font=F_TIT), color)
        ctl.next_to(etq, DOWN, buff=0.2)
        return self.barras[idx], tit, fr, dt, etq, ctl

    def entrar_textos(self, barra, color, tit, fr, dt, *extra):
        self.play(barra.animate.set_fill(color), FadeIn(tit, shift=DOWN * 0.3, scale=1.15),
                  *extra, run_time=0.6)
        self.play(FadeIn(fr, shift=UP * 0.2), FadeIn(dt), run_time=0.45)

    def salir(self, *mobs, **kw):
        self.play(*[FadeOut(m, shift=LEFT * 0.6) for m in mobs], run_time=0.4, **kw)

    def etiqueta(self, texto, color, pos, size=26):
        t = T(texto, size=size, color=color, weight=BOLD)
        fondo = RoundedRectangle(width=t.width + 0.36, height=t.height + 0.24, corner_radius=0.14,
                                 fill_color=BG, fill_opacity=0.85, stroke_width=0)
        return VGroup(fondo, t).move_to(pos).set_z_index(30)

    def valor(self, texto, color, y, size=34):
        t = T(texto, size=size, color=color, weight=HEAVY, font=F_TIT)
        return t.move_to([X_VALOR, y - 0.35, 0]).set_z_index(30)

    # ---------- Gancho ----------
    def gancho(self):
        l1 = T("¿Por qué las hélices", size=62, weight=HEAVY, font=F_TIT)
        l2 = T("están", size=62, weight=HEAVY, font=F_TIT)
        pal = T("TORCIDAS?", size=110, color=BG, weight=HEAVY, font=F_TIT)
        caja = RoundedRectangle(width=pal.width + 0.7, height=pal.height + 0.5, corner_radius=0.3,
                                fill_color=C_TOR, fill_opacity=1, stroke_width=0).move_to(pal)
        destacado = VGroup(caja, pal)
        bloque = VGroup(l1, l2, destacado).arrange(DOWN, buff=0.32).move_to(UP * 4.0)
        destacado.rotate(-3 * DEGREES)

        betas = [angulo_flujo(V_AVANCE, OMEGA, r) + ALFA_BUENO for _, r, _ in SECCIONES]
        cols = [C_TOR, "#FCD98A", "#FEF3C7"]
        f = ValueTracker(0.0)
        centro = (-0.9, 1.4)

        def abanico():
            bs = [BETA_FIJO + f.get_value() * (b - BETA_FIJO) for b in betas]
            return pala_torcida(centro, bs, cuerda=4.2, colores=cols)
        pala = always_redraw(abanico)
        nota = T("una pala vista desde la punta: cada trozo, otro ángulo", size=22,
                 color=TEXTO_SEC, weight=MEDIUM).move_to([0, -1.0, 0])

        txt = T("NO ES UN DEFECTO", size=70, color=C_TOR, weight=HEAVY, font=F_TIT)
        marco = RoundedRectangle(width=txt.width + 0.6, height=txt.height + 0.5,
                                 corner_radius=0.2, stroke_color=C_TOR, stroke_width=10,
                                 fill_opacity=0)
        sello = VGroup(marco, txt.move_to(marco)).rotate(5 * DEGREES).move_to(DOWN * 2.6)

        t0, d = self.voz("gancho")
        self.play(FadeIn(l1, shift=UP * 0.3), FadeIn(pala), run_time=0.35)
        self.play(FadeIn(l2, shift=UP * 0.3), run_time=0.3)
        self.play(GrowFromCenter(caja), FadeIn(pal, scale=1.6), f.animate.set_value(1.0),
                  rate_func=rate_functions.ease_out_back, run_time=0.6)
        self.play(FadeIn(nota), run_time=0.3)
        self.hasta(0, 2.65)
        self.play(FadeIn(sello, scale=2.2), rate_func=rate_functions.ease_out_back, run_time=0.35)
        self.rellenar(t0, d, margen=-0.5)
        pala.clear_updaters()
        self.play(FadeOut(VGroup(bloque, sello, pala, nota), shift=UP * 0.6), run_time=0.35)

    # ---------- 1. Velocidad de cada trozo ----------
    def seccion_velocidad(self):
        t0, d = self.voz("velocidad")
        barra, tit, fr, dt, etq, ctl = self.textos(
            0, "Velocidad", "La punta va mucho más rápido",
            "v = ω·r · ejemplo: hélice de 1,9 m a unas 2300 rpm", "CRECE CON EL RADIO",
            "VELOCIDAD = ω·r", C_VEL)

        k = 2.55 / R_PALA                       # unidades de pantalla por metro
        hel = HeliceFrontal(centro=(0.0, 0.3), radio=2.55).set_z_index(10)
        self.hel = hel
        rad = [r for _, r, _ in SECCIONES]
        circ = VGroup(*[DashedVMobject(Circle(radius=r * k, color=C_VEL, stroke_width=3),
                                       num_dashes=int(20 + 40 * r)).set_stroke(opacity=0.55)
                        .move_to(hel.c) for r in rad]).set_z_index(2)
        puntos = VGroup(*[Dot(hel.punto(r * k), radius=0.1, color=C_VEL).set_z_index(15)
                          for r in rad])
        flechas, textos = VGroup(), VGroup()
        for r in rad:
            p = hel.c + UP * r * k
            u = OMEGA * r
            flechas.add(vector(p, p + LEFT * u * 0.009, C_VEL, ancho=10, punta=0.26).set_z_index(14))
            textos.add(self.etiqueta(f"{redondo(u / 10) * 10} m/s", C_VEL, ORIGIN, size=30)
                       .next_to(p, RIGHT, buff=0.32))
        nota = T("vista de frente", size=22, color=TEXTO_SEC, weight=MEDIUM)
        nota.move_to([2.7, -1.9, 0])

        self.entrar_textos(barra, C_VEL, tit, fr, dt, FadeIn(hel, scale=0.9), FadeIn(nota))
        # "Al girar, la punta recorre un círculo mucho mayor que la raíz"
        self.play(hel.angulo.animate.set_value(3 * TAU), Create(circ),
                  rate_func=rate_functions.ease_in_out_sine, run_time=2.4)
        self.play(FadeIn(puntos, scale=2), run_time=0.3)
        self.hasta(t0, 3.4)
        self.play(Indicate(circ[0], color=C_VEL, scale_factor=1.03),
                  Indicate(circ[2], color=C_VEL, scale_factor=1.15), run_time=0.8)
        # "así que va mucho más rápido"
        self.hasta(t0, 4.6)
        self.play(LaggedStart(*[GrowArrow(f_) for f_ in flechas[::-1]], lag_ratio=0.25),
                  LaggedStart(*[FadeIn(t) for t in textos[::-1]], lag_ratio=0.25), run_time=0.9)
        self.play(FadeIn(etq), FadeIn(ctl, scale=0.8), run_time=0.4)
        self.rellenar(t0, d)
        hel.clear_updaters()
        self.salir(tit, fr, dt, etq, ctl, hel, circ, puntos, flechas, textos, nota)

    # ---------- 2. Viento relativo ----------
    def seccion_viento(self):
        t0, d = self.voz("viento")
        barra, tit, fr, dt, etq, ctl = self.textos(
            1, "Viento", "Cada trozo recibe el aire distinto",
            "ejemplo: avance de 50 m/s · visto desde la punta", "LO QUE CAMBIA",
            "ÁNGULO DEL AIRE φ", C_VIENTO)

        self.filas = []
        nombres, giros, avances, rel, arcos, phis = (VGroup() for _ in range(6))
        for nombre, r, y in SECCIONES:
            le = np.array([X_LE, y, 0.0])
            tri = triangulo_velocidades(le, OMEGA * r, V_AVANCE, ESC_TRI, C_VEL, TEXTO,
                                        C_VIENTO)
            phi = np.degrees(tri["phi"])
            arco = angulo_entre(tri["origen"], 0, -tri["phi"], 0.55, C_VIENTO, ancho=5)
            n = T(nombre, size=28, color=TEXTO_SEC, weight=HEAVY, font=F_TIT)
            n.move_to([-3.05, y - 0.25, 0])
            nombres.add(n)
            giros.add(tri["giro"].set_z_index(12))
            avances.add(tri["avance"].set_z_index(12))
            rel.add(tri["relativo"].set_z_index(13))
            arcos.add(arco.set_z_index(13))
            phis.add(self.valor(f"φ = {redondo(phi)}°", C_VIENTO, y))
            self.filas.append({"le": le, "phi": phi, "y": y})
        self.giros, self.avances, self.rel, self.arcos = giros, avances, rel, arcos
        self.nombres = nombres

        # secciones de la pala (aún sin torsión), atenuadas
        self.betas = [ValueTracker(BETA_FIJO) for _ in SECCIONES]
        self.op_pala = ValueTracker(0.3)

        def secciones():
            g = VGroup()
            for fila, b in zip(self.filas, self.betas):
                s = seccion_pala(fila["le"], b.get_value(), cuerda=1.3)
                s.set_fill(opacity=self.op_pala.get_value())
                s.set_stroke(opacity=min(1.0, self.op_pala.get_value() + 0.3))
                g.add(s)
            return g.set_z_index(8)
        self.secciones = always_redraw(secciones)

        top = SECCIONES[0][2]
        lbl_giro = self.etiqueta("por el giro", C_VEL, [X_LE - 1.37, top + 0.6 + 0.3, 0],
                                 size=22)
        lbl_av = self.etiqueta("por el avance", TEXTO, [X_LE + 1.2, top + 0.4, 0], size=22)
        lbl_rel = self.etiqueta("aire que llega", C_VIENTO, [X_LE - 1.5, top - 0.12, 0],
                                size=22)

        self.entrar_textos(barra, C_VIENTO, tit, fr, dt, FadeIn(nombres),
                           FadeIn(self.secciones))
        # "Pero el avión también avanza"
        self.play(LaggedStart(*[GrowArrow(g) for g in giros], lag_ratio=0.15), FadeIn(lbl_giro),
                  run_time=0.5)
        self.hasta(t0, 1.0)
        self.play(LaggedStart(*[GrowArrow(a) for a in avances], lag_ratio=0.15), FadeIn(lbl_av),
                  run_time=0.5)
        # "el aire llega a cada trozo con un ángulo distinto"
        self.hasta(t0, 2.1)
        self.play(LaggedStart(*[GrowArrow(r_) for r_ in rel], lag_ratio=0.2), FadeIn(lbl_rel),
                  run_time=0.8)
        self.play(LaggedStart(*[Create(a) for a in arcos], lag_ratio=0.2),
                  LaggedStart(*[FadeIn(p, shift=LEFT * 0.2) for p in phis], lag_ratio=0.2),
                  run_time=0.9)
        # "muy inclinado cerca del centro"
        self.hasta(t0, 5.55)
        self.play(Indicate(phis[2], color=C_VIENTO, scale_factor=1.3),
                  Indicate(rel[2], color=C_VIENTO), run_time=1.0)
        # "y casi en el plano de giro en la punta"
        self.hasta(t0, 7.85)
        self.play(Indicate(phis[0], color=C_VIENTO, scale_factor=1.3),
                  Indicate(rel[0], color=C_VIENTO), run_time=1.0)
        self.play(FadeIn(etq), FadeIn(ctl, scale=0.8), run_time=0.4)
        self.rellenar(t0, d)
        self.salir(tit, fr, dt, etq, ctl, phis, lbl_giro, lbl_av, lbl_rel)

    # ---------- 3. Torsión ----------
    def seccion_torsion(self):
        t0, d = self.voz("torsion")
        barra, tit, fr, dt, etq, ctl = self.textos(
            2, "Torsión", "Un ángulo de ataque parecido",
            "sin torsión: 30° en toda la pala (ejemplo)", "LO RESUELVE",
            "LA TORSIÓN", C_TOR)
        dt2 = T("con torsión: unos 44° en la raíz y 16° en la punta", size=28, color=TEXTO_SEC,
                weight=MEDIUM).move_to(dt)

        def color_alfa(a):
            if abs(a - ALFA_BUENO) < 1.5:
                return C_TOR
            return C_MAL if (a < 0 or a > ALFA_CRIT) else TEXTO

        def indicador(i):
            def f():
                fila, b = self.filas[i], self.betas[i].get_value()
                le, phi = fila["le"], fila["phi"]
                a = b - phi
                col = color_alfa(a)
                u = np.array([np.cos(-phi * DEGREES), np.sin(-phi * DEGREES), 0])
                ext = DashedLine(le, le + u * 1.35, color=C_VIENTO, stroke_width=3,
                                 dash_length=0.08)
                arco = angulo_entre(le, -phi * DEGREES, -b * DEGREES, 1.0, col, ancho=6)
                txt = self.valor(f"α = {redondo(a)}°".replace("-", "−"), col, fila["y"])
                return VGroup(ext, arco, txt).set_z_index(20)
            return always_redraw(f)
        inds = [indicador(i) for i in range(3)]

        y_raiz, y_punta = SECCIONES[2][2], SECCIONES[0][2]
        mal_raiz = self.etiqueta("empuja al revés", C_MAL, [X_VALOR, y_raiz - 0.95, 0], size=22)
        mal_punta = self.etiqueta("en pérdida", C_MAL, [X_VALOR, y_punta - 0.95, 0], size=22)
        bien = VGroup(*[self.etiqueta("trabaja bien", C_TOR, [X_VALOR, f["y"] - 0.95, 0],
                                      size=22) for f in self.filas])

        self.entrar_textos(barra, C_TOR, tit, fr, dt, self.op_pala.animate.set_value(1.0),
                           *[g.animate.set_opacity(0.25) for g in self.giros],
                           *[a.animate.set_opacity(0.25) for a in self.avances],
                           *[a.animate.set_opacity(0.25) for a in self.arcos])
        self.play(*[FadeIn(i_) for i_ in inds], run_time=0.3)
        # "la raíz empujaría al revés"
        self.hasta(t0, 1.3)
        self.play(FadeIn(mal_raiz, scale=1.3), run_time=0.6)
        # "y la punta entraría en pérdida"
        self.hasta(t0, 3.3)
        self.play(FadeIn(mal_punta, scale=1.3), run_time=0.6)
        # "La torsión gira cada trozo"
        self.hasta(t0, 5.45)
        self.play(FadeOut(mal_raiz), FadeOut(mal_punta), FadeOut(dt), FadeIn(dt2), run_time=0.3)
        self.play(*[b.animate.set_value(f["phi"] + ALFA_BUENO)
                    for b, f in zip(self.betas, self.filas)],
                  rate_func=smooth, run_time=1.8)
        # "para que todos tengan un ángulo de ataque parecido"
        self.hasta(t0, 8.0)
        self.play(LaggedStart(*[FadeIn(b_, scale=1.2) for b_ in bien], lag_ratio=0.15),
                  FadeIn(etq), FadeIn(ctl, scale=0.8), run_time=0.6)
        self.rellenar(t0, d)
        for m in (self.secciones, *inds):
            m.clear_updaters()
        self.salir(tit, fr, dt2, etq, ctl, bien, self.secciones, *inds, self.giros, self.avances,
                   self.rel, self.arcos, self.nombres)

    # ---------- Cierre ----------
    def cierre(self):
        datos = [("Velocidad", "crece con el radio", "ω·r", C_VEL),
                 ("Viento", "llega con otro ángulo", "φ", C_VIENTO),
                 ("Torsión", "α parecido en la pala", "α ≈ 4°", C_TOR)]
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
            c = pastilla(T(ctl, size=30, color=col, weight=BOLD), col, relleno=0.12,
                         pad_x=0.22, pad_y=0.12)
            c.move_to(fondo.get_right() + LEFT * (c.width / 2 + 0.3))
            tarjetas.add(VGroup(fondo, acento, txt, c))
        tarjetas.arrange(DOWN, buff=0.3).move_to(UP * 3.3)

        lema = T("Una pala, muchos ángulos", size=40, color=TEXTO,
                 weight=SEMIBOLD).next_to(tarjetas, DOWN, buff=0.45)
        p1 = T("¿Te habías fijado", size=60, weight=HEAVY, font=F_TIT)
        p2 = T("alguna vez?", size=60, color=C_TOR, weight=HEAVY, font=F_TIT)
        preg = VGroup(p1, p2).arrange(DOWN, buff=0.15).next_to(lema, DOWN, buff=0.7)
        com = T("Te leo en comentarios", size=32, color=TEXTO_SEC, weight=MEDIUM)
        com.next_to(preg, DOWN, buff=0.25)

        t0, d = self.voz("cierre")
        self.play(LaggedStart(*[FadeIn(t, shift=RIGHT * 0.5) for t in tarjetas], lag_ratio=0.25),
                  run_time=1.0)
        self.play(FadeIn(lema, shift=UP * 0.2), run_time=0.4)
        self.hasta(t0, 2.2)
        self.play(FadeIn(preg, shift=UP * 0.3, scale=1.1), run_time=0.5)
        self.play(FadeIn(com), run_time=0.3)
        self.rellenar(t0, d, margen=1.5)

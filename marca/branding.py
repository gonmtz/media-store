"""
Identidad del canal "Por Qué Vuela".
Avatar (800x800):   BRAND=avatar manim -s -qh marca/branding.py Avatar
Banner (2560x1440): BRAND=banner manim -s -qh marca/branding.py Banner
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.porquevuela import *  # noqa: E402,F401,F403  (estilo, colores y aviones)


def _config(w, h, frame_h):
    config.pixel_width = w
    config.pixel_height = h
    config.frame_height = frame_h
    config.frame_width = frame_h * w / h


def arcos_marca(radio=3.0, ancho=26):
    """Tres arcos con los colores de los tres ejes: la firma visual del canal."""
    cols = [C_CABECEO, C_ALABEO, C_GUINADA]
    return VGroup(*[Arc(radius=radio, start_angle=PI / 2 + i * TAU / 3 + 0.18,
                        angle=TAU / 3 - 0.36, color=c, stroke_width=ancho)
                    for i, c in enumerate(cols)])


if os.environ.get("BRAND") == "banner":
    _config(2560, 1440, 9)
else:
    _config(800, 800, 8)


class Avatar(Scene):
    def construct(self):
        self.camera.background_color = BG
        avion, _, _ = avion_superior()
        avion.scale(0.62, about_point=ORIGIN).rotate(-35 * DEGREES, about_point=ORIGIN)
        avion.move_to(ORIGIN)
        self.add(resplandor(C_CABECEO, ORIGIN, rmax=3.0), arcos_marca(3.05, 24), avion)


class Banner(Scene):
    def construct(self):
        self.camera.background_color = BG
        w = config.frame_width
        puntos = VGroup(*[Dot([x, y, 0], radius=0.012, color="#334155")
                          for x in np.arange(-w / 2, w / 2 + 0.1, 0.35)
                          for y in np.arange(-4.5, 4.6, 0.35)]).set_opacity(0.55)
        # Zona segura visible en todos los dispositivos: 1546x423 px centrados
        seguro_w = 1546 / 2560 * w

        # Trayectorias de vuelo decorativas (solo visibles en pantallas anchas)
        trayectorias = VGroup(*[
            DashedVMobject(ParametricFunction(
                lambda t, a=a, f=f: np.array([t, a * np.sin(f * t + ph), 0]),
                t_range=[-w / 2, w / 2]), num_dashes=70, dashed_ratio=0.45)
            .set_stroke(c, width=3, opacity=0.18)
            for a, f, ph, c in [(2.6, 0.22, 0.4, C_CABECEO), (3.3, 0.17, 2.2, C_ALABEO),
                                (2.1, 0.28, 4.1, C_GUINADA)]
        ])

        # Marca: el mismo emblema que la foto de perfil
        avion, _, _ = avion_superior()
        avion.scale(0.5, about_point=ORIGIN).rotate(-35 * DEGREES, about_point=ORIGIN)
        emblema = VGroup(Circle(radius=2.45, fill_color=BG, fill_opacity=1, stroke_width=0),
                         resplandor(C_CABECEO, ORIGIN, rmax=2.4), arcos_marca(2.45, 20),
                         avion.move_to(ORIGIN))

        t1 = Text("Por Qué Vuela", font=F_TIT, weight=HEAVY, font_size=110, color=TEXTO)
        t1[6:].set_color(C_GUINADA)  # "Vuela" (los índices omiten espacios)
        t2 = Text("La aviación, explicada en un minuto", font=F_TXT, weight=MEDIUM,
                  font_size=40, color=TEXTO_SEC)
        temas = VGroup(*[
            pastilla(Text(txt, font=F_TXT, weight=BOLD, font_size=26, color=c), c,
                     relleno=0.14, pad_x=0.3, pad_y=0.14)
            for txt, c in [("Aerodinámica", C_CABECEO), ("Estabilidad", C_ALABEO),
                           ("Propulsión", C_GUINADA)]
        ]).arrange(RIGHT, buff=0.22)
        textos = VGroup(t1, t2, temas).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        textos.next_to(emblema, RIGHT, buff=0.7)
        todo = VGroup(emblema, textos)

        seguro_h = 423 / 1440 * config.frame_height
        todo.scale(min(0.9 * seguro_w / todo.width, 0.8 * seguro_h / todo.height))
        todo.move_to(ORIGIN)
        self.add(puntos, trayectorias, todo)

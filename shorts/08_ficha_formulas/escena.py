"""
Short 08 (ficha): "Lo que debes saber de ingeniería aeroespacial".
Una sola imagen fija con 6 fórmulas, sin voz; solo música. Pensada para guardarse.
Datos (atmósfera estándar ISA): ρ0 = 1,225 kg/m³, T0 = 288,15 K, p0 = 101 325 Pa,
gradiente −6,5 K/km hasta 11 km; a = √(1,4·287·288,15) ≈ 340 m/s; a 11 km (216,65 K) ≈ 295 m/s.
Re ala de avión en crucero ≈ 3·10⁷ (ρ 0,38, V 250 m/s, c 5 m); mosca ≈ 3·10² (V 2 m/s, c 2 mm).
Render de la imagen:  manim -qh -s shorts/08_ficha_formulas/escena.py Ficha
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403

FICHAS = [
    ("SUSTENTACIÓN", r"L = \tfrac{1}{2}\,\rho\,V^2\,S\,C_L",
     "El doble de velocidad da 4 veces la sustentación", C_CABECEO),
    ("RESISTENCIA", r"D = \tfrac{1}{2}\,\rho\,V^2\,S\,C_D",
     "En crucero: sustentación = peso y empuje = resistencia", C_ALABEO),
    ("NÚMERO DE MACH", r"M = V/a\,,\quad a = \sqrt{\gamma R T}",
     "a ≈ 340 m/s al nivel del mar · ≈ 295 m/s a 11 km", C_GUINADA),
    ("NÚMERO DE REYNOLDS", r"\mathrm{Re} = \rho\,V\,c\,/\,\mu",
     "Ala de avión ≈ 3·10⁷ · ala de mosca ≈ 3·10²", C_CABECEO),
    ("ATMÓSFERA ESTÁNDAR", r"\rho_0 = 1{,}225\ \mathrm{kg/m^3}\,,\quad T_0 = 15\ ^{\circ}\mathrm{C}",
     "La temperatura baja 6,5 °C por km (hasta 11 km)", C_ALABEO),
    ("COHETES (TSIOLKOVSKY)", r"\Delta v = I_{\mathrm{sp}}\,g_0\,\ln(m_0/m_f)",
     "Para llegar a órbita baja hacen falta ≈ 9–10 km/s", C_GUINADA),
]

ALTO_FICHA = 1.6
Y_TOP = 3.65          # primera ficha; todo dentro de y ∈ [-6, 6] (recorte 3:4)


def ficha(nombre, formula, nota, color, y):
    fondo = RoundedRectangle(width=8.1, height=ALTO_FICHA - 0.14, corner_radius=0.22,
                             fill_color=PANEL, fill_opacity=1, stroke_color=color,
                             stroke_width=2, stroke_opacity=0.45)
    barra = RoundedRectangle(width=0.12, height=ALTO_FICHA - 0.42, corner_radius=0.06,
                             fill_color=color, fill_opacity=1, stroke_width=0)
    barra.move_to(fondo.get_left() + RIGHT * 0.3)
    tit = T(nombre, size=24, color=color, weight=HEAVY)
    f = MathTex(formula, color=TEXTO).scale(0.95)
    if f.height > 0.55:
        f.scale_to_fit_height(0.55)
    if f.width > 6.9:
        f.scale_to_fit_width(6.9)
    n = T(nota, size=22, color=TEXTO_SEC, weight=MEDIUM)
    if n.width > 7.2:
        n.scale_to_fit_width(7.2)
    col = VGroup(tit, f, n).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
    if col.height > ALTO_FICHA - 0.42:
        col.scale_to_fit_height(ALTO_FICHA - 0.42)
    col.next_to(barra, RIGHT, buff=0.3)
    g = VGroup(fondo, barra, col)
    return g.move_to([0, y, 0])


class Ficha(ShortBase):
    def construct(self):
        self.add(rejilla())
        sup = T("LO QUE DEBES SABER DE", size=34, color=TEXTO_SEC, weight=SEMIBOLD)
        tit = T("INGENIERÍA AEROESPACIAL", size=60, weight=HEAVY, font=F_TIT)
        cab = VGroup(sup, tit).arrange(DOWN, buff=0.12).move_to(UP * 5.15)
        fichas = VGroup(*[ficha(*d, Y_TOP - i * ALTO_FICHA) for i, d in enumerate(FICHAS)])
        pie = T("@porquevuela · Guárdalo para tu próximo examen", size=24, color=TEXTO_SEC,
                weight=SEMIBOLD).move_to(DOWN * 5.6)
        self.portada(cab, fichas, pie)
        self.wait(0.1)

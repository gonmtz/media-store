"""
Short 40 (ficha): señales luminosas de la torre (OACI, Anexo 2, apéndice 1), para un avión sin
radio. Imagen fija sin voz.
- Verde fija: en vuelo, autorizado a aterrizar · en tierra, autorizado a despegar.
- Roja fija: en vuelo, ceda el paso y siga en circuito · en tierra, alto.
- Verde intermitente: en vuelo, regrese para aterrizar · en tierra, autorizado a rodar.
- Roja intermitente: en vuelo, aeródromo peligroso, no aterrice · en tierra, apártese del área
  de aterrizaje en uso.
- Blanca intermitente: en vuelo, aterrice aquí y vaya a la plataforma · en tierra, vuelva al
  punto de partida en el aeródromo.
Render de la imagen:  manim -qh -s shorts/40_senales_torre/escena.py SenalesTorre
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from lib.porquevuela import *  # noqa: E402,F401,F403

VERDE, ROJA, BLANCA = "#22C55E", "#EF4444", "#F8FAFC"
FILAS = [
    (VERDE, False, "Verde fija", "Autorizado a aterrizar", "Autorizado a despegar"),
    (ROJA, False, "Roja fija", "Ceda el paso y siga en circuito", "Alto"),
    (VERDE, True, "Verde intermitente", "Regrese para aterrizar", "Autorizado a rodar"),
    (ROJA, True, "Roja intermitente", "Aeródromo peligroso: no aterrice", "Apártese del área de aterrizaje"),
    (BLANCA, True, "Blanca intermitente", "Aterrice aquí y vaya a la plataforma", "Vuelva al punto de partida"),
]


def lampara(c, color, intermitente):
    c = np.array([*c, 0])
    g = VGroup()
    if intermitente:
        for i, x in enumerate((-0.32, 0.0, 0.32)):
            for r, op in ((0.2, 0.15), (0.13, 0.3)):
                g.add(Circle(radius=r, stroke_width=0, fill_color=color, fill_opacity=op).move_to(c + RIGHT * x))
            g.add(Circle(radius=0.085, stroke_width=0, fill_color=color, fill_opacity=1).move_to(c + RIGHT * x))
    else:
        for r, op in ((0.42, 0.1), (0.32, 0.2), (0.24, 0.35)):
            g.add(Circle(radius=r, stroke_width=0, fill_color=color, fill_opacity=op).move_to(c))
        g.add(Circle(radius=0.17, stroke_width=0, fill_color=color, fill_opacity=1).move_to(c))
    return g


def texto(t, ancho, size=21, color=TEXTO, weight=BOLD):
    m = Paragraph(*partir(t, 19), font=F_TXT, font_size=size, weight=weight, alignment="center",
                  line_spacing=0.6).set_color(color)
    if m.width > ancho:
        m.scale_to_fit_width(ancho)
    return m


def partir(t, n):
    pal, lineas, act = t.split(), [], ""
    for p in pal:
        if len(act) + len(p) + 1 > n and act:
            lineas.append(act)
            act = p
        else:
            act = (act + " " + p).strip()
    lineas.append(act)
    return lineas


class SenalesTorre(ShortBase):
    def construct(self):
        self.add(rejilla())
        X = (-2.95, -0.05, 2.95)          # columnas: señal, en vuelo, en tierra
        AN = (2.7, 2.7, 2.7)
        y0, h = 2.75, 1.42
        cab = VGroup()
        for x, txt, col in zip(X, ("SEÑAL", "EN VUELO", "EN TIERRA"), (TEXTO_SEC, C_CABECEO, C_GUINADA)):
            cab.add(T(txt, size=24, color=col, weight=HEAVY).move_to([x, y0 + 0.78, 0]))
        tabla = VGroup()
        for i, (col, inter, nombre, vuelo, tierra) in enumerate(FILAS):
            y = y0 - i * h
            fondo = RoundedRectangle(width=8.8, height=h - 0.14, corner_radius=0.2, fill_color="#111827",
                                     fill_opacity=0.92, stroke_color="#334155", stroke_width=1.5).move_to([0, y - 0.15, 0])
            lam = lampara((X[0], y + 0.12), col, inter)
            nom = T(nombre, size=20, color=col if col != BLANCA else TEXTO, weight=HEAVY).move_to([X[0], y - 0.45, 0])
            if nom.width > AN[0]:
                nom.scale_to_fit_width(AN[0])
            tv = texto(vuelo, AN[1]).move_to([X[1], y - 0.15, 0])
            tt = texto(tierra, AN[2]).move_to([X[2], y - 0.15, 0])
            tabla.add(fondo, lam, nom, tv, tt)
        for x in (-1.5, 1.45):
            tabla.add(DashedLine([x, y0 + 0.45, 0], [x, y0 - 4 * h - 0.8, 0], color="#334155", stroke_width=2,
                                 dash_length=0.08))
        sup = T("SI EL AVIÓN SE QUEDA SIN RADIO", size=28, color=TEXTO_SEC, weight=SEMIBOLD)
        tit = T("LAS LUCES DE LA TORRE", size=64, weight=HEAVY, font=F_TIT)
        if tit.width > 8.6:
            tit.scale_to_fit_width(8.6)
        cabe = VGroup(sup, tit).arrange(DOWN, buff=0.12).move_to(UP * 5.05)
        nota = T("Señales con pistola de luz · OACI, Anexo 2", size=20, color=TEXTO_SEC,
                 weight=MEDIUM).move_to(DOWN * 4.4)
        pie = T("@porquevuela · Guárdalo", size=26, color=TEXTO_SEC, weight=SEMIBOLD).move_to(DOWN * 5.6)
        reto = T("¿Has visto alguna vez estas luces? Cuéntalo en comentarios ↓", size=28, color=C_GUINADA, weight=HEAVY).move_to(DOWN * 5.0)
        if reto.width > 8.4:
            reto.scale_to_fit_width(8.4)
        self.add(brillo([0, 0.3, 0], C_GUINADA, 4.6, 0.5), cab, tabla, cabe, nota, reto, pie)
        self.wait(0.1)

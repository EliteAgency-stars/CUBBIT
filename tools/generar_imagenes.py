"""Genera las imágenes PNG del repositorio CUBBIT a partir de los datos de la propuesta.
Uso: python3 tools/generar_imagenes.py  (desde la raíz CUBBIT/)
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

OUT = os.path.join(os.path.dirname(__file__), "..", "assets")
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})

INK = "#2d2d2d"      # Obsidian Black (marca)
ROVERE = "#B08A5E"   # aprox. melamina Rovere Pelikano
GLOSS = "#FAFAFA"    # high gloss blanco
CREMA = "#EDE3CF"    # muros crema/marfil
SPC = "#C9B396"      # piso SPC Bosco Beige (aprox.)
LED = "#FFE9A8"      # luz LED 4000K
MUTED = "#8A8A8A"


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)


# 1. Plano esquemático de zonificación -------------------------------------
def plano():
    W, D, WA = 9.97, 3.75, 6.41
    fig, ax = plt.subplots(figsize=(12, 5.6))
    ax.add_patch(Rectangle((0, 0), W, D, fc=SPC, ec=INK, lw=3))
    ax.add_patch(Rectangle((0, 0), WA, D, fc="#E4D6BC", ec="none"))
    ax.add_patch(Rectangle((WA, 0), W - WA, D, fc="#D9D4CC", ec="none"))
    ax.plot([WA, WA], [0, D], color=INK, lw=4)
    ax.add_patch(Rectangle((WA - 0.06, 1.2), 0.12, 0.80, fc="white", ec=INK, lw=1))  # puerta 0.80
    ax.text(WA + 0.12, 1.6, "Puerta\n0.80×2.10", fontsize=8, va="center")
    # fachada
    ax.plot([0, W], [0, 0], color="#555", lw=7, solid_capstyle="butt")
    ax.text(W / 2, -0.35, "FACHADA · cortina enrollable motorizada + letrero CUBITT (acero inox + LED 5000K)",
            ha="center", fontsize=9, color=INK, weight="bold")
    items = [  # (x, y, w, h, color, label)
        (0.15, 2.95, 5.9, 0.6, GLOSS, "Panel mural backlit · 5 módulos 1.13×1.60 (fondo)"),
        (1.0, 1.35, 1.70, 0.75, ROVERE, "Isla relojes #1\n1.70×0.75"),
        (3.2, 1.35, 1.70, 0.75, ROVERE, "Isla relojes #2\n1.70×0.75"),
        (0.15, 0.25, 0.55, 2.4, ROVERE, "Mueble\ntermos"),
        (4.95, 0.25, 1.30, 0.70, ROVERE, "Mostrador caja"),
        (1.0, 0.25, 2.0, 0.45, "white", "Bancos zona experiencia"),
        (WA + 0.15, 2.85, 3.25, 0.7, "#BDBDBD", "Estantería metálica"),
        (WA + 2.2, 0.25, 1.2, 0.6, "#BDBDBD", "Escritorio + silla"),
    ]
    for x, y, w, h, c, l in items:
        ax.add_patch(Rectangle((x, y), w, h, fc=c, ec=INK, lw=1.2))
        ax.text(x + w / 2, y + h / 2, l, ha="center", va="center", fontsize=8)
    ax.text(WA / 2, 2.55, "ZONA A · COMERCIAL  ≈24.0 m²", ha="center", weight="bold", fontsize=11)
    ax.text(WA + (W - WA) / 2, 2.2, "ZONA B · BODEGA / SERVICIO\n≈13.4 m²", ha="center", weight="bold", fontsize=10)
    for x0, x1, t in [(0, WA, "6.41 m"), (WA, W, "3.56 m"), (0, W, "9.97 m")]:
        y = 4.05 if t != "9.97 m" else 4.45
        ax.annotate("", (x0, y), (x1, y), arrowprops=dict(arrowstyle="<->", color=INK))
        ax.text((x0 + x1) / 2, y + 0.08, t, ha="center", fontsize=9)
    ax.annotate("", (W + 0.25, 0), (W + 0.25, D), arrowprops=dict(arrowstyle="<->", color=INK))
    ax.text(W + 0.35, D / 2, "≈3.75 m", rotation=90, va="center")
    ax.set_xlim(-0.3, W + 0.8); ax.set_ylim(-0.6, 4.8); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("Tienda CUBITT · C.C. Centro Mayor — Planta esquemática de zonificación (37.4 m²)",
                 weight="bold", fontsize=12, loc="left")
    fig.text(0.01, 0.01, "Esquema ilustrativo generado desde la propuesta. Posiciones aproximadas; no reemplaza el plano arquitectónico.",
             fontsize=7.5, color=MUTED)
    save(fig, "01-plano-zonificacion.png")


# 2. Costos por capítulo -----------------------------------------------------
CAPS = [("Carpintería arquitectónica", 49138472), ("Señalética y branding", 26082000),
        ("Eléctricas e iluminación", 22988000), ("Cortina enrollable", 16500000),
        ("Aire acondicionado", 11800000), ("Preliminares y desmontes", 8372500),
        ("Cielo raso y fachada", 8220660), ("Estructura metálica", 4776000),
        ("Muros y pintura", 4191859), ("Pisos SPC", 3523500), ("Aseo y entrega", 1530000)]


def costos():
    total = sum(v for _, v in CAPS)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    names = [n for n, _ in CAPS][::-1]; vals = [v / 1e6 for _, v in CAPS][::-1]
    bars = ax.barh(names, vals, color=[ROVERE if i >= len(vals) - 2 else "#9C9C9C" for i in range(len(vals))])
    for b, v in zip(bars, vals):
        ax.text(b.get_width() + 0.5, b.get_y() + b.get_height() / 2,
                f"${v:,.1f} M · {v * 1e6 / total:.1%}".replace(",", "."), va="center", fontsize=9)
    ax.set_xlabel("Millones COP (costo directo)")
    ax.set_xlim(0, 62)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.set_title(f"Costo directo por capítulo — total ${total:,.0f} COP".replace(",", "."),
                 weight="bold", loc="left")
    fig.text(0.01, -0.02, r"Con AIU 30 %: \$204.259.888 · Con IVA sobre utilidad: \$207.842.292", fontsize=9, color=INK)
    save(fig, "02-costos-por-capitulo.png")


# 3. Cronograma ------------------------------------------------------------
FASES = [("F1 Preliminares", 1, 4, "obra"), ("F2 Estructura + drywall", 5, 9, "obra"),
         ("F3 Redes eléctricas base", 6, 8, "obra"), ("F4a Carpintería (taller)", 1, 14, "carp"),
         ("F5 Cielo raso + cenefa LED", 10, 15, "obra"), ("F6 Muros estuco y pintura", 15, 19, "obra"),
         ("F7 Piso SPC", 20, 22, "obra"), ("F8 Aire acondicionado", 20, 22, "obra"),
         ("F4b Carpintería (instalación)", 21, 26, "carp"), ("F9 Iluminación final", 27, 30, "rem"),
         ("F11 Cortina (nocturna)", 27, 28, "noct"), ("F10 Señalética y branding", 31, 35, "rem"),
         ("F12 Pintura final + retoques", 36, 37, "rem"), ("F13 Aseo e inspección C.C.", 38, 39, "rem"),
         ("F14 Acta de entrega", 40, 42, "rem")]
COL = {"obra": "#9C9C9C", "carp": ROVERE, "rem": INK, "noct": "#4A5A8A"}


def gantt():
    fig, ax = plt.subplots(figsize=(11, 6))
    for i, (n, a, b, k) in enumerate(FASES):
        ax.barh(i, b - a + 1, left=a - 1, color=COL[k], height=0.6)
        ax.text(b + 0.3, i, f"D{a}–D{b}", va="center", fontsize=8)
    ax.set_yticks(range(len(FASES))); ax.set_yticklabels([f[0] for f in FASES]); ax.invert_yaxis()
    for w in range(7, 43, 7): ax.axvline(w, color="#ddd", lw=1, zorder=0)
    ax.set_xticks([3.5 + 7 * i for i in range(6)]); ax.set_xticklabels([f"Semana {i + 1}" for i in range(6)])
    ax.set_xlim(0, 46)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=COL[k], label=l) for k, l in
                       [("obra", "Obra civil"), ("carp", "Carpintería"), ("rem", "Remates y entrega"), ("noct", "Trabajo nocturno")]],
              loc="lower left", fontsize=8, frameon=False)
    ax.set_title("Cronograma de obra CUBITT — plazo contractual 40 días", weight="bold", loc="left")
    save(fig, "03-cronograma.png")


# 4. Mueble CUBITT / ATTENZA (alzado) -------------------------------------
def mueble():
    fig, ax = plt.subplots(figsize=(7, 8.2))
    W, H, cop, col, base = 2200, 2480, 300, 601, 812
    body = H - cop
    ax.add_patch(Rectangle((0, body), W, cop, fc=GLOSS, ec=INK, lw=1.6))
    ax.text(W / 2, body + cop / 2, "COPETE · logo de marca (alto brillo)", ha="center", va="center", fontsize=9, weight="bold")
    ax.add_patch(Rectangle((0, 0), col, body, fc=ROVERE, ec=INK, lw=1.4))
    for k in range(1, 5):
        ax.plot([0, col], [body * k / 5] * 2, color=INK, lw=0.8)
    ax.text(col / 2, body / 2, "Columna\nrepisas", ha="center", va="center", fontsize=9, color="white", weight="bold")
    ax.add_patch(Rectangle((col, base), W - col, body - base, fc="white", ec=INK, lw=1.4))
    ax.add_patch(Rectangle((col, base + 380), W - col, 18, fc=LED, ec=INK, lw=0.8))
    ax.text(col + (W - col) / 2, base + (body - base) * 0.68, "Nicho de exhibición\nfondo blanco 1599 × 1368", ha="center", fontsize=9)
    ax.text(col + (W - col) / 2, base + 300, "Repisa expositora", ha="center", fontsize=8, color=MUTED)
    ax.add_patch(Rectangle((col, 0), W - col, base, fc=ROVERE, ec=INK, lw=1.4))
    ax.plot([col + (W - col) / 2] * 2, [0, base], color=INK, lw=0.8)
    ax.add_patch(Rectangle((col, base - 20), W - col, 20, fc=GLOSS, ec=INK, lw=0.8))
    ax.text(col + (W - col) / 2, base / 2, "Gabinete inferior · mesón relojes h=812", ha="center", va="center",
            fontsize=8.5, color="white", weight="bold")

    def dim(x0, y0, x1, y1, t, off, vertical=False):
        ax.annotate("", (x0, y0), (x1, y1), arrowprops=dict(arrowstyle="<->", color=INK, lw=0.9))
        if vertical:
            ax.text(x0 + off, (y0 + y1) / 2, t, rotation=90, va="center", ha="center", fontsize=8)
        else:
            ax.text((x0 + x1) / 2, y0 + off, t, ha="center", fontsize=8)
    dim(0, H + 120, W, H + 120, "2200", 40)
    dim(0, -120, col, -120, "601", -90); dim(col, -120, W, -120, "1599", -90)
    dim(W + 120, 0, W + 120, H, "2480", 70, True)
    dim(-120, body, -120, H, "300", -70, True); dim(-120, 0, -120, base, "812", -70, True)
    ax.set_xlim(-350, W + 350); ax.set_ylim(-320, H + 300); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("Mueble CUBITT / ATTENZA — alzado frontal (mm)\nfondo 480 mm · Rovere + alto brillo blanco",
                 weight="bold", fontsize=11)
    save(fig, "04-mueble-attenza-alzado.png")


# 5. Paleta de materiales ---------------------------------------------------
def paleta():
    sw = [(INK, "Obsidian Black", "Marca · #2d2d2d"),
          (GLOSS, "High gloss blanco\n18 mm", "Superficies de exhibición"),
          (ROVERE, "Melamina Rovere\nPelikano 15 mm", "Estructura de mobiliario"),
          (CREMA, "Pintura mate\ncrema / marfil", "Muros interiores"),
          (SPC, "Piso SPC\nBosco Beige", "1220×180×5 mm"),
          (LED, "LED 4000–4100K\n/ 5000K", "Mobiliario neutro · branding frío")]
    fig, ax = plt.subplots(figsize=(11, 3.4))
    for i, (c, n, d) in enumerate(sw):
        ax.add_patch(Rectangle((i * 1.85, 0.9), 1.6, 1.4, fc=c, ec="#999", lw=1))
        ax.text(i * 1.85 + 0.8, 0.55, n, ha="center", fontsize=8.5, weight="bold")
        ax.text(i * 1.85 + 0.8, 0.15, d, ha="center", fontsize=7.5, color=MUTED)
    ax.set_xlim(-0.1, 11.1); ax.set_ylim(-0.05, 2.6); ax.axis("off")
    ax.set_title("Paleta de materiales y color — Tienda CUBITT (tonos aproximados)", weight="bold", loc="left")
    save(fig, "05-paleta-materiales.png")


# 6. Estado de obra a Semana 5 ----------------------------------------------
def estado():
    rows = [("Preliminares y desmontes", "C"), ("Estructura metálica", "C"), ("Eléctricas e iluminación", "C"),
            ("Aire acondicionado", "C"), ("Cielo raso y fachada", "C"), ("Muros y pintura", "C"),
            ("Pisos", "C"), ("Carpintería arquitectónica", "P"), ("Señalética y branding", "P"),
            ("Cortina enrollable", "P"), ("Aseo y entrega", "N")]
    c = {"C": ("#3C8D5A", "Completado"), "P": ("#D9A21B", "En proceso"), "N": ("#B0B0B0", "Pendiente")}
    fig, ax = plt.subplots(figsize=(8, 5))
    for i, (n, s) in enumerate(rows):
        ax.add_patch(Rectangle((0, -i), 0.35, 0.7, fc=c[s][0]))
        ax.text(0.5, -i + 0.35, n, va="center", fontsize=10)
        ax.text(4.3, -i + 0.35, c[s][1], va="center", fontsize=10, color=c[s][0], weight="bold")
    ax.set_xlim(0, 6); ax.set_ylim(-len(rows) + 0.5, 1.1); ax.axis("off")
    ax.set_title("Estado de obra por capítulo — corte Semana 5", weight="bold", loc="left")
    save(fig, "06-estado-obra-s5.png")


if __name__ == "__main__":
    for f in (plano, costos, gantt, mueble, paleta, estado):
        f()
    print("OK:", sorted(os.listdir(OUT)))

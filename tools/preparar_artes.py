"""Genera las versiones web de ARTES CUBITT usadas por la propuesta 2027.

Entrada:  propuesta-2027/artes-cubitt/originales/  (copia de la carpeta ARTES CUBITT)
Salida:   propuesta-2027/artes-cubitt/web/         (artes y fotos optimizadas)
          propuesta-2027/artes-cubitt/productos/   (recortes PNG sin fondo para 3D y planos)

Uso: python tools/preparar_artes.py   (requiere Pillow, numpy y PyMuPDF)
"""
import os
import numpy as np
from PIL import Image
import pymupdf

RAIZ = os.path.join(os.path.dirname(__file__), "..", "propuesta-2027", "artes-cubitt")
ORIG = os.path.join(RAIZ, "originales")
WEB = os.path.join(RAIZ, "web")
PROD = os.path.join(RAIZ, "productos")
os.makedirs(WEB, exist_ok=True)
os.makedirs(PROD, exist_ok=True)

# Artes (vallas) del mobiliario: archivo original -> nombre web
ARTES = {
    "Cubitt_Viva Pro 58.6 x 43.80 cm.jpg": "arte-viva-pro-2.jpg",
    "Cubitt Terra 30.5x92 cm.jpg": "arte-terra.jpg",
    "Mueble_Lateral Aura Pro 40x76 cm.jpg": "arte-aura-pro-2.jpg",
    "CTBJ-DDR6-2.png": "arte-jr-rapunzel.jpg",
    "D2B87314-C5D6-4A54-89A7-C7A6524803EB.png": "arte-collab-ilustrado.jpg",
    "Captura de pantalla 2026-02-02 144328.jpg": "arte-nueva-era-horizontal.jpg",
    "GUS02717.jpg": "foto-tumbler-azul.jpg",
    "GUS02723.jpg": "foto-mug-azul.jpg",
}

# Productos sobre fondo blanco -> recorte PNG
PRODUCTOS = {
    "Viva Pro 2 negro.jpg": "viva-pro-2",
    "Viva 2 Rosado.jpg": "viva-2-rosado",
    "Viva Lite Lilac.jpg": "viva-lite-lilac",
    "Aura 2 Azul.jpg": "aura-2-azul",
    "Aura Pro 2 Chocolate.jpg": "aura-pro-2",
    "Terra verde.webp": "terra-verde",
    "CT-PWANC1-.webp": "power-anc-negro",
    "CT-PWANCL9-2.png": "power-anc-crema",
    "CT-PWBUDS2-2.jpg": "power-buds-2",
    "CT-PWPRO2-2-1.webp": "power-pro-2",
    "Cubitt 2025 Kit 1000x1000 CT-PWGO2-7 1.jpg": "power-go-2",
    "Cubitt 2025 Kit 1000x1000 CT-PWPLUS2-1 1.jpg": "power-plus-2",
    "CT-PWMINI1-2.jpg": "power-mini",
    "Termo Cubitt CTHB24-4D Burgandy 01.webp": "termo-burgandy",
    "CT-COF3-A.jpg": "coffee-mug-verde",
    "CT-TUMB4O-1.webp": "tumbler-lila",
    "CT-SCALE8-01.webp.jpeg": "bascula",
    "CTJR-DY6C-1.webp": "jr-rapunzel",
    "CTJR-PP4M_01.jpg": "jr-paw-patrol",
    "Reloj Inteligente Cubitt Jr. CTJR-2 Artic Blue 01.jpg": "jr-artic-blue",
    "Reloj Inteligente Cubitt Teens CTTN-3 Forest Green 01.jpg": "teens-forest-green",
    "Headphones Jr. Cubitt CTANCJR-5 Pink 01.jpg": "headphones-jr-pink",
    "Tumbler Jr. Cubitt CT-TUMBS5F Hot Pink 01.jpg": "tumbler-jr-pink",
    "CTBJ-DDR6-1.webp": "hydro-bottle-jr-rapunzel",
    "CTBJ-PWL4 0.webp": "hydro-bottle-jr-paw-patrol",
    "CT-MUGS2-1.webp": "mug-jr-azul",
}


def guardar_web(src, dst, lado=1600):
    im = Image.open(src).convert("RGB")
    im.thumbnail((lado, lado), Image.LANCZOS)
    im.save(dst, quality=84, optimize=True, progressive=True)


def recortar(src, dst, lado=640):
    """Quita el fondo blanco (umbral + suavizado del borde) y recorta al producto."""
    im = Image.open(src).convert("RGB")
    a = np.asarray(im).astype(np.int16)
    blanco = (a.min(axis=2) > 238) & ((a.max(axis=2) - a.min(axis=2)) < 14)
    alfa = np.where(blanco, 0, 255).astype(np.uint8)
    m = Image.fromarray(alfa).filter(__import__("PIL.ImageFilter", fromlist=["x"]).GaussianBlur(1.2))
    rgba = im.copy()
    rgba.putalpha(m)
    caja = m.point(lambda v: 255 if v > 20 else 0).getbbox()
    if caja:
        rgba = rgba.crop(caja)
    rgba.thumbnail((lado, lado), Image.LANCZOS)
    rgba.save(dst, optimize=True)


for o, n in ARTES.items():
    guardar_web(os.path.join(ORIG, o), os.path.join(WEB, n))

# Backing "Nueva Era" 56,5 x 114 cm (PDF de impresión)
doc = pymupdf.open(os.path.join(ORIG, "Backing Muebles 56.5x114 cm (1) (1).pdf"))
pix = doc[0].get_pixmap(dpi=38)
Image.frombytes("RGB", (pix.width, pix.height), pix.samples).save(os.path.join(WEB, "arte-nueva-era.jpg"), quality=86)

for o, n in PRODUCTOS.items():
    recortar(os.path.join(ORIG, o), os.path.join(PROD, n + ".png"))

print("artes:", len(ARTES) + 1, "productos:", len(PRODUCTOS))

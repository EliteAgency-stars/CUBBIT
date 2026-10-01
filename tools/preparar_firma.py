"""Extrae el logo de FARUK AGENCIA (PDF) a PNG para la firma de la propuesta.

Uso: python tools/preparar_firma.py "ruta/LOGO FARUK AGENCIA CREATIVA.pdf"
Salida: propuesta-2027/assets/firma/faruk-agencia-blanco.png (logo blanco, fondo transparente)
        propuesta-2027/assets/firma/faruk-agencia-negro.png  (logo negro, fondo transparente)
"""
import os, sys
import numpy as np
from PIL import Image
import pymupdf

pdf = sys.argv[1]
salida = os.path.join(os.path.dirname(__file__), "..", "propuesta-2027", "assets", "firma")
os.makedirs(salida, exist_ok=True)

pix = pymupdf.open(pdf)[0].get_pixmap(dpi=200)
im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
lum = np.asarray(im.convert("L")).astype(np.float32)
# El logo es blanco sobre fondo negro: la luminancia es la opacidad
alfa = np.clip((lum - 40) * 255 / 175, 0, 255).astype(np.uint8)
caja = Image.fromarray(alfa).point(lambda v: 255 if v > 30 else 0).getbbox()
alfa_img = Image.fromarray(alfa).crop(caja)
for nombre, color in (("blanco", (255, 255, 255)), ("negro", (30, 28, 26))):
    logo = Image.new("RGBA", alfa_img.size, color + (0,))
    logo.putalpha(alfa_img)
    logo.thumbnail((1200, 1200), Image.LANCZOS)
    logo.save(os.path.join(salida, f"faruk-agencia-{nombre}.png"), optimize=True)
print("ok", alfa_img.size)

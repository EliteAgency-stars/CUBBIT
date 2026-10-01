"""Genera propuesta-2027/artes-cubitt/INVENTARIO.md a partir de artes-cubitt/originales/."""
import os
from PIL import Image

RAIZ = os.path.join(os.path.dirname(__file__), "..", "propuesta-2027", "artes-cubitt")
ORIG = os.path.join(RAIZ, "originales")


def tipo(nombre):
    n = nombre.lower()
    if n.endswith((".skp", ".psd")):
        return "Archivo fuente (SketchUp / Photoshop)"
    if "presentacion" in n:
        return "Presentación de marca"
    if any(k in n for k in ("medidas", "base ", "base audifonos", "plano", "dintel")):
        return "Plano / medidas"
    if any(k in n for k in ("backing", "x92", "58.6", "40x76", "arte", "captura", "d2b87314")):
        return "Arte / valla"
    if n.endswith(".xlsx"):
        return "Documento"
    return "Foto de producto"


filas = []
for f in sorted(os.listdir(ORIG), key=str.lower):
    ruta = os.path.join(ORIG, f)
    px = ""
    if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        try:
            with Image.open(ruta) as im:
                px = f"{im.width} × {im.height}"
        except Exception:
            px = "?"
    filas.append(f"| {f} | {tipo(f)} | {os.path.getsize(ruta) // 1024:,} | {px} |".replace(",", "."))

with open(os.path.join(RAIZ, "INVENTARIO.md"), "w", encoding="utf-8") as fh:
    fh.write("# Inventario · ARTES CUBITT\n\n")
    fh.write("Copia de la carpeta **ARTES CUBITT** entregada por FARUK AGENCIA (artes del mobiliario, fotos de producto, planos y archivos fuente).\n")
    fh.write("Las versiones optimizadas para la web están en `web/` y los recortes sin fondo en `productos/` (`python tools/preparar_artes.py`).\n\n")
    fh.write(f"Total: **{len(filas)} archivos**.\n\n| Archivo | Tipo | KB | Píxeles |\n|---|---|---:|---|\n")
    fh.write("\n".join(filas) + "\n")
print(len(filas), "archivos")

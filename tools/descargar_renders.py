"""Descarga los renders Higgsfield que siguen en uso y guarda versiones web en propuesta-2027/renders/.

Uso: python tools/descargar_renders.py
- RENDERS_V3: renders compuestos del mueble Jr & Teens (Higgsfield + logo oficial y artes a la talla con
  tools/componer_renders.py). Después de correrlo, en propuesta-2027/js/media.js se pueden cambiar sus entradas
  v3(...) por v2('<nombre>', ...) para que la página use las copias locales.
Los demás renders (familia, mesa, touch, vendedor, mueble, modular, sobremesa, logo, material, despiece) son v5 y se
hacen con tools/render_blender.py sobre los modelos exactos de los SketchUp; este script no los toca.
"""
import os, shutil, subprocess, sys
from PIL import Image

HF_V3 = "https://d2ol7oe51mr4n9.cloudfront.net/user_3H8VPOIlKTSsf171GizUHRYwT0M/"
RENDERS_V3 = {
    "kids": "e51149cf-4d2f-48de-8b69-57f931aa6aad.jpg",
    "kids-producto": "fbbe9958-05cf-4165-970d-5521c527c2b7.jpg",
}
SALIDA = os.path.join(os.path.dirname(__file__), "..", "propuesta-2027", "renders")
CACHE = sys.argv[1] if len(sys.argv) > 1 else SALIDA
os.makedirs(SALIDA, exist_ok=True)
CURL = shutil.which("curl.exe") or shutil.which("curl")

for base, lista in ((HF_V3, RENDERS_V3),):
    for nombre, archivo in lista.items():
        origen = os.path.join(CACHE, f"{nombre}-original{os.path.splitext(archivo)[1]}")
        if not os.path.exists(origen):
            subprocess.run([CURL, "-sf", "-o", origen, base + archivo], check=True)
        im = Image.open(origen).convert("RGB")
        grande = im.copy(); grande.thumbnail((2000, 2000), Image.LANCZOS)
        grande.save(os.path.join(SALIDA, f"{nombre}.jpg"), quality=84, optimize=True, progressive=True)
        chico = im.copy(); chico.thumbnail((900, 900), Image.LANCZOS)
        chico.save(os.path.join(SALIDA, f"{nombre}-900.jpg"), quality=80, optimize=True, progressive=True)
        if CACHE == SALIDA:
            os.remove(origen)
        print(nombre, im.size)

"""Descarga los renders de la propuesta y guarda versiones web en propuesta-2027/renders/.

Uso: python tools/descargar_renders.py
- RENDERS_V3: renders compuestos (Higgsfield + logo oficial y artes reales con tools/componer_renders.py).
- RENDERS_V2: renders v2 que siguen en uso (sin logo).
Después de correrlo, en propuesta-2027/js/media.js se pueden cambiar las entradas v3(...) por v2('<nombre>', ...)
para que la página use las copias locales en lugar del almacenamiento de Higgsfield.
"""
import os, shutil, subprocess, sys
from PIL import Image

HF_V3 = "https://d2ol7oe51mr4n9.cloudfront.net/user_3H8VPOIlKTSsf171GizUHRYwT0M/"
RENDERS_V3 = {
    "familia": "77f04329-ae83-4f91-b630-f3955a263dff.jpg",
    "mesa": "4e60c9af-f0eb-4195-a346-6228e579bac9.jpg",
    "touch": "1341c4da-7eab-4232-bd2e-5cb4e80e6d71.jpg",
    "mueble": "12ef1acb-8fec-4b21-81a6-ea887406d995.jpg",
    "modular": "3dd36272-d654-4c46-926c-5ec67b65e268.jpg",
    "sobremesa": "cca2e26e-e725-4676-bde9-7defe1502e90.jpg",
    "kids": "e51149cf-4d2f-48de-8b69-57f931aa6aad.jpg",
    "kids-producto": "fbbe9958-05cf-4165-970d-5521c527c2b7.jpg",
    "logo": "6a793f50-d5a7-41a4-8e7f-7273f4b895b8.jpg",
    "despiece": "8f5fde88-8aa5-4864-9714-99bc96f77767.jpg",
}
HF_V2 = "https://d8j0ntlcm91z4.cloudfront.net/user_3H8VPOIlKTSsf171GizUHRYwT0M/hf_20261001_"
RENDERS_V2 = {
    "vendedor": "065646_11dac186-3aa7-4d05-b305-6d97f4879a95.png",
    "material": "065646_99dcf6eb-e9c5-462b-aa6a-a7c7661654b2.png",
}
SALIDA = os.path.join(os.path.dirname(__file__), "..", "propuesta-2027", "renders")
CACHE = sys.argv[1] if len(sys.argv) > 1 else SALIDA
os.makedirs(SALIDA, exist_ok=True)
CURL = shutil.which("curl.exe") or shutil.which("curl")

for base, lista in ((HF_V3, RENDERS_V3), (HF_V2, RENDERS_V2)):
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

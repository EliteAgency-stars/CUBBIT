"""Descarga los renders de Higgsfield y guarda versiones web en propuesta-2027/renders/.

Uso: python tools/descargar_renders.py
Lee la lista de renders de RENDERS (nombre -> URL del resultado en Higgsfield).
"""
import os, subprocess, sys
from PIL import Image

CDN = "https://d8j0ntlcm91z4.cloudfront.net/user_3H8VPOIlKTSsf171GizUHRYwT0M/hf_20261001_"
RENDERS = {
    "familia": "065646_c0b06d67-518b-4890-a62b-cf04799a3864",
    "mesa": "065647_730df2a6-4d97-4eb4-81e8-e3000a4bc742",
    "touch": "065648_675206bc-b086-4e6a-a020-bcc26607f1b8",
    "vendedor": "065646_11dac186-3aa7-4d05-b305-6d97f4879a95",
    "mueble": "065646_4bdc7bab-ea98-485a-a634-517a98609040",
    "modular": "065646_a36f40b1-66c1-4f51-98ac-14b27d3593cb",
    "sobremesa": "065646_c2b128b6-c69a-4065-ae0c-17071bb4b62f",
    "kids": "065646_79a0eba2-13f8-4a1a-a96c-d1625f8fadfe",
    "logo": "065646_3dc38fc4-9276-49cd-b843-f8c4536aed05",
    "material": "065646_99dcf6eb-e9c5-462b-aa6a-a7c7661654b2",
    "despiece": "065646_be966f1e-0511-4517-bf49-b665715b8229",
    "fuente-mesa": "065646_3e4e374f-4643-4610-80fa-b9cba03fcad4",
}
SALIDA = os.path.join(os.path.dirname(__file__), "..", "propuesta-2027", "renders")
CACHE = sys.argv[1] if len(sys.argv) > 1 else SALIDA
os.makedirs(SALIDA, exist_ok=True)

for nombre, rid in RENDERS.items():
    png = os.path.join(CACHE, f"{nombre}.png")
    if not os.path.exists(png):
        subprocess.run(["curl.exe", "-s", "-o", png, CDN + rid + ".png"], check=True)
    im = Image.open(png).convert("RGB")
    grande = im.copy(); grande.thumbnail((2000, 2000), Image.LANCZOS)
    grande.save(os.path.join(SALIDA, f"{nombre}.jpg"), quality=84, optimize=True, progressive=True)
    chico = im.copy(); chico.thumbnail((900, 900), Image.LANCZOS)
    chico.save(os.path.join(SALIDA, f"{nombre}-900.jpg"), quality=80, optimize=True, progressive=True)
    print(nombre, im.size)

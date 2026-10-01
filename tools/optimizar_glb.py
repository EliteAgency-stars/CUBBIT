"""Reduce el peso de un GLB generado por Higgsfield: re-comprime las texturas a JPEG/WebP de 1024 px.

Uso: python tools/optimizar_glb.py entrada.glb salida.glb [lado_max]
Requiere: pip install pygltflib pillow
"""
import io, sys
from PIL import Image
from pygltflib import GLTF2, BufferFormat

ent, sal = sys.argv[1], sys.argv[2]
lado = int(sys.argv[3]) if len(sys.argv) > 3 else 1024
g = GLTF2().load(ent)
g.convert_buffers(BufferFormat.BINARYBLOB)
blob = g.binary_blob()

# Inventario de bufferViews usados por imágenes
img_views = {im.bufferView: i for i, im in enumerate(g.images) if im.bufferView is not None}
tot_img = sum(g.bufferViews[v].byteLength for v in img_views)
print(f"imágenes: {len(img_views)} · {tot_img / 1e6:.1f} MB de {len(blob) / 1e6:.1f} MB")

nuevo = bytearray()
for vi, bv in enumerate(g.bufferViews):
    datos = blob[bv.byteOffset or 0:(bv.byteOffset or 0) + bv.byteLength]
    if vi in img_views:
        im = Image.open(io.BytesIO(datos))
        tiene_alfa = im.mode in ("RGBA", "LA") and im.getextrema()[-1][0] < 255
        im.thumbnail((lado, lado), Image.LANCZOS)
        out = io.BytesIO()
        if tiene_alfa:
            im.save(out, "PNG", optimize=True); mime = "image/png"
        else:
            im.convert("RGB").save(out, "JPEG", quality=82, optimize=True); mime = "image/jpeg"
        datos = out.getvalue()
        g.images[img_views[vi]].mimeType = mime
    while len(nuevo) % 4:
        nuevo.append(0)
    bv.byteOffset = len(nuevo)
    bv.byteLength = len(datos)
    nuevo.extend(datos)
g.buffers[0].byteLength = len(nuevo)
g.set_binary_blob(bytes(nuevo))
g.save_binary(sal)
print(f"salida: {len(nuevo) / 1e6:.1f} MB")

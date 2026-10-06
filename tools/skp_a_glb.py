"""Convierte la mesa de experiencia de SketchUp (.skp) a GLB para la web, con la geometría exacta del archivo.

- Ejes: SketchUp (x fondo, y ancho, z arriba, pulgadas) -> glTF (X derecha, Y arriba, Z hacia el cliente, metros).
- Materiales del proyecto: Capri (cuerpo), Duna (tope y elevador), inox (zócalo), aluminio (marco),
  caja de luz con el arte a la talla (tools/artes_a_la_talla.py) y LED 3000K en la línea de sombra.
- El logo que venía modelado en el .skp se reemplaza por el archivo oficial en platino, con halo cálido 3000K.
- Los relojes que en el archivo quedaron flotando delante de la mesa ya vienen corregidos en el .skp leído
  (la matriz de cada grupo se lee por filas).

Uso: python tools/skp_a_glb.py mesa.skp salida.glb
Requiere numpy, Pillow, mapbox_earcut, pygltflib (y lo que pide tools/artes_a_la_talla.py).
"""
import io
import os
import sys
import tempfile

import numpy as np
from PIL import Image, ImageFilter
from pygltflib import (GLTF2, Accessor, Asset, Buffer, BufferView, Image as GImage, Material, Mesh, Node,
                       PbrMetallicRoughness, Primitive, Sampler, Scene, Texture, TextureInfo)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import artes_a_la_talla  # noqa: E402
from skp_lector import Modelo, extraer  # noqa: E402

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'propuesta-2027')
CM = 0.0254 * 100  # pulgadas -> cm
LOGO = os.path.join(RAIZ, 'assets', 'logo', 'logo-cubitt-platino.png')
CAPRI = os.path.join(RAIZ, 'assets', 'materiales', 'capri.jpg')
DUNA = os.path.join(RAIZ, 'assets', 'materiales', 'duna.jpg')


def a_gltf(p_cm):
    """(x fondo, y ancho, z alto) en cm, frente en x=0 y ancho de 0 a -80 -> metros glTF centrados."""
    x, y, z = p_cm[:, 0], p_cm[:, 1], p_cm[:, 2]
    return np.stack([-(y + 40.0), z, 25.0 - x], 1) / 100.0


class Constructor:
    def __init__(self):
        self.g = GLTF2(asset=Asset(generator='CUBBIT tools/skp_a_glb.py', version='2.0'))
        self.blob = bytearray()
        self.g.samplers.append(Sampler(magFilter=9729, minFilter=9987, wrapS=10497, wrapT=10497))
        self.g.samplers.append(Sampler(magFilter=9729, minFilter=9987, wrapS=33648, wrapT=33648))  # espejo: sin costuras
        self.nodos = []

    def _vista(self, datos, target=None):
        while len(self.blob) % 4:
            self.blob.append(0)
        off = len(self.blob)
        self.blob.extend(datos)
        self.g.bufferViews.append(BufferView(buffer=0, byteOffset=off, byteLength=len(datos), target=target))
        return len(self.g.bufferViews) - 1

    def _accesor(self, arr, tipo, target):
        arr = np.ascontiguousarray(arr)
        v = self._vista(arr.tobytes(), target)
        comp = 5126 if arr.dtype == np.float32 else 5125
        acc = Accessor(bufferView=v, componentType=comp, count=len(arr), type=tipo)
        if tipo == 'VEC3' and comp == 5126:
            acc.min = arr.min(0).tolist()
            acc.max = arr.max(0).tolist()
        self.g.accessors.append(acc)
        return len(self.g.accessors) - 1

    def textura(self, img, calidad=86, sampler=0):
        b = io.BytesIO()
        if img.mode == 'RGBA':
            img.save(b, 'PNG', optimize=True)
            mime = 'image/png'
        else:
            img.convert('RGB').save(b, 'JPEG', quality=calidad, optimize=True)
            mime = 'image/jpeg'
        v = self._vista(b.getvalue())
        self.g.images.append(GImage(bufferView=v, mimeType=mime))
        self.g.textures.append(Texture(sampler=sampler, source=len(self.g.images) - 1))
        return len(self.g.textures) - 1

    def material(self, nombre, color=(1, 1, 1, 1), metal=0.0, rugosidad=0.8, tex=None, emisivo=None, tex_emisiva=None,
                 mezcla='OPAQUE', doble=True, sin_luz=False):
        m = Material(name=nombre, doubleSided=doble, alphaMode=mezcla,
                     pbrMetallicRoughness=PbrMetallicRoughness(baseColorFactor=list(color), metallicFactor=metal,
                                                               roughnessFactor=rugosidad))
        if tex is not None:
            m.pbrMetallicRoughness.baseColorTexture = TextureInfo(index=tex)
        if emisivo is not None:
            m.emissiveFactor = list(emisivo)
        if tex_emisiva is not None:
            m.emissiveTexture = TextureInfo(index=tex_emisiva)
        if sin_luz:
            m.extensions = {'KHR_materials_unlit': {}}
            if 'KHR_materials_unlit' not in self.g.extensionsUsed:
                self.g.extensionsUsed.append('KHR_materials_unlit')
        self.g.materials.append(m)
        return len(self.g.materials) - 1

    def malla(self, nombre, pos, nor, uv, idx, mat):
        at = {'POSITION': self._accesor(pos.astype(np.float32), 'VEC3', 34962),
              'NORMAL': self._accesor(nor.astype(np.float32), 'VEC3', 34962)}
        if uv is not None:
            at['TEXCOORD_0'] = self._accesor(uv.astype(np.float32), 'VEC2', 34962)
        prim = Primitive(attributes=at, indices=self._accesor(idx.astype(np.uint32).ravel(), 'SCALAR', 34963), material=mat)
        self.g.meshes.append(Mesh(name=nombre, primitives=[prim]))
        self.g.nodes.append(Node(name=nombre, mesh=len(self.g.meshes) - 1))
        self.nodos.append(len(self.g.nodes) - 1)

    def guardar(self, ruta):
        self.g.scenes = [Scene(nodes=self.nodos)]
        self.g.scene = 0
        self.g.buffers = [Buffer(byteLength=len(self.blob))]
        self.g.set_binary_blob(bytes(self.blob))
        self.g.save_binary(ruta)


def uv_caja(p, n, escala_m):
    """Proyección plana según la normal (para que la veta y el grano queden derechos)."""
    a = np.abs(n)
    if a[1] >= a[0] and a[1] >= a[2]:
        return np.stack([p[:, 0], p[:, 2]], 1) / escala_m
    if a[0] >= a[2]:
        return np.stack([p[:, 2], -p[:, 1]], 1) / escala_m
    return np.stack([p[:, 0], -p[:, 1]], 1) / escala_m


def plano_logo(c, centro, normal, ancho, mat_letras, mat_halo):
    """Logo oficial (PNG) en un plano vertical + halo cálido detrás. normal = ±X."""
    img = Image.open(LOGO)
    alto = ancho * img.height / img.width
    for nombre, mat, esc, sep in (('halo-logo', mat_halo, 1.22, 0.002), ('logo-platino', mat_letras, 1.0, 0.004)):
        w, h = ancho * esc, alto * (1 + (esc - 1) * 2.6)
        s = np.sign(normal[0])
        # el plano mira hacia +X o -X; u avanza hacia el frente del lado que se mira
        dz = np.array([0, 0, 1.0]) * -s
        base = centro + normal * sep
        esq = [base + dz * (-w / 2) + np.array([0, -h / 2, 0]), base + dz * (w / 2) + np.array([0, -h / 2, 0]),
               base + dz * (w / 2) + np.array([0, h / 2, 0]), base + dz * (-w / 2) + np.array([0, h / 2, 0])]
        pos = np.array(esq)
        nor = np.repeat(normal[None], 4, 0)
        uv = np.array([[0, 1], [1, 1], [1, 0], [0, 0]], float)
        idx = np.array([[0, 1, 2], [0, 2, 3]])
        c.malla(nombre, pos, nor, uv, idx, mat)


def main():
    skp, salida = sys.argv[1], sys.argv[2]
    m = Modelo(extraer(skp, tempfile.mkdtemp()))
    nombres = {k: v['nombre'] for k, v in m.mats.items()}
    c = Constructor()

    # ---- materiales
    # zona limpia de la muestra Capri (la foto trae el rótulo «CAPRI · textura mate» y una línea abajo a la derecha)
    t_capri = c.textura(Image.open(CAPRI).convert('RGB').crop((0, 0, 600, 480)).resize((512, 410)), sampler=1)
    t_duna = c.textura(Image.open(DUNA).convert('RGB'))
    caras_arte = [t for t in m.triangulos() if nombres.get(t[1]) == '_2']
    p_arte = a_gltf(np.concatenate([t[3] for t in caras_arte]) * CM)
    ancho_arte = np.ptp(p_arte[:, 0])
    alto_arte = np.ptp(p_arte[:, 1])
    arte = artes_a_la_talla.generar('viva-pro-2', ancho_arte / alto_arte, 900)
    t_arte = c.textura(Image.fromarray(arte), 88)
    logo = Image.open(LOGO).convert('RGBA')
    logo.thumbnail((1024, 1024))
    t_logo = c.textura(logo)
    # halo: alfa del logo dilatada y difuminada, color 3000K
    W, H = logo.size
    lienzo = Image.new('L', (int(W * 1.22), int(H * (1 + 0.22 * 2.6))), 0)
    lienzo.paste(logo.getchannel('A'), ((lienzo.width - W) // 2, (lienzo.height - H) // 2))
    alfa = lienzo.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(H * 0.16))
    alfa = alfa.point(lambda v: min(255, int(v * 1.6)))
    halo = Image.merge('RGBA', (Image.new('L', alfa.size, 255), Image.new('L', alfa.size, 180), Image.new('L', alfa.size, 107), alfa))
    t_halo = c.textura(halo)

    M = {
        'capri': c.material('Capri', tex=t_capri, rugosidad=0.85),
        'duna': c.material('Duna', tex=t_duna, rugosidad=0.6),
        'inox': c.material('Inox satinado', (0.86, 0.86, 0.87, 1), metal=1.0, rugosidad=0.25),
        'aluminio': c.material('Aluminio', (0.80, 0.79, 0.77, 1), metal=0.9, rugosidad=0.32),
        'arte': c.material('Tela backlight 5000K', tex=t_arte, emisivo=(0.9, 0.92, 1.0), tex_emisiva=t_arte, rugosidad=0.9),
        'sombra': c.material('Línea de sombra', (0.33, 0.30, 0.27, 1), rugosidad=0.9),
        'led': c.material('LED 3000K', (1, 0.76, 0.49, 1), emisivo=(1.0, 0.70, 0.42), sin_luz=True),
        'vidrio': c.material('Acrílico', (0.92, 0.94, 0.95, 0.28), rugosidad=0.05, mezcla='BLEND'),
        'logo': c.material('Logo platino', (0.92, 0.91, 0.88, 1), metal=0.75, rugosidad=0.3, tex=t_logo, mezcla='MASK'),
        'halo': c.material('Halo 3000K', (1, 1, 1, 1), tex=t_halo, mezcla='BLEND', sin_luz=True),
    }
    c.g.materials[M['logo']].alphaCutoff = 0.4
    colores = {}

    def mat_de(nombre_skp, ruta):
        grupo = ruta[1] if len(ruta) > 1 else ''
        if nombre_skp == '_2':
            return 'arte'
        if nombre_skp == '_':
            return 'duna'
        if nombre_skp == 'C02_Golden_Beige':
            return 'capri'
        if nombre_skp == 'Metal_06_1K':
            return 'aluminio' if grupo == 'Grupo#2' else 'inox'
        if nombre_skp == 'Glass_Basic_012':
            return 'vidrio'
        if grupo == 'Grupo#1':
            return 'sombra'
        return None

    # ---- geometría por material
    lotes = {}
    for ruta, mid, fid, pw, tri, nw, mb in m.triangulos():
        if 'Grupo#64' in ruta:  # logo modelado en el .skp: se reemplaza por el archivo oficial
            continue
        nombre_skp = nombres.get(mid)
        clave = mat_de(nombre_skp, ruta)
        if clave is None:  # productos y piezas sin material del proyecto: color del .skp
            info = m.mats.get(mid)
            rgb = info['color'] if info else (205, 205, 205)
            if any('Logo Plate' in r for r in ruta):
                rgb = (40, 40, 42)  # sin marcas de terceros en los audífonos de referencia
            alfa = info['alfa'] if info and info['alfa'] < 1 else 1.0
            clave = f'skp:{rgb}:{alfa:.2f}'
            if clave not in M:
                M[clave] = c.material(f'SKP {rgb}', tuple(v / 255 for v in rgb) + (alfa,), rugosidad=0.55,
                                      mezcla='BLEND' if alfa < 1 else 'OPAQUE')
        p = a_gltf(pw * CM)
        n = np.array([-nw[1], nw[2], -nw[0]])
        t = tri.copy()
        # orientar los triángulos con la normal de la cara
        v1, v2 = p[t[:, 1]] - p[t[:, 0]], p[t[:, 2]] - p[t[:, 0]]
        inv = np.cross(v1, v2) @ n < 0
        t[inv] = t[inv][:, ::-1]
        L = lotes.setdefault(clave, {'pos': [], 'nor': [], 'uv': [], 'idx': [], 'n': 0})
        if clave == 'arte':
            uv = np.stack([(p[:, 0] - p_arte[:, 0].min()) / ancho_arte, (p_arte[:, 1].max() - p[:, 1]) / alto_arte], 1)
        else:
            uv = uv_caja(p, n, 0.6 if clave == 'capri' else 0.35)
        L['pos'].append(p)
        L['nor'].append(np.repeat(n[None], len(p), 0))
        L['uv'].append(uv)
        L['idx'].append(t + L['n'])
        L['n'] += len(p)
    for clave, L in lotes.items():
        c.malla(clave.split(':')[0] if not clave.startswith('skp') else 'producto', np.concatenate(L['pos']), np.concatenate(L['nor']),
                np.concatenate(L['uv']), np.concatenate(L['idx']), M[clave])

    # ---- LED 3000K continuo en la línea de sombra (bajo el tope, a 2 mm del canto rehundido)
    y_led = 0.765
    for (x0, x1, z) in ((-0.37, 0.37, 0.221), (-0.37, 0.37, -0.221)):
        pos = np.array([[x0, y_led - 0.004, z], [x1, y_led - 0.004, z], [x1, y_led + 0.004, z], [x0, y_led + 0.004, z]])
        c.malla('led', pos, np.repeat([[0, 0, np.sign(z)]], 4, 0), None, np.array([[0, 1, 2], [0, 2, 3]]), M['led'])
    for (z0, z1, x) in ((-0.22, 0.22, 0.371), (-0.22, 0.22, -0.371)):
        pos = np.array([[x, y_led - 0.004, z0], [x, y_led - 0.004, z1], [x, y_led + 0.004, z1], [x, y_led + 0.004, z0]])
        c.malla('led', pos, np.repeat([[np.sign(x), 0, 0]], 4, 0), None, np.array([[0, 1, 2], [0, 2, 3]]), M['led'])

    # ---- logo oficial en ambos laterales: donde estaba el del .skp (36,5 cm de ancho, centro a 40 cm de alto)
    for lado in (1, -1):
        plano_logo(c, np.array([0.40 * lado, 0.40, 0.25 - 0.2595]), np.array([lado, 0, 0.0]), 0.365, M['logo'], M['halo'])

    c.guardar(salida)
    print(f'{salida}: {os.path.getsize(salida) / 1e6:.2f} MB · arte {ancho_arte * 100:.1f} × {alto_arte * 100:.1f} cm')


if __name__ == '__main__':
    main()

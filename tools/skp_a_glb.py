"""Convierte los muebles de SketchUp (.skp) de FARUK AGENCIA a GLB para la web, con la geometría exacta del archivo.

- Ejes: SketchUp (x fondo, y ancho, z arriba, pulgadas) -> glTF (X derecha, Y arriba, Z hacia el cliente, metros).
- Materiales del proyecto: Capri (cuerpo), Duna (tope y elevador), inox (zócalo), aluminio (marco),
  caja de luz con el arte a la talla (tools/artes_a_la_talla.py) y LED 3000K en la línea de sombra.
- El logo que venía modelado en el .skp se reemplaza por el archivo oficial en platino, con halo cálido 3000K.
- Los relojes que en el archivo quedaron flotando delante de la mesa ya vienen corregidos en el .skp leído
  (la matriz de cada grupo se lee por filas).

Uso: python tools/skp_a_glb.py archivo.skp salida.glb [mesa|mueble|mueble2]
     mesa    -> mesa de experiencia (primer mueble mesa cubitt.skp)
     mueble  -> mueble de exhibición de 120 cm (segundo mueble mesa cubitt.skp)
     mueble2 -> dos muebles iguales lado a lado (240 cm): mallas compartidas, logo solo en los laterales exteriores
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


# Cada pieza: qué instancias del .skp toma (centro en y, cm), su centro en planta, material del arte, arte a la talla,
# grupos que son marco de aluminio o línea de sombra, logos (lado, centro y ancho en m) y la línea de LED.
PIEZAS = {
    'mesa': {'filtro': lambda yc: yc > -100, 'origen': (25.0, -40.0), 'arte_mat': '_2', 'arte': 'viva-pro-2',
             'aluminio': ('Grupo#2',), 'sombra': ('Grupo#1',),
             'logos': [(1, (0.40, 0.40, -0.0095)), (-1, (-0.40, 0.40, -0.0095))], 'ancho_logo': 0.365,
             'led': (-0.37, 0.37, -0.22, 0.22, 0.765)},
    'mueble': {'filtro': lambda yc: yc < -150, 'origen': (30.05, -250.1), 'arte_mat': '_4', 'arte': 'nueva-era',
               'aluminio': ('Grupo#9', 'Grupo#11'), 'sombra': ('Grupo#1',),
               'logos': [(1, (0.60, 0.406, 0.012)), (-1, (-0.60, 0.406, 0.012))], 'ancho_logo': 0.31,
               'led': (-0.567, 0.55, -0.1695, 0.1695, 0.765)},
}
ORIGEN = PIEZAS['mesa']['origen']


def a_gltf(p_cm):
    """(x fondo, y ancho, z alto) en cm -> metros glTF (X derecha, Y arriba, Z hacia el cliente) centrados en ORIGEN."""
    x, y, z = p_cm[:, 0], p_cm[:, 1], p_cm[:, 2]
    return np.stack([-(y - ORIGEN[1]), z, ORIGEN[0] - x], 1) / 100.0


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

    def malla(self, nombre, pos, nor, uv, idx, mat, nodos=((0, 0, 0),)):
        """Crea la malla y un nodo por cada traslación de `nodos` (los módulos repetidos comparten la geometría)."""
        at = {'POSITION': self._accesor(pos.astype(np.float32), 'VEC3', 34962),
              'NORMAL': self._accesor(nor.astype(np.float32), 'VEC3', 34962)}
        if uv is not None:
            at['TEXCOORD_0'] = self._accesor(uv.astype(np.float32), 'VEC2', 34962)
        prim = Primitive(attributes=at, indices=self._accesor(idx.astype(np.uint32).ravel(), 'SCALAR', 34963), material=mat)
        self.g.meshes.append(Mesh(name=nombre, primitives=[prim]))
        mi = len(self.g.meshes) - 1
        for t in nodos:
            self.nodo(mi, t)
        return mi

    def otra_malla(self, mi, mat, nombre, nodos):
        """Misma geometría que la malla mi con otro material (p. ej. otro arte en la caja de luz del segundo módulo)."""
        prim = self.g.meshes[mi].primitives[0]
        self.g.meshes.append(Mesh(name=nombre, primitives=[Primitive(attributes=prim.attributes, indices=prim.indices, material=mat)]))
        for t in nodos:
            self.nodo(len(self.g.meshes) - 1, t)

    def nodo(self, mi, traslacion):
        n = Node(name=self.g.meshes[mi].name, mesh=mi)
        if any(traslacion):
            n.translation = [float(v) for v in traslacion]
        self.g.nodes.append(n)
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


def plano_logo(c, centro, normal, ancho, mat_letras, mat_halo, nodos=((0, 0, 0),)):
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
        c.malla(nombre, pos, nor, uv, idx, mat, nodos)


def main():
    global ORIGEN
    skp, salida = sys.argv[1], sys.argv[2]
    modo = sys.argv[3] if len(sys.argv) > 3 else 'mesa'
    pieza = PIEZAS['mueble' if modo == 'mueble2' else modo]
    ORIGEN = pieza['origen']
    # composición: dos módulos de 1,20 m lado a lado (el de la izquierda en -0,60 m, el de la derecha en +0,60 m)
    modulos = ((-0.60, 0, 0), (0.60, 0, 0)) if modo == 'mueble2' else ((0, 0, 0),)
    m = Modelo(extraer(skp, tempfile.mkdtemp()))
    nombres = {k: v['nombre'] for k, v in m.mats.items()}
    from skp_lector import matriz
    caras = []
    for inst in m.raiz[4]:
        d = m.defs.get(inst['ref'])
        tr = m.triangulos(d, matriz(inst['t']), inst['mat']) if d else []
        if tr and pieza['filtro'](np.concatenate([t[3] for t in tr])[:, 1].mean() * CM):
            caras += [(('MODELO',) + t[0],) + t[1:] for t in tr]
    c = Constructor()

    # ---- materiales
    # zona limpia de la muestra Capri (la foto trae el rótulo «CAPRI · textura mate» y una línea abajo a la derecha)
    t_capri = c.textura(Image.open(CAPRI).convert('RGB').crop((0, 0, 600, 480)).resize((512, 410)), sampler=1)
    t_duna = c.textura(Image.open(DUNA).convert('RGB'))
    es_arte = lambda t: nombres.get(t[1]) == pieza['arte_mat'] or nombres.get(t[6]) == pieza['arte_mat']
    p_arte = a_gltf(np.concatenate([t[3] for t in caras if es_arte(t)]) * CM)
    ancho_arte = np.ptp(p_arte[:, 0])
    alto_arte = np.ptp(p_arte[:, 1])
    artes = [pieza['arte']] if modo != 'mueble2' else ['nueva-era', 'viva-pro-2']
    t_artes = [c.textura(Image.fromarray(artes_a_la_talla.generar(a, ancho_arte / alto_arte, 900)), 88) for a in artes]
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
        'arte': c.material('Tela backlight 5000K', tex=t_artes[0], emisivo=(0.62, 0.64, 0.7), tex_emisiva=t_artes[0], rugosidad=0.9),
        'sombra': c.material('Línea de sombra', (0.33, 0.30, 0.27, 1), rugosidad=0.9),
        'led': c.material('LED 3000K', (1, 0.76, 0.49, 1), emisivo=(1.0, 0.70, 0.42), sin_luz=True),
        'vidrio': c.material('Acrílico', (0.92, 0.94, 0.95, 0.28), rugosidad=0.05, mezcla='BLEND'),
        'logo': c.material('Logo platino', (0.92, 0.91, 0.88, 1), metal=0.75, rugosidad=0.3, tex=t_logo, mezcla='MASK'),
        'halo': c.material('Halo 3000K', (1, 1, 1, 1), tex=t_halo, mezcla='BLEND', sin_luz=True),
    }
    arte_2 = None
    if len(t_artes) > 1:
        arte_2 = c.material('Tela backlight 5000K · módulo 2', tex=t_artes[1], emisivo=(0.62, 0.64, 0.7), tex_emisiva=t_artes[1], rugosidad=0.9)
    c.g.materials[M['logo']].alphaCutoff = 0.4

    def mat_de(nombre_skp, ruta):
        grupo = ruta[1] if len(ruta) > 1 else ''
        if nombre_skp == '_':
            return 'duna'
        if nombre_skp == 'C02_Golden_Beige':
            return 'capri'
        if grupo in pieza['aluminio']:
            return 'aluminio'
        if nombre_skp == 'Metal_06_1K':
            return 'inox'
        if nombre_skp == 'Glass_Basic_012':
            return 'vidrio'
        if grupo in pieza['sombra']:
            return 'sombra'
        return None

    # ---- geometría por material
    lotes = {}
    for ruta, mid, fid, pw, tri, nw, mb in caras:
        if 'Grupo#64' in ruta:  # logo modelado en el .skp: se reemplaza por el archivo oficial
            continue
        n = np.array([-nw[1], nw[2], -nw[0]])
        if nombres.get(mid) == pieza['arte_mat']:
            clave = 'arte'
        elif nombres.get(mb) == pieza['arte_mat']:
            clave, n = 'arte', -n  # el arte está en la cara posterior (mira al cliente)
        else:
            clave = mat_de(nombres.get(mid), ruta)
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
        nodos = modulos[:1] if (clave == 'arte' and arte_2 is not None) else modulos
        mi = c.malla(clave.split(':')[0] if not clave.startswith('skp') else 'producto', np.concatenate(L['pos']),
                     np.concatenate(L['nor']), np.concatenate(L['uv']), np.concatenate(L['idx']), M[clave], nodos)
        if clave == 'arte' and arte_2 is not None:
            c.otra_malla(mi, arte_2, 'arte-modulo-2', modulos[1:])

    # ---- LED 3000K continuo en la línea de sombra (bajo el tope, a 1 mm del canto rehundido)
    x0, x1, z0, z1, y_led = pieza['led']
    for z in (z0 - 0.001, z1 + 0.001):
        pos = np.array([[x0, y_led - 0.004, z], [x1, y_led - 0.004, z], [x1, y_led + 0.004, z], [x0, y_led + 0.004, z]])
        c.malla('led', pos, np.repeat([[0, 0, np.sign(z)]], 4, 0), None, np.array([[0, 1, 2], [0, 2, 3]]), M['led'], modulos)
    for x in (x0 - 0.001, x1 + 0.001):
        pos = np.array([[x, y_led - 0.004, z0], [x, y_led - 0.004, z1], [x, y_led + 0.004, z1], [x, y_led + 0.004, z0]])
        c.malla('led', pos, np.repeat([[np.sign(x), 0, 0]], 4, 0), None, np.array([[0, 1, 2], [0, 2, 3]]), M['led'], modulos)

    # ---- logo oficial en los laterales (donde estaba el del .skp); en composición solo en los laterales exteriores
    for lado, centro in pieza['logos']:
        nodos = modulos if len(modulos) == 1 else [t for t in modulos if np.sign(t[0]) == lado]
        plano_logo(c, np.array(centro), np.array([lado, 0, 0.0]), pieza['ancho_logo'], M['logo'], M['halo'], nodos)

    c.guardar(salida)
    print(f'{salida}: {os.path.getsize(salida) / 1e6:.2f} MB · arte {ancho_arte * 100:.1f} × {alto_arte * 100:.1f} cm')


if __name__ == '__main__':
    main()

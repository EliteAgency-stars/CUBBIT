"""Convierte los muebles de SketchUp (.skp) de FARUK AGENCIA a GLB para la web, con la geometría exacta del archivo.

- Ejes: SketchUp (x fondo, y ancho, z arriba, pulgadas) -> glTF (X derecha, Y arriba, Z hacia el cliente, metros).
- Materiales del proyecto: Capri (cuerpo), Duna (tope y elevador), inox (zócalo), aluminio (marco de la caja de luz y
  postes), caja de luz con el arte a la talla (tools/artes_a_la_talla.py) y LED 3000K en la línea de sombra. La lámina
  blanca que algún archivo trae (espalda de la caja de luz del display) pasa a Capri, como en el resto de la línea.
- Los logos modelados en el .skp se reemplazan por los archivos oficiales en platino, con halo cálido 3000K:
  el logo completo (assets/logo/logo-cubitt-platino.png) y el isotipo recortado de ese mismo archivo
  (assets/logo/isotipo-cubitt-platino.png, tools/preparar_isotipo.py).

Uso: python tools/skp_a_glb.py archivo.skp salida.glb [mesa|mueble|mueble2|sobremesa|muro] [--sin-productos] [--productos lista.json]
     mesa      -> mesa de experiencia de 100 cm (artes-cubitt/originales/mesa cubitt.skp)
     mueble    -> mueble de exhibición de 120 cm (artes-cubitt/originales/mueble cubitt.skp)
     mueble2   -> dos muebles iguales lado a lado (240 cm): mallas compartidas, logo al frente de cada módulo e
                  isotipo solo en los laterales exteriores
     sobremesa -> display de sobremesa de 50 cm (artes-cubitt/originales/sobre mesa cubitt.skp)
     muro      -> bonus: muro de exhibición de 220 cm (artes-cubitt/originales/cuarto mueble mesa cubitt.skp), con melamina
                  Nácar (textura del .skp, assets/materiales/nacar.jpg) en el lateral izquierdo y el interior del mesón
     --sin-productos  deja fuera los relojes y el audio de referencia del .skp (los renders ponen los productos reales)
     --productos      guarda en JSON cada producto del .skp (grupo, centro y tamaño en m) para ubicar los reales
Después se comprime con meshopt: npx gltfpack -i salida.glb -o salida.glb -cc
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
from skp_lector import Modelo, extraer, matriz  # noqa: E402

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'propuesta-2027')
CM = 0.0254 * 100  # pulgadas -> cm
LOGO = os.path.join(RAIZ, 'assets', 'logo', 'logo-cubitt-platino.png')
ISOTIPO = os.path.join(RAIZ, 'assets', 'logo', 'isotipo-cubitt-platino.png')
CAPRI = os.path.join(RAIZ, 'assets', 'materiales', 'capri.jpg')
DUNA = os.path.join(RAIZ, 'assets', 'materiales', 'duna.jpg')
NACAR = os.path.join(RAIZ, 'assets', 'materiales', 'nacar.jpg')


# Cada pieza: centro de su planta en el .skp (x, y en cm), material y arte de la caja de luz, grupos del .skp que son
# marco de aluminio o línea de sombra, grupos con el logo modelado (se reemplaza), logos oficiales
# (archivo, normal, centro en m, ancho en m) y la línea de LED (x0, x1, z0, z1, alto en m).
PIEZAS = {
    # 100 × 50 cm: caja de luz frontal (tela 82,4 × 56,1 cm) y logo en los dos laterales (36,5 cm a 40 cm de alto)
    'mesa': {'origen': (76.84, 83.17), 'arte_mat': '_2', 'arte': 'viva-pro-2',
             'aluminio': ('Grupo#8',), 'sombra': ('Grupo#1',), 'logo_skp': ('Grupo#12',),
             'logos': [('logo', (1, 0, 0), (0.50, 0.40, -0.0096), 0.365),
                       ('logo', (-1, 0, 0), (-0.50, 0.40, -0.0096), 0.365)],
             'led': (-0.4625, 0.4625, -0.22, 0.22, 0.765)},
    # 120 × 40 cm: caja de luz trasera sobre cinco postes, logo al frente (44,9 cm a 43,9 cm de alto; en el .skp quedó
    # 2 cm corrido a la izquierda y se centra) e isotipo de 13,6 cm en los laterales
    'mueble': {'origen': (44.5, -61.65), 'arte_mat': '_1', 'arte': 'nueva-era',
               'aluminio': ('Grupo#9', 'Grupo#11'), 'sombra': ('Grupo#1',), 'logo_skp': ('Grupo#12', 'Grupo#16'),
               'logos': [('logo', (0, 0, 1), (0.0, 0.4388, 0.1995), 0.449),
                         ('isotipo', (1, 0, 0), (0.60, 0.4336, 0.0083), 0.136),
                         ('isotipo', (-1, 0, 0), (-0.60, 0.4336, 0.0083), 0.136)],
               'led': (-0.57, 0.575, -0.1695, 0.1693, 0.765)},
    # 50 × 25 cm: caja de luz de 50 × 25 cm (tela 48,5 × 23,5 cm), logo de 9,4 cm al frente de la base Capri e isotipo
    # de 9 cm en la espalda de la caja de luz
    'sobremesa': {'origen': (46.85, 47.66), 'arte_mat': '_1', 'arte': 'nueva-era',
                  'aluminio': ('Grupo#17',), 'sombra': ('Grupo#13',), 'logo_skp': ('Grupo#12', 'Group7#2'),
                  'logos': [('logo', (0, 0, 1), (0.0, 0.0199, 0.125), 0.0944),
                            ('isotipo', (0, 0, -1), (0.0, 0.193, -0.1106), 0.0902)],
                  'led': (-0.24, 0.24, -0.115, 0.115, 0.0475)},
    # Bonus · 220 × 248 × 49 cm: mesón con cuatro puertas y tope Duna, repisa flotante (base Capri, línea de sombra con LED
    # y tope Duna) a 1,26 m con el audio, caja de luz de 208,8 × 60 cm (tela 206,7 × 56,8 cm), cabecera de 30 cm con LED
    # hacia abajo y el logo de 64,5 cm (en el .skp quedó 6 cm corrido a la derecha y se centra)
    'muro': {'origen': (25.26, 110.0), 'arte_mat': '_4', 'arte': 'nueva-era',
             'aluminio': ('Grupo#36',), 'sombra': ('Grupo#19',), 'logo_skp': ('Grupo#12',),
             'estructura': ('Grupo#19', 'Grupo#83', 'Grupo#85', 'Grupo#60', 'Grupo#49'),
             'logos': [('logo', (0, 0, 1), (0.0, 2.3645, 0.2382), 0.645)],
             'led': [(-0.7867, 0.8287, -0.1499, 0.0801, 1.2364)]},
}
ORIGEN = PIEZAS['mesa']['origen']
BLANCO_A_CAPRI = ('Lisanne_Caulk',)  # lámina blanca del .skp -> Capri
NACAR_SKP = 'color madera mueble ceramic'  # melamina Nácar del .skp del muro (textura Nacar.jpg)


def tipo_producto(m, d):
    """Qué producto de referencia es un grupo del .skp, por los componentes que trae adentro."""
    nombres, pila = set(), [d]
    while pila:
        for inst in pila.pop()[4]:
            sub = m.defs.get(inst['ref'])
            if sub and sub[0] not in nombres:
                nombres.add(sub[0])
                pila.append(sub)
    texto = ' '.join(nombres)
    for clave, tipo in (('Beats', 'audifonos'), ('Designed by Appl', 'buds'), ('POLK', 'parlante-grande'),
                        ('Grupo#82', 'parlante-alto'), ('Grupo#88', 'parlante-pequeno'), ('Grupo#23', 'reloj')):
        if clave in texto:
            return tipo
    return 'otro'


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


def uv_caja(p, n, escala_m, veta=False):
    """Proyección plana según la normal (para que la veta y el grano queden derechos). Con veta=True (Duna) la veta de
    la textura, que corre en vertical en la imagen, va a lo largo del tope y de sus cantos (eje X)."""
    a = np.abs(n)
    if a[1] >= a[0] and a[1] >= a[2]:
        return (np.stack([p[:, 2], p[:, 0]], 1) if veta else np.stack([p[:, 0], p[:, 2]], 1)) / escala_m
    if a[0] >= a[2]:
        return (np.stack([p[:, 1], p[:, 2]], 1) if veta else np.stack([p[:, 2], -p[:, 1]], 1)) / escala_m
    return (np.stack([p[:, 1], p[:, 0]], 1) if veta else np.stack([p[:, 0], -p[:, 1]], 1)) / escala_m


HALO = (1.22, 2.6)  # el halo es 22 % más ancho que el logo y crece 2,6 veces eso en alto


def textura_halo(img):
    """Alfa del logo dilatada y difuminada, en color 3000K."""
    W, H = img.size
    lienzo = Image.new('L', (int(W * HALO[0]), int(H * (1 + (HALO[0] - 1) * HALO[1]))), 0)
    lienzo.paste(img.getchannel('A'), ((lienzo.width - W) // 2, (lienzo.height - H) // 2))
    alfa = lienzo.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(min(W, H) * 0.16))
    alfa = alfa.point(lambda v: min(255, int(v * 1.6)))
    return Image.merge('RGBA', (Image.new('L', alfa.size, 255), Image.new('L', alfa.size, 180), Image.new('L', alfa.size, 107), alfa))


def plano_logo(c, archivo, centro, normal, ancho, mat_letras, mat_halo, nodos=((0, 0, 0),)):
    """Logo oficial (PNG) en un plano vertical que mira hacia `normal` + halo cálido detrás."""
    img = Image.open(archivo)
    alto = ancho * img.height / img.width
    normal = np.asarray(normal, float)
    derecha = np.cross([0, 1.0, 0], normal)  # derecha de quien mira el logo de frente
    arriba = np.array([0, 1.0, 0])
    for nombre, mat, esc, sep in (('halo-logo', mat_halo, HALO[0], 0.002), ('logo-platino', mat_letras, 1.0, 0.004)):
        w, h = ancho * esc, alto * (1 + (esc - 1) * HALO[1])
        base = np.asarray(centro, float) + normal * sep
        pos = np.array([base - derecha * w / 2 - arriba * h / 2, base + derecha * w / 2 - arriba * h / 2,
                        base + derecha * w / 2 + arriba * h / 2, base - derecha * w / 2 + arriba * h / 2])
        nor = np.repeat(normal[None], 4, 0)
        uv = np.array([[0, 1], [1, 1], [1, 0], [0, 0]], float)
        c.malla(nombre, pos, nor, uv, np.array([[0, 1, 2], [0, 2, 3]]), mat, nodos)


def main():
    global ORIGEN
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    skp, salida = args[0], args[1]
    modo = args[2] if len(args) > 2 and args[2] in ('mesa', 'mueble', 'mueble2', 'sobremesa', 'muro') else 'mesa'
    sin_productos = '--sin-productos' in sys.argv
    json_productos = sys.argv[sys.argv.index('--productos') + 1] if '--productos' in sys.argv else None
    pieza = PIEZAS['mueble' if modo == 'mueble2' else modo]
    ORIGEN = pieza['origen']
    # composición: dos módulos de 1,20 m lado a lado (el de la izquierda en -0,60 m, el de la derecha en +0,60 m)
    modulos = ((-0.60, 0, 0), (0.60, 0, 0)) if modo == 'mueble2' else ((0, 0, 0),)
    m = Modelo(extraer(skp, tempfile.mkdtemp()))
    nombres = {k: v['nombre'] for k, v in m.mats.items()}
    caras, productos = [], []
    for inst in m.raiz[4]:
        d = m.defs.get(inst['ref'])
        if not d:
            continue
        tri = [(('MODELO',) + t[0],) + t[1:] for t in m.triangulos(d, matriz(inst['t']), inst['mat'])]
        # producto de referencia: grupo con componentes adentro que no es caja de luz ni logo (relojes, audífonos, bafles)
        if d[4] and d[0] not in pieza['aluminio'] + pieza['logo_skp'] + pieza.get('estructura', ()) and tri:
            p = a_gltf(np.concatenate([t[3] for t in tri]) * CM)
            productos.append({'grupo': d[0], 'tipo': tipo_producto(m, d), 'centro': ((p.min(0) + p.max(0)) / 2).round(4).tolist(),
                              'tamano': np.ptp(p, 0).round(4).tolist(), 'base': round(float(p[:, 1].min()), 4)})
            if sin_productos:
                continue
        caras += tri
    if json_productos:
        import json
        with open(json_productos, 'w', encoding='utf-8') as fj:
            json.dump(sorted(productos, key=lambda q: (q['centro'][2], q['centro'][0])), fj, ensure_ascii=False, indent=1)
    c = Constructor()

    # ---- materiales
    # zona limpia de la muestra Capri (la foto trae el rótulo «CAPRI · textura mate» y una línea abajo a la derecha)
    t_capri = c.textura(Image.open(CAPRI).convert('RGB').crop((0, 0, 600, 480)).resize((512, 410)), sampler=1)
    t_duna = c.textura(Image.open(DUNA).convert('RGB'), sampler=1)
    t_nacar = c.textura(Image.open(NACAR).convert('RGB'), sampler=1) if NACAR_SKP in nombres.values() else None
    es_arte = lambda t: (nombres.get(t[1]) == pieza['arte_mat'] or nombres.get(t[6]) == pieza['arte_mat']) and not any(r in pieza['logo_skp'] for r in t[0][1:])
    p_arte = a_gltf(np.concatenate([t[3] for t in caras if es_arte(t)]) * CM)
    ancho_arte = np.ptp(p_arte[:, 0])
    alto_arte = np.ptp(p_arte[:, 1])
    artes = [pieza['arte']] if modo != 'mueble2' else ['nueva-era', 'viva-pro-2']
    t_artes = [c.textura(Image.fromarray(artes_a_la_talla.generar(a, ancho_arte / alto_arte, 900)), 88) for a in artes]
    t_logo, t_halo = {}, {}
    for clave, archivo in (('logo', LOGO), ('isotipo', ISOTIPO)):
        img = Image.open(archivo).convert('RGBA')
        img.thumbnail((1024, 1024))
        t_logo[clave] = c.textura(img)
        t_halo[clave] = c.textura(textura_halo(img))

    M = {
        'capri': c.material('Capri', tex=t_capri, rugosidad=0.85),
        'duna': c.material('Duna', tex=t_duna, rugosidad=0.6),
        'inox': c.material('Inox satinado', (0.86, 0.86, 0.87, 1), metal=1.0, rugosidad=0.25),
        'aluminio': c.material('Aluminio', (0.80, 0.79, 0.77, 1), metal=0.9, rugosidad=0.32),
        'arte': c.material('Tela backlight 5000K', tex=t_artes[0], emisivo=(0.62, 0.64, 0.7), tex_emisiva=t_artes[0], rugosidad=0.9),
        'sombra': c.material('Línea de sombra', (0.33, 0.30, 0.27, 1), rugosidad=0.9),
        'led': c.material('LED 3000K', (1, 0.76, 0.49, 1), emisivo=(1.0, 0.70, 0.42), sin_luz=True),
        'vidrio': c.material('Acrílico', (0.92, 0.94, 0.95, 0.28), rugosidad=0.05, mezcla='BLEND'),
    }
    if t_nacar is not None:
        M['nacar'] = c.material('Nácar', tex=t_nacar, rugosidad=0.6)
    for clave in t_logo:
        M[f'logo:{clave}'] = c.material(f'Platino · {clave}', (0.92, 0.91, 0.88, 1), metal=0.75, rugosidad=0.3,
                                        tex=t_logo[clave], mezcla='MASK')
        c.g.materials[M[f'logo:{clave}']].alphaCutoff = 0.4
        M[f'halo:{clave}'] = c.material(f'Halo 3000K · {clave}', (1, 1, 1, 1), tex=t_halo[clave], mezcla='BLEND', sin_luz=True)
    arte_2 = None
    if len(t_artes) > 1:
        arte_2 = c.material('Tela backlight 5000K · módulo 2', tex=t_artes[1], emisivo=(0.62, 0.64, 0.7), tex_emisiva=t_artes[1], rugosidad=0.9)

    def mat_de(nombre_skp, ruta):
        grupo = ruta[1] if len(ruta) > 1 else ''
        if nombre_skp == '_':
            return 'duna'
        if nombre_skp == 'C02_Golden_Beige' or nombre_skp in BLANCO_A_CAPRI:
            return 'capri'
        if nombre_skp == NACAR_SKP:
            return 'nacar'
        if nombre_skp == 'B01_Ivory_Dust':  # cinta bajo la cabecera del muro
            return 'led'
        if nombre_skp == 'M01_Silver_Fog':  # perfil de la cabecera del muro
            return 'aluminio'
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
        if any(r in pieza['logo_skp'] for r in ruta[1:]):  # logo modelado en el .skp: se reemplaza por el archivo oficial
            continue
        n = np.array([-nw[1], nw[2], -nw[0]])
        if nombres.get(mid) == pieza['arte_mat']:
            clave = 'arte'
        elif nombres.get(mb) == pieza['arte_mat']:
            clave, n = 'arte', -n  # el arte está en la cara posterior (mira al cliente)
        elif mid is None and nombres.get(mb) in BLANCO_A_CAPRI:
            clave, n = 'capri', -n  # la lámina blanca está en la cara posterior (espalda de la caja de luz)
        else:
            clave = mat_de(nombres.get(mid), ruta)
        if clave == 'arte':
            # la tela mira al cliente; el .skp la repite en la espalda de la caja de luz, que atrás va cerrada en Capri
            atras = a_gltf(pw * CM)[:, 2].mean() < p_arte[:, 2].max() - 0.003
            clave, n = ('capri', np.array([0, 0, -1.0])) if atras else ('arte', np.array([0, 0, 1.0]))
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
            uv = uv_caja(p, n, {'capri': 0.6, 'duna': 0.7, 'nacar': 0.8}.get(clave, 0.35), veta=clave == 'duna')
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
    for x0, x1, z0, z1, y_led in (pieza['led'] if isinstance(pieza['led'], list) else [pieza['led']]):
        h = min(0.004, y_led * 0.08)
        for z in (z0 - 0.001, z1 + 0.001):
            pos = np.array([[x0, y_led - h, z], [x1, y_led - h, z], [x1, y_led + h, z], [x0, y_led + h, z]])
            c.malla('led', pos, np.repeat([[0, 0, np.sign(z - (z0 + z1) / 2)]], 4, 0), None, np.array([[0, 1, 2], [0, 2, 3]]), M['led'], modulos)
        for x in (x0 - 0.001, x1 + 0.001):
            pos = np.array([[x, y_led - h, z0], [x, y_led - h, z1], [x, y_led + h, z1], [x, y_led + h, z0]])
            c.malla('led', pos, np.repeat([[np.sign(x - (x0 + x1) / 2), 0, 0]], 4, 0), None, np.array([[0, 1, 2], [0, 2, 3]]), M['led'], modulos)

    # ---- logos oficiales donde estaban los del .skp; en composición, los de los laterales solo en los exteriores
    for clave, normal, centro, ancho in pieza['logos']:
        lateral = abs(normal[0]) > 0.5
        nodos = modulos if (len(modulos) == 1 or not lateral) else [t for t in modulos if np.sign(t[0]) == np.sign(normal[0])]
        plano_logo(c, LOGO if clave == 'logo' else ISOTIPO, centro, normal, ancho, M[f'logo:{clave}'], M[f'halo:{clave}'], nodos)

    c.guardar(salida)
    print(f'{salida}: {os.path.getsize(salida) / 1e6:.2f} MB · arte {ancho_arte * 100:.1f} × {alto_arte * 100:.1f} cm')


if __name__ == '__main__':
    main()

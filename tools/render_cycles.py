"""Renders fotorrealistas (Blender Cycles) de la línea Cubitt 2027, hechos con los SketchUp de FARUK AGENCIA.

La geometría sale tal cual de los .skp (tools/skp_a_glb.py) y los materiales son los del proyecto, sin cambiarlos:
melamina Capri y Duna con las texturas de Madecentro/Pelíkano, zócalo inox, cajas de luz de aluminio con la tela
backlight y el arte a la talla (5000K), línea de sombra con LED 3000K y el logo y el isotipo oficiales en platino con
halo 3000K. Los relojes y el audio de referencia del .skp se cambian por los productos reales de Cubitt (recortes de
artes-cubitt/productos/) en las mismas posiciones del archivo.

Uso: python tools/render_cycles.py <toma[,toma...]|todas> [--muestras 160] [--ancho 1920] [--salida propuesta-2027/renders]
Tomas: familia, mesa, touch, vendedor, mueble, modular, sobremesa, logo, material, despiece, muro, muro-detalle
Salida: <toma>.jpg (1920 × 1200) y <toma>-900.jpg (miniatura) en la carpeta de salida.
Requiere bpy (pip install bpy), numpy y Pillow, más lo que pide tools/skp_a_glb.py.
"""
import json
import math
import os
import subprocess
import sys
import tempfile

import bpy
import numpy as np
from mathutils import Vector
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import artes_a_la_talla  # noqa: E402

RAIZ = os.path.normpath(os.path.join(HERE, '..', 'propuesta-2027'))
ORIG = os.path.join(RAIZ, 'artes-cubitt', 'originales')
PROD = os.path.join(RAIZ, 'artes-cubitt', 'productos')
MAT = os.path.join(RAIZ, 'assets', 'materiales')
LOGO = os.path.join(RAIZ, 'assets', 'logo', 'logo-cubitt-platino.png')
ISOTIPO = os.path.join(RAIZ, 'assets', 'logo', 'isotipo-cubitt-platino.png')
CACHE = os.path.join(tempfile.gettempdir(), 'cubitt-render')

PIEZAS = {  # modelo de skp_a_glb.py -> archivo SketchUp
    'mesa': 'mesa cubitt.skp', 'mueble': 'mueble cubitt.skp', 'mueble2': 'mueble cubitt.skp',
    'sobremesa': 'sobre mesa cubitt.skp', 'muro': 'cuarto mueble mesa cubitt.skp',
}
K3000, K4000, K5000 = (1.0, 0.71, 0.42), (1.0, 0.83, 0.66), (1.0, 0.90, 0.82)

# Relojes de izquierda a derecha (vistos desde el cliente) y audio por grupo del .skp
RELOJES = {
    'mesa': ['viva-pro-2', 'viva-2-rosado', 'viva-lite-lilac', 'aura-2-azul', 'aura-pro-2', 'terra-verde', 'viva-pro-2', 'aura-pro-2', 'terra-verde'],
    'mueble': ['viva-pro-2', 'viva-2-rosado', 'viva-lite-lilac', 'aura-2-azul', 'aura-pro-2', 'terra-verde', 'viva-pro-2', 'aura-pro-2'],
    'mueble2': ['viva-pro-2', 'viva-2-rosado', 'viva-lite-lilac', 'aura-2-azul', 'aura-pro-2', 'terra-verde', 'viva-pro-2', 'aura-pro-2',
                'terra-verde', 'aura-pro-2', 'aura-2-azul', 'viva-lite-lilac', 'viva-2-rosado', 'viva-pro-2', 'terra-verde', 'viva-pro-2'],
    'sobremesa': ['viva-2-rosado', 'viva-pro-2', 'aura-2-azul', 'terra-verde', 'aura-pro-2'],
    'muro': ['viva-pro-2', 'viva-2-rosado', 'viva-lite-lilac', 'aura-2-azul', 'aura-pro-2', 'terra-verde', 'viva-pro-2', 'aura-pro-2',
             'terra-verde', 'viva-2-rosado'],
}
# Audio por tipo de producto de referencia del .skp (tools/skp_a_glb.py lo detecta por sus componentes)
AUDIO = {'audifonos': ('power-anc-negro', 0.20), 'buds': ('power-buds-2', 0.072), 'parlante-grande': ('power-pro-2', 0.13),
         'parlante-alto': ('power-plus-2', 0.20), 'parlante-pequeno': (('power-go-2', 0.09), ('power-mini', 0.087))}
# Ajustes por pieza. El muro trae sus propios soportes acrílicos de audífonos y, en el .skp, los productos del mesón quedaron
# 1,8 cm por encima del tope Duna (79,4 cm): en el render se apoyan sobre el tope y cada reloj lleva su ficha acrílica.
OPCIONES = {'muro': {'soporte_audifonos': False, 'bajar': 0.018, 'fichas': True}}


def gl(x, y, z):
    """glTF (X derecha, Y arriba, Z hacia el cliente) -> Blender (X derecha, Y al fondo, Z arriba)."""
    return Vector((x, -z, y))


# ------------------------------------------------------------------ modelos

def preparar_modelos():
    """GLB sin los productos de referencia + JSON con su ubicación, una vez por sesión (caché en el temporal)."""
    os.makedirs(CACHE, exist_ok=True)
    for modo, skp in PIEZAS.items():
        glb = os.path.join(CACHE, f'{modo}.glb')
        if os.path.exists(glb) and os.path.getmtime(glb) > os.path.getmtime(os.path.join(HERE, 'skp_a_glb.py')):
            continue
        subprocess.run([sys.executable, os.path.join(HERE, 'skp_a_glb.py'), os.path.join(ORIG, skp), glb, modo,
                        '--sin-productos', '--productos', os.path.join(CACHE, f'{modo}.json')], check=True)


def productos_de(modo):
    lista = json.load(open(os.path.join(CACHE, f'{modo}.json'), encoding='utf-8'))
    if modo == 'mueble2':  # el .skp trae un módulo: se repite a ±0,60 m
        lista = [dict(q, centro=[q['centro'][0] + dx, q['centro'][1], q['centro'][2]]) for dx in (-0.6, 0.6) for q in lista]
    return lista


# ------------------------------------------------------------------ materiales

def nodos(mat):
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    return nt, out


def imagen(ruta, nombre=None, color=True):
    img = bpy.data.images.load(ruta, check_existing=True)
    if nombre:
        img.name = nombre
    img.colorspace_settings.name = 'sRGB' if color else 'Non-Color'
    return img


def tex(nt, img, extension='REPEAT'):
    t = nt.nodes.new('ShaderNodeTexImage')
    t.image = img
    t.extension = extension
    t.interpolation = 'Cubic'
    return t


def principled(nt, **kw):
    p = nt.nodes.new('ShaderNodeBsdfPrincipled')
    for k, v in kw.items():
        p.inputs[k].default_value = v
    return p


def mat_textura(nombre, ruta, rugosidad, especular=0.5, extension='MIRROR', recorte=None, capa=0.0):
    m = bpy.data.materials.new(nombre)
    nt, out = nodos(m)
    if recorte:
        ruta_r = os.path.join(CACHE, f'{nombre}.png')
        Image.open(ruta).convert('RGB').crop(recorte).save(ruta_r)
        ruta = ruta_r
    t = tex(nt, imagen(ruta), extension)
    p = principled(nt, Roughness=rugosidad)
    p.inputs['Specular IOR Level'].default_value = especular
    if capa:
        p.inputs['Coat Weight'].default_value = capa
        p.inputs['Coat Roughness'].default_value = 0.25
    nt.links.new(t.outputs['Color'], p.inputs['Base Color'])
    nt.links.new(p.outputs[0], out.inputs[0])
    return m


def mat_color(nombre, rgb, rugosidad=0.5, metal=0.0, aniso=0.0, transmision=0.0, ior=1.45, alfa=1.0):
    m = bpy.data.materials.new(nombre)
    nt, out = nodos(m)
    p = principled(nt, Roughness=rugosidad, Metallic=metal)
    p.inputs['Base Color'].default_value = (*rgb, 1)
    p.inputs['Anisotropic'].default_value = aniso
    p.inputs['Transmission Weight'].default_value = transmision
    p.inputs['IOR'].default_value = ior
    p.inputs['Alpha'].default_value = alfa
    nt.links.new(p.outputs[0], out.inputs[0])
    return m


def mat_emision(nombre, rgb, fuerza):
    m = bpy.data.materials.new(nombre)
    nt, out = nodos(m)
    e = nt.nodes.new('ShaderNodeEmission')
    e.inputs['Color'].default_value = (*rgb, 1)
    e.inputs['Strength'].default_value = fuerza
    nt.links.new(e.outputs[0], out.inputs[0])
    return m


def mat_tela(nombre, ruta, fuerza):
    """Tela backlight: el arte se ve por la luz que la atraviesa (emisión 5000K) más un poco de difuso."""
    m = bpy.data.materials.new(nombre)
    nt, out = nodos(m)
    t = tex(nt, imagen(ruta), 'EXTEND')
    e = nt.nodes.new('ShaderNodeEmission')
    e.inputs['Strength'].default_value = fuerza
    tinte = nt.nodes.new('ShaderNodeVectorMath')  # luz 5000K detrás de la tela
    tinte.operation = 'MULTIPLY'
    tinte.inputs[1].default_value = K5000
    nt.links.new(t.outputs['Color'], tinte.inputs[0])
    nt.links.new(tinte.outputs['Vector'], e.inputs['Color'])
    d = principled(nt, Roughness=0.85)
    nt.links.new(t.outputs['Color'], d.inputs['Base Color'])
    suma = nt.nodes.new('ShaderNodeAddShader')
    nt.links.new(e.outputs[0], suma.inputs[0])
    nt.links.new(d.outputs[0], suma.inputs[1])
    nt.links.new(suma.outputs[0], out.inputs[0])
    return m


def mat_recorte(nombre, ruta, metal=0.0, rugosidad=0.45, rgb=None, emision=0.0, emision_rgb=None):
    """Imagen con alfa (logo, isotipo, halo o foto de producto): fuera del alfa es transparente."""
    m = bpy.data.materials.new(nombre)
    nt, out = nodos(m)
    t = tex(nt, imagen(ruta), 'CLIP')
    p = principled(nt, Roughness=rugosidad, Metallic=metal)
    if rgb:
        p.inputs['Base Color'].default_value = (*rgb, 1)
    else:
        nt.links.new(t.outputs['Color'], p.inputs['Base Color'])
    if emision:
        p.inputs['Emission Strength'].default_value = emision
        if emision_rgb:
            p.inputs['Emission Color'].default_value = (*emision_rgb, 1)
        else:
            nt.links.new(t.outputs['Color'], p.inputs['Emission Color'])
    nt.links.new(t.outputs['Alpha'], p.inputs['Alpha'])
    nt.links.new(p.outputs[0], out.inputs[0])
    return m


def mat_halo(nombre, ruta, fuerza):
    m = bpy.data.materials.new(nombre)
    nt, out = nodos(m)
    t = tex(nt, imagen(ruta), 'CLIP')
    e = nt.nodes.new('ShaderNodeEmission')
    e.inputs['Color'].default_value = (*K3000, 1)
    e.inputs['Strength'].default_value = fuerza
    tr = nt.nodes.new('ShaderNodeBsdfTransparent')
    mix = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(t.outputs['Alpha'], mix.inputs['Fac'])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(e.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs[0])
    return m


class Materiales:
    def __init__(self):
        self.capri = mat_textura('Capri', os.path.join(MAT, 'capri.jpg'), 0.62, 0.35, recorte=(0, 0, 600, 480))
        self.duna = mat_textura('Duna', os.path.join(MAT, 'duna.jpg'), 0.42, 0.5, capa=0.12)
        self.nacar = mat_textura('Nacar', os.path.join(MAT, 'nacar.jpg'), 0.45, 0.45, capa=0.08)
        self.inox = mat_color('Inox', (0.86, 0.86, 0.87), 0.2, 1.0, aniso=0.6)
        self.aluminio = mat_color('Aluminio', (0.84, 0.83, 0.81), 0.28, 1.0, aniso=0.3)
        self.sombra = mat_color('Sombra', (0.30, 0.27, 0.24), 0.9)
        self.led = mat_emision('LED 3000K', K3000, 45.0)
        self.acrilico = mat_color('Acrilico', (0.96, 0.96, 0.95), 0.3, transmision=0.55, ior=1.49)  # ficha acrílica esmerilada
        self.blanco = mat_color('Plastico blanco', (0.93, 0.93, 0.92), 0.3)
        self.checkpoint = mat_color('Checkpoint', (0.95, 0.95, 0.94), 0.22)
        # platino: metal cepillado claro con un leve brillo propio para que no se apague contra el Capri
        self.logo = mat_recorte('Platino logo', LOGO, metal=0.7, rugosidad=0.32, rgb=(0.93, 0.92, 0.9), emision=0.35, emision_rgb=(0.95, 0.94, 0.92))
        self.isotipo = mat_recorte('Platino isotipo', ISOTIPO, metal=0.7, rugosidad=0.32, rgb=(0.93, 0.92, 0.9), emision=0.35, emision_rgb=(0.95, 0.94, 0.92))
        self.artes = {}

    def arte(self, nombre, proporcion, fuerza):
        clave = (nombre, round(proporcion, 3))
        if clave not in self.artes:
            ruta = os.path.join(CACHE, f'arte-{nombre}-{proporcion:.3f}.png')
            if not os.path.exists(ruta):
                Image.fromarray(artes_a_la_talla.generar(nombre, proporcion, 1600)).save(ruta)
            self.artes[clave] = mat_tela(f'Tela {nombre}', ruta, fuerza)
        return self.artes[clave]


def halo_png(origen, destino):
    """Halo de contorno del logo para la emisión 3000K: la luz sale por detrás de las letras (separadores de 15 mm)
    y baña el Capri pegada al contorno. Mismo lienzo que el plano del halo de skp_a_glb.py (22 % más ancho)."""
    from PIL import ImageFilter
    from skp_a_glb import HALO
    if not os.path.exists(destino):
        img = Image.open(origen).convert('RGBA')
        img.thumbnail((1024, 1024))
        W, H = img.size
        lienzo = Image.new('L', (int(W * HALO[0]), int(H * (1 + (HALO[0] - 1) * HALO[1]))), 0)
        lienzo.paste(img.getchannel('A'), ((lienzo.width - W) // 2, (lienzo.height - H) // 2))
        base = min(W, H)
        cerca = np.asarray(lienzo.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(base * 0.035)), np.float32) / 255
        lejos = np.asarray(lienzo.filter(ImageFilter.GaussianBlur(base * 0.12)), np.float32) / 255
        alfa = np.clip(1.25 * cerca + 0.9 * lejos / max(lejos.max(), 1e-6) * 0.6, 0, 1)
        a = Image.fromarray((alfa * 255).astype(np.uint8))
        Image.merge('RGBA', (Image.new('L', a.size, 255),) * 3 + (a,)).save(destino)
    return destino


# ------------------------------------------------------------------ escena

def limpiar():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def importar(modo, M, ubicacion=(0, 0, 0), fuerza_arte=1.6, artes=None):
    """Importa el GLB de la pieza, cambia sus materiales por los del proyecto y la ubica (coordenadas glTF)."""
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(CACHE, f'{modo}.glb'))
    nuevos = [o for o in bpy.data.objects if o not in antes]
    raiz = bpy.data.objects.new(f'pieza-{modo}', None)
    bpy.context.scene.collection.objects.link(raiz)
    for o in nuevos:
        if o.parent is None:
            o.parent = raiz
    raiz.location = gl(*ubicacion)
    halo_logo = mat_halo('Halo logo', halo_png(LOGO, os.path.join(CACHE, 'halo-logo.png')), 7.0)
    halo_iso = mat_halo('Halo isotipo', halo_png(ISOTIPO, os.path.join(CACHE, 'halo-isotipo.png')), 7.0)
    for o in nuevos:
        if o.type != 'MESH':
            continue
        o.visible_shadow = 'halo' not in o.name and 'led' not in o.name
        for slot in o.material_slots:
            if slot.material and slot.material.get('proyecto'):
                continue  # malla compartida entre módulos: ya tiene el material del proyecto
            n = slot.material.name if slot.material else ''
            if n.startswith('Capri'):
                nuevo = M.capri
            elif n.startswith('Duna'):
                nuevo = M.duna
            elif n.startswith('Nácar'):
                nuevo = M.nacar
            elif n.startswith('Inox'):
                nuevo = M.inox
            elif n.startswith('Aluminio'):
                nuevo = M.aluminio
            elif n.startswith('Tela backlight'):
                ancho, alto = dimensiones_tela(o)
                arte = (artes or {}).get('modulo 2' if 'módulo 2' in n else 'modulo 1')
                nuevo = M.arte(arte, ancho / alto, fuerza_arte)
            elif n.startswith('Línea de sombra'):
                nuevo = M.sombra
            elif n.startswith('LED'):
                nuevo = M.led
            elif n.startswith('Acrílico'):
                nuevo = M.acrilico
            elif n.startswith('Platino · logo'):
                nuevo = M.logo
            elif n.startswith('Platino · isotipo'):
                nuevo = M.isotipo
            elif n.startswith('Halo 3000K · logo'):
                nuevo = halo_logo
            elif n.startswith('Halo 3000K · isotipo'):
                nuevo = halo_iso
            else:
                nuevo = M.blanco
            nuevo['proyecto'] = True
            slot.material = nuevo
    bajar = OPCIONES.get(modo, {}).get('bajar')
    if bajar:  # fichas y soportes acrílicos del mesón, que en el .skp flotan sobre el tope
        for o in nuevos:
            if o.type == 'MESH' and o.material_slots and o.material_slots[0].material.name == 'Acrilico':
                for v in o.data.vertices:
                    if v.co.z < 1.0:
                        v.co.z -= bajar
    return raiz, nuevos


def dimensiones_tela(o):
    v = np.array([o.matrix_world @ p.co for p in o.data.vertices])
    return np.ptp(v[:, 0]), np.ptp(v[:, 2])


def plano_foto(nombre, ruta, alto, centro, mira, M_cache, adelante=0.0):
    """Foto recortada del producto en un plano vertical que mira hacia la cámara (solo gira en el eje vertical).
    adelante: cuánto se adelanta el plano hacia la cámara (para tapar el poste o el soporte que lo sostiene)."""
    if ruta not in M_cache:
        M_cache[ruta] = mat_recorte(f'Producto {os.path.basename(ruta)}', ruta, rugosidad=0.5, emision=0.22)
    w, h = Image.open(ruta).size
    ancho = alto * w / h
    bpy.ops.mesh.primitive_plane_add(size=1)
    p = bpy.context.object
    p.name = nombre
    p.scale = (ancho, alto, 1)
    p.rotation_euler = (math.pi / 2, 0, 0)
    p.location = centro
    d = Vector((mira.x - centro.x, mira.y - centro.y))
    p.rotation_euler.z = math.atan2(d.x, -d.y)
    p.location += Vector((math.sin(p.rotation_euler.z), -math.cos(p.rotation_euler.z), 0)) * adelante
    p.data.materials.append(M_cache[ruta])
    return p


def cilindro(r, h, ubicacion, mat, nombre):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, vertices=48, location=(ubicacion.x, ubicacion.y, ubicacion.z + h / 2))
    o = bpy.context.object
    o.name = nombre
    bpy.ops.object.shade_smooth()
    o.data.materials.append(mat)
    return o


def poner_productos(modo, ubicacion, M, camara, cache, desplazar=(0, 0, 0)):
    """Productos reales de Cubitt donde el .skp tenía los de referencia: relojes en checkpoint y audio sobre el elevador."""
    objetos = []
    opc = OPCIONES.get(modo, {})
    lista = productos_de(modo)
    for q in lista:  # productos del mesón apoyados sobre el tope
        if opc.get('bajar') and q['base'] < 1.0:
            q['base'] -= opc['bajar']
            q['centro'][1] -= opc['bajar']
    relojes = sorted([q for q in lista if q['tipo'] == 'reloj'], key=lambda q: (round(q['centro'][2], 2), q['centro'][0]))
    # filas de adelante hacia atrás; en cada fila de izquierda a derecha (el display tiene dos filas)
    filas = {}
    for q in relojes:
        filas.setdefault(round(q['centro'][2], 2), []).append(q)
    orden = [q for z in sorted(filas, reverse=True) for q in sorted(filas[z], key=lambda q: q['centro'][0])]
    if modo == 'mueble2':
        orden = sorted(relojes, key=lambda q: q['centro'][0])
    nombres = RELOJES[modo]
    ox, oy, oz = (ubicacion[i] + desplazar[i] for i in range(3))
    for i, q in enumerate(orden):
        x, base, z = q['centro'][0] + ox, q['base'] + oy, q['centro'][2] + oz
        b = gl(x, base, z)
        objetos.append(cilindro(0.025, 0.008, b, M.checkpoint, f'checkpoint-{i}'))
        objetos.append(cilindro(0.0055, 0.034, b + Vector((0, 0, 0.008)), M.checkpoint, f'poste-{i}'))
        foto = os.path.join(PROD, f'{nombres[i % len(nombres)]}.png')
        objetos.append(plano_foto(f'reloj-{i}', foto, 0.072, b + Vector((0, 0, 0.025 + 0.036)), camara, cache, adelante=0.012))
        if opc.get('fichas'):
            bpy.ops.mesh.primitive_cube_add(size=1, location=gl(x, base + 0.002, z + 0.072))
            ficha = bpy.context.object
            ficha.scale = (0.08, 0.05, 0.004)
            ficha.data.materials.append(M.acrilico)
            objetos.append(ficha)
    vistos = {}
    for q in sorted([q for q in lista if q['tipo'] in AUDIO], key=lambda q: q['centro'][0]):
        info = AUDIO[q['tipo']]
        if isinstance(info[0], tuple):  # dos parlantes pequeños: el de la izquierda Power Go 2, el otro Power Mini
            k = vistos.get((q['grupo'], round(q['centro'][0] + ox, 1) // 1.2), 0)
            vistos[(q['grupo'], round(q['centro'][0] + ox, 1) // 1.2)] = k + 1
            info = info[min(k, 1)]
        nombre, alto = info
        x, base, z = q['centro'][0] + ox, q['base'] + oy, q['centro'][2] + oz
        b = gl(x, base, z)
        if nombre == 'power-anc-negro' and not opc.get('soporte_audifonos', True):  # cuelga del soporte acrílico del .skp
            objetos.append(plano_foto(nombre, os.path.join(PROD, f'{nombre}.png'), alto, gl(x, q['centro'][1], z), camara, cache, adelante=0.03))
        elif nombre == 'power-anc-negro':  # soporte de audífonos en aluminio
            objetos.append(cilindro(0.035, 0.006, b, M.aluminio, 'soporte-base'))
            objetos.append(cilindro(0.005, 0.17, b + Vector((0, 0.01, 0.006)), M.aluminio, 'soporte-poste'))
            objetos.append(plano_foto(nombre, os.path.join(PROD, f'{nombre}.png'), alto, b + Vector((0, 0, 0.02 + alto / 2)), camara, cache, adelante=0.016))
        else:
            objetos.append(plano_foto(nombre, os.path.join(PROD, f'{nombre}.png'), alto, b + Vector((0, 0, alto / 2)), camara, cache))
    return objetos


def tienda(piso=True, muros=(), mostrador=None, M=None):
    """Piso de porcelanato claro, muros blanco cálido y, si se pide, el mostrador de la tienda."""
    objs = []
    if piso:
        m = bpy.data.materials.new('Piso')
        nt, out = nodos(m)
        p = principled(nt, Roughness=0.3)
        ruido = nt.nodes.new('ShaderNodeTexNoise')
        ruido.inputs['Scale'].default_value = 3.0
        rampa = nt.nodes.new('ShaderNodeValToRGB')
        rampa.color_ramp.elements[0].color = (0.46, 0.43, 0.40, 1)
        rampa.color_ramp.elements[1].color = (0.53, 0.50, 0.46, 1)
        nt.links.new(ruido.outputs['Fac'], rampa.inputs['Fac'])
        nt.links.new(rampa.outputs['Color'], p.inputs['Base Color'])
        nt.links.new(p.outputs[0], out.inputs[0])
        bpy.ops.mesh.primitive_plane_add(size=30)
        bpy.context.object.data.materials.append(m)
        objs.append(bpy.context.object)
    mm = mat_color('Muro', (0.78, 0.75, 0.71), 0.9)
    for (x, y, rot, ancho) in muros:  # x, y del centro en planta (Blender), giro y ancho
        bpy.ops.mesh.primitive_plane_add(size=1, location=(x, y, 1.6), rotation=(math.pi / 2, 0, rot))
        o = bpy.context.object
        o.scale = (ancho, 3.2, 1)
        o.data.materials.append(mm)
        objs.append(o)
    if mostrador:
        x, y, w, d, h = mostrador
        mb = mat_color('Mostrador', (0.92, 0.91, 0.89), 0.18)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, h / 2))
        o = bpy.context.object
        o.scale = (w, d, h)
        bev = o.modifiers.new('bisel', 'BEVEL')
        bev.width, bev.segments = 0.012, 3
        o.data.materials.append(mb)
        objs.append(o)
    return objs


def luces(principal=(0.6, -1.2, 3.0), fuerza=1.0, focos=()):
    w = bpy.data.worlds.new('Mundo')
    bpy.context.scene.world = w
    w.use_nodes = True
    w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.92, 0.89, 0.85, 1)
    w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.07 * fuerza
    # plafón difuso de la tienda (4000K) y focos cálidos dirigidos a las piezas (3000K)
    d = bpy.data.lights.new('plafon', 'AREA')
    d.shape, d.size, d.size_y = 'RECTANGLE', 4.0, 3.0
    d.energy, d.color = 240 * fuerza, K4000
    o = bpy.data.objects.new('plafon', d)
    o.location = principal
    bpy.context.scene.collection.objects.link(o)
    for i, (pos, objetivo, energia) in enumerate(focos):
        f = bpy.data.lights.new(f'foco{i}', 'SPOT')
        f.energy, f.color, f.spot_size, f.spot_blend, f.shadow_soft_size = energia * 1.6, K3000, math.radians(38), 0.55, 0.1
        o = bpy.data.objects.new(f'foco{i}', f)
        o.location = pos
        direc = Vector(objetivo) - Vector(pos)
        o.rotation_euler = direc.to_track_quat('-Z', 'Y').to_euler()
        bpy.context.scene.collection.objects.link(o)


def camara(pos_gl, obj_gl, lente=40, apertura=None, foco_gl=None):
    c = bpy.data.cameras.new('cam')
    c.lens = lente
    c.sensor_width = 36
    o = bpy.data.objects.new('cam', c)
    bpy.context.scene.collection.objects.link(o)
    o.location = gl(*pos_gl)
    o.rotation_euler = (gl(*obj_gl) - o.location).to_track_quat('-Z', 'Y').to_euler()
    if apertura:
        c.dof.use_dof = True
        c.dof.aperture_fstop = apertura
        c.dof.focus_distance = (gl(*(foco_gl or obj_gl)) - o.location).length
    bpy.context.scene.camera = o
    return o


def configurar(ancho, muestras, exposicion=0.0):
    s = bpy.context.scene
    s.render.engine = 'CYCLES'
    s.cycles.device = 'CPU'
    s.cycles.samples = muestras
    s.cycles.use_adaptive_sampling = True
    s.cycles.adaptive_threshold = 0.02
    s.cycles.use_denoising = True
    s.cycles.denoiser = 'OPENIMAGEDENOISE'
    s.cycles.max_bounces = 8
    s.cycles.transparent_max_bounces = 32
    s.cycles.caustics_reflective = False
    s.cycles.caustics_refractive = False
    s.cycles.blur_glossy = 1.0
    s.render.resolution_x = ancho
    s.render.resolution_y = round(ancho * 10 / 16)
    s.render.resolution_percentage = 100
    s.render.image_settings.file_format = 'PNG'
    s.view_settings.view_transform = 'AgX'
    try:
        s.view_settings.look = 'AgX - Medium High Contrast'
    except TypeError:
        pass
    s.view_settings.exposure = exposicion
    s.render.film_transparent = False


# ------------------------------------------------------------------ tomas

ARTES_MESA = {'modulo 1': 'viva-pro-2'}
ARTES_MUEBLE = {'modulo 1': 'nueva-era'}
ARTES_MUEBLE2 = {'modulo 1': 'nueva-era', 'modulo 2': 'viva-pro-2'}
ARTES_SOBREMESA = {'modulo 1': 'nueva-era'}


def toma(nombre, M):
    """Monta la toma y devuelve la exposición. Las posiciones van en coordenadas glTF (metros)."""
    cache = {}
    if nombre == 'familia':
        cam = camara((1.95, 1.32, 3.25), (0.6, 0.74, -0.8), lente=34)
        importar('mesa', M, artes=ARTES_MESA)
        poner_productos('mesa', (0, 0, 0), M, cam.location, cache)
        importar('mueble2', M, (0, 0, -1.75), artes=ARTES_MUEBLE2)
        poner_productos('mueble2', (0, 0, -1.75), M, cam.location, cache)
        importar('sobremesa', M, (2.35, 0.9, -0.85), artes=ARTES_SOBREMESA)
        poner_productos('sobremesa', (2.35, 0.9, -0.85), M, cam.location, cache)
        tienda(muros=[(0, 1.97, 0, 12), (-3.2, 0, math.pi / 2, 8)], mostrador=(2.35, 0.85, 1.2, 0.6, 0.9))
        luces((0.4, 0.2, 3.1), 1.0, [((0.9, -1.6, 2.9), (0, 0, 0.8), 260), ((-0.3, 0.6, 2.9), (0, 1.7, 1.0), 300),
                                     ((2.6, 0.2, 2.9), (2.35, 0.85, 1.0), 120)])
        return 0.0
    if nombre in ('mesa', 'touch', 'vendedor', 'logo', 'material', 'despiece'):
        vistas = {
            'mesa': dict(pos=(1.45, 1.3, 1.95), obj=(0.0, 0.52, 0.0), lente=46),
            'touch': dict(pos=(-0.42, 1.18, 0.95), obj=(0.04, 0.84, -0.02), lente=50, apertura=4.0, foco=(0.0, 0.85, 0.1)),
            'vendedor': dict(pos=(-1.45, 1.38, -1.85), obj=(0.0, 0.55, -0.05), lente=42),
            'logo': dict(pos=(1.2, 0.55, 0.55), obj=(0.5, 0.42, -0.03), lente=55, apertura=5.6, foco=(0.5, 0.4, 0.0)),
            'material': dict(pos=(0.92, 0.98, 0.78), obj=(0.44, 0.64, 0.18), lente=45, apertura=5.6, foco=(0.5, 0.77, 0.25)),
            'despiece': dict(pos=(2.5, 1.7, 2.95), obj=(0.0, 0.88, 0.0), lente=40),
        }[nombre]
        cam = camara(vistas['pos'], vistas['obj'], vistas['lente'], vistas.get('apertura'), vistas.get('foco'))
        raiz, objs = importar('mesa', M, artes=ARTES_MESA)
        prods = poner_productos('mesa', (0, 0, 0), M, cam.location, cache)
        if nombre == 'despiece':
            despiece(objs, prods)
            # números de los cinco pasos de «Se arma en cinco pasos» (index.html), junto a cada capa
            ETIQUETAS[:] = [(1, (0.5, 0.03, 0.25)), (2, (0.5, 0.55, 0.25)), (3, (-0.5, 0.95, 0.6)),
                            (4, (0.5, 1.29, 0.25)), (5, (0.46, 1.5, -0.14))]
        if nombre == 'vendedor':
            tienda(muros=[(0, -2.4, 0, 16), (-3.0, 0, math.pi / 2, 10)])
        else:
            tienda(muros=[(0, 2.2, 0, 16), (-3.0, 0, math.pi / 2, 10)])
        luces((0.5, -0.6, 3.0), 1.0, [((1.2, -1.4, 2.8), (0, 0, 0.8), 220), ((-1.0, 1.2, 2.8), (0, 0, 0.8), 140)])
        return {'logo': -0.2, 'despiece': 0.1}.get(nombre, 0.0)
    if nombre in ('mueble', 'modular'):
        modo = 'mueble' if nombre == 'mueble' else 'mueble2'
        cam = camara(*(((1.4, 1.4, 2.45), (0.0, 0.8, -0.1)) if nombre == 'mueble' else ((1.75, 1.6, 2.95), (0.12, 0.92, -0.1))),
                     lente=38 if nombre == 'mueble' else 35)
        importar(modo, M, artes=ARTES_MUEBLE if modo == 'mueble' else ARTES_MUEBLE2)
        poner_productos(modo, (0, 0, 0), M, cam.location, cache)
        tienda(muros=[(0, 0.215, 0, 12)])
        luces((0.3, -1.4, 3.0), 1.0, [((1.0, -1.6, 2.9), (0, 0, 0.9), 240), ((-1.2, -1.4, 2.9), (0, 0, 1.0), 180)])
        return 0.0
    if nombre == 'sobremesa':
        cam = camara((0.62, 1.3, 0.82), (0.0, 1.0, -0.02), lente=50, apertura=5.6, foco_gl=(0.0, 1.0, 0.02))
        importar('sobremesa', M, (0, 0.9, 0), artes=ARTES_SOBREMESA)
        poner_productos('sobremesa', (0, 0.9, 0), M, cam.location, cache)
        tienda(muros=[(0, 1.6, 0, 10)], mostrador=(0, 0.0, 1.4, 0.65, 0.9))
        luces((0.3, -0.5, 3.0), 0.9, [((0.8, -1.0, 2.6), (0, 0, 0.95), 160)])
        return 0.0
    if nombre in ('muro', 'muro-detalle'):
        if nombre == 'muro':
            cam = camara((2.05, 1.5, 4.3), (0.0, 1.27, 0.0), lente=34)
        else:
            cam = camara((0.8, 1.38, 1.15), (-0.1, 1.0, -0.02), lente=40, apertura=4.0, foco_gl=(0.1, 0.92, 0.07))
        importar('muro', M, artes={'modulo 1': 'nueva-era'})
        poner_productos('muro', (0, 0, 0), M, cam.location, cache)
        tienda(muros=[(0, 0.245, 0, 12), (-2.6, 0, math.pi / 2, 10)])
        luces((0.4, -1.2, 3.1), 1.0, [((1.2, -1.8, 3.0), (0, 0, 1.0), 260), ((-1.2, -1.8, 3.0), (0, 0, 1.2), 200)])
        return 0.0
    raise SystemExit(f'toma desconocida: {nombre}')


ETIQUETAS = []


def numerar(png):
    """Dibuja los números de los pasos del despiece sobre el render (círculo Capri oscuro con el número en blanco)."""
    from bpy_extras.object_utils import world_to_camera_view
    from PIL import ImageDraw, ImageFont
    s = bpy.context.scene
    img = Image.open(png).convert('RGB')
    W, H = img.size
    d = ImageDraw.Draw(img)
    r = round(W * 0.016)
    try:
        fuente = ImageFont.truetype('DejaVuSans-Bold.ttf', round(r * 1.15))
    except OSError:
        fuente = ImageFont.load_default(round(r * 1.15))
    for n, p in ETIQUETAS:
        c = world_to_camera_view(s, s.camera, gl(*p))
        x, y = c.x * W + r * 1.6, (1 - c.y) * H
        d.ellipse((x - r, y - r, x + r, y + r), fill=(59, 53, 48), outline=(242, 236, 228), width=max(2, r // 8))
        d.text((x, y), str(n), fill=(255, 255, 255), font=fuente, anchor='mm')
    img.save(png)


def despiece(objs, prods):
    """Separa la mesa en capas: zócalo abajo, cuerpo, caja de luz al frente, logos a los lados, línea LED, tope,
    elevador y productos arriba (como el despiece de la escena 3D)."""
    for o in objs:
        if o.type != 'MESH' or not o.material_slots:
            continue
        n = o.material_slots[0].material.name
        dz = {'Inox': 0.0, 'Sombra': 0.36, 'LED 3000K': 0.36, 'Acrilico': 0.8, 'Duna': 0.0, 'Plastico blanco': 0.68}.get(n, 0.18)
        dy = 0
        if n.startswith('Tela') or n == 'Aluminio':
            dy = -0.35
        o.location.z += dz
        o.location.y += dy
        if n == 'Duna':
            separar_duna(o)
    for o in objs:
        if o.type == 'MESH' and o.material_slots and o.material_slots[0].material.name.startswith(('Platino', 'Halo')):
            v = np.array([o.matrix_world @ p.co for p in o.data.vertices])
            o.location.x += 0.25 * np.sign(v[:, 0].mean())
    for p in prods:
        p.location.z += 0.8


def separar_duna(o):
    """El tope y el elevador comparten material: se separan por piezas sueltas y el elevador sube más."""
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.separate(type='LOOSE')
    bpy.ops.object.mode_set(mode='OBJECT')
    for p in bpy.context.selected_objects:
        v = np.array([p.matrix_world @ q.co for q in p.data.vertices])
        # el elevador está todo por encima del tope (78,8 cm) y dentro de su franja al fondo de la mesa
        elevador = v[:, 2].min() > 0.785 and v[:, 1].min() > 0.045 and np.abs(v[:, 0]).max() < 0.47
        p.location.z += 0.68 if elevador else 0.52


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    opt = lambda k, d: type(d)(sys.argv[sys.argv.index(k) + 1]) if k in sys.argv else d
    muestras, ancho = opt('--muestras', 160), opt('--ancho', 1920)
    salida = opt('--salida', os.path.join(RAIZ, 'renders'))
    tomas = ['familia', 'mesa', 'touch', 'vendedor', 'mueble', 'modular', 'sobremesa', 'logo', 'material', 'despiece', 'muro', 'muro-detalle']
    pedidas = tomas if not args or args[0] == 'todas' else args[0].split(',')
    preparar_modelos()
    os.makedirs(salida, exist_ok=True)
    for nombre in pedidas:
        limpiar()
        M = Materiales()
        exposicion = toma(nombre, M)
        configurar(ancho, muestras, exposicion)
        png = os.path.join(CACHE, f'{nombre}.png')
        bpy.context.scene.render.filepath = png
        ETIQUETAS.clear() if nombre != 'despiece' else None
        bpy.ops.render.render(write_still=True)
        if nombre == 'despiece' and ETIQUETAS:
            numerar(png)
        img = Image.open(png).convert('RGB')
        img.save(os.path.join(salida, f'{nombre}.jpg'), quality=90, optimize=True, progressive=True)
        img.thumbnail((900, 900))
        img.save(os.path.join(salida, f'{nombre}-900.jpg'), quality=86, optimize=True, progressive=True)
        print(f'{nombre}: {os.path.join(salida, nombre + ".jpg")}', flush=True)


if __name__ == '__main__':
    main()

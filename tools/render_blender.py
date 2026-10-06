"""Renders de la propuesta con Blender Cycles, hechos sobre los modelos exactos de los SketchUp.

Así cada render coincide con la escena 3D, los planos y los GLB: mismas medidas, mismas cajas de luz con los artes
a la talla, el logo oficial con halo 3000K y los productos reales de Cubitt (fotos recortadas en artes-cubitt/productos).

Uso:
  python tools/skp_a_glb.py "<primer...skp>"  <dir>/mesa.glb    mesa    --sin-productos
  python tools/skp_a_glb.py "<segundo...skp>" <dir>/mueble.glb  mueble  --sin-productos
  python tools/skp_a_glb.py "<segundo...skp>" <dir>/mueble2.glb mueble2 --sin-productos
  python tools/render_blender.py <dir> <salida> [familia mesa touch vendedor mueble modular sobremesa logo material despiece]
         [--muestras 128] [--escala 1.0] [--web propuesta-2027/renders]
  Con --web también guarda las versiones de la página: <nombre>.jpg (hasta 2000 px, q84) y <nombre>-900.jpg (q80).
Requiere el paquete bpy (Blender como módulo de Python) y Pillow.
"""
import json
import math
import os
import sys

import bpy
from mathutils import Vector

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'propuesta-2027')
PROD = os.path.join(RAIZ, 'artes-cubitt', 'productos')
TALLA = os.path.join(RAIZ, 'artes-cubitt', 'a-la-talla')
LOGO = os.path.join(RAIZ, 'assets', 'logo', 'logo-cubitt-platino.png')
DUNA = os.path.join(RAIZ, 'assets', 'materiales', 'duna.jpg')


def B(x, y, z):
    """Coordenadas de la web (glTF: Y arriba, Z hacia el cliente) -> Blender (Z arriba)."""
    return Vector((x, -z, y))


def lin(r, g, b):
    f = lambda c: (c / 255) / 12.92 if c / 255 <= 0.04045 else ((c / 255 + 0.055) / 1.055) ** 2.4
    return (f(r), f(g), f(b), 1.0)


# ------------------------------------------------------------------ materiales

def _mat(nombre):
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    return m, m.node_tree.nodes, m.node_tree.links, m.node_tree.nodes['Principled BSDF']


def principled(nombre, color, rugosidad=0.5, metal=0.0, aniso=0.0, coat=0.0):
    m, n, l, b = _mat(nombre)
    b.inputs['Base Color'].default_value = color
    b.inputs['Roughness'].default_value = rugosidad
    b.inputs['Metallic'].default_value = metal
    if aniso:
        b.inputs['Anisotropic'].default_value = aniso
    if coat:
        b.inputs['Coat Weight'].default_value = coat
    return m


def mat_capri():
    m = principled('Capri', lin(192, 180, 168), 0.72)
    n, l = m.node_tree.nodes, m.node_tree.links
    ruido = n.new('ShaderNodeTexNoise')
    ruido.inputs['Scale'].default_value = 900
    rel = n.new('ShaderNodeBump')
    rel.inputs['Strength'].default_value = 0.025
    l.new(ruido.outputs['Fac'], rel.inputs['Height'])
    l.new(rel.outputs['Normal'], n['Principled BSDF'].inputs['Normal'])
    return m


def mat_duna():
    m, n, l, b = _mat('Duna')
    tc = n.new('ShaderNodeTexCoord')
    mp = n.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (2.4, 2.4, 2.4)
    tx = n.new('ShaderNodeTexImage')
    tx.image = bpy.data.images.load(DUNA)
    tx.projection = 'BOX'
    tx.projection_blend = 0.25
    l.new(tc.outputs['Object'], mp.inputs['Vector'])
    l.new(mp.outputs['Vector'], tx.inputs['Vector'])
    l.new(tx.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.5
    b.inputs['Coat Weight'].default_value = 0.15
    b.inputs['Coat Roughness'].default_value = 0.3
    return m


def mat_emisivo(nombre, color, fuerza):
    m, n, l, b = _mat(nombre)
    b.inputs['Base Color'].default_value = color
    b.inputs['Emission Color'].default_value = color
    b.inputs['Emission Strength'].default_value = fuerza
    return m


def mat_arte(imagen, fuerza=2.4):
    m, n, l, b = _mat('Tela backlight ' + imagen.name)
    tx = n.new('ShaderNodeTexImage')
    tx.image = imagen
    l.new(tx.outputs['Color'], b.inputs['Base Color'])
    l.new(tx.outputs['Color'], b.inputs['Emission Color'])
    b.inputs['Emission Strength'].default_value = fuerza
    b.inputs['Roughness'].default_value = 0.9
    return m


def mat_imagen_alfa(nombre, ruta_o_imagen, metal=0.0, rugosidad=0.5, color=None):
    m, n, l, b = _mat(nombre)
    tx = n.new('ShaderNodeTexImage')
    tx.image = ruta_o_imagen if isinstance(ruta_o_imagen, bpy.types.Image) else bpy.data.images.load(ruta_o_imagen)
    if color is None:
        l.new(tx.outputs['Color'], b.inputs['Base Color'])
    else:
        mx = n.new('ShaderNodeMix')
        mx.data_type = 'RGBA'
        mx.inputs['Factor'].default_value = 0.55
        l.new(tx.outputs['Color'], mx.inputs['A'])
        mx.inputs['B'].default_value = color
        l.new(mx.outputs['Result'], b.inputs['Base Color'])
    l.new(tx.outputs['Alpha'], b.inputs['Alpha'])
    b.inputs['Metallic'].default_value = metal
    b.inputs['Roughness'].default_value = rugosidad
    return m


def mat_halo(imagen, fuerza=2.2):
    """Luz 3000K que sale por detrás de las letras y baña el Capri."""
    m, n, l, b = _mat('Halo 3000K')
    tx = n.new('ShaderNodeTexImage')
    tx.image = imagen
    em = n.new('ShaderNodeEmission')
    em.inputs['Color'].default_value = (1.0, 0.52, 0.2, 1)
    em.inputs['Strength'].default_value = fuerza
    tr = n.new('ShaderNodeBsdfTransparent')
    mx = n.new('ShaderNodeMixShader')
    l.new(tx.outputs['Alpha'], mx.inputs['Fac'])
    l.new(tr.outputs['BSDF'], mx.inputs[1])
    l.new(em.outputs['Emission'], mx.inputs[2])
    l.new(mx.outputs['Shader'], n['Material Output'].inputs['Surface'])
    return m


def mat_vidrio():
    # acrílico de las fichas de precio: lámina clara y algo traslúcida (sin refracción oscura sobre la madera)
    m = principled('Acrílico', (0.97, 0.98, 0.99, 1), 0.12, coat=0.6)
    m.node_tree.nodes['Principled BSDF'].inputs['Alpha'].default_value = 0.45
    return m


MAT = {}


def materiales():
    MAT.update({
        'capri': mat_capri(),
        'duna': mat_duna(),
        'inox': principled('Inox', lin(205, 205, 207), 0.28, 1.0, aniso=0.5),
        'alu': principled('Aluminio', lin(222, 220, 214), 0.36, 1.0),
        'sombra': principled('Sombra', lin(70, 62, 56), 0.9),
        'led': mat_emisivo('LED 3000K', (1.0, 0.55, 0.24, 1), 22),
        'vidrio': mat_vidrio(),
        'blanco': principled('Checkpoint', lin(240, 239, 236), 0.3, coat=0.4),
        'logo': mat_imagen_alfa('Logo platino', LOGO, metal=0.85, rugosidad=0.26),
        'muro': principled('Muro', lin(226, 217, 203), 0.9),
        'techo': principled('Techo', lin(246, 244, 240), 0.9),
        'mostrador': principled('Mostrador', lin(246, 245, 242), 0.12, coat=0.5),
    })
    # piso porcelanato claro 60 × 60
    m, n, l, b = _mat('Piso')
    tc = n.new('ShaderNodeTexCoord')
    br = n.new('ShaderNodeTexBrick')
    br.inputs['Scale'].default_value = 1 / 0.6
    br.inputs['Mortar Size'].default_value = 0.004
    br.inputs['Color1'].default_value = lin(186, 175, 160)
    br.inputs['Color2'].default_value = lin(191, 180, 165)
    br.inputs['Mortar'].default_value = lin(160, 150, 137)
    br.offset = 0.0
    l.new(tc.outputs['Object'], br.inputs['Vector'])
    l.new(br.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.28
    MAT['piso'] = m


# ------------------------------------------------------------------ geometría

def caja(nombre, w, h, d, centro, mat, bisel=0.0):
    """Caja en coordenadas de la web: w ancho (X), h alto (Y), d fondo (Z); centro (x, y, z)."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=B(*centro))
    o = bpy.context.object
    o.name = nombre
    o.scale = (w, d, h)
    bpy.ops.object.transform_apply(scale=True)
    if bisel:
        mod = o.modifiers.new('bisel', 'BEVEL')
        mod.width = bisel
        mod.segments = 6
        mod.limit_method = 'ANGLE'
    o.data.materials.append(mat)
    return o


def plano(nombre, w, h, centro, mat, normal='Y-'):
    bpy.ops.mesh.primitive_plane_add(size=1, location=B(*centro))
    o = bpy.context.object
    o.name = nombre
    o.scale = (w, h, 1)
    o.rotation_euler = (math.radians(90), 0, 0) if normal == 'Y-' else (0, 0, 0)
    o.data.materials.append(mat)
    return o


def importar(glb, desplazamiento=(0, 0, 0)):
    antes = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=glb)
    nuevos = [o for o in bpy.data.objects if o not in antes]
    raiz = bpy.data.objects.new(os.path.basename(glb), None)
    bpy.context.scene.collection.objects.link(raiz)
    for o in nuevos:
        if o.parent is None:
            o.parent = raiz
    raiz.location = B(*desplazamiento)
    for o in nuevos:
        if o.type != 'MESH':
            continue
        for i, slot in enumerate(o.material_slots):
            mt = slot.material
            if mt is None:
                continue
            nom = mt.name
            img = next((nd.image for nd in mt.node_tree.nodes if nd.type == 'TEX_IMAGE'), None) if mt.use_nodes else None
            if nom.startswith('Capri'):
                o.material_slots[i].material = MAT['capri']
            elif nom.startswith('Duna'):
                o.material_slots[i].material = MAT['duna']
            elif nom.startswith('Inox'):
                o.material_slots[i].material = MAT['inox']
            elif nom.startswith('Aluminio'):
                o.material_slots[i].material = MAT['alu']
            elif nom.startswith('Línea de sombra'):
                o.material_slots[i].material = MAT['sombra']
            elif nom.startswith('LED'):
                o.material_slots[i].material = MAT['led']
            elif nom.startswith('Acrílico'):
                o.material_slots[i].material = MAT['vidrio']
            elif nom.startswith('Logo platino'):
                o.material_slots[i].material = MAT['logo']
            elif nom.startswith('Halo') and img:
                o.material_slots[i].material = mat_halo(img)
            elif nom.startswith('Tela backlight') and img:
                o.material_slots[i].material = mat_arte(img)
        o.data.shade_flat() if hasattr(o.data, 'shade_flat') else None
    return raiz, nuevos


_cache_prod = {}


def producto(nombre, alto, pos, camara, base=None):
    """Foto real del producto (recorte PNG) en una tarjeta vertical orientada hacia la cámara."""
    ruta = os.path.join(PROD, nombre + '.png')
    if nombre not in _cache_prod:
        img = bpy.data.images.load(ruta)
        _cache_prod[nombre] = (img, mat_imagen_alfa('prod-' + nombre, img, rugosidad=0.45))
    img, mat = _cache_prod[nombre]
    w = alto * img.size[0] / img.size[1]
    x, y, z = pos
    y0 = y
    if base == 'checkpoint':
        bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.014, vertices=40, location=B(x, y + 0.007, z))
        bpy.context.object.data.materials.append(MAT['blanco'])
        bpy.ops.mesh.primitive_cylinder_add(radius=0.007, depth=0.05, vertices=20, location=B(x, y + 0.035, z))
        bpy.context.object.data.materials.append(MAT['blanco'])
        y0 = y + 0.03
    bpy.ops.mesh.primitive_plane_add(size=1, location=B(x, y0 + alto / 2, z))
    o = bpy.context.object
    o.scale = (w, alto, 1)
    d = (camara - o.location)
    o.rotation_euler = (math.radians(90), 0, math.atan2(d.x, -d.y))
    o.data.materials.append(mat)
    return o


def logo_plano(ancho, centro, lado):
    """Logo oficial (PNG) a 15 mm del Capri + halo cálido detrás; lado ±1 = lateral derecho/izquierdo (eje X)."""
    img = bpy.data.images.load(LOGO) if 'logo-halo' not in bpy.data.images else bpy.data.images['logo-halo']
    alto = ancho * img.size[1] / img.size[0]
    x, y, z = centro
    for nom, esc, sep, mat in (('halo', 1.22, 0.002, None), ('letras', 1.0, 0.014, MAT['logo'])):
        bpy.ops.mesh.primitive_plane_add(size=1, location=B(x + lado * sep, y, z))
        o = bpy.context.object
        o.scale = (ancho * esc, alto * (1 + (esc - 1) * 2.6), 1)
        o.rotation_euler = (math.radians(90), 0, math.radians(90) * lado)
        o.data.materials.append(mat if mat else mat_halo(_imagen_halo()))


def _imagen_halo():
    if 'halo-logo' in bpy.data.images:
        return bpy.data.images['halo-logo']
    from PIL import Image, ImageFilter
    import numpy as np
    logo = Image.open(LOGO).convert('RGBA')
    logo.thumbnail((1024, 1024))
    W, H = logo.size
    lienzo = Image.new('L', (int(W * 1.22), int(H * (1 + 0.22 * 2.6))), 0)
    lienzo.paste(logo.getchannel('A'), ((lienzo.width - W) // 2, (lienzo.height - H) // 2))
    alfa = lienzo.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(H * 0.16)).point(lambda v: min(255, int(v * 1.6)))
    a = np.asarray(alfa, np.float32)[::-1] / 255
    img = bpy.data.images.new('halo-logo', alfa.width, alfa.height, alpha=True)
    px = np.zeros((alfa.height, alfa.width, 4), np.float32)
    px[..., 0], px[..., 1], px[..., 2], px[..., 3] = 1, 0.55, 0.25, a
    img.pixels = px.ravel()
    return img


def luz_area(nombre, centro, tam, potencia, color=(1, 0.93, 0.85), apunta=None, forma='RECTANGLE'):
    datos = bpy.data.lights.new(nombre, 'AREA')
    datos.shape = forma
    datos.size, datos.size_y = tam
    datos.energy = potencia
    datos.color = color
    o = bpy.data.objects.new(nombre, datos)
    bpy.context.scene.collection.objects.link(o)
    o.location = B(*centro)
    if apunta is not None:
        d = B(*apunta) - o.location
        o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return o


# ------------------------------------------------------------------ piezas

MESA_PRODUCTOS = [
    ('power-pro-2', 0.13, (-0.197, 0.838, -0.128), None), ('power-plus-2', 0.2, (0.0345, 0.838, -0.149), None),
    ('power-go-2', 0.09, (0.175, 0.838, -0.149), None), ('power-mini', 0.085, (0.2865, 0.838, -0.149), None),
    ('power-buds-2', 0.07, (-0.277, 0.788, 0.034), None), ('power-anc-negro', 0.2, (0.277, 0.788, 0.052), None),
    ('viva-pro-2', 0.075, (-0.2165, 0.788, 0.1445), 'checkpoint'), ('viva-2-rosado', 0.075, (-0.0865, 0.788, 0.1445), 'checkpoint'),
    ('aura-pro-2', 0.075, (0.0525, 0.788, 0.1445), 'checkpoint'), ('terra-verde', 0.075, (0.2035, 0.788, 0.1445), 'checkpoint'),
]
RELOJES_A = ['viva-pro-2', 'viva-2-rosado', 'viva-lite-lilac', 'aura-2-azul', 'aura-pro-2', 'terra-verde', 'viva-pro-2', 'aura-pro-2']
RELOJES_B = ['terra-verde', 'aura-pro-2', 'aura-2-azul', 'viva-lite-lilac', 'viva-2-rosado', 'viva-pro-2', 'terra-verde', 'viva-pro-2']


def mueble_productos(relojes):
    xs = [-0.5305, -0.4005, -0.2615, -0.1105, 0.0355, 0.1655, 0.3045, 0.4555]
    lista = [(relojes[i], 0.075, (x, 0.788, 0.0725), 'checkpoint') for i, x in enumerate(xs)]
    return lista + [('power-anc-negro', 0.2, (-0.444, 0.838, -0.0675), None), ('power-buds-2', 0.07, (-0.281, 0.838, -0.1055), None),
                    ('power-pro-2', 0.13, (0.029, 0.838, -0.1005), None), ('power-plus-2', 0.2, (0.211, 0.838, -0.0795), None),
                    ('power-go-2', 0.09, (0.352, 0.838, -0.08), None), ('power-mini', 0.085, (0.463, 0.838, -0.08), None)]


def poner_productos(lista, desplazamiento, camara):
    dx, dy, dz = desplazamiento
    for nom, alto, (x, y, z), base in lista:
        producto(nom, alto, (x + dx, y + dy, z + dz), camara, base)


def luces_led_mesa(o, ancho, fondo, y=0.765):
    """Luz real de la cinta 3000K bajo el tope (además del material emisivo)."""
    ox, oy, oz = o
    for z in (fondo / 2 + 0.01, -fondo / 2 - 0.01):
        luz_area('led', (ox, oy + y - 0.004, oz + z), (ancho, 0.01), 18 * ancho, (1, 0.62, 0.34), apunta=(ox, oy, oz + z * 3))
    for x in (ancho / 2 + 0.01, -ancho / 2 - 0.01):
        l = luz_area('led', (ox + x, oy + y - 0.004, oz), (fondo, 0.01), 18 * fondo, (1, 0.62, 0.34), apunta=(ox + x * 3, oy, oz))


def mesa(o=(0, 0, 0), camara=None, productos=True, glb_dir=''):
    raiz, objs = importar(os.path.join(glb_dir, 'mesa.glb'), o)
    luces_led_mesa(o, 0.72, 0.44)
    luz_area('caja-mesa', (o[0], o[1] + 0.40, o[2] + 0.30), (0.6, 0.5), 25, (0.95, 0.97, 1.0), apunta=(o[0], o[1] + 0.1, o[2] + 1.5))
    if productos:
        poner_productos(MESA_PRODUCTOS, o, camara)
    return raiz, objs


def composicion(o=(0, 0, -1.75), camara=None, glb_dir='', dos=True):
    raiz, objs = importar(os.path.join(glb_dir, 'mueble2.glb' if dos else 'mueble.glb'), o)
    mods = [(-0.6, RELOJES_A), (0.6, RELOJES_B)] if dos else [(0.0, RELOJES_A)]
    for dx, rel in mods:
        p = (o[0] + dx, o[1], o[2])
        luces_led_mesa(p, 1.1, 0.339)
        luz_area('caja-mueble', (p[0], p[1] + 1.16, p[2] + 0.15), (1.0, 0.5), 30, (0.95, 0.97, 1.0), apunta=(p[0], p[1] + 0.8, p[2] + 1.5))
        poner_productos(mueble_productos(rel), p, camara)
    return raiz, objs


def sobremesa(o, camara):
    """Display de sobremesa 50 × 30 × 25 cm: base Capri con LED, plataforma Duna, caja de luz Viva Pro 2,
    tres checkpoints, riel inox y logo platino en el frente de la base (sin banda superior)."""
    x, y, z = o
    caja('sob-base', 0.5, 0.035, 0.25, (x, y + 0.0175, z), MAT['capri'], 0.012)
    caja('sob-led', 0.46, 0.004, 0.004, (x, y + 0.037, z + 0.118), MAT['led'])
    caja('sob-duna', 0.5, 0.045, 0.25, (x, y + 0.0595, z), MAT['duna'], 0.012)
    caja('sob-marco', 0.48, 0.2, 0.03, (x, y + 0.19, z - 0.105), MAT['alu'], 0.03)
    tela = plano('sob-tela', 0.436, 0.156, (x, y + 0.19, z - 0.0895), mat_arte(bpy.data.images.load(os.path.join(TALLA, 'sobremesa-viva-pro-2.jpg')), 2.2))
    caja('sob-riel', 0.46, 0.022, 0.006, (x, y + 0.06, z + 0.128), MAT['inox'], 0.002)
    luz_area('sob-led', (x, y + 0.033, z + 0.13), (0.46, 0.01), 6, (1, 0.62, 0.34), apunta=(x, y - 0.2, z + 0.4))
    luz_area('sob-caja', (x, y + 0.19, z + 0.05), (0.4, 0.15), 6, (0.95, 0.97, 1.0), apunta=(x, y + 0.19, z + 1))
    for i, n in enumerate(['viva-pro-2', 'viva-2-rosado', 'viva-lite-lilac']):
        producto(n, 0.07, (x - 0.15 + i * 0.15, y + 0.082, z + 0.02), camara, 'checkpoint')
    logo = bpy.data.images.load(LOGO)
    ancho = 0.12
    alto = ancho * logo.size[1] / logo.size[0]
    bpy.ops.mesh.primitive_plane_add(size=1, location=B(x, y + 0.0175, z + 0.1265))
    p = bpy.context.object
    p.scale = (ancho, alto, 1)
    p.rotation_euler = (math.radians(90), 0, 0)
    p.data.materials.append(MAT['logo'])


def repisas(x0, x1, z_muro, camara):
    """Repisas Duna flotantes en el muro con productos Cubitt (contexto de tienda, fuera del foco)."""
    surtido = ['termo-burgandy', 'tumbler-lila', 'coffee-mug-verde', 'power-anc-crema', 'mug-jr-azul', 'hydro-bottle-jr-rapunzel']
    ancho = x1 - x0
    for k, y in enumerate((1.05, 1.42, 1.79)):
        caja('repisa', ancho, 0.03, 0.26, ((x0 + x1) / 2, y, z_muro + 0.13), MAT['duna'], 0.004)
        caja('repisa-led', ancho - 0.04, 0.004, 0.004, ((x0 + x1) / 2, y - 0.017, z_muro + 0.24), MAT['led'])
        n = max(2, int(ancho / 0.32))
        for i in range(n):
            nom = surtido[(i + k * 2) % len(surtido)]
            alto = 0.17 if nom.startswith('power-anc') else 0.2 if 'termo' in nom or 'hydro' in nom or 'tumbler' in nom else 0.11
            producto(nom, alto, (x0 + ancho * (i + 0.5) / n, y + 0.015, z_muro + 0.13), camara)


def tienda(muro_z=-1.97, ancho=8.0, fondo=7.0, alto=3.0, con_muro=True, x_muro=4.0, frente=None):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
    piso = bpy.context.object
    piso.scale = (ancho * 2, fondo * 2, 1)
    piso.data.materials.append(MAT['piso'])
    if con_muro:
        plano('muro', ancho * 2, alto, (0, alto / 2, muro_z), MAT['muro'])
        caja('guardaescoba', ancho * 2, 0.08, 0.012, (0, 0.04, muro_z + 0.006), MAT['muro'])
    for lado in (-1, 1):
        o = plano('muro-lateral', fondo * 2, alto, (lado * x_muro, alto / 2, 0), MAT['muro'])
        o.rotation_euler = (math.radians(90), 0, math.radians(90))
    if frente is not None:
        o = plano('muro-frente', ancho * 2, alto, (0, alto / 2, frente), MAT['muro'])
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, alto))
    t = bpy.context.object
    t.scale = (ancho * 2, fondo * 2, 1)
    t.rotation_euler = (math.radians(180), 0, 0)
    t.data.materials.append(MAT['techo'])
    # luminarias de techo (luz difusa neutra-cálida) y relleno general
    for x in (-2.0, 0.0, 2.0):
        for z in (-1.2, 0.8, 2.6):
            luz_area('techo', (x, alto - 0.02, z), (1.2, 1.2), 16, (1, 0.93, 0.84), apunta=(x, 0, z))
    mundo((0.92, 0.88, 0.82, 1), 0.05)
    # luz principal suave desde arriba a la izquierda, para dar volumen y sombras
    luz_area('principal', (-2.2, 2.6, 2.4), (2.0, 2.0), 220, (1, 0.95, 0.88), apunta=(0, 0.6, -0.4))


def mundo(color, fuerza):
    e = bpy.context.scene
    if e.world is None:
        e.world = bpy.data.worlds.new('mundo')
    w = e.world
    w.use_nodes = True
    w.node_tree.nodes['Background'].inputs['Color'].default_value = color
    w.node_tree.nodes['Background'].inputs['Strength'].default_value = fuerza


def camara(pos, objetivo, lente=35, f=None, ortho=None):
    datos = bpy.data.cameras.new('cam')
    datos.lens = lente
    datos.sensor_width = 36
    if ortho:
        datos.type = 'ORTHO'
        datos.ortho_scale = ortho
    o = bpy.data.objects.new('cam', datos)
    bpy.context.scene.collection.objects.link(o)
    o.location = B(*pos)
    d = B(*objetivo) - o.location
    o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    if f:
        datos.dof.use_dof = True
        datos.dof.focus_distance = d.length
        datos.dof.aperture_fstop = f
    bpy.context.scene.camera = o
    return o.location.copy()


def ajustes(ancho, alto, muestras):
    e = bpy.context.scene
    e.render.engine = 'CYCLES'
    e.cycles.device = 'CPU'
    e.cycles.samples = muestras
    e.cycles.use_adaptive_sampling = True
    e.cycles.adaptive_threshold = 0.02
    e.cycles.use_denoising = True
    e.cycles.denoiser = 'OPENIMAGEDENOISE'
    e.cycles.max_bounces = 8
    e.cycles.caustics_reflective = False
    e.cycles.caustics_refractive = False
    e.cycles.sample_clamp_indirect = 8
    e.render.resolution_x, e.render.resolution_y = ancho, alto
    e.render.resolution_percentage = 100
    e.render.image_settings.file_format = 'JPEG'
    e.render.image_settings.quality = 92
    e.view_settings.view_transform = 'AgX'
    for look in ('AgX - Medium High Contrast', 'Medium High Contrast'):
        try:
            e.view_settings.look = look
            break
        except TypeError:
            continue
    e.view_settings.exposure = 0.0


# ------------------------------------------------------------------ escenas

def nueva():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _cache_prod.clear()
    MAT.clear()
    materiales()


def escena(nombre, glb):
    nueva()
    W, H = 1920, 1080
    if nombre == 'familia':
        tienda()
        cam = camara((2.15, 1.5, 2.55), (-0.2, 0.85, -0.9), 28, f=11)
        repisas(-3.4, -1.55, -1.97, cam)
        repisas(1.55, 3.4, -1.97, cam)
        mesa((0, 0, 0), cam, glb_dir=glb)
        composicion((0, 0, -1.75), cam, glb)
    elif nombre == 'mesa':
        tienda()
        cam = camara((1.5, 1.3, 1.8), (0, 0.55, 0), 40, f=5.6)
        repisas(-3.4, -1.55, -1.97, cam)
        repisas(1.55, 3.4, -1.97, cam)
        mesa((0, 0, 0), cam, glb_dir=glb)
        composicion((0, 0, -1.75), cam, glb)
    elif nombre == 'touch':
        tienda()
        cam = camara((0.55, 1.33, 1.2), (-0.02, 0.78, 0.0), 32, f=2.8)
        repisas(-3.4, -1.55, -1.97, cam)
        repisas(1.55, 3.4, -1.97, cam)
        mesa((0, 0, 0), cam, glb_dir=glb)
        composicion((0, 0, -1.75), cam, glb)
    elif nombre == 'vendedor':
        tienda(muro_z=-4.0, frente=3.0)
        cam = camara((-1.2, 1.15, -1.5), (0, 0.45, -0.05), 35, f=8)
        repisas(-1.6, 1.6, 2.97, cam)
        mesa((0, 0, 0), cam, glb_dir=glb)
    elif nombre == 'mueble':
        W, H = 1600, 1200
        tienda(muro_z=-0.215, x_muro=3.0)
        cam = camara((1.05, 1.3, 1.6), (0.0, 0.9, -0.05), 35, f=8)
        composicion((0, 0, 0), cam, glb, dos=False)
    elif nombre == 'modular':
        tienda(muro_z=-0.215, x_muro=3.0)
        cam = camara((0.7, 1.32, 2.85), (0, 0.9, -0.05), 32, f=8)
        composicion((0, 0, 0), cam, glb)
    elif nombre == 'sobremesa':
        W, H = 1600, 1200
        tienda(muro_z=-1.5)
        caja('mostrador', 1.4, 0.9, 0.6, (0, 0.45, 0), MAT['mostrador'], 0.02)
        cam = camara((0.42, 1.18, 0.72), (0, 0.98, 0), 50, f=4)
        sobremesa((0, 0.9, 0), cam)
    elif nombre == 'logo':
        tienda()
        cam = camara((1.2, 0.78, 0.58), (0.40, 0.56, -0.02), 40, f=4)
        mesa((0, 0, 0), cam, glb_dir=glb)
        composicion((0, 0, -1.75), cam, glb)
    elif nombre == 'material':
        tienda()
        cam = camara((0.8, 0.98, 0.66), (0.37, 0.74, 0.21), 50, f=3.5)
        mesa((0, 0, 0), cam, glb_dir=glb)
        composicion((0, 0, -1.75), cam, glb)
    elif nombre == 'despiece':
        return despiece(glb)
    return W, H


def despiece(glb):
    """Despiece de la mesa: capas separadas en vertical sobre fondo cálido; las etiquetas se dibujan después."""
    piso = principled('Fondo', lin(244, 240, 233), 0.9)
    bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, -0.3))
    bpy.context.object.data.materials.append(piso)
    mundo((0.95, 0.93, 0.89, 1), 0.9)
    raiz, objs = importar(os.path.join(glb, 'mesa.glb'))
    import bmesh
    capas = {}
    for o in objs:
        if o.type != 'MESH':
            continue
        nom = o.material_slots[0].material.name if o.material_slots and o.material_slots[0].material else ''
        if nom.startswith('Duna') or nom.startswith('Inox'):
            # separar tope / elevador (Duna) y zócalo / riel (inox) por partes sueltas
            bpy.ops.object.select_all(action='DESELECT')
            o.select_set(True)
            bpy.context.view_layer.objects.active = o
            bpy.ops.mesh.separate(type='LOOSE')
    for o in [o for o in raiz.children_recursive if o.type == 'MESH']:
        nom = o.material_slots[0].material.name if o.material_slots and o.material_slots[0].material else ''
        zmin = min((o.matrix_world @ v.co).z for v in o.data.vertices)
        if nom.startswith('Inox'):
            capa = 'zocalo' if zmin < 0.2 else 'elevador'
        elif nom.startswith('Duna'):
            capa = 'tope' if zmin < 0.785 else 'elevador'
        elif nom.startswith('Capri'):
            capa = 'cuerpo'
        elif nom.startswith('Aluminio') or nom.startswith('Tela'):
            capa = 'caja'
        elif nom.startswith('Sombra') or nom.startswith('LED'):
            capa = 'sombra'
        elif nom.startswith('Acrílico'):
            capa = 'acrilico'
        else:
            capa = 'logo'
        capas.setdefault(capa, []).append(o)
    sube = {'zocalo': -0.28, 'cuerpo': 0.0, 'caja': 0.0, 'sombra': 0.3, 'tope': 0.52, 'acrilico': 0.62, 'elevador': 0.78, 'logo': 0.0}
    for capa, lista in capas.items():
        for o in lista:
            o.location.z += sube[capa]
            if capa == 'caja':
                o.location.y -= 0.42
            if capa == 'logo':
                cx = sum((o.matrix_world @ v.co).x for v in o.data.vertices) / len(o.data.vertices)
                o.location.x += 0.3 if cx > 0 else -0.3
    luz_area('clave', (2.5, 3.5, 3.0), (3, 3), 900, (1, 0.96, 0.9), apunta=(0, 0.8, 0))
    luz_area('relleno', (-3, 2.0, 2.0), (3, 3), 350, (0.95, 0.97, 1), apunta=(0, 0.6, 0))
    cam_pos = camara((3.2, 2.2, 3.5), (0.45, 0.66, -0.15), 50, ortho=4.0)
    # muestra de puntos de cada capa (mundo) para ubicar las etiquetas después del render
    puntos = {}
    for capa, lista in capas.items():
        pts = [list(o.matrix_world @ v.co) for o in lista for v in o.data.vertices]
        paso = max(1, len(pts) // 400)
        puntos[capa] = pts[::paso]
    bpy.context.scene['anclas'] = json.dumps(puntos)
    return 1920, 1080


def etiquetas_despiece(salida):
    """Etiquetas con líneas guía, como la lámina anterior, sobre el render del despiece."""
    from bpy_extras.object_utils import world_to_camera_view
    from PIL import Image, ImageDraw, ImageFont
    e = bpy.context.scene
    anclas = json.loads(e['anclas'])
    im = Image.open(salida).convert('RGB')
    d = ImageDraw.Draw(im)
    fuente = '/usr/share/fonts/opentype/inter/Inter-Regular.otf'
    W, H = im.size
    f = ImageFont.truetype(fuente, int(W * 0.0125)) if os.path.exists(fuente) else ImageFont.load_default()
    ft = ImageFont.truetype(fuente.replace('Regular', 'Medium'), int(W * 0.015)) if os.path.exists(fuente) else f
    textos = [('elevador', 'Elevador Duna 72,7 × 14 × 5 cm con riel inox'), ('acrilico', 'Fichas acrílicas de precio'),
              ('tope', 'Tope Duna 18 mm · esquinas R40'), ('sombra', 'Línea de sombra con LED 3000K'),
              ('caja', 'Caja de luz 66 × 56 cm · aluminio + tela backlight 5000K'), ('logo', 'Logo Cubitt platino · halo 3000K'),
              ('cuerpo', 'Cuerpo recto Capri 80 × 50 × 70 cm · 2 puertas push atrás'), ('zocalo', 'Zócalo de acero inoxidable 5 cm')]
    xs = W * 0.64
    filas = [(k, t) for k, t in textos if k in anclas]
    pos = []
    for k, t in filas:
        pts = [world_to_camera_view(e, e.camera, Vector(p)) for p in anclas[k]]
        pts = [(p.x * W, (1 - p.y) * H) for p in pts]
        ys = sorted(p[1] for p in pts)
        y0, y1 = ys[len(ys) // 4], ys[3 * len(ys) // 4]
        medio = [p for p in pts if y0 <= p[1] <= y1] or pts
        px, py = max(medio, key=lambda p: p[0])  # borde derecho de la capa, a media altura
        pos.append((k, t, px, py))
    pos.sort(key=lambda r: r[3])
    paso = (H * 0.84) / max(1, len(pos))
    for i, (k, t, px, py) in enumerate(pos):
        ty = H * 0.08 + i * paso + paso / 2
        r = max(2, W // 400)
        d.line([(px, py), (xs - W * 0.008, ty)], fill=(150, 142, 132), width=max(1, W // 960))
        d.ellipse([px - r, py - r, px + r, py + r], fill=(150, 142, 132))
        d.text((xs, ty - W * 0.0075), f'{i + 1}  {t}', font=f, fill=(60, 56, 52))
    d.text((W * 0.04, H * 0.9), 'Mesa de experiencia · 80 × 79 × 50 cm', font=ft, fill=(60, 56, 52))
    im.save(salida, quality=92)


def versiones_web(ruta, carpeta):
    from PIL import Image
    nombre = os.path.splitext(os.path.basename(ruta))[0]
    im = Image.open(ruta).convert('RGB')
    grande = im.copy(); grande.thumbnail((2000, 2000), Image.LANCZOS)
    grande.save(os.path.join(carpeta, f'{nombre}.jpg'), quality=84, optimize=True, progressive=True)
    chico = im.copy(); chico.thumbnail((900, 900), Image.LANCZOS)
    chico.save(os.path.join(carpeta, f'{nombre}-900.jpg'), quality=80, optimize=True, progressive=True)


def main():
    opciones, args, it = {}, [], iter(sys.argv[1:])
    for a in it:
        if a.startswith('--'):
            opciones[a[2:]] = next(it)
        else:
            args.append(a)
    glb, salida = os.path.abspath(args[0]), os.path.abspath(args[1])
    nombres = args[2:] or ['familia', 'mesa', 'touch', 'vendedor', 'mueble', 'modular', 'sobremesa', 'logo', 'material', 'despiece']
    muestras = int(opciones.get('muestras', 128))
    escala = float(opciones.get('escala', 1.0))
    os.makedirs(salida, exist_ok=True)
    for nombre in nombres:
        W, H = escena(nombre, glb)
        ajustes(int(W * escala), int(H * escala), muestras)
        ruta = os.path.join(salida, f'{nombre}.jpg')
        bpy.context.scene.render.filepath = ruta
        bpy.ops.render.render(write_still=True)
        if nombre == 'despiece':
            etiquetas_despiece(ruta)
        if 'web' in opciones:
            versiones_web(ruta, os.path.abspath(opciones['web']))
        print('listo', nombre, flush=True)


if __name__ == '__main__':
    main()

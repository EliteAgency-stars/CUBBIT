"""Lector de archivos SketchUp 2021+ (.skp) sin SketchUp: geometría, materiales e instancias.

El .skp moderno es un zip (con unos bytes de cabecera) que trae model.dat en formato TLV
(etiqueta u16 + largo u32 + datos) y una carpeta materials/ con material.xml y texturas.
Estructura usada (etiquetas hex):
  01f9/1770/1771/157c  definiciones de componentes y grupos (157e nombre, 1388 entidades)
  01f6/1388            entidades del modelo raíz
  1388/1389/09c4       vértices (05dc/05de id, 09c5 = 3 doubles en pulgadas)
  1388/138a/0bb8       aristas (0bb9 / 0bba = ids de vértice)
  1388/138b/0dac       caras (07d0/07d1 material frontal, 0daf material posterior,
                       0dad plano, 0dae/1194/1195/0fa0 lazos de usos de arista: 0fa1 arista, 0fa2 invertida)
  1388/138c, 138d      instancias y grupos (1964: 1966 = matriz 3x3 por filas + traslación + escala,
                       1967 = id de la definición, 07d0/07d1 material heredado)
  01f7/30d4/30d5/32c8  materiales (05de id, 32cc nombre -> materials/<nombre>/material.xml)

Uso: python tools/skp_lector.py archivo.skp     (imprime el resumen por grupo, en cm)
Requiere numpy y mapbox_earcut.
"""
import io, os, re, struct, sys, zipfile
import numpy as np
import mapbox_earcut as earcut

class SKP:
    def __init__(self, path):
        self.d = open(path, 'rb').read()
    def items(self, off, end):
        d = self.d; out = []
        while off < end:
            if off + 6 > end: return None
            tag, ln = struct.unpack_from('<HI', d, off)
            if off + 6 + ln > end: return None
            out.append((tag, off + 6, ln)); off += 6 + ln
        return out
    def kids(self, node, tag=None):
        t, o, l = node
        it = self.items(o, o + l) or []
        return [x for x in it if tag is None or x[0] == tag]
    def kid(self, node, tag):
        k = self.kids(node, tag)
        return k[0] if k else None
    def raw(self, node):
        t, o, l = node
        return self.d[o:o + l]
    def path(self, node, *tags):
        for t in tags:
            node = self.kid(node, t)
            if node is None: return None
        return node
    def root(self):
        top = self.items(0, len(self.d))[0]
        return top

def ident(b):
    return int.from_bytes(b, 'little')



def leer_materiales(s, top, carpeta):
    mats = {}
    for m in s.kids(s.path(top, 0x1f7, 0x30d4, 0x30d5), 0x32c8):
        mid = ident(s.raw(s.path(m, 0x5dc, 0x5de)))
        nombre = s.raw(s.kid(m, 0x32cc)).decode('utf-8', 'replace')
        info = {'nombre': nombre, 'color': (200, 200, 200), 'textura': None, 'escala': (1, 1), 'alfa': 1.0}
        xml = os.path.join(carpeta, 'materials', nombre, 'material.xml')
        if os.path.exists(xml):
            t = open(xml, encoding='utf-8', errors='replace').read()
            g = lambda k: re.search(k + r'="([^"]*)"', t)
            info['color'] = tuple(int(g(c).group(1)) for c in ('colorRed', 'colorGreen', 'colorBlue'))
            if g('useTrans') and g('useTrans').group(1) == '1':
                info['alfa'] = float(g('trans').group(1))
            img = re.search(r'path="\./([^"]+)"', t)
            if img:
                info['textura'] = os.path.join(carpeta, 'materials', nombre, img.group(1))
                info['escala'] = (float(g('xScale').group(1)), float(g('yScale').group(1)))
        mats[mid] = info
    return mats


def leer_entidades(s, cuerpo):
    """Vértices, aristas, caras e instancias de un bloque 1388."""
    V, E, F, I = {}, {}, [], []
    n = s.kid(cuerpo, 0x1389)
    for v in (s.kids(n, 0x9c4) if n else []):
        V[ident(s.raw(s.path(v, 0x5dc, 0x5de)))] = struct.unpack('<3d', s.raw(s.kid(v, 0x9c5)))
    n = s.kid(cuerpo, 0x138a)
    for e in (s.kids(n, 0xbb8) if n else []):
        E[ident(s.raw(s.path(e, 0x7d0, 0x5dc, 0x5de)))] = (ident(s.raw(s.kid(e, 0xbb9))), ident(s.raw(s.kid(e, 0xbba))))
    n = s.kid(cuerpo, 0x138b)
    for f in (s.kids(n, 0xdac) if n else []):
        plano = struct.unpack('<4d', s.raw(s.kid(f, 0xdad)))
        mf = s.path(f, 0x7d0, 0x7d1)  # material de la cara frontal
        mb = s.kid(f, 0xdaf)  # material de la cara posterior
        lazos = []
        for lz in s.kids(s.kid(f, 0xdae), 0x1194):
            usos = []
            for u in s.kids(s.kid(lz, 0x1195), 0xfa0):
                usos.append((ident(s.raw(s.kid(u, 0xfa1))), s.raw(s.kid(u, 0xfa2)) == b'\x01'))
            lazos.append(usos)
        F.append({'id': ident(s.raw(s.path(f, 0x7d0, 0x5dc, 0x5de))), 'plano': plano, 'lazos': lazos,
                  'mat': ident(s.raw(mf)) if mf else None, 'matb': ident(s.raw(mb)) if mb else None})
    for tag in (0x138c, 0x138d):
        n = s.kid(cuerpo, tag)
        if not n:
            continue
        for x in s.kids(n):
            inst = x if x[0] == 0x1964 else s.kid(x, 0x1964)
            if not inst:
                continue
            t = struct.unpack('<13d', s.raw(s.kid(inst, 0x1966)))
            ref = ident(s.raw(s.kid(inst, 0x1967)))
            mat = s.path(inst, 0x7d0, 0x7d1)
            I.append({'ref': ref, 't': t, 'grupo': tag == 0x138d, 'mat': ident(s.raw(mat)) if mat else None,
                      'tags': [hex(c[0]) for c in s.kids(inst)]})
    return V, E, F, I


def matriz(t):
    M = np.eye(4)
    M[0, :3] = t[0:3]  # la matriz 3x3 viene por filas
    M[1, :3] = t[3:6]
    M[2, :3] = t[6:9]
    M[:3, 3] = t[9:12]
    M /= t[12] if t[12] else 1
    M[3, 3] = 1
    return M


def lazo_vertices(lazo, E):
    pts = []
    for eid, rev in lazo:
        a, b = E[eid]
        pts.append(b if rev else a)
    return pts


def triangular(cara, V, E):
    n = np.array(cara['plano'][:3])
    lazos = [[np.array(V[v]) for v in lazo_vertices(l, E)] for l in cara['lazos']]
    if not lazos or len(lazos[0]) < 3:
        return None, None
    # base 2D del plano
    a = np.array([1.0, 0, 0]) if abs(n[0]) < 0.9 else np.array([0, 1.0, 0])
    u = np.cross(n, a); u /= np.linalg.norm(u)
    w = np.cross(n, u)
    todos = np.concatenate(lazos)
    p2 = np.stack([todos @ u, todos @ w], 1)
    cortes = np.cumsum([len(l) for l in lazos]).astype(np.uint32)
    try:
        tri = earcut.triangulate_float64(p2, cortes)
    except Exception:
        return None, None
    tri = np.array(tri, np.int64).reshape(-1, 3)
    return todos, tri


def extraer(skp, destino):
    """Descomprime el .skp (zip con cabecera) en destino y devuelve la carpeta."""
    datos = open(skp, 'rb').read()
    inicio = datos.find(b'PK')
    with zipfile.ZipFile(io.BytesIO(datos[inicio:])) as z:
        z.extractall(destino)
    return destino


class Modelo:
    def __init__(self, carpeta):
        self.carpeta = carpeta
        self.s = s = SKP(os.path.join(carpeta, 'model.dat'))
        top = s.root()
        self.mats = leer_materiales(s, top, carpeta)
        self.defs = {}
        for df in s.kids(s.path(top, 0x1f9, 0x1770, 0x1771), 0x157c):
            cuerpo = s.kid(df, 0x1388)
            did = ident(s.raw(s.path(cuerpo, 0x7d0, 0x5dc, 0x5de)))
            nombre = s.raw(s.kid(df, 0x157e)).decode('utf-8', 'replace')
            self.defs[did] = (nombre,) + leer_entidades(s, cuerpo)
        self.raiz = ('MODELO',) + leer_entidades(s, s.path(top, 0x1f6, 0x1388))

    def triangulos(self, defn=None, M=None, mat_heredado=None, ruta=(), salida=None, prof=0):
        """Lista de (ruta_de_nombres, material_id, cara_id, vértices Nx3 mundo, triángulos Kx3, normal)."""
        if salida is None:
            salida = []
        defn = defn or self.raiz
        M = np.eye(4) if M is None else M
        nombre, V, E, F, I = defn
        for c in F:
            pts, tri = triangular(c, V, E)
            if pts is None or len(tri) == 0:
                continue
            pw = (np.c_[pts, np.ones(len(pts))] @ M.T)[:, :3]
            nw = M[:3, :3] @ np.array(c['plano'][:3])
            nw /= np.linalg.norm(nw) or 1
            salida.append((ruta + (nombre,), c['mat'] if c['mat'] is not None else mat_heredado, c['id'], pw, tri, nw, c['matb'] if c['matb'] is not None else mat_heredado))
        for inst in I:
            sub = self.defs.get(inst['ref'])
            if sub is None or prof > 20:
                continue
            self.triangulos(sub, M @ matriz(inst['t']), inst['mat'] if inst['mat'] is not None else mat_heredado,
                            ruta + (nombre,), salida, prof + 1)
        return salida


if __name__ == '__main__':
    import tempfile
    carpeta = extraer(sys.argv[1], tempfile.mkdtemp())
    m = Modelo(carpeta)
    grupos = {}
    for ruta, mat, fid, pw, tri, nw, mb in m.triangulos():
        grupos.setdefault(ruta[1] if len(ruta) > 1 else ruta[0], []).append(pw)
    for k, v in grupos.items():
        p = np.concatenate(v) * 2.54
        print(f'{k:24s} caras={len(v):5d} min={p.min(0).round(1)} max={p.max(0).round(1)} cm')

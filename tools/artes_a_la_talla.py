"""Artes Cubitt «a la talla»: cada arte se rediagrama a la proporción exacta de su caja de luz.

Nada se estira ni se rellena con copias difuminadas. Cada pieza (logo, títulos, relojes, foto, sello VITA)
conserva su proporción y se reubica sobre el fondo real del arte:

- Nueva Era: se rearma desde el PDF vectorial «Backing Muebles 56.5x114 cm» (fondo plano). Horizontal
  sigue la diagramación horizontal oficial de Cubitt (títulos a la izquierda, logo y relojes a la derecha,
  sello VITA en la esquina); vertical sigue el backing.
- Viva Pro 2: se recorta la foto (las dos caras, el texto y los dos relojes siempre quedan) y a la izquierda
  continúa el degradado gris del propio arte; si la caja es muy ancha, el texto del arte pasa a ese panel.
- Terra y Aura Pro 2: artes verticales; solo se recorta el sobrante (sin tocar textos ni relojes).
- Rapunzel (Cubitt Jr.): fondo lila plano; el grupo reloj + botella se centra y el logo oficial va a la izquierda.

Uso: python tools/artes_a_la_talla.py <arte> <ancho/alto> <alto_px> salida.jpg
     python tools/artes_a_la_talla.py muestras    (genera muestras en varias proporciones)
Requiere Pillow, numpy, PyMuPDF y opencv-python.
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'propuesta-2027')
ORIG = os.path.join(RAIZ, 'artes-cubitt', 'originales')
LOGO_NEGRO = os.path.join(RAIZ, 'assets', 'logo', 'logo-cubitt-negro.png')
_cache = {}


def _rgb(path):
    if path not in _cache:
        _cache[path] = np.asarray(Image.open(path).convert('RGB')).astype(np.float32)
    return _cache[path]


def _escalar(img, s):
    h, w = img.shape[:2]
    nw, nh = max(1, round(w * s)), max(1, round(h * s))
    return cv2.resize(img, (nw, nh), interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC)


def _pegar(lienzo, pieza, alfa, x, y):
    """Pega pieza (RGB float) con alfa (0-1) en lienzo, recortando a los bordes."""
    H, W = lienzo.shape[:2]
    h, w = pieza.shape[:2]
    x, y = int(round(x)), int(round(y))
    x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    p = pieza[y0 - y:y1 - y, x0 - x:x1 - x]
    a = alfa[y0 - y:y1 - y, x0 - x:x1 - x, None]
    lienzo[y0:y1, x0:x1] = lienzo[y0:y1, x0:x1] * (1 - a) + p * a


# ---------------------------------------------------------------- Nueva Era (desde el PDF vectorial)

def _kit_nueva_era():
    if 'nueva_era' in _cache:
        return _cache['nueva_era']
    import pymupdf
    doc = pymupdf.open(os.path.join(ORIG, 'Backing Muebles 56.5x114 cm (1) (1).pdf'))
    z = 2.0
    pix = doc[0].get_pixmap(matrix=pymupdf.Matrix(z, z), colorspace=pymupdf.csRGB)
    a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3).astype(np.float32)
    fondo = a[8, 8].copy()
    dif = np.abs(a - fondo).max(2)
    # cajas en px del render a z=1.5 (medidas sobre el PDF) -> escala z
    k = z / 1.5
    cajas = {
        'logo': (860, 418, 1560, 588),
        'nueva': (712, 788, 1740, 1016),
        'era': (130, 1022, 2322, 1912),
        'relojes': (0, 2262, 2417, 3500),
        'tagline': (442, 3838, 1982, 3921),
        'modelos': (302, 3972, 2108, 4043),
        'vita': (1500, 4506, 2417, 4864),
    }
    kit = {'fondo': fondo}
    for n, (x0, y0, x1, y1) in cajas.items():
        x0, y0, x1, y1 = [int(round(v * k)) for v in (x0, y0, x1, y1)]
        alfa = np.clip((dif[y0:y1, x0:x1] - 1.5) / 10, 0, 1)
        kit[n] = (a[y0:y1, x0:x1], alfa)
    _cache['nueva_era'] = kit
    return kit


def nueva_era(R, H):
    kit = _kit_nueva_era()
    W = int(round(R * H))
    lienzo = np.empty((H, W, 3), np.float32)
    lienzo[:] = kit['fondo']
    tam = {n: kit[n][0].shape[1::-1] for n in kit if n != 'fondo'}  # (w, h)

    def poner(n, s, x, y):
        img, alfa = kit[n]
        _pegar(lienzo, _escalar(img, s), _escalar(alfa, s), x, y)

    if R >= 1.25:
        # Horizontal (como la versión horizontal oficial): títulos a la izquierda, logo sobre los relojes
        # a la derecha y el sello VITA a ras de la esquina inferior derecha.
        bloque_h = tam['nueva'][1] + 1.08 * tam['era'][1] + tam['tagline'][1] + 1.10 * tam['modelos'][1] + 0.08 * tam['era'][1]
        st = 0.68 * H / bloque_h
        sr = 0.60 * H / tam['relojes'][1]
        sv = 0.19 * H / tam['vita'][1]
        w_vita = sv * tam['vita'][0]
        contenido = st * tam['era'][0] + sr * tam['relojes'][0]
        disponible = W - 0.16 * H - 0.35 * w_vita
        if contenido > disponible:  # caja poco apaisada: se reduce el conjunto
            k = disponible / contenido
            st, sr, contenido = st * k, sr * k, contenido * k
        libre = W - contenido
        hueco = min(max(0.08 * H, 0.30 * libre), 0.9 * H)
        x_txt = (libre - hueco) * 0.42
        x_rel = x_txt + st * tam['era'][0] + hueco
        w_rel, h_rel = sr * tam['relojes'][0], sr * tam['relojes'][1]
        # el bloque de relojes no invade el sello VITA
        x_rel = min(x_rel, W - 0.35 * w_vita - w_rel)
        y = (H - st * bloque_h) / 2
        poner('nueva', st, x_txt + 0.025 * st * tam['era'][0], y)
        y += st * tam['nueva'][1] + 0.02 * st * tam['era'][1]
        poner('era', st, x_txt, y)
        y += 1.06 * st * tam['era'][1]
        poner('tagline', st, x_txt + 0.035 * st * tam['era'][0], y)
        y += st * tam['tagline'][1] + 0.05 * st * tam['era'][1]
        poner('modelos', st * 1.10 * tam['tagline'][0] / tam['modelos'][0] * 0.86, x_txt + 0.035 * st * tam['era'][0], y)
        sl = min(0.11 * H / tam['logo'][1], 0.40 * w_rel / tam['logo'][0])
        y_logo = 0.075 * H
        poner('logo', sl, x_rel + (w_rel - sl * tam['logo'][0]) / 2, y_logo)
        y_rel = min(H - h_rel - 0.05 * H, max(y_logo + sl * tam['logo'][1] + 0.015 * H, (H - h_rel) / 2 + 0.06 * H))
        poner('relojes', sr, x_rel, y_rel)
        poner('vita', sv, W - w_vita, H - sv * tam['vita'][1])
    else:
        # Vertical: la pila del backing; el alto que sobra o falta se reparte entre los espacios.
        k = 2.0 / 1.5
        ancho_b = 2417 * k
        s = W / ancho_b
        orden = ['logo', 'nueva', 'era', 'relojes', 'tagline', 'modelos']
        ys = {'logo': 418, 'nueva': 788, 'era': 1022, 'relojes': 2262, 'tagline': 3838, 'modelos': 3972}
        xs = {'logo': 860, 'nueva': 712, 'era': 130, 'relojes': 0, 'tagline': 442, 'modelos': 302}
        alto_b = 4864 * k
        esp, prev = [], 0
        for n in orden:
            esp.append(ys[n] * k - prev)
            prev = ys[n] * k + tam[n][1]
        vita_h = tam['vita'][1]
        esp.append(alto_b - prev - vita_h)
        esp = np.maximum(np.array(esp, np.float64), 0)
        contenido = sum(tam[n][1] for n in orden) + vita_h
        if H / s < contenido + 0.35 * esp.sum():  # caja más ancha que el backing: se reduce todo
            s = H / (contenido + 0.35 * esp.sum())
        esp = esp * (H / s - contenido) / esp.sum()
        x_off = (W - ancho_b * s) / 2
        y = 0
        for i, n in enumerate(orden):
            y += esp[i] * s
            poner(n, s, x_off + xs[n] * k * s, y)
            y += tam[n][1] * s
        poner('vita', s, W - s * tam['vita'][0], H - s * vita_h)
    return np.clip(lienzo, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- Viva Pro 2 (foto)

# Líneas de texto del arte Viva Pro 2 (fracciones del arte): isotipo, VIVA PRO 2, SMARTWATCH, lema.
_VIVA_TEXTO = [(0.208, 0.280, 0.316, 0.398), (0.077, 0.443, 0.446, 0.520), (0.150, 0.555, 0.3755, 0.592),
               (0.070, 0.673, 0.452, 0.704)]


def _viva_capas():
    """Foto Viva Pro 2 a 2200 px de ancho, separada en foto limpia (sin textos) y capa de texto blanco (alfa)."""
    if 'viva' in _cache:
        return _cache['viva']
    f = _rgb(os.path.join(ORIG, 'Cubitt_Viva Pro 58.6 x 43.80 cm.jpg'))
    a = cv2.resize(f, (2200, round(2200 * f.shape[0] / f.shape[1])), interpolation=cv2.INTER_AREA)
    h, w = a.shape[:2]
    caja = np.zeros((h, w), np.uint8)
    for x0, y0, x1, y1 in _VIVA_TEXTO:
        caja[int(y0 * h):int(y1 * h), int(x0 * w):int(x1 * w)] = 1
    mn = a.min(2)
    nucleo = ((mn > 222) & (caja > 0)).astype(np.uint8)
    region = cv2.dilate(nucleo, np.ones((11, 11), np.uint8))
    region = cv2.morphologyEx(region, cv2.MORPH_CLOSE, np.ones((31, 31), np.uint8)) & caja
    # relleno a 1/4 de resolución (suave, sin bloques) + grano de la foto
    q = 4
    chica = cv2.resize(a, (w // q, h // q), interpolation=cv2.INTER_AREA).clip(0, 255).astype(np.uint8)
    rc = (cv2.resize(region.astype(np.float32), (w // q, h // q), interpolation=cv2.INTER_AREA) > 0.02).astype(np.uint8)
    relleno = cv2.inpaint(chica, rc * 255, 6, cv2.INPAINT_TELEA)
    relleno = cv2.GaussianBlur(relleno, (0, 0), 1.5)
    relleno = cv2.resize(relleno, (w, h), interpolation=cv2.INTER_CUBIC).astype(np.float32)
    relleno += np.random.default_rng(7).normal(0, 2.2, relleno.shape).astype(np.float32)
    m = cv2.GaussianBlur(region.astype(np.float32), (0, 0), 2)[..., None]
    limpia = a * (1 - m) + relleno * m
    fondo = limpia.min(2)
    cerca = cv2.dilate(nucleo, np.ones((5, 5), np.uint8)) & caja
    alfa = np.clip((mn - fondo) / np.maximum(255 - fondo, 1), 0, 1) * cerca
    _cache['viva'] = (a, limpia, alfa)
    return _cache['viva']


def viva_pro_2(R, H):
    a, limpia, alfa = _viva_capas()
    fh, fw = a.shape[:2]
    W = int(round(R * H))
    y_min, y_max = 0.10, 0.885  # franja que siempre queda: cejas de ella a la base del reloj blanco
    r_foto = fw / fh
    if R <= r_foto * 1.04:
        cw = fh * R
        x0 = min(max(0, 0.5 * fw - cw / 2), fw - cw)
        rec = a[:, int(x0):int(x0 + cw)]
        return cv2.resize(rec, (W, H), interpolation=cv2.INTER_AREA).clip(0, 255).astype(np.uint8)
    if R <= r_foto / (y_max - y_min):
        ch = fw / R
        y0 = min(max(0, (y_min + y_max) / 2 * fh - ch / 2), fh - ch)
        rec = a[int(y0):int(round(y0 + ch))]
        return cv2.resize(rec, (W, H), interpolation=cv2.INTER_AREA).clip(0, 255).astype(np.uint8)
    y0, y1 = int(y_min * fh), int(y_max * fh)
    s = H / (y1 - y0)
    mover = R >= 2.3  # caja muy ancha: el texto del arte pasa al panel y la foto queda limpia
    base = limpia if mover else a
    franja = _escalar(base[y0:y1], s)[:H]
    wf = franja.shape[1]
    x_f = W - wf
    lienzo = np.zeros((H, W, 3), np.float32)
    lienzo[:, x_f:] = franja
    banda = franja[:, :max(4, int(0.012 * wf))].mean(1)
    banda = cv2.GaussianBlur(banda[None], (0, 0), sigmaX=H * 0.08)[0]
    panel = np.repeat(banda[:, None, :], x_f + 1, axis=1)
    lienzo[:, :x_f + 1] = panel
    # transición corta de la foto al panel: continúa el velo gris que el arte ya tiene a la izquierda
    ancho_f = int(0.06 * H)
    t = np.linspace(0, 1, ancho_f)[None, :, None]
    t = t * t * (3 - 2 * t)
    lienzo[:, x_f:x_f + ancho_f] = panel[:, :1] * (1 - t) + franja[:, :ancho_f] * t
    if mover:
        xs0 = int(min(b[0] for b in _VIVA_TEXTO) * fw) - 4
        xs1 = int(max(b[2] for b in _VIVA_TEXTO) * fw) + 4
        ys0 = int(min(b[1] for b in _VIVA_TEXTO) * fh) - 4
        ys1 = int(max(b[3] for b in _VIVA_TEXTO) * fh) + 4
        st = s * 1.12
        capa = _escalar(alfa[ys0:ys1, xs0:xs1], st)
        blanco = np.full(capa.shape + (3,), 255, np.float32)
        ancho_panel = x_f + 0.12 * wf
        x = (ancho_panel - capa.shape[1]) / 2
        _pegar(lienzo, blanco, capa, x, (H - capa.shape[0]) / 2)
    return lienzo.clip(0, 255).astype(np.uint8)


# ---------------------------------------------------------------- Terra y Aura Pro 2 (verticales)

def _vertical(path, R, H, cx=0.5, cy=0.5):
    foto = _rgb(path)
    fh, fw = foto.shape[:2]
    W = int(round(R * H))
    if R < fw / fh:
        cw = fh * R
        x0 = min(max(0, cx * fw - cw / 2), fw - cw)
        rec = foto[:, int(x0):int(round(x0 + cw))]
    else:
        ch = fw / R
        y0 = min(max(0, cy * fh - ch / 2), fh - ch)
        rec = foto[int(y0):int(round(y0 + ch))]
    return cv2.resize(rec, (W, H), interpolation=cv2.INTER_AREA).clip(0, 255).astype(np.uint8)


def terra(R, H):
    return _vertical(os.path.join(ORIG, 'Cubitt Terra 30.5x92 cm.jpg'), R, H, cx=0.5, cy=0.55)


def aura_pro_2(R, H):
    return _vertical(os.path.join(ORIG, 'Mueble_Lateral Aura Pro 40x76 cm.jpg'), R, H, cx=0.52, cy=0.55)


# ---------------------------------------------------------------- Rapunzel / Cubitt Jr.

def rapunzel(R, H):
    a = np.asarray(Image.open(os.path.join(ORIG, 'CTBJ-DDR6-2.png')).convert('RGB')).astype(np.float32)
    fondo = a[5, 5].copy()
    dif = np.abs(a - fondo).max(2)
    alfa = np.clip((dif - 2) / 14, 0, 1)
    W = int(round(R * H))
    lienzo = np.empty((H, W, 3), np.float32)
    lienzo[:] = fondo
    s = H / a.shape[0]
    grupo = _escalar(a, s)
    ga = _escalar(alfa, s)
    if R >= 2.2:
        # grupo a la derecha del centro, logo oficial a la izquierda
        xg = W * 0.60 - grupo.shape[1] / 2
        _pegar(lienzo, grupo, ga, xg, 0)
        logo = Image.open(LOGO_NEGRO).convert('RGBA')
        la = np.asarray(logo).astype(np.float32)
        la = _escalar(la, 0.15 * H / la.shape[0])
        xl = W * 0.31 - la.shape[1] / 2
        xl = min(xl, xg - la.shape[1] - 0.05 * H)
        _pegar(lienzo, la[..., :3], la[..., 3] / 255, xl, (H - la.shape[0]) / 2)
    else:
        _pegar(lienzo, grupo, ga, (W - grupo.shape[1]) / 2, 0)
    return lienzo.clip(0, 255).astype(np.uint8)


ARTES = {'nueva-era': nueva_era, 'viva-pro-2': viva_pro_2, 'terra': terra, 'aura-pro-2': aura_pro_2, 'rapunzel': rapunzel}


def generar(nombre, R, H):
    return ARTES[nombre](R, H)


if __name__ == '__main__':
    if sys.argv[1] == 'muestras':
        out = sys.argv[2] if len(sys.argv) > 2 else '.'
        for n, rs in (('nueva-era', (2.8, 4.5, 0.3, 0.45)), ('viva-pro-2', (3.1, 4.5)), ('terra', (0.29,)), ('aura-pro-2', (0.46,)), ('rapunzel', (4.5, 6.7))):
            for r in rs:
                Image.fromarray(generar(n, r, 600)).save(os.path.join(out, f'{n}-{r}.jpg'), quality=88)
    else:
        n, R, H, salida = sys.argv[1], float(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        Image.fromarray(generar(n, R, H)).save(salida, quality=92)

"""Compone los renders de Higgsfield con artes Cubitt «a la talla» y el logo oficial en platino.

Higgsfield deja cada caja de luz en verde croma (#00FF00) y el lugar del logo en una placa magenta (#FF00FF).
Este script, para cada render:
  1. separa cada caja de luz y cada placa (sin unir cajas vecinas) y ajusta sus cuatro bordes con rectas;
  2. calcula la proporción REAL del rectángulo visto en perspectiva (puntos de fuga + Zhang & He), así ni el
     arte ni el logo quedan estirados al proyectarlos;
  3. genera el arte exactamente a esa proporción (tools/artes_a_la_talla.py: nada estirado ni difuminado) y lo
     pega con homografía, conservando las sombras y brillos que el render tenía sobre la tela;
  4. pega el logo oficial platino sin deformarlo, con halo de contorno cálido 3000K sobre el Capri;
  5. limpia el reflejo verde que el croma dejaba en piso y muebles.

Uso: python3 componer_renders.py entrada.png salida.jpg arte0,arte1,... [dir_artes_salida]
     (artes en el orden de las cajas de izquierda a derecha: nueva-era, viva-pro-2, terra, aura-pro-2, rapunzel)
Imprime un JSON con las cajas, proporciones y artes usados.
"""
import json
import os
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import artes_a_la_talla  # noqa: E402

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'propuesta-2027')
LOGO = os.path.join(RAIZ, 'assets', 'logo', 'logo-cubitt-platino.png')
CALIDO = np.array([107, 180, 255], np.float32)  # BGR de una luz 3000K


# ------------------------------------------------------------------ detección

def mascaras(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    verde = cv2.inRange(hsv, (42, 110, 90), (78, 255, 255))
    magenta = cv2.inRange(hsv, (141, 130, 110), (159, 255, 255))
    return verde, magenta


def regiones(mask, area_min, k=5):
    """Componentes conectados con un cierre pequeño: cajas vecinas separadas por un marco no se unen."""
    cerrada = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (k, k)))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(cerrada)
    out = []
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] < area_min:
            continue
        zona = (lab == i).astype(np.uint8) * 255
        out.append((cuadrilatero(zona), cv2.bitwise_and(mask, zona), zona))
    return sorted(out, key=lambda r: r[0][:, 0].mean())


def _esquinas_aprox(hull):
    per = cv2.arcLength(hull, True)
    for f in np.linspace(0.01, 0.15, 29):
        ap = cv2.approxPolyDP(hull, f * per, True)
        if len(ap) == 4:
            return ap.reshape(4, 2).astype(np.float64)
    p = hull.reshape(-1, 2).astype(np.float64)
    s, d = p.sum(1), p[:, 0] - p[:, 1]
    return np.array([p[s.argmin()], p[d.argmax()], p[s.argmax()], p[d.argmin()]])


def _ordenar(pts):
    c = pts.mean(0)
    pts = pts[np.argsort(np.arctan2(pts[:, 1] - c[1], pts[:, 0] - c[0]))]
    pts = np.roll(pts, -int(np.argmin(pts.sum(1))), 0)
    if abs(pts[1, 1] - pts[0, 1]) > abs(pts[1, 0] - pts[0, 0]):
        pts = np.roll(pts, 1, 0)
    return pts


def cuadrilatero(zona):
    """Esquinas TL, TR, BR, BL: una recta ajustada a cada lado y sus cortes (las esquinas redondeadas
    de la caja no recortan el arte; la máscara real las respeta al pegar)."""
    cont = max(cv2.findContours(zona, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0], key=cv2.contourArea)
    ap = _ordenar(_esquinas_aprox(cv2.convexHull(cont)))
    pts = cont.reshape(-1, 2).astype(np.float64)
    lineas = []
    for i in range(4):
        a, b = ap[i], ap[(i + 1) % 4]
        L = np.linalg.norm(b - a)
        u = (b - a) / L
        t = (pts - a) @ u
        dist = np.abs((pts - a) @ np.array([-u[1], u[0]]))
        sel = pts[(t > 0.12 * L) & (t < 0.88 * L) & (dist < max(4, 0.04 * L))]
        if len(sel) < 10:
            lineas.append((a, u))
            continue
        vx, vy, x0, y0 = cv2.fitLine(sel.astype(np.float32), cv2.DIST_HUBER, 0, 0.01, 0.01).ravel()
        lineas.append((np.array([x0, y0]), np.array([vx, vy])))
    esq = []
    for i in range(4):
        (p1, d1), (p2, d2) = lineas[i - 1], lineas[i]
        try:
            s = np.linalg.solve(np.array([d1, -d2]).T, p2 - p1)
            esq.append(p1 + s[0] * d1)
        except np.linalg.LinAlgError:
            esq.append(ap[i])
    return np.array(esq, np.float32)


# ------------------------------------------------------------------ perspectiva

def _fuga(quad):
    """Punto de fuga de los lados superior e inferior (None si son casi paralelos)."""
    tl, tr, br, bl = [np.append(p, 1.0) for p in quad.astype(np.float64)]
    v = np.cross(np.cross(tl, tr), np.cross(bl, br))
    if abs(v[2]) < 1e-9 or np.linalg.norm(v[:2] / v[2]) > 1e6:
        return None
    return v[:2] / v[2]


def estimar_focal(img_wh, cajas, placas, defecto=2.0):
    """Focal (px) con dos planos verticales perpendiculares del mismo mueble: la caja de luz del frente y la
    placa del logo en el lateral. f² = -(v1-c)·(v2-c). Sin ese par, defecto × ancho (lente de producto)."""
    W, H = img_wh
    c = np.array([W / 2, H / 2])
    medidas = []
    for qp in placas:
        if not cajas:
            break
        qc = min(cajas, key=lambda q: np.linalg.norm(q.mean(0) - qp.mean(0)))
        v1, v2 = _fuga(qc), _fuga(qp)
        if v1 is None or v2 is None:
            continue
        a, b = v1 - c, v2 - c
        if np.sign(a[0]) == np.sign(b[0]):
            continue  # misma cara del mueble
        f2 = -(a @ b)
        if f2 > 0 and 0.8 * W < np.sqrt(f2) < 5 * W:
            medidas.append(np.sqrt(f2))
    return (float(np.median(medidas)) if medidas else defecto * W), bool(medidas)


def proporcion_real(quad, W, H, f):
    """Ancho/alto real del rectángulo proyectado (Zhang & He, 'Whiteboard scanning and image enhancement')."""
    c = np.array([W / 2, H / 2])
    tl, tr, br, bl = [np.append(np.asarray(p, np.float64) - c, 1.0) for p in quad]
    m1, m2, m3, m4 = tl, tr, bl, br
    k2 = np.dot(np.cross(m1, m4), m3) / np.dot(np.cross(m2, m4), m3)
    k3 = np.dot(np.cross(m1, m4), m2) / np.dot(np.cross(m3, m4), m2)
    n2, n3 = k2 * m2 - m1, k3 * m3 - m1
    return float(np.sqrt((n2[0] ** 2 + n2[1] ** 2 + (f * n2[2]) ** 2) / (n3[0] ** 2 + n3[1] ** 2 + (f * n3[2]) ** 2)))


def pegar(img, plano, quad, mask_real, sombreado=None):
    H, W = plano.shape[:2]
    src = np.array([[0, 0], [W - 1, 0], [W - 1, H - 1], [0, H - 1]], np.float32)
    M = cv2.getPerspectiveTransform(src, quad)
    warp = cv2.warpPerspective(plano, M, (img.shape[1], img.shape[0]), flags=cv2.INTER_LINEAR,
                               borderMode=cv2.BORDER_REPLICATE).astype(np.float32)
    if sombreado is not None:
        warp = warp * sombreado[..., None]
    m = cv2.dilate(mask_real, np.ones((3, 3), np.uint8))
    m = cv2.GaussianBlur(m, (0, 0), 0.8).astype(np.float32)[..., None] / 255
    return np.clip(img * (1 - m) + warp * m, 0, 255).astype(np.uint8)


def sombreado_tela(img, mask):
    """Variación de luz que el render dejó sobre la tela verde (sombras del marco, reflejos), suavizada."""
    v = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)[..., 2].astype(np.float32)
    sel = mask > 0
    if sel.sum() < 100:
        return None
    ref = np.median(v[sel])
    s = np.ones_like(v)
    s[sel] = v[sel] / max(ref, 1)
    s = cv2.GaussianBlur(s, (0, 0), 6)
    return np.clip(s, 0.86, 1.04) ** 0.8


# ------------------------------------------------------------------ logo

def placa_logo(logo_rgba, ancho, alto, color):
    """Placa del color del panel con el logo platino (sin deformar) y halo de contorno cálido 3000K."""
    W, H = int(round(ancho)), int(round(alto))
    lh, lw = logo_rgba.shape[:2]
    esc = min(W * 0.84 / lw, H * 0.62 / lh)
    l = cv2.resize(logo_rgba, (max(1, int(lw * esc)), max(1, int(lh * esc))), interpolation=cv2.INTER_AREA).astype(np.float32)
    y, x = (H - l.shape[0]) // 2, (W - l.shape[1]) // 2
    a = np.zeros((H, W), np.float32)
    a[y:y + l.shape[0], x:x + l.shape[1]] = l[:, :, 3] / 255
    rgb = np.zeros((H, W, 3), np.float32)
    rgb[y:y + l.shape[0], x:x + l.shape[1]] = l[:, :, :3]
    alto_letra = max(2.0, l.shape[0])
    placa = np.full((H, W, 3), color, np.float32)
    # luz que sale por detrás de las letras (separadores de 15 mm) y baña el Capri: halo amplio + contorno intenso
    halo = cv2.GaussianBlur(a, (0, 0), alto_letra * 0.16)
    halo /= max(halo.max(), 1e-6)
    contorno = cv2.GaussianBlur(cv2.dilate(a, np.ones((3, 3), np.uint8)), (0, 0), alto_letra * 0.035)
    contorno = np.clip(contorno * 1.6, 0, 1)
    luz = np.clip(0.55 * halo + 0.75 * contorno, 0, 1)[..., None]
    placa = 255 - (255 - placa) * (1 - luz * (CALIDO / 255) * 0.95)
    placa = placa * (1 - 0.10 * luz) + CALIDO * 0.10 * luz
    # sombra corta del canto del acrílico
    off = max(1, int(alto_letra * 0.04))
    sombra = cv2.GaussianBlur(np.roll(np.roll(a, off, 0), off // 2, 1), (0, 0), alto_letra * 0.03)[..., None]
    placa = placa * (1 - 0.18 * sombra * (1 - a[..., None]))
    # cara platino; el borde de las letras toma un filo cálido
    filo = np.clip(a - cv2.erode(a, np.ones((3, 3), np.uint8)), 0, 1)[..., None]
    cara = rgb * (1 - 0.35 * filo) + CALIDO * 0.35 * filo
    placa = placa * (1 - a[..., None]) + cara * a[..., None]
    return np.clip(placa, 0, 255).astype(np.uint8)


def color_anillo(img, mask):
    anillo = cv2.dilate(mask, np.ones((25, 25), np.uint8)) & ~cv2.dilate(mask, np.ones((9, 9), np.uint8))
    px = img[anillo > 0]
    return np.median(px, 0) if len(px) else np.array([170, 185, 200])


# ------------------------------------------------------------------ limpieza

def quitar_reflejo_verde(img, cajas):
    """El croma tiñe de verde el piso y los cantos cercanos. Se neutraliza solo por debajo del borde superior
    de cada caja, cerca de ella y en tonos verdes (los relojes verde oliva o los productos no se tocan)."""
    H, W = img.shape[:2]
    zona = np.zeros((H, W), bool)
    yy = np.arange(H)[:, None]
    for quad, _, z in cajas:
        cerca = cv2.GaussianBlur(z.astype(np.float32) / 255, (0, 0), 140) > 0.002
        zona |= cerca & (yy > quad[:, 1].min())
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    tono = (hsv[..., 0] >= 45) & (hsv[..., 0] <= 82) & (hsv[..., 1] > 18)
    b, g, r = [c.astype(np.float32) for c in cv2.split(img)]
    exceso = np.clip(g - (np.maximum(r, b) * 0.6 + (r + b) * 0.2), 0, None)
    mascara_cajas = np.zeros((H, W), np.uint8)
    for _, _, z in cajas:
        mascara_cajas |= z
    sel = zona & tono & (cv2.dilate(mascara_cajas, np.ones((5, 5), np.uint8)) == 0)
    exceso = cv2.GaussianBlur(exceso * sel, (0, 0), 1.5)
    return cv2.merge([b, g - exceso, r]).clip(0, 255).astype(np.uint8), int((exceso > 3).sum())


def main():
    entrada, salida, lista = sys.argv[1], sys.argv[2], [x for x in sys.argv[3].split(',') if x]
    dir_artes = sys.argv[4] if len(sys.argv) > 4 else None
    img = cv2.imread(entrada)
    H, W = img.shape[:2]
    logo = cv2.imread(LOGO, cv2.IMREAD_UNCHANGED)
    verde, magenta = mascaras(img)
    cajas = regiones(verde, H * W * 0.0015)
    placas = [p for p in regiones(magenta, H * W * 0.0006) if np.linalg.norm(p[0][1] - p[0][0]) > 1.6 * np.linalg.norm(p[0][3] - p[0][0])]
    f, medida = estimar_focal((W, H), [q for q, _, _ in cajas], [q for q, _, _ in placas])
    rep = {'imagen': os.path.basename(entrada), 'focal_px': round(f), 'focal_medida': medida, 'cajas': [], 'logos': []}
    if len(lista) != len(cajas):
        raise SystemExit(f'{entrada}: {len(cajas)} cajas de luz y {len(lista)} artes')
    todo = np.zeros((H, W), np.uint8)
    base = os.path.splitext(os.path.basename(salida))[0]
    for i, ((quad, real, zona), nombre) in enumerate(zip(cajas, lista)):
        R = proporcion_real(quad, W, H, f)
        alto_px = int(np.clip(max(np.linalg.norm(quad[3] - quad[0]), np.linalg.norm(quad[2] - quad[1])) * 1.15, 300, 1400))
        arte = cv2.cvtColor(artes_a_la_talla.generar(nombre, R, alto_px), cv2.COLOR_RGB2BGR)
        if dir_artes:
            cv2.imwrite(os.path.join(dir_artes, f'{base}-{i}-{nombre}.jpg'), arte, [cv2.IMWRITE_JPEG_QUALITY, 90])
        img = pegar(img, arte, quad, real, sombreado_tela(img, real))
        todo |= zona
        rep['cajas'].append({'arte': nombre, 'proporcion': round(R, 3), 'px': list(arte.shape[1::-1]), 'quad': quad.round(1).tolist()})
    for quad, real, zona in placas:
        R = proporcion_real(quad, W, H, f)
        alto = max(np.linalg.norm(quad[3] - quad[0]), np.linalg.norm(quad[2] - quad[1])) * 1.5
        img = pegar(img, placa_logo(logo, alto * R, alto, color_anillo(img, real)), quad, real)
        todo |= zona
        rep['logos'].append({'proporcion': round(R, 3), 'quad': quad.round(1).tolist()})
    # bordes de croma que hayan quedado alrededor de lo compuesto
    v2, m2 = mascaras(img)
    resto = cv2.dilate(v2 | m2, np.ones((3, 3), np.uint8)) & cv2.dilate(todo, np.ones((9, 9), np.uint8))
    rep['pixeles_croma_restantes'] = int((resto > 0).sum())
    if resto.any():
        img = cv2.inpaint(img, resto, 4, cv2.INPAINT_TELEA)
    img, rep['pixeles_reflejo_verde'] = quitar_reflejo_verde(img, cajas)
    cv2.imwrite(salida, img, [cv2.IMWRITE_JPEG_QUALITY, 92])
    print(json.dumps(rep, ensure_ascii=False))


if __name__ == '__main__':
    main()

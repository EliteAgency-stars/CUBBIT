"""Compone los renders de Higgsfield con el logo oficial y las artes reales de Cubitt.

Higgsfield genera cada escena con marcadores de color:
  - verde croma (#00FF00) en cada caja de luz  -> se reemplaza por un arte real (tela backlight)
  - magenta (#FF00FF) donde va el logo          -> se reemplaza por el logo Cubitt platino oficial
Así el logo y las artes nunca los dibuja la IA: se pegan los archivos originales con perspectiva.

Uso: python3 componer_renders.py entrada.png salida.jpg arte1,arte2,... [dir_artes]
Imprime un JSON con las regiones encontradas y la verificación SIFT del logo.
"""
import json
import math
import sys

import cv2
import numpy as np

ARTES_DIR = sys.argv[4] if len(sys.argv) > 4 else 'a'


def mascaras(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    verde = cv2.inRange(hsv, (42, 110, 90), (78, 255, 255))
    magenta = cv2.inRange(hsv, (138, 90, 90), (168, 255, 255))
    return verde, magenta


def regiones(mask, area_min):
    """Agrupa la máscara en regiones (cerrando huecos de objetos delante) y devuelve (cuadrilátero, máscara_real)."""
    h, w = mask.shape
    k = max(5, int(w * 0.02)) | 1
    cerrada = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (k, k)))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(cerrada)
    salida = []
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] < area_min:
            continue
        zona = (lab == i).astype(np.uint8) * 255
        pts = cv2.findNonZero(zona).reshape(-1, 2).astype(np.float64)
        s, d = pts.sum(1), pts[:, 0] - pts[:, 1]
        quad = np.array([pts[s.argmin()], pts[d.argmax()], pts[s.argmax()], pts[d.argmin()]], np.float32)  # TL TR BR BL
        real = cv2.bitwise_and(mask, zona)
        salida.append((quad, real, int(stats[i, cv2.CC_STAT_AREA])))
    salida.sort(key=lambda r: -r[2])
    return salida


def medidas(quad):
    tl, tr, br, bl = quad
    ancho = (np.linalg.norm(tr - tl) + np.linalg.norm(br - bl)) / 2
    alto = (np.linalg.norm(bl - tl) + np.linalg.norm(br - tr)) / 2
    return ancho, alto


def ajustar(arte, ancho, alto):
    """Ajusta el arte a ancho×alto: 'cover' si las proporciones son parecidas; si no, 'contain' sobre el mismo arte difuminado."""
    W, H = int(round(ancho)), int(round(alto))
    ah, aw = arte.shape[:2]
    if abs(math.log((W / H) / (aw / ah))) < 0.28:
        esc = max(W / aw, H / ah)
        r = cv2.resize(arte, (math.ceil(aw * esc), math.ceil(ah * esc)), interpolation=cv2.INTER_AREA)
        y, x = (r.shape[0] - H) // 2, (r.shape[1] - W) // 2
        return r[y:y + H, x:x + W]
    esc = max(W / aw, H / ah)
    fondo = cv2.resize(arte, (math.ceil(aw * esc), math.ceil(ah * esc)))
    y, x = (fondo.shape[0] - H) // 2, (fondo.shape[1] - W) // 2
    fondo = cv2.GaussianBlur(fondo[y:y + H, x:x + W], (0, 0), max(W, H) / 25)
    fondo = cv2.addWeighted(fondo, 0.85, np.full_like(fondo, 255), 0.15, 0)
    esc = min(W / aw, H / ah) * 0.96
    r = cv2.resize(arte, (int(aw * esc), int(ah * esc)), interpolation=cv2.INTER_AREA)
    y, x = (H - r.shape[0]) // 2, (W - r.shape[1]) // 2
    fondo[y:y + r.shape[0], x:x + r.shape[1]] = r
    return fondo


def placa_logo(logo_rgba, ancho, alto, color):
    """Placa del color del panel con el logo platino centrado, sombra suave y halo cálido 3000K."""
    W, H = int(round(ancho)), int(round(alto))
    placa = np.full((H, W, 3), color, np.float32)
    lh, lw = logo_rgba.shape[:2]
    esc = min(W * 0.86 / lw, H * 0.80 / lh)
    l = cv2.resize(logo_rgba, (max(1, int(lw * esc)), max(1, int(lh * esc))), interpolation=cv2.INTER_AREA).astype(np.float32)
    y, x = (H - l.shape[0]) // 2, (W - l.shape[1]) // 2
    a = np.zeros((H, W), np.float32)
    a[y:y + l.shape[0], x:x + l.shape[1]] = l[:, :, 3] / 255
    rgb = np.zeros((H, W, 3), np.float32)
    rgb[y:y + l.shape[0], x:x + l.shape[1]] = l[:, :, :3]
    sig = max(1.0, l.shape[0] * 0.08)
    halo = cv2.GaussianBlur(a, (0, 0), sig * 2.2)[..., None]
    placa = placa * (1 - 0.35 * halo) + np.array([107, 180, 255], np.float32) * 0.35 * halo  # BGR ≈ 3000K
    sombra = cv2.GaussianBlur(np.roll(np.roll(a, max(1, int(sig * 0.5)), 0), max(1, int(sig * 0.3)), 1), (0, 0), sig * 0.6)[..., None]
    placa = placa * (1 - 0.30 * sombra)
    placa = placa * (1 - a[..., None]) + rgb * a[..., None]
    return np.clip(placa, 0, 255).astype(np.uint8)


def pegar(img, plano, quad, mask_real):
    H, W = plano.shape[:2]
    src = np.array([[0, 0], [W - 1, 0], [W - 1, H - 1], [0, H - 1]], np.float32)
    M = cv2.getPerspectiveTransform(src, quad)
    warp = cv2.warpPerspective(plano, M, (img.shape[1], img.shape[0]), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    m = cv2.dilate(mask_real, np.ones((5, 5), np.uint8))
    m = cv2.GaussianBlur(m, (0, 0), 1.2).astype(np.float32)[..., None] / 255
    return (img * (1 - m) + warp * m).astype(np.uint8)


def color_anillo(img, mask):
    anillo = cv2.dilate(mask, np.ones((25, 25), np.uint8)) & ~cv2.dilate(mask, np.ones((9, 9), np.uint8))
    px = img[anillo > 0]
    return np.median(px, 0) if len(px) else np.array([170, 185, 200])


def verificar_logo(img, logo_rgba):
    """Cuenta inliers SIFT entre el logo oficial y la imagen final (alto = logo correcto presente)."""
    ref = np.full(logo_rgba.shape[:2], 150, np.uint8)
    a = logo_rgba[:, :, 3] / 255.0
    ref = (ref * (1 - a) + cv2.cvtColor(logo_rgba[:, :, :3], cv2.COLOR_BGR2GRAY) * a).astype(np.uint8)
    ref = cv2.resize(ref, (800, int(800 * ref.shape[0] / ref.shape[1])))
    sift = cv2.SIFT_create()
    k1, d1 = sift.detectAndCompute(ref, None)
    k2, d2 = sift.detectAndCompute(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), None)
    if d1 is None or d2 is None:
        return 0
    buenos = [m for m, n in cv2.BFMatcher().knnMatch(d1, d2, k=2) if m.distance < 0.75 * n.distance]
    if len(buenos) < 6:
        return len(buenos)
    p1 = np.float32([k1[m.queryIdx].pt for m in buenos])
    p2 = np.float32([k2[m.trainIdx].pt for m in buenos])
    _, inl = cv2.findHomography(p1, p2, cv2.RANSAC, 5.0)
    return int(inl.sum()) if inl is not None else 0


def main():
    entrada, salida, lista = sys.argv[1], sys.argv[2], [x for x in sys.argv[3].split(',') if x]
    img = cv2.imread(entrada)
    logo = cv2.imread(f'{ARTES_DIR}/logo.png', cv2.IMREAD_UNCHANGED)
    area_min = img.shape[0] * img.shape[1] * 0.0015
    verde, magenta = mascaras(img)
    reporte = {'imagen': entrada, 'cajas': [], 'logos': []}

    artes = {n: cv2.imread(f'{ARTES_DIR}/{n}.jpg') for n in set(lista)}
    usos = {n: 0 for n in lista}
    for quad, real, area in regiones(verde, area_min):
        ancho, alto = medidas(quad)
        prop = ancho / max(alto, 1)
        # arte con la proporción más parecida, penalizando repeticiones
        nombre = min(lista, key=lambda n: abs(math.log(prop / (artes[n].shape[1] / artes[n].shape[0]))) + 0.6 * usos[n])
        usos[nombre] += 1
        img = pegar(img, ajustar(artes[nombre], ancho, alto), quad, real)
        reporte['cajas'].append({'arte': nombre, 'area': area, 'proporcion': round(float(prop), 2), 'quad': quad.round().tolist()})

    for quad, real, area in regiones(magenta, area_min * 0.4):
        ancho, alto = medidas(quad)
        img = pegar(img, placa_logo(logo, ancho, alto, color_anillo(img, real)), quad, real)
        reporte['logos'].append({'area': area, 'proporcion': round(float(ancho / max(alto, 1)), 2), 'quad': quad.round().tolist()})

    # limpieza de bordes de croma que hayan quedado
    v2, m2 = mascaras(img)
    resto = cv2.dilate(v2 | m2, np.ones((3, 3), np.uint8))
    reporte['pixeles_croma_restantes'] = int((v2 | m2).sum() / 255)
    if resto.any():
        img = cv2.inpaint(img, resto, 4, cv2.INPAINT_TELEA)
    reporte['sift_logo_inliers'] = verificar_logo(img, logo) if reporte['logos'] else None
    cv2.imwrite(salida, img, [cv2.IMWRITE_JPEG_QUALITY, 90])
    print(json.dumps(reporte, ensure_ascii=False))


if __name__ == '__main__':
    main()

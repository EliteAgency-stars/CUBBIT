"""Isotipo Cubitt (retícula de puntos con conectores) recortado del logo oficial en platino.

No se redibuja nada: se toma el archivo oficial propuesta-2027/assets/logo/logo-cubitt-platino.png, se busca el
espacio vacío que separa la palabra «Cubitt» de la retícula y se recorta la retícula con sus conectores.
Los SketchUp nuevos llevan el isotipo en los laterales del mueble y en la espalda de la caja de luz del display.

Uso: python tools/preparar_isotipo.py
Requiere Pillow y numpy.
"""
import os

import numpy as np
from PIL import Image

LOGO = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'propuesta-2027', 'assets', 'logo')


def recortar(origen, destino, margen=0.04):
    img = Image.open(origen).convert('RGBA')
    a = np.asarray(img.getchannel('A')) > 20
    cols = a.any(0)
    # el hueco más ancho entre columnas vacías separa la palabra de la retícula
    huecos, ini = [], None
    for x, lleno in enumerate(cols):
        if not lleno and ini is None:
            ini = x
        elif lleno and ini is not None:
            huecos.append((x - ini, ini, x))
            ini = None
    x0 = max(huecos)[2]
    filas = np.where(a[:, x0:].any(1))[0]
    x1 = x0 + np.where(a[:, x0:].any(0))[0].max() + 1
    y0, y1 = filas.min(), filas.max() + 1
    m = int(round((y1 - y0) * margen))
    recorte = img.crop((x0 - m, y0 - m, x1 + m, y1 + m))
    recorte.save(destino, optimize=True)
    print(f'{destino}: {recorte.size[0]} × {recorte.size[1]} px (proporción {recorte.size[0] / recorte.size[1]:.3f})')


if __name__ == '__main__':
    recortar(os.path.join(LOGO, 'logo-cubitt-platino.png'), os.path.join(LOGO, 'isotipo-cubitt-platino.png'))

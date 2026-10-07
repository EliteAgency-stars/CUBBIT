// Planos cenitales (planogramas) de cada pieza: posición de los productos reales de Cubitt.
// Unidades en milímetros; x crece a la derecha, y crece hacia el frente (cliente abajo).
const P = (n) => `propuesta-2027/artes-cubitt/productos/${n}.png`;

// Módulo del mueble de exhibición (centrado en dx): caja de luz, elevador Duna y relojes al frente.
const RELOJ = { 'viva-pro-2': 'Viva Pro 2', 'viva-2-rosado': 'Viva 2', 'viva-lite-lilac': 'Viva Lite', 'aura-2-azul': 'Aura 2',
  'aura-pro-2': 'Aura Pro 2', 'terra-verde': 'Terra' };
const RELOJES_MESA = ['viva-pro-2', 'viva-2-rosado', 'viva-lite-lilac', 'aura-2-azul', 'aura-pro-2', 'terra-verde', 'viva-pro-2', 'aura-pro-2', 'terra-verde'];
const RELOJES_MURO = ['viva-pro-2', 'viva-2-rosado', 'viva-lite-lilac', 'aura-2-azul', 'aura-pro-2', 'terra-verde', 'viva-pro-2', 'aura-pro-2', 'terra-verde', 'viva-2-rosado'];
const MUEBLE_ZONAS = (dx, etiquetas = true) => [
  { x: dx - 600, y: -184, w: 1200, h: 16, tipo: 'luz', etiqueta: 'Caja de luz trasera 120 × 65 cm · arte 5000K' },
  { x: dx - 572, y: -158, w: 1124, h: 140, tipo: 'duna', etiqueta: 'Elevador Duna · 112 × 14 × 5 cm · audio' },
  { x: dx - 585, y: 35, w: 1100, h: 140, tipo: 'zona', etiqueta: 'Relojes · 8 checkpoints con ficha acrílica al frente' },
].map((z) => (etiquetas ? z : { ...z, etiqueta: null }));
const MUEBLE_PRODUCTOS = (dx, relojes) => [
  ...[-530, -400, -261, -110, 35, 165, 304, 455].map((x, i) => ({ n: relojes[i], x: dx + x, y: 72, w: 70, nombre: RELOJ[relojes[i]] })),
  { n: 'power-anc-negro', x: dx - 444, y: -67, w: 150, nombre: 'Power ANC' },
  { n: 'power-buds-2', x: dx - 281, y: -105, w: 70, nombre: 'Power Buds 2' },
  { n: 'power-pro-2', x: dx - 20, y: -100, w: 230, nombre: 'Power Pro 2' },
  { n: 'power-plus-2', x: dx + 211, y: -80, w: 85, nombre: 'Power Plus 2' },
  { n: 'power-go-2', x: dx + 352, y: -80, w: 70, nombre: 'Power Go 2' },
  { n: 'power-mini', x: dx + 463, y: -80, w: 65, nombre: 'Power Mini' },
];

export const PLANOS = {
  mesa: {
    // Medidas y posiciones tomadas del SketchUp «mesa cubitt» (100 × 50 cm, tope Duna con esquinas R40).
    titulo: 'Mesa de experiencia',
    ancho: 1000, fondo: 500, radio: 40,
    zonas: [
      { x: -448, y: -240, w: 910, h: 188, tipo: 'duna', etiqueta: 'Elevador en madera Duna · 91 × 18,8 × 5 cm · audio y 5 fichas acrílicas' },
      { x: -478, y: 72, w: 952, h: 150, tipo: 'zona', etiqueta: 'Relojes · 9 checkpoints con ficha acrílica al frente' },
    ],
    productos: [
      { n: 'power-buds-2', x: -353, y: -121, w: 80, nombre: 'Power Buds 2' },
      { n: 'power-pro-2', x: -117, y: -117, w: 250, nombre: 'Power Pro 2' },
      { n: 'power-plus-2', x: 92, y: -124, w: 90, nombre: 'Power Plus 2' },
      { n: 'power-go-2', x: 223, y: -121, w: 75, nombre: 'Power Go 2' },
      { n: 'power-anc-negro', x: 386, y: -127, w: 150, nombre: 'Power ANC' },
      ...[-437, -324, -216, -110, 1, 110, 215, 320, 431].map((x, i) => ({
        n: RELOJES_MESA[i], x, y: 104, w: 70, nombre: RELOJ[RELOJES_MESA[i]],
      })),
    ],
    frente: 'Frente: caja de luz 85 × 58 cm (Viva Pro 2) · laterales: logo platino 3000K · atrás: dos puertas push',
  },
  mueble: {
    // Medidas y posiciones del SketchUp «mueble cubitt»: módulo de 120 cm que se une lado a lado.
    titulo: 'Mueble de exhibición',
    ancho: 1200, fondo: 400, radio: 40,
    zonas: MUEBLE_ZONAS(0),
    productos: MUEBLE_PRODUCTOS(0, ['viva-pro-2', 'viva-2-rosado', 'viva-lite-lilac', 'aura-2-azul', 'aura-pro-2', 'terra-verde', 'viva-pro-2', 'aura-pro-2']),
    frente: 'Frente liso con logo platino 3000K · laterales: isotipo platino · caja de luz trasera 120 × 65 cm · atrás: dos puertas push',
  },
  modular: {
    titulo: 'Composición de dos muebles',
    ancho: 2400, fondo: 400, radio: 40, modulos: 2,
    zonas: [...MUEBLE_ZONAS(-600), ...MUEBLE_ZONAS(600, false)],
    productos: [
      ...MUEBLE_PRODUCTOS(-600, ['viva-pro-2', 'viva-2-rosado', 'viva-lite-lilac', 'aura-2-azul', 'aura-pro-2', 'terra-verde', 'viva-pro-2', 'aura-pro-2']),
      ...MUEBLE_PRODUCTOS(600, ['terra-verde', 'aura-pro-2', 'aura-2-azul', 'viva-lite-lilac', 'viva-2-rosado', 'viva-pro-2', 'terra-verde', 'viva-pro-2']),
    ],
    frente: 'Dos módulos iguales lado a lado (240 cm) · cajas de luz Nueva Era y Viva Pro 2 · logo al frente de cada módulo · isotipo solo en los laterales exteriores',
  },
  sobremesa: {
    // Medidas y posiciones del SketchUp «sobre mesa cubitt»: 50 × 32 × 25 cm, cinco relojes en dos filas.
    titulo: 'Display de sobremesa',
    ancho: 500, fondo: 250, radio: 33,
    zonas: [
      { x: -250, y: -112, w: 500, h: 14, tipo: 'luz', etiqueta: 'Caja de luz 50 × 25 cm · arte Nueva Era 5000K' },
      { x: -225, y: -45, w: 450, h: 150, tipo: 'zona', etiqueta: 'Relojes · 5 checkpoints en dos filas, cada uno con ficha acrílica' },
    ],
    productos: [['viva-2-rosado', -183, 26], ['viva-pro-2', 9, 26], ['aura-2-azul', 173, 26], ['terra-verde', -84, -66], ['aura-pro-2', 94, -66]]
      .map(([n, x, y]) => ({ n, x, y, w: 60, nombre: RELOJ[n] })),
    frente: 'Frente: logo platino en la base Capri · espalda de la caja de luz: isotipo platino · línea LED 3000K bajo el tope Duna',
  },
  muro: {
    // Bonus · SketchUp «cuarto mueble mesa cubitt»: muro de 220 × 49 cm. Abajo el mesón (relojes y audífonos); la repisa
    // flotante a 1,26 m (audio) se dibuja en su posición en planta, sobre el mesón.
    titulo: 'Muro de exhibición (bonus)',
    ancho: 2200, fondo: 490, radio: 4,
    zonas: [
      { x: -820, y: -160, w: 1683, h: 250, tipo: 'duna', etiqueta: 'Repisa flotante Duna a 1,26 m · 168 × 25 cm · audio y 8 fichas · LED 3000K' },
      { x: -1051, y: -172, w: 2088, h: 14, tipo: 'luz', etiqueta: 'Caja de luz 209 × 60 cm · arte Nueva Era 5000K (de 1,52 a 2,12 m)' },
      { x: -720, y: -30, w: 1440, h: 190, tipo: 'zona', etiqueta: 'Mesón a 79,4 cm · 10 relojes con ficha acrílica' },
      { x: -1010, y: -40, w: 230, h: 200, tipo: 'zona', etiqueta: 'Power ANC en soporte acrílico a cada lado' },
      { x: 820, y: -40, w: 230, h: 200, tipo: 'zona', etiqueta: null },
    ],
    productos: [
      { n: 'power-anc-negro', x: -873, y: 44, w: 150, nombre: 'Power ANC' },
      { n: 'power-anc-negro', x: 937, y: 44, w: 150, nombre: 'Power ANC' },
      { n: 'power-pro-2', x: -612, y: -53, w: 250, nombre: 'Power Pro 2' },
      { n: 'power-pro-2', x: 694, y: -53, w: 250, nombre: 'Power Pro 2' },
      ...[-361, -186, -18, 134].map((x) => ({ n: 'power-buds-2', x, y: -44, w: 75, nombre: 'Power Buds 2' })),
      { n: 'power-go-2', x: 290, y: -53, w: 70, nombre: 'Power Go 2' },
      { n: 'power-plus-2', x: 420, y: -53, w: 85, nombre: 'Power Plus 2' },
      // los relojes van en el mesón, debajo del vuelo de la repisa: se dibujan encima para que se lean
      ...[-618, -462, -330, -200, -61, 87, 227, 376, 519, 667].map((x, i) => ({ n: RELOJES_MURO[i], x, y: 18, w: 70, nombre: RELOJ[RELOJES_MURO[i]] })),
    ],
    frente: 'Frente: cuatro puertas push Capri · cabecera con logo platino de 64,5 cm y LED 3000K hacia abajo · lateral izquierdo e interior en Nácar',
  },
  kids: {
    titulo: 'Mueble Cubitt Jr & Teens',
    ancho: 1200, fondo: 550, radio: 50,
    zonas: [
      { x: -580, y: -275, w: 1160, h: 50, tipo: 'luz', etiqueta: 'Caja de luz Cubitt Jr. · 93–125 cm' },
      { x: -600, y: -225, w: 1200, h: 225, tipo: 'duna', etiqueta: 'Mesón padres · h 90 cm' },
      { x: -600, y: 0, w: 1200, h: 275, tipo: 'kids', etiqueta: 'Mesón niños · h 60 cm' },
    ],
    productos: [
      { n: 'hydro-bottle-jr-rapunzel', x: -400, y: -120, w: 70, nombre: 'Hydro Bottle Jr.' },
      { n: 'hydro-bottle-jr-paw-patrol', x: -130, y: -120, w: 70, nombre: 'Hydro Bottle Jr.' },
      { n: 'tumbler-jr-pink', x: 140, y: -120, w: 90, nombre: 'Tumbler Jr.' },
      { n: 'mug-jr-azul', x: 410, y: -120, w: 80, nombre: 'Mug Jr.' },
      ...['jr-rapunzel', 'jr-paw-patrol', 'jr-artic-blue', 'teens-forest-green'].map((n, i) => ({
        n, x: -420 + i * 220, y: 150, w: 80, nombre: ['Jr. Rapunzel', 'Jr. Paw Patrol', 'Jr. Artic Blue', 'Teens'][i],
      })),
      { n: 'headphones-jr-pink', x: 480, y: 140, w: 150, nombre: 'Headphones Jr.' },
    ],
    frente: 'Frente: logo platino a 32 cm · sin vidrio · esquinas R50',
  },
};

const ESTILO = {
  duna: 'fill:#d9c3a3;stroke:#b39672',
  zona: 'fill:none;stroke:#b8aa98;stroke-dasharray:14 10',
  luz: 'fill:#eef2ff;stroke:#c9c8c4',
  inox: 'fill:#d9dadb;stroke:#a9aaab',
  kids: 'fill:#ead7bd;stroke:#c2a27b',
};

const FONDO = { duna: '#d9c3a3', zona: 'transparent', luz: '#eef2ff', inox: '#d9dadb', kids: '#ead7bd' };

export function planoSVG(clave) {
  const p = PLANOS[clave];
  const m = 170; // margen para cotas y etiquetas
  const W = p.ancho + m * 2, H = p.fondo + m * 2;
  const ox = W / 2, oy = H / 2;
  const t = (txt, x, y, extra = '') => `<text x="${x}" y="${y}" ${extra}>${txt}</text>`;
  let s = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Plano cenital: ${p.titulo}" xmlns="http://www.w3.org/2000/svg">`;
  const n = p.modulos || 1, wm = p.ancho / n;
  for (let i = 0; i < n; i++) {
    s += `<rect x="${ox - p.ancho / 2 + i * wm}" y="${oy - p.fondo / 2}" width="${wm}" height="${p.fondo}" rx="${p.radio}" class="plano-cuerpo"/>`;
  }
  for (const z of p.zonas) {
    s += `<rect x="${ox + z.x}" y="${oy + z.y}" width="${z.w}" height="${z.h}" rx="10" style="${ESTILO[z.tipo]};stroke-width:3"/>`;
  }
  for (const pr of p.productos) {
    const w = pr.w, x = ox + pr.x - w / 2, y = oy + pr.y - w / 2;
    s += `<image href="${P(pr.n)}" x="${x}" y="${y}" width="${w}" height="${w}" preserveAspectRatio="xMidYMid meet"><title>${pr.nombre}</title></image>`;
  }
  // Cotas
  const yc = oy + p.fondo / 2 + 55, xc = ox + p.ancho / 2 + 55;
  s += `<path d="M${ox - p.ancho / 2} ${yc} H${ox + p.ancho / 2} M${ox - p.ancho / 2} ${yc - 14} v28 M${ox + p.ancho / 2} ${yc - 14} v28" class="plano-cota"/>`;
  s += t(`${p.ancho} mm`, ox, yc + 42, 'class="plano-cota-txt" text-anchor="middle"');
  s += `<path d="M${xc} ${oy - p.fondo / 2} V${oy + p.fondo / 2} M${xc - 14} ${oy - p.fondo / 2} h28 M${xc - 14} ${oy + p.fondo / 2} h28" class="plano-cota"/>`;
  s += t(`${p.fondo} mm`, xc + 46, oy, `class="plano-cota-txt" text-anchor="middle" transform="rotate(-90 ${xc + 46} ${oy})"`);
  s += t('CLIENTE ↓', ox, H - 12, 'class="plano-lado" text-anchor="middle"');
  s += t('↑ VENDEDOR / MURO', ox, 40, 'class="plano-lado" text-anchor="middle"');
  s += '</svg>';
  return s;
}

export function leyenda(clave) {
  const p = PLANOS[clave];
  const zonas = p.zonas.filter((z) => z.etiqueta).map((z) => `<li><span class="leyenda-muestra" style="background:${FONDO[z.tipo]}"></span>${z.etiqueta}</li>`).join('');
  const vistos = new Set();
  const prods = p.productos.filter((pr) => pr.nombre && !vistos.has(pr.n) && vistos.add(pr.n))
    .map((pr) => `<li><img src="${P(pr.n)}" alt="" loading="lazy">${pr.nombre}</li>`).join('');
  return `<ul class="leyenda-zonas">${zonas}<li><span class="leyenda-muestra"></span>${p.frente}</li></ul><ul class="leyenda-productos">${prods}</ul>`;
}

// Planos cenitales (planogramas) de cada pieza: posición de los productos reales de Cubitt.
// Unidades en milímetros; x crece a la derecha, y crece hacia el frente (cliente abajo).
const P = (n) => `propuesta-2027/artes-cubitt/productos/${n}.png`;

export const PLANOS = {
  mesa: {
    titulo: 'Mesa de experiencia',
    ancho: 1500, fondo: 700, radio: 30,
    zonas: [
      { x: -390, y: -310, w: 1080, h: 220, tipo: 'duna', etiqueta: 'Elevador en madera Duna · h 10 cm · bafles' },
      { x: -740, y: -310, w: 300, h: 620, tipo: 'zona', etiqueta: 'Audífonos' },
      { x: -440, y: 110, w: 1150, h: 190, tipo: 'zona', etiqueta: 'Relojes · checkpoints' },
    ],
    productos: [
      { n: 'power-go-2', x: -270, y: -200, w: 110, nombre: 'Power Go 2' },
      { n: 'power-pro-2', x: 20, y: -200, w: 300, nombre: 'Power Pro 2' },
      { n: 'power-plus-2', x: 300, y: -200, w: 80, nombre: 'Power Plus 2' },
      { n: 'power-mini', x: 520, y: -200, w: 100, nombre: 'Power Mini' },
      { n: 'power-anc-negro', x: -600, y: -170, w: 180, nombre: 'Power ANC' },
      { n: 'power-anc-crema', x: -600, y: 40, w: 170, nombre: 'Power ANC crema' },
      { n: 'power-buds-2', x: -600, y: 240, w: 90, nombre: 'Power Buds 2' },
      ...['viva-pro-2', 'viva-2-rosado', 'viva-lite-lilac', 'aura-2-azul', 'aura-pro-2', 'terra-verde'].map((n, i) => ({
        n, x: -360 + i * 190, y: 200, w: 75,
        nombre: ['Viva Pro 2', 'Viva 2', 'Viva Lite', 'Aura 2', 'Aura Pro 2', 'Terra'][i],
      })),
    ],
    frente: 'Frente: caja de luz «Nueva Era» · laterales: logo platino',
  },
  mueble: {
    titulo: 'Mueble de exhibición',
    ancho: 1200, fondo: 400, radio: 30,
    zonas: [
      { x: -580, y: -200, w: 1160, h: 60, tipo: 'luz', etiqueta: 'Caja de luz trasera · arte de campaña 5000K' },
      { x: -500, y: -130, w: 1000, h: 140, tipo: 'zona', etiqueta: 'Repisa acrílica regulable · producto héroe' },
      { x: -580, y: 170, w: 1160, h: 25, tipo: 'inox', etiqueta: 'Riel de precio inox · CTA' },
    ],
    productos: [
      { n: 'viva-pro-2', x: 0, y: -60, w: 80, nombre: 'Héroe: Viva Pro 2' },
      { n: 'viva-2-rosado', x: -440, y: 70, w: 75, nombre: 'Viva 2' },
      { n: 'viva-lite-lilac', x: -220, y: 70, w: 75, nombre: 'Viva Lite' },
      { n: 'power-buds-2', x: 0, y: 70, w: 90, nombre: 'Power Buds 2' },
      { n: 'termo-burgandy', x: 300, y: 60, w: 80, nombre: 'Termo' },
      { n: 'coffee-mug-verde', x: 440, y: 60, w: 90, nombre: 'Coffee Mug' },
    ],
    frente: 'Frente: gabinete Capri con logo platino · lateral: caja de luz 40 × 76',
  },
  sobremesa: {
    titulo: 'Display de sobremesa',
    ancho: 500, fondo: 250, radio: 20,
    zonas: [
      { x: -240, y: -125, w: 480, h: 35, tipo: 'luz', etiqueta: 'Caja de luz + banda con logo' },
      { x: -230, y: 105, w: 460, h: 18, tipo: 'inox', etiqueta: 'Riel de precio' },
    ],
    productos: ['viva-pro-2', 'viva-2-rosado', 'viva-lite-lilac'].map((n, i) => ({
      n, x: -150 + i * 150, y: 20, w: 70, nombre: ['Viva Pro 2', 'Viva 2', 'Viva Lite'][i],
    })),
    frente: '3 checkpoints integrados en la madera',
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
  s += `<rect x="${ox - p.ancho / 2}" y="${oy - p.fondo / 2}" width="${p.ancho}" height="${p.fondo}" rx="${p.radio}" class="plano-cuerpo"/>`;
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
  const zonas = p.zonas.map((z) => `<li><span class="leyenda-muestra" style="background:${FONDO[z.tipo]}"></span>${z.etiqueta}</li>`).join('');
  const prods = p.productos.map((pr) => `<li><img src="${P(pr.n)}" alt="" loading="lazy">${pr.nombre}</li>`).join('');
  return `<ul class="leyenda-zonas">${zonas}<li><span class="leyenda-muestra"></span>${p.frente}</li></ul><ul class="leyenda-productos">${prods}</ul>`;
}

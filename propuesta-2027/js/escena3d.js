// Escena 3D paramétrica de la familia Cubitt 2027 (unidades en metros, medidas del brief).
// Materiales: melamina Capri (cuerpos) y Duna (cubiertas) de Madecentro/Pelíkano, zócalo inox,
// cajas de luz de aluminio con esquinas redondas y tela backlight con las artes reales de Cubitt.
// Luz: 3000K en muebles y logo, 5000K en cajas de luz. Los productos son las fotos reales de Cubitt.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const BASE = new URL('../', import.meta.url).href;
const ruta = (p) => BASE + p;

const COLOR = {
  capri: 0xbfb0a4,
  inox: 0xd9dadb,
  aluminio: 0xc9c8c4,
  luz3000: 0xffc27d,
  luz5000: 0xf2f5ff,
  piso: 0xe2d6c6,
  muro: 0xf1ebe2,
  mostrador: 0xf7f5f1,
  checkpoint: 0xf4f3f1,
};

// ---------- Construcción ----------

class Pieza {
  constructor(nombre) {
    this.nombre = nombre;
    this.grupo = new THREE.Group();
    this.grupo.name = nombre;
    this.partes = [];      // { obj, base, despiece }
    this.materiales = [];
    this.cajasLuz = [];    // materiales de tela backlight (5000K)
    this.lineas = [];      // materiales de LED cálido (3000K)
    this.halos = [];       // halos del logo (3000K)
  }
  mat(params, tipo) {
    const m = params.isMaterial ? params : new THREE.MeshStandardMaterial(params);
    // Los materiales mate (Capri, Duna) reciben menos luz ambiental para conservar su tono real
    if (m.isMeshStandardMaterial && m.metalness < 0.5 && !tipo) m.envMapIntensity = 0.4;
    this.materiales.push(m);
    if (tipo === 'caja') this.cajasLuz.push(m);
    if (tipo === 'linea') this.lineas.push(m);
    if (tipo === 'halo') this.halos.push(m);
    return m;
  }
  add(obj, despiece = [0, 0, 0]) {
    this.grupo.add(obj);
    this.partes.push({ obj, base: obj.position.clone(), despiece: new THREE.Vector3(...despiece) });
    return obj;
  }
  caja(w, h, d, material, x, y, z, radio = 0.004, despiece) {
    const geo = radio > 0 ? new RoundedBoxGeometry(w, h, d, 4, Math.min(radio, w / 2, h / 2, d / 2)) : new THREE.BoxGeometry(w, h, d);
    const m = new THREE.Mesh(geo, material);
    m.position.set(x, y, z);
    m.castShadow = m.receiveShadow = true;
    return this.add(m, despiece);
  }
}

function rectRedondeado(w, h, r) {
  const s = new THREE.Shape();
  const x = -w / 2, y = -h / 2;
  s.moveTo(x + r, y);
  s.lineTo(x + w - r, y);
  s.quadraticCurveTo(x + w, y, x + w, y + r);
  s.lineTo(x + w, y + h - r);
  s.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  s.lineTo(x + r, y + h);
  s.quadraticCurveTo(x, y + h, x, y + h - r);
  s.lineTo(x, y + r);
  s.quadraticCurveTo(x, y, x + r, y);
  return s;
}

// Volumen con aristas verticales redondeadas: rectángulo redondeado en planta extruido en altura.
function cuerpo(p, w, h, d, material, x, y, z, despiece, r = 0.03) {
  const g = new THREE.ExtrudeGeometry(rectRedondeado(w, d, r), { depth: h, bevelEnabled: false, curveSegments: 10 });
  g.rotateX(-Math.PI / 2);
  const m = new THREE.Mesh(g, material);
  m.position.set(x, y, z);
  m.castShadow = m.receiveShadow = true;
  return p.add(m, despiece);
}

// Textura de madera con proyección por caras (para que la veta corra a lo largo de la cubierta)
function materialDuna(tex) {
  const t = tex.clone();
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(1.2, 1.2);
  t.rotation = Math.PI / 2;
  t.needsUpdate = true;
  return { color: 0xffffff, map: t, roughness: 0.62 };
}

// Caja de luz: marco de aluminio con esquinas redondas + tela backlight con el arte (5000K)
// Las artes vienen a la talla de cada caja (artes-cubitt/a-la-talla/, tools/artes_a_la_talla.py): no se recortan ni se estiran.
function cajaDeLuz(p, w, h, arte, x, y, z, rotY = 0, despiece, { borde = 0.022, fondo = 0.03, radio = 0.045 } = {}) {
  const r = Math.min(radio, h / 4);
  const anillo = rectRedondeado(w, h, r);
  anillo.holes.push(rectRedondeado(w - borde * 2, h - borde * 2, r - borde * 0.6));
  const bisel = Math.min(0.004, borde / 3);
  const geoMarco = new THREE.ExtrudeGeometry(anillo, { depth: fondo, bevelEnabled: true, bevelThickness: bisel, bevelSize: bisel, bevelSegments: 2, curveSegments: 10 });
  const alu = p.mat({ color: COLOR.aluminio, metalness: 0.9, roughness: 0.32 });
  const marco = new THREE.Mesh(geoMarco, alu);
  const wi = w - borde * 2, hi = h - borde * 2;
  const geoTela = new THREE.ShapeGeometry(rectRedondeado(wi, hi, r - borde * 0.6), 10);
  const uv = geoTela.attributes.uv, pos = geoTela.attributes.position;
  for (let i = 0; i < uv.count; i++) uv.setXY(i, (pos.getX(i) + wi / 2) / wi, (pos.getY(i) + hi / 2) / hi);
  const t = arte.clone();
  const ia = arte.image.width / arte.image.height, ib = wi / hi;
  if (ia > ib) { t.repeat.set(ib / ia, 1); t.offset.set((1 - ib / ia) / 2, 0); }
  else { t.repeat.set(1, ia / ib); t.offset.set(0, (1 - ia / ib) / 2); }
  t.needsUpdate = true;
  const tela = p.mat({ color: 0x5a5a5a, map: t, emissive: COLOR.luz5000, emissiveMap: t, emissiveIntensity: 1, roughness: 0.9 }, 'caja');
  const malla = new THREE.Mesh(geoTela, tela);
  malla.position.z = fondo * 0.73;
  const g = new THREE.Group();
  g.add(marco, malla);
  g.position.set(x, y, z);
  g.rotation.y = rotY;
  return p.add(g, despiece);
}

// Logo oficial Cubitt en platino con halo cálido 3000K
let LOGO = null, HALO = null;
const PROPORCION_LOGO = 951 / 4154;
function logoPlatino(p, ancho, x, y, z, rotY = 0, despiece) {
  const g = new THREE.Group();
  const alto = ancho * PROPORCION_LOGO;
  const halo = p.mat(new THREE.MeshBasicMaterial({ map: HALO, color: COLOR.luz3000, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false }), 'halo');
  const mHalo = new THREE.Mesh(new THREE.PlaneGeometry(ancho * 1.18, alto * 1.9), halo);
  const letras = p.mat({ map: LOGO, transparent: true, alphaTest: 0.35, metalness: 0.8, roughness: 0.28, color: 0xdedad3 });
  const mLetras = new THREE.Mesh(new THREE.PlaneGeometry(ancho, alto), letras);
  mLetras.position.z = 0.012;
  g.add(mHalo, mLetras);
  g.position.set(x, y, z);
  g.rotation.y = rotY;
  return p.add(g, despiece);
}

// Producto real (foto recortada) sobre su base
const PRODUCTOS = {};
function producto(p, nombre, alto, x, y, z, { base = 'checkpoint', despiece } = {}) {
  const tex = PRODUCTOS[nombre];
  if (!tex) return;
  const g = new THREE.Group();
  let yProd = 0;
  if (base === 'checkpoint') {
    const m = p.mat({ color: COLOR.checkpoint, roughness: 0.35 });
    const disco = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.032, 0.014, 28), m);
    disco.position.y = 0.007;
    const poste = new THREE.Mesh(new THREE.CylinderGeometry(0.007, 0.007, 0.05, 12), m);
    poste.position.y = 0.035;
    disco.castShadow = poste.castShadow = true;
    g.add(disco, poste);
    yProd = 0.03;
  }
  const mat = p.mat(new THREE.SpriteMaterial({ map: tex, alphaTest: 0.08, transparent: true }));
  const s = new THREE.Sprite(mat);
  const asp = tex.image.width / tex.image.height;
  s.scale.set(alto * asp, alto, 1);
  s.position.y = yProd + alto / 2;
  g.add(s);
  g.position.set(x, y, z);
  return p.add(g, despiece);
}

function lineaLed(p, w, x, y, z, despiece) {
  const m = p.mat({ color: COLOR.luz3000, emissive: COLOR.luz3000, emissiveIntensity: 1.2 }, 'linea');
  return p.caja(w, 0.005, 0.005, m, x, y, z, 0, despiece);
}

function zocalo(p, w, d, despiece) {
  const inox = p.mat({ color: COLOR.inox, metalness: 1, roughness: 0.22 });
  return cuerpo(p, w, 0.06, d, inox, 0, 0, 0, despiece, 0.02);
}

// ---------- 01 · Mesa de experiencia 80 × 79 × 50 (SketchUp «primer mueble mesa cubitt») ----------
// Medidas tomadas del archivo: base recta Capri 80 × 50 × 70,2 cm sobre zócalo inox de 5 cm, línea de sombra
// rehundida 3 cm con LED 3000K, tope Duna de 18 mm con esquinas R40, caja de luz frontal 66 × 56 cm a ras,
// logo platino en ambos laterales, elevador Duna 72,7 × 14 × 5 cm al fondo y dos puertas push atrás.
function crearMesa(tx) {
  const p = new Pieza('mesa');
  const capri = p.mat({ color: COLOR.capri, roughness: 0.8 });
  const duna = p.mat(materialDuna(tx.duna));
  const sombra = p.mat({ color: 0x8f8579, roughness: 0.9 });
  const inox = p.mat({ color: COLOR.inox, metalness: 1, roughness: 0.22 });
  const acrilico = p.mat({ color: 0xffffff, transparent: true, opacity: 0.35, roughness: 0.05 });

  cuerpo(p, 0.8, 0.05, 0.5, inox, 0, 0, 0, [0, -0.25, 0], 0.04);
  cuerpo(p, 0.8, 0.702, 0.5, capri, 0, 0.05, 0, undefined, 0.002);
  cuerpo(p, 0.74, 0.018, 0.44, sombra, 0, 0.752, 0, [0, 0.25, 0], 0.01);
  lineaLed(p, 0.72, 0, 0.765, 0.222, [0, 0.25, 0]);
  lineaLed(p, 0.72, 0, 0.765, -0.222, [0, 0.25, 0]);
  cuerpo(p, 0.8, 0.018, 0.5, duna, 0, 0.77, 0, [0, 0.4, 0], 0.04);
  // Frente: caja de luz a ras con el arte Viva Pro 2 a la talla (65,9 × 56,1 cm de tela)
  cajaDeLuz(p, 0.678, 0.58, tx.arteMesa, 0, 0.401, 0.247, 0, [0, 0, 0.3], { borde: 0.0093, fondo: 0.006, radio: 0.04 });
  // Laterales Capri con logo platino 3000K (36,5 cm, centrado a 40 cm de alto)
  logoPlatino(p, 0.365, 0.402, 0.4, -0.0095, Math.PI / 2, [0.22, 0, 0]);
  logoPlatino(p, 0.365, -0.402, 0.4, -0.0095, -Math.PI / 2, [-0.22, 0, 0]);
  // Elevador Duna al fondo con riel inox atrás
  const yTop = 0.788;
  p.caja(0.727, 0.05, 0.14, duna, 0.0055, yTop + 0.025, -0.139, 0.003, [0, 0.55, 0]);
  p.caja(0.689, 0.025, 0.003, inox, 0.0045, 0.8145, -0.2105, 0.001, [0, 0.55, 0]);
  const yRiser = yTop + 0.05;
  producto(p, 'power-pro-2', 0.13, -0.197, yRiser, -0.128, { base: null, despiece: [0, 0.72, 0] });
  producto(p, 'power-plus-2', 0.2, 0.0345, yRiser, -0.149, { base: null, despiece: [0, 0.72, 0] });
  producto(p, 'power-go-2', 0.09, 0.175, yRiser, -0.149, { base: null, despiece: [0, 0.72, 0] });
  producto(p, 'power-mini', 0.085, 0.2865, yRiser, -0.149, { base: null, despiece: [0, 0.72, 0] });
  // Audífonos: in-ear a la izquierda y de diadema a la derecha, cada uno con su ficha acrílica
  producto(p, 'power-buds-2', 0.07, -0.277, yTop, 0.034, { base: null, despiece: [0, 0.6, 0] });
  producto(p, 'power-anc-negro', 0.2, 0.277, yTop, 0.052, { base: null, despiece: [0, 0.6, 0] });
  // Relojes al frente: cuatro checkpoints con base acrílica delante
  ['viva-pro-2', 'viva-2-rosado', 'aura-pro-2', 'terra-verde'].forEach((n, i) => {
    const x = [-0.2165, -0.0865, 0.0525, 0.2035][i];
    producto(p, n, 0.075, x, yTop, 0.1445, { despiece: [0, 0.6, 0] });
    p.caja(0.08, 0.004, 0.05, acrilico, x, yTop + 0.002, 0.21, 0.001, [0, 0.6, 0]);
  });
  [[-0.339, 0.034], [0.337, 0.047]].forEach(([x, z]) => p.caja(0.05, 0.004, 0.08, acrilico, x, yTop + 0.002, z, 0.001, [0, 0.6, 0]));
  // Lado vendedor: dos puertas push (sin manijas)
  p.caja(0.003, 0.65, 0.002, sombra, 0, 0.401, -0.251, 0, [0, 0, -0.12]);
  p.caja(0.748, 0.003, 0.002, sombra, 0, 0.076, -0.251, 0, [0, 0, -0.12]);
  p.caja(0.748, 0.003, 0.002, sombra, 0, 0.726, -0.251, 0, [0, 0, -0.12]);
  return p;
}

// ---------- 02 · Mueble de exhibición 120 × 140 × 40 ----------
function crearMueble(tx, nombre, { arteFondo, arteLateral, lado = 0, conLogo, productos }) {
  const p = new Pieza(nombre);
  const capri = p.mat({ color: COLOR.capri, roughness: 0.8 });
  const duna = p.mat(materialDuna(tx.duna));
  const sombra = p.mat({ color: 0x8f8579, roughness: 0.9 });
  const acrilico = p.mat({ color: 0xffffff, transparent: true, opacity: 0.25, roughness: 0.05 });

  zocalo(p, 1.12, 0.34);
  cuerpo(p, 1.2, 0.79, 0.4, capri, 0, 0.06, 0);
  p.caja(0.003, 0.7, 0.002, sombra, 0, 0.45, 0.201, 0);
  lineaLed(p, 1.16, 0, 0.845, 0.19);
  cuerpo(p, 1.22, 0.03, 0.42, duna, 0, 0.85, 0);
  // Caja de luz trasera (88 a 140 cm)
  cuerpo(p, 1.2, 0.52, 0.06, capri, 0, 0.88, -0.17, undefined, 0.015);
  cajaDeLuz(p, 1.16, 0.48, arteFondo, 0, 1.14, -0.14, 0);
  if (conLogo) logoPlatino(p, 0.46, 0, 0.47, 0.202);
  // Caja de luz lateral 40 × 76 en el lado expuesto
  if (lado) cajaDeLuz(p, 0.36, 0.72, arteLateral, lado * 0.601, 0.48, 0, lado * Math.PI / 2);
  // Repisa acrílica regulable
  p.caja(1.0, 0.008, 0.14, acrilico, 0, 1.06, -0.06, 0.002);
  producto(p, productos[0], 0.085, 0, 1.064, -0.06);
  productos.slice(1).forEach((n, i, arr) => producto(p, n, n.startsWith('termo') || n.startsWith('coffee') ? 0.22 : n.startsWith('power-anc') ? 0.17 : 0.085,
    -0.44 + i * (0.88 / Math.max(1, arr.length - 1)), 0.88, 0.06, { base: n.startsWith('termo') || n.startsWith('coffee') || n.startsWith('power-anc') ? null : 'checkpoint' }));
  const inox = p.mat({ color: COLOR.inox, metalness: 1, roughness: 0.22 });
  p.caja(1.18, 0.022, 0.006, inox, 0, 0.865, 0.213, 0.002);
  return p;
}

// ---------- 03 · Display de sobremesa 50 × 30 × 25 ----------
function crearSobremesa(tx) {
  const p = new Pieza('sobremesa');
  const capri = p.mat({ color: COLOR.capri, roughness: 0.8 });
  const duna = p.mat(materialDuna(tx.duna));
  cuerpo(p, 0.5, 0.035, 0.25, capri, 0, 0, 0, undefined, 0.02);
  lineaLed(p, 0.46, 0, 0.037, 0.118);
  cuerpo(p, 0.5, 0.045, 0.25, duna, 0, 0.037, 0, [0, 0.06, 0], 0.02);
  cajaDeLuz(p, 0.48, 0.2, tx.arteSobremesa, 0, 0.19, -0.105, 0, [0, 0.14, -0.06]);
  const banda = p.mat({ color: COLOR.aluminio, metalness: 0.85, roughness: 0.35 });
  p.caja(0.48, 0.065, 0.03, banda, 0, 0.322, -0.11, 0.012, [0, 0.2, -0.06]);
  logoPlatino(p, 0.17, 0, 0.322, -0.094, 0, [0, 0.2, -0.04]);
  ['viva-pro-2', 'viva-2-rosado', 'viva-lite-lilac'].forEach((n, i) => producto(p, n, 0.07, -0.15 + i * 0.15, 0.082, 0.02, { despiece: [0, 0.14, 0] }));
  const inox = p.mat({ color: COLOR.inox, metalness: 1, roughness: 0.22 });
  p.caja(0.46, 0.022, 0.006, inox, 0, 0.06, 0.128, 0.002);
  return p;
}

// ---------- 04 · Mueble Cubitt Jr & Teens (accesibilidad infantil) 120 × 125 × 55 ----------
function crearKids(tx) {
  const p = new Pieza('kids');
  const capri = p.mat({ color: COLOR.capri, roughness: 0.8 });
  const duna = p.mat(materialDuna(tx.duna));
  zocalo(p, 1.12, 0.47);
  // Mesón infantil a 60 cm (frente) y mesón de padres a 90 cm (atrás), todas las esquinas R50
  cuerpo(p, 1.2, 0.51, 0.3, capri, 0, 0.06, 0.125, undefined, 0.05);
  cuerpo(p, 1.22, 0.03, 0.32, duna, 0, 0.57, 0.125, undefined, 0.05);
  lineaLed(p, 1.14, 0, 0.565, 0.282);
  cuerpo(p, 1.2, 0.81, 0.25, capri, 0, 0.06, -0.15, undefined, 0.05);
  cuerpo(p, 1.22, 0.03, 0.27, duna, 0, 0.87, -0.15, undefined, 0.05);
  lineaLed(p, 1.14, 0, 0.865, -0.02);
  // Caja de luz con el arte Cubitt Jr. (93 a 125 cm, a la altura de los ojos de un niño de 8 a 10 años)
  cuerpo(p, 1.2, 0.36, 0.05, capri, 0, 0.9, -0.255, undefined, 0.02);
  cajaDeLuz(p, 1.14, 0.32, tx.arteJr, 0, 1.08, -0.23, 0);
  logoPlatino(p, 0.42, 0, 0.32, 0.276);
  ['jr-rapunzel', 'jr-paw-patrol', 'jr-artic-blue', 'teens-forest-green'].forEach((n, i) => producto(p, n, 0.09, -0.42 + i * 0.22, 0.6, 0.15));
  producto(p, 'headphones-jr-pink', 0.16, 0.48, 0.6, 0.13, { base: null });
  ['hydro-bottle-jr-rapunzel', 'hydro-bottle-jr-paw-patrol', 'tumbler-jr-pink', 'mug-jr-azul'].forEach((n, i) =>
    producto(p, n, n.startsWith('tumbler') ? 0.24 : 0.2, -0.4 + i * 0.27, 0.9, -0.14, { base: null }));
  // Siluetas de escala: niño de 7 años (1,20 m) y adulto (1,70 m)
  const escala = p.mat({ color: 0x8f969c, transparent: true, opacity: 0.2, roughness: 1, depthWrite: false });
  const figura = (alto, x, z) => {
    const r = alto * 0.11;
    const c = new THREE.Mesh(new THREE.CapsuleGeometry(r, alto * 0.62 - r * 2, 6, 16), escala);
    c.position.set(x, alto * 0.31 + 0.02, z);
    const cab = new THREE.Mesh(new THREE.SphereGeometry(alto * 0.075, 20, 16), escala);
    cab.position.set(x, alto * 0.86, z);
    p.add(c); p.add(cab);
  };
  figura(1.2, -0.9, 0.45);
  figura(1.7, 0.95, 0.5);
  return p;
}

// ---------- Vistas ligadas a las secciones ----------
const VISTAS = {
  familia:    { cam: [3.4, 2.4, 4.4], obj: [-0.3, 0.75, -0.8], foco: null },
  mesa:       { cam: [1.2, 1.2, 1.5], obj: [0, 0.6, 0], foco: ['mesa'] },
  luz:        { cam: [0.0, 0.62, 1.45], obj: [0, 0.42, 0], foco: ['mesa'], pulso: true },
  planta:     { cam: [0.0, 2.05, 0.02], obj: [0, 0.8, 0], foco: ['mesa'] },
  vendedor:   { cam: [-0.95, 1.15, -1.2], obj: [0, 0.45, -0.1], foco: ['mesa'] },
  mueble:     { cam: [0.55, 1.45, 0.95], obj: [-0.61, 1.0, -1.75], foco: ['mueble-a'] },
  modular:    { cam: [0.0, 1.55, 2.0], obj: [0, 1.0, -1.75], foco: ['mueble-a', 'mueble-b'] },
  sobremesa:  { cam: [2.95, 1.32, -0.15], obj: [2.35, 1.0, -0.85], foco: ['sobremesa'] },
  kids:       { cam: [-1.05, 1.25, 1.35], obj: [-2.3, 0.7, -0.55], foco: ['kids'] },
  logo:       { cam: [1.25, 0.5, 0.3], obj: [0.4, 0.4, 0], foco: ['mesa'] },
  materiales: { cam: [0.85, 1.0, 0.75], obj: [0.38, 0.72, 0.22], foco: ['mesa'] },
  despiece:   { cam: [1.7, 1.45, 1.9], obj: [0, 0.75, 0], foco: ['mesa'], despiece: true },
};

function cargar(url) {
  return new THREE.TextureLoader().loadAsync(url).then((t) => { t.colorSpace = THREE.SRGBColorSpace; return t; });
}

function texturaHalo(logo) {
  const img = logo.image;
  const W = 1024, H = Math.round(W * PROPORCION_LOGO * 1.9 / 1.18);
  const c = document.createElement('canvas');
  c.width = W; c.height = H;
  const g = c.getContext('2d');
  const w = W / 1.18, h = w * PROPORCION_LOGO;
  g.filter = 'blur(18px)';
  g.drawImage(img, (W - w) / 2, (H - h) / 2, w, h);
  g.globalCompositeOperation = 'source-in';
  g.filter = 'none';
  g.fillStyle = '#ffffff';
  g.fillRect(0, 0, W, H);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

export function crearEscena(contenedor, { onListo } = {}) {
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 0.95;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  contenedor.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xf1ebe2);
  scene.environment = new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(renderer), 0.04).texture;

  const camera = new THREE.PerspectiveCamera(38, 1, 0.05, 50);
  camera.position.set(...VISTAS.familia.cam);
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.target.set(...VISTAS.familia.obj);
  controls.enableDamping = true;
  controls.minDistance = 0.4;
  controls.maxDistance = 9;
  controls.maxPolarAngle = Math.PI * 0.495;

  scene.add(new THREE.HemisphereLight(0xfffaf2, 0xd7c6ab, 0.55));
  const sol = new THREE.DirectionalLight(0xfff4e6, 1.3);
  sol.position.set(2.5, 4.5, 3);
  sol.castShadow = true;
  sol.shadow.mapSize.set(2048, 2048);
  Object.assign(sol.shadow.camera, { left: -4.5, right: 4.5, top: 4.5, bottom: -4.5 });
  sol.shadow.bias = -0.0004;
  sol.shadow.radius = 6;
  scene.add(sol);

  const piso = new THREE.Mesh(new THREE.PlaneGeometry(14, 14), new THREE.MeshStandardMaterial({ color: COLOR.piso, roughness: 0.85 }));
  piso.rotation.x = -Math.PI / 2;
  piso.receiveShadow = true;
  scene.add(piso);
  const muro = new THREE.Mesh(new THREE.PlaneGeometry(14, 3.2), new THREE.MeshStandardMaterial({ color: COLOR.muro, roughness: 0.95 }));
  muro.position.set(0, 1.6, -1.97);
  muro.receiveShadow = true;
  scene.add(muro);
  const mostrador = new THREE.Mesh(new RoundedBoxGeometry(1.1, 0.9, 0.55, 4, 0.02), new THREE.MeshStandardMaterial({ color: COLOR.mostrador, roughness: 0.15 }));
  mostrador.position.set(2.35, 0.45, -0.85);
  mostrador.castShadow = mostrador.receiveShadow = true;
  scene.add(mostrador);

  const piezas = {};
  const brillos = [];
  const halo = (x, y, z, color = COLOR.luz5000, i = 0.6) => {
    const l = new THREE.PointLight(color, i, 1.7, 2);
    l.position.set(x, y, z);
    l.userData.base = i;
    scene.add(l);
    brillos.push(l);
  };

  const ARTES = {
    arteMesa: 'artes-cubitt/a-la-talla/mesa-frente-viva-pro-2.jpg',
    arteFondoViva: 'artes-cubitt/a-la-talla/mueble-fondo-viva-pro-2.jpg',
    arteFondoNuevaEra: 'artes-cubitt/a-la-talla/mueble-fondo-nueva-era.jpg',
    arteLateralAura: 'artes-cubitt/a-la-talla/mueble-lateral-aura-pro-2.jpg',
    arteLateralTerra: 'artes-cubitt/a-la-talla/mueble-lateral-terra.jpg',
    arteSobremesa: 'artes-cubitt/a-la-talla/sobremesa-viva-pro-2.jpg',
    arteJr: 'artes-cubitt/a-la-talla/kids-rapunzel.jpg',
    duna: 'assets/materiales/duna.jpg',
    logo: 'assets/logo/logo-cubitt-platino.png',
  };
  const NOMBRES = ['viva-pro-2', 'viva-2-rosado', 'viva-lite-lilac', 'aura-2-azul', 'aura-pro-2', 'terra-verde',
    'power-go-2', 'power-pro-2', 'power-plus-2', 'power-mini', 'power-anc-negro', 'power-anc-crema', 'power-buds-2',
    'termo-burgandy', 'coffee-mug-verde', 'jr-rapunzel', 'jr-paw-patrol', 'jr-artic-blue', 'teens-forest-green',
    'headphones-jr-pink', 'hydro-bottle-jr-rapunzel', 'hydro-bottle-jr-paw-patrol', 'tumbler-jr-pink', 'mug-jr-azul'];

  Promise.all([
    ...Object.entries(ARTES).map(([k, u]) => cargar(ruta(u)).then((t) => [k, t])),
    ...NOMBRES.map((n) => cargar(ruta(`artes-cubitt/productos/${n}.png`)).then((t) => { PRODUCTOS[n] = t; return null; })),
  ]).then((res) => {
    const tx = Object.fromEntries(res.filter(Boolean));
    tx.logo.anisotropy = renderer.capabilities.getMaxAnisotropy();
    LOGO = tx.logo;
    HALO = texturaHalo(tx.logo);

    piezas.mesa = crearMesa(tx);
    piezas['mueble-a'] = crearMueble(tx, 'mueble-a', { arteFondo: tx.arteFondoViva, arteLateral: tx.arteLateralAura, lado: -1, conLogo: true,
      productos: ['viva-pro-2', 'viva-2-rosado', 'viva-lite-lilac', 'power-buds-2', 'termo-burgandy'] });
    piezas['mueble-b'] = crearMueble(tx, 'mueble-b', { arteFondo: tx.arteFondoNuevaEra, arteLateral: tx.arteLateralTerra, lado: 1, conLogo: false,
      productos: ['terra-verde', 'aura-2-azul', 'aura-pro-2', 'power-anc-crema', 'coffee-mug-verde'] });
    piezas.sobremesa = crearSobremesa(tx);
    piezas.kids = crearKids(tx);
    piezas['mueble-a'].grupo.position.set(-0.61, 0, -1.75);
    piezas['mueble-b'].grupo.position.set(0.61, 0, -1.75);
    piezas.sobremesa.grupo.position.set(2.35, 0.9, -0.85);
    piezas.kids.grupo.position.set(-2.3, 0, -0.55);
    piezas.kids.grupo.rotation.y = 0.55;
    Object.values(piezas).forEach((p) => scene.add(p.grupo));
    halo(0, 0.4, 0.6);
    halo(-0.61, 1.15, -1.4);
    halo(0.61, 1.15, -1.4);
    halo(2.35, 1.1, -0.65, COLOR.luz5000, 0.35);
    halo(-2.1, 1.1, -0.35);
    halo(0.62, 0.4, 0, COLOR.luz3000, 0.35);
    halo(-0.62, 0.4, 0, COLOR.luz3000, 0.35);
    onListo?.();
  });

  const estado = {
    desde: { cam: camera.position.clone(), obj: controls.target.clone() },
    hacia: null, t: 1,
    despiece: 0, despieceMeta: 0,
    luz: 1, luzMeta: 1,
    foco: null, pulso: false,
  };

  function irA(nombre) {
    const v = VISTAS[nombre] || VISTAS.familia;
    estado.desde = { cam: camera.position.clone(), obj: controls.target.clone() };
    estado.hacia = { cam: new THREE.Vector3(...v.cam), obj: new THREE.Vector3(...v.obj) };
    estado.t = 0;
    estado.foco = v.foco;
    estado.pulso = !!v.pulso;
    estado.despieceMeta = v.despiece ? 1 : 0;
  }

  const suave = (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
  function ajustarTam() {
    const w = contenedor.clientWidth, h = contenedor.clientHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }
  new ResizeObserver(ajustarTam).observe(contenedor);
  ajustarTam();
  controls.addEventListener('start', () => { estado.t = 1; });

  const reloj = new THREE.Clock();
  let visible = true;
  new IntersectionObserver(([e]) => { visible = e.isIntersecting; }).observe(contenedor);

  renderer.setAnimationLoop(() => {
    if (!visible) return;
    const dt = Math.min(reloj.getDelta(), 0.25);
    const k4 = 1 - Math.exp(-dt * 4);
    const tiempo = reloj.elapsedTime;

    if (estado.hacia && estado.t < 1) {
      estado.t = Math.min(1, estado.t + dt / 1.3);
      const k = suave(estado.t);
      camera.position.lerpVectors(estado.desde.cam, estado.hacia.cam, k);
      controls.target.lerpVectors(estado.desde.obj, estado.hacia.obj, k);
    }
    estado.despiece += (estado.despieceMeta - estado.despiece) * (1 - Math.exp(-dt * 3));
    estado.luz += (estado.luzMeta - estado.luz) * k4;
    const pulso = estado.pulso ? 0.8 + 0.2 * Math.sin(tiempo * 2.2) : 1;
    const luz = Math.max(0.06, estado.luz);

    for (const [nombre, p] of Object.entries(piezas)) {
      const meta = !estado.foco || estado.foco.includes(nombre) ? 1 : 0.1;
      for (const m of p.materiales) {
        if (m.userData.op === undefined) m.userData.op = m.opacity;
        const actual = m.userData.actual ?? 1;
        const nuevo = actual + (meta - actual) * k4;
        m.userData.actual = nuevo;
        const transparente = nuevo < 0.999 || m.userData.op < 1 || m.alphaTest > 0 || m.blending === THREE.AdditiveBlending || m.isSpriteMaterial;
        if (m.transparent !== transparente) { m.transparent = transparente; m.needsUpdate = true; }
        m.opacity = m.userData.op * nuevo;
        if (!m.isSpriteMaterial && m.blending !== THREE.AdditiveBlending) m.depthWrite = nuevo > 0.5;
      }
      for (const m of p.cajasLuz) m.emissiveIntensity = 1.05 * luz * pulso;
      for (const m of p.lineas) m.emissiveIntensity = 1.2 * luz;
      for (const m of p.halos) m.opacity = 0.85 * estado.luz * (m.userData.actual ?? 1);
      const d = nombre === 'mesa' ? estado.despiece : 0;
      for (const parte of p.partes) parte.obj.position.copy(parte.base).addScaledVector(parte.despiece, d);
    }
    for (const l of brillos) l.intensity = l.userData.base * estado.luz * pulso;

    controls.update();
    renderer.render(scene, camera);
  });

  return {
    irA,
    setLuz: (on) => { estado.luzMeta = on ? 1 : 0; },
    setDespiece: (on) => { estado.despieceMeta = on ? 1 : 0; },
    getLuz: () => estado.luzMeta === 1,
    getDespiece: () => estado.despieceMeta === 1,
  };
}

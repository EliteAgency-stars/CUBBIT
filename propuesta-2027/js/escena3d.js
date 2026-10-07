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
// bordeY: borde de arriba y abajo cuando el marco no es igual en los cuatro lados (caja de luz del muro).
function cajaDeLuz(p, w, h, arte, x, y, z, rotY = 0, despiece, { borde = 0.022, bordeY = borde, fondo = 0.03, radio = 0.045 } = {}) {
  const r = Math.min(radio, h / 4);
  const anillo = rectRedondeado(w, h, r);
  anillo.holes.push(rectRedondeado(w - borde * 2, h - bordeY * 2, r - borde * 0.6));
  const bisel = Math.min(0.004, borde / 3);
  const geoMarco = new THREE.ExtrudeGeometry(anillo, { depth: fondo, bevelEnabled: true, bevelThickness: bisel, bevelSize: bisel, bevelSegments: 2, curveSegments: 10 });
  const alu = p.mat({ color: COLOR.aluminio, metalness: 0.9, roughness: 0.32 });
  const marco = new THREE.Mesh(geoMarco, alu);
  const wi = w - borde * 2, hi = h - bordeY * 2;
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

// Logo oficial Cubitt en platino con halo cálido 3000K. tipo 'isotipo': la retícula de puntos recortada del mismo
// archivo oficial (tools/preparar_isotipo.py), que los SketchUp ponen en los laterales del mueble y en la espalda del display.
const LOGOS = {
  logo: { tex: null, halo: null, proporcion: 951 / 4154, halo_w: 1.18, halo_h: 1.9 },
  isotipo: { tex: null, halo: null, proporcion: 300 / 338, halo_w: 1.3, halo_h: 1.34 },
};
function logoPlatino(p, ancho, x, y, z, rotY = 0, despiece, separacion = 0.012, tipo = 'logo') {
  const L = LOGOS[tipo];
  const g = new THREE.Group();
  const alto = ancho * L.proporcion;
  const halo = p.mat(new THREE.MeshBasicMaterial({ map: L.halo, color: COLOR.luz3000, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false }), 'halo');
  const mHalo = new THREE.Mesh(new THREE.PlaneGeometry(ancho * L.halo_w, alto * L.halo_h), halo);
  const letras = p.mat({ map: L.tex, transparent: true, alphaTest: 0.35, metalness: 0.8, roughness: 0.28, color: 0xdedad3 });
  const mLetras = new THREE.Mesh(new THREE.PlaneGeometry(ancho, alto), letras);
  mLetras.position.z = separacion;
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

// ---------- 01 · Mesa de experiencia 100 × 78,8 × 50 (SketchUp «mesa cubitt») ----------
// Medidas tomadas del archivo: base recta Capri 100 × 50 × 70,2 cm sobre zócalo inox de 5 cm, línea de sombra
// rehundida con LED 3000K, tope Duna de 18 mm con esquinas R40, caja de luz frontal a ras de 84,9 × 58,1 cm
// (tela 82,4 × 56,1 cm), logo platino en ambos laterales, elevador Duna 91 × 18,8 × 5 cm al fondo con el audio
// y cinco fichas acrílicas, nueve relojes al frente con su ficha y dos puertas push atrás.
const RELOJES_MESA = ['viva-pro-2', 'viva-2-rosado', 'viva-lite-lilac', 'aura-2-azul', 'aura-pro-2', 'terra-verde', 'viva-pro-2', 'aura-pro-2', 'terra-verde'];
function crearMesa(tx) {
  const p = new Pieza('mesa');
  const capri = p.mat({ color: COLOR.capri, roughness: 0.8 });
  const duna = p.mat(materialDuna(tx.duna));
  const sombra = p.mat({ color: 0x8f8579, roughness: 0.9 });
  const inox = p.mat({ color: COLOR.inox, metalness: 1, roughness: 0.22 });
  const acrilico = p.mat({ color: 0xffffff, transparent: true, opacity: 0.35, roughness: 0.05 });

  cuerpo(p, 1.0, 0.05, 0.5, inox, 0, 0, 0, [0, -0.25, 0], 0.04);
  cuerpo(p, 1.0, 0.702, 0.5, capri, 0, 0.05, 0, undefined, 0.002);
  cuerpo(p, 0.925, 0.018, 0.44, sombra, 0, 0.752, 0, [0, 0.25, 0], 0.01);
  lineaLed(p, 0.905, 0, 0.765, 0.222, [0, 0.25, 0]);
  lineaLed(p, 0.905, 0, 0.765, -0.222, [0, 0.25, 0]);
  cuerpo(p, 1.0, 0.018, 0.5, duna, 0, 0.77, 0, [0, 0.4, 0], 0.04);
  // Frente: caja de luz a ras con el arte Viva Pro 2 a la talla (82,4 × 56,1 cm de tela)
  cajaDeLuz(p, 0.849, 0.581, tx.arteMesa, 0, 0.401, 0.247, 0, [0, 0, 0.3], { borde: 0.011, fondo: 0.006, radio: 0.04 });
  // Laterales Capri con logo platino 3000K (36,5 cm, centrado a 40 cm de alto)
  logoPlatino(p, 0.365, 0.502, 0.4, -0.0096, Math.PI / 2, [0.22, 0, 0]);
  logoPlatino(p, 0.365, -0.502, 0.4, -0.0096, -Math.PI / 2, [-0.22, 0, 0]);
  // Elevador Duna al fondo: audio adelante y cinco fichas acrílicas detrás, como en el SketchUp
  const yTop = 0.788, yRiser = 0.838;
  p.caja(0.91, 0.05, 0.188, duna, 0.0069, 0.813, -0.1464, 0.003, [0, 0.55, 0]);
  producto(p, 'power-buds-2', 0.07, -0.353, yRiser, -0.121, { base: null, despiece: [0, 0.72, 0] });
  producto(p, 'power-pro-2', 0.13, -0.117, yRiser, -0.117, { base: null, despiece: [0, 0.72, 0] });
  producto(p, 'power-plus-2', 0.2, 0.092, yRiser, -0.124, { base: null, despiece: [0, 0.72, 0] });
  producto(p, 'power-go-2', 0.09, 0.223, yRiser, -0.121, { base: null, despiece: [0, 0.72, 0] });
  producto(p, 'power-anc-negro', 0.2, 0.386, yRiser, -0.127, { base: null, despiece: [0, 0.72, 0] });
  [0.385, 0.224, 0.089, -0.114, -0.353].forEach((x) => p.caja(0.08, 0.004, 0.05, acrilico, x, yRiser + 0.002, -0.2006, 0.001, [0, 0.72, 0]));
  // Relojes al frente: nueve checkpoints con ficha acrílica delante
  [-0.4368, -0.3238, -0.2158, -0.1098, 0.0012, 0.1097, 0.2152, 0.3197, 0.4312].forEach((x, i) => {
    producto(p, RELOJES_MESA[i], 0.075, x, yTop, 0.1039, { despiece: [0, 0.6, 0] });
    p.caja(0.08, 0.004, 0.08, acrilico, x + 0.001, yTop + 0.002, 0.1774, 0.001, [0, 0.6, 0]);
  });
  // Lado vendedor: dos puertas push (sin manijas)
  p.caja(0.003, 0.65, 0.002, sombra, 0, 0.401, -0.251, 0, [0, 0, -0.12]);
  p.caja(0.948, 0.003, 0.002, sombra, 0, 0.076, -0.251, 0, [0, 0, -0.12]);
  p.caja(0.948, 0.003, 0.002, sombra, 0, 0.726, -0.251, 0, [0, 0, -0.12]);
  return p;
}

// ---------- 02 · Mueble de exhibición 120 × 148,6 × 40 (SketchUp «mueble cubitt») ----------
// Módulo de 120 cm: mesón como la mesa (base recta Capri sobre zócalo inox, línea de sombra con LED 3000K y tope Duna
// a 78,8 cm), frente liso con el logo platino, isotipo en los laterales, dos puertas push atrás, elevador Duna al fondo
// y caja de luz trasera de 120 × 64,8 cm sobre cinco postes. Funciona solo o en composición: dos módulos iguales lado a
// lado (240 cm), con el logo al frente de cada módulo y el isotipo solo en los laterales exteriores.
function crearMueble(tx, nombre, { arte, isotipos = [-1, 1], relojes }) {
  const p = new Pieza(nombre);
  const capri = p.mat({ color: COLOR.capri, roughness: 0.8 });
  const duna = p.mat(materialDuna(tx.duna));
  const sombra = p.mat({ color: 0x8f8579, roughness: 0.9 });
  const inox = p.mat({ color: COLOR.inox, metalness: 1, roughness: 0.22 });
  const alu = p.mat({ color: COLOR.aluminio, metalness: 0.9, roughness: 0.32 });
  const acrilico = p.mat({ color: 0xffffff, transparent: true, opacity: 0.35, roughness: 0.05 });

  cuerpo(p, 1.2, 0.05, 0.399, inox, 0, 0, 0, undefined, 0.04);
  cuerpo(p, 1.2, 0.702, 0.399, capri, 0, 0.05, 0, undefined, 0.002);
  cuerpo(p, 1.145, 0.018, 0.339, sombra, 0, 0.752, 0, undefined, 0.01);
  lineaLed(p, 1.125, 0.002, 0.765, 0.1705);
  lineaLed(p, 1.125, 0.002, 0.765, -0.1705);
  cuerpo(p, 1.2, 0.018, 0.399, duna, 0, 0.77, 0, undefined, 0.045);
  // Frente liso con el logo platino 3000K (44,9 cm, centrado a 43,9 cm de alto); atrás, dos puertas push
  logoPlatino(p, 0.449, 0, 0.4388, 0.2005, 0);
  p.caja(0.003, 0.65, 0.002, sombra, 0, 0.401, -0.2005, 0);
  // Elevador Duna al fondo y caja de luz trasera sobre cinco postes de aluminio
  const yTop = 0.788, yRiser = 0.838;
  p.caja(1.124, 0.05, 0.14, duna, -0.01, 0.813, -0.0885, 0.003);
  [-0.4955, -0.2721, -0.0283, 0.2517, 0.5105].forEach((x) => {
    const poste = new THREE.Mesh(new THREE.CylinderGeometry(0.006, 0.006, 0.05, 16), alu);
    poste.position.set(x, 0.813, -0.1735);
    p.add(poste);
  });
  cajaDeLuz(p, 1.2, 0.648, arte, 0, 1.162, -0.1795, 0, undefined, { borde: 0.0095, fondo: 0.007, radio: 0.06 });
  // Isotipo platino 3000K en los laterales (13,6 cm, centrado a 43,4 cm); en composición, solo en los exteriores
  isotipos.forEach((lado) => logoPlatino(p, 0.136, lado * 0.602, 0.4336, 0.0083, lado * Math.PI / 2, undefined, 0.012, 'isotipo'));
  // Productos como en el SketchUp: ocho relojes al frente con ficha acrílica y audio sobre el elevador
  [-0.5305, -0.4005, -0.2615, -0.1105, 0.0355, 0.1655, 0.3045, 0.4555].forEach((x, i) => {
    producto(p, relojes[i % relojes.length], 0.075, x, yTop, 0.0725);
    p.caja(0.08, 0.004, 0.05, acrilico, x, yTop + 0.002, 0.1375, 0.001);
  });
  producto(p, 'power-anc-negro', 0.2, -0.444, yRiser, -0.0675, { base: null });
  producto(p, 'power-buds-2', 0.07, -0.278, yRiser, -0.1055, { base: null });
  producto(p, 'power-pro-2', 0.13, -0.02, yRiser, -0.1005, { base: null });
  producto(p, 'power-plus-2', 0.2, 0.211, yRiser, -0.0795, { base: null });
  producto(p, 'power-go-2', 0.09, 0.352, yRiser, -0.08, { base: null });
  producto(p, 'power-mini', 0.085, 0.463, yRiser, -0.08, { base: null });
  return p;
}

// ---------- 03 · Display de sobremesa 50 × 32 × 25 (SketchUp «sobre mesa cubitt») ----------
// Base Capri de 4 cm con esquinas redondas, línea de sombra con LED 3000K, tope Duna de 15 mm, caja de luz de
// aluminio de 50 × 25 cm atrás (tela 48,5 × 23,5 cm) con el arte Nueva Era, espalda Capri con el isotipo platino,
// cinco relojes en dos filas con ficha acrílica y el logo platino al frente de la base.
function crearSobremesa(tx) {
  const p = new Pieza('sobremesa');
  const capri = p.mat({ color: COLOR.capri, roughness: 0.8 });
  const duna = p.mat(materialDuna(tx.duna));
  const sombra = p.mat({ color: 0x8f8579, roughness: 0.9 });
  const acrilico = p.mat({ color: 0xffffff, transparent: true, opacity: 0.35, roughness: 0.05 });
  cuerpo(p, 0.5, 0.04, 0.25, capri, 0, 0, 0, undefined, 0.033);
  cuerpo(p, 0.48, 0.015, 0.23, sombra, 0, 0.04, 0, [0, 0.03, 0], 0.012);
  lineaLed(p, 0.46, 0, 0.0475, 0.116, [0, 0.03, 0]);
  lineaLed(p, 0.46, 0, 0.0475, -0.116, [0, 0.03, 0]);
  cuerpo(p, 0.5, 0.015, 0.25, duna, 0, 0.055, 0, [0, 0.06, 0], 0.017);
  cajaDeLuz(p, 0.5, 0.25, tx.arteSobremesa, 0, 0.195, -0.1106, 0, [0, 0.14, -0.06], { borde: 0.0075, fondo: 0.0099, radio: 0.03 });
  // Espalda de la caja de luz en Capri con el isotipo platino 3000K (9 cm, centrado a 19,3 cm)
  const espalda = new THREE.Mesh(new THREE.ShapeGeometry(rectRedondeado(0.5, 0.25, 0.03), 10), capri);
  espalda.position.set(0, 0.195, -0.1108);
  espalda.rotation.y = Math.PI;
  p.add(espalda, [0, 0.14, -0.06]);
  logoPlatino(p, 0.0902, 0, 0.193, -0.1112, Math.PI, [0, 0.14, -0.06], 0.004, 'isotipo');
  // Sin banda superior: el logo platino (9,4 cm) va al frente de la base Capri, bajo la línea LED
  logoPlatino(p, 0.0944, 0, 0.0199, 0.1255, 0, undefined, 0.003);
  // Cinco relojes en dos filas, cada uno con su ficha acrílica delante (los de la Nueva Era)
  [['viva-2-rosado', -0.1829, 0.0255, 0.0815], ['viva-pro-2', 0.0091, 0.0255, 0.0815], ['aura-2-azul', 0.1731, 0.0255, 0.0815],
    ['terra-verde', -0.0839, -0.066, -0.0105], ['aura-pro-2', 0.0941, -0.066, -0.0105]].forEach(([n, x, z, zf]) => {
    producto(p, n, 0.065, x, 0.07, z, { despiece: [0, 0.14, 0] });
    p.caja(0.08, 0.004, 0.05, acrilico, x - 0.0025, 0.072, zf, 0.001, [0, 0.14, 0]);
  });
  return p;
}

// ---------- Bonus · Muro de exhibición 220 × 248 × 49 (SketchUp «cuarto mueble mesa cubitt») ----------
// Mueble de pared: mesón Capri con cuatro puertas push sobre zócalo (frente inox) y tope Duna a 79,4 cm, repisa flotante
// de 168 cm a 1,26 m (base Capri, línea de sombra con LED 3000K y tope Duna) con el audio, caja de luz de 208,8 × 60 cm con
// el arte Nueva Era, cabecera de 30 cm con LED hacia abajo y el logo platino de 64,5 cm. El lateral izquierdo y el interior
// del mesón van en melamina Nácar, como en el SketchUp.
const RELOJES_MURO = ['viva-pro-2', 'viva-2-rosado', 'viva-lite-lilac', 'aura-2-azul', 'aura-pro-2', 'terra-verde', 'viva-pro-2', 'aura-pro-2', 'terra-verde', 'viva-2-rosado'];
function crearMuro(tx) {
  const p = new Pieza('muro');
  const capri = p.mat({ color: COLOR.capri, roughness: 0.8 });
  const duna = p.mat(materialDuna(tx.duna));
  const nacar = p.mat({ color: 0xffffff, map: tx.nacar, roughness: 0.65 });
  const sombra = p.mat({ color: 0x8f8579, roughness: 0.9 });
  const inox = p.mat({ color: COLOR.inox, metalness: 1, roughness: 0.22 });
  const alu = p.mat({ color: COLOR.aluminio, metalness: 0.9, roughness: 0.32 });
  const acrilico = p.mat({ color: 0xffffff, transparent: true, opacity: 0.35, roughness: 0.05 });
  const led = p.mat({ color: COLOR.luz3000, emissive: COLOR.luz3000, emissiveIntensity: 1.2 }, 'linea');
  // Zócalo: frente inox y cuerpo Nácar
  p.caja(2.17, 0.0497, 0.022, inox, 0, 0.025, 0.2196, 0);
  p.caja(2.17, 0.0497, 0.426, nacar, 0, 0.025, -0.0047, 0);
  // Mesón: cuerpo Nácar, cuatro puertas push Capri, banda Capri, gola rehundida de 5 cm (frente Capri 6,6 cm atrás) y tope Duna de 18 mm
  p.caja(2.17, 0.676, 0.454, nacar, 0, 0.0497 + 0.338, -0.004, 0);
  [[3.11, 54.65], [56.19, 106.89], [108.42, 160], [161.5, 218.5]].forEach(([a, b]) => {
    p.caja((b - a) / 100, 0.6462, 0.015, capri, -((a + b) / 2 - 110) / 100, 0.0647 + 0.3231, 0.2231, 0.002);
  });
  p.caja(2.17, 0.015, 0.469, capri, 0, 0.7184, 0.0, 0);
  p.caja(2.17, 0.05, 0.4024, capri, 0, 0.7509, -0.0369, 0);
  p.caja(2.17, 0.018, 0.469, duna, 0, 0.7849, 0.0, 0.002);
  // Laterales: el izquierdo en Nácar y el derecho en Capri (así vienen en el SketchUp), espalda Capri y cabecera
  p.caja(0.015, 2.18, 0.452, nacar, -1.0925, 1.09, 0.0081, 0);
  p.caja(0.015, 2.18, 0.4763, capri, 1.0925, 1.09, 0, 0);
  p.caja(2.17, 1.3681, 0.0243, capri, 0, 0.8119 + 0.684, -0.172, 0);
  p.caja(2.2, 0.30, 0.4764, capri, 0, 2.33, 0, 0.002);
  p.caja(2.17, 0.01, 0.004, alu, 0, 2.235, 0.2365, 0);
  p.caja(2.17, 0.004, 0.0133, led, 0, 2.178, 0.1641, 0);
  logoPlatino(p, 0.645, 0, 2.3645, 0.2392, 0, undefined, 0.012);
  // Caja de luz con el arte Nueva Era a la talla (tela 206,7 × 56,8 cm)
  cajaDeLuz(p, 2.0875, 0.60, tx.arteMuro, -0.0069, 1.8197, -0.1599, 0, undefined, { borde: 0.0105, bordeY: 0.0158, fondo: 0.0086, radio: 0.05 });
  // Repisa flotante: base Capri, línea de sombra con LED 3000K y tope Duna (esquinas redondas)
  cuerpo(p, 1.6826, 0.04, 0.25, capri, 0.021, 1.1889, -0.0349, undefined, 0.033);
  cuerpo(p, 1.6154, 0.015, 0.23, sombra, 0.021, 1.2289, -0.0349, undefined, 0.012);
  lineaLed(p, 1.5954, 0.021, 1.2364, 0.0811);
  lineaLed(p, 1.5954, 0.021, 1.2364, -0.1509);
  cuerpo(p, 1.6826, 0.015, 0.25, duna, 0.021, 1.2439, -0.0349, undefined, 0.017);
  // Audio sobre la repisa, con sus fichas acrílicas al frente
  const yRepisa = 1.2589;
  [-0.6119, 0.6941].forEach((x) => producto(p, 'power-pro-2', 0.13, x, yRepisa, -0.0532, { base: null }));
  [-0.3609, -0.1861, -0.0181, 0.1339].forEach((x) => producto(p, 'power-buds-2', 0.07, x, yRepisa, -0.0442, { base: null }));
  producto(p, 'power-go-2', 0.09, 0.2904, yRepisa, -0.0528, { base: null });
  producto(p, 'power-plus-2', 0.2, 0.4197, yRepisa, -0.0526, { base: null });
  [0.702, 0.43, 0.285, 0.13, -0.02, -0.185, -0.371, -0.604].forEach((x) => p.caja(0.08, 0.004, 0.05, acrilico, x, yRepisa + 0.002, 0.0346, 0.001));
  // Mesón: diez relojes en checkpoint con su ficha y Power ANC en soportes acrílicos a los dos lados
  const yTope = 0.7939;
  [-0.6178, -0.4624, -0.3299, -0.1999, -0.0609, 0.0871, 0.2271, 0.3761, 0.5191, 0.6671].forEach((x, i) => {
    producto(p, RELOJES_MURO[i], 0.075, x, yTope, 0.018);
    p.caja(0.08, 0.004, 0.05, acrilico, x, yTope + 0.002, 0.12, 0.001);
  });
  [[-0.8728, 0.0436], [0.9367, 0.0436]].forEach(([x, z]) => {
    p.caja(0.142, 0.265, 0.008, acrilico, x, yTope + 0.1325, z, 0.002);
    producto(p, 'power-anc-negro', 0.2, x, yTope + 0.07, z + 0.01, { base: null });
    p.caja(0.08, 0.004, 0.05, acrilico, x, yTope + 0.002, 0.1326, 0.001);
  });
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
  familia:    { cam: [3.2, 2.5, 4.6], obj: [-0.75, 0.85, -0.8], foco: null },
  mesa:       { cam: [1.4, 1.25, 1.75], obj: [0, 0.6, 0], foco: ['mesa'] },
  luz:        { cam: [0.0, 0.62, 1.7], obj: [0, 0.42, 0], foco: ['mesa'], pulso: true },
  planta:     { cam: [0.0, 2.75, 0.02], obj: [0, 0.8, 0], foco: ['mesa'] },
  vendedor:   { cam: [-1.1, 1.2, -1.35], obj: [0, 0.45, -0.1], foco: ['mesa'] },
  mueble:     { cam: [-1.15, 1.35, -0.15], obj: [-0.55, 0.85, -1.75], foco: ['mueble-a'] },
  modular:    { cam: [2.4, 1.75, 1.4], obj: [0.1, 0.95, -1.75], foco: ['mueble-a', 'mueble-b'] },
  sobremesa:  { cam: [2.85, 1.3, -0.2], obj: [2.35, 1.0, -0.85], foco: ['sobremesa'] },
  kids:       { cam: [-0.5, 1.25, 1.35], obj: [-1.75, 0.7, -0.55], foco: ['kids'] },
  muro:       { cam: [0.05, 1.6, 1.75], obj: [-2.95, 1.32, -0.8], foco: ['muro'] },
  logo:       { cam: [1.45, 0.52, 0.32], obj: [0.5, 0.33, 0], foco: ['mesa'] },
  materiales: { cam: [1.1, 1.08, 0.9], obj: [0.46, 0.66, 0.2], foco: ['mesa'] },
  despiece:   { cam: [1.9, 1.5, 2.1], obj: [0, 0.75, 0], foco: ['mesa'], despiece: true },
};

function cargar(url) {
  return new THREE.TextureLoader().loadAsync(url).then((t) => { t.colorSpace = THREE.SRGBColorSpace; return t; });
}

function texturaHalo(logo, { proporcion, halo_w, halo_h }) {
  const img = logo.image;
  const W = 1024, H = Math.round(W * proporcion * halo_h / halo_w);
  const c = document.createElement('canvas');
  c.width = W; c.height = H;
  const g = c.getContext('2d');
  const w = W / halo_w, h = w * proporcion;
  g.filter = `blur(${Math.round(Math.min(w, h) * 0.08)}px)`;
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
  const pared = new THREE.Mesh(new THREE.PlaneGeometry(14, 3.2), new THREE.MeshStandardMaterial({ color: COLOR.muro, roughness: 0.95 }));
  pared.position.set(0, 1.6, -1.97);
  pared.receiveShadow = true;
  scene.add(pared);
  // Pared lateral izquierda, donde va el muro de exhibición (bonus)
  const lateral = new THREE.Mesh(new THREE.PlaneGeometry(5.2, 3.2), new THREE.MeshStandardMaterial({ color: COLOR.muro, roughness: 0.95 }));
  lateral.position.set(-3.2, 1.6, 0.63);
  lateral.rotation.y = Math.PI / 2;
  lateral.receiveShadow = true;
  scene.add(lateral);
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
    arteSobremesa: 'artes-cubitt/a-la-talla/sobremesa-nueva-era.jpg',
    arteJr: 'artes-cubitt/a-la-talla/kids-rapunzel.jpg',
    arteMuro: 'artes-cubitt/a-la-talla/muro-nueva-era.jpg',
    nacar: 'assets/materiales/nacar.jpg',
    duna: 'assets/materiales/duna.jpg',
    logo: 'assets/logo/logo-cubitt-platino.png',
    isotipo: 'assets/logo/isotipo-cubitt-platino.png',
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
    for (const tipo of ['logo', 'isotipo']) {
      tx[tipo].anisotropy = renderer.capabilities.getMaxAnisotropy();
      LOGOS[tipo].tex = tx[tipo];
      LOGOS[tipo].halo = texturaHalo(tx[tipo], LOGOS[tipo]);
    }

    piezas.mesa = crearMesa(tx);
    // Composición de dos módulos iguales lado a lado: logo al frente de cada módulo, isotipo solo en los laterales exteriores
    piezas['mueble-a'] = crearMueble(tx, 'mueble-a', { arte: tx.arteFondoNuevaEra, isotipos: [-1],
      relojes: ['viva-pro-2', 'viva-2-rosado', 'viva-lite-lilac', 'aura-2-azul', 'aura-pro-2', 'terra-verde', 'viva-pro-2', 'aura-pro-2'] });
    piezas['mueble-b'] = crearMueble(tx, 'mueble-b', { arte: tx.arteFondoViva, isotipos: [1],
      relojes: ['terra-verde', 'aura-pro-2', 'aura-2-azul', 'viva-lite-lilac', 'viva-2-rosado', 'viva-pro-2', 'terra-verde', 'viva-pro-2'] });
    piezas.sobremesa = crearSobremesa(tx);
    piezas.kids = crearKids(tx);
    piezas.muro = crearMuro(tx);
    piezas['mueble-a'].grupo.position.set(-0.6, 0, -1.75);
    piezas['mueble-b'].grupo.position.set(0.6, 0, -1.75);
    piezas.sobremesa.grupo.position.set(2.35, 0.9, -0.85);
    piezas.kids.grupo.position.set(-1.75, 0, -0.55);
    piezas.kids.grupo.rotation.y = 0.55;
    // El muro va contra la pared lateral izquierda, mirando hacia la tienda
    piezas.muro.grupo.position.set(-2.9618, 0, -0.8);
    piezas.muro.grupo.rotation.y = Math.PI / 2;
    Object.values(piezas).forEach((p) => scene.add(p.grupo));
    halo(0, 0.4, 0.6);
    halo(-0.6, 1.16, -1.5);
    halo(0.6, 1.16, -1.5);
    halo(2.35, 1.1, -0.65, COLOR.luz5000, 0.35);
    halo(-1.55, 1.1, -0.35);
    halo(-2.55, 1.82, -0.8, COLOR.luz5000, 0.5);
    halo(-2.55, 2.1, -0.8, COLOR.luz3000, 0.35);
    halo(0.72, 0.4, 0, COLOR.luz3000, 0.35);
    halo(-0.72, 0.4, 0, COLOR.luz3000, 0.35);
    halo(-0.6, 0.44, -1.4, COLOR.luz3000, 0.3);
    halo(0.6, 0.44, -1.4, COLOR.luz3000, 0.3);
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

// Escena 3D paramétrica de la familia Cubitt 2027 (unidades en metros, medidas del brief).
// La cámara, la luz y el despiece responden a la sección que se está leyendo.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const COLOR = {
  arena: 0xcbb18c,
  roble: 0xc99c6c,
  aluminio: 0xc4c2bd,
  opal: 0xfff3e2,
  piso: 0xd3bea0,
  muro: 0xefe6d8,
  mostrador: 0xf7f5f1,
  producto: 0x55534f,
};

const R30 = 0.03;

// ---------- Texturas ----------

function texturaRoble() {
  const c = document.createElement('canvas');
  c.width = 512; c.height = 512;
  const g = c.getContext('2d');
  g.fillStyle = '#c99c6c';
  g.fillRect(0, 0, 512, 512);
  for (let i = 0; i < 140; i++) {
    const y = Math.random() * 512;
    g.strokeStyle = `rgba(${120 + Math.random() * 40},${80 + Math.random() * 30},${40 + Math.random() * 20},${0.08 + Math.random() * 0.12})`;
    g.lineWidth = 0.5 + Math.random() * 2.5;
    g.beginPath();
    g.moveTo(0, y);
    for (let x = 0; x <= 512; x += 32) g.lineTo(x, y + Math.sin(x / 70 + i) * 3);
    g.stroke();
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  return t;
}

// ---------- Utilidades de construcción ----------

class Pieza {
  constructor(nombre) {
    this.nombre = nombre;
    this.grupo = new THREE.Group();
    this.grupo.name = nombre;
    this.partes = [];       // { obj, base: Vector3, despiece: Vector3 }
    this.materiales = [];
    this.paneles = [];      // materiales emisivos de lámina opal
  }
  mat(params, emisivo = false) {
    const m = new THREE.MeshStandardMaterial(params);
    this.materiales.push(m);
    if (emisivo) this.paneles.push(m);
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
  plano(w, h, material, x, y, z, despiece, rotY = 0) {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), material);
    m.position.set(x, y, z);
    m.rotation.y = rotY;
    return this.add(m, despiece);
  }
}

// Volumen con sólo las aristas verticales redondeadas (R30): extrusión de un rectángulo redondeado en planta.
function geoCuerpo(w, h, d, r = R30) {
  const s = new THREE.Shape();
  const x = -w / 2, z = -d / 2;
  s.moveTo(x + r, z);
  s.lineTo(x + w - r, z);
  s.quadraticCurveTo(x + w, z, x + w, z + r);
  s.lineTo(x + w, z + d - r);
  s.quadraticCurveTo(x + w, z + d, x + w - r, z + d);
  s.lineTo(x + r, z + d);
  s.quadraticCurveTo(x, z + d, x, z + d - r);
  s.lineTo(x, z + r);
  s.quadraticCurveTo(x, z, x + r, z);
  const g = new THREE.ExtrudeGeometry(s, { depth: h, bevelEnabled: false, curveSegments: 10 });
  g.rotateX(Math.PI / 2);
  g.translate(0, h, 0);
  return g;
}

function cuerpo(p, w, h, d, material, x, y, z, despiece) {
  const m = new THREE.Mesh(geoCuerpo(w, h, d), material);
  m.position.set(x, y, z);
  m.castShadow = m.receiveShadow = true;
  return p.add(m, despiece);
}

function reloj(p, x, y, z, matBase, matProd, despiece, alto = 0.085) {
  const g = new THREE.Group();
  const base = new THREE.Mesh(new RoundedBoxGeometry(0.06, 0.012, 0.06, 3, 0.004), matBase);
  base.position.y = 0.006;
  const poste = new THREE.Mesh(new THREE.CylinderGeometry(0.006, 0.006, alto, 12), matBase);
  poste.position.y = alto / 2 + 0.012;
  const caja = new THREE.Mesh(new THREE.CylinderGeometry(0.022, 0.022, 0.012, 32), matProd);
  caja.rotation.x = Math.PI / 2;
  caja.position.set(0, alto + 0.02, 0.012);
  const correa = new THREE.Mesh(new THREE.BoxGeometry(0.022, 0.07, 0.006), matProd);
  correa.position.set(0, alto + 0.02, 0.006);
  [base, poste, caja, correa].forEach((m) => { m.castShadow = true; g.add(m); });
  g.position.set(x, y, z);
  return p.add(g, despiece);
}

// ---------- Logo oficial en platino ----------

function materialLogo(textura, p) {
  return p.mat({
    map: textura,
    transparent: true,
    alphaTest: 0.35,
    metalness: 0.75,
    roughness: 0.3,
    color: 0xd9d5cd,
  });
}
const PROPORCION_LOGO = 951 / 4154;

// ---------- Tipología 01 · Mesa de experiencia 150 × 90 × 70 ----------

function crearMesa(texLogo, texRoble) {
  const p = new Pieza('mesa');
  const arena = p.mat({ color: COLOR.arena, roughness: 0.78 });
  const roble = p.mat({ color: 0xffffff, map: texRoble, roughness: 0.55 });
  const alu = p.mat({ color: COLOR.aluminio, metalness: 0.85, roughness: 0.35 });
  const opal = p.mat({ color: COLOR.opal, emissive: COLOR.opal, emissiveIntensity: 1.1, roughness: 0.4 }, true);
  const opalRiser = p.mat({ color: COLOR.opal, emissive: COLOR.opal, emissiveIntensity: 0.9, roughness: 0.4, transparent: true, opacity: 0.96 }, true);
  const blanco = p.mat({ color: 0xf6f4f0, roughness: 0.3 });
  const prod = p.mat({ color: COLOR.producto, roughness: 0.4, metalness: 0.3 });
  const sombra = p.mat({ color: 0x8c7a62, roughness: 0.9 });

  // Zócalo de aluminio rehundido 6 cm
  p.caja(1.42, 0.06, 0.62, alu, 0, 0.03, 0, 0.01, [0, -0.25, 0]);
  // Cuerpo arena (MDF 18 mm melamina), aristas verticales R30
  cuerpo(p, 1.5, 0.795, 0.7, arena, 0, 0.06, 0, [0, 0, 0]);
  // Línea de sombra 15 mm bajo la cubierta + luz indirecta
  p.caja(1.46, 0.015, 0.66, sombra, 0, 0.8625, 0, 0, [0, 0.25, 0]);
  const linea = p.mat({ color: COLOR.opal, emissive: COLOR.opal, emissiveIntensity: 0.8 }, true);
  p.caja(1.44, 0.004, 0.004, linea, 0, 0.858, 0.332, 0, [0, 0.25, 0]);
  // Cubierta roble 30 mm con esquinas R30 en planta
  cuerpo(p, 1.52, 0.03, 0.72, roble, 0, 0.87, 0, [0, 0.45, 0]);
  // Frente: lámina opal en marco de aluminio
  p.caja(1.38, 0.62, 0.012, alu, 0, 0.47, 0.351, 0.004, [0, 0, 0.3]);
  p.plano(1.34, 0.58, opal, 0, 0.47, 0.3585, [0, 0, 0.3]);
  // Logo platino centrado (ancho 60 cm)
  const wLogo = 0.6;
  p.plano(wLogo, wLogo * PROPORCION_LOGO, materialLogo(texLogo, p), 0, 0.47, 0.362, [0, 0, 0.42]);
  // Elevador opal iluminado para producto héroe
  p.caja(0.62, 0.1, 0.22, opalRiser, 0, 0.95, -0.18, 0.01, [0, 0.62, 0]);
  // Producto
  const yTop = 0.9;
  [-0.55, -0.33, 0.33, 0.55].forEach((x) => reloj(p, x, yTop, 0.12, blanco, prod, [0, 0.8, 0]));
  [-0.12, 0.12].forEach((x) => reloj(p, x, 1.0, -0.18, blanco, prod, [0, 0.95, 0], 0.1));
  // Pasacables
  [-0.44, 0.44].forEach((x) => {
    const g = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.018, 0.002, 24), alu);
    g.position.set(x, 0.901, -0.05);
    p.add(g, [0, 0.45, 0]);
  });
  // Lado vendedor: juntas de puertas y cajón
  [-0.375, 0, 0.375].forEach((x) => p.caja(0.003, 0.56, 0.002, sombra, x, 0.4, -0.351, 0, [0, 0, -0.15]));
  p.caja(1.44, 0.003, 0.002, sombra, 0, 0.69, -0.351, 0, [0, 0, -0.15]);
  return p;
}

// ---------- Tipología 02 · Mueble de exhibición 120 × 140 × 40 ----------

function crearMueble(texLogo, texRoble, conLogo, nombre) {
  const p = new Pieza(nombre);
  const arena = p.mat({ color: COLOR.arena, roughness: 0.78 });
  const roble = p.mat({ color: 0xffffff, map: texRoble, roughness: 0.55 });
  const alu = p.mat({ color: COLOR.aluminio, metalness: 0.85, roughness: 0.35 });
  const opal = p.mat({ color: COLOR.opal, emissive: COLOR.opal, emissiveIntensity: 1.1, roughness: 0.4 }, true);
  const acrilico = p.mat({ color: 0xffffff, transparent: true, opacity: 0.25, roughness: 0.05 });
  const blanco = p.mat({ color: 0xf6f4f0, roughness: 0.3 });
  const prod = p.mat({ color: COLOR.producto, roughness: 0.4, metalness: 0.3 });
  const sombra = p.mat({ color: 0x8c7a62, roughness: 0.9 });
  const termo = p.mat({ color: 0xe9e2d6, roughness: 0.35, metalness: 0.2 });

  p.caja(1.12, 0.06, 0.34, alu, 0, 0.03, 0, 0.01, [0, -0.2, 0]);
  cuerpo(p, 1.2, 0.775, 0.4, arena, 0, 0.06, 0);
  p.caja(0.003, 0.7, 0.002, sombra, 0, 0.45, 0.201, 0);
  cuerpo(p, 1.22, 0.03, 0.42, roble, 0, 0.85, 0, [0, 0.2, 0]);
  // Back panel opal 55 cm (de 0,88 a 1,40 m)
  p.caja(1.2, 0.52, 0.07, alu, 0, 1.14, -0.165, 0.015, [0, 0.4, -0.2]);
  p.plano(1.15, 0.47, opal, 0, 1.14, -0.1295, [0, 0.4, -0.2]);
  if (conLogo) {
    const w = 0.42;
    p.plano(w, w * PROPORCION_LOGO, materialLogo(texLogo, p), 0, 1.31, -0.126, [0, 0.4, -0.12]);
  }
  // Repisa acrílica regulable sobre rieles de aluminio
  [-0.56, 0.56].forEach((x) => p.caja(0.012, 0.4, 0.02, alu, x, 1.12, -0.12, 0.002, [0, 0.4, -0.1]));
  p.caja(1.1, 0.008, 0.16, acrilico, 0, 1.08, -0.05, 0.002, [0, 0.55, 0]);
  reloj(p, 0, 1.084, -0.05, blanco, prod, [0, 0.65, 0], 0.07);
  // Familia sobre el mesón + riel de precio
  [-0.42, -0.24, 0.24].forEach((x) => reloj(p, x, 0.88, 0.05, blanco, prod, [0, 0.3, 0]));
  const t = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.035, 0.24, 32), termo);
  t.position.set(0.44, 1.0, 0.0); t.castShadow = true; p.add(t, [0, 0.3, 0]);
  const aud = new THREE.Mesh(new THREE.TorusGeometry(0.07, 0.012, 12, 40, Math.PI), prod);
  aud.position.set(0.02, 0.9, 0.04); p.add(aud, [0, 0.3, 0]);
  p.caja(1.18, 0.02, 0.008, alu, 0, 0.855, 0.214, 0.002, [0, 0.2, 0.1]);
  return p;
}

// ---------- Tipología 03 · Display de sobremesa 50 × 30 × 25 ----------

function crearSobremesa(texLogo, texRoble) {
  const p = new Pieza('sobremesa');
  const arena = p.mat({ color: COLOR.arena, roughness: 0.78 });
  const roble = p.mat({ color: 0xffffff, map: texRoble, roughness: 0.55 });
  const alu = p.mat({ color: COLOR.aluminio, metalness: 0.85, roughness: 0.35 });
  const opal = p.mat({ color: COLOR.opal, emissive: COLOR.opal, emissiveIntensity: 1.1, roughness: 0.4 }, true);
  const blanco = p.mat({ color: 0xf6f4f0, roughness: 0.3 });
  const prod = p.mat({ color: COLOR.producto, roughness: 0.4, metalness: 0.3 });

  cuerpo(p, 0.5, 0.068, 0.25, arena, 0, 0, 0);
  cuerpo(p, 0.5, 0.012, 0.25, roble, 0, 0.068, 0, [0, 0.08, 0]);
  p.caja(0.5, 0.22, 0.03, alu, 0, 0.08 + 0.11, -0.11, 0.008, [0, 0.16, -0.08]);
  p.plano(0.47, 0.19, opal, 0, 0.19, -0.0945, [0, 0.16, -0.08]);
  const w = 0.3;
  p.plano(w, w * PROPORCION_LOGO, materialLogo(texLogo, p), 0, 0.23, -0.0925, [0, 0.16, -0.05]);
  [-0.15, 0, 0.15].forEach((x) => reloj(p, x, 0.08, 0.02, blanco, prod, [0, 0.14, 0], 0.07));
  p.caja(0.46, 0.022, 0.008, alu, 0, 0.04, 0.128, 0.002, [0, 0, 0.06]);
  return p;
}

// ---------- Vistas ligadas a las secciones ----------

const VISTAS = {
  familia:   { cam: [3.7, 2.2, 3.7], obj: [0.6, 0.7, -0.8], foco: null },
  mesa:      { cam: [1.85, 1.35, 2.25], obj: [0, 0.62, 0], foco: ['mesa'] },
  luz:       { cam: [0.0, 0.72, 2.05], obj: [0, 0.52, 0], foco: ['mesa'], pulso: true },
  vendedor:  { cam: [-1.35, 1.45, -1.2], obj: [0, 0.5, -0.1], foco: ['mesa'] },
  mueble:    { cam: [1.15, 1.35, 0.75], obj: [-0.61, 1.0, -1.75], foco: ['mueble-a'] },
  modular:   { cam: [0.0, 1.45, 1.75], obj: [0, 0.95, -1.75], foco: ['mueble-a', 'mueble-b'] },
  sobremesa: { cam: [2.9, 1.3, 0.0], obj: [2.35, 1.0, -0.85], foco: ['sobremesa'] },
  logo:      { cam: [0.35, 0.6, 1.45], obj: [0, 0.5, 0.35], foco: ['mesa'] },
  materiales:{ cam: [1.05, 1.0, 0.75], obj: [0.72, 0.82, 0.3], foco: ['mesa'] },
  despiece:  { cam: [2.4, 1.75, 2.6], obj: [0, 0.8, 0], foco: ['mesa'], despiece: true },
};

export function crearEscena(contenedor, { onListo } = {}) {
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 0.95;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  contenedor.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xf1e9dd);
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(renderer), 0.04).texture;

  const camera = new THREE.PerspectiveCamera(38, 1, 0.05, 50);
  camera.position.set(...VISTAS.familia.cam);
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.target.set(...VISTAS.familia.obj);
  controls.enableDamping = true;
  controls.minDistance = 0.4;
  controls.maxDistance = 8;
  controls.maxPolarAngle = Math.PI * 0.49;

  // Luces
  scene.add(new THREE.HemisphereLight(0xfffaf2, 0xd7c6ab, 0.5));
  const sol = new THREE.DirectionalLight(0xfff4e6, 1.4);
  sol.position.set(2.5, 4.5, 3);
  sol.castShadow = true;
  sol.shadow.mapSize.set(2048, 2048);
  sol.shadow.camera.left = -4; sol.shadow.camera.right = 4;
  sol.shadow.camera.top = 4; sol.shadow.camera.bottom = -4;
  sol.shadow.bias = -0.0004;
  sol.shadow.radius = 6;
  scene.add(sol);

  // Local: piso SPC beige, muro crema, mostrador de caja
  const piso = new THREE.Mesh(new THREE.PlaneGeometry(12, 12), new THREE.MeshStandardMaterial({ color: COLOR.piso, roughness: 0.85 }));
  piso.rotation.x = -Math.PI / 2;
  piso.receiveShadow = true;
  scene.add(piso);
  const muro = new THREE.Mesh(new THREE.PlaneGeometry(12, 3.2), new THREE.MeshStandardMaterial({ color: COLOR.muro, roughness: 0.95 }));
  muro.position.set(0, 1.6, -1.97);
  muro.receiveShadow = true;
  scene.add(muro);
  const mostrador = new THREE.Mesh(new RoundedBoxGeometry(1.1, 0.9, 0.55, 4, 0.02), new THREE.MeshStandardMaterial({ color: COLOR.mostrador, roughness: 0.15 }));
  mostrador.position.set(2.35, 0.45, -0.85);
  mostrador.castShadow = mostrador.receiveShadow = true;
  scene.add(mostrador);

  const texRoble = texturaRoble();
  const piezas = {};
  const brillo = []; // luces puntuales que simulan el resplandor de las láminas
  const halo = (x, y, z) => {
    const l = new THREE.PointLight(0xfff0dc, 0.6, 1.6, 2);
    l.position.set(x, y, z);
    scene.add(l);
    brillo.push(l);
  };

  new THREE.TextureLoader().load(new URL('../assets/logo/logo-cubitt-platino.png', import.meta.url).href, (texLogo) => {
    texLogo.colorSpace = THREE.SRGBColorSpace;
    texLogo.anisotropy = renderer.capabilities.getMaxAnisotropy();

    piezas.mesa = crearMesa(texLogo, texRoble);
    piezas['mueble-a'] = crearMueble(texLogo, texRoble, true, 'mueble-a');
    piezas['mueble-b'] = crearMueble(texLogo, texRoble, false, 'mueble-b');
    piezas.sobremesa = crearSobremesa(texLogo, texRoble);
    piezas['mueble-a'].grupo.position.set(-0.61, 0, -1.75);
    piezas['mueble-b'].grupo.position.set(0.61, 0, -1.75);
    piezas.sobremesa.grupo.position.set(2.35, 0.9, -0.85);
    Object.values(piezas).forEach((p) => scene.add(p.grupo));
    halo(0, 0.45, 0.7);
    halo(-0.61, 1.15, -1.45);
    halo(0.61, 1.15, -1.45);
    halo(2.35, 1.1, -0.65);
    onListo?.();
  });

  // ---------- Estado animado ----------
  const estado = {
    desde: { cam: camera.position.clone(), obj: controls.target.clone() },
    hacia: null,
    t: 1,
    despiece: 0, despieceMeta: 0,
    luz: 1, luzMeta: 1,
    foco: null,
    pulso: false,
    autoGiro: false,
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

  function setLuz(encendida) { estado.luzMeta = encendida ? 1 : 0; }
  function setDespiece(activo) { estado.despieceMeta = activo ? 1 : 0; }
  function getLuz() { return estado.luzMeta === 1; }
  function getDespiece() { return estado.despieceMeta === 1; }

  const suave = (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);

  function ajustarTam() {
    const w = contenedor.clientWidth, h = contenedor.clientHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  }
  new ResizeObserver(ajustarTam).observe(contenedor);
  ajustarTam();

  // Si el usuario arrastra, se cancela la transición en curso
  controls.addEventListener('start', () => { estado.t = 1; });

  const reloj3d = new THREE.Clock();
  let visible = true;
  new IntersectionObserver(([e]) => { visible = e.isIntersecting; }).observe(contenedor);

  renderer.setAnimationLoop(() => {
    if (!visible) return;
    const dt = Math.min(reloj3d.getDelta(), 0.25);
    const k4 = 1 - Math.exp(-dt * 4);
    const tiempo = reloj3d.elapsedTime;

    if (estado.hacia && estado.t < 1) {
      estado.t = Math.min(1, estado.t + dt / 1.3);
      const k = suave(estado.t);
      camera.position.lerpVectors(estado.desde.cam, estado.hacia.cam, k);
      controls.target.lerpVectors(estado.desde.obj, estado.hacia.obj, k);
    }

    estado.despiece += (estado.despieceMeta - estado.despiece) * (1 - Math.exp(-dt * 3));
    estado.luz += (estado.luzMeta - estado.luz) * k4;
    const pulso = estado.pulso ? 0.82 + 0.18 * Math.sin(tiempo * 2.2) : 1;

    for (const [nombre, p] of Object.entries(piezas)) {
      const enFoco = !estado.foco || estado.foco.includes(nombre);
      const meta = enFoco ? 1 : 0.12;
      for (const m of p.materiales) {
        if (m.userData.op === undefined) m.userData.op = m.opacity;
        const actual = m.userData.actual ?? 1;
        const nuevo = actual + (meta - actual) * k4;
        m.userData.actual = nuevo;
        const transparente = nuevo < 0.999 || m.userData.op < 1 || m.alphaTest > 0;
        if (m.transparent !== transparente) {
          m.transparent = transparente;
          m.needsUpdate = true; // el shader opaco ignora la opacidad hasta recompilar
        }
        m.opacity = m.userData.op * nuevo;
        m.depthWrite = nuevo > 0.5;
      }
      for (const m of p.paneles) m.emissiveIntensity = 0.72 * estado.luz * pulso;
      const d = nombre === 'mesa' ? estado.despiece : 0;
      for (const parte of p.partes) parte.obj.position.copy(parte.base).addScaledVector(parte.despiece, d);
    }
    for (const l of brillo) l.intensity = 0.6 * estado.luz * pulso;

    controls.update();
    renderer.render(scene, camera);
  });

  return { irA, setLuz, setDespiece, getLuz, getDespiece, vistas: Object.keys(VISTAS) };
}

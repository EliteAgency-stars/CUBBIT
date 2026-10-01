import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { crearEscena } from './escena3d.js';
import { RENDERS, MODELOS_IA } from './media.js';
import { planoSVG, leyenda } from './planos.js';

// ---------- Renders: cada <img data-render="clave"> toma su archivo de media.js ----------
document.querySelectorAll('[data-render]').forEach((img) => {
  const r = RENDERS[img.dataset.render];
  if (!r) return;
  img.src = img.dataset.calidad === 'alta' ? r.full : r.thumb;
  img.alt = r.alt;
  img.loading = img.dataset.calidad === 'alta' ? 'eager' : 'lazy';
  img.decoding = 'async';
  img.closest('figure')?.addEventListener('click', () => abrirLightbox(r.full, r.alt));
});
document.querySelectorAll('[data-render-bg]').forEach((el) => {
  const r = RENDERS[el.dataset.renderBg];
  if (r) el.style.backgroundImage = `url("${r.full}")`;
});
document.querySelectorAll('figure[data-ampliar] img').forEach((img) => {
  img.closest('figure').addEventListener('click', () => abrirLightbox(img.dataset.full || img.src, img.alt));
});

// ---------- Lightbox ----------
const lb = document.getElementById('lightbox');
const lbImg = lb.querySelector('img');
const lbCap = lb.querySelector('figcaption');
function abrirLightbox(src, alt) {
  lbImg.src = src;
  lbImg.alt = alt;
  lbCap.textContent = alt;
  lb.showModal();
}
lb.addEventListener('click', () => lb.close());

// ---------- Planos cenitales ----------
const lamina = document.getElementById('plano-lamina');
const ley = document.getElementById('plano-leyenda');
function mostrarPlano(clave) {
  lamina.innerHTML = planoSVG(clave);
  ley.innerHTML = leyenda(clave);
  document.querySelectorAll('[data-plano]').forEach((b) => b.setAttribute('aria-selected', String(b.dataset.plano === clave)));
}
document.querySelectorAll('[data-plano]').forEach((b) => b.addEventListener('click', () => mostrarPlano(b.dataset.plano)));
mostrarPlano('mesa');
const planoMesa = document.getElementById('plano-mesa');
if (planoMesa) planoMesa.innerHTML = planoSVG('mesa');

// ---------- Escena 3D sincronizada con el recorrido ----------
const lienzo = document.getElementById('escena');
const etiqueta = document.getElementById('escena-etiqueta');
const btnLuz = document.getElementById('btn-luz');
const btnDespiece = document.getElementById('btn-despiece');
let escena = null;

try {
  escena = crearEscena(lienzo, { onListo: () => lienzo.classList.add('listo') });
} catch (e) {
  lienzo.classList.add('sin-webgl');
  console.warn('WebGL no disponible', e);
}

const secciones = [...document.querySelectorAll('[data-vista]')];
let actual = null;
function activar(sec) {
  if (!sec || sec === actual) return;
  actual = sec;
  escena?.irA(sec.dataset.vista);
  etiqueta.textContent = sec.dataset.etiqueta || '';
  const id = sec.closest('section[id]')?.id;
  document.querySelectorAll('.indice a').forEach((a) => a.classList.toggle('activo', a.getAttribute('href') === `#${id}`));
  if (escena) btnDespiece.setAttribute('aria-pressed', String(escena.getDespiece()));
}
const obs = new IntersectionObserver((entradas) => {
  const vis = entradas.filter((e) => e.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio);
  if (vis[0]) activar(vis[0].target);
}, { rootMargin: '-35% 0px -45% 0px', threshold: [0, 0.25, 0.5, 1] });
secciones.forEach((s) => obs.observe(s));

document.querySelectorAll('[data-ir]').forEach((b) => b.addEventListener('click', () => {
  escena?.irA(b.dataset.ir);
  etiqueta.textContent = b.title || b.textContent.trim();
}));
btnLuz.addEventListener('click', () => {
  if (!escena) return;
  const on = !escena.getLuz();
  escena.setLuz(on);
  btnLuz.setAttribute('aria-pressed', String(on));
  btnLuz.textContent = on ? 'Luz encendida' : 'Luz apagada';
});
btnDespiece.addEventListener('click', () => {
  if (!escena) return;
  const on = !escena.getDespiece();
  escena.setDespiece(on);
  btnDespiece.setAttribute('aria-pressed', String(on));
});

// ---------- Visor del modelo 3D generado con Higgsfield ----------
const visor = document.getElementById('visor-ia');
const estadoVisor = document.getElementById('visor-ia-estado');
let visorIA = null;

function crearVisorIA() {
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  visor.prepend(renderer.domElement);
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xf4eee5);
  scene.environment = new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(renderer), 0.04).texture;
  scene.add(new THREE.HemisphereLight(0xffffff, 0xd8c7ad, 0.8));
  const cam = new THREE.PerspectiveCamera(35, 1, 0.01, 100);
  const ctr = new OrbitControls(cam, renderer.domElement);
  ctr.enableDamping = true;
  ctr.autoRotate = true;
  ctr.autoRotateSpeed = 0.8;
  let modelo = null;
  const tam = () => {
    const w = visor.clientWidth, h = visor.clientHeight;
    renderer.setSize(w, h, false);
    cam.aspect = w / h;
    cam.updateProjectionMatrix();
  };
  new ResizeObserver(tam).observe(visor);
  tam();
  renderer.setAnimationLoop(() => { ctr.update(); renderer.render(scene, cam); });
  const loader = new GLTFLoader().setMeshoptDecoder(MeshoptDecoder);
  return {
    cargar(url) {
      estadoVisor.textContent = 'Cargando modelo…';
      estadoVisor.hidden = false;
      loader.load(url, (gltf) => {
        if (modelo) scene.remove(modelo);
        modelo = gltf.scene;
        const caja = new THREE.Box3().setFromObject(modelo);
        modelo.position.sub(caja.getCenter(new THREE.Vector3()));
        const tamano = caja.getSize(new THREE.Vector3()).length();
        scene.add(modelo);
        cam.position.set(tamano * 0.7, tamano * 0.45, tamano * 0.9);
        ctr.target.set(0, 0, 0);
        estadoVisor.hidden = true;
      }, undefined, () => {
        estadoVisor.innerHTML = `No se pudo cargar el modelo en este navegador. <a href="${url}" download>Descargar GLB</a>`;
      });
    },
  };
}

const botonesIA = document.querySelectorAll('[data-modelo]');
botonesIA.forEach((b) => {
  const url = MODELOS_IA[b.dataset.modelo];
  if (!url) { b.disabled = true; return; }
  b.addEventListener('click', () => {
    botonesIA.forEach((o) => o.setAttribute('aria-pressed', String(o === b)));
    visorIA ??= crearVisorIA();
    visorIA.cargar(url);
  });
});
new IntersectionObserver(([e], o) => {
  if (!e.isIntersecting) return;
  o.disconnect();
  [...botonesIA].find((b) => !b.disabled)?.click();
}, { rootMargin: '200px' }).observe(visor);

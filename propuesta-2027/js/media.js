// Renders de la propuesta.
//
// v3 (Higgsfield GPT Image 2.5 + composición): Higgsfield genera la escena con los productos reales
// de Cubitt como referencia y deja las cajas de luz en verde croma y el lugar del logo en magenta.
// tools/componer_renders.py pega encima, con perspectiva, las artes reales (artes-cubitt/web/) y el
// logo oficial en platino. Así ni el logo ni las artes los redibuja la IA.
// Las imágenes v3 viven en el almacenamiento de Higgsfield; las de propuesta-2027/renders/ son de la v2.
const HF = 'https://d2ol7oe51mr4n9.cloudfront.net/user_3H8VPOIlKTSsf171GizUHRYwT0M/';
const R = 'propuesta-2027/renders/';

const v3 = (id, alt) => ({ alt, full: `${HF}${id}.jpg`, thumb: `${HF}${id}.jpg` });
const v2 = (clave, alt) => ({ alt, full: `${R}${clave}.jpg`, thumb: `${R}${clave}-900.jpg` });

export const RENDERS = {
  familia: v3('3defafd6-576a-4791-895c-5b6af8d4e42c', 'Familia Cubitt 2027 en tienda: mesa de experiencia y dos muebles con cajas de luz y artes reales'),
  mesa: v3('23d31f91-bd13-4bef-9cc2-6fd8c9facc10', 'Mesa de experiencia: caja de luz «Nueva Era», elevador de madera con bafles, audífonos a la izquierda y relojes al frente'),
  touch: v3('40b70006-be24-421a-ade4-abb3e047c505', 'Clientes probando relojes y audífonos Cubitt en la mesa de experiencia'),
  vendedor: v2('vendedor', 'Lado vendedor de la mesa: puertas push, cajón, bandeja de cables y zócalo inox'),
  mueble: v3('c0dfb782-7239-4a4a-a0ba-925861c58a08', 'Mueble de exhibición: caja de luz Viva Pro 2, lateral Aura Pro 2 y logo platino 3000K'),
  modular: v3('2beff505-2ba8-4523-a1ab-4a65664c4732', 'Composición modular de tres muebles con artes Nueva Era, Viva Pro 2, Terra y laterales'),
  sobremesa: v3('cca2e26e-e725-4676-bde9-7defe1502e90', 'Display de sobremesa con caja de luz, logo platino en la base y tres checkpoints'),
  kids: v3('400b13cd-2ba3-4703-898d-602e34047cb8', 'Mueble Cubitt Jr & Teens: niños probando relojes Cubitt Jr. en el mesón de 60 cm y caja de luz Rapunzel'),
  kidsProducto: v3('8ffd62fc-aef8-421c-98d8-9c4e7a375130', 'Mueble Cubitt Jr & Teens: mesón infantil a 60 cm, mesón de padres a 90 cm y caja de luz Cubitt Jr.'),
  logo: v3('6a793f50-d5a7-41a4-8e7f-7273f4b895b8', 'Logo Cubitt oficial en platino con halo cálido 3000K sobre Capri'),
  material: v2('material', 'Detalle de materiales: melamina Capri, cubierta Duna, LED 3000K, zócalo inox y marco redondeado'),
  despiece: v3('8f5fde88-8aa5-4864-9714-99bc96f77767', 'Despiece de la mesa de experiencia con sus ocho capas'),
};

// Modelos 3D generados por Higgsfield (Tripo H3.1, imagen → 3D).
export const MODELOS_IA = {
  mesa: 'propuesta-2027/modelos/mesa-experiencia.glb',
  kids: 'https://d8j0ntlcm91z4.cloudfront.net/user_3H8VPOIlKTSsf171GizUHRYwT0M/hf_20261001_073624_5615a9f7-658f-469c-987c-a8bb33867665.glb',
};

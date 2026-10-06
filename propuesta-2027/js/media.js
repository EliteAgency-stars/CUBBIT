// Renders de la propuesta.
//
// v3 (Higgsfield GPT Image 2.5 + composición): Higgsfield genera la escena con los productos reales
// de Cubitt como referencia y deja las cajas de luz en verde croma y el lugar del logo en magenta.
// tools/componer_renders.py pega encima, con perspectiva, las artes reales y el logo oficial en platino.
// v4 (familia, mesa, touch, mueble, modular, kids, kidsProducto): cada arte se rediagrama a la proporción
// real de su caja (tools/artes_a_la_talla.py), sin estirar ni rellenar con copias difuminadas, y el logo
// lleva halo de contorno cálido 3000K.
// Las imágenes v3 viven en el almacenamiento de Higgsfield; las de propuesta-2027/renders/ son de la v2.
const HF = 'https://d2ol7oe51mr4n9.cloudfront.net/user_3H8VPOIlKTSsf171GizUHRYwT0M/';
const R = 'propuesta-2027/renders/';

const v3 = (id, alt) => ({ alt, full: `${HF}${id}.jpg`, thumb: `${HF}${id}.jpg` });
const v2 = (clave, alt) => ({ alt, full: `${R}${clave}.jpg`, thumb: `${R}${clave}-900.jpg` });

export const RENDERS = {
  familia: v3('77f04329-ae83-4f91-b630-f3955a263dff', 'Familia Cubitt 2027 en tienda: mesa de experiencia y dos muebles con cajas de luz y artes reales'),
  mesa: v3('4e60c9af-f0eb-4195-a346-6228e579bac9', 'Mesa de experiencia: caja de luz «Nueva Era», elevador de madera con bafles, audífonos a la izquierda y relojes al frente'),
  touch: v3('1341c4da-7eab-4232-bd2e-5cb4e80e6d71', 'Clientes probando relojes y audífonos Cubitt en la mesa de experiencia'),
  vendedor: v2('vendedor', 'Lado vendedor de la mesa: puertas push, cajón, bandeja de cables y zócalo inox'),
  mueble: v3('12ef1acb-8fec-4b21-81a6-ea887406d995', 'Mueble de exhibición: caja de luz Viva Pro 2, lateral Aura Pro 2 y logo platino 3000K'),
  modular: v3('3dd36272-d654-4c46-926c-5ec67b65e268', 'Composición modular de tres muebles: Nueva Era, Viva Pro 2 y Nueva Era, con laterales Terra'),
  sobremesa: v3('cca2e26e-e725-4676-bde9-7defe1502e90', 'Display de sobremesa con caja de luz, logo platino en la base y tres checkpoints'),
  kids: v3('e51149cf-4d2f-48de-8b69-57f931aa6aad', 'Mueble Cubitt Jr & Teens: niños probando relojes Cubitt Jr. en el mesón de 60 cm y caja de luz Rapunzel'),
  kidsProducto: v3('fbbe9958-05cf-4165-970d-5521c527c2b7', 'Mueble Cubitt Jr & Teens: mesón infantil a 60 cm, mesón de padres a 90 cm y caja de luz Cubitt Jr.'),
  logo: v3('6a793f50-d5a7-41a4-8e7f-7273f4b895b8', 'Logo Cubitt oficial en platino con halo cálido 3000K sobre Capri'),
  material: v2('material', 'Detalle de materiales: melamina Capri, cubierta Duna, LED 3000K, zócalo inox y marco redondeado'),
  despiece: v3('8f5fde88-8aa5-4864-9714-99bc96f77767', 'Despiece de la mesa de experiencia con sus ocho capas'),
};

// Modelos 3D. La mesa sale directo del SketchUp de FARUK AGENCIA (geometría exacta, tools/skp_a_glb.py,
// comprimida con meshopt); el mueble Jr & Teens es el modelo Higgsfield (Tripo H3.1, imagen → 3D).
export const MODELOS_IA = {
  mesa: 'propuesta-2027/modelos/mesa-cubitt-2027.glb',
  kids: 'https://d8j0ntlcm91z4.cloudfront.net/user_3H8VPOIlKTSsf171GizUHRYwT0M/hf_20261001_073624_5615a9f7-658f-469c-987c-a8bb33867665.glb',
};

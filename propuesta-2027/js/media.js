// Renders de la propuesta.
//
// v5 (Blender Cycles, tools/render_cycles.py): se renderizan los SketchUp de FARUK AGENCIA tal cual (mesa cubitt,
// mueble cubitt y sobre mesa cubitt), con los materiales del proyecto (Capri, Duna, inox, aluminio), las artes a la talla
// en la tela backlight 5000K, el LED 3000K, el logo y el isotipo oficiales con halo 3000K y los productos reales de Cubitt
// en las posiciones del archivo. Viven en propuesta-2027/renders/ (completo + miniatura de 900 px).
// v3/v4 (Higgsfield GPT Image 2.5 + composición): solo quedan los del mueble Cubitt Jr & Teens, que no cambió.
const HF = 'https://d2ol7oe51mr4n9.cloudfront.net/user_3H8VPOIlKTSsf171GizUHRYwT0M/';
const R = 'propuesta-2027/renders/';

const v3 = (id, alt) => ({ alt, full: `${HF}${id}.jpg`, thumb: `${HF}${id}.jpg` });
const local = (clave, alt) => ({ alt, full: `${R}${clave}.jpg`, thumb: `${R}${clave}-900.jpg` });

export const RENDERS = {
  familia: local('familia', 'Familia Cubitt 2027 en tienda: mesa de experiencia de 100 cm, composición de dos muebles con cajas de luz Nueva Era y Viva Pro 2 y display de sobremesa en el mostrador'),
  mesa: local('mesa', 'Mesa de experiencia de 100 × 79 × 50 cm: caja de luz Viva Pro 2, nueve relojes al frente y el audio sobre el elevador Duna'),
  touch: local('touch', 'Touch & Try a la altura del cliente: relojes en checkpoint con ficha acrílica y audio Cubitt sobre el elevador'),
  vendedor: local('vendedor', 'Lado vendedor de la mesa: dos puertas push en Capri, tope Duna y logo platino en el lateral'),
  mueble: local('mueble', 'Mueble de exhibición de 120 cm: frente liso con logo platino 3000K, isotipo en el lateral y caja de luz Nueva Era'),
  modular: local('modular', 'Composición de dos módulos (240 cm): cajas de luz Nueva Era y Viva Pro 2 y logo al frente de cada módulo'),
  sobremesa: local('sobremesa', 'Display de sobremesa de 50 × 32 × 25 cm sobre el mostrador: caja de luz Nueva Era, cinco relojes y logo platino en la base'),
  muro: local('muro', 'Bonus · Muro de exhibición de 220 × 248 cm: mesón con relojes, repisa flotante con el audio, caja de luz Nueva Era de 209 × 60 cm y cabecera con el logo platino'),
  muroDetalle: local('muro-detalle', 'Bonus · Muro de exhibición: relojes en checkpoint sobre el tope Duna, repisa con línea LED 3000K y audio Cubitt'),
  kids: v3('e51149cf-4d2f-48de-8b69-57f931aa6aad', 'Mueble Cubitt Jr & Teens: niños probando relojes Cubitt Jr. en el mesón de 60 cm y caja de luz Rapunzel'),
  kidsProducto: v3('fbbe9958-05cf-4165-970d-5521c527c2b7', 'Mueble Cubitt Jr & Teens: mesón infantil a 60 cm, mesón de padres a 90 cm y caja de luz Cubitt Jr.'),
  logo: local('logo', 'Logo Cubitt oficial en platino con halo de contorno 3000K sobre el lateral Capri de la mesa'),
  material: local('material', 'Detalle de materiales: tope Duna con esquina R40, línea de sombra con LED 3000K, Capri, marco de aluminio y logo platino'),
  despiece: local('despiece', 'Despiece de la mesa de experiencia en cinco pasos: zócalo, cuerpo, caja de luz, tope con línea de sombra y elevador'),
};

// Modelos 3D. La mesa, el mueble (solo y en composición de dos), el display de sobremesa y el muro (bonus) salen directo de los SketchUp de FARUK AGENCIA (geometría exacta, tools/skp_a_glb.py,
// comprimida con meshopt); el mueble Jr & Teens es el modelo Higgsfield (Tripo H3.1, imagen → 3D).
export const MODELOS_IA = {
  mesa: 'propuesta-2027/modelos/mesa-cubitt-2027.glb',
  mueble: 'propuesta-2027/modelos/mueble-cubitt-2027.glb',
  mueble2: 'propuesta-2027/modelos/mueble-cubitt-2027-x2.glb',
  sobremesa: 'propuesta-2027/modelos/sobremesa-cubitt-2027.glb',
  muro: 'propuesta-2027/modelos/muro-cubitt-2027.glb',
  kids: 'https://d8j0ntlcm91z4.cloudfront.net/user_3H8VPOIlKTSsf171GizUHRYwT0M/hf_20261001_073624_5615a9f7-658f-469c-987c-a8bb33867665.glb',
};

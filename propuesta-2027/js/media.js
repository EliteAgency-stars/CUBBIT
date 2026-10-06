// Renders de la propuesta.
//
// v5 (Blender Cycles, tools/render_blender.py): diez renders hechos sobre los modelos exactos de los SketchUp
// (los mismos GLB de la escena 3D), con los artes a la talla de cada caja de luz, el logo oficial en platino con
// halo 3000K y las fotos reales de los productos Cubitt. Viven en propuesta-2027/renders/ (<clave>.jpg y <clave>-900.jpg).
// Jr & Teens sigue en v4 (Higgsfield + tools/componer_renders.py con artes a la talla): ese mueble no cambió.
const HF = 'https://d2ol7oe51mr4n9.cloudfront.net/user_3H8VPOIlKTSsf171GizUHRYwT0M/';
const R = 'propuesta-2027/renders/';

const v3 = (id, alt) => ({ alt, full: `${HF}${id}.jpg`, thumb: `${HF}${id}.jpg` });
const v2 = (clave, alt) => ({ alt, full: `${R}${clave}.jpg`, thumb: `${R}${clave}-900.jpg` });

export const RENDERS = {
  familia: v2('familia', 'Familia Cubitt 2027 en tienda: mesa de experiencia de 80 cm al frente y composición de dos muebles de 120 cm con cajas de luz Nueva Era y Viva Pro 2'),
  mesa: v2('mesa', 'Mesa de experiencia 80 × 79 × 50 cm: caja de luz Viva Pro 2 a ras, tope Duna con LED 3000K, elevador con bafles y relojes en checkpoints'),
  touch: v2('touch', 'Lo que ve el cliente al acercarse: relojes en checkpoints, audífonos y bafles sobre el tope Duna de la mesa de experiencia'),
  vendedor: v2('vendedor', 'Lado vendedor de la mesa de experiencia: dos puertas push en Capri, tope Duna y zócalo inox'),
  mueble: v2('mueble', 'Mueble de exhibición 120 × 149 × 40 cm: caja de luz Nueva Era, elevador Duna, ocho relojes en checkpoints y logo platino 3000K'),
  modular: v2('modular', 'Composición modular de dos muebles de 120 cm lado a lado: cajas de luz Nueva Era y Viva Pro 2, logo solo en los laterales exteriores'),
  sobremesa: v2('sobremesa', 'Display de sobremesa sin banda superior: caja de luz Viva Pro 2, logo platino en el frente de la base y tres checkpoints'),
  kids: v3('e51149cf-4d2f-48de-8b69-57f931aa6aad', 'Mueble Cubitt Jr & Teens: niños probando relojes Cubitt Jr. en el mesón de 60 cm y caja de luz Rapunzel'),
  kidsProducto: v3('fbbe9958-05cf-4165-970d-5521c527c2b7', 'Mueble Cubitt Jr & Teens: mesón infantil a 60 cm, mesón de padres a 90 cm y caja de luz Cubitt Jr.'),
  logo: v2('logo', 'Logo Cubitt oficial en platino con halo cálido 3000K sobre el lateral Capri de la mesa'),
  material: v2('material', 'Detalle de materiales: melamina Capri, tope Duna con esquina curva, línea de sombra con LED 3000K y caja de luz de aluminio'),
  despiece: v2('despiece', 'Despiece de la mesa de experiencia 80 × 79 × 50 cm con sus capas'),
};

// Modelos 3D. La mesa y el mueble (solo y en composición de dos) salen directo de los SketchUp de FARUK AGENCIA (geometría exacta, tools/skp_a_glb.py,
// comprimida con meshopt); el mueble Jr & Teens es el modelo Higgsfield (Tripo H3.1, imagen → 3D).
export const MODELOS_IA = {
  mesa: 'propuesta-2027/modelos/mesa-cubitt-2027.glb',
  mueble: 'propuesta-2027/modelos/mueble-cubitt-2027.glb',
  mueble2: 'propuesta-2027/modelos/mueble-cubitt-2027-x2.glb',
  kids: 'https://d8j0ntlcm91z4.cloudfront.net/user_3H8VPOIlKTSsf171GizUHRYwT0M/hf_20261001_073624_5615a9f7-658f-469c-987c-a8bb33867665.glb',
};

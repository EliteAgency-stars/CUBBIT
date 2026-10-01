// Renders generados con Higgsfield (GPT Image 2.5) usando como referencia el logo oficial en platino,
// las artes reales de Cubitt, las fotos de producto y las texturas Capri y Duna de Pelíkano.
// Todos se guardan en el repositorio (propuesta-2027/renders/), así la página no depende de servicios externos.
const R = 'propuesta-2027/renders/';

const render = (clave, alt) => ({ alt, full: `${R}${clave}.jpg`, thumb: `${R}${clave}-900.jpg` });

export const RENDERS = {
  familia: render('familia', 'Familia Cubitt 2027 en tienda: mesa de experiencia, muebles con cajas de luz y artes reales'),
  mesa: render('mesa', 'Mesa de experiencia: frente con caja de luz «Nueva Era», elevador de madera con bafles, audífonos y relojes'),
  touch: render('touch', 'Clientes probando relojes y audífonos Cubitt en la mesa de experiencia'),
  vendedor: render('vendedor', 'Lado vendedor de la mesa: puertas push, cajón, bandeja de cables y zócalo inox'),
  mueble: render('mueble', 'Mueble de exhibición: caja de luz Viva Pro 2, lateral Aura Pro 2 y logo platino 3000K'),
  modular: render('modular', 'Composición modular de tres muebles con las artes Terra, Viva Pro 2, Aura Pro 2 y Nueva Era'),
  sobremesa: render('sobremesa', 'Display de sobremesa con caja de luz Viva Pro 2, banda con logo y tres checkpoints'),
  kids: render('kids', 'Mueble Cubitt Jr & Teens: mesón infantil a 60 cm, mesón de padres a 90 cm y caja de luz Cubitt Jr.'),
  logo: render('logo', 'Logo Cubitt en platino con halo cálido 3000K junto a la caja de luz de aluminio'),
  material: render('material', 'Detalle de materiales: melamina Capri, cubierta Duna, LED 3000K, zócalo inox y marco redondeado'),
  fuenteMesa: render('fuente-mesa', 'Render limpio de la mesa usado para generar el modelo 3D'),
};

// Modelo 3D generado por Higgsfield (Tripo H3.1) a partir del render limpio de la mesa.
export const MODELOS_IA = {
  mesa: 'propuesta-2027/modelos/mesa-experiencia.glb',
};

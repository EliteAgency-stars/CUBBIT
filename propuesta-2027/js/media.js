// Renders y modelos 3D generados con Higgsfield (GPT Image 2.5 con el logo oficial
// en platino como referencia · Tripo H3.1 imagen → 3D).
// Para reemplazar un render basta con cambiar su id aquí.
const CDN = 'https://d8j0ntlcm91z4.cloudfront.net/user_3H8VPOIlKTSsf171GizUHRYwT0M/hf_20261001_';

const render = (stamp, id, alt) => ({
  alt,
  full: `${CDN}${stamp}_${id}.png`,
  thumb: `${CDN}${stamp}_${id}_min.webp`,
});

export const RENDERS = {
  familia: render('010751', '7ccde1c5-b229-4291-aed3-46581a00f3f2', 'Familia Cubitt 2027 en tienda: mesa de experiencia, muebles de exhibición y display de sobremesa'),
  mesa: render('010751', '286fd898-60e8-4eb5-8116-c247f6f388c2', 'Mesa de experiencia con frente de lámina opal retroiluminada y logo Cubitt platino'),
  touch: render('010751', 'b764f477-9e56-4cb3-9f96-0f9a3a4f269b', 'Clientes probando relojes en la mesa de experiencia'),
  vendedor: render('010751', 'c8a6d6ff-9f6a-4287-97ae-52dfa59caf62', 'Lado vendedor de la mesa: puertas push, cajón y bandeja de cables'),
  mueble: render('010751', '99f3425e-3212-446e-b9b7-f2d02f321033', 'Mueble de exhibición con back panel opal iluminado y repisa regulable'),
  modular: render('010751', '17db5589-4e53-4f1d-a4cb-0aab755f8a94', 'Tres muebles de exhibición formando una pared continua de luz'),
  sobremesa: render('010751', '9bcf2d27-a55f-4300-b230-1e873f4c5912', 'Display de sobremesa con lámina de luz, checkpoints y riel de precio'),
  logo: render('010751', '87a9ac66-a44d-40be-a41f-75805828e996', 'Logo Cubitt platino sobre lámina opal retroiluminada'),
  material: render('010751', '29f5c17e-cdb6-4172-b63d-ace2792fca83', 'Detalle de esquina R30, cubierta de roble flotante y zócalo de aluminio'),
  despiece: render('010750', 'dc34e17e-9847-44b8-afa8-ba6ba67a351e', 'Despiece axonométrico de la mesa de experiencia'),
  fuenteMesa: render('010750', '31068059-b031-4ded-ac9d-16269c1d8816', 'Render limpio de la mesa usado para generar el modelo 3D'),
  fuenteMueble: render('010751', '56850253-6a09-400e-b53e-2d9879a00f15', 'Render limpio del mueble usado para generar el modelo 3D'),
};

// Modelos GLB generados por Higgsfield a partir de los renders limpios.
// Se cargan solo cuando el usuario lo pide (≈60 MB cada uno).
export const MODELOS_IA = {
  mesa: `${CDN}012223_ba487222-9478-404a-b980-dd010ceac24b.glb`,
  mueble: `${CDN}012225_93212ca0-26b2-444b-9b63-803f3f507537.glb`,
};

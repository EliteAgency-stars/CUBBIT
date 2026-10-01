# Cubitt 2027 · Línea Platino — Propuesta de mobiliario

> Respuesta al brief **Cubitt 2027 · Mobiliario** (tecnología + diseño + experiencia). La propuesta completa, con escena 3D interactiva y renders, está en [`index.html`](../index.html).

## Idea

**Un volumen sereno, una lámina de luz y el logo Cubitt en platino.**
Tres tipologías con un mismo ADN, armadas con **los mismos cinco componentes** para que el taller produzca en serie y el costo no se dispare.

| # | Componente | Especificación |
|---|---|---|
| 1 | Cuerpo arena | MDF 18 mm con melamina mate color arena, canto PVC 2 mm. Radio **R30 solo en aristas verticales visibles** |
| 2 | Cubierta roble flotante | Melamina roble claro 15 + 15 mm reengrosada, esquinas R30 por CNC, sobre línea de sombra de 15 mm |
| 3 | Lámina de luz | Acrílico opal 3 mm (transmisión 50–60 %) en caja de luz de 80 mm con cinta LED COB 24 V 4000K, CRI > 90 (sin puntos) |
| 4 | Logo Cubitt platino | Logo oficial sin cambios, acrílico 6 mm cortado con láser y cara de vinilo aluminio cepillado (tipo 3M 1080), adherido a la lámina |
| 5 | Aluminio satinado | Perfil comercial en U para enmarcar la lámina, zócalo rehundido de 6 cm y riel de precio |

Color de referencia del platino: Pantone 877 C · digital `#D6D2CA` → `#B0ACA4`.
Archivos del logo: [`assets/logo/`](assets/logo/) (platino PNG, negro original y fondos de referencia).

## Tipologías

### 01 · Mesa de experiencia — 150 × 90 × 70 cm
- Frente = una sola lámina opal retroiluminada con el logo platino de 60 cm.
- Cubierta roble de 1,52 × 0,72 m más un elevador opal iluminado de 62 × 10 × 22 cm para el producto héroe (dos niveles de exhibición).
- Pasacables de aluminio hacia una bandeja interna, con regleta y driver de 24 V ventilado.
- Lado vendedor: dos puertas push y un cajón, sin manijas. Se fabrica en dos módulos que pasan por una puerta de 0,80 m.
- Opción: cambiar el elevador por un monitor de 24″ empotrado.

### 02 · Mueble de exhibición — 120 × 140 × 40 cm
- Gabinete arena de 85 cm con puertas push y mesón de roble a 88 cm.
- Back panel opal de 55 cm, que funciona como la caja de luz del mueble, con el logo de 42 cm.
- Repisa acrílica regulable sobre rieles de aluminio para el producto héroe.
- Jerarquía: producto héroe → familia de producto → accesorios → CTA / precio.
- Modular: los módulos se unen en una franja continua de luz, con un solo logo por composición.

### 03 · Display de sobremesa — 50 × 30 × 25 cm
- Base arena de 8 cm, cubierta roble y lámina opal de 22 cm iluminada por el canto, con logo de 30 cm.
- Tres checkpoints integrados en la cubierta y riel de aluminio con precio y CTA.
- Un solo cable de 12 V; viaja armado.

## Costos de referencia (costo directo por unidad, COP)

Calculados con los valores unitarios del proyecto Centro Mayor (`data/presupuesto.csv`). No incluyen AIU ni IVA y deben validarse con el taller.

| Pieza | Rango | Base |
|---|---:|---|
| Mesa de experiencia | 4,6 – 5,4 M | Isla relojes 1.3.1 ($3.900.000) + caja de luz ≈ $0,9 M/m² (CL4) + logo 1.9.8 ($380.000) |
| Mueble de exhibición | 3,0 – 3,6 M | Panel mural backlit 1.3.3 ($2.500.000) + gabinete + logo |
| Display de sobremesa | 0,6 – 0,9 M | Caja de luz tipo 1 CL6 ($580.000) + base y checkpoints |
| **Familia (1 + 2 + 1)** | **11,2 – 13,5 M** | Costo directo antes de AIU |

## Cumplimiento del brief

- **Sin negro:** el logo pasa de negro a platino y el mobiliario usa arena, blanco, roble y aluminio.
- **Luz:** solo 4000K, COB detrás de acrílico opal (sin LED de puntos, sin azul ni RGB).
- **Branding:** un logo por pieza, integrado en la lámina.
- **Constructibilidad:** sin curvas compuestas, lacas ni piezas a medida; perfilería y LED comerciales.
- **Laterales terminados**, cables ocultos y mantenimiento desde el lado del vendedor.

## Recursos generados con Higgsfield

- 12 renders (GPT Image 2.5, con el logo oficial en platino como referencia). Las URLs están en [`js/media.js`](js/media.js).
- 2 modelos 3D GLB (Tripo H3.1, imagen → 3D) de la mesa y del mueble.
- La escena 3D interactiva de la página es paramétrica (three.js), con las medidas exactas del brief y el logo oficial como textura.

> Las imágenes y modelos son conceptuales. Dimensiones, materiales, acabados, estructura, costos, seguridad, instalación y mantenimiento se validan antes de producción.

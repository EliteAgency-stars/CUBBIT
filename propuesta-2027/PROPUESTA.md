# Cubitt 2027 · Línea Platino — Propuesta de mobiliario

**FARUK AGENCIA** · Respuesta al brief *Cubitt 2027 · Mobiliario* con las correcciones de la revisión interna. La propuesta completa (escena 3D, planos cenitales, renders, artes y productos reales) está en [`index.html`](../index.html).

## Sistema: cinco componentes en cuatro piezas

| # | Componente | Especificación |
|---|---|---|
| 1 | Cuerpo | Melamina **Capri** Pelíkano (Madecentro) 18 mm + canto rígido Capri. Reemplaza la lámina blanca por durabilidad; antibacterial 99 %. |
| 2 | Madera | Melamina **Duna** Pelíkano (Madecentro) 15 + 15 mm en cubiertas, elevadores y repisas. |
| 3 | Cajas de luz | Perfil de **aluminio con esquinas redondas** para tela SEG + **tela backlight** impresa (cambio de arte en minutos). LED **5000K**, CRI > 90. |
| 4 | Logo | Logo oficial Cubitt en **platino** (acrílico 6 mm + cara metalizada) con halo LED **3000K**, siempre sobre Capri. |
| 5 | Metal | **Acero inoxidable** satinado en zócalos, riel de precio y pasacables. |

Iluminación: **3000K** en muebles y logo · **5000K** en cajas de luz · cinta continua sin puntos.

## Piezas

### 01 · Mesa de experiencia — 80 × 79 × 50 cm (SketchUp «primer mueble mesa cubitt»)
- Reemplaza a la mesa de 150 × 90 × 70 cm. Medidas leídas del archivo [`artes-cubitt/originales/primer mueble mesa cubitt.skp`](artes-cubitt/originales/).
- **Base recta**: cuerpo Capri 80 × 50 × 70,2 cm (aristas vivas) sobre zócalo inox de 5 cm.
- **Tope de madera con curva**: Duna de 18 mm con esquinas R40 en planta, sobre un marco rehundido 3 cm que forma la línea de sombra con LED 3000K (tope a 78,8 cm).
- Frente: caja de luz a ras de **66 × 56 cm** (tela 65,9 × 56,1 cm) con el arte **Viva Pro 2** a la talla.
- Laterales Capri con el logo platino oficial (36,5 cm, centrado a 40 cm de alto) y halo cálido 3000K.
- Distribución (plano cenital): **bafles** atrás sobre elevador Duna 72,7 × 14 × 5 cm con riel inox (Power Pro 2, Power Plus 2, Power Go 2, Power Mini) · **audífonos** a los costados (Power Buds 2 a la izquierda, Power ANC en soporte a la derecha) · **relojes** al frente en 4 checkpoints con ficha acrílica (Viva Pro 2, Viva 2, Aura Pro 2, Terra).
- Lado vendedor: dos puertas push sin manijas.
- Modelo 3D exacto: [`modelos/mesa-cubitt-2027.glb`](modelos/mesa-cubitt-2027.glb) (`tools/skp_a_glb.py`, 1,1 MB con meshopt).
- Los renders de ambiente conservan el volumen de la versión anterior; la escena 3D, el plano y el GLB usan estas medidas.

### 02 · Mueble de exhibición — 120 × 140 × 40 cm
- Gabinete Capri con logo platino 3000K, mesón Duna a 88 cm con LED 3000K.
- Caja de luz trasera 116 × 48 cm (arte **Viva Pro 2**) y caja de luz lateral **40 × 76 cm** (arte **Aura Pro 2**, formato existente).
- Jerarquía: héroe en repisa acrílica → familia en el mesón → accesorios en los extremos → precio en riel inox.

### Composición modular — 3 × 120 cm
- Artes Terra, Viva Pro 2 y Nueva Era; laterales Aura Pro 2. Un solo logo, en el módulo central.

### 03 · Display de sobremesa — 50 × 30 × 25 cm
- Basado en el display con checkpoints actual: base Capri con LED 3000K, plataforma Duna, caja de luz con banda de aluminio y logo platino, tres checkpoints y riel inox.

### 04 · Mueble Cubitt Jr & Teens — 120 × 125 × 55 cm (nuevo)
- **Mesón infantil a 60 cm** (alcance de niños de 4 a 10 años) y **mesón de padres a 90 cm**.
- Caja de luz Cubitt Jr. entre 93 y 125 cm (altura de ojos de 8 a 10 años).
- Esquinas **R50**, sin vidrio, cables espiral cortos, anclaje antivuelco, zócalo inox rehundido. El mesón de 60 cm también es accesible en silla de ruedas.
- Productos: Cubitt Jr. (Rapunzel, Paw Patrol, Artic Blue), Teens, Headphones Jr., Hydro Bottle Jr., Tumbler Jr.

## Costos (valores aproximados por unidad, COP)

| Pieza | Valor |
|---|---:|
| Mesa de experiencia (valor de la versión de 150 cm · se recotiza con la nueva de 80 × 79 × 50 cm) | $ 8.500.000 |
| Mueble de exhibición | $ 12.400.000 |
| Display de sobremesa | $ 1.200.000 |
| Composición modular | $ 25.000.000 |
| Mueble Cubitt Jr & Teens (estimado, por validar) | ≈ $ 9.000.000 |

## Correcciones aplicadas

- [x] Tono madera Duna (Madecentro) · Capri en lugar de la lámina blanca.
- [x] Cajas de luz en aluminio con esquinas redondas y tela backlight.
- [x] Iluminación 3000K muebles y logo · 5000K cajas de luz.
- [x] Zócalos en acero inoxidable · elevador en madera (no acrílico).
- [x] Costos revisados según material.
- [x] Planos cenitales de distribución de productos (mesa, mueble, display, kids).
- [x] Mueble para niños con criterios de accesibilidad.
- [x] Logo oficial en cada render: Higgsfield deja una placa magenta y `tools/componer_renders.py` pega el archivo original del logo platino (la IA ya no lo dibuja).
- [x] Artes reales en las cajas de luz: Higgsfield deja la tela en verde croma y se pega el arte original con perspectiva.
- [x] Modelo 3D Higgsfield del mueble Cubitt Jr & Teens.
- [x] Firma únicamente de **FARUK AGENCIA**, con su logo y el aviso de marca registrada.
- [x] Artes **a la talla** de cada caja de luz (`tools/artes_a_la_talla.py`): cada arte se rediagrama a la proporción real de su caja, sin estirar piezas ni rellenar con copias difuminadas. Renders v4 recompuestos con `tools/componer_renders.py` (cajas separadas, proporción medida en perspectiva).
- [x] Halo de contorno del logo en luz cálida **3000K**.
- [x] Mesa de experiencia nueva según el SketchUp (base recta, tope Duna con esquinas curvas), con plano cenital y modelo 3D exacto.

## Recursos

- Artes y fotos de producto originales: [`artes-cubitt/originales/`](artes-cubitt/originales/) (ver [`artes-cubitt/INVENTARIO.md`](artes-cubitt/INVENTARIO.md)); versiones web en `artes-cubitt/web/` y recortes en `artes-cubitt/productos/` (generados con `tools/preparar_artes.py`).
- Renders v3/v4 Higgsfield (GPT Image 2.5 con las hojas de producto de [`referencias/`](referencias/) + composición con `tools/componer_renders.py` y artes de `tools/artes_a_la_talla.py`): enlaces en [`js/media.js`](js/media.js). Los renders v2 que quedan en [`renders/`](renders/) son el lado vendedor y el detalle de materiales.
- Artes a la talla de las cajas de la escena 3D: [`artes-cubitt/a-la-talla/`](artes-cubitt/a-la-talla/).
- Modelo 3D de la mesa de experiencia convertido directo del SketchUp (`tools/skp_lector.py` + `tools/skp_a_glb.py`): [`modelos/mesa-cubitt-2027.glb`](modelos/mesa-cubitt-2027.glb).
- Modelo 3D Higgsfield del mueble Cubitt Jr & Teens (Tripo H3.1, 10,8 MB): enlace en [`js/media.js`](js/media.js).
- Texturas Capri y Duna (Pelíkano): [`assets/materiales/`](assets/materiales/). Firma FARUK AGENCIA: [`assets/firma/`](assets/firma/) (`tools/preparar_firma.py`).
- Los archivos SketchUp (`.skp`, formato 2021+) se leen sin SketchUp con `tools/skp_lector.py` y se convierten a GLB con `tools/skp_a_glb.py`.

> Cubitt y sus productos, logos y artes son propiedad de Cubitt. Las imágenes y modelos son conceptuales y se validan antes de producción.

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

### 01 · Mesa de experiencia — 150 × 90 × 70 cm
- Frente: caja de luz 138 × 62 cm con el arte **«Nueva Era»**.
- Laterales Capri con logo platino 3000K.
- Distribución (plano cenital): **bafles** sobre elevador de **madera Duna** h 10 cm (Power Go 2, Power Pro 2, Power Plus 2, Power Mini) · **audífonos** en el extremo izquierdo (Power ANC negro y crema, Power Buds 2) · **relojes** al frente en checkpoints (Viva Pro 2, Viva 2, Viva Lite, Aura 2, Aura Pro 2, Terra).
- Lado vendedor: dos puertas push + cajón, bandeja de cables y driver 24 V.

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
| Mesa de experiencia | $ 8.500.000 |
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
- [x] Logo verificado en cada render (dos t, retícula completa); se descartó el despiece generado por IA porque omitía la retícula.
- [x] Firma únicamente de **FARUK AGENCIA**, con su logo y el aviso de marca registrada.

## Recursos

- Artes y fotos de producto originales: [`artes-cubitt/originales/`](artes-cubitt/originales/) (ver [`artes-cubitt/INVENTARIO.md`](artes-cubitt/INVENTARIO.md)); versiones web en `artes-cubitt/web/` y recortes en `artes-cubitt/productos/` (generados con `tools/preparar_artes.py`).
- Renders Higgsfield (GPT Image 2.5 con logo, artes, productos y texturas como referencia): [`renders/`](renders/) (`tools/descargar_renders.py`).
- Modelo 3D Higgsfield (Tripo H3.1) optimizado a 4,4 MB: [`modelos/mesa-experiencia.glb`](modelos/mesa-experiencia.glb) (`tools/optimizar_glb.py` + gltf-transform).
- Texturas Capri y Duna (Pelíkano): [`assets/materiales/`](assets/materiales/). Firma FARUK AGENCIA: [`assets/firma/`](assets/firma/) (`tools/preparar_firma.py`).
- Los archivos SketchUp (`.skp`) se conservan como referencia; para usarlos en la web hay que exportarlos desde SketchUp a `.glb`, `.dae` u `.obj`.

> Cubitt y sus productos, logos y artes son propiedad de Cubitt. Las imágenes y modelos son conceptuales y se validan antes de producción.

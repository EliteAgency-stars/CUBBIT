# AGENTS.md — Guía para agentes de IA

Repositorio de la propuesta de adecuación de la **Tienda CUBITT** (C.C. Centro Mayor, Bogotá), elaborada por FARUK AGENCIA — Inversiones Rahman SAS / BAE Group. No es un proyecto de software: es documentación de obra y diseño interior.

## Dónde está cada cosa

- `README.md` — fuente principal: datos del local, presupuesto, alcance por capítulo, materiales, cronograma, estado de obra y documentos fuente.
- `data/presupuesto.csv` — los 63 ítems del presupuesto (capítulo, ítem, descripción, unidad, cantidad, valor unitario y total en COP). Úsalo para cualquier cálculo.
- `assets/*.png` — esquemas generados desde la propuesta (planta, costos, cronograma, mueble, paleta, estado).
- `index.html` + `propuesta-2027/` — propuesta de mobiliario 2027 «Línea Platino»: sitio estático con escena 3D (three.js incluido en `propuesta-2027/vendor/`), ficha en `propuesta-2027/PROPUESTA.md`. Renders en `propuesta-2027/renders/`, modelos GLB en `propuesta-2027/modelos/`, planos cenitales en `propuesta-2027/js/planos.js`, artes y fotos reales de Cubitt en `propuesta-2027/artes-cubitt/` (originales + `web/` + `productos/`). Scripts de regeneración en `tools/` (requieren Pillow, numpy, PyMuPDF, pygltflib, opencv-python, mapbox_earcut): `artes_a_la_talla.py` (artes a la proporción exacta de cada caja, sin estirar ni difuminar), `componer_renders.py` (logo y artes sobre los renders Higgsfield), `skp_lector.py` + `skp_a_glb.py` (SketchUp → GLB), `render_cycles.py` (renders v5 en Blender Cycles desde los SketchUp; requiere `pip install bpy`) y `preparar_isotipo.py` (isotipo recortado del logo oficial).
- La mesa de experiencia vigente es la del SketchUp `artes-cubitt/originales/mesa cubitt.skp`: 100 × 79 × 50 cm, base recta Capri, tope Duna con esquinas R40, caja de luz frontal 84,9 × 58,1 cm (tela 82,4 × 56,1), logo en los laterales, nueve relojes al frente y todo el audio sobre el elevador de 91 cm.
- El mueble de exhibición vigente es el del SketchUp `artes-cubitt/originales/mueble cubitt.skp`: módulo de 120 × 149 × 40 cm con caja de luz trasera de 120 × 65 cm, frente liso con el logo y el isotipo en los laterales (puertas atrás); es modular, solo o dos iguales lado a lado (240 cm), con logo al frente de cada módulo e isotipo solo en los laterales exteriores.
- El display de sobremesa vigente es el del SketchUp `artes-cubitt/originales/sobre mesa cubitt.skp`: 50 × 32 × 25 cm, caja de luz de 50 × 25 cm con arte Nueva Era y espalda Capri con isotipo, cinco relojes y logo al frente de la base. GLB: `python tools/skp_a_glb.py <skp> <salida> mesa|mueble|mueble2|sobremesa|muro` y luego `npx gltfpack -i <salida> -o <salida> -cc`.
- Bonus: el muro de exhibición es el del SketchUp `artes-cubitt/originales/cuarto mueble mesa cubitt.skp`: 220 × 248 × 49 cm, mesón con cuatro puertas y tope Duna a 79,4 cm, repisa flotante a 1,26 m con el audio, caja de luz de 208,8 × 60 cm (Nueva Era) y cabecera con el logo; lleva melamina Nácar (`propuesta-2027/assets/materiales/nacar.jpg`) en el lateral izquierdo y el interior del mesón.
- Los artes nunca se estiran ni se rellenan con copias difuminadas: se generan a la talla de la caja con `tools/artes_a_la_talla.py`.
- La propuesta se firma solo como **FARUK AGENCIA** (logo en `propuesta-2027/assets/firma/`). Materiales: melamina Capri (cuerpos) y Duna (madera) de Madecentro; luz 3000K muebles/logo y 5000K cajas de luz; zócalos inox.
- `tools/generar_imagenes.py` — regenera los PNG: `python3 tools/generar_imagenes.py` (requiere matplotlib).

## Cifras clave

- Área neta 37,4 m² · zona comercial ≈24,0 m² · bodega ≈13,4 m² · frente 9,97 m · fondo ≈3,75 m.
- Costo directo $157.122.991 · total con AIU 30 % $204.259.888 · total con IVA sobre utilidad $207.842.292 (COP).
- Plazo contractual 40 días calendario.

## Reglas al trabajar aquí

- Los valores en COP usan punto como separador de miles en el README y números enteros en el CSV.
- Si cambias un valor del presupuesto, actualiza el README, el CSV y vuelve a generar las imágenes para que todo coincida.
- El Video Wall (ítem 1.9.6) fue reemplazado por caja de luz en la Semana 4; el presupuesto original aún lo lista.
- Las imágenes son esquemas ilustrativos, no planos oficiales. El logo oficial de CUBITT es `Cubitt_Logo_Full_black 2.png`; la versión platino y el isotipo recortado de ella están en `propuesta-2027/assets/logo/`. No redibujar el logo: usar siempre estos archivos.
- Documento confidencial: uso exclusivo CUBITT / FARUK AGENCIA SAS.

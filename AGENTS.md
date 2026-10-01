# AGENTS.md — Guía para agentes de IA

Repositorio de la propuesta de adecuación de la **Tienda CUBITT** (C.C. Centro Mayor, Bogotá), elaborada por FARUK AGENCIA — Inversiones Rahman SAS / BAE Group. No es un proyecto de software: es documentación de obra y diseño interior.

## Dónde está cada cosa

- `README.md` — fuente principal: datos del local, presupuesto, alcance por capítulo, materiales, cronograma, estado de obra y documentos fuente.
- `data/presupuesto.csv` — los 63 ítems del presupuesto (capítulo, ítem, descripción, unidad, cantidad, valor unitario y total en COP). Úsalo para cualquier cálculo.
- `assets/*.png` — esquemas generados desde la propuesta (planta, costos, cronograma, mueble, paleta, estado).
- `index.html` + `propuesta-2027/` — propuesta de mobiliario 2027 «Línea Platino»: sitio estático con escena 3D (three.js incluido en `propuesta-2027/vendor/`), ficha en `propuesta-2027/PROPUESTA.md`. Renders en `propuesta-2027/renders/`, modelo GLB en `propuesta-2027/modelos/`, planos cenitales en `propuesta-2027/js/planos.js`, artes y fotos reales de Cubitt en `propuesta-2027/artes-cubitt/` (originales + `web/` + `productos/`). Scripts de regeneración en `tools/` (requieren Pillow, numpy, PyMuPDF, pygltflib).
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
- Las imágenes son esquemas ilustrativos, no planos oficiales. El logo oficial de CUBITT es `Cubitt_Logo_Full_black 2.png`; la versión platino está en `propuesta-2027/assets/logo/`. No redibujar el logo: usar siempre estos archivos.
- Documento confidencial: uso exclusivo CUBITT / FARUK AGENCIA SAS.

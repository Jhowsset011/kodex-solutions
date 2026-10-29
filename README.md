# Kodex Solutions

Tienda empresarial de Kodex para **solutions.kodex.com.do**, derivada de `Jhowsset011/kodex-gaming-` (base `429a0b6100c6b26cfbaf311fbbd143ed597be032`).

Conserva el catálogo, carrito, pedidos por WhatsApp, filtros, paginación, temas, píxel Meta, fichas y páginas SEO de Gaming. La presentación usa los logos proporcionados, azul corporativo, modo claro inicial y banners rotativos con pausa, controles y respeto por movimiento reducido. No incorpora un sistema de cobros adicional.

## Catálogo y automatización

- Nexcom es la única fuente de precios de venta, stock, descripciones y fotografías.
- Omega confirma referencias públicas compartidas; sus precios no se publican ni se utilizan para fijar el precio de venta.
- `scripts/solutions_scope.py` selecciona artículos para oficina y empresa: impresión, energía, seguridad, Cricut, redes, computación, accesorios de oficina y punto de venta. Excluye productos gamer, RGB y reacondicionados.
- Epson, Brother y Canon se incluyen por fabricante completo, con todas las páginas de sus búsquedas públicas en Omega, además de las categorías habituales. Esto cubre impresoras, tintas, tóner, cabezales, mantenimiento, papel y demás equipos y accesorios compartidos.
- Cada actualización consulta el catálogo completo de Nexcom y las categorías empresariales públicas de Omega con HTTPS verificado. Las coincidencias usan `sku = referencia`; no se importan productos por compartir solamente marca o nombre.
- Las altas, incluidas las manuales, deben pasar la misma intersección y clasificación. Si desaparecen más de 5% de las referencias anteriores (mínimo 3), se detiene la publicación para revisión.
- Se conservan los controles de Gaming: se retiene el precio anterior cuando cambia más de RD$500 y se bloquea la actualización cuando más del 20% de los precios propuestos cambia. Los costos estimados se escriben fuera del sitio y nunca en el artefacto público.
- Las imágenes se almacenan localmente y se genera HTML para productos y categorías, datos estructurados, mapas del sitio y robots.txt.
- `data/solutions-intersection.json` registra los títulos y enlaces públicos usados para verificar cada referencia, con la fecha de la última sincronización exitosa.

La acción `sync-catalogo.yml` ejecuta las pruebas y actualiza diariamente a las **6:00 a. m. de República Dominicana**, además de los cambios relevantes de código y la ejecución manual. Publica el resultado mediante GitHub Pages. Activar Pages con origen **GitHub Actions** y configurar el CNAME DNS `solutions` hacia `jhowsset011.github.io`. El archivo CNAME del repositorio establece `solutions.kodex.com.do`; no configura el DNS por sí solo.

## Desarrollo

```sh
python3 -m unittest discover -s tests -v
node --test tests/test_meta_pixel.cjs
python3 scripts/sync_nexcom_catalog.py --dry-run
python3 scripts/generate_product_pages.py
python3 -m http.server 8080
```

Python 3.12 y Node están disponibles en la acción de GitHub. Los scripts no requieren dependencias Python externas. Los importadores históricos de Omega se conservan junto con sus pruebas para mantener la base técnica; el flujo activo de Solutions es `sync_nexcom_catalog.py`, que aplica obligatoriamente el alcance empresarial.

El píxel de Meta y el WhatsApp mantienen la configuración de Gaming por solicitud del propietario. Los carritos y preferencias de Solutions usan claves independientes en el navegador.

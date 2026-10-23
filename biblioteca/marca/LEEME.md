# Marca para los vídeos

- `logo.png`: logotipo oficial «Path of the Rose», el mismo del juego (letras de vidriera verdes y rojas con las rosas). PNG con fondo transparente, recortado sin márgenes, 1600 × 298 px. Sale de `assets/ui/screens/title.png` del juego (1339 px, el original más grande que existe), ampliado con Lanczos sobre alfa premultiplicado: bordes limpios sobre fondos claros y oscuros. Lleva su propio contorno oscuro: no necesita sombra ni caja. No se traduce: es el mismo en todos los idiomas.
- `google_play_<idioma>.png`: insignias oficiales «Get it on Google Play» (Google Partner Marketing Hub), renderizadas a 640 px desde el SVG oficial. Úsalas tal cual: sin cambiar color ni proporciones, sobre fondo liso, con un margen de al menos 1/4 de su altura. Una por idioma del vídeo (Spanish para es, Portuguese-Brazil para pt-BR, Catalan, English, Indonesian).
- `cierre_<idioma>.mp4` (es, pt-BR, en, ca, id): pantalla final animada de 2,2 s (fondo de jardín difuminado, logo con halo, icono en medallón de vidriera, rayos, pétalos, CTA e insignia). El `.png` del mismo nombre es su último fotograma. Se generan con `../herramientas/cierre.py`.
- `fondo_cierre.png`, `icono_arte.png`: fondo y arte del icono que usa `cierre.py`.
- `cinzel-900.woff`: fuente Cinzel (SIL OFL) para los textos en pantalla, dorado #F3D98E con borde #2A1408.

## Skins (`skins/`)

Dibujo original de cada skin, el mismo de su ficha en la tienda del juego. PNG con fondo transparente, copiado tal cual (sin recortar ni reescalar).
- `skins/caballero.png`: Caballero (caballero por defecto) — `assets/player/knight.png` — 787 × 1019 px.
- `skins/sir_baldalot.png`: Sir Baldalot — `assets/player/calvaller.png` — 1007 × 1024 px.
- `skins/esqueleto.png`: Esqueleto — `assets/player/esqueleto.png` — 787 × 1024 px.
- `skins/condesa_ermesenda.png`: Condesa Ermesenda — `assets/player/ermessenda.png` — 845 × 1024 px.
- `skins/ksatria_barong.png`: Ksatria Barong — `assets/player/knight_barong.png` — 1004 × 1024 px.
- `skins/cagatio.png`: Cagatió — `assets/player/cagatio.png` — 756 × 1024 px.
- `skins/ninja.png`: Ninja — `assets/player/ninja_2.png` — 832 × 1024 px.
- `skins/caballero_cazuela.png`: Caballero Cazuela — `assets/player/knight_chef.png` — 971 × 1024 px.
- `skins/castanera.png`: Castañera — `assets/player/castanyera.png` — 988 × 1024 px.
- `skins/el_cavaller_de_plata.png`: El Cavaller de Plata — `assets/player/caballer_de_plata.png` — 853 × 1024 px.
- `skins/casco.png`: Casco — `assets/player/casc.png` — 814 × 1024 px.
- `skins/cabezudo.png`: Cabezudo — `assets/player/el_capgros.png` — 785 × 1024 px.
- `skins/cocollona.png`: Cocollona — `assets/player/cocollona.png` — 1010 × 1004 px.
- `skins/rara_jonggrang.png`: Rara Jonggrang — `assets/player/rara_jonggrang.png` — 754 × 1024 px.
- `skins/gargola.png`: Gárgola — `assets/player/gargola.png` — 968 × 1024 px.
- `skins/saci_perere.png`: Saci Pererê — `assets/player/saci_perere.png` — 962 × 1024 px.
- `skins/sir_batistan.png`: Sir Batistan — `assets/player/sir_batistan.png` — 803 × 1024 px.
- `skins/vesper.png`: Vesper — `assets/player/vesper.png` — 892 × 1024 px.
- `skins/khufu.png`: Khufu — `assets/player/khufu.png` — 978 × 1024 px.

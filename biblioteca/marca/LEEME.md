# Marca para los vídeos

- `logo.png`: logotipo oficial «Path of the Rose», el mismo del juego (letras de vidriera verdes y rojas con las rosas). PNG con fondo transparente, recortado sin márgenes, 1600 × 298 px. Sale de `assets/ui/screens/title.png` del juego (1339 px, el original más grande que existe), ampliado con Lanczos sobre alfa premultiplicado: bordes limpios sobre fondos claros y oscuros. Lleva su propio contorno oscuro: no necesita sombra ni caja. No se traduce: es el mismo en todos los idiomas.
- `google_play_<idioma>.png`: insignias oficiales «Get it on Google Play» (Google Partner Marketing Hub), renderizadas a 640 px desde el SVG oficial. Úsalas tal cual: sin cambiar color ni proporciones, sobre fondo liso, con un margen de al menos 1/4 de su altura. Una por idioma del vídeo (Spanish para es, Portuguese-Brazil para pt-BR, Catalan, English, Indonesian).
- `cierre_<idioma>.mp4` (es, pt-BR, en, ca, id): pantalla final animada de 2,2 s (fondo de jardín difuminado, logo con halo, icono en medallón de vidriera, rayos, pétalos, CTA e insignia). El `.png` del mismo nombre es su último fotograma. Se generan con `../herramientas/cierre.py`.
- `fondo_cierre.png`, `icono_arte.png`: fondo y arte del icono que usa `cierre.py`.
- `cinzel-900.woff`: fuente Cinzel (SIL OFL) para los textos en pantalla, dorado #F3D98E con borde #2A1408.

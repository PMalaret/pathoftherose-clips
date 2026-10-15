# Herramientas de montaje

Estilo aprobado por el autor el 15/10/2026 (vídeo del Saci Pererê). Úsalo en todos los vídeos.

## Archivos
- `cierre.py`: genera la pantalla final animada (2,2 s) de un idioma. Ya están generadas en `../marca/cierre_<idioma>.mp4` (es, pt-BR, en, ca, id), con su último fotograma en `.png`. Solo hay que volver a generarlas si cambia el diseño.
- `revela.py`: revelación de una skin en la tienda (2,18 s). Zoom acelerado de la tienda con un texto de intriga, golpe al equipar, la skin sale de la carta con rayos, remolino y chispas, nombre y subtítulo. Necesita el clip `<skin>_tienda_sfx.mp4` y el segundo exacto en que se equipa. Revisa siempre el `_recorte.png` que deja.
- `montar_ejemplo.sh`: el montaje completo del vídeo aprobado, para copiar y adaptar.

## Reglas del montaje
- **Ritmo:** música `dragon_60s.ogg` desde 3,65 s, a 110 BPM (1 tiempo = 0,5455 s). Cada plano dura un número entero de tiempos y los cortes caen en el tiempo. Duración total de 7 a 11 s.
- **Primer segundo:** siempre movimiento y un texto que intrigue. Nunca un recorrido tranquilo con el personaje pequeño.
- **Velocidad:** la acción va acelerada x1,35 con `tmix=frames=2` (estela) y el audio con `atempo=1.35`. El zoom de la tienda va x1,7.
- **Cortes:** secos en el tiempo. Nada de destellos blancos, fundidos a negro ni golpes de zoom encima de un clip donde ya se mueve la cámara. Solo un fundido de 0,25 s para entrar al cierre, y el cierre aguanta hasta el último fotograma (TikTok repite el vídeo).
- **Textos:** Cinzel 900 dorado `#F3D98E` con borde `#2A1408`, grandes (100-136 px), arriba (y = 200-345), como mucho 2 líneas de 2-3 palabras. Nada por debajo de y = 1450 (zona de los textos de TikTok) ni pegado al borde derecho.
- **Encuadre de la acción:** zoom 1,1 anclado arriba (`y='0'`) para que el texto no tape al personaje.

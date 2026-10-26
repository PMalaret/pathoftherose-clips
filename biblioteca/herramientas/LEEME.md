# Herramientas de montaje

## Estilo vigente (aprobado por el autor el 26/10/2026)

Úsalo en todos los vídeos. Sustituye al estilo del 15/10 (más abajo, solo como referencia).

**Estructura (unos 10,5 s):** 3 planos de acción → final integrado.
1. **Acción desde el primer fotograma.** Nada de logo ni intro al principio: el primer fotograma ya es un personaje moviéndose por el mapa, con su título visible.
2. **3 planos de 4 tiempos** (2,18 s a 110 BPM), cortes secos en el tiempo, **a velocidad real** (sin x1,35 ni estela). Solo clips `momento_` de capítulos altos (30 o más); nunca niveles iniciales ni recorridos con el personaje pequeño. La persecución del dragón del capítulo 50 con la Castañera es sosa: no la uses (la del capítulo 32 sí).
3. **Cada vídeo de la semana abre en un mapa distinto** (capítulo distinto) y, dentro del vídeo, evita dos planos seguidos del mismo mapa.
4. **Un título por plano**, desde su primer fotograma: Cinzel 900 dorado `#F3D98E` con borde `#2A1408`, arriba (y = 200 y la segunda línea debajo), 1-2 líneas que quepan en 940 px. Con el nombre de lo que se ve (skin o peligro), con el término exacto del glosario: «¡CORRE, GÁRGOLA!», «¡CUIDADO, ESQUELETO!», «¡AL LADRÓN!».
5. **Final integrado** `../marca/final_<idioma>.mp4` (4,2 s), con fundido de 0,3 s desde la acción: el icono se enciende a oscuras (camino dorado, rosa, ojo del dragón), se transforma en el medallón (cuadrado → círculo) mientras amanece el fondo del jardín, y entran el logo, «¡JUEGA YA!» y la insignia de Google Play. Aguanta hasta el último fotograma.
6. **Música del juego** (nunca de fuera): por defecto `dragon_60s.ogg` desde 3,65 s a 110 BPM; `laberinto.ogg` si no sale el dragón. Los sonidos del juego (versión `_sfx` de los clips) van debajo al 45 %. Cita CC-BY en la descripción.

**Herramienta:** `montar_acciones.py <spec.json> <salida.mp4>` hace todo el montaje (el formato del spec está al principio del script). Tipos de plano: `d` persecución (encuadre entero), `m` momento (zoom 1,1 arriba), `t` tienda.

**Archivos del final integrado:** `icono_fin.py` → `../marca/icono_fin.mp4` (icono encendiéndose) y `final_animado.py <idioma> ../marca/icono_fin.mp4 ../marca/final_<idioma>.mp4`. Ya están generados en los 5 idiomas (es, ca, en, pt-BR, id); solo hay que regenerarlos si cambia el diseño.

---

## Estilo anterior (15/10/2026, ya no se usa)

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

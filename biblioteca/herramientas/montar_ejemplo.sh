#!/usr/bin/env bash
# Plantilla de montaje aprobada por el autor (vídeo del Saci, 17/10/2026, 7,4 s):
#   revelación en la tienda (4 tiempos) -> momento de acción acelerado (6 tiempos) -> cierre (4 tiempos)
# Música: dragon_60s.ogg desde 3,65 s (golpe fuerte), 110 BPM: 1 tiempo = 0,5455 s.
# Todos los cortes caen en tiempos. Sin destellos blancos ni fundidos a negro.
# Uso: edita las variables y ejecútalo desde biblioteca/herramientas.
set -euo pipefail
B=..                                   # biblioteca/
IDIOMA=pt-BR                           # es | pt-BR | en | ca | id (cierre de marca/)
TIENDA=$B/general/saci_perere_tienda_sfx.mp4
EQUIPA=2.60                            # segundo en que «Equipar» pasa a «EQUIPADO»
ACCION=$B/jardin/momento_dragon_persecucion_saci_sfx.mp4
ACCION_SS=0.4                          # desde dónde empieza la acción en el clip
GANCHO="CORRE, SACI!"                  # texto durante la acción (corto, en mayúsculas)
FUENTE=$B/marca/cinzel-900.woff
SALIDA=video.mp4

# 1) Revelación en la tienda (sin audio), 2,18 s
python3 revela.py --tienda "$TIENDA" --equipa $EQUIPA --intriga "QUEM CHEGOU?" \
  --nombre "SACI PERERÊ" --sub "DESBLOQUEIE COM ROSAS" --salida rev.mp4
# Revisa rev_recorte.png antes de seguir.

# 2) Montaje: acción x1,35 con estela (tmix), 6 tiempos = 196 fotogramas = 4,42 s de clip original
printf '%s' "$GANCHO" > gancho.txt
ST="fontcolor=0xF3D98E:borderw=8:bordercolor=0x2A1408:shadowcolor=0x000000AA:shadowy=6:x=(w-text_w)/2"
TA=$(python3 -c "print(f'{$EQUIPA-1.85:.3f}')")
ffmpeg -v error -y \
 -i rev.mp4 \
 -ss $ACCION_SS -t 4.43 -i "$ACCION" \
 -i $B/marca/cierre_$IDIOMA.mp4 \
 -ss 3.65 -t 7.5 -i $B/musica/dragon_60s.ogg \
 -ss $TA -t 2.95 -i "$TIENDA" \
 -filter_complex "
[0:v]format=yuv420p,setsar=1[s];
[1:v]setpts=PTS/1.35,fps=60,tmix=frames=2,zoompan=z='1.1+0.04*in/196':x='iw/2-iw/zoom/2':y='0':d=1:s=1080x1920:fps=60,setsar=1,trim=end_frame=196,setpts=PTS-STARTPTS,drawtext=fontfile=$FUENTE:textfile=gancho.txt:fontsize=136:y=200:$ST[a];
[s][a]concat=n=2:v=1:a=0,format=yuv420p,fps=60,settb=1/60[g];
[2:v]format=yuv420p,setsar=1,fps=60,settb=1/60[e];
[g][e]xfade=transition=fade:duration=0.25:offset=5.2,format=yuv420p[v];
[4:a]asplit[x1][x2];[x1]atrim=0:1.85,asetpts=PTS-STARTPTS,atempo=1.7[ta];[x2]atrim=1.85:2.94,asetpts=PTS-STARTPTS[tb];
[1:a]atrim=0:4.42,asetpts=PTS-STARTPTS,atempo=1.35[ca];
[ta][tb][ca]concat=n=3:v=0:a=1,volume=0.8,afade=t=out:st=5.1:d=0.4,apad[sfx];
[3:a]volume=0.6,afade=t=out:st=6.98:d=0.4[mus];
[mus][sfx]amix=inputs=2:normalize=0:duration=first[ao]" \
 -map "[v]" -map "[ao]" -t 7.383 -c:v libx264 -crf 19 -pix_fmt yuv420p -r 60 \
 -c:a aac -b:a 160k -movflags +faststart "$SALIDA"
rm -f gancho.txt
echo "ok $SALIDA"

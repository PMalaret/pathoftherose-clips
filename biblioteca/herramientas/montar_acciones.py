"""Montaje aprobado el 26/10/2026: 3 planos de acción desde el primer fotograma + final integrado
(el icono se enciende, se transforma en el medallón y entra la pantalla final).

uso: python3 montar_acciones.py <spec.json> <salida.mp4>

spec.json:
{
  "idioma": "es",                       # es | pt-BR | en | ca | id  -> ../marca/final_<idioma>.mp4
  "musica": "musica/dragon_60s.ogg",    # ruta dentro de biblioteca/
  "musica_ss": 3.65,                    # desde dónde suena (golpe fuerte de dragon_60s)
  "bpm": 110, "tiempos_por_plano": 4,   # cortes en el tiempo: 4 tiempos a 110 BPM = 2,18 s
  "planos": [
    {"clip": "jardin/momento_jabali_esqueleto", "ss": 1.0, "velocidad": 1.0, "tipo": "m", "texto": ["¡CUIDADO,", "ESQUELETO!"]},
    {"clip": "jardin/momento_dragon_persecucion_sir_batistan", "ss": 0.4, "tipo": "d", "texto": ["¡CORRE,", "SIR BATISTAN!"]},
    {"clip": "general/tienda_halloween", "ss": 1.6, "tipo": "t", "texto": ["ESPECIAL", "HALLOWEEN"]}
  ]
}
- clip: sin «_sfx.mp4» (se usa siempre la versión solo efectos y la música va aparte).
- tipo: "d" persecución del dragón (encuadre entero, empuje suave centrado), "m" momento (zoom 1,1 anclado
  arriba con empuje), "t" tienda (tal cual).
- velocidad: 1.0 = velocidad real (aprobado). <1 alarga un clip corto (p. ej. 0.89 para un clip de 2 s).
- texto: 1 o 2 líneas; el tamaño se ajusta solo para que quepa en 940 px.
"""
import json, os, subprocess, sys, tempfile
from PIL import ImageFont

H = os.path.dirname(os.path.abspath(__file__))
B = os.path.normpath(os.path.join(H, '..'))
F = f'{B}/marca/cinzel-900.woff'
X1 = 0.30          # fundido de la acción al final integrado
FIN = 4.2          # duración de final_<idioma>.mp4

spec = json.load(open(sys.argv[1]))
out = sys.argv[2]
lang = spec.get('idioma', 'es')
beat = 60.0 / spec.get('bpm', 110)
d = round(spec.get('tiempos_por_plano', 4) * beat, 4)
shots = spec['planos']
G = d * len(shots)
END = round(G - X1 + FIN, 3)

def fsize(lines, base=124, maxw=940):
    f = ImageFont.truetype(F, base)
    w = max(f.getbbox(l, stroke_width=8)[2] for l in lines)
    return int(base * min(1, maxw / w))

ST = f"fontfile={F}:fontcolor=0xF3D98E:borderw=8:bordercolor=0x2A1408:shadowcolor=0x000000AA:shadowy=6:x=(w-text_w)/2"
tmp = tempfile.mkdtemp()
cmd = ['ffmpeg', '-v', 'error', '-y', '-i', f'{B}/marca/final_{lang}.mp4']
for p in shots:
    sp = p.get('velocidad', 1.0)
    cmd += ['-ss', f"{p.get('ss', 0)}", '-t', f'{d * sp + 0.05:.3f}', '-i', f"{B}/{p['clip']}_sfx.mp4"]
cmd += ['-ss', f"{spec.get('musica_ss', 0)}", '-i', f"{B}/{spec.get('musica', 'musica/dragon_60s.ogg')}"]
mi = len(shots) + 1
fc = ['[0:v]format=yuv420p,setsar=1,fps=60,settb=1/60[a]']
nf = round(d * 60)
for k, p in enumerate(shots):
    sp = p.get('velocidad', 1.0); kind = p.get('tipo', 'm'); lines = p['texto']
    if kind == 'd':
        zp = f"zoompan=z='1.0+0.04*in/{nf}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=1080x1920:fps=60"
    elif kind == 't':
        zp = 'scale=1080:1920'
    else:
        zp = f"zoompan=z='1.1+0.06*in/{nf}':x='iw/2-iw/zoom/2':y='0':d=1:s=1080x1920:fps=60"
    sz = fsize(lines); txt = ''
    for j, l in enumerate(lines):
        tf = f'{tmp}/t{k}_{j}.txt'; open(tf, 'w').write(l)
        y = 200 + j * int(sz * 1.12) if len(lines) > 1 else 220
        txt += f',drawtext={ST}:textfile={tf}:fontsize={sz}:y={y}'
    pre = f'setpts=PTS/{sp},' if sp != 1.0 else ''
    fc.append(f'[{k+1}:v]{pre}fps=60,{zp},setsar=1,trim=end_frame={nf},setpts=PTS-STARTPTS{txt},format=yuv420p[s{k}]')
    fc.append(f'[{k+1}:a]atrim=0:{d * sp:.3f},asetpts=PTS-STARTPTS' + (f',atempo={sp}' if sp != 1.0 else '') + f',volume=0.45[x{k}]')
n = len(shots)
fc.append(''.join(f'[s{k}]' for k in range(n)) + f'concat=n={n}:v=1:a=0,fps=60,settb=1/60[gp]')
fc.append(f'[gp][a]xfade=transition=fade:duration={X1}:offset={G - X1:.4f},format=yuv420p[v]')
fc.append(''.join(f'[x{k}]' for k in range(n)) + f'concat=n={n}:v=0:a=1,afade=t=out:st={G - 0.4:.3f}:d=0.4,apad[sfx]')
fc.append(f'[{mi}:a]afade=t=out:st={END - 0.5}:d=0.5,apad[mus]')
fc.append(f'[mus][sfx]amix=inputs=2:normalize=0:duration=first,atrim=0:{END},alimiter=limit=0.95[ao]')
cmd += ['-filter_complex', ';\n'.join(fc), '-map', '[v]', '-map', '[ao]', '-t', f'{END}',
        '-c:v', 'libx264', '-crf', '19', '-pix_fmt', 'yuv420p', '-r', '60', '-c:a', 'aac', '-b:a', '160k',
        '-movflags', '+faststart', out]
subprocess.run(cmd, check=True)
print('ok', out, f'{END} s')

"""Revelación de una skin en la tienda (2,18 s = 4 tiempos a 110 BPM, 60 fps).
  0,00-1,09 s: el zoom de la tienda hasta la carta, acelerado x1,7, con un texto de intriga.
  1,09 s     : al equipar (cae en un tiempo): destello dorado y temblor.
  1,09-2,18 s: la tienda se oscurece, rayos girando, el personaje sale de la carta
               dentro de un remolino de polvo y hojas, chispas, el nombre entra de golpe
               y debajo un subtítulo.
uso:
  python3 revela.py --tienda biblioteca/general/<skin>_tienda_sfx.mp4 --equipa 2.60 \
      --intriga "QUEM CHEGOU?" --nombre "SACI PERERÊ" --sub "DESBLOQUEIE COM ROSAS" --salida rev.mp4
--equipa: segundo exacto del clip de tienda en que el botón pasa de «Equipar» a «EQUIPADO»
(míralo fotograma a fotograma). Hace falta al menos 1,85 s de zoom antes.
--caja x0,y0,x1,y1: zona del dibujo dentro de la carta (por defecto 272,560,790,1112, la carta
centrada al final del zoom). Revisa siempre <salida>_recorte.png: el personaje debe salir
limpio, sin el fondo crema de la carta ni la sombra del suelo.
Sale sin audio: el audio se monta aparte (ver montar_ejemplo.sh).
"""
import sys, os, math, random, glob, argparse, subprocess, tempfile, shutil
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance, ImageChops

ap = argparse.ArgumentParser()
ap.add_argument('--tienda', required=True); ap.add_argument('--equipa', type=float, required=True)
ap.add_argument('--intriga', required=True); ap.add_argument('--nombre', required=True)
ap.add_argument('--sub', default=''); ap.add_argument('--salida', required=True)
ap.add_argument('--caja', default='272,560,790,1112')
ap.add_argument('--arte', default='', help='PNG transparente de la skin (biblioteca/marca/skins/<skin>.png). Recomendado: sale más nítido que el recorte.')
A_ = ap.parse_args()
TEASER, NAME, SUB = A_.intriga, A_.nombre, A_.sub
W, H = 1080, 1920
FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'marca', 'cinzel-900.woff')
GOLD = (243, 217, 142); DARK = (42, 20, 8)
EQ = 65; N = 131
box = [int(v) for v in A_.caja.split(',')]
CX = (box[0] + box[2]) // 2
tmp = tempfile.mkdtemp(); dirA = f'{tmp}/A'; out = f'{tmp}/B'; os.makedirs(dirA); os.makedirs(out)

# parte A: zoom acelerado x1,7 que termina justo al equipar
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{A_.equipa - 1.85:.3f}', '-t', '1.87', '-i', A_.tienda,
                '-vf', 'setpts=PTS/1.7,fps=60,tmix=frames=2', '-frames:v', '65', f'{dirA}/a%04d.png'], check=True)
# carta ya equipada, a resolución completa
card_p = f'{tmp}/card.png'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{A_.equipa + 0.3:.3f}', '-i', A_.tienda, '-frames:v', '1', card_p], check=True)

# recorte del personaje: quita el fondo crema conectado al borde y la sombra del suelo
im = Image.open(card_p).convert('RGB').crop(box)
a = np.asarray(im).astype(int); h, w, _ = a.shape
r_, g_, b_ = a[..., 0], a[..., 1], a[..., 2]
cream = (r_ > 200) & (g_ > 185) & (b_ > 150) & ((r_ - b_) < 75) & (abs(r_ - g_) < 35)
lab, n = ndimage.label(cream)
border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
bg = np.isin(lab, list(border))
sat = a.max(-1) - a.min(-1)
shadow = (np.arange(h)[:, None] > h - 40) & (sat < 60) & (r_ > 185) & (g_ > 170)
fg = ndimage.binary_opening(~bg & ~shadow, iterations=1)
lab2, n2 = ndimage.label(fg); sizes = ndimage.sum(fg, lab2, range(1, n2 + 1))
fg = np.isin(lab2, [i + 1 for i, s in enumerate(sizes) if s > max(3000, 0.05 * sizes.max())])
m = Image.fromarray((fg * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(1))
cut = im.convert('RGBA'); cut.putalpha(m)
bb = m.getbbox(); cut = cut.crop(bb)
cut_p = A_.salida.rsplit('.', 1)[0] + '_recorte.png'
prev = Image.new('RGBA', cut.size, (40, 90, 40, 255)); prev.alpha_composite(cut); prev.convert('RGB').save(cut_p)
CUT_CY0 = box[1] + (bb[1] + bb[3]) / 2
ART_K = 1.0
if A_.arte:
    # dibujo original: mismo tamaño y posición que en la carta, guardado a la escala máxima (x1,85)
    ART_K = 1.85
    art = Image.open(A_.arte).convert('RGBA'); art = art.crop(art.getbbox())
    th = int(cut.height * ART_K)
    cut = art.resize((max(1, int(art.width * th / art.height)), th), Image.LANCZOS)

def eo(t): t = min(max(t, 0), 1); return 1 - (1 - t) ** 3
def eob(t, s=2.2): t = min(max(t, 0), 1) - 1; return t*t*((s+1)*t+s) + 1

def text_img(txt, size, stroke=9, maxw=1000):
    f = ImageFont.truetype(FONT, size)
    while f.getbbox(txt, stroke_width=stroke)[2] > maxw and size > 40:
        size -= 2; f = ImageFont.truetype(FONT, size)
    bb = f.getbbox(txt, stroke_width=stroke)
    im = Image.new('RGBA', (bb[2]-bb[0]+60, bb[3]-bb[1]+70), (0, 0, 0, 0))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((30-bb[0], 42-bb[1]), txt, font=f, fill=(0, 0, 0, 170), stroke_width=stroke, stroke_fill=(0, 0, 0, 170))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    ImageDraw.Draw(im).text((30-bb[0], 30-bb[1]), txt, font=f, fill=GOLD, stroke_width=stroke, stroke_fill=DARK)
    return im

def scaled(im, s):
    return im.resize((max(1, int(im.width*s)), max(1, int(im.height*s))), Image.BICUBIC)

def put_center(fr, im, cx, cy, alpha=1.0):
    if alpha < 1:
        im = im.copy(); im.putalpha(im.split()[3].point(lambda v: int(v*alpha)))
    fr.alpha_composite(im, (int(cx - im.width/2), int(cy - im.height/2)))

T_TEASER = text_img(TEASER, 112)
T_NAME = text_img(NAME, 118, 10)
T_SUB = text_img(SUB, 62, 7) if SUB else None

# --- personaje recortado con contorno blanco y brillo ---
pad = int(50 * ART_K)
C = Image.new('RGBA', (cut.width+2*pad, cut.height+2*pad), (0, 0, 0, 0))
a = Image.new('L', C.size, 0); a.paste(cut.split()[3], (pad, pad))
outline = a.filter(ImageFilter.MaxFilter(2 * round(6 * ART_K) + 1))
glow = a.filter(ImageFilter.MaxFilter(2 * round(10 * ART_K) + 1)).filter(ImageFilter.GaussianBlur(16 * ART_K))
C.paste(Image.new('RGBA', C.size, (255, 214, 120, 255)), (0, 0), glow)
C.paste(Image.new('RGBA', C.size, (255, 250, 235, 255)), (0, 0), outline)
C.alpha_composite(cut, (pad, pad))
SH = Image.new('RGBA', C.size, (0, 0, 0, 0))
SH.paste(Image.new('RGBA', C.size, (0, 0, 0, 255)), (0, 0), outline.filter(ImageFilter.GaussianBlur(18 * ART_K)).point(lambda v: int(v*0.6)))

# --- fondo de la parte B: la carta equipada, oscurecida ---
card = Image.open(card_p).convert('RGB')
def bg_b(k):
    b = ImageEnhance.Brightness(card).enhance(1 - 0.6*k)
    if k > 0: b = b.filter(ImageFilter.GaussianBlur(6*k))
    return b.convert('RGBA')
BGS = {}

# --- rayos ---
R = 2200
rays = Image.new('L', (R, R), 0)
d = ImageDraw.Draw(rays)
for i in range(16):
    a0 = 2*math.pi*i/16; a1 = a0 + 2*math.pi/16*0.45
    d.polygon([(R/2, R/2)] + [(R/2 + R*math.cos(q), R/2 + R*math.sin(q)) for q in (a0, a1)], fill=255)
fall = ImageChops.invert(Image.radial_gradient('L').resize((R, R))).point(lambda v: int(255*(v/255)**1.8))
rays = ImageChops.multiply(rays, fall).filter(ImageFilter.GaussianBlur(8))
RAYCOL = Image.new('RGBA', (R, R), (255, 205, 110, 255))

random.seed(3)
sparks = [dict(a=random.uniform(0, 6.283), v=random.uniform(900, 2200), s=random.uniform(5, 13)) for _ in range(40)]
leaves = [dict(r=random.uniform(170, 330), a=random.uniform(0, 6.283), y=random.uniform(-300, 260),
               sp=random.uniform(7, 11), s=random.uniform(14, 26), c=random.choice([(92, 140, 50), (150, 110, 60), (200, 170, 110)]))
          for _ in range(22)]

framesA = sorted(glob.glob(f'{dirA}/*.png'))
for f in range(N):
    if f < EQ:
        fr = Image.open(framesA[min(f, len(framesA)-1)]).convert('RGBA')
        k = eob((f - 2)/14)
        if k > 0:
            put_center(fr, scaled(T_TEASER, 0.6 + 0.4*k), W/2, 300, min(1, (f-2)/6))
    else:
        t = (f - EQ) / 60
        k = eo(t/0.25)
        kq = round(k, 2)
        if kq not in BGS: BGS[kq] = bg_b(kq)
        fr = BGS[kq].copy()
        # rayos
        rr = rays.rotate(-t*40, resample=Image.BICUBIC).point(lambda v: int(v*0.75*k))
        fr.paste(RAYCOL, (CX - R//2, 900 - R//2), rr)
        # remolino de polvo (detrás)
        dd = ImageDraw.Draw(fr)
        ky = eo(t/0.3)
        cy = CUT_CY0 + (920 - CUT_CY0)*ky
        for j in range(7):
            rad = 210 + j*32 + 18*math.sin(t*6 + j)
            ry = rad*0.28
            yy = cy + 330 - j*50
            st = (t*720*(1 + j*0.08) + j*50) % 360
            col = (236, 214, 170, int(200*k*(1 - j/10)))
            dd.arc((CX - rad, yy - ry, CX + rad, yy + ry), st, st + 230, fill=col, width=12)
        # personaje sale de la carta
        s = 1.0 + 0.85*eob(t/0.3)
        bob = 8*math.sin(t*9) if t > 0.3 else 0
        rot = 6*math.sin(t*7)*min(1, t/0.3)
        Cs = scaled(C, s / ART_K).rotate(rot, resample=Image.BICUBIC, expand=True)
        Ss = scaled(SH, s / ART_K).rotate(rot, resample=Image.BICUBIC, expand=True)
        put_center(fr, Ss, CX + 14, cy + 30 + bob, 0.8)
        put_center(fr, Cs, CX, cy + bob)
        # remolino (delante) y hojas
        for j in range(3):
            rad = 250 + j*45; ry = rad*0.28; yy = cy + 370 - j*45
            st = (t*900 + 180 + j*70) % 360
            dd.arc((CX - rad, yy - ry, CX + rad, yy + ry), st, st + 130, fill=(245, 230, 200, int(230*k)), width=10)
        for L in leaves:
            ang = L['a'] + t*L['sp']
            x = CX + L['r']*math.cos(ang); y = cy + L['y'] + L['r']*0.25*math.sin(ang) - t*120
            sz = L['s']*(0.7 + 0.3*math.sin(ang))
            dd.ellipse((x - sz, y - sz*0.45, x + sz, y + sz*0.45), fill=L['c'] + (int(230*k),))
        # chispas
        for sp in sparks:
            dist = sp['v']*(1 - math.exp(-t*4))/4
            x = CX + dist*math.cos(sp['a']); y = 900 + dist*math.sin(sp['a'])
            al = max(0, 1 - t/0.9)
            sz = sp['s']*al
            if sz > 0.5:
                c = (255, 240, 190, int(255*al))
                dd.polygon([(x, y-sz*2.2), (x+sz*0.5, y), (x, y+sz*2.2), (x-sz*0.5, y)], fill=c)
                dd.polygon([(x-sz*2.2, y), (x, y+sz*0.5), (x+sz*2.2, y), (x, y-sz*0.5)], fill=c)
        # nombre que golpea y subtítulo
        kn = (f - EQ - 3)/10
        if kn > 0:
            put_center(fr, scaled(T_NAME, 1 + 1.3*(1 - eo(kn))), W/2, 300, min(1, kn*3))
        ks = (f - EQ - 22)/10
        if ks > 0 and T_SUB:
            put_center(fr, T_SUB, W/2, 1445 + 40*(1 - eo(ks)), eo(ks))
        # flash
        if f - EQ < 6:
            fl = Image.new('RGBA', (W, H), (255, 225, 150, int(130*(1 - (f-EQ)/6))))
            fr.alpha_composite(fl)
        # temblor
        if f - EQ < 8:
            amp = 22*(1 - (f-EQ)/8)
            fr = fr.transform(fr.size, Image.AFFINE, (1, 0, amp*math.sin(f*2.1), 0, 1, amp*math.cos(f*1.7)), resample=Image.BILINEAR)
    fr.convert('RGB').save(f'{out}/f{f:04d}.png', compress_level=1)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', '60', '-i', f'{out}/f%04d.png',
                '-c:v', 'libx264', '-crf', '16', '-pix_fmt', 'yuv420p', A_.salida], check=True)
shutil.rmtree(tmp)
print('ok', A_.salida, '| revisa', cut_p)

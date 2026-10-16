"""Revelación de una skin en la tienda SIN ampliar el dibujo (2,18 s = 4 tiempos a 110 BPM, 60 fps).
Variante segura para TikTok: el 15/10/2026 TikTok etiquetó como «generado por IA» y no repartió
un vídeo en el que el dibujo de la skin salía ampliado de la carta. Aquí la carta se queda en la tienda.
  0,00-1,09 s: zoom de la tienda hasta la carta, acelerado x1,7, con texto de intriga.
  1,09 s     : al equipar (cae en un tiempo): destello dorado, temblor y golpe de zoom sobre la carta.
  1,09-2,18 s: la tienda sigue en vivo; fuera de la carta se oscurece y giran rayos dorados,
               chispas que salen de la carta, nombre que entra de golpe y subtítulo debajo.
uso:
  python3 revela_carta.py --tienda ../general/<skin>_tienda_sfx.mp4 --equipa 2.60 --caja 272,560,790,1112 \\
      --intriga "QUEM CHEGOU?" --nombre "SACI PERERÊ" --sub "DESBLOQUEIE COM ROSAS" --salida rev.mp4
--caja: la misma zona del dibujo que en revela.py; la carta entera se calcula a partir de ella.
Sale sin audio.
"""
import os, math, random, glob, argparse, subprocess, tempfile, shutil
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance, ImageChops

ap = argparse.ArgumentParser()
ap.add_argument('--tienda', required=True); ap.add_argument('--equipa', type=float, required=True)
ap.add_argument('--intriga', required=True); ap.add_argument('--nombre', required=True)
ap.add_argument('--sub', default=''); ap.add_argument('--salida', required=True)
ap.add_argument('--caja', default='272,560,790,1112')
A = ap.parse_args()
W, H = 1080, 1920
FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'marca', 'cinzel-900.woff')
GOLD = (243, 217, 142); DARK = (42, 20, 8)
EQ = 65; N = 131
b = [int(v) for v in A.caja.split(',')]
CARD = (b[0] - 76, b[1] - 160, b[2] + 76, b[3] + 398)
CX, CY = (CARD[0] + CARD[2]) // 2, (CARD[1] + CARD[3]) // 2

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

T_TEASER = text_img(A.intriga, 112)
T_NAME = text_img(A.nombre, 118, 10)
T_SUB = text_img(A.sub, 62, 7) if A.sub else None

tmp = tempfile.mkdtemp(); dA, dB, out = f'{tmp}/A', f'{tmp}/B', f'{tmp}/O'
for d in (dA, dB, out): os.makedirs(d)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{A.equipa - 1.85:.3f}', '-t', '1.87', '-i', A.tienda,
                '-vf', 'setpts=PTS/1.7,fps=60,tmix=frames=2', '-frames:v', '65', f'{dA}/a%04d.png'], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{A.equipa:.3f}', '-t', '1.2', '-i', A.tienda,
                '-vf', 'fps=60', '-frames:v', '66', f'{dB}/b%04d.png'], check=True)
fA = sorted(glob.glob(f'{dA}/*.png')); fB = sorted(glob.glob(f'{dB}/*.png'))

# máscara: todo menos la carta (esquinas redondeadas)
outside = Image.new('L', (W, H), 255)
ImageDraw.Draw(outside).rounded_rectangle(CARD, radius=40, fill=0)
outside = outside.filter(ImageFilter.GaussianBlur(10))
glowcard = Image.new('L', (W, H), 0)
ImageDraw.Draw(glowcard).rounded_rectangle(CARD, radius=40, outline=255, width=26)
glowcard = glowcard.filter(ImageFilter.GaussianBlur(22))

R = 2400
rays = Image.new('L', (R, R), 0)
d = ImageDraw.Draw(rays)
for i in range(16):
    a0 = 2*math.pi*i/16; a1 = a0 + 2*math.pi/16*0.45
    d.polygon([(R/2, R/2)] + [(R/2 + R*math.cos(q), R/2 + R*math.sin(q)) for q in (a0, a1)], fill=255)
fall = ImageChops.invert(Image.radial_gradient('L').resize((R, R))).point(lambda v: int(255*(v/255)**1.6))
rays = ImageChops.multiply(rays, fall).filter(ImageFilter.GaussianBlur(8))

random.seed(5)
sparks = [dict(a=random.uniform(0, 6.283), v=random.uniform(900, 2400), s=random.uniform(6, 14)) for _ in range(46)]

for f in range(N):
    if f < EQ:
        fr = Image.open(fA[min(f, len(fA)-1)]).convert('RGBA')
        k = eob((f - 2)/14)
        if k > 0:
            put_center(fr, scaled(T_TEASER, 0.6 + 0.4*k), W/2, 300, min(1, (f-2)/6))
    else:
        t = (f - EQ) / 60
        k = eo(t/0.25)
        base = Image.open(fB[min(f - EQ, len(fB)-1)]).convert('RGB')
        dark = ImageEnhance.Brightness(base).enhance(0.45).filter(ImageFilter.GaussianBlur(5))
        fr = Image.composite(dark, base, outside.point(lambda v: int(v*k))).convert('RGBA')
        rr = rays.rotate(-t*40, resample=Image.BICUBIC)
        rr = ImageChops.multiply(rr.crop((R//2 - CX, R//2 - CY, R//2 - CX + W, R//2 - CY + H)), outside).point(lambda v: int(v*0.8*k))
        fr.paste(Image.new('RGBA', (W, H), (255, 205, 110, 255)), (0, 0), rr)
        pulse = 0.6 + 0.4*math.sin(t*10)
        fr.paste(Image.new('RGBA', (W, H), (255, 220, 130, 255)), (0, 0), glowcard.point(lambda v: int(v*k*pulse)))
        dd = ImageDraw.Draw(fr)
        for sp in sparks:
            dist = 330 + sp['v']*(1 - math.exp(-t*4))/4
            x = CX + dist*math.cos(sp['a']); y = CY + dist*1.4*math.sin(sp['a'])
            al = max(0, 1 - t/0.9); sz = sp['s']*al
            if sz > 0.5:
                c = (255, 240, 190, int(255*al))
                dd.polygon([(x, y-sz*2.2), (x+sz*0.5, y), (x, y+sz*2.2), (x-sz*0.5, y)], fill=c)
                dd.polygon([(x-sz*2.2, y), (x, y+sz*0.5), (x+sz*2.2, y), (x, y-sz*0.5)], fill=c)
        # golpe de zoom sobre la carta
        z = 1 + 0.10*(1 - eo(t/0.35)) + 0.04*eo(t/0.35)
        if z != 1:
            zw, zh = int(W*z), int(H*z)
            big = fr.resize((zw, zh), Image.BICUBIC)
            ox = int(CX*z - CX); oy = int(CY*z - CY)
            fr = big.crop((ox, oy, ox + W, oy + H))
        kn = (f - EQ - 3)/10
        if kn > 0:
            put_center(fr, scaled(T_NAME, 1 + 1.3*(1 - eo(kn))), W/2, 270, min(1, kn*3))
        ks = (f - EQ - 18)/10
        if ks > 0 and T_SUB:
            put_center(fr, T_SUB, W/2, 375 + 30*(1 - eo(ks)), eo(ks))
        if f - EQ < 6:
            fr.alpha_composite(Image.new('RGBA', (W, H), (255, 225, 150, int(130*(1 - (f-EQ)/6)))))
        if f - EQ < 8:
            amp = 22*(1 - (f-EQ)/8)
            fr = fr.transform(fr.size, Image.AFFINE, (1, 0, amp*math.sin(f*2.1), 0, 1, amp*math.cos(f*1.7)), resample=Image.BILINEAR)
    fr.convert('RGB').save(f'{out}/f{f:04d}.png', compress_level=1)

subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', '60', '-i', f'{out}/f%04d.png',
                '-c:v', 'libx264', '-crf', '16', '-pix_fmt', 'yuv420p', A.salida], check=True)
shutil.rmtree(tmp)
print('ok', A.salida)

"""Final integrado (4,2 s): el icono se enciende a oscuras, se transforma en el medallón
(cuadrado redondeado -> círculo, se encoge a su sitio) mientras amanece el fondo, y entra la pantalla final.
uso: python3 final_animado.py <es|pt-BR|en|ca|id> ../marca/icono_fin.mp4 ../marca/final_<idioma>.mp4
"""
import sys, math, random, os, subprocess, tempfile, shutil
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops, ImageEnhance

REPO = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'marca')
lang, ICO_MP4, mp4 = sys.argv[1], sys.argv[2], sys.argv[3]
N = 132
out = tempfile.mkdtemp()
W, H = 1080, 1920
FPS = 60
CTA = {'es': '¡JUEGA YA!', 'pt-BR': 'JOGUE AGORA!', 'en': 'PLAY NOW!', 'ca': 'JUGA ARA!', 'id': 'MAIN SEKARANG!'}[lang]
BADGE = {'es': 'Spanish', 'pt-BR': 'Portuguese-Brazil', 'en': 'English', 'ca': 'Catalan', 'id': 'Indonesian'}[lang]
FONT = f'{REPO}/cinzel-900.woff'
GOLD = (243, 217, 142)
DARK = (42, 20, 8)
os.makedirs(out, exist_ok=True)

def ease_out_back(t, s=1.70158):
    t = min(max(t, 0), 1) - 1
    return t * t * ((s + 1) * t + s) + 1

def ease_out(t):
    t = min(max(t, 0), 1)
    return 1 - (1 - t) ** 3

# ---------- fondo ----------
bg = Image.open(f'{REPO}/fondo_cierre.png').convert('RGB').filter(ImageFilter.GaussianBlur(10))
bg = ImageEnhance.Brightness(bg).enhance(0.55)
bg = ImageEnhance.Color(bg).enhance(0.8)
warm = Image.new('RGB', (W, H), (70, 35, 10))
bg = Image.blend(bg, warm, 0.25)
MC = (540, 840)          # centro del medallón
# brillo cálido detrás del medallón + viñeta
glow = Image.new('L', (W, H), 0)
d = ImageDraw.Draw(glow)
d.ellipse((MC[0]-520, MC[1]-520, MC[0]+520, MC[1]+520), fill=150)
glow = glow.filter(ImageFilter.GaussianBlur(170))
bg = Image.composite(Image.new('RGB', (W, H), (255, 190, 90)), bg, glow.point(lambda v: int(v*0.55)))
vig = Image.new('L', (W, H), 0)
ImageDraw.Draw(vig).ellipse((-260, -120, W+260, H+120), fill=255)
vig = vig.filter(ImageFilter.GaussianBlur(220))
bg = Image.composite(bg, Image.new('RGB', (W, H), (8, 4, 2)), vig)
bg = bg.convert('RGBA')

# ---------- rayos ----------
R = 2400
rays = Image.new('L', (R, R), 0)
d = ImageDraw.Draw(rays)
n = 18
for i in range(n):
    a0 = 2*math.pi*i/n; a1 = a0 + 2*math.pi/n*0.42
    pts = [(R/2, R/2)] + [(R/2 + R*math.cos(a), R/2 + R*math.sin(a)) for a in (a0, a1)]
    d.polygon(pts, fill=255)
mask = Image.new('L', (R, R), 0)
ImageDraw.Draw(mask).ellipse((0, 0, R, R), fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(1))
fall = Image.radial_gradient('L').resize((R, R))           # 0 centro -> 255 borde
fall = ImageChops.invert(fall)
fall = fall.point(lambda v: int(255*(v/255)**2.2))
rays = ImageChops.multiply(rays, fall).filter(ImageFilter.GaussianBlur(10))
rays = rays.point(lambda v: int(v*0.38))

# ---------- medallón ----------
MR = 285                                              # radio exterior con anillo
art = Image.open(f'{REPO}/icono_arte.png').convert('RGBA')
ART_R = 248
art = art.resize((ART_R*2, ART_R*2), Image.LANCZOS)
SZ = MR*2 + 80
med = Image.new('RGBA', (SZ, SZ), (0, 0, 0, 0))
c = SZ//2
# sombra
sh = Image.new('L', (SZ, SZ), 0)
ImageDraw.Draw(sh).ellipse((c-MR, c-MR+14, c+MR, c+MR+14), fill=200)
sh = sh.filter(ImageFilter.GaussianBlur(18))
med.paste(Image.new('RGBA', (SZ, SZ), (0, 0, 0, 255)), (0, 0), sh)
# anillo dorado con degradado
ring = Image.new('RGBA', (SZ, SZ), (0, 0, 0, 0))
grad = Image.linear_gradient('L').resize((SZ, SZ))
gold = Image.merge('RGBA', (grad.point(lambda v: int(255 - v*0.15)), grad.point(lambda v: int(232 - v*0.45)),
                            grad.point(lambda v: int(150 - v*0.5)), Image.new('L', (SZ, SZ), 255)))
rm = Image.new('L', (SZ, SZ), 0)
ImageDraw.Draw(rm).ellipse((c-MR, c-MR, c+MR, c+MR), fill=255)
med.paste(gold, (0, 0), rm)
dd = ImageDraw.Draw(med)
dd.ellipse((c-MR, c-MR, c+MR, c+MR), outline=DARK+(255,), width=5)
dd.ellipse((c-MR+16, c-MR+16, c+MR-16, c+MR-16), outline=(120, 70, 20, 255), width=3)
# remaches del anillo
for i in range(24):
    a = 2*math.pi*i/24
    x, y = c + (MR-9)*math.cos(a), c + (MR-9)*math.sin(a)
    dd.ellipse((x-4, y-4, x+4, y+4), fill=(255, 240, 190, 255), outline=(110, 60, 15, 255))
# arte recortado en círculo
am = Image.new('L', (ART_R*2, ART_R*2), 0)
ImageDraw.Draw(am).ellipse((0, 0, ART_R*2-1, ART_R*2-1), fill=255)
am = am.filter(ImageFilter.GaussianBlur(0.8))
med.paste(art, (c-ART_R, c-ART_R), am)
dd.ellipse((c-ART_R, c-ART_R, c+ART_R, c+ART_R), outline=DARK+(255,), width=4)
# reflejo de cristal
hl = Image.new('L', (SZ, SZ), 0)
ImageDraw.Draw(hl).ellipse((c-ART_R*0.9, c-ART_R*0.95, c+ART_R*0.5, c-ART_R*0.1), fill=60)
amz = Image.new('L', (SZ, SZ), 0); amz.paste(am, (c-ART_R, c-ART_R))
hl = ImageChops.multiply(hl.filter(ImageFilter.GaussianBlur(30)), amz)
med.paste(Image.new('RGBA', (SZ, SZ), (255, 255, 240, 255)), (0, 0), hl)

# ---------- logo con halo (sin caja) ----------
logo = Image.open(f'{REPO}/logo.png').convert('RGBA')
LW = 860
logo = logo.resize((LW, int(logo.height*LW/logo.width)), Image.LANCZOS)
pad = 40
L = Image.new('RGBA', (logo.width+2*pad, logo.height+2*pad), (0, 0, 0, 0))
a = Image.new('L', L.size, 0); a.paste(logo.split()[3], (pad, pad))
halo_in = a.filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.MaxFilter(7))
halo_out = halo_in.filter(ImageFilter.MaxFilter(9))
shadow = halo_out.filter(ImageFilter.GaussianBlur(14))
L.paste(Image.new('RGBA', L.size, (0, 0, 0, 255)), (0, 8), shadow.point(lambda v: int(v*0.7)))
L.paste(Image.new('RGBA', L.size, DARK+(255,)), (0, 0), halo_out)
L.paste(Image.new('RGBA', L.size, (246, 234, 205, 255)), (0, 0), halo_in)
L.alpha_composite(logo, (pad, pad))

# ---------- texto CTA ----------
font = ImageFont.truetype(FONT, 92)
tb = font.getbbox(CTA, stroke_width=9)
T = Image.new('RGBA', (tb[2]-tb[0]+40, tb[3]-tb[1]+50), (0, 0, 0, 0))
td = ImageDraw.Draw(T)
td.text((20-tb[0], 30-tb[1]), CTA, font=font, fill=(0, 0, 0, 150), stroke_width=9, stroke_fill=(0, 0, 0, 150))
T = T.filter(ImageFilter.GaussianBlur(5))
ImageDraw.Draw(T).text((20-tb[0], 22-tb[1]), CTA, font=font, fill=GOLD, stroke_width=9, stroke_fill=DARK)

badge = Image.open(f'{REPO}/google_play_{BADGE}.png').convert('RGBA')

# ---------- divisor ornamental ----------
def divider(w=520):
    D = Image.new('RGBA', (w, 40), (0, 0, 0, 0))
    g = ImageDraw.Draw(D)
    m = w//2
    for s in (-1, 1):
        g.line((m + s*26, 20, m + s*(w//2-10), 20), fill=GOLD+(255,), width=4)
        g.ellipse((m + s*(w//2-10) - 6, 14, m + s*(w//2-10) + 6, 26), fill=GOLD+(255,))
    g.polygon([(m, 6), (m+14, 20), (m, 34), (m-14, 20)], fill=(200, 30, 45, 255), outline=GOLD+(255,))
    return D
DIV = divider()

# ---------- pétalos ----------
def petal(size):
    p = Image.new('RGBA', (size, int(size*1.3)), (0, 0, 0, 0))
    g = ImageDraw.Draw(p)
    w, h = p.size
    g.ellipse((0, 0, w-1, h-1), fill=(176, 18, 40, 255))
    g.ellipse((w*0.2, h*0.15, w*0.75, h*0.7), fill=(214, 45, 62, 255))
    g.polygon([(w*0.35, 0), (w*0.5, h*0.18), (w*0.65, 0)], fill=(0, 0, 0, 0))
    return p.filter(ImageFilter.GaussianBlur(0.8))
random.seed(7)
petals = []
for i in range(16):
    size = random.randint(22, 46)
    petals.append(dict(img=petal(size), x=random.uniform(30, W-30), y0=random.uniform(-500, H*0.75),
                       vy=random.uniform(170, 300), sway=random.uniform(20, 55), fq=random.uniform(0.6, 1.4),
                       ph=random.uniform(0, 6.28), rot=random.uniform(0, 360), vr=random.uniform(-160, 160),
                       a=random.uniform(0.55, 0.95)))

# chispas
sparks = [dict(ang=random.uniform(0, 6.28), r=random.uniform(MR+20, MR+120), ph=random.uniform(0, 6.28),
               f=random.uniform(2, 4)) for _ in range(14)]

LOGO_Y = 360
DIV_Y = 1150
CTA_Y = 1185
BADGE_Y = 1315


import numpy as np
NA, NB, NC = 84, 36, 132          # icono 1,4 s · transformación 0,6 s · pantalla final 2,2 s
def smooth(t): t = min(max(t, 0), 1); return t*t*(3-2*t)
# fase A: los fotogramas del icono encendiéndose
icodir = tempfile.mkdtemp()
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', ICO_MP4, '-frames:v', str(NA), f'{icodir}/i%04d.png'], check=True)
for f in range(NA):
    shutil.copy(f'{icodir}/i{f+1:04d}.png', f'{out}/f{f:04d}.png')
lastA = Image.open(f'{icodir}/i{NA:04d}.png').convert('RGBA')
shutil.rmtree(icodir)

S0 = 880; S1 = ART_R*2                 # lado del icono -> diámetro del arte del medallón
artI = Image.open(f'{REPO}/icono_arte.png').convert('RGBA')
darkbg = Image.blend(bg, Image.new('RGBA', (W, H), (3, 3, 8, 255)), 0.9)

def rays_layer(t, k):
    rr = rays.rotate(t*9, resample=Image.BICUBIC)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    lay.paste(Image.new('RGBA', (R, R), (255, 214, 140, 255)), (MC[0]-R//2, MC[1]-R//2), rr.point(lambda v: int(v*k)))
    return lay

def scene(t, morph, tc):
    """morph: 0..1 (icono -> medallón). tc: tiempo de la pantalla final (<0 = aún no)."""
    e = smooth(morph)
    fr = Image.blend(darkbg, bg, e) if e < 1 else bg.copy()
    if e > 0:
        fr.alpha_composite(rays_layer(t, e))
    if e < 1:
        s = int(S0 + (S1 - S0)*e)
        rad = int(s*(0.2 + 0.3*e))
        a = artI.resize((s, s), Image.LANCZOS)
        m = Image.new('L', (s, s), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, s-1, s-1), radius=rad, fill=255)
        a.putalpha(m)
        fr.alpha_composite(a, (MC[0]-s//2, MC[1]-s//2))
        g = Image.new('RGBA', (s, s), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
        al = int(255*(1-e))
        gd.rounded_rectangle((0, 0, s-1, s-1), radius=rad, outline=(120, 70, 18, al), width=max(2, int(22*s/S0)))
        gd.rounded_rectangle((5, 5, s-6, s-6), radius=max(1, rad-5), outline=(236, 190, 90, al), width=max(2, int(11*s/S0)))
        fr.alpha_composite(g, (MC[0]-s//2, MC[1]-s//2))
        # el anillo dorado del medallón aparece alrededor
        ms = max(1, int(SZ*s/S1))
        mm = med.resize((ms, ms), Image.BICUBIC)
        mm.putalpha(mm.split()[3].point(lambda v: int(v*e**1.5)))
        fr.alpha_composite(mm, (MC[0]-ms//2, MC[1]-ms//2))
    else:
        fr.alpha_composite(med, (MC[0]-SZ//2, MC[1]-SZ//2))
    # chispas y pétalos aparecen con la luz
    sd = ImageDraw.Draw(fr)
    for sp in sparks:
        k = (math.sin(t*sp['f']*2 + sp['ph'])+1)/2 * e
        if k < 0.55: continue
        x = MC[0] + sp['r']*math.cos(sp['ang']); y = MC[1] + sp['r']*math.sin(sp['ang'])
        rr_ = 2 + 7*(k-0.55)/0.45
        col = (255, 240, 190, int(255*k))
        sd.polygon([(x, y-rr_*2.2), (x+rr_*0.5, y), (x, y+rr_*2.2), (x-rr_*0.5, y)], fill=col)
        sd.polygon([(x-rr_*2.2, y), (x, y+rr_*0.5), (x+rr_*2.2, y), (x, y-rr_*0.5)], fill=col)
    for p in petals:
        tp = t - 1.4
        y = p['y0'] + p['vy']*tp
        x = p['x'] + p['sway']*math.sin(tp*p['fq']*2 + p['ph'])
        im = p['img'].rotate(p['rot'] + p['vr']*tp, expand=True, resample=Image.BICUBIC)
        im.putalpha(im.split()[3].point(lambda v: int(v*p['a']*e)))
        fr.alpha_composite(im, (int(x), int(y)))
    if tc >= 0:
        k = ease_out((tc-0.0)/0.4)
        if k > 0:
            Lf = L.copy(); Lf.putalpha(Lf.split()[3].point(lambda v: int(v*k)))
            fr.alpha_composite(Lf, (W//2-L.width//2, int(LOGO_Y - pad - 40*(1-k))))
        k = ease_out((tc-0.18)/0.35)
        if k > 0:
            for img, y in ((DIV, DIV_Y), (T, CTA_Y)):
                im = img.copy(); im.putalpha(im.split()[3].point(lambda v: int(v*k)))
                fr.alpha_composite(im, (W//2-img.width//2, int(y + 30*(1-k))))
        k = ease_out((tc-0.3)/0.35)
        if k > 0:
            sc = 0.9 + 0.1*ease_out_back((tc-0.3)/0.35)
            b = badge.resize((int(badge.width*sc), int(badge.height*sc)), Image.LANCZOS)
            b.putalpha(b.split()[3].point(lambda v: int(v*k)))
            fr.alpha_composite(b, (W//2-b.width//2, BADGE_Y + (badge.height-b.height)//2))
    return fr

for i in range(NB + NC):
    f = NA + i
    t = f / FPS
    morph = (i + 1) / NB
    tc = (i - NB*0.55) / FPS            # el logo empieza a bajar al final de la transformación
    fr = scene(t, morph, tc)
    if i < 6:                            # empalme suave con el último fotograma del icono
        fr = Image.blend(lastA, fr, (i + 1) / 7)
    fr.convert('RGB').save(f'{out}/f{f:04d}.png', compress_level=1)
fr.convert('RGB').save(mp4.rsplit('.', 1)[0] + '.png')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(FPS), '-i', f'{out}/f%04d.png',
                '-c:v', 'libx264', '-crf', '16', '-pix_fmt', 'yuv420p', mp4], check=True)
shutil.rmtree(out)
print('ok', mp4)

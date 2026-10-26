"""Icono que se enciende (2,0 s), base del final integrado (lo usa final_animado.py).
el camino dorado se enciende desde el caballero hasta la rosa, la rosa prende y la luz
se extiende por toda la vidriera, brilla el ojo del dragón y la cámara entra en la rosa.
uso: python3 icono_fin.py ../marca ../marca/icono_fin.mp4
"""
import sys, math, random, os, subprocess, tempfile, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

MARCA, MP4 = sys.argv[1], sys.argv[2]
W, H, FPS = 1080, 1920, 60
N = 120
out = tempfile.mkdtemp()

def clamp(t): return min(max(t, 0.0), 1.0)
def ease_out(t): t = clamp(t); return 1 - (1 - t) ** 3
def ease_in(t): t = clamp(t); return t ** 3
def ease_in_out(t): t = clamp(t); return t * t * (3 - 2 * t)

# ---------- icono como en la tienda: cuadrado redondeado con marco dorado ----------
S = 880                                   # lado del icono en pantalla
art = Image.open(f'{MARCA}/icono_arte.png').convert('RGB').resize((S, S), Image.LANCZOS)
A = np.asarray(art).astype(np.float32) / 255.0
rad = int(S * 0.2)
shape = Image.new('L', (S, S), 0)
ImageDraw.Draw(shape).rounded_rectangle((0, 0, S - 1, S - 1), radius=rad, fill=255)
# marco dorado
frame = Image.new('RGBA', (S, S), (0, 0, 0, 0))
fd = ImageDraw.Draw(frame)
fd.rounded_rectangle((0, 0, S - 1, S - 1), radius=rad, outline=(120, 70, 18, 255), width=22)
fd.rounded_rectangle((5, 5, S - 6, S - 6), radius=rad - 5, outline=(236, 190, 90, 255), width=11)
fd.rounded_rectangle((16, 16, S - 17, S - 17), radius=rad - 14, outline=(255, 236, 170, 255), width=3)
FR = np.asarray(frame).astype(np.float32) / 255.0

# versión apagada (vidriera sin luz)
lum = A.mean(2, keepdims=True)
DARKV = (A * 0.25 + lum * 0.75) * np.array([0.16, 0.18, 0.26])

# coordenadas relativas al icono
yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
ROSE = (0.50 * S, 0.27 * S)               # centro de la rosa
dist = np.hypot(xx - ROSE[0], yy - ROSE[1])
DMAX = dist.max()
# camino dorado: píxeles amarillos brillantes de la mitad inferior
r, g, b = A[..., 0], A[..., 1], A[..., 2]
path = ((r > 0.85) & (g > 0.65) & (b < 0.55) & (yy > 0.45 * S) & (xx > 0.38 * S) & (xx < 0.62 * S)).astype(np.float32)
pimg = Image.fromarray((path * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(3))
PATH = np.asarray(pimg).astype(np.float32) / 255.0
PGLOW = np.asarray(pimg.filter(ImageFilter.GaussianBlur(22))).astype(np.float32) / 255.0
# ojo del dragón
EYE = (0.866 * S, 0.405 * S)

# ---------- fondo: noche cerrada con brillo cálido detrás del icono ----------
BG = np.zeros((H, W, 3), np.float32)
gy, gx = np.mgrid[0:H, 0:W].astype(np.float32)
CX, CY = W / 2, 840
bgd = np.hypot((gx - CX) / 1.0, (gy - CY) / 1.25)
BG[...] = np.array([0.020, 0.022, 0.045])
WARMG = np.exp(-(bgd / 520) ** 2)[..., None] * np.array([1.0, 0.62, 0.25])

random.seed(5)
motes = [dict(x=random.uniform(80, 1000), y=random.uniform(380, 1500), ph=random.uniform(0, 6.3),
              f=random.uniform(1.2, 3.0), v=random.uniform(15, 45), r=random.uniform(1.5, 3.5)) for _ in range(28)]

def star(d, x, y, rr, col):
    d.polygon([(x, y - rr * 2.6), (x + rr * 0.45, y), (x, y + rr * 2.6), (x - rr * 0.45, y)], fill=col)
    d.polygon([(x - rr * 2.6, y), (x, y + rr * 0.45), (x + rr * 2.6, y), (x, y - rr * 0.45)], fill=col)

for f in range(N):
    t = f / FPS
    # --- iluminación de la vidriera ---
    pf = ease_in_out((t - 0.20) / 0.70)                 # frente del camino: de abajo (S) a la rosa (0,5 S)
    front = S * (1.0 - 0.52 * pf)
    pm = PATH * np.clip((yy - front) / 40 + 1, 0, 1) if t > 0.2 else PATH * 0
    rk = ease_out((t - 0.85) / 0.55)                     # la luz sale de la rosa hacia fuera
    rr = rk * (DMAX + 120)
    lit = np.clip((rr - dist) / 120, 0, 1) if rk > 0 else np.zeros_like(dist)
    # pulso de latido mientras está a oscuras
    beat = 0.5 + 0.5 * math.cos(2 * math.pi * 1.8 * t)
    darkk = 0.85 + 0.25 * beat ** 6
    lit3 = lit[..., None]
    img = DARKV * darkk * (1 - lit3) + A * lit3
    # el camino encendido
    pm3 = pm[..., None]
    img = img * (1 - pm3) + np.minimum(A * 1.25 + 0.08, 1) * pm3
    halo = (PGLOW * np.clip((yy - front) / 40 + 1, 0, 1))[..., None] if t > 0.2 else 0
    img = img + halo * np.array([1.0, 0.78, 0.30]) * 0.55 * (1 - 0.6 * rk)
    # brillo de la rosa al prender
    rg = math.sin(math.pi * clamp((t - 0.80) / 0.9))
    img = img + (np.exp(-(dist / (90 + 260 * rk)) ** 2) * rg * 0.65)[..., None] * np.array([1.0, 0.8, 0.4])
    img = np.clip(img, 0, 1)
    ico = np.concatenate([img, np.asarray(shape)[..., None].astype(np.float32) / 255.0], 2)
    # marco dorado: se enciende con la luz
    fk = 0.25 + 0.75 * ease_out((t - 0.95) / 0.5)
    fa = FR[..., 3:4]
    ico[..., :3] = ico[..., :3] * (1 - fa) + FR[..., :3] * fk * fa
    icoI = Image.fromarray((ico * 255).astype(np.uint8), 'RGBA')

    # ojo del dragón 1,45-1,85 s
    ek = math.sin(math.pi * clamp((t - 1.45) / 0.4))
    if ek > 0:
        dd = ImageDraw.Draw(icoI)
        gl = Image.new('RGBA', (S, S), (0, 0, 0, 0))
        gd = ImageDraw.Draw(gl)
        gd.ellipse((EYE[0] - 30, EYE[1] - 30, EYE[0] + 30, EYE[1] + 30), fill=(255, 40, 30, int(170 * ek)))
        gl = gl.filter(ImageFilter.GaussianBlur(10))
        icoI.alpha_composite(gl)
        star(ImageDraw.Draw(icoI), EYE[0], EYE[1], 9 * ek, (255, 210, 190, int(255 * ek)))

    # --- cámara: aparece, empuje lento y entrada en la rosa al final ---
    ap = ease_out((t + 0.07) / 0.25)
    sc = 0.94 + 0.06 * ap + 0.04 * clamp((t - 0.25) / 1.6)
    zk = 0.0
    sc *= 1 + 3.0 * zk
    # al entrar, el punto de zoom es la rosa
    ox = (ROSE[0] - S / 2) * sc * zk
    oy = (ROSE[1] - S / 2) * sc * zk
    sz = int(S * sc)
    ic = icoI.resize((sz, sz), Image.BICUBIC)
    if ap < 1:
        ic.putalpha(Image.fromarray((np.asarray(ic.split()[3]) * ap).astype(np.uint8)))

    bgl = 0.15 + 0.85 * rk
    fr = np.clip(BG + WARMG * (0.06 + 0.30 * bgl) * ap, 0, 1)
    frI = Image.fromarray((fr * 255).astype(np.uint8)).convert('RGBA')
    # sombra del icono
    if zk < 0.5:
        sh = Image.new('L', (W, H), 0)
        x0, y0 = int(CX - sz / 2 - ox), int(CY - sz / 2 - oy)
        ImageDraw.Draw(sh).rounded_rectangle((x0 + 10, y0 + 30, x0 + sz - 10, y0 + sz + 30), radius=int(rad * sc), fill=int(200 * ap))
        sh = sh.filter(ImageFilter.GaussianBlur(30))
        frI.paste(Image.new('RGBA', (W, H), (0, 0, 0, 255)), (0, 0), sh)
    frI.alpha_composite(ic, (int(CX - sz / 2 - ox), int(CY - sz / 2 - oy)))
    # motas de luz
    d = ImageDraw.Draw(frI)
    for m in motes:
        k = (math.sin(t * m['f'] * 2 + m['ph']) + 1) / 2 * rk
        if k < 0.45: continue
        star(d, m['x'], m['y'] - m['v'] * t, m['r'] * k, (255, 226, 160, int(220 * k)))
    dk = 0.0
    if dk > 0:
        frI = Image.blend(frI, Image.new('RGBA', (W, H), (4, 5, 12, 255)), dk)
    frI.convert('RGB').save(f'{out}/f{f:04d}.png', compress_level=1)

subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(FPS), '-i', f'{out}/f%04d.png',
                '-c:v', 'libx264', '-crf', '16', '-pix_fmt', 'yuv420p', MP4], check=True)
shutil.rmtree(out)
print('ok', MP4)

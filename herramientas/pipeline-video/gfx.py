"""Graphics for the Somerton documentary: photo prep, overlays, cards, maps."""
import os, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

P = os.path.dirname(os.path.abspath(__file__))
OUT = f"{P}/g"; os.makedirs(OUT, exist_ok=True)
W, H = 1920, 1080
BW_, BH_ = 2880, 1620  # zoompan source size
F = {
    'black': '/usr/share/fonts/opentype/inter/InterDisplay-Black.otf',
    'xbold': '/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf',
    'bold': '/usr/share/fonts/opentype/inter/Inter-Bold.otf',
    'med': '/usr/share/fonts/opentype/inter/Inter-Medium.otf',
    'type': '/usr/share/fonts/X11/Type1/c0419bt_.pfb',
    'typeb': '/usr/share/fonts/X11/Type1/c0583bt_.pfb',
    'serif': '/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf',
    'serifr': '/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf',
}
def font(k, s): return ImageFont.truetype(F[k], int(s))
COL = {'VERIFICADO': (74, 178, 112), 'DISPUTADO': (232, 168, 52), 'LEYENDA': (222, 74, 60)}
PAPER = (226, 214, 186); INK = (38, 32, 26)

rng = np.random.default_rng(3)

def _grain(img, amt=14):
    a = np.asarray(img).astype(np.float32)
    n = rng.normal(0, amt, (a.shape[0] // 2 + 1, a.shape[1] // 2 + 1)).astype(np.float32)
    n = np.kron(n, np.ones((2, 2), np.float32))[:a.shape[0], :a.shape[1]]
    if a.ndim == 3: n = n[..., None]
    return Image.fromarray(np.clip(a + n, 0, 255).astype(np.uint8))

def _vignette(img, strength=0.55):
    w, h = img.size
    y, x = np.ogrid[-1:1:complex(0, h), -1:1:complex(0, w)]
    m = 1 - strength * np.clip((x ** 2 * 0.8 + y ** 2) - 0.25, 0, None)
    a = np.asarray(img).astype(np.float32)
    if a.ndim == 3: m = m[..., None]
    return Image.fromarray(np.clip(a * m, 0, 255).astype(np.uint8))

def cover(img, w, h):
    iw, ih = img.size; s = max(w / iw, h / ih)
    img = img.resize((max(w, int(iw * s + 0.5)), max(h, int(ih * s + 0.5))), Image.LANCZOS)
    iw, ih = img.size
    return img.crop(((iw - w) // 2, (ih - h) // 2, (iw - w) // 2 + w, (ih - h) // 2 + h))

def prep_photo(src, name, bw=True, crop=None, dim=1.0, tint=None):
    out = f"{OUT}/{name}.jpg"
    if os.path.exists(out): return out
    im = Image.open(src).convert('RGB')
    if crop: im = im.crop(crop)
    small = min(im.size) < 900
    im = cover(im, BW_, BH_)
    if small: im = im.filter(ImageFilter.UnsharpMask(radius=3, percent=90, threshold=2))
    if bw:
        g = ImageOps.autocontrast(im.convert('L'), cutoff=0.5)
        t = tint or (232, 236, 240)
        im = ImageOps.colorize(g, (8, 9, 11), t)
        im = _grain(im, 11 if small else 6)
    else:
        im = _grain(im, 6)
    im = _vignette(im)
    if dim != 1.0: im = Image.fromarray((np.asarray(im) * dim).astype(np.uint8))
    im.save(out, quality=92)
    return out

# ---------- overlays (1920x1080 RGBA, not zoomed) ----------
def _ov(): return Image.new('RGBA', (W, H), (0, 0, 0, 0))

def _shadow_text(d, xy, text, f, fill=(240, 236, 228, 255), anchor='la', sh=3):
    x, y = xy
    d.text((x + sh, y + sh), text, font=f, fill=(0, 0, 0, 170), anchor=anchor)
    d.text((x, y), text, font=f, fill=fill, anchor=anchor)

def ov_loc(name, line1, line2=None):
    out = f"{OUT}/ov_{name}.png"
    im = _ov(); d = ImageDraw.Draw(im)
    f1 = font('typeb', 34); f2 = font('type', 28)
    d.rectangle((70, 900, 76, 1000 if line2 else 952), fill=(232, 168, 52, 255))
    _shadow_text(d, (96, 902), line1.upper(), f1)
    if line2: _shadow_text(d, (96, 952), line2, f2, fill=(220, 214, 200, 255))
    im.save(out); return out

def ov_tag():
    out = f"{OUT}/ov_tag.png"
    im = _ov(); d = ImageDraw.Draw(im)
    f = font('bold', 20)
    d.rounded_rectangle((1676, 1012, 1880, 1048), 6, fill=(0, 0, 0, 120))
    d.text((1778, 1030), "RECREACIÓN IA", font=f, fill=(235, 235, 235, 210), anchor='mm')
    im.save(out); return out

def ov_sello(name, kind, caption, pos='tr'):
    out = f"{OUT}/ov_{name}.png"
    c = COL[kind]
    st = Image.new('RGBA', (560, 150), (0, 0, 0, 0)); d = ImageDraw.Draw(st)
    d.rounded_rectangle((8, 8, 552, 142), 14, outline=c + (255,), width=8)
    d.rounded_rectangle((22, 22, 538, 128), 8, outline=c + (200,), width=3)
    d.text((280, 76), kind, font=font('black', 66), fill=c + (255,), anchor='mm')
    # distress
    a = np.asarray(st).copy(); mask = rng.random(a.shape[:2]) < 0.10; a[mask, 3] = (a[mask, 3] * 0.3).astype(np.uint8)
    st = Image.fromarray(a).rotate(-6, expand=True, resample=Image.BICUBIC)
    im = _ov(); d = ImageDraw.Draw(im)
    x0, y0 = (1260, 70) if pos == 'tr' else (100, 70)
    im.alpha_composite(st, (x0, y0))
    if caption:
        f = font('bold', 34)
        lines = _wrap(caption, f, 600)
        yy = y0 + st.size[1] + 10
        hgt = 46 * len(lines) + 24
        d.rounded_rectangle((x0 + 10, yy, x0 + 640, yy + hgt), 10, fill=(10, 10, 12, 190))
        d.rectangle((x0 + 10, yy, x0 + 18, yy + hgt), fill=c + (255,))
        for i, l in enumerate(lines): d.text((x0 + 36, yy + 14 + 46 * i), l, font=f, fill=(245, 242, 235, 255))
    im.save(out); return out

def _wrap(text, f, maxw):
    words = text.split(); lines = []; cur = ''
    for w_ in words:
        t = (cur + ' ' + w_).strip()
        if f.getlength(t) <= maxw: cur = t
        else: lines.append(cur); cur = w_
    if cur: lines.append(cur)
    return lines

def ov_center(name, text, size=86, sub=None, box=True, y=540, col=(245, 242, 235)):
    out = f"{OUT}/ov_{name}.png"
    im = _ov(); d = ImageDraw.Draw(im)
    f = font('xbold', size); lines = _wrap(text, f, 1500)
    lh = size * 1.18; tot = lh * len(lines) + (70 if sub else 0)
    top = y - tot / 2
    if box:
        wmax = max(f.getlength(l) for l in lines)
        d.rounded_rectangle((960 - wmax / 2 - 50, top - 36, 960 + wmax / 2 + 50, top + tot + 30), 16, fill=(0, 0, 0, 150))
    for i, l in enumerate(lines): _shadow_text(d, (960, top + lh * i + lh / 2), l, f, fill=col + (255,), anchor='mm', sh=4)
    if sub:
        _shadow_text(d, (960, top + lh * len(lines) + 34), sub, font('type', 40), fill=(232, 168, 52, 255), anchor='mm')
    im.save(out); return out

def ov_labels(name, items, x=1180, y=230, title=None):
    out = f"{OUT}/ov_{name}.png"
    im = _ov(); d = ImageDraw.Draw(im)
    f = font('typeb', 34); ft = font('bold', 26)
    if title: _shadow_text(d, (x, y - 56), title, ft, fill=(232, 168, 52, 255))
    for i, t in enumerate(items):
        yy = y + i * 74
        w_ = f.getlength(t)
        d.rectangle((x - 14, yy - 8, x + w_ + 18, yy + 50), fill=(228, 218, 192, 235))
        d.text((x, yy), t, font=f, fill=(30, 26, 22, 255))
    im.save(out); return out

def ov_labels_seq(name, items, x=1180, y=230, title=None):
    """one overlay per item (cumulative) for staggered reveal"""
    outs = []
    for k in range(1, len(items) + 1):
        outs.append(ov_labels(f"{name}_{k}", items[:k], x, y, title))
    return outs

# ---------- full-frame cards (2880x1620) ----------
S = 1.5
def _canvas(bg=(14, 14, 16)): return Image.new('RGB', (BW_, BH_), bg)
def _paper(seed=1):
    r = np.random.default_rng(seed)
    base = np.ones((BH_, BW_, 3), np.float32) * np.array(PAPER, np.float32)
    n = r.normal(0, 1, (BH_ // 60 + 2, BW_ // 60 + 2)).astype(np.float32)
    n = np.asarray(Image.fromarray(((n - n.min()) / (n.max() - n.min()) * 255).astype(np.uint8)).resize((BW_, BH_), Image.BICUBIC)).astype(np.float32) / 255
    base *= (0.86 + 0.18 * n)[..., None]
    base += r.normal(0, 6, base.shape[:2])[..., None]
    img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))
    return _vignette(img, 0.45)

def save_card(img, name):
    out = f"{OUT}/{name}.jpg"; img.save(out, quality=93); return out

def card_chapter(num, title, bgsrc=None):
    if bgsrc:
        im = Image.open(bgsrc).convert('RGB'); im = Image.fromarray((np.asarray(im) * 0.28).astype(np.uint8))
    else: im = _canvas()
    d = ImageDraw.Draw(im)
    d.text((BW_ / 2, BH_ / 2 - 120 * S), f"{num:02d}", font=font('black', 260 * S), fill=(232, 168, 52), anchor='mm')
    d.line((BW_ / 2 - 260 * S, BH_ / 2 + 30 * S, BW_ / 2 + 260 * S, BH_ / 2 + 30 * S), fill=(200, 196, 188), width=int(3 * S))
    d.text((BW_ / 2, BH_ / 2 + 110 * S), title.upper(), font=font('typeb', 74 * S), fill=(240, 236, 228), anchor='mm')
    d.text((BW_ / 2, BH_ / 2 + 200 * S), f"CAPÍTULO {num}", font=font('type', 38 * S), fill=(170, 166, 158), anchor='mm')
    return save_card(im, f"card_ch{num}")

def card_title(bgsrc):
    im = Image.open(bgsrc).convert('RGB'); im = Image.fromarray((np.asarray(im) * 0.42).astype(np.uint8))
    d = ImageDraw.Draw(im)
    d.text((BW_ / 2, BH_ / 2 - 130 * S), "EL HOMBRE SIN NOMBRE", font=font('black', 150 * S), fill=(245, 242, 235), anchor='mm')
    d.text((BW_ / 2, BH_ / 2 + 10 * S), "DE LA PLAYA DE SOMERTON", font=font('typeb', 70 * S), fill=(232, 168, 52), anchor='mm')
    d.text((BW_ / 2, BH_ / 2 + 120 * S), "Un documental de investigación", font=font('type', 44 * S), fill=(200, 196, 188), anchor='mm')
    return save_card(im, "card_title")

def _proj(lon, lat, box, bounds):
    x0, y0, x1, y1 = box; lo0, la0, lo1, la1 = bounds
    return (x0 + (lon - lo0) / (lo1 - lo0) * (x1 - x0), y0 + (la0 - lat) / (la0 - la1) * (y1 - y0))

AUS = [(113.6,-22.0),(114.1,-26.0),(115.0,-30.0),(115.7,-32.0),(115.0,-34.3),(118.0,-35.0),(121.9,-33.9),(124.0,-33.0),(126.0,-32.3),(129.0,-31.6),(131.0,-31.5),(134.0,-32.8),(135.6,-34.8),(136.4,-33.6),(137.6,-32.7),(137.8,-34.0),(137.3,-35.3),(138.0,-35.1),(138.5,-34.8),(138.4,-35.6),(139.4,-35.9),(140.0,-37.5),(141.5,-38.4),(143.5,-38.8),(144.6,-38.1),(146.4,-39.1),(148.0,-37.8),(150.0,-37.5),(150.9,-34.8),(151.2,-33.9),(152.5,-32.2),(153.0,-31.0),(153.6,-28.2),(153.1,-25.0),(150.8,-22.5),(149.0,-20.5),(146.3,-19.0),(145.4,-16.0),(145.3,-14.9),(143.5,-14.0),(142.5,-10.7),(141.6,-12.6),(141.5,-15.8),(140.8,-17.4),(139.3,-17.4),(137.0,-15.9),(135.9,-15.0),(135.9,-13.0),(136.9,-12.2),(134.0,-11.9),(132.6,-11.5),(130.8,-12.4),(129.8,-14.9),(128.1,-15.0),(126.0,-14.0),(124.4,-16.3),(122.2,-17.9),(121.0,-19.6),(118.5,-20.3),(116.7,-20.6),(114.2,-21.8)]
TAS = [(144.6,-40.7),(148.3,-40.9),(148.0,-43.2),(146.8,-43.6),(145.2,-42.2)]
CITY = {'Adelaida': (138.6, -34.93), 'Melbourne': (144.96, -37.81), 'Sídney': (151.21, -33.87), 'Perth': (115.86, -31.95), 'Brisbane': (153.03, -27.47), 'Darwin': (130.84, -12.46)}

def card_map_aus(name, highlight=('Adelaida',), line=None, pins=0, caption=None):
    im = _paper(5); d = ImageDraw.Draw(im)
    box = (520, 120, 2360, 1500); b = (111, -9, 156, -45)
    pts = [_proj(lo, la, box, b) for lo, la in AUS]
    d.polygon(pts, fill=(212, 198, 166), outline=INK); d.line(pts + [pts[0]], fill=INK, width=5)
    tp = [_proj(lo, la, box, b) for lo, la in TAS]; d.polygon(tp, fill=(212, 198, 166), outline=INK); d.line(tp + [tp[0]], fill=INK, width=5)
    r = np.random.default_rng(11)
    for _ in range(pins):
        lo, la = r.uniform(116, 152), r.uniform(-38, -18)
        x, y = _proj(lo, la, box, b); d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=(150, 60, 50))
    if line:
        a, c = line; xa, ya = _proj(*CITY[a], box, b); xc, yc = _proj(*CITY[c], box, b)
        for k in range(0, 100, 4):
            t0, t1 = k / 100, (k + 2) / 100
            d.line((xa + (xc - xa) * t0, ya + (yc - ya) * t0, xa + (xc - xa) * t1, ya + (yc - ya) * t1), fill=(176, 40, 32), width=9)
    for nm, (lo, la) in CITY.items():
        x, y = _proj(lo, la, box, b); hl = nm in highlight
        rr = 22 if hl else 11
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(176, 40, 32) if hl else INK)
        if hl: d.ellipse((x - rr - 16, y - rr - 16, x + rr + 16, y + rr + 16), outline=(176, 40, 32), width=6)
        d.text((x + 40, y - 10), nm.upper(), font=font('typeb', (58 if hl else 40)), fill=INK, anchor='lm')
    d.text((180, 140), "AUSTRALIA", font=font('typeb', 90), fill=INK)
    if caption: d.text((180, 250), caption, font=font('type', 56), fill=(90, 70, 50))
    return save_card(im, name)

COAST = [(138.47, -34.80), (138.485, -34.86), (138.493, -34.917), (138.502, -34.95), (138.509, -34.975), (138.513, -34.988), (138.515, -35.0), (138.52, -35.05), (138.525, -35.08)]
PLACES = {'est': ('ESTACIÓN CENTRAL', (138.596, -34.921)), 'henley': ('HENLEY BEACH', (138.494, -34.917)),
          'glenelg': ('GLENELG', (138.513, -34.981)), 'somerton': ('SOMERTON', (138.517, -34.997))}

def card_map_coast(name, show, notes=None, route=None, caption=None):
    im = _paper(9); d = ImageDraw.Draw(im)
    box = (300, 80, 2580, 1540); b = (138.38, -34.84, 138.66, -35.06)
    pts = [_proj(lo, la, box, b) for lo, la in COAST]
    sea = [(box[0], box[1])] + [(min(p[0], 9999), p[1]) for p in pts] + [(box[0], box[3])]
    sea = [(0, 0)] + pts + [(0, BH_)]
    d.polygon(sea, fill=(176, 186, 182)); d.line(pts, fill=INK, width=7)
    d.text((420, 760), "GOLFO\nSAN VICENTE", font=font('type', 60), fill=(70, 80, 80), anchor='mm', align='center')
    xy = {k: _proj(*PLACES[k][1], box, b) for k in PLACES}
    if route:
        for a, c, col in route:
            (xa, ya), (xc, yc) = xy[a], xy[c]
            n = 40
            for k in range(0, n, 2):
                t0, t1 = k / n, (k + 1) / n
                d.line((xa + (xc - xa) * t0, ya + (yc - ya) * t0, xa + (xc - xa) * t1, ya + (yc - ya) * t1), fill=col, width=10)
    for k in show:
        x, y = xy[k]; nm = PLACES[k][0]
        d.ellipse((x - 24, y - 24, x + 24, y + 24), fill=(176, 40, 32)); d.ellipse((x - 44, y - 44, x + 44, y + 44), outline=(176, 40, 32), width=6)
        d.text((x + 70, y - 12), nm, font=font('typeb', 64), fill=INK, anchor='lm')
        if notes and k in notes: d.text((x + 70, y + 54), notes[k], font=font('type', 46), fill=(120, 50, 40), anchor='lm')
    d.text((2600, 150), "ADELAIDA · 1948", font=font('typeb', 70), fill=INK, anchor='rm')
    if caption: d.text((2600, 240), caption, font=font('type', 50), fill=(90, 70, 50), anchor='rm')
    d.text((2600, 1500), "Mapa esquemático", font=font('type', 40), fill=(110, 95, 75), anchor='rm')
    return save_card(im, name)

CODE = ["WRGOABABD", "MLIAOI", "WTBIMPANETP", "MLIABOAIAQC", "ITTMTSAMSTGAB"]
def code_layers(bgsrc, scrambled=False):
    """base card (paper) + cumulative overlays per line, drawn at 1920x1080 overlay scale"""
    base = Image.open(bgsrc).convert('RGB') if bgsrc else _paper(21)
    base = Image.fromarray((np.asarray(cover(base, BW_, BH_)) * 0.95).astype(np.uint8))
    basep = save_card(base, 'card_code_base')
    outs = []
    r = random.Random(4)
    for k in range(1, len(CODE) + 1):
        im = _ov(); d = ImageDraw.Draw(im)
        for i, line in enumerate(CODE[:k]):
            y = 250 + i * 140; x = 360
            for j, ch in enumerate(line):
                f = font('serifr', 92 + r.randint(-6, 6))
                d.text((x + j * 92 + r.randint(-4, 4), y + r.randint(-6, 6)), ch, font=f, fill=(60, 56, 54, 225))
            if i == 1: d.line((350, y + 50, 360 + len(line) * 92, y + 40), fill=(60, 56, 54, 220), width=6)
        im = im.filter(ImageFilter.GaussianBlur(0.8))
        p = f"{OUT}/ov_code_{k}.png"; im.save(p); outs.append(p)
    return basep, outs

def card_text(name, text, sub=None, bg=(8, 8, 10)):
    im = _canvas(bg); d = ImageDraw.Draw(im)
    f = font('xbold', 96 * S); lines = _wrap(text, f, BW_ * 0.8)
    lh = 120 * S; top = BH_ / 2 - lh * len(lines) / 2 - (40 * S if sub else 0)
    for i, l in enumerate(lines): d.text((BW_ / 2, top + lh * i + lh / 2), l, font=f, fill=(240, 236, 228), anchor='mm')
    if sub: d.text((BW_ / 2, top + lh * len(lines) + 60 * S), sub, font=font('type', 46 * S), fill=(232, 168, 52), anchor='mm')
    return save_card(im, name)

def card_page_hole():
    im = _paper(31); d = ImageDraw.Draw(im)
    # stylised printed page
    x0, x1 = 760, 2120
    d.rectangle((x0 - 40, 120, x1 + 40, 1500), fill=(236, 226, 200)); d.rectangle((x0 - 40, 120, x1 + 40, 1500), outline=(150, 135, 110), width=4)
    r = random.Random(2)
    for i in range(13):
        y = 200 + i * 66
        w_ = r.randint(700, 1300)
        d.rectangle((x0 + 40, y, x0 + 40 + w_, y + 18), fill=(120, 112, 100))
    d.text(((x0 + x1) / 2, 1130), "·  ·  ·", font=font('serif', 70), fill=(110, 100, 90), anchor='mm')
    # the torn hole where TAMAM SHUD was
    hole = [(1150, 1240), (1740, 1232), (1752, 1300), (1730, 1372), (1160, 1380), (1140, 1310)]
    d.polygon(hole, fill=(20, 18, 16))
    return save_card(im, 'card_page_hole')

def ov_scrap():
    """scrap piece (RGBA) positioned to fill the hole: placed at final x,y in overlay coords"""
    im = _ov(); d = ImageDraw.Draw(im)
    s = 1 / S
    hole = [(x * s, y * s) for x, y in [(1150, 1240), (1740, 1232), (1752, 1300), (1730, 1372), (1160, 1380), (1140, 1310)]]
    d.polygon(hole, fill=(238, 228, 204, 255), outline=(150, 135, 110, 255))
    cx = sum(p[0] for p in hole) / len(hole); cy = sum(p[1] for p in hole) / len(hole)
    d.text((cx, cy), "Tamám Shud", font=font('serif', 44), fill=(40, 34, 30, 255), anchor='mm')
    p = f"{OUT}/ov_scrap.png"; im.save(p); return p

def ov_scrap_text(name, text="Tamám Shud", y=540, size=120):
    """printed words on top of the macro scrap photo"""
    im = _ov(); d = ImageDraw.Draw(im)
    f = font('serif', size)
    w_ = f.getlength(text)
    d.rounded_rectangle((960 - w_ / 2 - 60, y - size * 0.75, 960 + w_ / 2 + 60, y + size * 0.75), 6, fill=(232, 222, 196, 235))
    d.text((960, y), text, font=f, fill=(34, 30, 26, 255), anchor='mm')
    im = im.rotate(-3, resample=Image.BICUBIC)
    p = f"{OUT}/ov_{name}.png"; im.save(p); return p

def ov_headline(name, text, sub=None):
    im = _ov(); d = ImageDraw.Draw(im)
    f = font('serif', 120)
    w_ = f.getlength(text)
    d.rectangle((960 - w_ / 2 - 50, 360, 960 + w_ / 2 + 50, 540), fill=(236, 228, 208, 245))
    d.text((960, 450), text, font=f, fill=(20, 18, 16, 255), anchor='mm')
    d.line((960 - w_ / 2, 520, 960 + w_ / 2, 520), fill=(200, 30, 30, 255), width=10)
    if sub: _shadow_text(d, (960, 600), sub, font('type', 40), fill=(232, 168, 52, 255), anchor='mm')
    p = f"{OUT}/ov_{name}.png"; im.save(p); return p

def ov_keane(name="keane", size=150):
    im = _ov(); d = ImageDraw.Draw(im)
    f = font('typeb', size)
    d.rounded_rectangle((640, 420, 1280, 660), 12, fill=(240, 236, 226, 235), outline=(60, 50, 40, 255), width=4)
    d.text((960, 540), "KEANE", font=f, fill=(20, 26, 60, 255), anchor='mm')
    im = im.rotate(4, resample=Image.BICUBIC)
    p = f"{OUT}/ov_{name}.png"; im.save(p); return p

def card_process():
    im = _canvas((10, 18, 24)); d = ImageDraw.Draw(im)
    steps = ["ADN DEL PELO", "PRIMOS LEJANOS\n(bases de datos)", "ÁRBOL\nFAMILIAR", "UN SOLO\nCANDIDATO"]
    n = len(steps); bw, bh = 520, 380; gap = (BW_ - n * bw) / (n + 1)
    for i, s in enumerate(steps):
        x = gap + i * (bw + gap); y = BH_ / 2 - bh / 2
        c = (90, 200, 220) if i < 3 else (232, 168, 52)
        d.rounded_rectangle((x, y, x + bw, y + bh), 26, outline=c, width=8, fill=(16, 30, 38))
        d.text((x + bw / 2, y + 70), f"{i + 1}", font=font('black', 80), fill=c, anchor='mm')
        d.multiline_text((x + bw / 2, y + 230), s, font=font('bold', 56), fill=(236, 240, 242), anchor='mm', align='center', spacing=14)
        if i < n - 1:
            ax = x + bw + 20; d.line((ax, BH_ / 2, ax + gap - 40, BH_ / 2), fill=(200, 210, 214), width=8)
            d.polygon([(ax + gap - 40, BH_ / 2 - 22), (ax + gap - 14, BH_ / 2), (ax + gap - 40, BH_ / 2 + 22)], fill=(200, 210, 214))
    d.text((BW_ / 2, 260), "GENEALOGÍA GENÉTICA", font=font('black', 110), fill=(236, 240, 242), anchor='mm')
    d.text((BW_ / 2, 1320), "Así se identifican hoy restos de hace décadas", font=font('med', 56), fill=(160, 180, 188), anchor='mm')
    return save_card(im, 'card_process')

def card_tree(highlight=False):
    im = _canvas((10, 18, 24)); d = ImageDraw.Draw(im)
    def node(x, y, t, sub, c=(90, 200, 220), fill=(16, 30, 38)):
        d.rounded_rectangle((x - 330, y - 110, x + 330, y + 110), 22, outline=c, width=8, fill=fill)
        d.text((x, y - 28), t, font=font('bold', 66), fill=(236, 240, 242), anchor='mm')
        d.text((x, y + 48), sub, font=font('med', 44), fill=(160, 180, 188), anchor='mm')
    d.text((BW_ / 2, 170), "LA FAMILIA DE CARL WEBB", font=font('black', 100), fill=(236, 240, 242), anchor='mm')
    d.line((BW_ / 2, 330, BW_ / 2, 430), fill=(200, 210, 214), width=6)
    d.text((BW_ / 2, 300), "Padres: Richard y Eliza Webb", font=font('med', 50), fill=(160, 180, 188), anchor='mm')
    d.line((800, 430, 2080, 430), fill=(200, 210, 214), width=6)
    d.line((800, 430, 800, 560), fill=(200, 210, 214), width=6); d.line((2080, 430, 2080, 560), fill=(200, 210, 214), width=6)
    node(800, 670, "CARL WEBB", "n. 1905 · Melbourne")
    node(2080, 670, "FREDA WEBB", "hermana")
    d.line((2080, 780, 2080, 940), fill=(232, 168, 52) if highlight else (200, 210, 214), width=8)
    d.text((2120, 860), "casada con", font=font('med', 46), fill=(160, 180, 188), anchor='lm')
    c = (232, 168, 52) if highlight else (90, 200, 220)
    node(2080, 1060, "THOMAS KEANE", "cuñado de Carl", c=c, fill=(48, 36, 14) if highlight else (16, 30, 38))
    if highlight:
        d.text((800, 1060), "KEANE", font=font('typeb', 150), fill=(232, 168, 52), anchor='mm')
        d.text((800, 1180), "el nombre de la maleta", font=font('type', 54), fill=(232, 168, 52), anchor='mm')
        d.line((1100, 1060, 1730, 1060), fill=(232, 168, 52), width=8)
    return save_card(im, 'card_tree_hl' if highlight else 'card_tree')

def card_headline():
    im = _canvas((240, 240, 238)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, BW_, 150), fill=(18, 18, 20))
    d.text((140, 75), "ÚLTIMA HORA · ADELAIDA, AUSTRALIA", font=font('bold', 56), fill=(240, 240, 238), anchor='lm')
    d.text((140, 330), "26 DE JULIO DE 2022", font=font('bold', 70), fill=(176, 40, 32), anchor='lm')
    d.text((140, 560), "Investigadores ponen nombre", font=font('black', 130), fill=(18, 18, 20), anchor='lm')
    d.text((140, 720), "al Hombre de Somerton", font=font('black', 130), fill=(18, 18, 20), anchor='lm')
    d.rectangle((140, 860, 2740, 866), fill=(18, 18, 20))
    d.text((140, 1040), "CARL «CHARLES» WEBB", font=font('black', 170), fill=(176, 40, 32), anchor='lm')
    d.text((140, 1230), "n. 16 nov. 1905, Footscray (Melbourne) · ingeniero eléctrico y fabricante de instrumentos", font=font('med', 56), fill=(60, 60, 64), anchor='lm')
    d.text((140, 1500), "Recreación tipográfica", font=font('med', 40), fill=(130, 130, 134), anchor='lm')
    return save_card(im, 'card_headline')

def card_columns(fill=False):
    im = _canvas((12, 12, 14)); d = ImageDraw.Draw(im)
    cols = [('VERIFICADO', ["Muerte en Somerton, dic. 1948", "Etiquetas arrancadas", "«Tamám Shud» y el libro", "ADN → Carl Webb (investigadores)", "Familia ligada a «Keane»"]),
            ('DISPUTADO', ["Confirmación oficial", "Causa de la muerte", "Relación con la enfermera"]),
            ('LEYENDA', ["El espía de la Guerra Fría"])]
    cw = BW_ / 3
    for i, (k, items) in enumerate(cols):
        c = COL[k]; x = cw * i + cw / 2
        d.rounded_rectangle((cw * i + 60, 140, cw * (i + 1) - 60, 1480), 24, outline=c, width=8)
        d.text((x, 260), k, font=font('black', 100), fill=c, anchor='mm')
        if fill:
            for j, t in enumerate(items):
                lines = _wrap(t, font('bold', 54), cw - 220)
                yy = 430 + j * 200
                for li, l in enumerate(lines): d.text((cw * i + 120, yy + li * 66), ("• " if li == 0 else "  ") + l, font=font('bold', 54), fill=(236, 232, 224))
    return save_card(im, 'card_cols_full' if fill else 'card_cols')

def card_end(bgsrc):
    im = Image.open(bgsrc).convert('RGB'); im = Image.fromarray((np.asarray(im) * 0.30).astype(np.uint8))
    d = ImageDraw.Draw(im)
    d.text((BW_ / 2, 210), "PRÓXIMO CASO", font=font('typeb', 80), fill=(232, 168, 52), anchor='mm')
    d.text((BW_ / 2, 350), "El hombre que llegó a Irlanda para desaparecer", font=font('xbold', 92), fill=(245, 242, 235), anchor='mm')
    d.rounded_rectangle((300, 520, 1500, 1195), 24, outline=(232, 168, 52), width=8)
    d.text((900, 857), "VIDEO SIGUIENTE", font=font('bold', 70), fill=(200, 196, 188), anchor='mm')
    d.ellipse((1900, 600, 2500, 1200), outline=(245, 242, 235), width=8)
    d.text((2200, 900), "SUSCRÍBETE", font=font('bold', 64), fill=(245, 242, 235), anchor='mm')
    d.text((BW_ / 2, 1420), "Casos reales · evidencia verificada · sin morbo", font=font('type', 52), fill=(200, 196, 188), anchor='mm')
    return save_card(im, 'card_end')

def thumbnail(bgsrc, out):
    im = cover(Image.open(bgsrc).convert('RGB'), 1280, 720)
    im = ImageOps.colorize(im.convert('L'), (6, 6, 8), (236, 238, 240)); im = _vignette(im, 0.7)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 470, 1280, 720), fill=(0, 0, 0))
    d.text((640, 545), "74 AÑOS", font=font('black', 120), fill=(232, 168, 52), anchor='mm')
    d.text((640, 660), "SIN NOMBRE", font=font('black', 120), fill=(250, 248, 242), anchor='mm')
    f = font('serif', 74); t = "Tamám Shud"; w_ = f.getlength(t)
    sc = Image.new('RGBA', (int(w_ + 80), 130), (236, 226, 200, 255)); ImageDraw.Draw(sc).text((40, 65), t, font=f, fill=(30, 26, 22), anchor='lm')
    sc = sc.rotate(-7, expand=True, resample=Image.BICUBIC)
    im.paste(sc, (640 - sc.size[0] // 2, 160), sc)
    im.save(out, quality=94); return out

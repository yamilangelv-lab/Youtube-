"""Procedural stickman animation engine (pycairo)."""
import math, cairo, numpy as np

W, H = 1920, 1080
INK = (0.10, 0.10, 0.11); BG = (0.965, 0.955, 0.925)
RED = (0.88, 0.27, 0.23); YEL = (0.96, 0.72, 0.22); BLUE = (0.20, 0.45, 0.88); GREEN = (0.22, 0.64, 0.36)
PINK = (0.93, 0.45, 0.66); GRAY = (0.55, 0.55, 0.55); LGRAY = (0.86, 0.85, 0.81); MGRAY = (0.72, 0.71, 0.68)
BROWN = (0.55, 0.38, 0.22); WATER = (0.40, 0.62, 0.80); DARK = (0.22, 0.22, 0.24); ORANGE = (0.96, 0.52, 0.18)
WHITE = (1, 1, 1); MONEY = (0.42, 0.72, 0.38); GOLD = (0.95, 0.78, 0.25); PURPLE = (0.55, 0.38, 0.78)
STAMP = {'VERIFICADO': GREEN, 'DISPUTADO': (0.93, 0.62, 0.12), 'LEYENDA': RED}
FONT = "Inter Display"; MONO = "Courier 10 Pitch"

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def eout(x): x = clamp(x); return 1 - (1 - x) ** 3
def back(x):
    x = clamp(x); s = 1.70158
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2
def ap(t, t0, dur=0.35): return back((t - t0) / dur) if t >= t0 else 0.0
def lerp(a, b, x): return a + (b - a) * x

# ---------------- primitives ----------------
def col(c, rgb, a=1.0): c.set_source_rgba(rgb[0], rgb[1], rgb[2], a)
def line(c, pts, w=7, rgb=INK, a=1.0):
    c.set_line_width(w); c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.move_to(*pts[0])
    for p in pts[1:]: c.line_to(*p)
    col(c, rgb, a); c.stroke()
def circle(c, x, y, r, fill=None, stroke=INK, w=6, a=1.0):
    c.new_path(); c.arc(x, y, r, 0, 2 * math.pi)
    if fill is not None: col(c, fill, a); c.fill_preserve() if stroke else c.fill()
    if stroke: c.set_line_width(w); col(c, stroke, a); c.stroke()
def rrect(c, x, y, w, h, r, fill=None, stroke=INK, lw=6, a=1.0):
    r = min(r, w / 2, h / 2); c.new_path()
    c.arc(x + w - r, y + r, r, -math.pi / 2, 0); c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi); c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi); c.close_path()
    if fill is not None: col(c, fill, a); c.fill_preserve() if stroke else c.fill()
    if stroke: c.set_line_width(lw); col(c, stroke, a); c.stroke()
def poly(c, pts, fill=None, stroke=INK, lw=6, a=1.0):
    c.new_path(); c.move_to(*pts[0])
    for p in pts[1:]: c.line_to(*p)
    c.close_path()
    if fill is not None: col(c, fill, a); c.fill_preserve() if stroke else c.fill()
    if stroke: c.set_line_width(lw); c.set_line_join(cairo.LINE_JOIN_ROUND); col(c, stroke, a); c.stroke()

def text(c, s, x, y, size, rgb=INK, align='c', bold=True, font=FONT, a=1.0, valign='m'):
    c.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(size); e = c.text_extents(s)
    dx = {'c': -e.width / 2 - e.x_bearing, 'l': -e.x_bearing, 'r': -e.width - e.x_bearing}[align]
    dy = {'m': -e.height / 2 - e.y_bearing, 'b': 0, 't': -e.y_bearing}[valign]
    c.move_to(x + dx, y + dy); col(c, rgb, a); c.show_text(s)
    return e.width
def text_w(c, s, size, bold=True, font=FONT):
    c.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(size); return c.text_extents(s).width

def pop(c, x, y, k):
    """scale around point; use with save/restore"""
    c.translate(x, y); c.scale(max(k, 0.001), max(k, 0.001)); c.translate(-x, -y)

def label(c, s, x, y, size=54, fg=WHITE, bg=INK, k=1.0, pad=26, rot=0.0):
    if k <= 0: return
    c.save(); pop(c, x, y, k); c.translate(x, y); c.rotate(rot); c.translate(-x, -y)
    w = text_w(c, s, size) + pad * 2; h = size * 1.55
    rrect(c, x - w / 2, y - h / 2, w, h, 16, fill=bg, stroke=None)
    text(c, s, x, y, size, fg); c.restore()

def stamp(c, kind, x, y, k=1.0, size=70, sub=None):
    if k <= 0: return
    rgb = STAMP[kind]
    c.save(); pop(c, x, y, k); c.translate(x, y); c.rotate(-0.09); c.translate(-x, -y)
    w = text_w(c, kind, size) + 80; h = size * 1.7
    rrect(c, x - w / 2, y - h / 2, w, h, 16, fill=None, stroke=rgb, lw=9)
    rrect(c, x - w / 2 + 14, y - h / 2 + 14, w - 28, h - 28, 10, fill=None, stroke=rgb, lw=3)
    text(c, kind, x, y, size, rgb)
    c.restore()
    if sub: label(c, sub, x, y + h / 2 + 50, 40, WHITE, DARK, k)

def bubble(c, s, x, y, k=1.0, size=44, tail=(-60, 80), bg=WHITE, fg=INK, think=False):
    if k <= 0: return
    c.save(); pop(c, x + tail[0], y + tail[1], k)
    lines = s.split('\n'); w = max(text_w(c, l, size) for l in lines) + 70; h = size * 1.35 * len(lines) + 50
    if not think:
        poly(c, [(x - 30, y + h / 2 - 8), (x + tail[0], y + tail[1] + h / 2), (x + 30, y + h / 2 - 8)], fill=bg, stroke=INK, lw=5)
    rrect(c, x - w / 2, y - h / 2, w, h, 34, fill=bg, stroke=INK, lw=5)
    if not think: line(c, [(x - 26, y + h / 2 - 3), (x + 26, y + h / 2 - 3)], 8, bg)
    else:
        for i, (dx, dy, r) in enumerate([(0.45, 0.35, 14), (0.75, 0.75, 9)]):
            circle(c, x + tail[0] * dx, y + h / 2 + tail[1] * dy * 0.7, r, fill=bg, w=4)
    for i, l in enumerate(lines):
        text(c, l, x, y - h / 2 + 25 + size * 0.68 + i * size * 1.35, size, fg)
    c.restore()

def arrow(c, x1, y1, x2, y2, rgb=INK, w=8, k=1.0, head=26):
    if k <= 0: return
    x2 = lerp(x1, x2, k); y2 = lerp(y1, y2, k)
    line(c, [(x1, y1), (x2, y2)], w, rgb)
    a = math.atan2(y2 - y1, x2 - x1)
    poly(c, [(x2 + math.cos(a) * 6, y2 + math.sin(a) * 6), (x2 - math.cos(a - 0.5) * head, y2 - math.sin(a - 0.5) * head),
             (x2 - math.cos(a + 0.5) * head, y2 - math.sin(a + 0.5) * head)], fill=rgb, stroke=None)

def dashed(c, pts, w=6, rgb=INK, dash=(18, 14), off=0):
    c.set_dash(dash, off); line(c, pts, w, rgb); c.set_dash([])

def ground(c, y=860, x0=-50, x1=W + 50):
    line(c, [(x0, y), (x1, y)], 6, INK)

# ---------------- stickman ----------------
L = dict(head=31, neck=10, torso=96, ua=52, fa=48, th=60, sh=58)
BASE = dict(lean=0.0, tilt=0.0, ua_b=-0.2, fa_b=-0.1, ua_f=0.2, fa_f=0.1, th_b=-0.11, kn_b=0.0, th_f=0.11, kn_f=0.0, by=0.0)

def pose(name, t=0.0, **kw):
    p = dict(BASE); s = math.sin
    if name == 'stand':
        p['by'] = 1.5 * s(2 * math.pi * 0.5 * t); p['ua_f'] += 0.03 * s(3 * t); p['ua_b'] -= 0.03 * s(3 * t)
    elif name in ('walk', 'run'):
        run = name == 'run'; sp = kw.get('sp', 2.6 if run else 1.7); amp = 0.75 if run else 0.45
        ph = 2 * math.pi * sp * t
        p['th_f'] = amp * s(ph); p['th_b'] = -amp * s(ph)
        p['kn_f'] = -(1.3 if run else 0.7) * max(0, s(ph + 1.9)); p['kn_b'] = -(1.3 if run else 0.7) * max(0, s(ph + 1.9 + math.pi))
        p['ua_f'] = -0.5 * amp / 0.45 * s(ph) * 0.8; p['ua_b'] = 0.5 * amp / 0.45 * s(ph) * 0.8
        p['fa_f'] = 1.4 if run else 0.35; p['fa_b'] = 1.4 if run else 0.35
        p['lean'] = 0.22 if run else 0.04; p['by'] = -(6 if run else 3) * abs(math.cos(ph))
    elif name == 'talk':
        p['ua_f'] = 0.9 + 0.25 * s(4.1 * t); p['fa_f'] = -0.8 + 0.35 * s(5.3 * t); p['tilt'] = 0.06 * s(2.2 * t); p['by'] = 1.5 * s(3 * t)
        p['ua_b'] = -0.25 - 0.1 * s(3.1 * t)
    elif name == 'point':
        p['ua_f'] = 1.55 + 0.03 * s(3 * t); p['fa_f'] = 0.0; p['lean'] = 0.03
    elif name == 'pointup':
        p['ua_f'] = 2.6; p['fa_f'] = 0.2
    elif name == 'handsup':
        sh = 0.06 * s(14 * t) * kw.get('shake', 1)
        p['ua_b'] = -2.65 + sh; p['fa_b'] = -0.25; p['ua_f'] = 2.65 - sh; p['fa_f'] = 0.25
    elif name == 'think':
        p['ua_f'] = 0.45; p['fa_f'] = -3.25; p['tilt'] = -0.12; p['ua_b'] = -0.35; p['fa_b'] = 1.1; p['by'] = 1 * s(2 * t)
    elif name == 'shrug':
        k = 0.5 + 0.5 * s(3 * t)
        p['ua_b'] = -0.65; p['fa_b'] = -1.5 - 0.2 * k; p['ua_f'] = 0.65; p['fa_f'] = 1.5 + 0.2 * k; p['tilt'] = 0.15
    elif name == 'phone':
        p['ua_f'] = 0.35; p['fa_f'] = -3.3; p['ua_b'] = -0.2; p['tilt'] = 0.05 * s(2 * t)
    elif name == 'phone_talk':
        p['ua_f'] = 0.35; p['fa_f'] = -3.3; p['ua_b'] = 0.9 + 0.25 * s(4 * t); p['fa_b'] = -0.9 + 0.3 * s(5 * t); p['tilt'] = 0.05 * s(2 * t)
    elif name == 'sit':
        p['th_b'] = 1.45; p['th_f'] = 1.5; p['kn_b'] = -1.45; p['kn_f'] = -1.5; p['by'] = 1 * s(2 * t)
    elif name == 'cower':
        p['th_b'] = 1.5; p['th_f'] = 1.55; p['kn_b'] = -2.6; p['kn_f'] = -2.6; p['lean'] = 0.15
        p['ua_b'] = -2.3 + 0.05 * s(12 * t); p['fa_b'] = 2.0; p['ua_f'] = 2.3 - 0.05 * s(12 * t); p['fa_f'] = -2.0
    elif name == 'celebrate':
        w = 0.2 * s(8 * t); p['ua_b'] = -2.5 + w; p['ua_f'] = 2.5 - w; p['fa_b'] = -0.3; p['fa_f'] = 0.3; p['by'] = -14 * abs(s(5 * t))
    elif name == 'sad':
        p['lean'] = 0.1; p['tilt'] = 0.35; p['ua_b'] = -0.05; p['ua_f'] = 0.05; p['by'] = 1 * s(1.5 * t)
    elif name == 'hips':
        p['ua_b'] = -0.75; p['fa_b'] = 1.75; p['ua_f'] = 0.75; p['fa_f'] = -1.75; p['tilt'] = 0.08 * s(2 * t)
    elif name == 'dig':
        k = s(3.5 * t); p['lean'] = 0.35; p['ua_f'] = 1.0 + 0.45 * k; p['fa_f'] = 0.5; p['ua_b'] = 0.75 + 0.45 * k; p['fa_b'] = 0.7
        p['th_f'] = 0.35; p['kn_f'] = -0.4; p['th_b'] = -0.25
    elif name == 'paddle':
        k = s(3 * t); p.update(pose('sit', t)); p['ua_f'] = 1.2 + 0.5 * k; p['fa_f'] = 0.3; p['ua_b'] = 1.0 + 0.5 * k; p['fa_b'] = 0.4; p['lean'] = 0.15 + 0.1 * k
    elif name == 'carry':
        p.update(pose('walk', t)) if kw.get('walking') else None
        p['ua_f'] = 0.08; p['fa_f'] = 0.0
    elif name == 'laugh':
        p['lean'] = -0.08 + 0.05 * s(10 * t); p['ua_f'] = 0.5; p['fa_f'] = -2.0; p['ua_b'] = -0.5; p['fa_b'] = 2.0; p['by'] = -3 * abs(s(10 * t))
    elif name == 'worried':
        p['ua_b'] = -0.5; p['fa_b'] = -2.4; p['ua_f'] = 0.5; p['fa_f'] = 2.4; p['tilt'] = 0.05 * s(6 * t)
    elif name == 'typing':
        p.update(pose('sit', t)); p['ua_f'] = 0.9; p['fa_f'] = 0.6 + 0.1 * s(20 * t); p['ua_b'] = 0.8; p['fa_b'] = 0.7 + 0.1 * s(17 * t)
    elif name == 'cuffed':
        p['ua_b'] = 0.35; p['fa_b'] = 0.0; p['ua_f'] = -0.35; p['fa_f'] = 0.0; p['lean'] = 0.05; p['tilt'] = 0.25
    for k_, v in kw.items():
        if k_ in p: p[k_] = v
    return p

def _seg(o, a, l, d): return (o[0] + math.sin(a) * l * d, o[1] + math.cos(a) * l)

def stick(c, x, gy, s=1.0, p=None, face='n', d=1, acc=(), shirt=None, t=0.0, lw=7.5, hold=None, alpha=1.0, blink=True):
    p = p or pose('stand', t)
    c.save(); c.translate(x, gy); c.scale(s, s)
    hip = (0.0, 0.0)
    kb = _seg(hip, p['th_b'], L['th'], d); fb = _seg(kb, p['th_b'] + p['kn_b'], L['sh'], d)
    kf = _seg(hip, p['th_f'], L['th'], d); ff = _seg(kf, p['th_f'] + p['kn_f'], L['sh'], d)
    oy = -max(fb[1], ff[1]) + p['by']
    def T(pt): return (pt[0], pt[1] + oy)
    hip, kb, fb, kf, ff = map(T, (hip, kb, fb, kf, ff))
    sh = (hip[0] + math.sin(p['lean']) * L['torso'] * d, hip[1] - math.cos(p['lean']) * L['torso'])
    hc = (sh[0] + math.sin(p['lean'] + p['tilt']) * (L['neck'] + L['head']) * d, sh[1] - math.cos(p['lean'] + p['tilt']) * (L['neck'] + L['head']))
    eb = _seg(sh, p['ua_b'], L['ua'], d); hb = _seg(eb, p['ua_b'] + p['fa_b'], L['fa'], d)
    ef = _seg(sh, p['ua_f'], L['ua'], d); hf = _seg(ef, p['ua_f'] + p['fa_f'], L['fa'], d)
    A = alpha
    if 'hair_long' in acc:
        c.new_path(); col(c, (0.25, 0.18, 0.12), A)
        c.move_to(hc[0] - 34 * d, hc[1] - 4); c.curve_to(hc[0] - 46 * d, hc[1] + 40, hc[0] - 36 * d, hc[1] + 70, hc[0] - 14 * d, hc[1] + 74)
        c.line_to(hc[0] + 10 * d, hc[1] + 20); c.close_path(); c.fill()
    # back limbs
    line(c, [hip, kb, fb], lw, INK, A); line(c, [sh, eb, hb], lw, INK, A)
    if 'dress' in acc:
        dc = acc_color(acc, 'dress', RED)
        poly(c, [(sh[0] - 8 * d, sh[1] + 10), (sh[0] + 8 * d, sh[1] + 10), (hip[0] + 40, hip[1] + 18), (hip[0] - 40, hip[1] + 18)], fill=dc, stroke=INK, lw=5, a=A)
    elif shirt:
        line(c, [sh, hip], 22, shirt, A)
    line(c, [hip, sh], lw, INK, A)
    if 'tie' in acc: line(c, [(sh[0], sh[1] + 6), (sh[0] + 3 * d, sh[1] + 40)], 9, acc_color(acc, 'tie', RED), A)
    # head
    circle(c, hc[0], hc[1], L['head'], fill=BG, stroke=INK, w=lw, a=A)
    _face(c, hc, d, face, t, blink, A, 'mask' in acc)
    _hats(c, hc, d, acc, A)
    # front limbs
    line(c, [hip, kf, ff], lw, INK, A); line(c, [sh, ef, hf], lw, INK, A)
    if hold: _hold(c, hf, d, hold, t, A)
    c.restore()
    def W_(pt): return (x + pt[0] * s, gy + pt[1] * s)
    return dict(head=W_(hc), hand_f=W_(hf), hand_b=W_(hb), hip=W_(hip), sh=W_(sh))

def acc_color(acc, key, default):
    for a in acc:
        if isinstance(a, tuple) and a[0] == key: return a[1]
    return default

def _face(c, hc, d, face, t, blink, A, mask):
    ex = hc[0] + 9 * d; ey = hc[1] - 5
    if mask:
        rrect(c, hc[0] - 31, ey - 11, 62, 20, 6, fill=INK, stroke=None, a=A)
        circle(c, ex - 9, ey - 1, 4, fill=WHITE, stroke=None, a=A); circle(c, ex + 9, ey - 1, 4, fill=WHITE, stroke=None, a=A)
    else:
        closed = blink and (t % 3.7) < 0.12
        for dx in (-9, 9):
            if closed or face == 'happy_eyes': line(c, [(ex + dx - 4, ey), (ex + dx + 4, ey)], 3.5, INK, A)
            else: circle(c, ex + dx, ey, 3.8, fill=INK, stroke=None, a=A)
    mx, my = hc[0] + 8 * d, hc[1] + 12
    if face in ('h', 'happy_eyes'):
        c.new_path(); c.arc(mx, my - 6, 10, 0.3, math.pi - 0.3); c.set_line_width(3.5); col(c, INK, A); c.stroke()
    elif face == 'o': circle(c, mx, my, 6, fill=INK, stroke=None, a=A)
    elif face == 's':
        c.new_path(); c.arc(mx, my + 8, 9, math.pi + 0.4, 2 * math.pi - 0.4); c.set_line_width(3.5); col(c, INK, A); c.stroke()
    elif face == 'w': line(c, [(mx - 9, my), (mx - 4, my - 3), (mx + 1, my), (mx + 6, my - 3), (mx + 10, my)], 3, INK, A)
    elif face == 'grin':
        c.new_path(); c.arc(mx, my - 4, 11, 0.15, math.pi - 0.15); c.close_path(); col(c, INK, A); c.fill()
    elif face == 'angry':
        line(c, [(ex - 15, ey - 12), (ex - 4, ey - 7)], 3.5, INK, A); line(c, [(ex + 15, ey - 12), (ex + 4, ey - 7)], 3.5, INK, A)
        line(c, [(mx - 8, my + 2), (mx + 8, my + 2)], 3.5, INK, A)
    else: line(c, [(mx - 7, my), (mx + 7, my)], 3.5, INK, A)

def _hats(c, hc, d, acc, A):
    x, y = hc
    if 'cap_police' in acc:
        poly(c, [(x - 30, y - 18), (x - 26, y - 44), (x + 26, y - 44), (x + 30, y - 18)], fill=BLUE, stroke=INK, lw=5, a=A)
        line(c, [(x - 30, y - 18), (x + 44 * d if d > 0 else x + 30, y - 18)], 6, INK, A)
        circle(c, x, y - 32, 5, fill=YEL, stroke=None, a=A)
    if 'cap' in acc:
        cc = acc_color(acc, 'cap', RED)
        c.new_path(); c.arc(x, y - 10, 31, math.pi, 2 * math.pi); c.close_path(); col(c, cc, A); c.fill_preserve(); c.set_line_width(5); col(c, INK, A); c.stroke()
        line(c, [(x, y - 10), (x + 48 * d, y - 10)], 6, INK, A)
    if 'hat' in acc:
        hc_ = acc_color(acc, 'hat', DARK)
        rrect(c, x - 22, y - 62, 44, 34, 6, fill=hc_, stroke=INK, lw=5, a=A); line(c, [(x - 44, y - 28), (x + 44, y - 28)], 7, INK, A)
    if 'party' in acc:
        poly(c, [(x - 18, y - 26), (x + 18, y - 26), (x + 2, y - 78)], fill=PINK, stroke=INK, lw=4, a=A); circle(c, x + 2, y - 80, 7, fill=YEL, stroke=None, a=A)
    if 'glasses' in acc:
        circle(c, x + 0 * d, y - 5, 10, stroke=INK, w=3, a=A); circle(c, x + 20 * d, y - 5, 10, stroke=INK, w=3, a=A)
    if 'hair_long' in acc:
        c.new_path(); c.arc(x, y - 4, 33, math.pi * 1.05, math.pi * 1.95); col(c, (0.25, 0.18, 0.12), A); c.set_line_width(12); c.stroke()
    if 'bun' in acc: circle(c, x - 22 * d, y - 26, 13, fill=(0.25, 0.18, 0.12), stroke=None, a=A)
    if 'beanie' in acc:
        c.new_path(); c.arc(x, y - 6, 32, math.pi, 2 * math.pi); c.close_path(); col(c, DARK, A); c.fill()

def _hold(c, h, d, what, t, A):
    x, y = h
    if what == 'bag': money_bag(c, x + 4 * d, y + 40, 0.75)
    elif what == 'phone': rrect(c, x - 9, y - 26, 18, 40, 4, fill=DARK, stroke=None, a=A)
    elif what == 'gun': toy_gun(c, x, y, 0.8, d)
    elif what == 'shovel':
        line(c, [(x - 40 * d, y - 40), (x + 50 * d, y + 70)], 6, BROWN, A); poly(c, [(x + 40 * d, y + 60), (x + 70 * d, y + 70), (x + 58 * d, y + 100), (x + 34 * d, y + 86)], fill=GRAY, stroke=INK, lw=4, a=A)
    elif what == 'pizza': pizza_box(c, x, y - 4, 0.7)
    elif what == 'paper': rrect(c, x - 16, y - 40, 34, 44, 3, fill=WHITE, stroke=INK, lw=3, a=A)
    elif what == 'gavel':
        line(c, [(x, y), (x + 20 * d, y - 50)], 6, BROWN, A); rrect(c, x + 20 * d - 26, y - 68, 52, 26, 6, fill=BROWN, stroke=INK, lw=4, a=A)
    elif what == 'magnifier':
        line(c, [(x, y), (x + 26 * d, y - 26)], 8, INK, A); circle(c, x + 44 * d, y - 44, 24, fill=(0.85, 0.92, 1.0), stroke=INK, w=6, a=A)

# ---------------- props ----------------
def money_bag(c, x, y, s=1.0, label_='$'):
    c.save(); c.translate(x, y); c.scale(s, s)
    c.new_path(); c.move_to(-20, -50); c.curve_to(-70, -10, -60, 50, 0, 50); c.curve_to(60, 50, 70, -10, 20, -50); c.close_path()
    col(c, (0.82, 0.70, 0.48)); c.fill_preserve(); c.set_line_width(5); col(c, INK); c.stroke()
    line(c, [(-24, -52), (24, -52)], 8, INK); poly(c, [(-14, -54), (0, -76), (14, -54)], fill=(0.82, 0.70, 0.48), stroke=INK, lw=4)
    text(c, label_, 0, 8, 46, (0.30, 0.50, 0.22)); c.restore()

def cash(c, x, y, s=1.0, n=3):
    c.save(); c.translate(x, y); c.scale(s, s)
    for i in range(n):
        rrect(c, -60, -18 - i * 12, 120, 34, 4, fill=MONEY, stroke=INK, lw=4); circle(c, 0, -1 - i * 12, 9, fill=(0.75, 0.88, 0.70), stroke=INK, w=3)
    c.restore()

def gem(c, x, y, s=1.0, rgb=(0.45, 0.80, 0.95)):
    c.save(); c.translate(x, y); c.scale(s, s)
    poly(c, [(-22, -10), (-12, -24), (12, -24), (22, -10), (0, 22)], fill=rgb, stroke=INK, lw=4)
    line(c, [(-22, -10), (22, -10)], 3, INK); c.restore()

def toy_gun(c, x, y, s=1.0, d=1):
    c.save(); c.translate(x, y); c.scale(s * d, s)
    rrect(c, -10, -18, 80, 26, 6, fill=GRAY, stroke=INK, lw=4); rrect(c, -8, 0, 24, 42, 6, fill=DARK, stroke=INK, lw=4)
    rrect(c, 66, -18, 14, 26, 3, fill=ORANGE, stroke=INK, lw=3); c.restore()

def pizza_box(c, x, y, s=1.0, open_=False):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -70, -14, 140, 28, 4, fill=(0.88, 0.72, 0.48), stroke=INK, lw=4)
    text(c, "PIZZA", 0, 0, 22, RED); c.restore()

def bank(c, x, gy, w=760, h=470, sign="BANCO", sub="Sucursal Acassuso", door_open=0.0, k=1.0):
    c.save(); pop(c, x, gy, k)
    x0 = x - w / 2; top = gy - h
    poly(c, [(x0 - 30, top + 70), (x, top - 30), (x0 + w + 30, top + 70)], fill=LGRAY, stroke=INK, lw=6)
    rrect(c, x0, top + 70, w, h - 70, 4, fill=(0.93, 0.92, 0.88), stroke=INK, lw=6)
    rrect(c, x - 200, top + 92, 400, 70, 10, fill=INK, stroke=None); text(c, sign, x, top + 127, 48 if len(sign) <= 8 else 36, WHITE)
    text(c, sub, x, top + 192, 26, DARK, bold=False)
    for i in range(6):
        cx = x0 + 60 + i * (w - 120) / 5
        if abs(cx - x) < 90: continue
        line(c, [(cx, top + 230), (cx, gy - 10)], 18, MGRAY); line(c, [(cx - 22, top + 230), (cx + 22, top + 230)], 6, INK)
    dh = min(190, (h - 210) * 0.95)
    rrect(c, x - 70, gy - dh, 140, dh, 6, fill=DARK, stroke=INK, lw=6)
    if door_open > 0: rrect(c, x - 70, gy - dh, 140 * (1 - door_open), dh, 6, fill=(0.45, 0.33, 0.22), stroke=INK, lw=5)
    else: line(c, [(x, gy - dh), (x, gy)], 4, (0.35, 0.35, 0.35))
    line(c, [(x0 - 40, gy), (x0 + w + 40, gy)], 6, INK)
    c.restore()

def police_car(c, x, gy, t, d=1, s=1.0):
    c.save(); c.translate(x, gy); c.scale(s * d, s)
    rrect(c, -150, -88, 300, 60, 18, fill=WHITE, stroke=INK, lw=5)
    poly(c, [(-80, -88), (-55, -130), (60, -130), (90, -88)], fill=(0.80, 0.88, 0.96), stroke=INK, lw=5)
    rrect(c, -150, -66, 300, 18, 2, fill=BLUE, stroke=None)
    on = int(t * 6) % 2
    rrect(c, -30, -146, 30, 16, 4, fill=RED if on else (0.5, 0.2, 0.2), stroke=INK, lw=3); rrect(c, 0, -146, 30, 16, 4, fill=(0.2, 0.3, 0.6) if on else BLUE, stroke=INK, lw=3)
    for wx in (-90, 90): circle(c, wx, -26, 26, fill=DARK, stroke=INK, w=5); circle(c, wx, -26, 9, fill=GRAY, stroke=None)
    c.restore()

def tv(c, x, y, w, h, live=True, k=1.0):
    c.save(); pop(c, x, y, k)
    rrect(c, x - w / 2 - 24, y - h / 2 - 24, w + 48, h + 48, 22, fill=DARK, stroke=INK, lw=6)
    line(c, [(x - 60, y + h / 2 + 24), (x - 100, y + h / 2 + 80)], 8, INK); line(c, [(x + 60, y + h / 2 + 24), (x + 100, y + h / 2 + 80)], 8, INK)
    c.restore()

def tv_badge(c, x, y, t):
    if int(t * 2) % 2 == 0: circle(c, x, y, 10, fill=RED, stroke=None)
    rrect(c, x + 18, y - 22, 150, 44, 8, fill=RED, stroke=None); text(c, "EN VIVO", x + 93, y, 26, WHITE)

def note(c, x, y, k=1.0, rot=-0.05, lines=None, size=40):
    if k <= 0: return
    lines = lines or ["En barrio de ricachones,", "sin armas ni rencores.", "Es solo plata, no amores."]
    c.save(); pop(c, x, y, k); c.translate(x, y); c.rotate(rot); c.translate(-x, -y)
    w = max(text_w(c, l, size, False, MONO) for l in lines) + 90; h = len(lines) * size * 1.5 + 80
    rrect(c, x - w / 2, y - h / 2, w, h, 6, fill=(1.0, 0.99, 0.93), stroke=INK, lw=4)
    for i in range(len(lines) + 1): line(c, [(x - w / 2 + 20, y - h / 2 + 40 + i * size * 1.5 + 14), (x + w / 2 - 20, y - h / 2 + 40 + i * size * 1.5 + 14)], 1.5, (0.6, 0.75, 0.9))
    for i, l in enumerate(lines): text(c, l, x - w / 2 + 45, y - h / 2 + 40 + i * size * 1.5, size, (0.15, 0.2, 0.45), align='l', bold=False, font=MONO)
    c.restore()

def hole_wall(c, x, y, r=90, k=1.0):
    if k <= 0: return
    c.save(); pop(c, x, y, k)
    for row in range(-3, 4):
        for col_ in range(-4, 4):
            bx = x + col_ * 64 + (32 if row % 2 else 0); by_ = y + row * 34
            rrect(c, bx - 30, by_ - 15, 60, 30, 3, fill=(0.80, 0.50, 0.40), stroke=INK, lw=3)
    pts = []
    for i in range(14):
        a = i / 14 * 2 * math.pi; rr = r * (0.8 + 0.25 * math.sin(i * 2.7))
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr * 0.8))
    poly(c, pts, fill=(0.08, 0.08, 0.09), stroke=INK, lw=5); c.restore()

def boat(c, x, y, s=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    rrect(c, -150, -40, 300, 64, 32, fill=ORANGE, stroke=INK, lw=6); line(c, [(-120, -10), (120, -10)], 4, (0.8, 0.35, 0.1)); c.restore()

def tower(c, x, gy, h=380, t=0.0, waves=True, k=1.0):
    c.save(); pop(c, x, gy, k)
    top = gy - h
    line(c, [(x - 70, gy), (x, top)], 7, INK); line(c, [(x + 70, gy), (x, top)], 7, INK)
    for i in range(1, 6):
        yy = gy - h * i / 6; ww = 70 * (1 - i / 6)
        line(c, [(x - ww, yy), (x + ww * 0.8, yy - h / 12)], 3, INK); line(c, [(x + ww, yy), (x - ww * 0.8, yy - h / 12)], 3, INK)
    circle(c, x, top, 14, fill=RED, stroke=INK, w=4)
    if waves:
        for i in range(3):
            ph = (t * 0.9 + i / 3) % 1
            for sgn in (-1, 1):
                c.new_path(); c.arc(x, top, 40 + ph * 160, (-0.5 if sgn > 0 else math.pi - 0.5) - 0.0, (0.5 if sgn > 0 else math.pi + 0.5))
                c.set_line_width(5); col(c, BLUE, 1 - ph); c.stroke()
    c.restore()

def phone_icon(c, x, y, s=1.0, rgb=DARK, glow=0.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    if glow > 0: circle(c, 0, 0, 48, fill=YEL, stroke=None, a=glow * 0.6)
    rrect(c, -18, -32, 36, 64, 7, fill=rgb, stroke=INK, lw=4); rrect(c, -12, -24, 24, 40, 3, fill=(0.75, 0.88, 1.0), stroke=None); c.restore()

def clock(c, x, y, r, hours, k=1.0):
    c.save(); pop(c, x, y, k)
    circle(c, x, y, r, fill=WHITE, stroke=INK, w=8)
    for i in range(12):
        a = i / 12 * 2 * math.pi; line(c, [(x + math.sin(a) * r * 0.82, y - math.cos(a) * r * 0.82), (x + math.sin(a) * r * 0.92, y - math.cos(a) * r * 0.92)], 5, INK)
    ah = hours / 12 * 2 * math.pi; am = hours * 2 * math.pi
    line(c, [(x, y), (x + math.sin(ah) * r * 0.5, y - math.cos(ah) * r * 0.5)], 10, INK)
    line(c, [(x, y), (x + math.sin(am) * r * 0.75, y - math.cos(am) * r * 0.75)], 6, RED)
    circle(c, x, y, 10, fill=INK, stroke=None); c.restore()

def bars(c, x0, y0, w, h, k=1.0):
    for i in range(int(w / 70) + 1):
        xx = x0 + i * 70; line(c, [(xx, y0), (xx, y0 + h * k)], 12, DARK)
    line(c, [(x0 - 10, y0), (x0 + w + 10, y0)], 14, DARK)

def question(c, x, y, size=260, k=1.0, rgb=RED):
    if k <= 0: return
    c.save(); pop(c, x, y, k); text(c, "?", x, y, size, rgb); c.restore()

def heart(c, x, y, s=1.0, broken=0.0, rgb=RED):
    c.save(); c.translate(x, y); c.scale(s, s)
    for side in (-1, 1):
        c.save(); c.translate(side * broken * 30, broken * 10); c.rotate(side * broken * 0.25)
        c.new_path(); c.move_to(0, 60)
        if side < 0: c.curve_to(-90, 0, -60, -70, 0, -30)
        else: c.curve_to(90, 0, 60, -70, 0, -30)
        c.line_to(10 * side if broken else 0, 0); c.line_to(-8 * side if broken else 0, 25); c.close_path()
        col(c, rgb); c.fill_preserve(); c.set_line_width(5); col(c, INK); c.stroke(); c.restore()
    c.restore()

def calendar(c, x, y, k=1.0, day="13", month="ENERO", year="2006"):
    if k <= 0: return
    c.save(); pop(c, x, y, k)
    rrect(c, x - 120, y - 130, 240, 260, 14, fill=WHITE, stroke=INK, lw=6); rrect(c, x - 120, y - 130, 240, 70, 14, fill=RED, stroke=INK, lw=6)
    text(c, month, x, y - 95, 34, WHITE); text(c, day, x, y + 10, 110, INK); text(c, year, x, y + 92, 32, DARK, bold=False)
    c.restore()

def paper_bg(seed=1):
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 1, (H // 8 + 2, W // 8 + 2)).astype(np.float32)
    from PIL import Image
    big = np.asarray(Image.fromarray(((n - n.min()) / (n.max() - n.min()) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)).astype(np.float32) / 255
    base = np.array(BG[::-1], np.float32) * 255  # BGR
    img = base[None, None, :] * (0.975 + 0.035 * big[..., None]) + rng.normal(0, 2.0, (H, W, 1))
    out = np.zeros((H, W, 4), np.uint8); out[..., :3] = np.clip(img, 0, 255); out[..., 3] = 255
    return out

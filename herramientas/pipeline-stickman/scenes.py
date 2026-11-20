"""Scene library for 'El robo del siglo' (stickman)."""
import math
from engine import *

GY = 880
NARR = dict(acc=(('hat', BROWN), 'hat'), shirt=YEL)          # narrator/detective mascot
VIT = dict(shirt=PINK)                                       # Vitette
BETO = dict(shirt=GREEN, acc=('beanie',))
ARAUJO = dict(shirt=YEL, acc=('glasses',))
COP = dict(shirt=BLUE, acc=('cap_police',))
SILEO = dict(shirt=BLUE, acc=('cap_police', 'tie'))
ALICIA = dict(acc=('hair_long', ('dress', PURPLE), 'dress'))
ROB = dict(acc=('mask',), shirt=DARK)
HOST = [dict(shirt=RED), dict(shirt=BLUE), dict(acc=('hair_long', ('dress', GREEN), 'dress')), dict(shirt=ORANGE),
        dict(acc=('hair_long', ('dress', YEL), 'dress', 'bun')), dict(shirt=PURPLE), dict(shirt=GRAY)]

def S(c, x, t, name='stand', d=1, face='n', s=1.3, gy=GY, hold=None, ch=None, **pk):
    ch = ch or {}
    return stick(c, x, gy, s, pose(name, t, **pk), face, d, ch.get('acc', ()), ch.get('shirt'), t, hold=hold)

def caption(c, s, t, t0=0.15, y=150, size=64, bg=INK, fg=WHITE):
    label(c, s, W / 2, y, size, fg, bg, ap(t, t0))

# ---------------- scenes ----------------
def bank_police(c, t, d, p):
    ground(c)
    bank(c, 960, GY, k=ap(t, 0))
    for i, x in enumerate([260, 1660]):
        police_car(c, x, GY, t + i * 0.3, 1 if i == 0 else -1, 0.9)
    for i, x in enumerate([430, 560, 1360, 1490]):
        S(c, x, t + i, 'point' if i % 2 == 0 else 'stand', d=1 if x < 960 else -1, ch=COP, s=0.85, face='angry')
    if p.get('siren'):
        for i in range(3):
            ph = (t * 1.2 + i / 3) % 1
            circle(c, 960, 380, 60 + ph * 500, stroke=RED, w=6, a=(1 - ph) * 0.5)
    else:
        calendar(c, 1700, 250, ap(t, 0.4), "13", "ENERO", "2006")
    label(c, "ACASSUSO · BUENOS AIRES", 420, 150, 46, WHITE, INK, ap(t, 0.2))

def _room(c):
    rrect(c, 120, 140, 1680, 740, 10, fill=(0.94, 0.93, 0.89), stroke=INK, lw=6)
    line(c, [(120, GY), (1800, GY)], 6, INK)

def hostages(c, t, d, p):
    _room(c)
    n = p.get('n', 7); shown = min(n, 9)
    for i in range(shown):
        x = 300 + i * 150
        stick(c, x, GY, 0.8, pose('cower', t + i * 0.37), 's' if i % 2 else 'w', 1 if i % 2 else -1, HOST[i % 7].get('acc', ()), HOST[i % 7].get('shirt'), t + i)
    S(c, 1640, t, 'stand', d=-1, ch=ROB, hold='gun', face='angry', ua_f=1.3, fa_f=0.2)
    if p.get('label'):
        caption(c, p['label'], t, 0.6, 230, 90, RED)

def phone_talk(c, t, d, p):
    mode = p.get('mode')
    line(c, [(960, 120), (960, 960)], 5, MGRAY)
    S(c, 480, t, 'phone_talk', d=1, ch=SILEO if mode == 'names' else COP, hold='phone')
    S(c, 1440, t, 'phone_talk', d=-1, ch=VIT, hold='phone', face='h' if mode == 'calm' else 'n')
    if mode == 'names':
        label(c, "MIGUEL SILEO · negociador", 480, 960, 40, WHITE, BLUE, ap(t, 0.3))
        label(c, "LUIS MARIO VITETTE SELLANES", 1440, 960, 40, WHITE, PINK, ap(t, 1.6))
    elif mode == 'calm':
        bubble(c, "Tranquilo...\nhablemos.", 1500, 340, ap(t, 0.5), 46, tail=(-40, 90))
        clock(c, 960, 260, 90, t / d * 3, ap(t, 1.0))
        label(c, "+ TIEMPO", 960, 420, 44, WHITE, GREEN, ap(t, d * 0.6))
    else:
        items = ["TIEMPO", "COMIDA", "PIZZAS"]
        for i, s_ in enumerate(items):
            t0 = d * (0.2 + 0.22 * i)
            label(c, s_, 1440, 230 + i * 0, 54, WHITE, [GRAY, ORANGE, RED][i], ap(t, t0) * (1 if t < t0 + d * 0.22 or i == 2 else 0))
        if t > d * 0.66: pizza_box(c, 1180, 300, 1.2 * ap(t, d * 0.66))

def tv_live(c, t, d, p):
    tv(c, 960, 470, 1100, 600, k=ap(t, 0))
    c.save(); c.rectangle(960 - 550, 470 - 300, 1100, 600); c.clip()
    col(c, (0.85, 0.90, 0.96)); c.paint()
    c.translate(0, 0); bank(c, 960, 760, 560, 340, k=1.0)
    police_car(c, 600, 760, t, 1, 0.6); police_car(c, 1320, 760, t + 0.2, -1, 0.6)
    tv_badge(c, 450, 220, t)
    if p.get('headline'):
        rrect(c, 410, 650, 1100, 110, 0, fill=RED, stroke=None); text(c, p['headline'], 960, 705, 64, WHITE)
    c.restore()
    for i, x in enumerate([200, 1720]):
        S(c, x, t + i, 'sit', d=1 if i == 0 else -1, ch=HOST[(i + 3) % 7], face='o', gy=GY + 60)

def empty_bank(c, t, d, p):
    _room(c)
    k = ease(t / 1.2)
    x = lerp(150, 520, k) if p.get('enter') else lerp(200, 600, k)
    S(c, x, t, 'walk' if k < 1 else 'stand', d=1, ch=COP, face='o' if k >= 1 else 'n')
    S(c, x - 140, t + 0.3, 'walk' if k < 1 else 'shrug', d=1, ch=COP, face='o')
    if t > d * 0.35:
        for i in range(4):
            stick(c, 1050 + i * 150, GY, 0.85, pose('stand', t + i), 'h', -1, HOST[i].get('acc', ()), HOST[i].get('shirt'), t + i, alpha=ap(t, d * 0.35 + i * 0.15))
    question(c, 1350, 330, 220, ap(t, d * 0.6))

def evidence(c, t, d, p):
    rrect(c, 160, 600, 1600, 60, 8, fill=BROWN, stroke=INK, lw=6)
    line(c, [(240, 660), (240, 900)], 10, INK); line(c, [(1680, 660), (1680, 900)], 10, INK)
    items = p.get('items', [])
    n = len(items)
    for i, it in enumerate(items):
        x = 480 + i * 480; t0 = d * (0.12 + 0.25 * i); k = ap(t, t0)
        if k <= 0: continue
        c.save(); pop(c, x, 520, k)
        if it == 'gun': toy_gun(c, x - 50, 520, 1.6); label(c, "DE JUGUETE", x, 360, 40, WHITE, ORANGE)
        elif it == 'hole': hole_wall(c, x, 440, 70, 1.0); label(c, "UN BOQUETE", x, 300, 40, WHITE, DARK)
        elif it == 'note': note(c, x, 470, 1.0, -0.06, ["En barrio de", "ricachones..."], 32); label(c, "UNA NOTA", x, 330, 40, WHITE, BLUE)
        c.restore()

def title(c, t, d, p):
    col(c, INK); c.paint()
    k = ap(t, 0.1, 0.5)
    c.save(); pop(c, 960, 430, k)
    text(c, "EL ROBO", 960, 360, 190, WHITE); text(c, "DEL SIGLO", 960, 540, 190, YEL)
    c.restore()
    label(c, "BANCO RÍO · ACASSUSO · 2006", 960, 720, 46, INK, WHITE, ap(t, 0.8))
    for i in range(6):
        ph = (t * 0.35 + i / 6) % 1
        x = 160 + i * 320 + 40 * math.sin(t + i); y = 1080 - ph * 1200
        text(c, "$", x, y, 70, MONEY, a=0.35)
    label(c, "US$ 19 MILLONES (estimado)", 960, 860, 50, WHITE, GREEN, ap(t, d * 0.55))

def narrator(c, t, d, p):
    ground(c)
    pz = p.get('pose', 'talk'); face = {'think': 'n', 'shrug': 'w', 'laugh': 'grin', 'worried': 'w', 'point': 'h'}.get(pz, 'h')
    ps = 'talk' if t < d * 0.25 else pz
    S(c, 620, t, ps, d=1, ch=NARR, face=face, s=1.35)
    lab = p.get('label')
    if lab:
        k = ap(t, d * 0.25)
        c.save(); pop(c, 1260, 420, k)
        rrect(c, 860, 300, 800, 240, 30, fill=WHITE, stroke=INK, lw=7)
        size = 76 if len(lab) < 16 else 58
        text(c, lab, 1260, 420, size, INK)
        c.restore()
    if pz == 'think': question(c, 760, 300, 120, ap(t, d * 0.3), YEL)
    if pz == 'worried':
        for i in range(10):
            yy = (t * 400 + i * 120) % 900; xx = 900 + (i * 97) % 900
            line(c, [(xx, yy), (xx - 10, yy + 40)], 4, WATER, 0.7)

def chapter(c, t, d, p):
    col(c, YEL); c.paint()
    k = ap(t, 0.05, 0.45)
    c.save(); pop(c, 960, 430, k)
    text(c, f"CAPÍTULO {p['n']}", 960, 330, 64, INK)
    text(c, p['title'], 960, 480, 150 if len(p['title']) < 12 else 118, INK)
    c.restore()
    x = lerp(-100, 2020, t / d)
    S(c, x, t, 'run', d=1, ch=NARR, face='h', gy=860)
    line(c, [(0, 862), (1920, 862)], 6, INK)

def map_baires(c, t, d, p):
    col(c, (0.80, 0.88, 0.94)); c.rectangle(0, 0, 1920, 1080); c.fill()
    c.new_path(); c.move_to(0, 1080); c.line_to(0, 380)
    c.curve_to(400, 420, 700, 300, 1000, 260); c.curve_to(1300, 210, 1550, 120, 1920, 0); c.line_to(1920, 1080); c.close_path()
    col(c, (0.93, 0.91, 0.84)); c.fill_preserve(); c.set_line_width(6); col(c, INK); c.stroke()
    text(c, "RÍO DE LA PLATA", 520, 160, 54, (0.25, 0.4, 0.55))
    for i in range(14):
        for j in range(7):
            x = 300 + i * 110 + (j % 2) * 30; y = 520 + j * 80
            if y < 300 + (1920 - x) * 0.15: continue
            rrect(c, x, y, 80, 54, 6, fill=LGRAY, stroke=None)
    pts = [("BUENOS AIRES", 520, 900, ap(t, 0.2)), ("SAN ISIDRO", 1180, 520, ap(t, d * 0.25)), ("ACASSUSO", 1330, 400, ap(t, d * 0.45))]
    for nm, x, y, k in pts:
        if k <= 0: continue
        circle(c, x, y, 18 * k, fill=RED, stroke=INK, w=5); label(c, nm, x, y - 70, 42, WHITE, INK, k)
    if t > d * 0.65:
        for i in range(5): text(c, "$", 1380 + 60 * math.cos(t * 2 + i), 330 - 40 * i * ap(t, d * 0.65), 50, MONEY)

def bulb(c, t, d, p):
    ground(c)
    S(c, 760, t, 'think', d=1, ch=ARAUJO)
    k = ap(t, d * 0.2)
    c.save(); pop(c, 900, 360, k)
    circle(c, 900, 330, 80, fill=YEL, stroke=INK, w=7); rrect(c, 870, 400, 60, 50, 6, fill=GRAY, stroke=INK, lw=5)
    for i in range(8):
        a = i / 8 * 2 * math.pi; line(c, [(900 + math.cos(a) * 105, 330 + math.sin(a) * 105), (900 + math.cos(a) * 135, 330 + math.sin(a) * 135)], 7, YEL)
    c.restore()
    label(c, p['name'], 1380, 520, 58, WHITE, INK, ap(t, d * 0.4))
    label(c, p['sub'], 1380, 620, 40, INK, YEL, ap(t, d * 0.5))

def boqueteros(c, t, d, p):
    # wall cross-section: thief digs through wall
    rrect(c, 900, 200, 120, 680, 0, fill=(0.80, 0.50, 0.40), stroke=INK, lw=6)
    for yy in range(200, 880, 40): line(c, [(900, yy), (1020, yy)], 2, INK)
    ground(c)
    k = clamp(t / (d * 0.6))
    hole_r = 70 * k
    if hole_r > 5:
        circle(c, 960, 760, hole_r, fill=(0.08, 0.08, 0.09), stroke=INK, w=4)
    S(c, 700 + 120 * k, t, 'dig', d=1, ch=ROB, hold='shovel')
    rrect(c, 1250, 600, 300, 280, 10, fill=GRAY, stroke=INK, lw=6); circle(c, 1400, 740, 90, fill=MGRAY, stroke=INK, w=6)
    text(c, "BÓVEDA", 1400, 560, 44, INK)
    caption(c, "«BOQUETEROS»", t, 0.3, 140, 80, RED)

def plan_board(c, t, d, p):
    rrect(c, 160, 110, 1600, 820, 18, fill=(0.20, 0.32, 0.26), stroke=BROWN, lw=26)
    text(c, "EL PLAN", 960, 210, 76, WHITE, font=MONO)
    step = p['step']
    rows = [("1", "ENTRAR Y TOMAR REHENES", RED), ("2", "VACIAR LAS CAJAS DE SEGURIDAD", YEL), ("3", "ESCAPAR POR DEBAJO DE LA TIERRA", (0.5, 0.8, 1.0))]
    for i, (n, s_, rgb) in enumerate(rows):
        y = 380 + i * 170
        vis = (i + 1 < step) or (i + 1 == step and True)
        if step == 0:
            k = ap(t, 0.3 + i * 0.5)
        else:
            k = 1.0 if i + 1 < step else (ap(t, 0.2) if i + 1 == step else 0.0)
        if k <= 0: continue
        c.save(); pop(c, 300, y, k)
        circle(c, 300, y, 50, fill=rgb, stroke=WHITE, w=5); text(c, n, 300, y, 60, INK)
        a = 1.0 if (step == 0 or i + 1 == step) else 0.45
        text(c, s_, 390, y, 58, WHITE, align='l', font=MONO, a=a)
        c.restore()
    if step == 0: question(c, 1600, 300, 160, ap(t, d * 0.5), YEL)

def tunnel(c, t, d, p):
    col(c, (0.80, 0.88, 0.94)); c.rectangle(0, 0, W, 420); c.fill()
    col(c, (0.62, 0.48, 0.34)); c.rectangle(0, 420, W, 660); c.fill()
    for i in range(30): circle(c, (i * 137) % W, 480 + (i * 71) % 560, 6 + i % 5, fill=(0.52, 0.40, 0.28), stroke=None)
    line(c, [(0, 420), (W, 420)], 6, INK)
    bank(c, 420, 420, 520, 300, k=1.0)
    rrect(c, 230, 420, 380, 160, 0, fill=(0.85, 0.83, 0.78), stroke=INK, lw=5); text(c, "TESORO / CAJAS", 420, 450, 28, INK)
    # crowd of police in front
    for i in range(4): S(c, 760 + i * 70, t + i, 'stand', d=-1, ch=COP, s=0.55, gy=420)
    # drain pipe
    rrect(c, 900, 760, 1100, 120, 60, fill=(0.30, 0.30, 0.33), stroke=INK, lw=6)
    for i in range(12):
        xx = 960 + ((t * 120 + i * 90) % 1000); line(c, [(xx, 850), (xx + 30, 850)], 4, WATER)
    text(c, "DESAGÜE PLUVIAL", 1450, 940, 40, WHITE)
    phase = p.get('phase')
    k = clamp(t / (d * 0.8))
    tx = lerp(560, 960, k if phase == 'dig' else 1.0)
    pts = [(560, 540), (700, 620), (820, 760), (tx, 800)]
    c.set_line_width(56); c.set_line_cap(cairo.LINE_CAP_ROUND); col(c, (0.12, 0.10, 0.09)); c.move_to(*pts[0])
    for pt in pts[1:]: c.line_to(*pt)
    c.stroke()
    if phase == 'dig':
        S(c, lerp(560, 920, k), t, 'dig', d=1, ch=ROB, s=0.45, gy=830, hold='shovel')
        caption(c, "MIENTRAS TODOS MIRAN LA PUERTA...", t, 0.4, 120, 50)
        arrow(c, 990, 300, 990, 360, RED, 8, 1.0)
    else:
        for i in range(3):
            x = lerp(600, 1700, clamp(t / d - i * 0.08))
            S(c, x, t + i, 'run', d=1, ch=ROB, s=0.45, gy=840, hold='bag')

def safe_boxes_explain(c, t, d, p):
    _boxes(c, 300, 200, 7, 5, 120, open_n=0)
    k = ap(t, d * 0.2)
    if k > 0:
        c.save(); pop(c, 1350, 460, k)
        rrect(c, 1100, 230, 520, 460, 26, fill=WHITE, stroke=INK, lw=7)
        cash(c, 1260, 380, 1.0); gem(c, 1460, 360, 1.6); money_bag(c, 1360, 560, 0.9)
        c.restore()
    question(c, 1700, 250, 150, ap(t, d * 0.6))
    label(c, "¿QUÉ HAY ADENTRO? NI EL BANCO LO SABE", 960, 980, 46, WHITE, INK, ap(t, d * 0.55))

def _boxes(c, x0, y0, cols, rows, cell, open_n=0, t=0.0):
    for r in range(rows):
        for q in range(cols):
            i = r * cols + q; x = x0 + q * cell; y = y0 + r * cell
            rrect(c, x, y, cell - 10, cell - 10, 6, fill=(0.80, 0.80, 0.78) if i >= open_n else (0.15, 0.15, 0.16), stroke=INK, lw=4)
            if i >= open_n: circle(c, x + (cell - 10) / 2, y + (cell - 10) / 2, 9, fill=GRAY, stroke=INK, w=3)

def gang_lineup(c, t, d, p):
    ground(c)
    crew = [(ARAUJO, "?"), (VIT, "?"), (BETO, "?"), (ROB, "?"), (ROB, "?")]
    for i, (ch, _) in enumerate(crew):
        x = 360 + i * 300; k = ap(t, 0.2 + i * 0.25)
        if k <= 0: continue
        S(c, x, t + i, 'hips' if i % 2 else 'stand', d=1 if i < 2 else -1, ch=ch)
    caption(c, "EL EQUIPO", t, 0.1, 160, 80, INK)

def gang_member(c, t, d, p):
    ground(c); who = p['who']
    if who == 'vitette':
        S(c, 640, t, 'phone_talk', ch=VIT, hold='phone', face='h', s=1.3)
        label(c, "LUIS MARIO VITETTE SELLANES", 1250, 420, 50, WHITE, PINK, ap(t, 0.3)); label(c, "la cara y la voz", 1250, 520, 42, INK, WHITE, ap(t, 0.8))
    elif who == 'beto':
        S(c, 640, t, 'hips', ch=BETO, face='angry', s=1.3)
        label(c, "RUBÉN ALBERTO DE LA TORRE", 1250, 420, 50, WHITE, GREEN, ap(t, 0.3)); label(c, "«Beto» · los rehenes", 1250, 520, 42, INK, WHITE, ap(t, 0.8))
    else:
        S(c, 560, t, 'stand', ch=dict(shirt=ORANGE), s=1.2); S(c, 860, t + 1, 'stand', ch=dict(shirt=GRAY), s=1.2, d=-1)
        label(c, "SEBASTIÁN GARCÍA BOLSTER", 1360, 400, 44, WHITE, ORANGE, ap(t, 0.4))
        label(c, "JULIÁN ZALLOECHEVERRÍA", 1360, 500, 44, WHITE, DARK, ap(t, 1.2))
        label(c, "+ otros integrantes", 1360, 600, 38, INK, WHITE, ap(t, 2.0))

def toy_guns(c, t, d, p):
    ground(c)
    S(c, 700, t, 'point', ch=ROB, hold='gun', face='angry', s=1.3)
    k = ap(t, d * 0.45)
    if k > 0:
        c.save(); pop(c, 1350, 420, k); toy_gun(c, 1250, 420, 3.0); c.restore()
        label(c, "DE JUGUETE", 1400, 640, 64, WHITE, ORANGE, k)

def stamp_sc(c, t, d, p):
    ground(c)
    S(c, 520, t, 'shrug' if p['text'].startswith('¿POR') else 'think', ch=NARR, face='w', s=1.2)
    stamp(c, p['kind'], 1250, 380, ap(t, 0.3), 90)
    label(c, p['text'], 1250, 600, 56, WHITE, INK, ap(t, 0.9))
    if 'JUGUETE' in p['text']: S(c, 1680, t, 'phone', d=-1, ch=SILEO, hold='phone', s=1.0)

def bank_enter(c, t, d, p):
    ground(c); bank(c, 1150, GY, door_open=clamp(t / 1.5))
    for i in range(4):
        x = lerp(80 - i * 130, 1150, clamp((t - i * 0.4) / (d * 0.75)))
        a = 1.0 if x < 1120 else 0.0
        if a: S(c, x, t + i * 0.2, 'walk', d=1, ch=[VIT, BETO, ROB, ROB][i], face='n')
    calendar(c, 300, 260, ap(t, 0.2))

def hostage_fear(c, t, d, p):
    _room(c)
    for i in range(3):
        stick(c, 700 + i * 260, GY, 1.1, pose('cower', t + i * 0.4), 'w', 1 if i != 1 else -1, HOST[i + 2].get('acc', ()), HOST[i + 2].get('shirt'), t)
    for i, s_ in enumerate(["¿Quiénes son?", "¿Qué quieren?", "¿Cómo termina?"]):
        bubble(c, s_, 520 + i * 440, 330 + (i % 2) * 70, ap(t, d * (0.12 + 0.25 * i)), 40, tail=(30, 90), think=True)

def counter(c, t, d, p):
    col(c, INK); c.paint()
    k = ap(t, 0.1, 0.5)
    c.save(); pop(c, 960, 470, k); text(c, p['value'], 960, 470, 200, YEL); c.restore()
    text(c, p['label'], 960, 640, 70, WHITE, a=ap(t, 0.5))
    if p.get('kind'): stamp(c, p['kind'], 960, 820, ap(t, d * 0.45), 50)
    if 'POLIC' in p['label']:
        for i in range(12): stick(c, 120 + i * 155, 1080, 0.55, pose('stand', t + i), 'n', 1, ('cap_police',), BLUE, t + i, alpha=0.35)

def split_view(c, t, d, p):
    col(c, (0.80, 0.88, 0.94)); c.rectangle(0, 0, W, 540); c.fill()
    col(c, (0.62, 0.48, 0.34)); c.rectangle(0, 540, W, 540); c.fill(); line(c, [(0, 540), (W, 540)], 6, INK)
    for i in range(6): S(c, 200 + i * 130, t + i, 'point', d=1, ch=COP, s=0.7, gy=540)
    police_car(c, 1100, 540, t, -1, 0.7); bank(c, 1550, 540, 520, 330, k=1.0)
    label(c, "TODOS MIRAN AQUÍ", 600, 120, 46, WHITE, BLUE, ap(t, 0.3))
    rrect(c, 1250, 640, 600, 300, 10, fill=(0.85, 0.83, 0.78), stroke=INK, lw=5)
    _boxes(c, 1280, 670, 5, 2, 100, open_n=int(t * 2))
    S(c, 1400, t, 'dig', d=1, ch=ROB, s=0.6, gy=940)
    label(c, "...Y LA ACCIÓN ESTÁ AQUÍ", 600, 760, 52, WHITE, RED, ap(t, d * 0.5))
    arrow(c, 980, 760, 1230, 780, RED, 9, ap(t, d * 0.55))

def pizza(c, t, d, p):
    ground(c); bank(c, 1350, GY, 700, 440, door_open=0.25)
    x = lerp(200, 980, ease(t / (d * 0.6)))
    S(c, x, t, 'walk' if t < d * 0.6 else 'stand', d=1, ch=COP, hold='pizza')
    for i in range(3): pizza_box(c, x + 20, 640 - i * 30 - 30, 0.9) if t < d * 0.6 else pizza_box(c, 1290 + i * 0, 690 - i * 30, 0.9)
    label(c, "PIZZAS + GASEOSAS", 600, 180, 56, WHITE, RED, ap(t, 0.4))

def birthday(c, t, d, p):
    _room(c)
    for i in range(5):
        h = HOST[i]; face = 'h' if t > d * 0.4 else 'w'
        stick(c, 400 + i * 170, GY, 0.9, pose('sit', t + i), face, 1, h.get('acc', ()) + (('party',) if i == 2 and t > d * 0.3 else ()), h.get('shirt'), t + i)
    k = ap(t, d * 0.3)
    if k > 0:
        c.save(); pop(c, 1450, 700, k)
        rrect(c, 1330, 640, 240, 110, 14, fill=PINK, stroke=INK, lw=6); rrect(c, 1360, 580, 180, 70, 12, fill=WHITE, stroke=INK, lw=5)
        for i in range(3):
            line(c, [(1400 + i * 50, 580), (1400 + i * 50, 540)], 6, BLUE); circle(c, 1400 + i * 50, 530 + 3 * math.sin(t * 9 + i), 8, fill=YEL, stroke=None)
        c.restore()
    label(c, "¡FELIZ CUMPLEAÑOS!", 960, 230, 60, WHITE, PINK, ap(t, d * 0.5))
    label(c, "según los relatos del caso", 960, 320, 34, INK, WHITE, ap(t, d * 0.6))

def vault(c, t, d, p):
    rrect(c, 80, 120, 1760, 780, 10, fill=(0.88, 0.87, 0.84), stroke=INK, lw=6)
    n = int(clamp(t / d) * 40)
    _boxes(c, 220, 180, 10, 4, 130, open_n=n)
    for i in range(3):
        x = 450 + i * 450
        S(c, x, t + i * 0.5, 'dig' if i == 1 else 'think', d=1 if i % 2 else -1, ch=ROB, s=0.95, gy=890, hold='bag' if i == 0 else None)
    label(c, "MIENTRAS TANTO, ABAJO...", 960, 990, 50, WHITE, INK, ap(t, 0.2))

def loot(c, t, d, p):
    ground(c)
    items = [lambda k: cash(c, 500, 500, 1.6 * k), lambda k: gem(c, 900, 470, 3.2 * k), lambda k: money_bag(c, 1300, 520, 1.5 * k),
             lambda k: gem(c, 1600, 470, 2.6 * k, (0.95, 0.4, 0.6))]
    for i, f in enumerate(items):
        k = ap(t, d * (0.1 + 0.12 * i))
        if k > 0: f(k)
    if t > d * 0.6:
        for i in range(4): stick(c, 400 + i * 380, GY, 0.8, pose('sad', t + i), 's', 1, HOST[i].get('acc', ()), HOST[i].get('shirt'), t + i, alpha=ap(t, d * 0.6))
    label(c, "AHORROS DE FAMILIAS", 960, 180, 56, WHITE, INK, ap(t, d * 0.62))

def clock_sc(c, t, d, p):
    ground(c)
    h = lerp(0, 5, clamp(t / (d * 0.8)))
    clock(c, 960, 420, 230, h + 1, 1.0)
    label(c, f"{int(h) + 1} H", 960, 750, 60, WHITE, RED, ap(t, 0.2))
    S(c, 330, t, 'hips', d=1, ch=COP, face='angry'); S(c, 1600, t, 'phone_talk', d=-1, ch=VIT, hold='phone', face='h')

def police_confused(c, t, d, p):
    ground(c)
    for i in range(3): S(c, 500 + i * 300, t + i, 'shrug' if i != 1 else 'think', d=1 if i != 2 else -1, ch=COP, face='w')
    for i, s_ in enumerate(p.get("labels", ["¿UN AUTO?", "¿COMIDA?", "¿UNA SALIDA?"])):
        bubble(c, s_, 500 + i * 300, 400 - (i % 2) * 60, ap(t, d * (0.15 + 0.2 * i)), 40, tail=(0, 110), think=True)
    question(c, 1550, 420, 240, ap(t, d * 0.75))

def drain_boat(c, t, d, p):
    col(c, (0.18, 0.18, 0.20)); c.paint()
    c.new_path(); c.arc(960, 540, 600, 0, 2 * math.pi); col(c, (0.30, 0.30, 0.33)); c.fill()
    col(c, WATER); c.rectangle(0, 700, W, 380); c.fill()
    for i in range(20):
        xx = (i * 110 - t * 200) % W; line(c, [(xx, 720 + (i % 3) * 30), (xx + 50, 720 + (i % 3) * 30)], 4, (0.7, 0.85, 0.95))
    x = 960 + 60 * math.sin(t * 0.8); y = 700 + 6 * math.sin(t * 3)
    boat(c, x, y, 1.6)
    for i in range(3):
        stick(c, x - 140 + i * 140, y - 20, 0.85, pose('paddle', t + i * 0.5), 'n', 1, ('mask',), DARK, t + i)
    money_bag(c, x + 210, y - 60, 0.8)
    for i in range(2): circle(c, 960, 540, 620 + i * 30, stroke=INK, w=10)
    label(c, "GOMONES · EN LA OSCURIDAD", 960, 150, 50, WHITE, ORANGE, ap(t, 0.4))

def map_escape(c, t, d, p):
    col(c, (0.93, 0.91, 0.84)); c.paint()
    for i in range(12):
        for j in range(6): rrect(c, 120 + i * 145, 120 + j * 145, 110, 110, 8, fill=LGRAY, stroke=None)
    rrect(c, 160, 680, 130, 130, 8, fill=YEL, stroke=INK, lw=5); text(c, "BANCO", 225, 745, 26, INK)
    pts = [(225, 745), (500, 745), (500, 455), (1080, 455), (1080, 310), (1500, 310)]
    k = clamp(t / (d * 0.7)); tot = len(pts) - 1; seg_ = k * tot
    shown = [pts[0]]
    for i in range(1, len(pts)):
        if seg_ >= i: shown.append(pts[i])
        else:
            f = seg_ - (i - 1); shown.append((lerp(pts[i - 1][0], pts[i][0], f), lerp(pts[i - 1][1], pts[i][1], f))); break
    dashed(c, shown, 10, RED, (24, 16), -t * 40)
    circle(c, shown[-1][0], shown[-1][1], 16, fill=RED, stroke=INK, w=4)
    if k >= 1:
        circle(c, 1500, 310, 34, fill=DARK, stroke=INK, w=5); label(c, "ALCANTARILLA", 1500, 220, 40, WHITE, INK)
        k2 = ap(t, d * 0.75)
        if k2 > 0:
            c.save(); pop(c, 1650, 500, k2)
            rrect(c, 1530, 450, 260, 110, 18, fill=WHITE, stroke=INK, lw=5); circle(c, 1580, 570, 24, fill=DARK, stroke=INK, w=4); circle(c, 1740, 570, 24, fill=DARK, stroke=INK, w=4)
            c.restore(); label(c, "¿CAMIONETA BLANCA?", 1640, 680, 36, WHITE, (0.93, 0.62, 0.12), k2)

def hostages_free(c, t, d, p):
    ground(c)
    for i in range(6):
        h = HOST[i % 7]
        stick(c, 300 + i * 250, GY, 0.95, pose('celebrate' if i % 2 else 'stand', t + i), 'h', 1, h.get('acc', ()), h.get('shirt'), t + i)
    label(c, "NINGÚN HERIDO", 960, 240, 72, WHITE, GREEN, ap(t, d * 0.4))

def note_sc(c, t, d, p):
    ground(c)
    note(c, 1050, 470, ap(t, 0.2, 0.5), -0.04, size=50)
    S(c, 300, t, 'think', d=1, ch=COP, face='o')

def money_counter(c, t, d, p):
    col(c, INK); c.paint()
    v = int(lerp(0, 19, ease(t / (d * 0.45))))
    text(c, f"US$ {v} MILLONES", 960, 420, 150, MONEY)
    text(c, "(estimado)", 960, 560, 50, WHITE, bold=False)
    if t > d * 0.5:
        for i, (s_, x) in enumerate([("8 M", 560), ("19 M", 960), ("25 M", 1360)]):
            label(c, s_, x, 780, 70, INK, [YEL, MONEY, YEL][i], ap(t, d * (0.5 + 0.08 * i)))
        stamp(c, 'DISPUTADO', 960, 940, ap(t, d * 0.75), 44)
    for i in range(8):
        ph = (t * 0.4 + i / 8) % 1; text(c, "$", 100 + i * 245, 1080 - ph * 1150, 60, MONEY, a=0.25)

def casa_papel(c, t, d, p):
    ground(c)
    tl_y = 600; line(c, [(200, tl_y), (1720, tl_y)], 8, INK)
    for x, yr, s_, rgb in [(450, "2006", "ROBO DEL SIGLO", RED), (1450, "2017", "LA SERIE", DARK)]:
        k = ap(t, 0.3 if yr == "2006" else d * 0.4)
        if k <= 0: continue
        circle(c, x, tl_y, 22 * k, fill=rgb, stroke=INK, w=5); label(c, yr, x, tl_y - 90, 60, WHITE, rgb, k); text(c, s_, x, tl_y + 80, 40, INK, a=k)
    arrow(c, 520, 720, 1380, 720, GREEN, 8, ap(t, d * 0.6)); label(c, "+10 AÑOS ANTES", 950, 800, 44, WHITE, GREEN, ap(t, d * 0.7))

def detectives(c, t, d, p):
    ground(c)
    rrect(c, 900, 200, 820, 520, 10, fill=(0.85, 0.72, 0.50), stroke=INK, lw=7)
    for i in range(6):
        x = 980 + (i % 3) * 250; y = 280 + (i // 3) * 220
        rrect(c, x, y, 160, 120, 4, fill=WHITE, stroke=INK, lw=3); phone_icon(c, x + 80, y + 60, 0.8)
    S(c, 500, t, 'point', ch=COP, hold=None, face='n'); S(c, 300, t, 'think', ch=dict(shirt=GRAY, acc=('glasses',)))
    label(c, "PISTA: LOS TELÉFONOS", 1310, 820, 48, WHITE, INK, ap(t, 0.4))

def tower_sc(c, t, d, p):
    ground(c); ph = p['phase']
    tower(c, 960, GY, 420, t, True)
    import random
    rnd = random.Random(3)
    pts = [(rnd.uniform(150, 1770), rnd.uniform(160, 820)) for _ in range(46)]
    for i, (x, y) in enumerate(pts):
        if abs(x - 960) < 120 and y > 400: continue
        k = ap(t, d * 0.1 + i * 0.03)
        hot = ph >= 1 and i % 9 == 0
        if k > 0: phone_icon(c, x, y, 0.55 * k, RED if hot else DARK, glow=1.0 if (hot and ph == 2) else 0.0)
    if ph == 0: label(c, "MILES DE LÍNEAS", 960, 120, 56, WHITE, BLUE, ap(t, 0.3))
    elif ph == 1: label(c, "~300.000 LÍNEAS CRUZADAS", 960, 120, 56, WHITE, BLUE, ap(t, 0.3))
    elif ph == 2: label(c, "¡AHÍ ESTÁN!", 960, 120, 64, WHITE, RED, ap(t, d * 0.4))
    else: label(c, "HOY: UNA HERRAMIENTA HABITUAL", 960, 120, 56, WHITE, GREEN, ap(t, 0.3))

def network(c, t, d, p):
    col(c, (0.12, 0.13, 0.16)); c.paint()
    nodes = [(960, 520, "?", 1), (620, 330, "", 0), (1300, 330, "", 0), (560, 720, "", 0), (1360, 720, "", 0), (960, 230, "", 0), (960, 840, "", 0), (360, 520, "", 0), (1560, 520, "", 0)]
    edges = [(0, 1), (0, 2), (0, 3), (0, 4), (1, 5), (2, 5), (3, 6), (4, 6), (1, 7), (3, 7), (2, 8), (4, 8), (1, 2)]
    for i, (a, b) in enumerate(edges):
        k = clamp((t - d * 0.05 - i * 0.18) / 0.4)
        if k > 0:
            (x1, y1, _, _), (x2, y2, _, _) = nodes[a], nodes[b]
            line(c, [(x1, y1), (lerp(x1, x2, k), lerp(y1, y2, k))], 4, (0.45, 0.75, 0.95))
    for i, (x, y, s_, big) in enumerate(nodes):
        k = ap(t, i * 0.15)
        if k > 0: c.save(); pop(c, x, y, k); phone_icon(c, x, y, 1.2 if big else 0.8, RED if big else DARK); c.restore()
    label(c, "+40.000 LLAMADAS", 960, 100, 56, INK, YEL, ap(t, 0.3))
    label(c, "ORGANIGRAMA DE LA BANDA", 960, 990, 48, WHITE, BLUE, ap(t, d * 0.5))

def couple(c, t, d, p):
    ground(c)
    S(c, 760, t, 'stand', d=1, ch=ALICIA, face='n'); S(c, 1160, t, 'stand', d=-1, ch=BETO, face='h')
    heart(c, 960, 380, 0.9, broken=0.0)
    label(c, "ALICIA DI TULLIO", 760, 980, 44, WHITE, PURPLE, ap(t, 0.3)); label(c, "BETO DE LA TORRE", 1160, 1040, 40, WHITE, GREEN, ap(t, 0.8))

def denounce(c, t, d, p):
    ground(c)
    rrect(c, 1150, 300, 560, 580, 8, fill=(0.90, 0.88, 0.82), stroke=INK, lw=6); text(c, "JUSTICIA", 1430, 360, 48, INK)
    x = lerp(300, 1000, ease(t / (d * 0.5)))
    S(c, x, t, 'walk' if t < d * 0.5 else 'point', d=1, ch=ALICIA, face='angry', hold='paper')
    heart(c, 400, 330, 0.7, broken=ease((t - d * 0.4) / 0.6))
    label(c, "LA DENUNCIA", 1430, 960, 50, WHITE, RED, ap(t, d * 0.55))

def puzzle(c, t, d, p):
    col(c, (0.12, 0.13, 0.16)); c.paint()
    for i in range(6):
        x = 560 + (i % 3) * 270; y = 360 + (i // 3) * 270
        if i == 4:
            k = ease((t - d * 0.3) / (d * 0.4)); x = lerp(1600, x, k); y = lerp(900, y, k)
            rgb = PURPLE
        else: rgb = BLUE
        rrect(c, x - 120, y - 120, 240, 240, 18, fill=rgb, stroke=WHITE, lw=6)
        circle(c, x + 120, y, 34, fill=rgb, stroke=WHITE, w=6)
    label(c, "LLAMADAS + DENUNCIA", 960, 120, 54, INK, YEL, ap(t, d * 0.7))

def arrests(c, t, d, p):
    ground(c)
    chars = [VIT, BETO, ARAUJO, dict(shirt=ORANGE), dict(shirt=GRAY)]
    for i, ch in enumerate(chars):
        k = ap(t, d * (0.08 + 0.15 * i))
        if k <= 0: continue
        x = 300 + i * 330
        S(c, x, t, 'cuffed', d=1, ch=ch, face='s'); S(c, x + 110, t + i, 'stand', d=-1, ch=COP, s=0.9)
        label(c, "DETENIDO", x + 50, 330, 34, WHITE, RED, k)

def court(c, t, d, p):
    ground(c)
    S(c, 960, t, 'stand', ch=dict(shirt=DARK), hold='gavel', gy=700, ua_f=1.2 + 0.6 * max(0, math.sin(t * 5)), fa_f=0.2)
    rrect(c, 660, 480, 600, 400, 8, fill=BROWN, stroke=INK, lw=7); text(c, "JUSTICIA", 960, 600, 48, WHITE)
    label(c, "TRIBUNAL DE SAN ISIDRO", 960, 160, 52, WHITE, INK, ap(t, 0.3))

def sentences(c, t, d, p):
    col(c, (0.95, 0.94, 0.90)); c.paint()
    rows = [("BETO DE LA TORRE", "15 AÑOS", GREEN), ("FERNANDO ARAUJO", "14 AÑOS*", YEL), ("J. ZALLOECHEVERRÍA", "10 AÑOS", GRAY),
            ("S. GARCÍA BOLSTER", "9 AÑOS", ORANGE), ("L. M. VITETTE", "CONDENADO", PINK)]
    for i, (n, s_, rgb) in enumerate(rows):
        k = ap(t, d * (0.05 + 0.17 * i))
        if k <= 0: continue
        y = 200 + i * 150
        c.save(); pop(c, 960, y, k)
        rrect(c, 360, y - 55, 1200, 110, 18, fill=WHITE, stroke=INK, lw=5); circle(c, 430, y, 30, fill=rgb, stroke=INK, w=4)
        text(c, n, 490, y, 46, INK, align='l'); text(c, s_, 1520, y, 50, RED, align='r')
        c.restore()
    text(c, "* luego reducidos, según algunas fuentes", 960, 1000, 32, DARK, bold=False, a=ap(t, d * 0.4))

def money_missing(c, t, d, p):
    ground(c)
    for i in range(19):
        x = 200 + (i % 10) * 160; y = 420 + (i // 10) * 170
        rec = i == 0
        a = 1.0 if rec else clamp(1 - (t - d * 0.35 - i * 0.12) / 0.25)
        if a > 0:
            c.push_group(); money_bag(c, x, y, 0.7, '$'); c.pop_group_to_source(); c.paint_with_alpha(a)
        if rec: label(c, "RECUPERADO: ~1 M", x + 120, y - 120, 36, WHITE, GREEN, ap(t, d * 0.3))
    label(c, "EL RESTO: NUNCA APARECIÓ", 1100, 860, 48, WHITE, RED, ap(t, d * 0.7))

def question_sc(c, t, d, p):
    ground(c)
    S(c, 500, t, 'shrug', ch=NARR, face='w', s=1.3)
    question(c, 1250, 460, 420, ap(t, 0.2, 0.5))
    label(c, "¿DÓNDE ESTÁ EL DINERO?", 1250, 820, 50, WHITE, INK, ap(t, d * 0.4))

def victims(c, t, d, p):
    ground(c)
    _boxes(c, 1180, 260, 4, 3, 130, open_n=12)
    for i in range(4):
        h = HOST[(i + 1) % 7]; stick(c, 260 + i * 210, GY, 1.0, pose('sad', t + i), 's', 1, h.get('acc', ()), h.get('shirt'), t + i)
    label(c, "LAS CAJAS TENÍAN DUEÑOS", 960, 140, 56, WHITE, INK, ap(t, d * 0.35))

def free_now(c, t, d, p):
    ground(c)
    k = ease(t / (d * 0.5))
    bars(c, 200, 300, 600, 580 * (1 - k))
    for i in range(3):
        x = lerp(380 + i * 140, 1100 + i * 250, ease((t - d * 0.4) / (d * 0.5)))
        S(c, x, t + i, 'walk' if 0.4 * d < t < 0.9 * d else 'stand', d=1, ch=[VIT, BETO, ARAUJO][i])
    label(c, "HOY: EN LIBERTAD", 1300, 220, 60, WHITE, GREEN, ap(t, d * 0.5))

def movie(c, t, d, p):
    col(c, (0.10, 0.10, 0.12)); c.paint()
    rrect(c, 360, 160, 1200, 560, 8, fill=(0.95, 0.94, 0.90), stroke=None)
    c.save(); c.rectangle(360, 160, 1200, 560); c.clip(); bank(c, 960, 680, 520, 330, k=1.0); c.restore()
    for i in range(8): stick(c, 260 + i * 200, 1060, 0.7, pose('sit', t + i), 'h', 1, (), [RED, BLUE, GREEN, YEL][i % 4], t + i)
    label(c, "«EL ROBO DEL SIGLO» · CINE 2020", 960, 820, 50, INK, YEL, ap(t, 0.3))
    label(c, "20 AÑOS · ENERO 2026", 960, 100, 46, WHITE, RED, ap(t, d * 0.55))

def uruguay(c, t, d, p):
    tunnel(c, t, d, {'phase': 'dig'}) if False else None
    col(c, (0.80, 0.88, 0.94)); c.rectangle(0, 0, W, 460); c.fill(); col(c, (0.62, 0.48, 0.34)); c.rectangle(0, 460, W, 620); c.fill()
    line(c, [(0, 460), (W, 460)], 6, INK)
    bank(c, 1350, 460, 520, 300, sign="BANCO", sub="Montevideo", k=1.0)
    k = clamp(t / (d * 0.6)); c.set_line_width(50); c.set_line_cap(cairo.LINE_CAP_ROUND); col(c, (0.12, 0.10, 0.09)); c.move_to(300, 760); c.line_to(lerp(300, 1150, k), 760); c.stroke()
    S(c, lerp(300, 1100, k), t, 'dig', ch=ROB, s=0.5, gy=790, hold='shovel')
    if t > d * 0.62:
        for i in range(3): S(c, 1700 - i * 110, t + i, 'point', d=-1, ch=COP, s=0.5, gy=790)
        stamp(c, 'VERIFICADO', 600, 300, ap(t, d * 0.7), 48, "FEB 2026 · FRUSTRADO")
    label(c, "MONTEVIDEO, URUGUAY", 520, 120, 50, WHITE, BLUE, ap(t, 0.2))

def verdict(c, t, d, p):
    col(c, (0.12, 0.12, 0.14)); c.paint()
    cols = [('VERIFICADO', ["Asalto y rehenes", "Túnel y fuga", "Condenas"]), ('DISPUTADO', ["Monto exacto", "¿Armas de juguete?", "Motivo de la denuncia"]), ('LEYENDA', ["Un robo «sin víctimas»"])]
    for i, (k_, items) in enumerate(cols):
        x = 340 + i * 620; k = ap(t, d * (0.08 + 0.3 * i))
        if k <= 0: continue
        rgb = STAMP[k_]
        c.save(); pop(c, x, 540, k)
        rrect(c, x - 280, 160, 560, 760, 22, fill=None, stroke=rgb, lw=7); text(c, k_, x, 240, 58, rgb)
        for j, s_ in enumerate(items): text(c, "• " + s_, x - 240, 380 + j * 120, 40, WHITE, align='l')
        c.restore()

def ending(c, t, d, p):
    ground(c)
    S(c, 620, t, 'talk', ch=NARR, face='h', s=1.3)
    note(c, 1300, 430, ap(t, 0.3), -0.05, ["sin armas", "ni rencores..."], 56)
    if t > d * 0.5:
        k = ap(t, d * 0.5)
        c.save(); pop(c, 1300, 430, k); line(c, [(1060, 470), (1540, 400)], 12, RED); c.restore()
        label(c, "EL ERROR FUE HUMANO", 1300, 720, 50, WHITE, RED, k)

def end_screen(c, t, d, p):
    col(c, YEL); c.paint()
    rrect(c, 140, 260, 900, 520, 24, fill=WHITE, stroke=INK, lw=8); text(c, "PRÓXIMO VIDEO", 590, 520, 64, INK)
    circle(c, 1450, 520, 230, fill=RED, stroke=INK, w=8); text(c, "SUSCRÍBETE", 1450, 520, 52, WHITE)
    S(c, 1450, t, 'celebrate', ch=NARR, face='h', gy=1060, s=0.9)
    text(c, "Casos reales · contados con evidencia", 960, 150, 46, INK)

def negotiation(c, t, d, p):
    ground(c)
    steps = ["ESCUCHAR", "EMPATÍA", "CONFIANZA", "CAMBIO"]
    for i, s_ in enumerate(steps):
        x = 360 + i * 330; y = 880 - (i + 1) * 120
        k = ap(t, d * (0.08 + 0.13 * i))
        if k <= 0: continue
        c.save(); pop(c, x + 160, 880, k)
        rrect(c, x, y, 330, 880 - y, 0, fill=[BLUE, GREEN, YEL, ORANGE][i], stroke=INK, lw=6)
        text(c, s_, x + 165, y + 50, 40, WHITE if i < 2 else INK)
        c.restore()
    st = min(3, int(clamp(t / (d * 0.75)) * 4))
    S(c, 360 + st * 330 + 165, t, 'stand', ch=SILEO, gy=880 - (st + 1) * 120, s=0.9)
    clock(c, 1700, 220, 90, t, ap(t, d * 0.6)); label(c, "EL TIEMPO = ALIADO", 1500, 360, 40, WHITE, BLUE, ap(t, d * 0.7))

def brazil(c, t, d, p):
    col(c, (0.80, 0.88, 0.94)); c.rectangle(0, 0, W, 460); c.fill(); col(c, (0.62, 0.48, 0.34)); c.rectangle(0, 460, W, 620); c.fill()
    line(c, [(0, 460), (W, 460)], 6, INK)
    rrect(c, 180, 300, 260, 160, 6, fill=(0.95, 0.85, 0.6), stroke=INK, lw=6); poly(c, [(160, 300), (310, 200), (460, 300)], fill=RED, stroke=INK, lw=6)
    text(c, "CASA ALQUILADA", 310, 520, 34, WHITE)
    bank(c, 1450, 460, 560, 320, sign="BANCO CENTRAL", sub="Fortaleza, Brasil", k=1.0)
    k = clamp(t / (d * 0.55)); c.set_line_width(46); c.set_line_cap(cairo.LINE_CAP_ROUND); col(c, (0.12, 0.10, 0.09))
    c.move_to(310, 600); c.line_to(lerp(310, 1450, k), 600); c.stroke()
    label(c, "~80 METROS DE TÚNEL", 880, 720, 46, WHITE, INK, ap(t, d * 0.3))
    label(c, "AGOSTO 2005", 300, 120, 46, WHITE, GREEN, ap(t, 0.2))
    label(c, "R$ 164 MILLONES", 1450, 860, 56, WHITE, GREEN, ap(t, d * 0.6))

SCENES = {k: v for k, v in globals().items() if callable(v) and not k.startswith('_')}
SCENES['stamp'] = stamp_sc; SCENES['note'] = note_sc; SCENES['clock'] = clock_sc; SCENES['tower'] = tower_sc; SCENES['question'] = question_sc

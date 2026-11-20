"""Timeline, audio, subtitles and clip rendering for the Somerton documentary."""
import json, os, sys, subprocess, math, random
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, resample_poly
from PIL import Image, ImageDraw
import gfx
from gfx import OUT as G

P = os.path.dirname(os.path.abspath(__file__))
IMG = f"{P}/img"; GEN = f"{IMG}/gen"
FPS = 24
blocks = json.load(open(f"{P}/blocks.json"))
sents = json.load(open(f"{P}/sentences.json"))
by_block = {}
for s in sents: by_block.setdefault(s['block'], []).append(s)

# ---------------- assets ----------------
def ph(key, bw=True, **kw):
    src = {'el_beach': f"{IMG}/el_beach.png", 'el_shoes': f"{IMG}/el_shoes.png", 'el_evidence': f"{IMG}/el_evidence.png",
           'station': f"{IMG}/station.png"}.get(key, f"{GEN}/{key}.png")
    return gfx.prep_photo(src, key + kw.pop('suffix', ''), bw=bw, **kw)

COLOR = {'university', 'exhumation_tent', 'dna_lab', 'hair_tweezers', 'plaster_museum', 'beach_sunset', 'ocean_horizon'}
def A(key, **kw):
    if key in COLOR: return ph(key, bw=False, **kw)
    return ph(key, **kw)

def card_list(name, title, items):
    im = gfx._paper(41); d = ImageDraw.Draw(im)
    d.text((240, 200), title, font=gfx.font('typeb', 96), fill=gfx.INK)
    d.line((240, 320, 2640, 320), fill=gfx.INK, width=5)
    for i, t in enumerate(items):
        d.text((260, 420 + i * 170), t, font=gfx.font('typeb', 78), fill=gfx.INK)
    return gfx.save_card(im, name)

def build_assets():
    a = {}
    a['tag'] = gfx.ov_tag()
    a['loc_somerton'] = gfx.ov_loc('loc_somerton', 'Playa de Somerton, Adelaida', 'Australia · 1 de diciembre de 1948')
    a['loc_adel'] = gfx.ov_loc('loc_adel', 'Adelaida, 1948', 'Australia del Sur')
    a['loc_station'] = gfx.ov_loc('loc_station', 'Estación central de Adelaida', 'Consigna de equipajes')
    a['loc_glenelg49'] = gfx.ov_loc('loc_glenelg49', 'Glenelg · julio de 1949', 'Oficina de detectives de Adelaida')
    a['loc_jessica'] = gfx.ov_loc('loc_jessica', 'Jessica «Jo» Thomson', 'Enfermera · Glenelg')
    a['loc_boxall'] = gfx.ov_loc('loc_boxall', 'Alfred Boxall', 'Sídney · estaba vivo')
    a['loc_uni'] = gfx.ov_loc('loc_uni', 'Universidad de Adelaida', 'Prof. Derek Abbott')
    a['loc_webb'] = gfx.ov_loc('loc_webb', 'Carl «Charles» Webb', 'Melbourne · desaparece de los registros en 1947')
    S = gfx.ov_sello
    a['s_testigos'] = S('s_testigos', 'DISPUTADO', 'Testigos: la tarde anterior, un hombre tendido en el mismo lugar')
    a['s_evid'] = S('s_evid', 'VERIFICADO', 'Contenido de los bolsillos')
    a['s_causa'] = S('s_causa', 'VERIFICADO', 'Causa oficial de la muerte: DESCONOCIDA')
    a['s_veneno'] = S('s_veneno', 'DISPUTADO', '¿Digital? ¿Ouabaína? Nunca se confirmó')
    a['s_maleta'] = S('s_maleta', 'VERIFICADO', 'Depositada el 30 de noviembre de 1948')
    a['s_keane'] = S('s_keane', 'VERIFICADO', 'Un nombre en algunas prendas', pos='tl')
    a['s_recorrido'] = S('s_recorrido', 'DISPUTADO', 'Recorrido desconocido')
    a['s_errata'] = S('s_errata', 'VERIFICADO', 'Errata en la prensa de la época')
    a['s_libro'] = S('s_libro', 'DISPUTADO', 'Cómo apareció el libro: versiones distintas')
    a['s_codigo'] = S('s_codigo', 'VERIFICADO', 'Nunca descifrado')
    a['s_boxall'] = S('s_boxall', 'VERIFICADO', 'El libro de Boxall estaba intacto')
    a['s_reaccion'] = S('s_reaccion', 'DISPUTADO', 'Su reacción ante el busto: versiones distintas')
    a['s_familia'] = S('s_familia', 'DISPUTADO', 'Teorías posteriores de su familia')
    a['s_espia'] = S('s_espia', 'LEYENDA', 'Sin pruebas documentales')
    a['s_amor'] = S('s_amor', 'DISPUTADO', 'Conexión nunca demostrada')
    a['s_suicidio'] = S('s_suicidio', 'DISPUTADO', 'No explica el código ni el teléfono')
    a['s_1959'] = S('s_1959', 'DISPUTADO', 'Testimonio de 1959')
    a['s_exhum'] = S('s_exhum', 'VERIFICADO', 'Mayo de 2021: exhumación')
    a['s_pelo'] = S('s_pelo', 'VERIFICADO', 'ADN de un pelo atrapado en el yeso')
    a['s_noconf'] = S('s_noconf', 'DISPUTADO', 'Identificación aún no confirmada oficialmente')
    C = gfx.ov_center
    a['t_seacabo'] = C('t_seacabo', '«Se acabó»', size=78, y=860)
    a['t_porque'] = C('t_porque', '¿Por qué?', size=120)
    a['t_pieza'] = C('t_pieza', 'La pieza que faltaba', size=84, y=860)
    a['t_ultimas'] = C('t_ultimas', 'Las últimas palabras del libro', size=70, y=900)
    a['t_teo1'] = C('t_teo1', 'TEORÍA 1: ESPÍA', size=90, y=880)
    a['t_teo2'] = C('t_teo2', 'TEORÍA 2: AMOR', size=90, y=880)
    a['t_teo3'] = C('t_teo3', 'TEORÍA 3: SUICIDIO', size=90, y=880)
    a['t_sinnombre'] = C('t_sinnombre', 'Sin nombre, ninguna teoría puede probarse', size=74)
    a['t_genetica'] = C('t_genetica', 'Genealogía genética', size=84, y=880)
    a['scrap_t'] = gfx.ov_scrap_text('scrap_t')
    a['scrap_slide'] = gfx.ov_scrap()
    a['keane'] = gfx.ov_keane()
    a['headline'] = gfx.ov_headline('headline', 'TAMAN SHUD', 'Así lo publicaron los periódicos: con una errata')
    a['lab_hombre'] = gfx.ov_labels_seq('lab_hombre', ['40-45 AÑOS (ESTIMADO)', 'BUENA FORMA FÍSICA', 'TRAJE Y CORBATA', 'SIN DOCUMENTOS'], x=1150, y=300, title='EL HOMBRE DE LA PLAYA')
    a['lab_teorias'] = gfx.ov_labels_seq('lab_teorias', ['1 · ESPÍA', '2 · AMOR', '3 · SUICIDIO'], x=1300, y=360, title='TRES TEORÍAS')
    # cards
    a['map_aus'] = gfx.card_map_aus('map_aus', ('Adelaida',), caption='1 de diciembre de 1948')
    a['map_pins'] = gfx.card_map_aus('map_pins', (), pins=46, caption='Ningún «Keane» desaparecido')
    a['map_syd'] = gfx.card_map_aus('map_syd', ('Adelaida', 'Sídney'), line=('Adelaida', 'Sídney'), caption='Alfred Boxall: vivo, en Sídney')
    a['map_mel'] = gfx.card_map_aus('map_mel', ('Adelaida', 'Melbourne'), line=('Melbourne', 'Adelaida'), caption='Carl Webb: de Melbourne')
    a['coast_route'] = gfx.card_map_coast('coast_route', ['est', 'henley', 'somerton'],
        notes={'est': 'maleta · 30 nov', 'henley': 'billete sin usar', 'somerton': 'hallazgo · 1 dic'},
        route=[('est', 'henley', (110, 110, 110)), ('est', 'somerton', (176, 40, 32))], caption='¿Por qué cambió de destino?')
    a['coast_glenelg'] = gfx.card_map_coast('coast_glenelg', ['glenelg', 'somerton'],
        notes={'glenelg': 'casa de la enfermera', 'somerton': 'lugar del hallazgo'}, caption='Muy cerca')
    a['card_title'] = gfx.card_title(A('el_beach'))
    for n, t, bg in [(1, 'Un hombre sin nada', 'adelaide_street'), (2, 'La maleta sin dueño', 'station'), (3, 'Tamám Shud', 'book_open'),
                     (4, 'La enfermera', 'woman_doorway'), (5, 'Espía, amante o suicida', 'three_files'), (6, 'Un pelo en una máscara de yeso', 'dna_lab'),
                     (7, 'Caso cerrado... o no', 'beach_sunset')]:
        a[f'ch{n}'] = gfx.card_chapter(n, t, A(bg))
    a['evlist'] = card_list('card_evlist', 'EVIDENCIA · BOLSILLOS', ['01  Billete de tren a Henley Beach (sin usar)', '02  Billete de autobús', '03  Peine de aluminio (EE. UU.)',
        '04  Medio paquete de chicles', '05  Caja de fósforos', '06  Cajetilla Army Club con 7 Kensitas'])
    a['page_hole'] = gfx.card_page_hole()
    a['code_base'], a['code_ov'] = gfx.code_layers(f"{GEN}/aged_paper.png")
    a['txt_version'] = gfx.card_text('txt_version', 'Ella nunca cambió su versión', sub='Murió sin aclararlo')
    a['txt_code'] = gfx.card_text('txt_code', 'El código sigue sin descifrar')
    a['process'] = gfx.card_process(); a['tree'] = gfx.card_tree(False); a['tree_hl'] = gfx.card_tree(True)
    a['headline_card'] = gfx.card_headline(); a['cols'] = gfx.card_columns(False); a['cols_full'] = gfx.card_columns(True)
    a['end'] = gfx.card_end(A('ocean_horizon'))
    return a

# ---------------- manifest ----------------
def SH(img, mot='in', ov=(), nb=None, tag=None, slide=None, hold=0.0, pre=0.0, post=0.0):
    return dict(img=img, mot=mot, ov=list(ov), nb=nb, tag=tag, slide=slide, hold=hold, pre=pre, post=post)

def manifest(a):
    E = lambda k, **kw: A(k, **kw)
    ev_crop = A('el_evidence', crop=(0, 260, 1720, 1228), suffix='_crop')
    seq = lambda lst, t0=0.08, step=0.18: [(p, t0 + i * step, 1.0) for i, p in enumerate(lst)]
    M = {
     1: [SH(E('el_beach'), 'in', [(a['loc_somerton'], 0.15, 0.95)], pre=1.2)],
     3: [SH(E('el_shoes'), 'in')],
     5: [SH(ev_crop, 'r')],
     7: [SH(E('shirt_collar'), 'in', pre=0.5)],
     9: [SH(E('paper_scrap'), 'in', [(a['scrap_t'], 0.0, 1.0)], pre=0.3)],
     11: [SH(E('plaster_museum'), 'in', pre=0.8), SH(E('hair_tweezers'), 'in')],
     13: [SH(a['map_aus'], 'in', tag=False), SH(a['card_title'], 'static', post=1.5, tag=False)],
     16: [SH(E('adelaide_street'), 'r', [(a['loc_adel'], 0.1, 0.9)])],
     18: [SH(E('beach_evening'), 'l', [(a['s_testigos'], 0.15, 1.0)], nb=1), SH(E('el_shoes', suffix='_b'), 'out', nb=1, post=0.4)],
     21: [SH(E('suit_silhouette'), 'in', seq(a['lab_hombre'], 0.1, 0.17))],
     23: [SH(ev_crop, 'in', [(a['s_evid'], 0.1, 1.0)]), SH(a['evlist'], 'static', tag=False)],
     25: [SH(A('el_evidence', crop=(1180, 520, 1960, 959), suffix='_pack'), 'in', [(a['t_porque'], 0.15, 0.9)])],
     27: [SH(E('pathology_lab'), 'r')],
     30: [SH(E('coroner_court'), 'in', [(a['s_causa'], 0.1, 1.0)])],
     32: [SH(E('poison_bottles'), 'in', [(a['s_veneno'], 0.1, 1.0)], nb=2), SH(E('suitcase_counter', suffix='_dim', dim=0.7), 'in', nb=1, post=0.6)],
     37: [SH(E('station'), 'l', [(a['loc_station'], 0.1, 0.9)])],
     39: [SH(E('suitcase_counter'), 'in', [(a['s_maleta'], 0.1, 1.0)])],
     41: [SH(E('suitcase_open'), 'out')],
     43: [SH(E('tie_label'), 'in', [(a['keane'], 0.12, 1.0), (a['s_keane'], 0.3, 1.0)])],
     46: [SH(a['coast_route'], 'in', [(a['s_recorrido'], 0.65, 1.0)], tag=False)],
     48: [SH(a['map_pins'], 'out', tag=False)],
     50: [SH(E('paper_scrap', suffix='_b'), 'out', [(a['scrap_t'], 0.0, 1.0), (a['t_pieza'], 0.2, 1.0)], post=0.6)],
     53: [SH(E('book_open'), 'in')],
     55: [SH(E('book_open', suffix='_b'), 'r', [(a['t_ultimas'], 0.05, 0.9)], nb=1), SH(E('suit_silhouette', suffix='_b'), 'out', nb=1)],
     58: [SH(E('newspaper'), 'in', [(a['headline'], 0.08, 1.0)])],
     60: [SH(E('car_night'), 'r', [(a['loc_glenelg49'], 0.05, 0.5), (a['s_libro'], 0.55, 1.0)])],
     62: [SH(a['page_hole'], 'static', slide=(a['scrap_slide'], 0.25), tag=False, post=0.4)],
     65: [SH(a['code_base'], 'static', seq(a['code_ov'], 0.03, 0.09) + [(a['s_codigo'], 0.6, 1.0)], tag=False)],
     67: [SH(E('rotary_phone'), 'in')],
     69: [SH(a['coast_glenelg'], 'in', nb=1, tag=False), SH(E('glenelg_street'), 'r', nb=1, post=0.6)],
     73: [SH(E('woman_doorway'), 'in', [(a['loc_jessica'], 0.15, 0.95)], nb=1), SH(E('detective_office'), 'r', nb=1)],
     76: [SH(a['map_syd'], 'in', [(a['loc_boxall'], 0.2, 0.95)], tag=False)],
     78: [SH(E('book_inscription'), 'in', [(a['s_boxall'], 0.1, 1.0)])],
     81: [SH(E('bust_cloth'), 'in', nb=1), SH(E('woman_doorway', suffix='_b'), 'out', [(a['s_reaccion'], 0.05, 1.0)], nb=1)],
     84: [SH(a['txt_version'], 'static', tag=False)],
     86: [SH(E('glenelg_street', suffix='_b'), 'l', [(a['s_familia'], 0.1, 1.0)])],
     89: [SH(E('three_files'), 'in', seq(a['lab_teorias'], 0.15, 0.22))],
     91: [SH(E('teletype'), 'in', [(a['t_teo1'], 0.03, 0.45), (a['s_espia'], 0.5, 1.0)])],
     93: [SH(a['coast_glenelg'], 'out', [(a['t_teo2'], 0.03, 0.45), (a['s_amor'], 0.5, 1.0)], tag=False)],
     95: [SH(E('paper_scrap', suffix='_c'), 'in', [(a['scrap_t'], 0.0, 1.0), (a['t_teo3'], 0.03, 0.45), (a['s_suicidio'], 0.5, 1.0)])],
     97: [SH(E('beach_night_figures'), 'in', [(a['s_1959'], 0.1, 1.0)])],
     100: [SH(E('three_files', suffix='_b'), 'out', [(a['t_sinnombre'], 0.1, 0.95)], nb=1), SH(E('cemetery_bw'), 'in', nb=1, post=0.6)],
     104: [SH(E('university'), 'r', [(a['loc_uni'], 0.1, 0.9)])],
     106: [SH(E('exhumation_tent'), 'in', [(a['s_exhum'], 0.1, 1.0)])],
     108: [SH(E('plaster_museum', suffix='_b'), 'in'), SH(E('hair_tweezers', suffix='_b'), 'in', [(a['s_pelo'], 0.05, 1.0)])],
     110: [SH(E('dna_lab'), 'r', [(a['t_genetica'], 0.05, 0.4)])],
     113: [SH(a['process'], 'static', tag=False)],
     115: [SH(a['headline_card'], 'in', tag=False)],
     117: [SH(a['map_mel'], 'in', tag=False), SH(E('melbourne_street'), 'in', [(a['loc_webb'], 0.1, 0.95)])],
     119: [SH(a['tree'], 'static', nb=1, tag=False), SH(E('tie_label', suffix='_b'), 'in', [(a['keane'], 0.0, 1.0)], nb=1)],
     122: [SH(a['tree_hl'], 'static', pre=2.2, tag=False, post=0.5)],
     125: [SH(a['cols'], 'static', tag=False)],
     127: [SH(E('plaster_museum', suffix='_c'), 'out', [(a['s_noconf'], 0.05, 1.0)], nb=1), SH(E('dna_lab', suffix='_b'), 'l', nb=1),
           SH(a['cols_full'], 'static', nb=4, tag=False)],
     134: [SH(a['code_base'], 'static', [(a['code_ov'][-1], 0.0, 0.85)], tag=False, post=0.8)],
     136: [SH(E('beach_sunset'), 'out', pre=0.6)],
     138: [SH(E('paper_scrap', suffix='_d'), 'in', [(a['scrap_t'], 0.0, 1.0)]), SH(E('ocean_horizon'), 'out', post=1.5)],
     140: [SH(a['txt_code'], 'static', hold=3.5, nb=0, tag=False), SH(a['end'], 'static', nb=1, post=14, tag=False)],
    }
    return M

# ---------------- timeline ----------------
GAP_S, GAP_P = 0.32, 0.6
CH_DUR = 3.4

def timeline(a, M):
    clips = []; voice = []  # voice: (t, file)
    t = 0.0; chapters = []; hits = []; stamps = []
    order = []
    cur = None
    for i, (typ, txt) in enumerate(blocks):
        if typ == 'H':
            if cur: order.append(cur); cur = None
            n = 0 if 'COLD OPEN' in txt else int(txt.split('CAPÍTULO ')[1].split()[0])
            order.append(('CH', n))
        elif typ == 'V':
            if i in M:
                if cur: order.append(cur)
                cur = ('SC', i, [])
        else:
            cur[2].append(i)
    if cur: order.append(cur)
    for item in order:
        if item[0] == 'CH':
            n = item[1]; chapters.append((n, t))
            if n == 0: continue
            clips.append(dict(img=a[f'ch{n}'], mot='static', ov=[], dur=CH_DUR, start=t, tag=False, slide=None, fin=0.6, fout=0.6))
            hits.append((t + 0.15, 0.6)); t += CH_DUR; continue
        _, v, nbl = item; shots = M[v]
        # assign narration blocks to shots
        if all(s['nb'] is None for s in shots) and len(shots) > 1:
            # equal time split over all blocks
            segs = []; tt = 0
            for b in nbl:
                for s in by_block[b]: segs.append((tt, s)); tt += s['dur'] + GAP_S
                tt += GAP_P - GAP_S
            total = tt + shots[0]['pre'] + sum(s['post'] for s in shots)
            t0 = t
            for s_ in segs: voice.append((t0 + shots[0]['pre'] + s_[0], s_[1]))
            each = total / len(shots)
            for k, sh in enumerate(shots):
                clips.append(dict(sh, dur=each, start=t + k * each))
            t += total
            continue
        bi = 0
        for k, sh in enumerate(shots):
            take = sh['nb'] if sh['nb'] is not None else len(nbl) - bi
            if k == len(shots) - 1 and sh['nb'] is None: take = len(nbl) - bi
            mine = nbl[bi:bi + take]; bi += take
            st = t; tt = t + sh['pre']
            for b in mine:
                for s in by_block[b]: voice.append((tt, s)); tt += s['dur'] + GAP_S
                tt += GAP_P - GAP_S
            tt += sh['hold'] + sh['post']
            clips.append(dict(sh, dur=tt - st, start=st)); t = tt
    for c in clips:
        for (p, f0, f1) in c['ov']:
            if os.path.basename(p).startswith('ov_s_'): stamps.append(c['start'] + f0 * c['dur'])
        if c['img'] in (a['card_title'], a['headline_card'], a['tree_hl']): hits.append((c['start'] + (c['pre'] if 'pre' in c else 0) + 0.05, 1.0))
        if any(p == a['keane'] for p, _, _ in c['ov']): hits.append((c['start'] + c['ov'][0][1] * c['dur'], 0.8))
    return clips, voice, chapters, hits, stamps, t

# ---------------- audio ----------------
SR = 48000
def lp(x, fc, order=2): return sosfilt(butter(order, fc, 'low', fs=SR, output='sos'), x)
def bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], 'band', fs=SR, output='sos'), x)

def note(f, dur=5.0, vel=1.0):
    n = int(dur * SR); tt = np.arange(n) / SR; s = np.zeros(n)
    for h in range(1, 7): s += np.sin(2 * np.pi * f * h * tt) * np.exp(-tt * (0.9 + 0.7 * h)) / h ** 1.4
    s *= np.minimum(1, tt / 0.006) * vel
    return s

CH_MUSIC = {0: (55.0, [220, 261.6, 329.6, 392, 440], False), 1: (73.4, [293.7, 349.2, 440, 523.3], False),
            2: (82.4, [329.6, 392, 493.9, 587.3], True), 3: (55.0, [220, 233.1, 277.2, 293.7, 329.6], False),
            4: (87.3, [349.2, 440, 523.3, 659.3], False), 5: (65.4, [261.6, 311.1, 392, 466.2], False),
            6: (98.0, [392, 493.9, 587.3, 740], True), 7: (55.0, [220, 277.2, 329.6, 440], False)}

def music_segment(dur, ch, seed):
    root, scale, pulse = CH_MUSIC[ch]; r = np.random.default_rng(seed)
    n = int(dur * SR); tt = np.arange(n) / SR
    L = np.zeros(n); R = np.zeros(n)
    for i, (m, amp) in enumerate([(1, .5), (1.5, .22), (2, .3), (2.997, .1), (4.01, .05)]):
        f = root * m; ph = r.uniform(0, 6.28)
        lfo = 0.65 + 0.35 * np.sin(2 * np.pi * tt / (7 + 3 * i) + ph)
        L += amp * lfo * np.sin(2 * np.pi * f * tt + ph); R += amp * lfo * np.sin(2 * np.pi * f * 1.0015 * tt + ph + 0.4)
    air = lp(r.normal(0, 1, n), 500) * (0.5 + 0.5 * np.sin(2 * np.pi * tt / 11)) * 0.35
    L += air; R += np.roll(air, 900)
    k = r.uniform(1, 4)
    while k < dur - 1:
        f = scale[r.integers(len(scale))]; s = note(f, min(6, dur - k), r.uniform(.5, 1)) * 0.55
        a0 = int(k * SR); e = min(n, a0 + len(s)); pan = r.uniform(.3, .7)
        L[a0:e] += s[:e - a0] * (1 - pan); R[a0:e] += s[:e - a0] * pan
        if r.random() < .35 and k + 0.6 < dur - 1:
            s2 = note(scale[r.integers(len(scale))], min(5, dur - k - .6), .6) * .45; a1 = int((k + .6) * SR); e2 = min(n, a1 + len(s2))
            L[a1:e2] += s2[:e2 - a1] * .5; R[a1:e2] += s2[:e2 - a1] * .5
        k += r.uniform(5, 9)
    if pulse:
        k = 0.5
        while k < dur - 0.5:
            for off, v in ((0, 1), (0.28, .6)):
                a0 = int((k + off) * SR); m_ = int(0.35 * SR); e = min(n, a0 + m_)
                th = np.sin(2 * np.pi * 52 * np.arange(e - a0) / SR) * np.exp(-np.arange(e - a0) / SR * 14) * v * 0.7
                L[a0:e] += th; R[a0:e] += th
            k += 1.6
    fade = np.minimum(1, np.minimum(tt / 2.0, (dur - tt) / 2.0)).clip(0, 1)
    return L * fade, R * fade

def waves(dur, seed=5):
    n = int(dur * SR); tt = np.arange(n) / SR; r = np.random.default_rng(seed)
    b = np.cumsum(r.normal(0, 1, n)); b -= lp(b, 0.5); b = lp(b, 900)
    b /= np.abs(b).max() + 1e-9
    env = 0.25 + 0.75 * np.sin(np.pi * ((tt / 7.5) % 1)) ** 2
    fade = np.minimum(1, np.minimum(tt / 2.5, (dur - tt) / 2.5)).clip(0, 1)
    return b * env * fade

def boom(v=1.0):
    n = int(2.5 * SR); tt = np.arange(n) / SR; r = np.random.default_rng(9)
    s = np.sin(2 * np.pi * (48 - 10 * tt) * tt) * np.exp(-tt * 2.2) + lp(r.normal(0, 1, n), 300) * np.exp(-tt * 8) * 0.6
    return s * v

def stamp():
    n = int(0.4 * SR); tt = np.arange(n) / SR; r = np.random.default_rng(13)
    s = np.sin(2 * np.pi * 90 * tt) * np.exp(-tt * 30) + bp(r.normal(0, 1, n), 1500, 6000) * np.exp(-tt * 60) * 0.5
    return s

def build_audio(voice, chapters, hits, stamps, total, wave_spans):
    n = int((total + 1) * SR)
    V = np.zeros(n)
    for t0, s in voice:
        a, sr = sf.read(s['file']); a = resample_poly(a, 2, 1) if sr == 24000 else a
        i0 = int(t0 * SR); e = min(n, i0 + len(a)); V[i0:e] += a[:e - i0]
    rms = np.sqrt(np.mean(V[V != 0] ** 2)); V *= 0.12 / rms   # ~ -18 dBFS rms
    # speech envelope for ducking
    act = np.zeros(n);
    for t0, s in voice: act[int(t0 * SR):int((t0 + s['dur']) * SR)] = 1
    k = int(0.5 * SR); env = np.convolve(act[::480], np.ones(k // 480) / (k // 480), 'same'); env = np.repeat(env, 480)[:n]
    if len(env) < n: env = np.pad(env, (0, n - len(env)))
    duck = 1.0 - 0.55 * np.clip(env, 0, 1)
    ML = np.zeros(n); MR = np.zeros(n)
    bounds = [c[1] for c in chapters] + [total]
    for idx, (ch, st) in enumerate(chapters):
        en = bounds[idx + 1] + 2.0; d = min(en, total + 0.5) - st
        l, r_ = music_segment(d, ch, 100 + ch); i0 = int(st * SR); e = min(n, i0 + len(l))
        ML[i0:e] += l[:e - i0]; MR[i0:e] += r_[:e - i0]
    m = max(np.abs(ML).max(), np.abs(MR).max()); ML *= 0.11 / m * 2.2; MR *= 0.11 / m * 2.2
    ML *= duck; MR *= duck
    FX = np.zeros(n)
    for (a0, b0) in wave_spans:
        w = waves(b0 - a0) * 0.10; i0 = int(a0 * SR); e = min(n, i0 + len(w)); FX[i0:e] += w[:e - i0]
    for th, v in hits:
        s = boom(v) * 0.22; i0 = int(th * SR); e = min(n, i0 + len(s)); FX[i0:e] += s[:e - i0]
    for ts in stamps:
        s = stamp() * 0.10; i0 = int(ts * SR); e = min(n, i0 + len(s)); FX[i0:e] += s[:e - i0]
    L = V + ML + FX; R = V + MR + FX
    out = np.stack([L, R], 1); out = np.tanh(out * 1.2) / 1.2
    sf.write(f"{P}/mix.wav", out.astype(np.float32), SR)

# ---------------- subtitles ----------------
def srt_time(x):
    h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s - int(s)) * 1000)) % 1000:03d}"

def build_srt(voice, path):
    out = []; k = 1
    for t0, s in voice:
        txt = s['text'].replace('*', ''); words = txt.split()
        chunks = []
        if len(words) <= 14: chunks = [txt]
        else:
            cur = []
            for w in words:
                cur.append(w)
                if (len(cur) >= 8 and w.endswith((',', ';', ':'))) or len(cur) >= 13: chunks.append(' '.join(cur)); cur = []
            if cur:
                if len(cur) <= 3 and chunks: chunks[-1] += ' ' + ' '.join(cur)
                else: chunks.append(' '.join(cur))
        tot = sum(len(c) for c in chunks); tt = t0
        for c in chunks:
            d = s['dur'] * len(c) / tot
            out.append(f"{k}\n{srt_time(tt)} --> {srt_time(tt + d)}\n{c}\n"); k += 1; tt += d
    open(path, 'w').write('\n'.join(out))

# ---------------- render ----------------
def zexpr(mot, N):
    c = "x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2'"
    if mot == 'in': return f"z='1+0.10*on/{N}':{c}"
    if mot == 'out': return f"z='1.10-0.10*on/{N}':{c}"
    if mot == 'r': return f"z='1.10':x='(iw-iw/zoom)*on/{N}':y='(ih-ih/zoom)/2'"
    if mot == 'l': return f"z='1.10':x='(iw-iw/zoom)*(1-on/{N})':y='(ih-ih/zoom)/2'"
    return f"z='1+0.035*on/{N}':{c}"

def render_clip(i, c, tagp):
    out = f"{P}/clips/c{i:04d}.mp4"
    if os.path.exists(out): return out
    N = c['frames']; dur = N / FPS
    ins = ['-loop', '1', '-framerate', str(FPS), '-i', c['img']]
    fc = [f"[0:v]zoompan={zexpr(c['mot'], N)}:d=1:s=1920x1080:fps={FPS},setsar=1,format=yuv420p[b0]"]
    last = 'b0'; k = 1
    ovs = list(c['ov'])
    if c.get('tag', True) is not False: ovs.append((tagp, 0, 1))
    for (p, f0, f1) in ovs:
        ins += ['-loop', '1', '-framerate', str(FPS), '-i', p]
        a0 = f0 * dur; a1 = f1 * dur
        fo = f",fade=t=out:st={max(a0, a1 - 0.35):.3f}:d=0.35:alpha=1" if f1 < 0.999 else ''
        fc.append(f"[{k}:v]format=rgba,fade=t=in:st={a0:.3f}:d=0.4:alpha=1{fo}[o{k}]")
        fc.append(f"[{last}][o{k}]overlay=0:0:enable='gte(t,{a0:.3f})'[b{k}]"); last = f"b{k}"; k += 1
    if c.get('slide'):
        p, f0 = c['slide']; a0 = f0 * dur
        ins += ['-loop', '1', '-framerate', str(FPS), '-i', p]
        fc.append(f"[{last}][{k}:v]overlay=x='if(lt(t,{a0:.3f}),1920,if(lt(t,{a0 + 1.3:.3f}),1920*(1-(t-{a0:.3f})/1.3),0))':y=0[b{k}]"); last = f"b{k}"; k += 1
    fin = c.get('fin', 0.0); fout = c.get('fout', 0.0); fl = []
    if fin > 0: fl.append(f"fade=t=in:st=0:d={fin}")
    if fout > 0: fl.append(f"fade=t=out:st={max(0, dur - fout):.3f}:d={fout}")
    fc.append(f"[{last}]{','.join(fl) if fl else 'null'}[v]")
    cmd = ['ffmpeg', '-y', '-loglevel', 'error'] + ins + ['-filter_complex', ';'.join(fc), '-map', '[v]', '-frames:v', str(N),
           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23', '-pix_fmt', 'yuv420p', '-r', str(FPS), out]
    subprocess.run(cmd, check=True)
    return out

if __name__ == '__main__':
    stage = sys.argv[1]
    a = build_assets(); M = manifest(a)
    clips, voice, chapters, hits, stamps, total = timeline(a, M)
    # frame-accurate
    for c in clips:
        f0 = round(c['start'] * FPS); f1 = round((c['start'] + c['dur']) * FPS); c['frames'] = max(1, f1 - f0)
    for i, c in enumerate(clips):
        if c['img'].split('/')[-1].startswith('card_ch'):
            if i > 0: clips[i - 1]['fout'] = 0.6
            if i + 1 < len(clips): clips[i + 1]['fin'] = 0.6
    clips[0]['fin'] = 1.2; clips[-1]['fout'] = 2.0
    print('clips', len(clips), 'total', round(total, 1), 's =', round(total / 60, 2), 'min')
    if stage in ('audio', 'all'):
        cold = [c for c in clips if c['img'].endswith('el_beach.jpg')][0]
        sunset = [c for c in clips if 'beach_sunset' in c['img']][0]
        wave_spans = [(0, cold['start'] + cold['dur'] + 14), (sunset['start'], sunset['start'] + sunset['dur'] + 30)]
        build_audio(voice, chapters, hits, stamps, total, wave_spans)
        build_srt(voice, f"{P}/subtitulos.srt"); print('audio ok')
    if stage in ('render', 'all'):
        os.makedirs(f"{P}/clips", exist_ok=True)
        from concurrent.futures import ThreadPoolExecutor
        tagp = a['tag']
        with ThreadPoolExecutor(int(sys.argv[2]) if len(sys.argv) > 2 else 4) as ex:
            list(ex.map(lambda ic: render_clip(ic[0], ic[1], tagp), enumerate(clips)))
        with open(f"{P}/clips/list.txt", 'w') as f:
            for i in range(len(clips)): f.write(f"file 'c{i:04d}.mp4'\n")
        print('render ok')
    json.dump([{k: v for k, v in c.items() if k in ('img', 'start', 'dur', 'frames', 'mot')} for c in clips], open(f"{P}/timeline.json", 'w'), indent=0)

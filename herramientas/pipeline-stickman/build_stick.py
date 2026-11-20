import json, os, sys, subprocess, math
import numpy as np, soundfile as sf, cairo
from scipy.signal import butter, sosfilt, resample_poly
S_ = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, S_)
from beats import BEATS
import engine as E
import scenes as SC

FPS = 24
sents = json.load(open(f"{S_}/sentences.json"))
byb = {}
for s in sents: byb.setdefault(s['beat'], []).append(s)
LEAD, GAP, TAIL = 0.35, 0.38, 0.95

def timeline():
    t = 0.0; out = []; voice = []
    for i, (sc, p, txt) in enumerate(BEATS):
        if not txt:
            d = p.get('dur', 3.0)
        else:
            tt = LEAD
            for s in byb[i]:
                voice.append((t + tt, s)); tt += s['dur'] + GAP
            d = tt - GAP + TAIL
        f0 = round(t * FPS); f1 = round((t + d) * FPS)
        out.append(dict(i=i, scene=sc, p=p, start=t, dur=d, frames=f1 - f0)); t += d
    return out, voice, t

BGARR = None
def render_beat(b):
    global BGARR
    out = f"{S_}/clips/b{b['i']:03d}.mp4"
    if os.path.exists(out): return out
    if BGARR is None: BGARR = E.paper_bg()
    W, H = E.W, E.H
    arr = np.zeros((H, W, 4), np.uint8)
    surf = cairo.ImageSurface.create_for_data(memoryview(arr), cairo.FORMAT_RGB24, W, H, W * 4)
    proc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                             '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', '-r', str(FPS), out], stdin=subprocess.PIPE)
    fn = SC.SCENES[b['scene']]; N = b['frames']; d = N / FPS
    for f in range(N):
        t = f / FPS
        np.copyto(arr, BGARR)
        c = cairo.Context(surf)
        z = 1.0 + 0.035 * E.ease(t / max(d, 0.1)) if b['scene'] not in ('chapter', 'title', 'counter', 'money_counter', 'end_screen') else 1.0
        c.translate(W / 2, H / 2); c.scale(z, z); c.translate(-W / 2, -H / 2)
        fn(c, t, d, b['p'])
        surf.flush()
        proc.stdin.write(arr.tobytes())
    proc.stdin.close(); proc.wait()
    return out

# ---------------- audio ----------------
SR = 48000
def lp(x, fc): return sosfilt(butter(2, fc, 'low', fs=SR, output='sos'), x)
def hp(x, fc): return sosfilt(butter(2, fc, 'high', fs=SR, output='sos'), x)
def env(n, a=0.004, r=8.0):
    tt = np.arange(n) / SR; return np.minimum(1, tt / a) * np.exp(-tt * r)

def music(total, chapters):
    bpm = 96; beat = 60 / bpm; n = int((total + 2) * SR); L = np.zeros(n); R = np.zeros(n)
    rng = np.random.default_rng(1)
    roots = [55.0, 65.41, 73.42, 82.41, 98.0]   # A minor pentatonic-ish
    def mode_at(tsec):
        m = 'full'
        for (st, md) in chapters:
            if tsec >= st: m = md
        return m
    nb = int(total / beat) + 2
    for k in range(nb):
        t0 = k * beat; md = mode_at(t0); i0 = int(t0 * SR)
        if i0 >= n: break
        bar_pos = k % 4
        # kick
        if md in ('full',) and bar_pos in (0, 2):
            m_ = int(0.35 * SR); tt = np.arange(m_) / SR; s = np.sin(2 * np.pi * (55 + 90 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 9) * 0.9
            e = min(n, i0 + m_); L[i0:e] += s[:e - i0]; R[i0:e] += s[:e - i0]
        # snap
        if md in ('full', 'calm') and bar_pos in (1, 3):
            m_ = int(0.2 * SR); s = hp(rng.normal(0, 1, m_), 1800) * env(m_, 0.002, 28) * (0.35 if md == 'full' else 0.18)
            e = min(n, i0 + m_); L[i0:e] += s[:e - i0]; R[i0:e] += s[:e - i0]
        # hats (8ths)
        if md != 'sad':
            for h in range(2):
                j0 = int((t0 + h * beat / 2) * SR); m_ = int(0.06 * SR)
                s = hp(rng.normal(0, 1, m_), 7000) * env(m_, 0.001, 70) * (0.12 if h else 0.08)
                e = min(n, j0 + m_); L[j0:e] += s[:e - j0] * 0.7; R[j0:e] += s[:e - j0]
        # bass (walking 8ths pattern)
        pat = [0, 0, 2, 3, 0, 4, 3, 2]
        for h in range(2):
            j0 = int((t0 + h * beat / 2) * SR); m_ = int(beat / 2 * SR * 0.95)
            f = roots[pat[(k * 2 + h) % 8]]
            tt = np.arange(m_) / SR
            s = (np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(2 * np.pi * 2 * f * tt)) * env(m_, 0.005, 5) * (0.30 if md != 'sad' else 0.22)
            e = min(n, j0 + m_); L[j0:e] += s[:e - j0]; R[j0:e] += s[:e - j0]
        # pluck stabs every 2 bars
        if k % 8 == 0 or (md == 'sad' and k % 4 == 0):
            m_ = int(2.5 * SR); tt = np.arange(m_) / SR
            chord = [220.0, 261.63, 329.63] if (k // 8) % 2 == 0 else [196.0, 246.94, 293.66]
            s = sum(np.sign(np.sin(2 * np.pi * f * tt)) * 0.3 + np.sin(2 * np.pi * f * tt) for f in chord)
            s = lp(s, 1800) * env(m_, 0.003, 2.2) * 0.10
            e = min(n, i0 + m_); L[i0:e] += s[:e - i0] * 0.8; R[i0:e] += s[:e - i0]
    return L, R

def sfx_whoosh():
    m_ = int(0.45 * SR); tt = np.arange(m_) / SR; rng = np.random.default_rng(3)
    s = rng.normal(0, 1, m_); s = lp(s, 2500) * np.sin(np.pi * tt / tt[-1]) ** 2
    return s * 0.10
def sfx_pop():
    m_ = int(0.12 * SR); tt = np.arange(m_) / SR
    return np.sin(2 * np.pi * (500 + 900 * tt / tt[-1]) * tt) * env(m_, 0.002, 30) * 0.12
def sfx_thump():
    m_ = int(0.5 * SR); tt = np.arange(m_) / SR
    return np.sin(2 * np.pi * 70 * tt) * np.exp(-tt * 14) * 0.45
def sfx_siren(dur):
    m_ = int(dur * SR); tt = np.arange(m_) / SR
    f = np.where((tt * 1.4) % 1 < 0.5, 660, 880); ph = np.cumsum(2 * np.pi * f / SR)
    return np.sin(ph) * 0.05 * np.minimum(1, np.minimum(tt / 0.5, (dur - tt) / 0.8)).clip(0, 1)
def sfx_ding():
    m_ = int(1.5 * SR); tt = np.arange(m_) / SR
    return (np.sin(2 * np.pi * 1320 * tt) + 0.5 * np.sin(2 * np.pi * 2640 * tt)) * np.exp(-tt * 4) * 0.08

def build_audio(tl, voice, total):
    n = int((total + 1.5) * SR); V = np.zeros(n)
    for t0, s in voice:
        a, sr = sf.read(s['file']); a = resample_poly(a, 2, 1)
        i0 = int(t0 * SR); e = min(n, i0 + len(a)); V[i0:e] += a[:e - i0]
    V *= 0.13 / np.sqrt(np.mean(V[V != 0] ** 2))
    chap_modes = {1: 'full', 2: 'full', 3: 'calm', 4: 'full', 5: 'calm', 6: 'sad', 7: 'calm'}
    chapters = [(0.0, 'full')]
    for b in tl:
        if b['scene'] == 'chapter': chapters.append((b['start'], chap_modes[b['p']['n']]))
    ML, MR = music(total, chapters)
    ML, MR = ML[:n], MR[:n]
    if len(ML) < n: ML = np.pad(ML, (0, n - len(ML))); MR = np.pad(MR, (0, n - len(MR)))
    act = np.zeros(n)
    for t0, s in voice: act[int(t0 * SR):int((t0 + s['dur']) * SR)] = 1
    k = 480; a2 = act[::k]; w = 25; sm = np.convolve(a2, np.ones(w) / w, 'same'); duck = np.repeat(1 - 0.6 * sm, k)[:n]
    if len(duck) < n: duck = np.pad(duck, (0, n - len(duck)), constant_values=1)
    m = max(np.abs(ML).max(), 1e-6); g = 0.30 / m
    ML *= g * duck; MR *= g * duck
    fade = np.ones(n); fe = int(3 * SR); fade[-fe:] = np.linspace(1, 0, fe); ML *= fade; MR *= fade
    FX = np.zeros(n)
    def add(s, t0):
        i0 = int(t0 * SR); e = min(n, i0 + len(s)); FX[i0:e] += s[:e - i0]
    for b in tl:
        add(sfx_whoosh(), max(0, b['start'] - 0.2))
        if b['scene'] in ('stamp', 'counter', 'title', 'chapter'): add(sfx_thump(), b['start'] + 0.3)
        if b['scene'] == 'bank_police' and b['p'].get('siren'): add(sfx_siren(b['dur']), b['start'])
        if b['scene'] in ('money_counter', 'loot'): add(sfx_ding(), b['start'] + 0.4)
        if b['scene'] in ('gang_member', 'bulb', 'evidence', 'hostages_free', 'arrests'): add(sfx_pop(), b['start'] + 0.35)
    L = V + ML + FX; R = V + MR + FX
    out = np.tanh(np.stack([L, R], 1) * 1.1) / 1.1
    sf.write(f"{S_}/mix.wav", out.astype(np.float32), SR)

def srt(voice, path):
    def ts(x):
        h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
        return f"{h:02d}:{m:02d}:{int(s):02d},{int((s - int(s)) * 1000):03d}"
    out = []; k = 1
    for t0, s in voice:
        words = s['text'].split(); chunks = []; cur = []
        for w in words:
            cur.append(w)
            if (len(cur) >= 7 and w.endswith((',', ';', ':'))) or len(cur) >= 11: chunks.append(' '.join(cur)); cur = []
        if cur:
            if len(cur) <= 2 and chunks: chunks[-1] += ' ' + ' '.join(cur)
            else: chunks.append(' '.join(cur))
        tot = sum(len(c) for c in chunks); tt = t0
        for ch in chunks:
            dd = s['dur'] * len(ch) / tot; out.append(f"{k}\n{ts(tt)} --> {ts(tt + dd)}\n{ch}\n"); k += 1; tt += dd
    open(path, 'w').write('\n'.join(out))

if __name__ == '__main__':
    tl, voice, total = timeline()
    print('beats', len(tl), 'total', round(total, 1), 's', round(total / 60, 2), 'min', flush=True)
    stage = sys.argv[1]
    if stage == 'preview':
        import random
        os.makedirs(f"{S_}/prev", exist_ok=True)
        W, H = E.W, E.H; bg = E.paper_bg()
        ids = [int(x) for x in sys.argv[2].split(',')] if len(sys.argv) > 2 else range(len(tl))
        for i in ids:
            b = tl[i]; arr = bg.copy(); surf = cairo.ImageSurface.create_for_data(memoryview(arr), cairo.FORMAT_RGB24, W, H, W * 4)
            c = cairo.Context(surf); d = b['frames'] / FPS
            SC.SCENES[b['scene']](c, d * 0.7, d, b['p']); surf.flush()
            from PIL import Image
            Image.fromarray(arr[..., [2, 1, 0]]).resize((480, 270)).save(f"{S_}/prev/p{i:03d}.jpg")
        print('preview ok')
    if stage == 'audio':
        build_audio(tl, voice, total); srt(voice, f"{S_}/subtitulos.srt"); print('audio ok')
    if stage == 'render':
        os.makedirs(f"{S_}/clips", exist_ok=True)
        from multiprocessing import Pool
        with Pool(int(sys.argv[2]) if len(sys.argv) > 2 else 4) as pool:
            for r in pool.imap_unordered(render_beat, sorted(tl, key=lambda b: -b['frames'])): pass
        with open(f"{S_}/clips/list.txt", 'w') as f:
            for b in tl: f.write(f"file 'b{b['i']:03d}.mp4'\n")
        print('render ok')
    json.dump([{k: v for k, v in b.items() if k != 'p'} for b in tl], open(f"{S_}/timeline.json", 'w'))

"""Monta el corto TEMPERATURA: planos, gradación de color, música sintetizada, narración y subtítulos."""
import os, subprocess, wave
import numpy as np

B = "/home/user/Youtube-/corto_temperatura"
TMP = "/tmp/claude-0/-home-user-Youtube-/ced2aa00-2ff9-5b44-8233-217327aadf3c/scratchpad/temp"
os.makedirs(TMP, exist_ok=True)
IMG, ST, AU, FONTS = f"{B}/img", f"{B}/stock", f"{B}/audio", f"{B}/fonts"
W, H, FPS = 1920, 1080, 30
ENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS), "-an"]
GRAIN = "noise=alls=9:allf=t"
VIG = "vignette=PI/4.2"

# --- gradaciones de color ---
COLD = "colorbalance=rs=-0.18:gs=-0.02:bs=0.22:rm=-0.12:bm=0.14:rh=-0.05:bh=0.08,eq=saturation=0.85:contrast=1.05"
TEALORANGE = "colorbalance=rs=-0.2:gs=0.02:bs=0.25:rh=0.25:gh=0.05:bh=-0.25,eq=saturation=1.25:contrast=1.1"
HOT = "colorbalance=rs=0.3:gs=-0.05:bs=-0.3:rm=0.25:bm=-0.25:rh=0.2:bh=-0.2,eq=saturation=1.6:contrast=1.25"
GRAY = "hue=s=0,eq=contrast=1.12:brightness=-0.04:gamma=0.95"


def run(args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


def still(path, dur, out, grade, z0=1.0, z1=1.12, cx=0.5, cy=0.5, crop=None, extra=""):
    """Plano a partir de imagen fija con movimiento de cámara lento (Ken Burns)."""
    n = int(dur * FPS)
    pre = f"crop={crop}," if crop else ""
    zexpr = f"{z0}+({z1}-{z0})*on/{n}"
    vf = (f"{pre}scale=3840:2160,zoompan=z='{zexpr}':x='(iw-iw/zoom)*{cx}':y='(ih-ih/zoom)*{cy}':"
          f"d={n}:s={W}x{H}:fps={FPS},{grade}{extra},{VIG},{GRAIN}")
    run(["-loop", "1", "-i", path, "-t", str(dur), "-vf", vf, *ENC, out])


def clip(path, ss, dur, out, grade, speed=1.0, extra="", reverse=False):
    vf = f"setpts={1/speed}*PTS," if speed != 1 else ""
    if reverse:
        vf += "scale=1280:-2,reverse,"
    vf += f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},{grade}{extra},{VIG},{GRAIN}"
    run(["-ss", str(ss), "-t", str(dur * speed), "-i", path, "-vf", vf, "-t", str(dur), *ENC, out])


def fades(inp, out, fin=0.0, fout=0.0, dur=None, white_out=False):
    f = []
    if fin: f.append(f"fade=in:st=0:d={fin}")
    if fout:
        col = ":color=white" if white_out else ""
        f.append(f"fade=out:st={dur - fout}:d={fout}{col}")
    if not f:
        os.replace(inp, out); return
    run(["-i", inp, "-vf", ",".join(f), *ENC, out])


shots = []   # (archivo, duración)
lines = []   # (índice de narración, tiempo absoluto)
T = [0.0]


def add(name, dur, maker, narr=(), fin=0.0, fout=0.0, white_out=False):
    raw, out = f"{TMP}/{name}_raw.mp4", f"{TMP}/{name}.mp4"
    if not os.path.exists(out):
        maker(raw)
        fades(raw, out, fin, fout, dur, white_out)
    for idx, off in narr:
        lines.append((idx, T[0] + off))
    shots.append((out, dur)); T[0] += dur


A1, A2, A3 = f"{IMG}/a1_chica_azul.png", f"{IMG}/a2_ciudad.png", f"{IMG}/a3_scroll_fuego.png"
CORM = f"{FONTS}/Cormorant-Light.ttf"

# ---------------- S0 TÍTULO ----------------
add("s00", 7, lambda o: run(["-f", "lavfi", "-i", f"color=black:s={W}x{H}:r={FPS}:d=7", "-vf",
    f"drawtext=fontfile={CORM}:text='T E M P E R A T U R A':fontsize=92:fontcolor=white:x=(w-tw)/2:y=(h-th)/2:"
    f"alpha='if(lt(t,1.5),0,if(lt(t,3.5),(t-1.5)/2,if(lt(t,5.5),1,max(0,(7-t)/1.5))))',{GRAIN}", *ENC, o]))

# ---------------- ACTO I: FRÍO ----------------
add("s01", 9, lambda o: still(A2, 9, o, COLD, 1.0, 1.15, 0.5, 0.6), [(0, 1.5)], fin=1.5)
add("s02", 9, lambda o: still(A1, 9, o, COLD, 1.05, 1.2, 0.25, 0.4), [(1, 1.0)], fin=0.6)
add("s03", 5, lambda o: still(A3, 5, o, COLD.replace("saturation=0.85", "saturation=1.1"), 1.0, 1.08, 0.4, 0.4), [(2, 0.5)])
add("s04", 1.2, lambda o: clip(f"{ST}/nightfire.mp4", 11, 1.2, o, TEALORANGE))
add("s05", 4.8, lambda o: still(A3, 4.8, o, COLD.replace("saturation=0.85", "saturation=1.1"), 1.15, 1.25, 0.6, 0.3), [(3, 0.3)])
add("s06", 1.0, lambda o: clip(f"{ST}/hellfire.mp4", 40, 1.0, o, TEALORANGE))
add("s07", 4.0, lambda o: still(A3, 4.0, o, COLD.replace("saturation=0.85", "saturation=1.1"), 1.3, 1.4, 0.5, 0.5), [(4, 0.3)])
add("s08", 7, lambda o: still(A1, 7, o, COLD, 1.0, 1.08, 0.5, 0.5, crop="640:360:180:40"), [(5, 0.8)], fout=0.4)

# ---------------- ACTO II: INVASIÓN NARANJA ----------------
# gradiente naranja que entra desde la ventana (derecha) y se funde en modo "screen"
grad = f"{TMP}/grad.png"
gx = np.linspace(0, 1, 3840)
g = np.clip((gx - 0.5) * 2, 0, 1) ** 1.6
rgb = np.stack([g * 255, g * 95, g * 10], -1)[None].repeat(H, 0).astype(np.uint8)
from PIL import Image
Image.fromarray(rgb).save(grad)


def s09(o):
    n = 9
    run(["-loop", "1", "-i", A1, "-loop", "1", "-i", grad, "-filter_complex",
         f"[0]scale=3840:2160,zoompan=z='1.0+0.08*on/{n*FPS}':x='(iw-iw/zoom)*0.3':y='(ih-ih/zoom)*0.4':d={n*FPS}:s={W}x{H}:fps={FPS},{COLD}[a];"
         f"[1]crop={W}:{H}:x='min(1920,max(0,1920*t/{n-1}))':y=0,fps={FPS},format=gbrp[b];"
         f"[a]format=gbrp[a2];[a2][b]blend=all_mode=screen,format=yuv420p,{VIG},{GRAIN}",
         "-t", str(n), *ENC, o])


add("s09", 9, s09, [(6, 1.5)], fin=0.4)
add("s10", 8, lambda o: clip(f"{ST}/nightfire.mp4", 10, 8, o, TEALORANGE, speed=0.8), [(7, 1.0)])


def s11(o):
    subprocess.run(["python3", "-I", f"{B}/embers_room.py", A1, o, "9"], check=True, stderr=subprocess.DEVNULL)


add("s11", 9, s11, [(8, 1.0)])

# ---------------- ACTO III: DISTORSIÓN ----------------


def s12(o):
    n = 7
    run(["-ss", "28", "-i", f"{ST}/hellfire.mp4", "-loop", "1", "-i", A1, "-filter_complex",
         f"[0]setpts=1.3*PTS,scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},{HOT},format=gbrp[a];"
         f"[1]scale={W}:{H},{HOT},format=gbrp[b];[a][b]blend=all_mode=screen:all_opacity=0.55,format=yuv420p,"
         f"rotate='0.025*sin(2*PI*t/1.7)':fillcolor=black,scale=2112:1188,crop={W}:{H},lagfun=decay=0.93,{VIG},{GRAIN}",
         "-t", str(n), *ENC, o])


add("s12", 7, s12, [(9, 0.8)])
add("s13", 8, lambda o: clip(f"{ST}/iceclock.mp4", 4, 8, o, HOT + ",hue=h=-8", speed=3.2, reverse=True,
                              extra=",rotate='0.015*sin(2*PI*t/2.3)':fillcolor=black,scale=2050:1153,crop=1920:1080"), [(10, 0.8)])
add("s14", 3.5, lambda o: clip(f"{ST}/embers.mp4", 40, 3.5, o, HOT, extra=",eq=brightness='0.0':contrast=1.4,zoompan=z='1+0.1*on/105':d=1:s=1920x1080:fps=30"),
    fout=0.8, white_out=True)
add("s15", 1.5, lambda o: run(["-f", "lavfi", "-i", f"color=black:s={W}x{H}:r={FPS}:d=1.5", *ENC, o]))

# ---------------- ACTO IV: GRIS Y VERDE ----------------
add("s16", 10, lambda o: clip(f"{ST}/gillard.mp4", 0, 10, o, GRAY, speed=0.9), [(11, 1.5), (12, 7.3)], fin=1.5)


def s17(o):
    subprocess.run(["python3", "-I", f"{B}/selective_green.py", f"{ST}/seedling.mp4", o, "9.4"], check=True,
                   stderr=subprocess.DEVNULL)


add("s17", 9.4, s17, [(13, 2.0)])
add("s18", 10, lambda o: clip(f"{ST}/tree.mp4", 0, 10, o, "eq=saturation=0.45:contrast=1.05,colorbalance=rh=0.08:bh=-0.08", speed=0.7),
    [(14, 0.8), (15, 5.0)], fout=1.5)

# ---------------- CIERRE ----------------
INTER = f"{FONTS}/Inter-Regular.ttf"
add("s19", 6, lambda o: run(["-f", "lavfi", "-i", f"color=black:s={W}x{H}:r={FPS}:d=6", "-vf",
    f"drawtext=fontfile={CORM}:text='El cambio climático no es una noticia que se desliza.':fontsize=58:fontcolor=white:x=(w-tw)/2:y=h/2-70:alpha='min(1,t/1.2)*min(1,(6-t)/0.8)',"
    f"drawtext=fontfile={CORM}:text='Es nuestra casa.':fontsize=58:fontcolor=0x7CFC6A:x=(w-tw)/2:y=h/2+20:alpha='if(lt(t,2),0,min(1,(t-2)/1))*min(1,(6-t)/0.8)'",
    *ENC, o]))
cred = ("Narración\\: voz neuronal es-BO (Sofía)   ·   Imágenes de la protagonista\\: generadas con IA (ElevenLabs)\n"
        "Material de archivo (CC BY)\\: Mário J.R. Matos · CC BY Nature · Gillard Forest Service Road (CC0)\n"
        "Música y diseño sonoro\\: originales")
open(f"{TMP}/cred.txt", "w").write(cred.replace("\\:", ":"))
add("s20", 9, lambda o: run(["-f", "lavfi", "-i", f"color=black:s={W}x{H}:r={FPS}:d=9", "-vf",
    f"drawtext=fontfile={CORM}:text='T E M P E R A T U R A':fontsize=96:fontcolor=white:x=(w-tw)/2:y=h/2-160:alpha='min(1,t/1.5)*min(1,(9-t)/1.5)',"
    f"drawtext=fontfile={INTER}:textfile={TMP}/cred.txt:fontsize=26:line_spacing=14:fontcolor=0xBBBBBB:x=(w-tw)/2:y=h/2+10:alpha='min(1,max(0,t-1)/1.5)*min(1,(9-t)/1.5)'",
    *ENC, o]))

TOTAL = T[0]
print("duración total", TOTAL)

# ---------------- VIDEO CONCATENADO ----------------
lst = f"{TMP}/list.txt"
open(lst, "w").write("".join(f"file '{p}'\n" for p, _ in shots))
run(["-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", f"{TMP}/video.mp4"])

# ---------------- MÚSICA Y DISEÑO SONORO (sintetizado) ----------------
SR = 44100
N = int(TOTAL * SR)
t = np.arange(N) / SR
mus = np.zeros((N, 2))
rng = np.random.default_rng(7)
starts = {}
acc = 0.0
for (p, d) in shots:
    starts[os.path.basename(p)[:3]] = acc; acc += d
a1s, a2s, a3s, a3e, a4s = starts["s01"], starts["s09"], starts["s12"], starts["s15"], starts["s16"]


def env(t0, t1, fi=2.0, fo=2.0):
    e = np.zeros(N); i0, i1 = int(t0 * SR), int(t1 * SR)
    x = t[i0:i1] - t0
    e[i0:i1] = np.minimum(1, x / fi) * np.minimum(1, (t1 - t0 - x) / fo)
    return np.clip(e, 0, 1)


def lp(x, a):  # filtro pasa-bajos simple
    y = np.empty_like(x); acc_ = 0.0
    for i in range(len(x)):
        acc_ += a * (x[i] - acc_); y[i] = acc_
    return y


def noise_lp(a, seconds):
    # ruido filtrado (calculado a menor resolución y luego interpolado, por velocidad)
    sr2 = 11025; n2 = int(seconds * sr2)
    x = rng.standard_normal(n2)
    from scipy.signal import lfilter  # noqa
    return x


try:
    from scipy.signal import butter, lfilter
    HAVE_SCIPY = True
except Exception:
    HAVE_SCIPY = False


def filt(x, f, kind="low"):
    if HAVE_SCIPY:
        b, a = butter(2, f / (SR / 2), btype=kind); return lfilter(b, a, x)
    k = int(SR / f); return np.convolve(x, np.ones(k) / k, mode="same") if kind == "low" else x - np.convolve(x, np.ones(k) / k, mode="same")


# Acto I: pad frío (La menor) + lluvia
pad = np.zeros(N)
for f0 in [110.0, 164.81, 261.63, 392.0, 493.88]:
    pad += np.sin(2 * np.pi * f0 * t + 0.3 * np.sin(2 * np.pi * 0.07 * t)) + 0.5 * np.sin(2 * np.pi * f0 * 1.003 * t)
pad *= 0.035 * (0.75 + 0.25 * np.sin(2 * np.pi * 0.11 * t))
e1 = env(a1s - 1, a3s + 1, 4, 3)
mus[:, 0] += pad * e1; mus[:, 1] += np.roll(pad, 300) * e1
rain = filt(rng.standard_normal(N), 3500) - filt(rng.standard_normal(N), 400) * 0.3
rain = filt(rain, 300, "high") * 0.045
er = env(a1s, a2s + 4, 3, 4)
mus[:, 0] += rain * er; mus[:, 1] += np.roll(rain, 997) * er

# whooshes en los cortes rápidos (flashes)
for k in ["s04", "s06"]:
    s0 = starts[k] - 0.25
    i0 = int(s0 * SR); L = int(0.8 * SR)
    w = filt(rng.standard_normal(L), 2000) * np.hanning(L) * 0.35
    mus[i0:i0 + L, :] += w[:, None]

# Acto II: dron grave que sube + crepitar de fuego
drone_f = 55 * (1 + 0.5 * np.clip((t - a2s) / (a3e - a2s), 0, 1))
ph = 2 * np.pi * np.cumsum(drone_f) / SR
drone = (np.sin(ph) + 0.4 * np.sin(2 * ph) + 0.2 * np.sin(3.01 * ph)) * 0.09
e2 = env(a2s, a3e, 3, 0.05)
mus += (drone * e2)[:, None]
crack = np.zeros(N)
pos = rng.uniform(a2s, a3e, 900)
for p in pos:
    i = int(p * SR); L = rng.integers(60, 400)
    if i + L < N:
        crack[i:i + L] += rng.standard_normal(L) * np.exp(-np.arange(L) / (L / 4)) * rng.uniform(0.2, 1)
crack = filt(crack, 800, "high") * 0.18 * np.clip((t - a2s) / 15, 0, 1)
mus[:, 0] += crack * e2; mus[:, 1] += np.roll(crack, 211) * e2

# latido de corazón (intro suave y Acto III acelerando)


def heartbeat(t0, t1, bpm0, bpm1, gain):
    tt = t0
    while tt < t1:
        frac = (tt - t0) / (t1 - t0); bpm = bpm0 + (bpm1 - bpm0) * frac
        for off, amp in [(0, 1.0), (0.18, 0.7)]:
            i = int((tt + off) * SR); L = int(0.16 * SR)
            if i + L < N:
                x = np.arange(L) / SR
                mus[i:i + L, :] += (np.sin(2 * np.pi * 52 * x) * np.exp(-x * 28) * amp * gain)[:, None]
        tt += 60 / bpm


heartbeat(1.0, 6.5, 55, 55, 0.35)
heartbeat(a3s - 2, a3e - 1.6, 75, 150, 0.55)
# subida de ruido (tensión) que corta en seco
riser = filt(rng.standard_normal(N), 1200) * np.clip((t - a3s) / (a3e - 1.5 - a3s), 0, 1) ** 2 * 0.35
riser[int((a3e - 1.5) * SR):] = 0
mus += riser[:, None]

# Acto IV: notas suaves en Do mayor tipo piano + viento
notes = [261.63, 329.63, 392.0, 440.0, 392.0, 329.63, 293.66, 329.63, 392.0, 523.25, 440.0, 392.0]
k = 0; tt = a4s + 1.0
while tt < TOTAL - 4:
    f0 = notes[k % len(notes)]; i = int(tt * SR); L = int(3.5 * SR)
    if i + L < N:
        x = np.arange(L) / SR
        tone = (np.sin(2 * np.pi * f0 * x) + 0.35 * np.sin(4 * np.pi * f0 * x) + 0.12 * np.sin(6 * np.pi * f0 * x)) * np.exp(-x * 1.4)
        tone[: int(0.01 * SR)] *= np.linspace(0, 1, int(0.01 * SR))
        mus[i:i + L, 0] += tone * 0.07; mus[i:i + L, 1] += tone * 0.07
        # eco
        d = int(0.42 * SR)
        if i + d + L < N:
            mus[i + d:i + d + L, 1] += tone * 0.03; mus[i + d:i + d + L, 0] += tone * 0.015
    tt += 1.6 if k % 4 != 3 else 3.2; k += 1
padc = np.zeros(N)
for f0 in [130.81, 196.0, 329.63]:
    padc += np.sin(2 * np.pi * f0 * t + 0.2 * np.sin(2 * np.pi * 0.05 * t))
e4 = env(a4s + 2, TOTAL, 6, 5)
mus += (padc * 0.022 * e4)[:, None]
wind = filt(filt(rng.standard_normal(N), 700), 120, "high") * 0.05 * (0.6 + 0.4 * np.sin(2 * np.pi * 0.09 * t))
ew = env(a4s, a4s + 30, 3, 6)
mus[:, 0] += wind * ew; mus[:, 1] += np.roll(wind, 555) * ew

mus = np.tanh(mus * 1.2) * 0.8
with wave.open(f"{TMP}/music.wav", "wb") as wf:
    wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
    wf.writeframes((np.clip(mus, -1, 1) * 32767).astype("<i2").tobytes())

# ---------------- NARRACIÓN + SUBTÍTULOS ----------------
texts = open(f"{AU}/lines.txt").read().split("\n")


def dur_of(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]).decode())


inputs, fl = [], []
for j, (idx, at) in enumerate(lines):
    inputs += ["-i", f"{AU}/l{idx:02d}.mp3"]
    ms = int(at * 1000)
    fl.append(f"[{j}]aresample=44100,aecho=0.8:0.5:60:0.12,volume=1.6,adelay={ms}|{ms},apad=whole_dur={TOTAL}[n{j}]")
mix = "".join(f"[n{j}]" for j in range(len(lines)))
run([*inputs, "-filter_complex", ";".join(fl) + f";{mix}amix=inputs={len(lines)}:normalize=0,atrim=0:{TOTAL}[out]",
     "-map", "[out]", "-ac", "2", f"{TMP}/narr.wav"])


def ts(x):
    h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f"{h}:{m:02d}:{s:05.2f}"


ass = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "",
       "[V4+ Styles]",
       "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
       "Style: Sub,Inter,44,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0.5,0,1,2.2,1,2,120,120,70,1",
       "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
for idx, at in lines:
    d = dur_of(f"{AU}/l{idx:02d}.mp3")
    ass.append(f"Dialogue: 0,{ts(at + 0.05)},{ts(at + d + 0.25)},Sub,,0,0,0,,{{\\fad(150,200)}}{texts[idx]}")
open(f"{TMP}/subs.ass", "w").write("\n".join(ass))

out = f"{B}/TEMPERATURA.mp4"
run(["-i", f"{TMP}/video.mp4", "-i", f"{TMP}/music.wav", "-i", f"{TMP}/narr.wav", "-filter_complex",
     f"[0]subtitles={TMP}/subs.ass:fontsdir={FONTS}[v];"
     f"[2]asplit[n1][n2];[1]volume=0.9[m];[m][n1]sidechaincompress=threshold=0.03:ratio=3:attack=20:release=500[md];"
     f"[md][n2]amix=inputs=2:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11,afade=t=out:st={TOTAL-2}:d=2[a]",
     "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "slow", "-b:v", "7M", "-maxrate", "9M", "-bufsize", "14M", "-pix_fmt", "yuv420p",
     "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", out])
print(out)

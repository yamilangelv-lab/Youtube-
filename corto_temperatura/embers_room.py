"""Brasas naranjas que flotan dentro del cuarto azul (contraste cálido-frío)."""
import subprocess, sys
import numpy as np

src, out, dur = sys.argv[1], sys.argv[2], float(sys.argv[3])
W, H, FPS = 1920, 1080, 30
N = int(dur * FPS)
COLD = "colorbalance=rs=-0.18:gs=-0.02:bs=0.22:rm=-0.12:bm=0.14:rh=-0.05:bh=0.08,eq=saturation=0.85:contrast=1.05"
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-loop", "1", "-i", src, "-vf",
                        f"scale=3840:2160,zoompan=z='1.1+0.06*on/{N}':x='(iw-iw/zoom)*0.25':y='(ih-ih/zoom)*0.45':d={N}:s={W}x{H}:fps={FPS},{COLD}",
                        "-frames:v", str(N), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                        "-i", "-", "-vf", "vignette=PI/4.2,noise=alls=9:allf=t", "-c:v", "libx264", "-crf", "18",
                        "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
rng = np.random.default_rng(3)
P = 260
# las brasas nacen sobre todo del lado de la ventana (derecha) y suben flotando hacia la izquierda
x = rng.uniform(800, 2000, P); y = rng.uniform(0, H + 200, P)
vx = rng.uniform(-70, -15, P); vy = rng.uniform(-120, -35, P)
size = rng.uniform(1.5, 5.5, P); ph = rng.uniform(0, 6.28, P); life0 = rng.uniform(0, 1, P)
# sprites de brillo
spr = {}
for s in range(1, 8):
    R = int(s * 5)
    yy, xx = np.mgrid[-R:R + 1, -R:R + 1]
    d2 = (xx ** 2 + yy ** 2) / (s ** 2)
    core = np.exp(-d2 * 1.4); glow = np.exp(-d2 / 6) * 0.35
    a = core + glow
    spr[s] = np.stack([a * 1.0, a * 0.45 + core * 0.35, a * 0.08 + core * 0.15], -1)
gx = np.linspace(0, 1, W)[None, :, None]
for f in range(N):
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3:
        break
    t = f / FPS
    img = np.frombuffer(buf, np.uint8).reshape(H, W, 3).astype(np.float32) / 255
    # luz cálida que crece desde la ventana
    k = min(1.0, t / dur) ** 1.3
    warm = np.clip((gx - 0.45) / 0.55, 0, 1) ** 1.5 * 0.6 * k
    img = 1 - (1 - img) * (1 - warm * np.array([1.0, 0.38, 0.05]))
    layer = np.zeros_like(img)
    px = x + vx * t + 25 * np.sin(ph + t * 1.3); py = (y + vy * t) % (H + 200) - 100
    flick = 0.6 + 0.4 * np.sin(ph * 3 + t * 9)
    fade = np.clip(t * 1.2 - life0 * 0.6, 0, 1)
    for i in range(P):
        s = max(1, min(7, int(round(size[i])))); R = s * 5
        cx, cy = int(px[i]), int(py[i])
        x0, y0, x1, y1 = cx - R, cy - R, cx + R + 1, cy + R + 1
        if x1 <= 0 or y1 <= 0 or x0 >= W or y0 >= H:
            continue
        sx0, sy0 = max(0, -x0), max(0, -y0)
        sx1, sy1 = (2 * R + 1) - max(0, x1 - W), (2 * R + 1) - max(0, y1 - H)
        layer[max(0, y0):min(H, y1), max(0, x0):min(W, x1)] += spr[s][sy0:sy1, sx0:sx1] * flick[i] * fade[i]
    img = 1 - (1 - img) * (1 - np.clip(layer, 0, 1))
    enc.stdin.write((np.clip(img, 0, 1) * 255).astype(np.uint8).tobytes())
enc.stdin.close(); enc.wait(); dec.terminate()

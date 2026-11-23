"""Deja solo el verde con color y convierte el resto a gris (contraste de cantidad)."""
import subprocess, sys
import numpy as np

src, out, dur = sys.argv[1], sys.argv[2], float(sys.argv[3])
W, H, FPS = 1920, 1080, 30
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-t", str(dur / 0.95),
                        "-vf", f"setpts=1.05*PTS,scale={W}:{H},fps={FPS}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                       stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                        "-i", "-", "-vf", "eq=contrast=1.08,vignette=PI/4.2,noise=alls=9:allf=t", "-t", str(dur),
                        "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
n = int(dur * FPS)
for _ in range(n):
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3:
        break
    f = np.frombuffer(buf, np.uint8).reshape(H, W, 3).astype(np.float32) / 255
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    mx, mn = f.max(-1), f.min(-1)
    sat = (mx - mn) / (mx + 1e-5)
    # tono: verde/amarillo-verde ~ 65-150 grados
    d = mx - mn + 1e-5
    hue = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    m = np.clip((hue - 55) / 12, 0, 1) * np.clip((160 - hue) / 15, 0, 1) * np.clip((sat - 0.25) / 0.2, 0, 1) * np.clip((mx - 0.12) / 0.1, 0, 1)
    gray = (0.299 * r + 0.587 * g + 0.114 * b)[..., None] * 0.92
    colored = np.clip(gray + (f - gray) * 1.35, 0, 1)
    res = gray * (1 - m[..., None]) + colored * m[..., None]
    enc.stdin.write((np.clip(res, 0, 1) * 255).astype(np.uint8).tobytes())
enc.stdin.close(); enc.wait(); dec.terminate()

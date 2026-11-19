#!/usr/bin/env python3
"""Encuentra los momentos más intensos de un VOD largo, sin verlo entero.

Señales:
  - Audio: picos de volumen respecto al nivel normal de los 2 minutos de alrededor (gritos, explosiones).
  - Chat de Twitch (opcional): picos de mensajes. Exporta el chat en JSON con TwitchDownloader.

Ejemplos:
  python momentos.py vod.mp4
  python momentos.py vod.mp4 --chat chat.json --top 15 --antes 20 --despues 15

Salida: tabla de candidatos y un momentos.csv con inicio/fin listos para clipear.py.
"""
import argparse
import csv
import json
import re
import statistics
import subprocess
import sys
from pathlib import Path


def hms(s):
    s = max(0, int(s))
    return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}"


def volumen_por_segundo(video):
    """RMS en dB de cada segundo de audio usando ffmpeg."""
    cmd = ["ffmpeg", "-nostats", "-i", str(video), "-vn", "-af",
           "aresample=16000,asetnsamples=16000,astats=metadata=1:reset=1,"
           "ametadata=print:key=lavfi.astats.Overall.RMS_level:file=-", "-f", "null", "-"]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    vals = []
    for m in re.finditer(r"RMS_level=(-?[\d.]+|-inf)", out):
        v = m.group(1)
        vals.append(-90.0 if v == "-inf" else max(-90.0, float(v)))
    if not vals:
        sys.exit("No se pudo leer el audio del video.")
    return vals


def picos_relativos(serie, ventana=60):
    """Cuánto sobresale cada segundo respecto a la mediana de su entorno."""
    res = []
    n = len(serie)
    for i in range(n):
        a, b = max(0, i - ventana), min(n, i + ventana)
        entorno = serie[a:b]
        med = statistics.median(entorno)
        disp = statistics.pstdev(entorno) or 1.0
        res.append((serie[i] - med) / disp)
    return res


def chat_por_segundo(ruta, n):
    data = json.loads(Path(ruta).read_text(encoding="utf-8"))
    comentarios = data.get("comments", data if isinstance(data, list) else [])
    cuenta = [0.0] * n
    for c in comentarios:
        t = c.get("content_offset_seconds")
        if t is not None and 0 <= int(t) < n:
            cuenta[int(t)] += 1
    # suavizar en ventanas de 10 s (el chat reacciona con retraso)
    return [sum(cuenta[max(0, i - 2):i + 8]) for i in range(n)]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--chat", help="JSON de chat de TwitchDownloader (opcional)")
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--separacion", type=int, default=60, help="segundos mínimos entre candidatos")
    ap.add_argument("--antes", type=int, default=15, help="segundos antes del pico")
    ap.add_argument("--despues", type=int, default=12, help="segundos después del pico")
    ap.add_argument("--minimo", type=float, default=1.5, help="score mínimo para considerar un pico")
    ap.add_argument("--csv", default="momentos.csv")
    a = ap.parse_args()

    print("Analizando audio (puede tardar unos minutos en VODs largos)…")
    vol = volumen_por_segundo(a.video)
    score = picos_relativos(vol)
    if a.chat:
        chat = chat_por_segundo(a.chat, len(vol))
        zc = picos_relativos(chat)
        score = [0.4 * s + 0.6 * c for s, c in zip(score, zc)]  # el chat es mejor señal que el audio

    orden = sorted(range(len(score)), key=lambda i: score[i], reverse=True)
    elegidos = []
    for i in orden:
        if score[i] < a.minimo:
            break
        if all(abs(i - j) >= a.separacion for j in elegidos):
            elegidos.append(i)
        if len(elegidos) >= a.top:
            break

    if not elegidos:
        sys.exit("No se encontraron picos claros. Prueba con --minimo 1.0 o añade el chat con --chat.")
    filas = []
    for rank, i in enumerate(elegidos, 1):
        ini, fin = max(0, i - a.antes), min(len(vol), i + a.despues)
        filas.append({"rank": rank, "pico": hms(i), "inicio": hms(ini), "fin": hms(fin), "score": round(score[i], 2)})

    print(f"\n{'#':>3}  {'pico':>8}  {'inicio':>8}  {'fin':>8}  score")
    for f in filas:
        print(f"{f['rank']:>3}  {f['pico']:>8}  {f['inicio']:>8}  {f['fin']:>8}  {f['score']}")
    with open(a.csv, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)
    print(f"\nGuardado en {a.csv}. Revisa cada candidato antes de clipearlo: la máquina sugiere, tú decides.")


if __name__ == "__main__":
    main()

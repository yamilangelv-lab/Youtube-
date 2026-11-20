#!/usr/bin/env python3
"""Convierte clips verticales (Shorts/TikTok) en encuadre horizontal 1920x1080 A PANTALLA COMPLETA,
sin barras ni fondo desenfocado. Elige el encuadre según el contenido (usa zonas.analizar):

  A) Cámara del streamer arriba + gameplay abajo (hay "costura" y las caras están arriba):
     el gameplay llena toda la pantalla y la cámara va en un recuadro arriba a la derecha,
     como en un directo.
  B) Plano de cara (sin costura, o con caras en varias zonas):
     recorte 16:9 de todo el ancho, centrado en la cara principal.
  C) Sin caras: recorte 16:9 centrado.
  Si el clip ya es horizontal, solo se escala/recorta para llenar el cuadro.

filtro(src, entrada="[0:v]", salida="[v0]") devuelve la cadena para -filter_complex.
"""
import subprocess
from pathlib import Path

W, H = 1920, 1080
INSET_W = 600   # ancho del recuadro de la cámara (caso A)
MARGEN = 36
_cache = {}


def _dims(src):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height", "-of", "csv=p=0", str(src)], capture_output=True, text=True).stdout
    w, h = (int(x) for x in out.strip().split(",")[:2])
    return w, h


def _costura(src, n=10):
    """Fila que separa cámara y juego, presente en la mayoría (mediana) de los fotogramas."""
    import cv2
    import numpy as np
    from zonas import _fotogramas
    perfiles = []
    for img in _fotogramas(src, n):
        g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
        f = (np.abs(np.diff(g, axis=0)) > 25).mean(axis=1)
        perfiles.append(np.maximum(f, np.maximum(np.roll(f, 1), np.roll(f, -1))))
    if not perfiles:
        return None
    perfil = np.median(np.array(perfiles), axis=0)
    zona = perfil[300:1000]
    return int(300 + zona.argmax()) if zona.max() > 0.4 else None


def analizar(src):
    src = str(Path(src).resolve())
    if src not in _cache:
        from zonas import analizar as zan
        w, h = _dims(src)
        if w >= h:
            _cache[src] = {"tipo": "horizontal"}
        else:
            caras, costura, _ = zan(src)
            if not costura or not (300 <= costura <= 1000):
                costura = _costura(src)
            # coordenadas de zonas.py: fotogramas escalados a 1080x1920
            arriba = sum(1 for x, y, ww, hh in caras if costura and y + hh / 2 < costura)
            if costura and caras and arriba >= 0.4 * len(caras):
                abajo = sorted(y + hh / 2 for x, y, ww, hh in caras if y + hh / 2 >= costura)
                _cache[src] = {"tipo": "camara_y_juego", "costura": costura,
                               "cy_abajo": abajo[len(abajo) // 2] if len(abajo) >= 3 else None}
            elif caras:
                x, y, ww, hh = max(caras, key=lambda c: c[2] * c[3])
                ys = sorted(c[1] + c[3] / 2 for c in caras if c[2] * c[3] >= 0.5 * ww * hh)
                _cache[src] = {"tipo": "cara", "cy": ys[len(ys) // 2]}
            else:
                _cache[src] = {"tipo": "centro"}
    return _cache[src]


NITIDEZ = f"scale={W}:{H}:flags=lanczos,unsharp=5:5:0.55:5:5:0.0,setsar=1"


def filtro(src, entrada="[0:v]", salida="[v0]"):
    a = analizar(src)
    if a["tipo"] == "horizontal":
        return f"{entrada}scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},setsar=1{salida}"
    # fuentes verticales normalizadas a 1080x1920
    base = f"{entrada}scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
    alto16 = 608  # 1080 * 9/16
    if a["tipo"] == "camara_y_juego":
        ys = int(a["costura"])
        resto = 1920 - ys
        alto_j = min(alto16, resto)
        ancho_j = int(alto_j * 16 / 9) if alto_j < alto16 else 1080
        yj = ys + (resto - alto_j) // 2
        if a.get("cy_abajo"):  # hay caras en la parte de abajo (p. ej. otro streamer): centrar en ellas
            yj = int(max(ys, min(1920 - alto_j, a["cy_abajo"] - alto_j * 0.45)))
        xj = (1080 - ancho_j) // 2
        return (f"{base},split[cam][jg];"
                f"[jg]crop={ancho_j}:{alto_j}:{xj}:{yj},{NITIDEZ}[fondo];"
                f"[cam]crop=1080:{ys}:0:0,scale={INSET_W}:-2:flags=lanczos,"
                f"pad=iw+10:ih+10:5:5:color=white,setsar=1[recuadro];"
                f"[fondo][recuadro]overlay=W-w-{MARGEN}:{MARGEN}{salida}")
    cy = a.get("cy", 960)
    y0 = int(max(0, min(1920 - alto16, cy - alto16 * 0.45)))
    return f"{base},crop=1080:{alto16}:0:{y0},{NITIDEZ}{salida}"


if __name__ == "__main__":
    import sys
    for f in sys.argv[1:]:
        print(Path(f).name, analizar(f))

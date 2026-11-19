#!/usr/bin/env python3
"""Encuentra dónde poner textos sin tapar al streamer.

1. Detecta caras (YuNet de OpenCV) en varios fotogramas del clip ya en 1080x1920 y
   protege cabeza + cuello + hombros de cada una.
2. Busca la "costura" horizontal entre la cámara del streamer y el gameplay (el borde
   que cruza todo el ancho) y la prefiere para el título, como hacen los canales de Top 5.
3. Para cada posición posible calcula cuánto taparía el texto de las zonas protegidas
   y elige la que menos tapa, lo más cerca de la posición preferida.

Devuelve {"y_titulo", "y_subs"} (centros verticales en píxeles).
"""
import subprocess
from pathlib import Path

ANCHO, ALTO = 1080, 1920
MODELO = Path(__file__).parent / "modelos" / "face_detection_yunet_2023mar.onnx"


def _fotogramas(video, n=8):
    import numpy as np
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                str(video)], capture_output=True, text=True).stdout.strip() or 0)
    for k in range(n):
        t = dur * (k + 0.5) / n
        raw = subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", str(video),
                              "-frames:v", "1", "-vf", f"scale={ANCHO}:{ALTO}", "-f", "rawvideo", "-pix_fmt", "bgr24",
                              "-"], capture_output=True).stdout
        if len(raw) == ANCHO * ALTO * 3:
            yield np.frombuffer(raw, dtype=np.uint8).reshape(ALTO, ANCHO, 3)


def textos_fijos(frames):
    """Franjas con texto/gráficos fijos ya pegados en el clip (títulos, banners): bordes fuertes que no se mueven."""
    import cv2
    import numpy as np
    grises = np.stack([cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float32) for f in frames])
    quieto = grises.std(axis=0) < 6
    media = grises.mean(axis=0)
    bordes = np.abs(cv2.Sobel(media, cv2.CV_32F, 0, 1)) + np.abs(cv2.Sobel(media, cv2.CV_32F, 1, 0))
    fijo = (quieto & (bordes > 120)).mean(axis=1)
    filas = np.convolve(fijo, np.ones(15) / 15, mode="same") > 0.06
    bandas, ini = [], None
    for y, v in enumerate(filas):
        if v and ini is None:
            ini = y
        if not v and ini is not None:
            if y - ini > 18:
                bandas.append((ini, y))
            ini = None
    return bandas


def analizar(video, n=8):
    """Devuelve (cajas_de_caras, y_costura o None, franjas_de_texto_fijo)."""
    try:
        import cv2
        import numpy as np
    except ImportError:
        return [], None, []
    frames = list(_fotogramas(video, n))
    if not frames:
        return [], None, []
    cajas = []
    if MODELO.exists():
        det = cv2.FaceDetectorYN.create(str(MODELO), "", (ANCHO // 2, ALTO // 2), 0.8, 0.3, 50)
        for img in frames:
            _, res = det.detect(cv2.resize(img, (ANCHO // 2, ALTO // 2)))
            if res is not None:
                for f in res:
                    x, y, w, h = (float(v) * 2 for v in f[:4])
                    if w > 60:  # ignorar caras diminutas del fondo del juego
                        cajas.append((x, y, w, h))
        # quedarse solo con caras que aparecen en varios fotogramas (descarta falsos positivos)
        def cerca(a, b):
            return abs((a[0] + a[2] / 2) - (b[0] + b[2] / 2)) < 0.6 * a[2] and abs((a[1] + a[3] / 2) - (b[1] + b[3] / 2)) < 0.6 * a[3]
        cajas = [c for c in cajas if sum(cerca(c, o) for o in cajas) >= 3]
    # costura: fila donde cambia la imagen a lo largo de casi todo el ancho, en todos los fotogramas
    perfiles = []
    for img in frames:
        g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
        d = np.abs(np.diff(g, axis=0))  # (ALTO-1, ANCHO)
        f = (d > 25).mean(axis=1)  # fracción del ancho con borde fuerte
        f = np.maximum(f, np.maximum(np.roll(f, 1), np.roll(f, -1)))  # tolerar ±1 px
        perfiles.append(f)
    perfil = np.percentile(np.array(perfiles), 30, axis=0)  # presente en al menos ~70 % de los fotogramas
    zona = perfil[380:1350]
    y_cost = None
    if zona.size and zona.max() > 0.4:
        y_cost = int(380 + zona.argmax())
    return cajas, y_cost, textos_fijos(frames)


def _protegidas(cajas, y_costura=None):
    """Rectángulos de cabeza + cuello + hombros. Si la cara está en la cámara (encima de la
    costura), el cuerpo termina en la costura: debajo ya empieza el gameplay."""
    prot = []
    for x, y, w, h in cajas:
        y1 = y + h + 0.9 * h
        y1c = y + h + 0.1 * h
        if y_costura and y + h / 2 < y_costura:
            y1, y1c = min(y1, y_costura - 4), min(y1c, y_costura - 4)
        prot.append((x - 0.15 * w, y - 0.15 * h, x + w + 0.15 * w, y1c, 50))  # la cara: nunca
        prot.append((x - 0.7 * w, y - 0.45 * h, x + w + 0.7 * w, y1, 4))     # pelo, cuello, hombros: evitar
    return prot


def _tapa(rect, prot):
    x0, y0, x1, y1 = rect
    total = 0.0
    for a0, b0, a1, b1, peso in prot:
        ix = max(0.0, min(x1, a1) - max(x0, a0))
        iy = max(0.0, min(y1, b1) - max(y0, b0))
        total += ix * iy * peso
    return total


def _mejor(prot, ancho, alto, preferida, evitar=None, y_min=90, y_max=1700):
    mejor, coste_min = preferida, None
    for y in range(y_min, y_max, 10):
        rect = ((ANCHO - ancho) / 2, y - alto / 2, (ANCHO + ancho) / 2, y + alto / 2)
        coste = _tapa(rect, prot) + abs(y - preferida) * 20
        if evitar and abs(y - evitar) < (alto + 60):
            coste += 1e9
        if coste_min is None or coste < coste_min:
            mejor, coste_min = y, coste
    return mejor


def posiciones(video, ancho_titulo=780, alto_titulo=76, ancho_subs=900, alto_subs=90):
    cajas, y_cost, bandas = analizar(video)
    prot = _protegidas(cajas, y_cost) + [(0, a, ANCHO, b, 20) for a, b in bandas]
    preferida = (y_cost + alto_titulo // 2 + 8) if y_cost else 200  # justo debajo de la costura
    y_tit = _mejor(prot, ancho_titulo, alto_titulo, preferida, y_max=1350)
    y_sub = _mejor(prot, ancho_subs, alto_subs, 1480, evitar=y_tit, y_min=1000, y_max=1720)
    return {"y_titulo": y_tit, "y_subs": y_sub, "caras": len(cajas), "costura": y_cost, "textos_fijos": bandas}


if __name__ == "__main__":
    import sys
    print(posiciones(sys.argv[1]))

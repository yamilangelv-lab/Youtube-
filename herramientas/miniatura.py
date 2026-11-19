#!/usr/bin/env python3
"""Miniatura 1280x720 para YouTube: fotograma de un clip (recortado en la cara) a la derecha
y texto grande a la izquierda, con degradado para que se lea.

Uso:
  python miniatura.py clip.mp4 SEGUNDO Y_RECORTE salida.jpg "LÍNEA 1" "LÍNEA 2" "LÍNEA AMARILLA"
  (Y_RECORTE: desde qué altura del clip vertical se toma la franja 16:9; 0 = arriba)
"""
import subprocess
import sys
import tempfile
from pathlib import Path


def miniatura(clip, t, y_recorte, salida, lineas, fuente="Inter Display Black"):
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        *blancas, amarilla = lineas
        texto = "\\N".join(blancas + ["{\\c&H00F2FF&}" + amarilla])
        (tmp / "t.ass").write_text(f"""[Script Info]
PlayResX: 1280
PlayResY: 720

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: T,{fuente},104,&H00FFFFFF,&H00FFFFFF,&H00000000,&H99000000,0,0,0,0,100,100,0,0,1,9,6,4,50,560,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:10.00,T,,0,0,0,,{texto}
""", encoding="utf-8")
        vf = (f"crop=iw:iw*9/16:0:{y_recorte},scale=1280:720,eq=saturation=1.25:contrast=1.08,"
              f"geq=r='r(X,Y)*min(1,0.35+X/900)':g='g(X,Y)*min(1,0.35+X/900)':b='b(X,Y)*min(1,0.35+X/900)',"
              f"ass=t.ass")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(t), "-i", str(Path(clip).resolve()),
                        "-frames:v", "1", "-vf", vf, "-q:v", "2", str(Path(salida).resolve())], check=True, cwd=tmp)


if __name__ == "__main__":
    if len(sys.argv) < 7:
        sys.exit(__doc__)
    miniatura(sys.argv[1], float(sys.argv[2]), int(sys.argv[3]), sys.argv[4], sys.argv[5:])

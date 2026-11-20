# Pipeline de producción de video (usado en el video del nicho 1)

Scripts que generaron el video de Somerton de forma automática:

1. `tts.py`: narración con Kokoro-82M (ONNX, voz `em_alex`, español latino). Divide el guion en frases y aplica la pronunciación de los nombres.
2. `genimgs.py` / `regen.py`: imágenes con LCM Dreamshaper v7 (CPU).
3. `gfx.py`: preparación de fotos (blanco y negro, grano, viñeta), sellos VERIFICADO/DISPUTADO/LEYENDA, mapas, tarjetas y miniatura.
4. `build.py`:
   - `audio`: línea de tiempo, mezcla de voz, música sintetizada y efectos, y subtítulos .srt.
   - `render`: clips con FFmpeg (zoompan y superposiciones).

Para reutilizarlo en otro video: cambia el guion (`blocks.json` se genera desde el .md), las imágenes y el `manifest()` de `build.py`.

Dependencias: Python 3.12, `kokoro-onnx`, `torch`, `diffusers`, `scipy`, `pillow`, `soundfile`, FFmpeg y `espeak-ng`.

# Herramientas de clipping

Tres scripts que unen las herramientas open-source recomendadas en un flujo de trabajo:

| Script | Qué hace |
|---|---|
| `momentos.py` | Analiza un VOD largo y lista los momentos con picos de audio y, si le das el chat de Twitch, picos de chat. |
| `montar.py` | Une varios clips en un Short completo a partir de un `plan.json`: zooms, cámara lenta, textos #1-#5, créditos, tu narración con ducking, música y subtítulos. Ejemplo en `primer-video/`. |
| `clipear.py` | Toma un tramo (link o archivo), lo pasa a 9:16 y le pone subtítulos palabra por palabra, un gancho de 3 s arriba, el crédito del creador y el audio normalizado a -14 LUFS. |

> Usa solo contenido que tengas permiso de usar: campañas de clipping (Content Rewards) o autorización escrita del creador. Pon siempre el crédito con `--credito`.

## Instalación (una vez)

**Windows** (PowerShell):
```powershell
winget install Python.Python.3.12
winget install Gyan.FFmpeg
# cierra y vuelve a abrir PowerShell
pip install yt-dlp faster-whisper
```

**Mac**:
```bash
brew install python ffmpeg
pip3 install yt-dlp faster-whisper
```

Aparte, descarga **TwitchDownloader** (GUI para Windows) desde https://github.com/lay295/TwitchDownloader/releases para bajar VODs y su chat en JSON.

La primera vez que transcribas, faster-whisper descarga el modelo (`small` ≈ 500 MB).

## Flujo de trabajo

```bash
# 1. Baja el VOD y su chat con TwitchDownloader (o el VOD con yt-dlp)
# 2. Busca los mejores momentos
python momentos.py vod.mp4 --chat chat.json --top 15

# 3. Revisa los candidatos en el reproductor y clipea los buenos
python clipear.py vod.mp4 --inicio 1:23:40 --fin 1:24:15 \
    --gancho "NADIE ESPERABA ESTO" --credito "Clip: @streamer" --idioma es

# También funciona directo con un link (descarga solo ese tramo):
python clipear.py "https://www.twitch.tv/videos/XXXX" --inicio 2:10:00 --fin 2:10:30 --modo fill
```

## Plantillas (`--modo`)

| Modo | Uso |
|---|---|
| `blur` (por defecto) | El video completo al centro con fondo desenfocado. Sirve para casi todo. |
| `fill` | Recorte vertical a pantalla completa. Usa `--desplazamiento 0..1` para mover el encuadre. |
| `split` | Facecam arriba y gameplay abajo, el formato clásico de clips de streamers. Necesita `--facecam x,y,ancho,alto`, medido en el video original. |

Para medir la facecam, saca un fotograma (`ffmpeg -ss 60 -i vod.mp4 -frames:v 1 frame.png`) y mira las coordenadas en Paint o en cualquier editor de imágenes.

## Opciones útiles de `clipear.py`

- `--modelo medium`: subtítulos más precisos, pero tarda más. `small` es buen equilibrio en CPU.
- `--palabras-por-linea 2`: subtítulos más grandes y rápidos.
- `--altura-subs 700`: sube los subtítulos.
- Junto al video se guarda un `.palabras.json`. Si un subtítulo sale mal, corrígelo ahí y vuelve a renderizar con `--palabras-json archivo.palabras.json` sin transcribir de nuevo.

El resultado es un borrador limpio. Revísalo y añade tu narración o comentario en CapCut, Kdenlive o Shotcut antes de publicar: sin aporte propio, YouTube no monetiza clips reutilizados.

# Repositorios de GitHub para clipping de GTA (revisión del 19-11-2026)

Las estrellas y la última actividad vienen de la API de GitHub el 19-11-2026. Los repos marcados con 🔍 se descargaron y se revisó su código.

## Base (lo que usan casi todas las herramientas de clipping)

| Repo | ★ | Licencia | Qué hace | Nivel | Agentes IA |
|---|---|---|---|---|---|
| [yt-dlp/yt-dlp](https://github.com/yt-dlp/yt-dlp) | 209k | Unlicense | Descarga videos y **solo el tramo que necesitas** de YouTube, Twitch, Kick, TikTok… | Principiante (CLI) | Sí, ideal |
| [lay295/TwitchDownloader](https://github.com/lay295/TwitchDownloader) | 4.1k | MIT | VODs, clips y **chat en JSON** de Twitch. También renderiza el chat como video. GUI para Windows y CLI. | Principiante | CLI sí |
| [FFmpeg](https://github.com/FFmpeg/FFmpeg) | 68k | LGPL/GPL | El motor que hay debajo de todo: cortes, 9:16, subtítulos, audio | Avanzado (directo) | Sí |
| [mifi/lossless-cut](https://github.com/mifi/lossless-cut) | 46k | GPL-2.0 | Corta VODs de horas al instante y sin recodificar | Principiante (GUI) | Poco |

## Subtítulos y detección

| Repo | ★ | Licencia | Qué hace | Nivel | Agentes IA |
|---|---|---|---|---|---|
| [SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper) | 27k | MIT | Transcripción local con marcas de tiempo por palabra, para subtítulos palabra por palabra | Intermedio | Sí |
| [m-bain/whisperX](https://github.com/m-bain/whisperX) | 25k | BSD-2 | Como el anterior, con mejor alineación e identifica quién habla | Intermedio-avanzado | Sí |
| [Breakthrough/PySceneDetect](https://github.com/Breakthrough/PySceneDetect) | 5.6k | BSD-3 | Detecta cambios de escena, útil para trocear trailers y compilaciones | Intermedio | Sí |
| [WyattBlue/auto-editor](https://github.com/WyattBlue/auto-editor) | 6k | Unlicense | Quita silencios y partes muertas, útil para tus videos largos narrados | Intermedio | Sí |
| [francozanardi/pycaps](https://github.com/francozanardi/pycaps) | 233 | MIT | Subtítulos animados con estilos CSS | Intermedio | Sí |

## De video largo a Shorts con IA

| Repo | ★ | Licencia | Veredicto |
|---|---|---|---|
| 🔍 [AgriciDaniel/claude-shorts](https://github.com/AgriciDaniel/claude-shorts) | 434 | MIT | **Recomendado si usas Claude Code.** Es un skill de Claude Code: Claude puntúa los momentos con una rúbrica y Remotion renderiza los subtítulos animados. Pensado para facecam/podcast, así que funciona con streamers que hablan. Avanzado (Python + Node). Última actualización: abril de 2026. |
| 🔍 [Anil-matcha/AI-Youtube-Shorts-Generator](https://github.com/Anil-matcha/AI-Youtube-Shorts-Generator) | 6.3k | MIT | Popular, pero por defecto usa la API de pago MuAPI. El modo local necesita una clave de OpenAI o Gemini. Su recorte sigue caras, algo que en gameplay sin facecam falla. Intermedio. |
| 🔍 [FujiwaraChoki/supoclip](https://github.com/FujiwaraChoki/supoclip) | 3.6k | **No comercial** | ❌ Su licencia **prohíbe expresamente** usarlo en canales monetizados o campañas pagadas. |
| [ClipsAI/clipsai](https://github.com/ClipsAI/clipsai) | 576 | MIT | ❌ Sin actualizaciones desde enero de 2024. |

## Específicos de GTA 6 (todos creados entre el 14 y el 18 de noviembre de 2026)

| Repo | ★ | Veredicto tras revisar el código |
|---|---|---|
| 🔍 [neubauerwilli/gta6-skill](https://github.com/neubauerwilli/gta6-skill) | 53 | 11 skills de Claude Code: buscador de campañas, buscador de momentos, chequeo de reglas, subtítulos… Buen diseño y honesto con el dinero, pero **está en alemán**. Sirve como referencia. |
| 🔍 [vossashtonai/gta6-clipper](https://github.com/vossashtonai/gta6-clipper) | 14 | Skills de Claude Code: facecam arriba, gameplay abajo, subtítulos, clipping de directos. Solo Mac. La versión de Windows se instala con `irm … \| iex` (ejecuta un script remoto sin verlo). Tiene 1 día de vida: **no ejecutes nada de él sin revisarlo antes**. |
| 🔍 [AnIntellectualBeing/GTA-Auto-Clipper](https://github.com/AnIntellectualBeing/GTA-Auto-Clipper) | 12 | Código real con tests y ranking por chat. Pero los subtítulos solo funcionan en **inglés e hindi**, y el autor vende un "prompt pack" aparte. |
| 🔍 [Zintara-studio/gta6-clipper](https://github.com/Zintara-studio/gta6-clipper) | 12 | ❌ Sube unos 25 Shorts al día **sin revisión**, automatizando el navegador. Es justo el contenido masivo que YouTube desmonetiza (política de contenido no auténtico) y viola las condiciones de subida. |
| 🔍 [rrobin9/clipper-engine](https://github.com/rrobin9/clipper-engine) | 26 | ❌ **No tiene código fuente**, solo un .exe/.app sin firmar. Se creó el día antes del lanzamiento y pide saltarse las protecciones de Windows y Mac. No lo instales. |

## Los 3 imprescindibles

1. **yt-dlp**: para conseguir el material.
2. **TwitchDownloader**: VOD + chat. El chat es la mejor señal de "aquí pasó algo".
3. **faster-whisper**: subtítulos palabra por palabra en español.

Más FFmpeg debajo de todo. Los scripts de `herramientas/` unen las tres.

# Video #1: "Esperaron 13 años para ESTO"

**Formato:** Short vertical de unos 40 s (YouTube Shorts, TikTok, Reels). Después, una versión larga de 8-10 min.
**Ventana:** GTA 6 salió el 19-11-2026. Publica en las **primeras 24-72 h**. Después de eso el tema se enfría y lo cubre todo el mundo.

## 1. Idea

GTA V salió en septiembre de 2013 y GTA 6 en noviembre de 2026: **13 años de espera**. El video es un **top 5 de reacciones de streamers en el momento exacto en que abren GTA 6 por primera vez**, de la más tranquila a la más intensa. El #1 es alguien que se quiebra (llora, grita o se levanta de la silla).

La gente no comparte "un clip de GTA". Comparte **la emoción de un evento que vivió**. Todos los que esperaron se ven reflejados.

## 2. Títulos

| Plataforma | Título |
|---|---|
| YouTube Shorts | **Esperaron 13 AÑOS para esto 😭 #GTA6** |
| TikTok / Reels (texto del post) | 13 años esperando… y así reaccionaron al abrir GTA 6 😭 ¿Cuál te pegó más? |
| Versión larga (YouTube) | **Así reaccionaron los streamers al abrir GTA 6 por primera vez (13 años esperando)** |

Alternativa para probar en la segunda subida: "El #1 me hizo llorar 😭 Reacciones a GTA 6".

## 3. Hook (0-3 s)

- **Qué se ve:** directamente el **pico de la reacción #1**: el grito o las lágrimas, con zoom de golpe a la cara a los 0,4 s. Nada de logo ni intro.
- **Texto arriba:** `ESPERARON 13 AÑOS PARA ESTO` (caja negra, letras blancas).
- **Qué se escucha:** 1 s del audio real del streamer (el grito), y encima tu voz: *"Trece años. Trece años esperando este momento."*

Empezar por el final funciona porque el espectador ve el pico, quiere saber qué pasó y se queda hasta el #1.

## 4. Estructura segundo a segundo

| Tiempo | Imagen (plan.json) | Texto en pantalla | Narración (tu voz) |
|---|---|---|---|
| 0:00-0:02.5 | Pico de la reacción #1 + zoom | ESPERARON 13 AÑOS PARA ESTO | "Trece años. Trece años esperando este momento." |
| 0:02.5-0:06.5 | Pantalla de carga con el chat explotando | 19 · NOV · 2026 | "Diecinueve de noviembre. Millones conectados al mismo tiempo…" |
| 0:06.5-0:11.5 | Reacción #5 (zoom a los 3 s) | #5 | *Una frase sobre lo que pasa de verdad en el clip.* Ej.: "Este no dijo nada. Se quedó congelado." |
| 0:11.5-0:16.5 | Reacción #4 | #4 | Ej.: "Este gritó antes de que cargara el juego." |
| 0:16.5-0:21.5 | Reacción #3 | #3 | Ej.: "Este llamó a su mamá. En directo." |
| 0:21.5-0:26.5 | Reacción #2 | #2 | Ej.: "Este tuvo que pararse de la silla." |
| 0:26.5-0:32.5 | Reacción #1 completa | #1 | "Pero nadie… nadie reaccionó como él." |
| 0:32.5-0:36.7 | #1 en cámara lenta (0,6×) + zoom | — | (silencio: deja que suene el clip) |
| 0:36.7-0:39.7 | Imagen congelada de la pantalla de carga | — | "¿Y tú? ¿Cuántos años esperaste?" |

> ⚠️ Las frases de #5 a #2 son **ejemplos**. Escribe cada una **según lo que pase en el clip real**. Si narras algo que no ocurrió, la gente lo nota y te lo dice en comentarios.

**Loop:** el final congelado es la misma pantalla de carga que aparece justo antes del hook. Cuando el Short vuelve a empezar, se siente como continuación, y cada repetición suma tiempo de visualización.

**Narración completa** (unas 75 palabras, ~38 s). Grábala en una sola toma con el iPhone, en la app Notas de voz, en un cuarto sin eco:

> Trece años. Trece años esperando este momento. … Diecinueve de noviembre. Millones conectados al mismo tiempo. … [frase #5]. … [frase #4]. … [frase #3]. … [frase #2]. … Pero nadie… nadie reaccionó como él. … (pausa de 4 s) … ¿Y tú? ¿Cuántos años esperaste?

Exporta el audio y guárdalo como `primer-video/narracion.m4a`.

## 5. Producción

### a) Conseguir los clips (lo más importante)
Necesitas **6 clips**: 5 reacciones y 1 pantalla de carga con el chat. Guárdalos en `primer-video/clips/` con estos nombres:

| Archivo | Qué buscar |
|---|---|
| `top1.mp4` | La reacción más extrema: llanto, grito largo o se levanta. Se le tiene que ver la cara. |
| `top2.mp4`…`top5.mp4` | Reacciones fuertes, cada una distinta a las demás: risa, shock, silencio, celebración. |
| `carga.mp4` | Pantalla de carga o logo inicial con el chat del stream moviéndose rápido. |

**De dónde sacarlos (con permiso):**
1. **Content Rewards** (contentrewards.com): busca campañas de GTA 6 y de streamers de gaming. Sus VODs ya vienen con permiso **y además te pagan por vistas**.
2. **Streamers hispanos que jugaron el lanzamiento:** escríbeles por Discord o X: *"Hola, hago clips de GTA 6 en español. ¿Me das permiso para usar tu reacción de lanzamiento? Va con crédito visible y link a tu canal."* Quédate con una captura de cada "sí".
3. **Para encontrar los momentos en VODs largos:** descarga el VOD y el chat con TwitchDownloader y ejecuta `python herramientas/momentos.py vod.mp4 --chat chat.json`. Te da los minutos donde el chat explotó.

Cuando tengas los clips, abre `primer-video/plan.json` y ajusta los `inicio`/`fin` de cada uno y la `etiqueta` (`@nombre` real del streamer).

### b) Montar el video (un comando, en tu PC con Windows)
```powershell
cd Youtube-\primer-video
python ..\herramientas\montar.py plan.json
```
Eso hace automáticamente:

| Parte | Herramienta |
|---|---|
| Cortes de cada clip | FFmpeg (en `montar.py`) |
| Reframe 9:16 con fondo desenfocado | FFmpeg |
| Zoom "punch" en el pico de cada reacción | FFmpeg `zoompan` (`zoom_en` en el plan) |
| Cámara lenta del #1 | FFmpeg (`lento: 0.6`) |
| Textos (#5…#1, fecha, gancho) y crédito del streamer | Subtítulos ASS (libass) |
| Subtítulos palabra por palabra | faster-whisper sobre tu narración |
| Bajar el audio del clip cuando tú hablas | FFmpeg `sidechaincompress` |
| Música de fondo al 10 % | FFmpeg (`musica.mp3`, opcional) |
| Volumen estándar de Shorts (-14 LUFS) | FFmpeg `loudnorm` |

Revisa los subtítulos. Si una palabra salió mal, corrígela en `final_13_anios.palabras.json` y vuelve a renderizar en segundos:
`python ..\herramientas\montar.py plan.json --palabras-json final_13_anios.palabras.json`

**Música:** usa solo música con licencia para YouTube, por ejemplo de la Biblioteca de audio de YouTube Studio. Un tema épico o emotivo con piano o cuerdas que suba hacia el #1.

### c) Toques finales en el iPhone (CapCut, 10 min)
Pasa `final_13_anios.mp4` al iPhone (Google Drive o iCloud para Windows) y en CapCut añade:
- Un **"whoosh"** en cada cambio de #5→#4→…
- Un **golpe de bajo / "boom"** justo cuando entra el #1.
- Un **flash blanco de 2 frames** al entrar al #1.
- Antes de exportar, revisa que **nada quede tapado por la interfaz de TikTok**: los botones de la derecha y la descripción abajo.

Exporta en 1080×1920, 30 fps, la máxima calidad. **No agregues la plantilla final de CapCut** (el cierre con el logo).

## 6. Miniatura / portada

En Shorts apenas se ve; en TikTok y Reels sí aparece en tu perfil y en el feed de cuadrícula.

- **Fondo:** fotograma del #1 en su pico: boca abierta o lágrimas, cara grande ocupando el 60 % superior.
- **Abajo:** el logo de GTA VI pequeño, o una franja con los colores de Vice City (rosa/morado/naranja atardecer).
- **Texto:** `13 AÑOS…` en blanco con borde negro grueso, tipografía Anton o Impact, ocupando un tercio del ancho. Nada más.
- **Contraste:** sube la saturación un 15-20 % y oscurece un poco los bordes para que la cara resalte.
- **Para la versión larga (16:9):** 3 caras de streamers en shock en fila, el logo GTA VI detrás y el texto "13 AÑOS…".

Puedes hacerla en Canva (gratis): plantilla 1080×1920 o 1280×720, sube el fotograma y añade el texto.

## 7. Descripción, hashtags y llamada a la acción

**YouTube Shorts:**
```
13 años esperando GTA 6… y así reaccionaron cuando por fin lo abrieron 😭
¿Cuál fue tu reacción? Te leo en comentarios 👇

Clips usados con permiso de:
@streamer1 · @streamer2 · @streamer3 · @streamer4 · @streamer5
(links a sus canales)

Suscríbete para los mejores momentos de GTA 6 en español todos los días.

#GTA6 #GTAVI #GrandTheftAuto #GTA6Reaccion #ViceCity #Shorts
```

**TikTok / Reels:**
```
13 años… y así reaccionaron 😭 ¿Cuál te pegó más? 👇 Clips con permiso: @... @...
#gta6 #gtavi #gta #viceCity #gaming #fyp
```

**Comentario fijado** (lo publicas tú mismo apenas subes el video):
> "Yo esperé desde [año]. ¿Y tú? 👇". Las preguntas fáciles de responder generan comentarios, y los comentarios empujan el video.

## 8. Por qué puede funcionar y cómo maximizar el alcance

**Por qué tiene potencial** (potencial, no garantía: nadie puede prometer que algo se haga viral):
- **Momento único:** es el lanzamiento más esperado de la década y la búsqueda de "GTA 6" está en su pico esta semana.
- **Emoción, no información:** las reacciones se comparten ("mira a este 😭"), las noticias no.
- **Estructura que retiene:** el hook muestra el final, la cuenta #5→#1 crea expectativa y el loop suma repeticiones.
- **En español:** la mayoría de estos tops salen primero en inglés. Ser de los primeros en español es tu ventaja.

**Plan de publicación:**
1. **YouTube Shorts primero.** 20-30 min después, TikTok. Luego Reels. Sube el **archivo limpio** a cada una: nunca un video con la marca de agua de TikTok a Reels o YouTube, porque esas plataformas penalizan el contenido reciclado.
2. **Horario:** no hay una hora mágica comprobada. Prueba la noche de Latinoamérica (19:00-22:00 en Bolivia) y compara en tus analíticas después de 5-10 videos.
3. **Primera hora:** responde todos los comentarios. Fija tu comentario.
4. **Etiqueta a los streamers** en TikTok/Reels/X y avísales: *"Subí tu reacción con crédito 🙌"*. Si la comparten, es el mayor empujón posible.
5. **En 48 h:** sube la **versión larga** (8-10 min, con más reacciones y contexto narrado) y enlázala desde el Short como "video relacionado".

**Cómo medir si funcionó** (YouTube Studio, a las 24-48 h):
- **"Vieron" vs. "Deslizaron"** en Shorts: si más del 30 % desliza, el hook falló. Cambia el primer segundo en el próximo video.
- **Porcentaje medio visto:** si es menor al 70 %, hay una parte lenta. Mira dónde cae la curva de retención.
- **Comentarios y compartidos:** muestran si conectaste emocionalmente.

## Checklist antes de publicar
- [ ] Tengo permiso de los 5 streamers (o los clips son de una campaña de Content Rewards).
- [ ] El @ real de cada streamer aparece en pantalla y en la descripción.
- [ ] Cada frase narrada describe lo que realmente pasa en el clip.
- [ ] La música es de la biblioteca de YouTube o tiene licencia.
- [ ] No hay spoilers de la historia (solo reacciones a los menús o al inicio).
- [ ] No hay violencia gráfica en los primeros segundos.
- [ ] Revisé los subtítulos y los corregí.

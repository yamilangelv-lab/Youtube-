# Video final — "El hombre sin nombre de la playa de Somerton"

| Archivo | Qué es |
|---|---|
| `somerton-man-documental-1080p.mp4` | El video completo, 1920×1080, 24 fps, ~18 min 20 s (no se sube a git por su tamaño; te lo envié directamente) |
| `subtitulos.srt` | Subtítulos en español sincronizados con la narración, para subirlos a YouTube |
| `miniatura.jpg` | Miniatura 1280×720 ("74 AÑOS SIN NOMBRE") |

## Cómo se hizo (cada pieza y con qué herramienta)

| Pieza | Herramienta | Notas |
|---|---|---|
| Guion | Escrito en esta sesión (`../guion-somerton-man.md`) | 2.745 palabras, con datos verificados |
| Voz | **Kokoro-82M** (modelo abierto, licencia Apache 2.0), voz masculina en español latino `em_alex`, ejecutado en el servidor | Pronunciación de nombres ajustada a mano (Keane→"Kin", Webb→"Uéb", etc.) |
| 3 imágenes principales (playa, zapatos, objetos) | **ElevenLabs** (modelo Seedream 5 Lite) | El plan gratuito solo permite 3 imágenes por día |
| 34 imágenes restantes | **LCM Dreamshaper v7** (modelo abierto, licencia MIT), generado en el servidor | Más simples que las de ElevenLabs; tratadas en blanco y negro con grano para el look de archivo |
| Mapas, tarjetas, sellos VERIFICADO/DISPUTADO/LEYENDA, código, árbol genealógico, titulares | Diseñados con código (Python/PIL) | Mapas esquemáticos, no cartográficos |
| Música y efectos (drones, piano, latido, olas, golpes, sellos) | Sintetizados con código, sin samples ni bibliotecas | Sin problemas de derechos |
| Montaje (movimiento Ken Burns, superposiciones, cortes, fundidos entre capítulos) y mezcla | FFmpeg | Loudness final normalizado a −14 LUFS |

Todas las imágenes generadas por IA llevan la etiqueta **"RECREACIÓN IA"** en pantalla.

## Antes de publicar (importante)

1. **Míralo entero.** Revisa sobre todo la pronunciación de la voz: Kokoro en español suena correcto pero menos natural que ElevenLabs.
2. **Licencia de las 3 imágenes de ElevenLabs.** Se generaron con el plan gratuito. Revisa los términos de ElevenLabs sobre uso comercial de imágenes en ese plan antes de monetizar. Si no lo permiten, se pueden sustituir por imágenes del modelo abierto.
3. **Confirma el estado oficial del caso** (ver `../fuentes.md`): si el forense ya confirmó la identidad, hay que cambiar el capítulo 7.
4. En YouTube Studio:
   - Marca **"contenido alterado o sintético: sí"** (hay recreaciones realistas).
   - Sube `subtitulos.srt` como subtítulos en español.
   - Usa el título, la descripción con capítulos y las etiquetas de `../README.md`.
   - Los capítulos reales del montaje final están más abajo.
5. Añade la pantalla final (los últimos ~15 s están preparados para ello) enlazando tu siguiente video.

## Capítulos del montaje final (para la descripción)

Ver `capitulos.txt` (generado a partir de la línea de tiempo real del video).

## Cómo mejorarlo

- **Voz:** el cambio que más subiría la calidad. Con ElevenLabs Starter (unos 5 USD/mes, licencia comercial, 30.000 caracteres; el guion tiene unos 16.500) se puede regenerar la narración con el `prompt-voz.md`. El montaje está automatizado: solo hay que cambiar el audio y volver a renderizar.
- **Imágenes:** con un plan de pago de ElevenLabs o Higgsfield, las 34 imágenes del modelo abierto se pueden sustituir por imágenes como las 3 principales.
- **Planos reales:** fotos de archivo de dominio público de Adelaida en 1948 (State Library of South Australia, Trove) le darían más autenticidad.

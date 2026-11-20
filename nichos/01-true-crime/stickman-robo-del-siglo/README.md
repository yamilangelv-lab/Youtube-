# Video stickman: "El robo del siglo" (nicho 1: True Crime & Misterios)

| Archivo | Qué es |
|---|---|
| `robo-del-siglo-stickman-1080p.mp4` | Video completo animado, 1920×1080, 24 fps, ~14 min 48 s (se envía directamente; no está en git) |
| `guion.md` | Guion con el tiempo y la escena de cada bloque |
| `subtitulos.srt` | Subtítulos en español sincronizados |
| `miniatura.jpg` | Miniatura 1280×720 en el mismo estilo stickman |
| `capitulos.txt` | Capítulos para la descripción de YouTube |
| `fuentes.md` | Fuentes y datos en disputa |

## Formato
- Animación de personajes **stickman** dibujados y animados con código: caminar, correr, hablar, señalar, levantar las manos, cavar, remar, encogerse de hombros…
- Fondo crema, trazo negro y colores de acento para identificar a cada personaje:
  - Vitette: rosa.
  - Beto: verde.
  - Araujo: amarillo con gafas.
  - Policías: azul con gorra.
  - El narrador: un detective con sombrero.
- Etiquetas, sellos VERIFICADO / DISPUTADO / LEYENDA, mapas, contadores y tarjetas de capítulo.
- Narración en español latino (Kokoro, voz `em_alex`), música "de atraco" y efectos sintetizados con código.

## Títulos sugeridos
1. **Robaron 19 millones sin disparar un tiro… y los delató algo que nadie esperaba** ← recomendado
2. El robo del siglo: el plan perfecto que cayó por celos
3. Les dejaron una rima a 300 policías: la historia real del robo del siglo

## Descripción
> 13 de enero de 2006. Una banda toma 23 rehenes en el Banco Río de Acassuso, negocia durante horas, pide pizzas… y desaparece por un túnel hacia los desagües, en botes inflables. Dejaron armas de juguete y una nota: "En barrio de ricachones, sin armas ni rencores. Es solo plata, no amores". Esta es la historia real del robo del siglo, y de cómo los atraparon.
>
> (pega aquí los capítulos de `capitulos.txt`)
>
> Fuentes: La Nación, Perfil, Infobae, El Cronista, La Capital (Mar del Plata), Diario de Cuyo, Infocielo, El Destape, El Financiero (lista completa en el comentario fijado).
>
> #RoboDelSiglo #TrueCrime #Argentina #Historia #Animación #Stickman

## Etiquetas
robo del siglo, banco río acassuso, robo del siglo argentina, historia real robo del siglo, túnel banco, vitette, araujo, robos famosos, true crime en español, stickman, animación, casos reales

## Antes de publicar
1. **Míralo entero** y comprueba que la voz y el ritmo te convencen.
2. Revisa `fuentes.md`: cifras como el botín, el número de cajas y el de policías están marcadas como disputadas en el propio video.
3. En YouTube Studio:
   - Sube `subtitulos.srt`.
   - Pega los capítulos.
   - En "contenido alterado o sintético" marca **no**: es animación caricaturesca, no realista. La voz es sintética; si quieres máxima transparencia, menciónalo en la descripción.

## Cómo se hizo
Ver `../../../herramientas/pipeline-stickman/`. La voz, las escenas y el montaje son reproducibles: cambiando el guion (`beats.py`) se genera otro video con el mismo estilo.

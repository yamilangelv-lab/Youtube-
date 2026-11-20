# Preferencias del canal (decididas por el dueño)

## Formato Top 5 de streamers
- ✅ **Estilo aprobado:** el de `videos/top5-djmariio`, que incluye:
  - un gancho de ~2 s con el remate del #1 y el título "TOP 5 MOMENTOS DE X EN GTA 6" arriba;
  - una etiqueta "#N · TÍTULO" arriba durante cada momento, colocada debajo de la cámara del streamer;
  - subtítulos grandes palabra por palabra (fuente Inter Display Black);
  - zoom a la cara en los picos;
  - efectos de sonido sintetizados (`herramientas/sfx.py`) y un whoosh entre momentos;
  - cierre de 3 s: "¡SUSCRÍBETE PARA NO PERDERTE NADA DE GTA 6!".
- ❌ **No usar** el formato ranking con la lista 1–5 fija a la izquierda (`videos/top5-rubius`). Se probó y se descartó.
- **Los textos nunca tapan la cara ni el cuerpo del streamer, ni los textos que ya trae el clip.** Van en tamaño pequeño. `herramientas/zonas.py` elige la posición automáticamente: la unión entre la cámara y el juego, o encima de la cabeza.
- Sin voz en off. Si algún día se añade voz, que sea con más energía y entusiasmo.
- Descartar los clips que traen marca de agua de otro canal o subtítulos ya pegados en la imagen.

## Próximos streamers (en orden)
Auronplay → La Cobra → Davo → otros grandes.

## Videos largos (YouTube normal)
- **Horizontal 16:9, 1920×1080, a pantalla completa de borde a borde.** Sin barras, sin fondo desenfocado y sin el clip vertical centrado en un marco.
- `herramientas/largo.py` con `"pantalla_completa": true` usa `herramientas/pantalla_completa.py`:
  - si el clip tiene cámara arriba y juego abajo, el juego llena la pantalla y la cámara va en un recuadro arriba a la derecha;
  - si es un plano de cara, se recorta en 16:9 centrado en la cara.

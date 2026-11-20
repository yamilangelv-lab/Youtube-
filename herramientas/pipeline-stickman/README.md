# Pipeline de animación stickman

- `beats.py`: el guion, como una lista de (escena, parámetros, narración).
- `tts2.py`: la narración con Kokoro (voz `em_alex`, español latino); cada audio se guarda con el hash de su texto.
- `engine.py`: el motor de dibujo (pycairo):
  - personaje stickman articulado con más de 20 poses;
  - expresiones y accesorios;
  - objetos de escena: banco, patrulla, túnel, bote, antena, notas, sellos.
- `scenes.py`: la biblioteca de escenas animadas.
- `build_stick.py`:
  - `preview`: fotogramas de prueba;
  - `audio`: voz, música de atraco sintetizada y efectos, y el .srt;
  - `render`: clips en paralelo con FFmpeg.

Para hacer otro video: escribe un `beats.py` nuevo (y las escenas que falten), ejecuta `tts2.py` y luego `build_stick.py audio` y `build_stick.py render`. Por último, concatena los clips y añade el audio con FFmpeg.

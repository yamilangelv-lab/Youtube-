# Tarea de foley: hoja de trabajo del grupo

## 1. Clip elegido
- Enlace: ______________________
- Empieza en: ____  Termina en: ____  (entre 30 y 60 s)
- Ya lo escuchamos con audífonos y no tiene música: [ ]

## 2. Hoja de tiempos
Los tiempos se cuentan desde el inicio del tramo elegido, no desde el inicio del video de YouTube.

| Tiempo | Qué pasa en pantalla | Sonido | Objeto que usamos | Archivo |
|---|---|---|---|---|
| 0:00 a 0:45 | Ambiente de playa (todo el clip) | Olas | Arroz en una bandeja, moviéndola de lado a lado | olas.m4a |
| 0:__ | Camina por la arena | Pasos | Maicena en una bolsa de tela, apretando | pasos.m4a |
| 0:__ | Golpea el coco contra la piedra | Golpe | Coco de verdad + piedra | golpe1.m4a |
| 0:__ | El coco se raja | Crujido | Apio o zanahoria partida | rama.m4a |
| 0:__ | Se mueve o se agacha | Ropa | Frotar una chamarra de tela | ropa.m4a |

Un archivo por cada sonido. Si el mismo sonido se repite (por ejemplo, 3 golpes), graben un archivo para cada golpe o pongan el mismo archivo 3 veces con distintos tiempos.

## 3. Cómo grabar
- Usen la grabadora de voz del celular, en el cuarto más callado y con frazadas alrededor.
- El celular va a unos 20 o 30 cm del objeto.
- Pongan la escena sin audio en una laptop y hagan el sonido al mismo tiempo que la imagen.
- Graben de 3 a 5 tomas de cada sonido y quédense con la mejor.
- **Cada archivo tiene que empezar con un poco de silencio y luego el sonido, sin aplausos ni voces.** El programa corta el silencio solo y deja el sonido justo en su segundo.
- Las olas o el ambiente: graben unos 20 a 30 s seguidos. El programa los repite durante toda la escena.
- Graben con otro celular un video del detrás de cámaras (de 20 a 40 s) mostrando cómo hacen los sonidos.

## 4. Qué entregar para armar el video
1. El clip descargado (mp4).
2. Todos los audios (m4a, mp3 o wav, cualquiera sirve).
3. El video del detrás de cámaras (opcional).
4. Esta hoja llena, más los nombres de los integrantes.

Con eso se llena `proyecto.json` y se corre:

```
python3 armar_video.py proyecto.json
```

Sale un solo video con: portada, la escena con el sonido original, la escena con el sonido recreado (con el nombre de cada objeto en pantalla), el detrás de cámaras y los créditos.

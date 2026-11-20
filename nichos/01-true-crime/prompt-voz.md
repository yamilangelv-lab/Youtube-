# Prompt de voz — Nicho 1 (True Crime & Misterios)

## 1. Prompt para diseñar la voz (ElevenLabs "Voice Design" o similar)

**Principal (masculina):**

> Narrador masculino latinoamericano de 35 a 45 años, acento neutro. Voz de barítono cálida y con cuerpo, grabada en estudio con micrófono cercano, sin reverberación. Tono de documental de investigación criminal: sereno, preciso, curioso e inteligente, como un investigador que te muestra las pruebas una por una y que todavía está intrigado por el caso. Energía contenida y nunca gritada. Ritmo variado: ágil y conversacional al dar contexto; más lento, grave y casi en voz baja en los momentos de tensión; pausas claras antes de cada pista o revelación. Empático y sobrio al hablar de muertes, sin dramatismo ni morbo. Nada de tono de locutor comercial ni de lectura plana.

**Alternativa (femenina):**

> Narradora latinoamericana de 30 a 40 años, acento neutro. Voz media-grave, cálida y nítida, grabada en estudio, sin reverberación. Tono de periodista de investigación: serena, precisa, con curiosidad genuina y complicidad con quien escucha. Crea suspense bajando el ritmo y el volumen, no subiéndolos. Pausas marcadas antes de las pistas importantes. Sobria y respetuosa al hablar de muertes.

**Texto de prueba para comparar voces:**

> El 1 de diciembre de 1948, en una playa del sur de Australia, encuentran a un hombre muerto. No lleva documentos. Alguien había arrancado las etiquetas de su ropa. Y en un bolsillo escondido, la policía encuentra un trozo de papel con solo dos palabras: "Tamám Shud". Significa "se acabó".

## 2. Ajustes (ElevenLabs)

- **Modelo:** prueba v3 (más expresivo, admite etiquetas) y Multilingual v2 (más estable en textos largos) con el texto de prueba; quédate con el más natural.
- **Stability:** 40–50%. **Similarity:** 75–80%. **Style:** 15–30%. **Speaker boost:** activado.
- **Velocidad:** 0.95–1.0 (objetivo: 140–155 palabras/min).
- **Genera por capítulos** (8 archivos), no todo de una vez.

## 3. Dirección por capítulo

| Capítulo | Indicación |
|---|---|
| Cold open | Íntimo, frases cortas. Pausa de 1 s antes de "Significa 'se acabó'". |
| 1 — Un hombre sin nada | Tono de inventario: claro y metódico al leer los objetos, cada uno con su pausa. |
| 2 — La maleta | Frustración contenida. "Y no encontró a ningún Keane" con un descenso. |
| 3 — Tamám Shud | Curiosidad creciente. "Justo donde estaban las palabras 'Tamám Shud'" despacio, casi susurrado. |
| 4 — La enfermera | Humano y cuidadoso. Sin insinuar culpas. |
| 5 — Teorías | Más ágil, casi de debate. Un tono distinto para cada teoría. |
| 6 — ADN | Energía ascendente, de descubrimiento. Pausa larga después de "Thomas Keane". |
| 7 — Veredicto | Reflexivo y cálido. La última frase, lenta. |

**Etiquetas (solo en ElevenLabs v3), con moderación:** `[whispers]` antes de "Justo donde estaban las palabras 'Tamám Shud'"; `[pause]` antes de "Keane. El nombre escrito en la ropa…".

## 4. Pronunciación

| Palabra | Cómo debe sonar |
|---|---|
| Tamám Shud | "Tamám Shud" (la "u" como en español) |
| Somerton | "Sómerton" |
| Adelaida | en español: "Adelaida" |
| Glenelg | "Glenélg" |
| Henley Beach | "Jénli Bich" |
| Rubaiyat | "Rubaiyát" |
| Omar Jayam | "Ómar Jayám" |
| Kensitas | "Kensítas" |
| Juicy Fruit | "Yúsi Frut" |
| Jessica Thomson | "Yésica Tómson" |
| Alfred Boxall | "Álfred Bóxol" |
| Cedric Stanton Hicks | "Sédric Stánton Jics" |
| John Harber Phillips | "Yon Járber Fílips" |
| Derek Abbott | "Dérek Ábot" |
| Colleen Fitzpatrick | "Colín Fitspátric" |
| Carl Webb | "Carl Uéb" |
| Footscray | "Futscréi" |
| Dorothy Robertson | "Dórothi Róbertson" |
| Freda | "Frída" |
| Thomas Keane | "Tómas Kín" |
| Gordon Cramer | "Górdon Créimer" |
| ouabaína | "ua-ba-í-na" |

Escribe estas pronunciaciones fonéticamente en el texto que envíes a la herramienta (o en su diccionario de pronunciación), pero deja la ortografía correcta en los subtítulos.

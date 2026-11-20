# Prompt de voz — narrador del canal

## 1. Prompt para diseñar la voz (ElevenLabs "Voice Design" u otra herramienta de voz por descripción)

**Versión principal (masculina):**

> Narrador masculino latinoamericano de 35 a 45 años, acento neutro sin regionalismos marcados. Voz de barítono cálida, cercana y con cuerpo, grabada en estudio con micrófono de cerca, sin reverberación. Tono de documental de misterio: sereno, inteligente y curioso, como alguien que te cuenta una historia real que conoce a fondo y que todavía lo intriga. Energía contenida, nunca gritada. Ritmo variado: fluido y conversacional al explicar contexto; más lento, grave y casi en voz baja en los momentos de suspense; pausas claras antes de cada revelación. Empático y respetuoso cuando habla de muertes. Nada de tono de locutor comercial ni de lectura plana.

**Alternativa femenina:**

> Narradora latinoamericana de 30 a 40 años, acento neutro. Voz media-grave, cálida y nítida, grabada en estudio, sin reverberación. Tono de documental de investigación: serena, precisa y con curiosidad genuina, con un toque de complicidad con quien escucha. Energía controlada; baja el volumen y el ritmo para crear suspense en lugar de subirlo. Pausas marcadas antes de los datos importantes. Empática y sobria al hablar de víctimas.

**Texto de prueba para generar las muestras** (úsalo al diseñar la voz):

> En 1991, en un cementerio diminuto del sur de Bolivia, un equipo de investigadores empieza a cavar. Buscan a dos hombres que murieron aquí hace más de ochenta años. Encuentran huesos. Comparan el ADN. Y el resultado es este: no son ellos.

## 2. Ajustes recomendados (ElevenLabs)

- **Modelo:** el más expresivo disponible para narración larga (en ElevenLabs, v3 si quieres etiquetas de emoción; Multilingual v2 si priorizas estabilidad en 20 minutos). Prueba ambos con el cold open y quédate con el que suene más natural.
- **Stability:** 40–50% (por debajo suena teatral; por encima, plano).
- **Similarity:** 75–80%.
- **Style/estilo:** 15–30%.
- **Speaker boost:** activado.
- **Velocidad:** 0.95–1.0. Objetivo: unas 145–155 palabras por minuto.
- Genera **por capítulos** (7 archivos), no los 20 minutos de una vez: es más fácil corregir y mantener el tono.

## 3. Dirección de interpretación por tramo

| Tramo | Indicación |
|---|---|
| Cold open | Voz baja, íntima, frases cortas. Pausa de 1 s antes de "no son ellos". |
| Cap. 1–2 | Conversacional, con una sonrisa leve en la ironía (la foto de Fort Worth, los forajidos rancheros). |
| Cap. 3 | Más tensión a medida que se acerca el asalto. "Vaca muerta" dicho despacio. |
| Cap. 4 | El tramo más lento del video. Casi susurrado en "Luego nada más". Sobrio, sin morbo, en el posible asesinato-suicidio. |
| Cap. 5 | Recupera energía: tono de detective que encuentra pistas. |
| Cap. 6 | Preciso, casi científico. |
| Cap. 7 | Reflexivo y cálido. La última frase, lenta y con peso. |

**Etiquetas (solo si usas ElevenLabs v3):** úsalas con moderación, por ejemplo `[whispers]` antes de "Luego nada más." y `[pause]` antes de "no son ellos". No las pongas en cada frase: el exceso suena artificial.

## 4. Pronunciación (añádelo a un diccionario de pronunciación o escríbelo fonéticamente en el texto que mandas a la herramienta)

| Palabra | Cómo debe sonar |
|---|---|
| Longabaugh | "LÓNGA-bo" |
| Butch Cassidy | "Buch Cásidi" |
| Sundance | "Sándans" |
| Pinkerton | "Pínkerton" |
| Huaca Huañusca | "Uáca Uañúsca" |
| Peró | "Peró" (aguda) |
| Quechisla | "Kechísla" |
| Circleville | "Sércol-vil" |
| Spokane | "Spokán" |
| Wilcox | "Uílcox" |
| Clyde Snow | "Cláid Snóu" |
| Zimmer | "Tsímer" (pronunciación alemana) |
| Betenson | "Bétenson" |

## 5. Si grabas tu propia voz (opcional y recomendable a medio plazo)

Una voz humana propia es el diferenciador más fuerte frente a canales automatizados. Si algún día te animas: micrófono dinámico USB, habitación con ropa/cortinas, la misma dirección de la tabla de arriba. Puedes empezar con IA y pasar a tu voz cuando el canal funcione.

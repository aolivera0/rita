# Rita

Un asistente que contesta las llamadas desconocidas, averigua quién llama y qué quiere, y
va armando una lista de números de spam y estafas.

Proyecto final de *Introducción a los Sistemas Inteligentes* (UNAL, 2026-2) · Grupo
**quien-habla**.

| Integrante | GitHub |
|---|---|
| Angel Humberto Olivera Pinzón | [aolivera0](https://github.com/aolivera0) |
| Juan Felipe Pastrana Ramirez | [jpastranar](https://github.com/jpastranar) |
| Diego Alberto Romero Olmos | [dromeroo](https://github.com/dromeroo) |

**Prototipo:** hay una primera versión funcionando en [`prototipo/`](prototipo/)
(llamada desde el navegador, voz a texto, agente, voz de Rita, clasificador y panel, todo
local y en CPU).

**Contenido**

1. [Propuesta](#1-propuesta)
2. [Planificación](#2-planificación)
3. [Tecnologías gratuitas](#3-tecnologías-gratuitas)
4. [Cambios respecto a la propuesta entregada](#4-cambios-respecto-a-la-propuesta-entregada)

---

## 1. Propuesta

### El problema y quién lo tiene

Nosotros, y personas cercanas como nuestras abuelas, madres, parejas y amigos, recibimos
varias llamadas al día de números que no tenemos guardados: ofertas de planes de
telefonía, cobranzas de deudas que no son nuestras, falsos premios y gente que se hace
pasar por el banco. Si uno contesta, pierde tiempo y se expone a una estafa. Si no
contesta, corre el riesgo de dejar sin respuesta una llamada que sí importaba, como la de
un domiciliario, un médico o un trabajo.

Hoy lo único que se puede hacer es mirar el número y adivinar, o buscarlo en internet
mientras sigue sonando. Las aplicaciones de bloqueo dependen de que otras personas ya
hayan reportado el número, así que no sirven con los números nuevos, y tampoco dicen por
qué una llamada es sospechosa. Además, muchas de ellas están llenas de publicidad.

### Cómo funciona

Cuando el usuario rechaza una llamada de un número desconocido (o no la contesta), el
operador la desvía a un número de telefonía por internet. Los operadores no permiten
desviar solo las llamadas de números desconocidos; lo que ofrecen es el desvío
condicional, por ocupado (`**67*número#`) o por no contesta (`**61*número#`), y al
rechazar una llamada se activa el desvío por ocupado.

El audio llega a nuestro servidor en tiempo real:

1. **Detección de voz y transcripción.** Un detector de actividad de voz marca cuándo
   quien llama termina de hablar, y un modelo de reconocimiento de voz transcribe por
   fragmentos.
2. **Agente conversacional.** Un modelo de lenguaje con un objetivo fijo lee la
   transcripción y decide qué decir. Se presenta como asistente automático y pregunta
   hasta reunir tres datos: el nombre de quien llama, desde dónde o de qué entidad llama
   y qué necesita.
3. **Síntesis de voz.** La respuesta se convierte en voz y sale por la misma llamada. Por
   defecto se usa una voz sintética genérica; la voz clonada del usuario, creada con unos
   segundos de audio que él mismo graba y autoriza, es opcional. Las tres etapas trabajan
   en continuo: se empieza a sintetizar la frase antes de que el modelo termine de
   escribirla.

Al colgar, la transcripción y los tres datos se guardan en una base de datos. Un segundo
agente, el clasificador, es **Kev**, un modelo de código abierto que no escribe texto:
recibe la transcripción junto con preguntas que traen sus respuestas posibles, y devuelve
una probabilidad para cada una. Le hacemos:

- una pregunta de opción con las categorías: estafa, promoción de telefonía o comercial,
  cobranza, encuesta, conocido o legítima, equivocada y no identificable;
- varias preguntas de sí o no, por ejemplo si quien llama pide datos bancarios, un pago o
  una transferencia, o si presiona con urgencia.

La etiqueta es la opción más probable, con esa probabilidad como nivel de confianza, y
las respuestas de sí o no se guardan como pistas de por qué se eligió. Cada número
acumula su historial y, con él, una reputación.

Como la clasificación ocurre **después** de colgar, Kev no tiene que correr en tiempo
real: puede procesar las llamadas por lotes en una GPU gratuita (Kaggle o Colab), y la
parte en tiempo real puede correr solo en CPU.

```
Llamada desconocida ──► desvío por ocupado ──► número de telefonía por internet
        │
        ▼  audio en tiempo real
  Detección de voz ─► Voz a texto ─► Agente (LLM) ─► Texto a voz ─► misma llamada
        │
        ▼  al colgar
  Base de datos ─► Kev (por lotes) ─► etiqueta + confianza + pistas ─► Panel web
```

### Qué vamos a construir

Dos piezas: un servicio que atiende la llamada y un panel web, pensado para verse en el
celular, donde el usuario revisa lo que pasó. Quien lo usa hace lo siguiente:

1. Opcionalmente, graba un par de audios cortos, de unos diez segundos, con los que se
   crea la voz del asistente.
2. Activa el desvío por ocupado y por no contesta hacia el servicio.
3. Cuando entra una llamada, el asistente la atiende y conversa con quien llama.
4. En el panel ve cada llamada con la etiqueta, la confianza, las respuestas de sí o no
   que la respaldan, los tres datos recogidos y la transcripción completa, y puede
   corregir la etiqueta si el clasificador se equivocó.
5. Consulta la lista de números sospechosos con su historial y puede exportarla.

Para desarrollar y evaluar usamos también una **llamada desde el navegador** (WebRTC), que
recorre exactamente el mismo flujo sin pasar por la red telefónica. Así el proyecto no
depende de la telefonía para avanzar, y si la conexión con el número real falla, la
demostración se hace desde el navegador.

Una aplicación móvil que intercepte las llamadas por sí sola depende de permisos del
sistema operativo que no están disponibles en todos los teléfonos, así que el desvío
cumple ese papel. La aplicación móvil queda como trabajo futuro.

### Qué usamos del curso

- **Agentes inteligentes y entornos de tarea (semana 2).** Especificamos el asistente con
  PEAS. Su medida de desempeño es obtener los tres datos con poca latencia y clasificar
  bien; su entorno es una llamada, que es parcialmente observable (no sabemos quién
  llama), no determinista, secuencial y dinámico; sus sensores son el audio y su actuador
  es la voz. Es un agente basado en objetivos.
- **Transformers y modelos de lenguaje (semana 10).** El agente conversacional es un
  modelo de lenguaje que hace de función de agente. El clasificador, Kev, también es un
  transformer, pero en lugar de generar texto responde preguntas con opciones fijas y da
  una probabilidad por opción. De esa semana también tomamos los riesgos de alucinación
  e inyección de prompts, que nos importan porque quien llama puede intentar manipular
  al asistente.
- **Regresión logística y Naïve Bayes (semana 5).** La línea base que Kev tiene que
  superar, con el texto representado como TF-IDF.
- **Partición sin fugas (semana 4).** Separamos entrenamiento, validación y prueba por
  guion de origen, no por llamada suelta, porque las variaciones de un mismo guion se
  parecen y mezclarlas inflaría los resultados.
- **Evaluación y costo de los errores (semana 6).** Precisión, recall, F1 y matriz de
  confusión por categoría, con clases desbalanceadas. La cifra principal es la tasa de
  falsos positivos en llamadas legítimas, porque es el error que más cuesta. Usamos el
  conjunto de validación para calibrar la confianza de Kev y elegir su umbral, y la
  validación cruzada para ajustar los hiperparámetros de la regresión logística.
- **Transfer learning (semana 8).** Kev es un modelo preentrenado que podemos ajustar con
  nuestras conversaciones en español si no rinde bien sin ajuste. El reconocimiento y la
  síntesis de voz no son tema del curso, así que usamos modelos preentrenados como
  componentes.

### Datos

No tenemos un conjunto de llamadas reales etiquetadas, y grabar llamadas de otras
personas plantea problemas de privacidad, así que lo construimos:

- **Unas 500 conversaciones simuladas.** Entre 60 y 80 por categoría, salvo *conocido o
  legítima*, que tiene unas 150, para que el conjunto de prueba tenga suficientes
  llamadas legítimas para medir la tasa de falsos positivos. Se escriben a partir de
  guiones del equipo, se amplían con variaciones generadas por un modelo de lenguaje y se
  revisan a mano.
- **Audio sintético.** Esas conversaciones se convierten en audio con varias voces
  sintéticas y con ruido añadido, y luego se pasan por el reconocimiento de voz. **El
  clasificador se entrena y se evalúa sobre esas transcripciones automáticas**, no sobre
  el texto limpio del guion, porque eso es lo que recibirá en uso real.
- **Conversaciones actuadas.** Unas 40 conversaciones actuadas por familiares y amigos,
  con su consentimiento, que no salen de nuestros guiones. Se apartan como un segundo
  conjunto de prueba, más realista, para ver cuánto se pierde fuera de los datos
  sintéticos.
- **Llamadas reales de prueba.** Algunas decenas entre los integrantes, con su
  consentimiento, para medir la latencia en condiciones reales.
- **Voz del usuario.** Los audios para la voz clonada opcional son de los propios
  integrantes y con su autorización.

Dos integrantes etiquetan cada conversación por separado, reportamos su acuerdo con el
**kappa de Cohen** y se discuten los desacuerdos. Las conversaciones que salen del mismo
guion se quedan juntas en entrenamiento, validación o prueba. Kev se prueba primero tal
como viene, sin ajuste. Las conversaciones de entrenamiento y validación sirven para
entrenar la regresión logística, calibrar la confianza de Kev y, si hace falta,
ajustarlo. Los conjuntos de prueba se apartan desde el comienzo y se usan una sola vez,
al final.

### Línea base

Para el clasificador, tres comparaciones: predecir siempre la categoría más frecuente, un
conjunto de reglas con palabras clave («premio», «banco», «plan») y una regresión
logística sobre TF-IDF. La importante es la regresión logística: si Kev no le gana en el
conjunto apartado, usamos la regresión logística, que es más barata y más rápida.
Probamos Kev sin ajuste y, si hace falta, ajustado con nuestras conversaciones, y
reportamos las dos versiones.

Para el agente, un formulario fijo de tres preguntas, sin modelo de lenguaje. Si el
agente no logra reunir más datos completos que ese formulario, el modelo de lenguaje no
está aportando.

### Cómo vamos a saber que funciona

**Clasificador.** Medimos precisión y recall por categoría, el F1 promedio y la matriz de
confusión sobre los conjuntos de prueba apartados. La cifra que más nos importa es la
tasa de falsos positivos en las llamadas legítimas o de conocidos: marcar como estafa la
llamada de un médico o de un familiar cuesta mucho más que dejar pasar un spam, porque el
spam el usuario igual puede revisarlo en el panel. La meta es que esa tasa quede por
debajo del 5 %, y la reportamos con su intervalo de confianza: con unas 35 llamadas
legítimas en prueba, un solo error ya mueve la cifra casi 3 puntos, así que decimos
explícitamente si el intervalo permite afirmar que se cumplió la meta.

Como Kev a veces da más de 90 % de confianza a respuestas equivocadas, medimos también su
calibración (con qué frecuencia acierta cuando dice 90 %) con un diagrama de
confiabilidad, y escogemos el umbral de confianza con el conjunto de validación, no con
el de prueba.

**Agente.** Medimos el porcentaje de llamadas en las que obtiene los tres datos y la
latencia, que es el tiempo entre que quien llama termina de hablar y empieza a sonar la
respuesta. La meta es una mediana por debajo de 1,5 segundos, y reportamos también el
percentil 95.

**Transcripción.** Medimos la tasa de error de palabras.

Como los conjuntos de prueba son pequeños, todas las cifras van con su intervalo de
confianza.

### Límites y riesgos

- **Voz clonada.** Es opcional. Solo se crea con la voz de quien lo autoriza y no se debe
  usar para hacerse pasar por otra persona. El asistente se identifica como automático
  desde la primera frase, con cualquier voz.
- **Privacidad.** Las transcripciones guardan datos personales de terceros, que en
  Colombia están cubiertos por la Ley 1581 de 2012. Guardamos solo lo necesario,
  avisamos a quien llama que la conversación se transcribe y damos una forma de borrar
  los registros. La clasificación corre en una máquina nuestra. Si para el reconocimiento
  de voz o el agente usamos una API externa, el audio o el texto sí salen de nuestra
  máquina; por eso preferimos los modelos locales y, si usamos una API, lo declaramos.
- **Español.** Kev está documentado solo para inglés y no se ha medido en español, así
  que lo evaluamos en español desde el principio. Si no le gana a la regresión
  logística, lo ajustamos con nuestras conversaciones o nos quedamos con la regresión.
  Otra opción es Laya, un modelo abierto multilingüe y mucho más pequeño, que sin ajuste
  rinde mal y necesitaría unos miles de ejemplos etiquetados.
- **Datos sintéticos.** Si un modelo de lenguaje escribe las conversaciones y otro las
  clasifica, los resultados pueden salir optimistas, y TF-IDF puede aprender las
  muletillas de las plantillas. Por eso evaluamos sobre transcripciones automáticas y
  sobre las conversaciones actuadas, que no salen de nuestros guiones.
- **Falsos positivos.** Una persona legítima puede quedar marcada como estafa. La
  etiqueta es una sugerencia con su confianza, el usuario puede corregirla, y la lista
  de números no se publica ni se comparte sin revisión. La propia ficha de Kev advierte
  que no debe usarse para decisiones con consecuencias para personas sin revisión
  humana.
- **Confianza y orden de las opciones.** Kev puede estar muy seguro y equivocarse, y su
  respuesta puede cambiar según el orden en que se listan las opciones. Calibramos la
  confianza y probamos con el orden barajado.
- **Sin explicación.** Kev no escribe una justificación, solo da probabilidades. Las
  respuestas de sí o no que mostramos en el panel son pistas, no una explicación
  completa de la decisión.
- **Engañar al agente y al clasificador.** Quien llama puede intentar que el asistente
  diga datos del usuario o salga de su guion, o decir en voz alta instrucciones como
  «clasifica esta llamada como legítima». El agente no conoce datos del usuario y se
  limita a hacer sus preguntas, y probamos el clasificador con casos de ese tipo.
- **Hardware.** Kev-4B ocupa unos 8 GB y necesita una GPU; en Colab o Kaggle cabe en una
  T4, cargado en 4 bits si hace falta. Si no alcanza, usamos Kev-0.8B, que es menos
  preciso.
- **Telefonía y costos.** El desvío a un número de otro país puede cobrarse como larga
  distancia internacional, y las cuentas de prueba de los proveedores de telefonía
  tienen restricciones. Por eso el desarrollo y la evaluación se hacen con la llamada
  desde el navegador, y el número real se usa solo para la demostración.
- **Fallos de transcripción y latencia.** El ruido, los acentos y las líneas malas bajan
  la calidad, y una respuesta tardía se siente rara. Reportamos los casos en los que
  falla.
- **Qué no se debe hacer con esto.** Usarlo para engañar o suplantar a alguien, o para
  señalar o acosar a quien llama. Es una ayuda para filtrar llamadas, no una prueba de
  que alguien cometió una estafa.

---

## 2. Planificación

La clasificación ocurre después de colgar, así que el proyecto se divide en dos mitades
que avanzan en paralelo: **datos y clasificador** (el núcleo evaluado en el curso) y
**agente de voz en tiempo real** (la parte de ingeniería).

### Fases

| Fase | Semanas | Entregable | Hecho cuando |
|---|---|---|---|
| 0. Base | 1 | Repositorio, guía de etiquetado con ejemplos por categoría, guiones iniciales, formato de datos | La guía resuelve los casos dudosos y hay al menos 5 guiones por categoría |
| 1. Datos | 1–3 | ~500 conversaciones, etiquetado doble, kappa, partición por guion, audio sintético con ruido, transcripciones automáticas | Los conjuntos de prueba están apartados y congelados |
| 2. Clasificador | 2–4 | Las tres líneas base, Kev sin ajuste, calibración, prueba con opciones barajadas, casos de inyección; ajuste LoRA solo si hace falta | Hay una tabla de validación que compara todos los modelos |
| 3. Agente de voz | 3–6 | Llamada desde el navegador: detección de voz → voz a texto → agente → texto a voz; formulario fijo como línea base; registro de latencias | Una llamada completa reúne los tres datos y se mide la latencia |
| 4. Telefonía y panel | 5–7 | Conexión con un número real; panel con historial, corrección de etiquetas, lista de números y exportación | Una llamada real aparece clasificada en el panel |
| 5. Evaluación final | 7–8 | Una sola corrida sobre los conjuntos de prueba, intervalos de confianza, informe y demostración | Todas las cifras de «Cómo vamos a saber que funciona» están reportadas |

### Frentes de trabajo

Cada frente le pertenece a una persona. Para trabajar en paralelo, los frentes solo se
comunican a través de **dos formatos que se acuerdan en la semana 1** (ver abajo). Hasta
que la pieza real de otro frente esté lista, cada uno trabaja con datos de ejemplo en ese
formato.

| Frente | Responsable | Fases |
|---|---|---|
| 1. Datos y clasificador | Por definir | 0, 1, 2, 5 |
| 2. Agente de voz | Por definir | 3, 5 |
| 3. Backend, panel y telefonía | Por definir | 0, 4, 5 |

#### Frente 1 · Datos y clasificador

*¿Qué tipo de llamada fue y qué tan seguros estamos?*

- Guía de etiquetado y guiones por categoría.
- Variaciones generadas con un modelo de lenguaje y revisadas a mano.
- Coordinación del etiquetado doble, kappa de Cohen y partición por guion.
- Las tres líneas base, Kev sin ajuste, calibración, prueba con opciones barajadas y
  casos de inyección; ajuste LoRA si hace falta.
- **Entrega:** una función o comando `clasificar(llamada) → clasificación` que corre por
  lotes, y la tabla de resultados.
- **Mientras tanto:** trabaja con el texto de los guiones hasta que el Frente 2 entregue
  las transcripciones automáticas.

#### Frente 2 · Agente de voz

*¿Cómo se atiende la llamada y se reúnen los tres datos?*

- Flujo en tiempo real: detección de voz → voz a texto → agente → texto a voz (Pipecat,
  llamada desde el navegador).
- Prompt del agente y defensas contra la manipulación.
- Formulario fijo como línea base del agente.
- Medición de latencia (mediana y percentil 95) y de la tasa de error de palabras.
- Conversión de los guiones del Frente 1 en audio con varias voces y ruido, y su
  transcripción automática (ya maneja las herramientas de voz).
- Voz clonada, opcional.
- **Entrega:** cada llamada terminada se guarda en el formato *Llamada*.
- **Mientras tanto:** no depende de nadie; empieza desde el primer día con el navegador.

#### Frente 3 · Backend, panel y telefonía

*¿Dónde queda todo y cómo lo ve el usuario?*

- API con FastAPI y base de datos SQLite según los dos formatos.
- Panel para celular: lista de llamadas, detalle con transcripción y pistas, corrección
  de etiquetas, lista de números sospechosos y exportación.
- Cloudflare Tunnel, conexión de Twilio con el flujo del Frente 2 y pruebas del desvío
  por ocupado y por no contesta con los operadores.
- Borrado de registros (Ley 1581).
- Montaje de Label Studio o de la hoja de etiquetado para el Frente 1.
- **Entrega:** una llamada real que aparece clasificada en el panel.
- **Mientras tanto:** trabaja con llamadas y clasificaciones de ejemplo en los dos
  formatos.

#### Formatos compartidos

**Llamada**, la produce el Frente 2:

```json
{
  "id": "…",
  "numero": "+57…",
  "inicio": "…",
  "fin": "…",
  "turnos": [{"hablante": "llamante|rita", "texto": "…", "t_inicio": 0.0, "t_fin": 2.1}],
  "datos": {"nombre": "…", "entidad": "…", "motivo": "…"},
  "latencias_ms": [820, 1140]
}
```

**Clasificación**, la produce el Frente 1:

```json
{
  "llamada_id": "…",
  "modelo": "kev-4b|regresion",
  "etiqueta": "estafa",
  "confianza": 0.87,
  "probabilidades": {"estafa": 0.87, "cobranza": 0.05},
  "pistas": {"pide_datos_bancarios": 0.92, "presiona_urgencia": 0.71}
}
```

El Frente 3 guarda y muestra los dos formatos sin necesidad de saber cómo se producen.

#### Trabajo compartido

- **Etiquetado:** cada conversación la etiquetan dos de las tres personas, repartiendo la
  carga para que nadie se quede esperando.
- **Evaluación final (semanas 7–8):** cada frente reporta sus cifras y el informe se arma
  en conjunto.

### Qué se recorta si no alcanza el tiempo

| Si pasa esto | Hacemos esto |
|---|---|
| La telefonía real no funciona o cuesta dinero | La demostración se hace con la llamada desde el navegador |
| La voz clonada agrega demasiada latencia | Voz sintética genérica |
| Kev-4B no cabe o es muy lento | Kev-0.8B o la regresión logística |
| Kev no le gana a la regresión logística | Se usa la regresión y se reporta el resultado negativo |
| La latencia no baja de 1,5 s | Frase de relleno corta mientras se genera la respuesta, y se reporta la latencia real |

### Estructura del repositorio (propuesta)

```
rita/
├── datos/            # guiones, conversaciones, etiquetas y particiones (sin datos personales)
├── clasificador/     # líneas base, Kev, calibración y evaluación
├── agente/           # flujo de voz en tiempo real (navegador y telefonía)
├── servidor/         # API y base de datos
├── panel/            # panel web
└── informe/          # resultados, figuras e informe final
```

---

## 3. Tecnologías gratuitas

| Pieza | Opción | Nota |
|---|---|---|
| Flujo de voz en tiempo real | [Pipecat](https://github.com/pipecat-ai/pipecat) (BSD-2) o [LiveKit Agents](https://github.com/livekit/agents) (Apache-2.0) | Traen detección de voz, interrupciones, flujo continuo y conexión con el navegador y con Twilio |
| Detección de voz | [Silero VAD](https://github.com/snakers4/silero-vad) | Corre en CPU |
| Voz a texto | [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (small o turbo, int8) | En CPU funciona para español. Hay APIs gratuitas con límites, pero el audio saldría de nuestra máquina |
| Agente | [Ollama](https://ollama.com) con un modelo pequeño en local, o el nivel gratuito de Groq o Gemini | Los límites gratuitos cambian; hay que revisarlos. La opción local es más coherente con la privacidad |
| Texto a voz | [Piper](https://github.com/rhasspy/piper) (rápido en CPU, voces en español) | También sirve para generar el audio del conjunto de datos con varias voces |
| Voz clonada (opcional) | OpenVoice v2 (MIT), XTTS-v2 o F5-TTS | XTTS-v2 y F5-TTS tienen licencia no comercial, válida para uso académico |
| Clasificador | Kev-4B con `transformers` en 4 bits, en Kaggle (~30 h de GPU a la semana) o Colab T4 | Corre por lotes después de colgar; no necesita servidor con GPU |
| Líneas base y calibración | scikit-learn | `TfidfVectorizer`, `LogisticRegression`, `CalibratedClassifierCV`, `cohen_kappa_score` |
| Etiquetado | [Label Studio](https://labelstud.io) o una hoja compartida | |
| Backend y base de datos | FastAPI + SQLite | Supabase gratuito si se necesita acceso remoto |
| Panel | HTML con HTMX, o React con Vite, servido por el mismo FastAPI | Pensado para verse en el celular |
| Exponer el servidor | [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/) desde el PC de un integrante | Colab se desconecta y no sirve como servidor permanente |
| Telefonía | Llamada desde el navegador para desarrollar; crédito de prueba de Twilio (Media Streams) para la demostración | Es la única pieza que no es gratuita a largo plazo |

Con esta combinación, todo lo que ocurre en tiempo real corre en CPU (con un modelo local
o una API gratuita para el agente), y la GPU gratuita solo se usa para evaluar Kev por
lotes.

---

## 4. Cambios respecto a la propuesta entregada

1. **Desvío de llamadas.** Se aclara que es desvío condicional (por ocupado o por no
   contesta), porque los operadores no desvían solo los números desconocidos.
2. **Voz clonada opcional.** La voz genérica pasa a ser la opción por defecto; la clonada
   agrega latencia y riesgos.
3. **Más llamadas legítimas.** Unas 150 en vez de 60–80, para poder medir la tasa de
   falsos positivos con algo de precisión.
4. **Evaluación sobre transcripciones automáticas** y un segundo conjunto de prueba con
   conversaciones actuadas, para reducir el sesgo de los datos sintéticos.
5. **Kappa de Cohen** para el acuerdo entre etiquetadores.
6. **La meta del 5 % se reporta con su intervalo de confianza**, diciendo si el intervalo
   permite afirmarla.
7. **Llamada desde el navegador** para desarrollar y evaluar, y como respaldo de la
   demostración.
8. **Kev corre por lotes** después de colgar, en una GPU gratuita.
9. **Privacidad.** Se declara qué pasa si se usa una API externa para la voz o el agente.
10. **Redacción.** Se corrige el cambio de sujeto en «El problema» y la frase unida con
    coma («además muchas de ellas…»).

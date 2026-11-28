# Guía de etiquetado

Esta guía define qué etiqueta lleva cada conversación. La usan los tres integrantes para
etiquetar por separado, y es lo que defendemos ante el jurado cuando pregunte «¿y cómo
decidieron qué era una estafa?».

## Cómo se etiqueta

1. **A ciegas.** Se etiqueta desde el CSV que genera `exportar_etiquetado.py`, que no
   muestra el guion ni la categoría con la que se escribió la conversación.
2. **Solo con lo que se dice en la llamada.** No se adivina lo que pasaría después.
3. **Una etiqueta por conversación**, de las siete de abajo. Si duda entre dos, aplica las
   reglas de frontera; si sigue en duda, escribe `si` en la columna `dudosa` y explica en
   `notas`.
4. **`descartar`** en la columna `etiqueta` si la conversación está rota: no tiene sentido,
   repite otra casi igual, o el modelo de lenguaje se salió del papel.

## Las siete categorías

| Etiqueta | Qué es | Señales típicas |
|---|---|---|
| `estafa` | Quiere engañar al usuario para sacarle dinero, datos o acceso. | Pide claves, códigos que llegan por mensaje, contraseñas o números de tarjeta; pide pagar para recibir un premio; suplanta a un banco, una autoridad o un familiar; presiona con urgencia o secreto. |
| `comercial` | Ofrece un producto o servicio. | Planes de telefonía, internet, seguros, tarjetas preaprobadas, créditos, clubes vacacionales. |
| `cobranza` | Reclama una deuda, propia del usuario o de un tercero. | Mora, cartera, obligación, acuerdo de pago, centrales de riesgo, cobro jurídico. |
| `encuesta` | Pide la opinión del usuario. | Encuestas de satisfacción, estudios de mercado, intención de voto. |
| `legitima` | Llamada con un propósito real para el usuario: un conocido o un servicio que sí usa. | Domicilios, citas médicas, entrevistas de trabajo, familiares o amigos con número nuevo, el colegio, el taller. |
| `equivocada` | Busca a otra persona o negocio y lo reconoce. | «¿Hablo con…?», «me equivoqué», «marqué mal». |
| `no_identificable` | No hay información suficiente para decidir. | Silencio, «aló, aló», cortes, mensajes automáticos sin contenido. |

## Reglas de frontera

Cuando una conversación encaja en dos categorías, manda la primera regla que aplique:

1. **Pedir claves, códigos de verificación, contraseñas o el número completo de una
   tarjeta es siempre `estafa`.** Ningún banco, operador o entidad seria los pide por
   teléfono, aunque la llamada suene profesional.
2. **Pedir un pago para recibir algo** (premio, devolución, liberar un paquete, evitar una
   captura) **es `estafa`**.
3. **Una cobranza que amenaza con cárcel o captura inmediata, o que pide consignar a una
   cuenta personal o a una billetera digital, es `estafa`.** Una cobranza que menciona
   centrales de riesgo, acuerdos de pago o puntos de pago oficiales es `cobranza`.
4. **Una oferta que termina pidiendo datos bancarios o un pago inmediato es `estafa`.**
   Una oferta que pide agendar una cita, enviar información o «¿le interesa?» es
   `comercial`.
5. **Una encuesta que termina vendiendo algo es `comercial`;** si termina pidiendo datos
   bancarios, `estafa`.
6. **Un banco u operador que llama a informar algo sin pedir datos sensibles** (por
   ejemplo, confirmar una compra respondiendo «sí» o «no», o avisar que la tarjeta está
   lista) **es `legitima`.** Estos son los casos difíciles más importantes: si los
   marcamos como estafa, el usuario pierde llamadas reales.
7. **«¿Hablo con X?» por una deuda de X es `cobranza`,** no `equivocada`.
8. **`no_identificable` no es «no estoy seguro».** Úsela solo si ni con toda la
   conversación se puede decidir. Si duda entre dos categorías, escoja una y marque
   `dudosa`.

## Ejemplos cortos

| Lo que dice quien llama | Etiqueta | Regla |
|---|---|---|
| «Le hablo de su banco, detectamos una compra; para bloquearla dígame el código que le llegó.» | `estafa` | 1 |
| «Le hablo de su banco, detectamos una compra por 300 000 en Medellín. ¿La reconoce? Si no, la bloqueamos y lo esperamos en la oficina.» | `legitima` | 6 |
| «Tiene una deuda con la tienda; si no consigna hoy a esta cuenta de ahorros, mañana va la policía.» | `estafa` | 3 |
| «Lo llamamos de la casa de cobranza por su obligación en mora; le ofrecemos un acuerdo de pago.» | `cobranza` | — |
| «Es una encuesta de satisfacción… y aprovecho para ofrecerle un plan con más gigas.» | `comercial` | 5 |
| «¿Doña Gloria? Es por la cuota del crédito que tiene atrasada.» | `cobranza` | 7 |

## Cómo escribir guiones (para quien escribe datos)

- **Basados en casos reales.** Las estafas, cobranzas y ofertas que reciben ustedes y sus
  familias, y las que reportan las noticias en Colombia. Anote la referencia en el campo
  `referencia` del guion (por ejemplo «llamada que recibió mi mamá, oct. 2026» o el
  enlace a la noticia).
- **Español de Colombia, como se habla:** muletillas, frases cortadas, «sumercé»,
  «qué pena», «mire».
- **Pueden nombrar entidades reales** (bancos, operadores), porque así suenan las llamadas
  de verdad. **Nunca** números de teléfono, cuentas, cédulas ni nombres completos de
  personas reales.
- **Al menos un tercio de casos difíciles** por categoría: legítimas que suenan a estafa
  (regla 6), cobranzas reales, ofertas agresivas que no son estafa, estafas educadas sin
  urgencia.
- **Variedad de largo:** desde dos frases hasta ocho turnos.
- Solo se escribe lo que dice **quien llama**; las preguntas de Rita las pone el sistema.

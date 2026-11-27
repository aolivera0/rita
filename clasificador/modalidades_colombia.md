# Modalidades de llamadas en Colombia (insumo para los guiones)

Recopilación hecha el 27 de noviembre de 2026 a partir de alertas de autoridades, bancos y
prensa colombiana. Sirve para escribir guiones realistas: cada guion debería citar en su
campo `referencia` la modalidad (`E1`, `L3`, …) y una de sus fuentes.

Todo está **parafraseado**: las notas describen cómo operan las llamadas, no las
transcriben. No copien textos de las noticias en los guiones; escriban con sus palabras
siguiendo los pasos descritos.

## Contexto en cifras (para el informe y el pitch)

- **Volumen:** Truecaller detectó ~9.577 millones de llamadas spam en Colombia en el primer
  semestre de 2026 (+21 % frente a 2025) y ~2.652 millones de intentos de estafa en ese
  periodo. Son estimaciones de una empresa, no cifras oficiales
  ([Infobae](https://www.infobae.com/tecno/2026/07/09/en-colombia-se-reportaron-casi-10000-millones-de-llamadas-spam-este-2026-datos-bancarios-los-mas-reportados/),
  [El Colombiano](https://www.elcolombiano.com/tecnologia/llamadas-spam-colombia-alcanzan-cifra-record-2026-AF38687025),
  [Portafolio](https://www.portafolio.co/tendencias/sociales/spam-telefonico-se-dispara-21-16-en-colombia-y-supera-9-576-millones-de-llamadas-en-seis-meses-498171)).
- **No todo el spam es estafa:** en 2025 hubo ~16.630 millones de llamadas spam; según
  Truecaller, ~80 % se relacionan con intentos de estafa y el resto con bancos o empresas
  que ofrecen productos ([Valora Analitik](https://www.valoraanalitik.com/?p=552225)).
  Esto justifica tener las categorías `comercial` y `cobranza` separadas de `estafa`.
- **Vishing es el esquema líder:** según TransUnion, las llamadas fraudulentas son el 39 %
  de los casos reportados por afectados ([El Tiempo](https://www.eltiempo.com/tecnosfera/novedades-tecnologia/cuidado-con-las-estafas-en-2026-conozca-las-cuatro-modalidades-mas-comunes-y-como-protegerse-de-fraudes-telefonicos-y-digitales-en-colombia-3525964)).
- **88 % recibió llamadas no deseadas** entre diciembre de 2025 y enero de 2026, y 11 % de
  ellas eran intentos de fraude bancario o promociones engañosas (Kaspersky, en
  [Noticias RCN](https://www.noticiasrcn.com/economia/estafas-telefonicas-colombia-falsos-call-centers-aplicaciones-987559)).
- **Extorsión por teléfono:** 6.077 denuncias de extorsión por llamada entre enero y
  noviembre de 2025 (+8,4 %), según la DIJIN; las llamadas extorsivas son el 41 % del delito
  que sale de las cárceles según la Procuraduría
  ([Noticias Caracol](https://www.noticiascaracol.com/colombia/llamadas-spam-en-colombia-subieron-21-en-el-primer-semestre-van-576-millones-registradas-rg10),
  [La FM](https://www.lafm.com.co/colombia/procuraduria-pide-acciones-por-aumento-de-llamadas-extorsivas-desde-las-carceles)).
- **Pérdidas:** más de $252 millones diarios en reclamaciones por fraude telefónico y por
  mensajes, según la CRC ([Occidente](https://occidente.co/secciones/tecnologia/estafas-telefonicas-en-colombia-vishing-smishing-modalidades/)).
- **No hay una cifra oficial** que diga qué modalidad produce más víctimas
  ([El Tiempo](https://www.eltiempo.com/datos/quien-nos-llama-tanto-esta-es-la-trampa-de-delincuentes-a-traves-de-llamadas-fantasma-para-robar-datos-en-colombia-3592663)).
  Es un buen argumento para el problema del pitch: hoy el usuario adivina.
- **Las bandas usan libretos:** la Policía de Bogotá encontró guiones escritos para que los
  «agentes» suenen creíbles, incluso imitando a grupos armados
  ([El Tiempo](https://www.eltiempo.com/bogota/asi-lo-perfila-un-estafador-cuando-lo-llama-por-telefono-para-robarle-su-dinero-3338814),
  [Noticias RCN](https://www.noticiasrcn.com/colombia/descubren-sofisticado-call-center-criminal-en-bogota-1028562),
  [Pulzo](https://www.pulzo.com/nacion/bogota/call-center-bogota-estafas-tenia-turnos-libretos-tumbar-gente-PP3844660A)).
  Por eso un clasificador de texto tiene sentido: las estafas repiten estructuras.

## Estafas (`estafa`)

| ID | Modalidad | Cómo transcurre la llamada | Señales para el clasificador | Fuentes |
|---|---|---|---|---|
| E1 | **Falso asesor del banco** | Dice ser del área de seguridad; avisa de un movimiento sospechoso o de un bloqueo; para «resolverlo» pide el código que llegó por SMS, la clave dinámica o pasar la plata a una «cuenta segura». El identificador puede mostrar el número real del banco. | Código, clave, token, cuenta segura, bloqueo, urgencia | [RCN (Kaspersky)](https://www.noticiasrcn.com/economia/mentiras-llamadas-ciberdelincuentes-fraudes-1010542), [Vanguardia](https://www.vanguardia.com/mundo/tecnologia/2026/04/09/la-llamada-que-parece-del-banco-y-termina-vaciando-la-cuenta-autoridades-advierten-sobre-esta-estafa/), [Pulzo](https://www.pulzo.com/tecnologia/frase-que-usan-estafadores-para-vaciar-cuentas-PP4634991), [El País](https://www.elpais.com.co/economia/banco-de-bogota-alerta-por-aumento-de-estafas-digitales-asi-operan-los-mensajes-y-llamadas-fraudulentas-1550.html) |
| E2 | **Falso asistente virtual del banco** | Voz que se presenta como asistente de seguridad; guía paso a paso, durante más de 20 minutos, un supuesto bloqueo de la cuenta, y en el camino obtiene datos y códigos. | Llamada larga, instrucciones paso a paso en la app, «asistente» | [Bogotá.gov.co](https://bogota.gov.co/mi-ciudad/seguridad/bogota-alerta-de-estafas-con-falsos-asistentes-de-seguridad-bancaria), [Noticias RCN](https://www.noticiasrcn.com/colombia/peligro-por-modalidad-de-estafa-telefonica-ladrones-se-hacen-pasar-como-asistentes-virtuales-1046092), [Semana](https://www.semana.com/tecnologia/articulo/responder-este-mensaje-de-un-asistente-virtual-podria-costarle-millones-de-pesos-y-hacerle-perder-sus-cuentas-bancarias/202642/) |
| E3 | **Falso soporte técnico con acceso remoto** | Del banco o del operador: dice que hay un virus o un movimiento raro; pide instalar AnyDesk, TeamViewer o una app «de protección» y desde ahí vacía las cuentas. | Instalar aplicación, «le voy a ayudar desde aquí», compartir pantalla | [Noticias RCN, feb. 2026](https://www.noticiasrcn.com/economia/estafas-telefonicas-colombia-falsos-call-centers-aplicaciones-987559) |
| E4 | **Falso operador de telefonía** | Dice ser de Claro, Movistar o Tigo; habla de una falla, una actualización o el bloqueo de la línea; pide un código para «verificar» y con él roba el WhatsApp o duplica la SIM. | Línea, SIM, código de verificación, WhatsApp | [RCN (Kaspersky)](https://www.noticiasrcn.com/economia/mentiras-llamadas-ciberdelincuentes-fraudes-1010542), [La FM](https://www.lafm.com.co/tecnologia/sim-swapping-como-funciona-el-nuevo-fraude-para-clonar-la-sim-de-su-telefono), [Publimetro](https://www.publimetro.co/tecnologia/2025/12/18/estafa-navidena-cuidado-si-se-queda-sin-senal-en-su-celular-seguro-estan-clonando-su-sim/) |
| E5 | **Paquete retenido en el aeropuerto o la aduana** | Se presenta como supervisor de carga; pregunta si espera un paquete y quién lo envió; dice que el escáner encontró varios equipos y que el paquete supera el tope de libre importación (US$3.700); exige una multa inmediata para evitar un «cobro jurídico» y embargo, y pide fotos de la cédula por WhatsApp. Saben de antemano que la víctima espera un envío. | Multa, aduana, contrabando, embargo, pago inmediato | [El Tiempo (libretos de la Policía)](https://www.eltiempo.com/bogota/asi-lo-perfila-un-estafador-cuando-lo-llama-por-telefono-para-robarle-su-dinero-3338814), [DIAN](https://www.dian.gov.co/aduanas/Documents/Fraudes-de-trafico-postal-y-envios-urgentes.pdf), [Publimetro, mar. 2026](https://www.publimetro.co/noticias/2026/03/12/no-caiga-asi-es-la-millonaria-estafa-con-falsos-paquetes-de-la-dian-que-vacia-cuentas-en-colombia/), [Infobae, mar. 2026](https://www.infobae.com/colombia/2026/03/11/dian-alerta-que-delincuentes-estan-enviando-cartas-falsas-para-cobrar-supuestos-aranceles-por-paquetes-internacionales/) |
| E6 | **Falso funcionario de impuestos (DIAN, Hacienda)** | Cobra una deuda tributaria o una multa inexistente; menciona mandamiento de pago o embargo; ofrece descuento si paga hoy a una cuenta. La DIAN no cobra a cuentas personales ni por empresas de mensajería. | Embargo, mandamiento de pago, descuento por pago inmediato | [DIAN](https://www.dian.gov.co/Prensa/Paginas/NG-Comunicado-de-Prensa-064-2026.aspx), [El Tiempo](https://www.eltiempo.com/bogota/bogota-asi-operaba-empresa-criminal-que-estafo-a-1-500-bogotanos-809987), [Portafolio](https://www.portafolio.co/mis-finanzas/falsas-multas-por-el-cobro-de-los-impuestos-evite-caer-en-esta-modalidad-de-estafa-571480) |
| E7 | **Falso funcionario de la Superfinanciera** | Dice que, por sanciones a los bancos, la víctima tiene un saldo a favor o un premio; para recibirlo hay que consignar primero. | Saldo a favor, devolución, consignar antes | [El Espectador](https://www.elespectador.com/?p=3005579) |
| E8 | **Premio o sorteo** | Felicita por un premio (moto, viaje, electrodoméstico); pide una «tarifa de liberación», impuestos o fotos de los documentos para entregarlo. | Ganó, sorteo, tarifa, impuestos del premio | [Noticias RCN, feb. 2026](https://www.noticiasrcn.com/economia/estafas-telefonicas-colombia-falsos-call-centers-aplicaciones-987559), [El Tiempo, 2026](https://www.eltiempo.com/tecnosfera/novedades-tecnologia/cuidado-con-las-estafas-en-2026-conozca-las-cuatro-modalidades-mas-comunes-y-como-protegerse-de-fraudes-telefonicos-y-digitales-en-colombia-3525964) |
| E9 | **Familiar en apuros (con voz clonada)** | «¿Sabe quién habla?»; un hijo, sobrino o nieto en un accidente, detenido o sin celular; pide dinero ya y que no le cuente a nadie. En 2026 usan voces clonadas con IA y sonidos de fondo (sirenas, llanto). | Parentesco sin nombre, urgencia, secreto, transferencia | [Publimetro, may. 2026](https://www.publimetro.co/tecnologia/2026/05/04/cuelgue-de-inmediato-la-estafa-del-familiar-en-apuros-con-clonacion-de-voz-por-ia-que-vacia-cuentas-de-whatsapp/), [El Tiempo](https://www.eltiempo.com/tecnosfera/novedades-tecnologia/estan-clonando-las-voces-de-familiares-con-ia-para-estafar-asi-opera-el-nuevo-engano-de-los-ciberdelincuentes-en-colombia-3391367), [Occidente, oct. 2026](https://occidente.co/secciones/tecnologia/clonacion-de-voz-con-inteligencia-artificial-estafas/) |
| E10 | **Falso secuestro o extorsión (muchas veces desde cárceles)** | Dice tener a un familiar o pertenecer a un grupo armado; amenaza y exige un pago por su «liberación» o para no hacer daño. Las bandas usan datos filtrados para sonar creíbles. | Amenaza, grupo armado, liberación, pago | [Noticias RCN](https://www.noticiasrcn.com/colombia/nueva-modalidad-de-extorsion-con-llamadas-de-carceles-440547), [El Colombiano (Cómbita)](https://www.elcolombiano.com/colombia/estafas-carcel-combita-el-salvador-extorsion-telefonica-DB32887730), [El Tiempo](https://www.eltiempo.com/bogota/desarticulan-red-de-39-extorsionistas-que-operaban-desde-carceles-en-bogota-entre-los-capturados-hay-funcionarios-del-inpec-3517015), [La FM](https://www.lafm.com.co/tecnologia/asi-opera-la-nueva-estafa-que-ataca-a-colombianos-en-estados-unidos-con-falsos) |
| E11 | **Falsa casa de cobranza** | Cobra una deuda que no existe o que ya se pagó; amenaza con embargo, cárcel o con cobrarle a los contactos; ofrece descuento si consigna hoy a una cuenta. | Deuda desconocida, amenaza desproporcionada, cuenta personal | [El País](https://www.elpais.com.co/colombia/tenga-cuidado-con-falsas-deudas-estarian-amenazando-y-extorsionando-a-nos.html), [El Tiempo](https://www.eltiempo.com/bogota/bogota-asi-operaba-empresa-criminal-que-estafo-a-1-500-bogotanos-809987) |
| E12 | **Falso subsidio (Prosperidad Social, Renta Ciudadana, adulto mayor)** | Conoce el nombre completo y la cédula; dice que la persona salió beneficiaria y cobra la «inscripción» o pide documentos. Los programas no cobran ni requieren inscripción. | Subsidio, beneficiario, cobro por trámite | [El Tiempo](https://www.eltiempo.com/economia/finanzas-personales/cuidado-con-las-llamadas-de-estafa-supuestamente-de-prosperidad-social-prometen-la-entrega-de-subsidios-3401971), [Portafolio](https://www.portafolio.co/economia/gobierno/si-recibe-esta-llamada-de-prosperidad-social-en-colombia-podria-ser-una-estafa-620285), [Blu Radio](https://lakalle.bluradio.com/sociedad/informacion-de-servicio/alerta-por-estafa-a-adultos-mayores-suplantan-prosperidad-social-ofreciendo-subsidios-so35) |
| E13 | **Pensión o «prueba de vida»** | Dice ser de la entidad de pensiones; hay pendientes o hay que actualizar datos; pide fotos de documentos o el pago de una tasa. | Pensión, actualizar datos, tasa | [RCN (Kaspersky)](https://www.noticiasrcn.com/economia/mentiras-llamadas-ciberdelincuentes-fraudes-1010542) |
| E14 | **Falsa oferta de empleo** | Mensaje grabado: recibieron la hoja de vida y hay que agregar un número de WhatsApp; desde ahí roban la cuenta o cobran exámenes y certificados. | Hoja de vida + WhatsApp, cobro por contratar | [Bogotá.gov.co](https://bogota.gov.co/en/node/303737), [Publimetro, jun. 2026](https://www.publimetro.co/bogota/2026/06/26/recibimos-tu-hoja-de-vida-agregame-a-whatsapp-pilas-esa-llamada-termina-en-estafa/), [Noticias Caracol](https://www.noticiascaracol.com/economia/como-reconocer-una-oferta-laboral-falsa-aqui-una-guia-detallada-so35) |
| E15 | **Falsos productos bancarios** | Ofrece un crédito o una tarjeta preaprobada; para desembolsar pide un pago anticipado o los datos de la tarjeta. Una banda («Los Call Center») habría estafado a ~6.900 personas así. | Crédito aprobado + pago previo | [Blu Radio](https://www.bluradio.com/judicial/cayeron-los-call-center-estafaron-a-mas-de-6-900-personas-con-venta-ficticia-de-servicios-bancarios), [La FM](https://www.lafm.com.co/judicial/tome-nota-la-modalidad-de-estafa-falsos-asesores-de-bancos-que-llaman-ofrecer-productos), [El Tiempo](https://www.eltiempo.com/tecnosfera/novedades-tecnologia/cuidado-con-las-estafas-en-2026-conozca-las-cuatro-modalidades-mas-comunes-y-como-protegerse-de-fraudes-telefonicos-y-digitales-en-colombia-3525964) |
| E16 | **Inversión o criptomonedas** | Un «asesor» ofrece rentabilidad alta y rápida, lleva a Telegram o a una plataforma, a veces con la imagen de una celebridad; pide depositar. | Rentabilidad garantizada, plataforma, depositar | [Portafolio](https://www.portafolio.co/tecnologia/fraudes-con-criptomonedas-e-ia-ya-moverian-52-600-millones-en-colombia-segun-asoblockchain-503794), [El Tiempo](https://www.eltiempo.com/economia/finanzas-personales/estas-son-las-estafas-con-criptomonedas-mas-comunes-evite-caer-en-ellas-783908) |
| E17 | **Problema con una compra en línea** | Un supuesto asesor de una tienda grande (Amazon u otra) avisa de un cargo o un pedido con problemas; pide datos de la tarjeta o acceso a la app de pagos. | Cargo no reconocido, pedido, datos de tarjeta | [El Tiempo, 2026](https://www.eltiempo.com/tecnosfera/novedades-tecnologia/cuidado-con-las-estafas-en-2026-conozca-las-cuatro-modalidades-mas-comunes-y-como-protegerse-de-fraudes-telefonicos-y-digitales-en-colombia-3525964), [RCN (Kaspersky)](https://www.noticiasrcn.com/economia/mentiras-llamadas-ciberdelincuentes-fraudes-1010542) |
| E18 | **Seguros con urgencia** | Dice que un seguro asociado a la tarjeta se va a cobrar o vencer y que hay que cancelarlo ya «confirmando» datos. | Seguro, cobro inminente, confirmar datos | [La República](https://www.larepublica.co/finanzas/banco-de-bogota-alerta-sobre-la-modalidad-de-fraudes-de-seguros-y-llamadas-urgentes-4339244) |

## No identificable (`no_identificable`)

| ID | Modalidad | Cómo transcurre | Fuentes |
|---|---|---|---|
| N1 | **Llamada fantasma o silenciosa** | Nadie habla, o solo una grabación tipo «¿me escucha?»; sirve para validar que el número está activo y a qué hora contesta. | [Portafolio](https://www.portafolio.co/tecnologia/llamadas-fantasma-en-colombia-asi-verifican-los-delincuentes-que-numeros-telefonicos-siguen-activos-504276), [El Universal](https://www.eluniversal.com.co/sucesos/2026/05/18/le-llaman-al-celular-y-no-le-hablan-policia-revelo-como-operan-las-llamadas-fantasmas/), [RCN (Kaspersky)](https://www.noticiasrcn.com/economia/mentiras-llamadas-ciberdelincuentes-fraudes-1010542) |

Ojo: una llamada fantasma no es «estafa» en el momento: no se dice nada. Por la regla 8 de
la guía va como `no_identificable`. Esto es un límite que vale la pena contar al jurado.

## Las contrapartes legítimas (casos difíciles)

Son las que impiden que el modelo aprenda «banco = estafa». Cada modalidad de estafa
debería tener al menos un guion legítimo parecido.

| ID | Categoría | Contraparte | Qué la distingue | Fuentes |
|---|---|---|---|---|
| L1 | `legitima` | **El banco real avisa de una compra** | Pregunta si reconoce la transacción y sugiere bloquear desde la app o llamar al número de la tarjeta; **nunca** pide claves, códigos ni transferir. | [Noticias RCN](https://www.noticiasrcn.com/economia/estafas-telefonicas-colombia-falsos-call-centers-aplicaciones-987559), [Bogotá.gov.co](https://bogota.gov.co/mi-ciudad/seguridad/bogota-alerta-de-estafas-con-falsos-asistentes-de-seguridad-bancaria) |
| L2 | `legitima` | **La transportadora confirma una entrega** | Confirma dirección u horario; si hay un pago contra entrega, es el valor del pedido y se paga al recibir, no por adelantado a una cuenta. | (contraparte de E5) |
| L3 | `legitima` | **Una entidad pública real** | Informa o recuerda un trámite sin cobrar; remite a sus canales oficiales. Prosperidad Social dice que tiene un único número de contacto. | [Portafolio](https://www.portafolio.co/economia/gobierno/si-recibe-esta-llamada-de-prosperidad-social-en-colombia-podria-ser-una-estafa-620285) |
| L4 | `legitima` | **Familiar con número nuevo** | Dice quién es con nombre y contexto, no pide plata con urgencia ni secreto. | (contraparte de E9) |
| L5 | `legitima` | **Proceso de selección real** | Ofrece entrevista en una fecha; no cobra nada ni pide agregar un WhatsApp desconocido. | (contraparte de E14) |
| C1 | `cobranza` | **Cobranza legítima** | Deuda concreta con un acreedor nombrado; ofrece acuerdo de pago; menciona centrales de riesgo, no cárcel. La Ley 2300 de 2023 («Dejen de fregar») limita el horario (L–V 7 a. m.–7 p. m., sábados 8 a. m.–3 p. m., nunca domingos ni festivos). | [Ley 2300 de 2023](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=213990), [Portafolio](https://www.portafolio.co/economia/finanzas/deudas-en-colombia-que-dias-los-bancos-tienen-prohibido-llamarlo-642565) |
| M1 | `comercial` | **Telemercadeo legal** | Ofertas reales de planes, tarjetas, seguros o créditos sin pago anticipado; buena parte del spam son bancos y empresas ofreciendo productos. | [Valora Analitik](https://www.valoraanalitik.com/?p=552225), [El Tiempo](https://www.eltiempo.com/bogota/asi-lo-perfila-un-estafador-cuando-lo-llama-por-telefono-para-robarle-su-dinero-3338814) |
| S1 | `encuesta` | **Encuestas de satisfacción, de mercado y de opinión** | Preguntan, no venden ni piden datos financieros. No encontré alertas específicas para Colombia; escríbanlas desde la experiencia propia. | — |

## Datos externos descargados (en `datos/externos/`, fuera de git)

| Fuente | Qué es en realidad | Cómo usarlo |
|---|---|---|
| [International Robocalls Dataset](https://zenodo.org/records/21066049) (CC BY-NC 4.0) | 841 transcripciones de robollamadas (725 de EE. UU., 116 internacionales), **todas en inglés** aunque el artículo hable de varios idiomas: el archivo de texto publicado no trae ninguna en español. Campañas: Google Business, spam financiero, beneficios, IRS, garantía de vehículos, alertas bancarias, cobro de deudas de la India. | **No sirve como prueba en español.** Solo como referencia de estructuras de robollamadas (por ejemplo, para E14 grabado o N1). |
| [BothBosu/scam-dialogue](https://huggingface.co/datasets/BothBosu/scam-dialogue) (Apache-2.0) | 1.600 diálogos sintéticos en inglés (~244 palabras), 8 escenarios × 200, mitad estafa y mitad no. | **Materia prima para adaptar al contexto colombiano**, solo para entrenamiento (ver tabla de abajo). |

Correspondencia de BothBosu con nuestras categorías y modalidades:

| Escenario BothBosu | ¿Estafa? | Nuestra categoría | Adaptación colombiana |
|---|---|---|---|
| `ssn` (número de Seguro Social comprometido) | sí | `estafa` | E6 (DIAN), E12 (subsidio) o E13 (pensión) |
| `refund` (reembolso) | sí | `estafa` | E7 (saldo a favor) o E17 (compra en línea) |
| `reward` (premio) | sí | `estafa` | E8 |
| `support` (soporte técnico) | sí | `estafa` | E3 o E4 |
| `delivery` (entrega) | no | `legitima` | L2 |
| `insurance` (seguro) | no | `comercial` | M1 |
| `telemarketing` | no | `comercial` | M1 |
| `wrong` (número equivocado) | no | `equivocada` | — |

BothBosu no trae cobranza, encuestas ni llamadas silenciosas: esas salen solo de los guiones
del equipo. Sus estafas son de EE. UU. (Seguro Social, IRS), así que no se traducen
literalmente: se adaptan a la modalidad colombiana equivalente, y en el informe se declara
que se usaron como base.

## Reparto sugerido de los ~90 guiones

| Categoría | Guiones | De qué |
|---|---|---|
| `estafa` | 30 | E1–E18: 2 de E1, E2, E5, E9, E10 y E11 (las más reportadas); 1–2 del resto |
| `legitima` | 20 | L1–L5 (al menos 8 casos difíciles) más domicilios, citas médicas, conocidos |
| `comercial` | 10 | M1: planes, tarjetas, seguros, créditos sin pago previo, clubes |
| `cobranza` | 10 | C1 con distintos acreedores y tonos (firme pero dentro de la ley) |
| `encuesta` | 8 | S1 |
| `equivocada` | 6 | Incluyendo «¿hablo con…?» que no es cobranza |
| `no_identificable` | 6 | N1 y llamadas cortadas |

Las estafas tienen más guiones porque hay más modalidades distintas; el desbalance real
(muchas más estafas que encuestas) lo maneja el peso de las clases al entrenar.

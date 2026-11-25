"""Conversaciones sintéticas de juguete para el prototipo.

Cada guion es una lista de turnos de quien llama, con huecos ({NOMBRE}, {BANCO}, ...)
que se llenan al azar. Todas las variaciones de un guion comparten el mismo `guion_id`,
para poder partir por guion y no por llamada suelta (partición sin fugas).

Las empresas y bancos son inventados. Esto NO es el conjunto de datos del proyecto:
solo sirve para que el prototipo tenga un clasificador que funcione.
"""

from __future__ import annotations

import random
import re

CATEGORIAS = [
    "estafa",
    "comercial",
    "cobranza",
    "encuesta",
    "legitima",
    "equivocada",
    "no_identificable",
]

NOMBRES_CATEGORIA = {
    "estafa": "Estafa",
    "comercial": "Promoción o comercial",
    "cobranza": "Cobranza",
    "encuesta": "Encuesta",
    "legitima": "Conocido o legítima",
    "equivocada": "Equivocada",
    "no_identificable": "No identificable",
}

HUECOS = {
    "NOMBRE": ["Carlos", "Andrea", "Juan Pablo", "Luisa", "Jhon", "Marcela", "Diego",
               "Paola", "Andrés", "Camila", "Esteban", "Natalia", "Sergio", "Valentina"],
    "OTRO": ["Martha Rodríguez", "Jorge Pérez", "Doña Gloria", "Ricardo Gómez",
             "Sandra Muñoz", "Don Hernando"],
    "BANCO": ["Banco Andino", "Banco Cóndor", "Financiera Sabana", "Banco del Llano",
              "Crediunión"],
    "OPERADOR": ["Telemóvil", "ConectaPlus", "Celumax", "Red Andina Móvil"],
    "TIENDA": ["Almacenes Prado", "Tienda La Rebaja Total", "Muebles Hogar Feliz",
               "Electro Ofertas"],
    "EMPRESA": ["Logística Andes", "Soluciones TIC", "Grupo Altamira", "Constructora Ceiba"],
    "COBRANZA": ["Cobranzas Integrales", "Recaudos del Centro", "Gestión de Cartera Nacional"],
    "ENCUESTADORA": ["Opinión Pública Andina", "Centro Nacional de Encuestas",
                     "Estudios de Mercado Colibrí"],
    "CLINICA": ["Clínica San Rafael del Norte", "Centro Médico Los Alpes",
                "Consultorio Odontológico Sonrisas"],
    "MONTO": ["quinientos mil", "un millón doscientos", "trescientos ochenta mil",
              "dos millones", "ochocientos mil", "ciento cincuenta mil"],
    "PRECIO": ["cuarenta y nueve mil novecientos", "treinta y cinco mil", "sesenta mil",
               "veintinueve mil novecientos"],
    "GB": ["veinte", "cincuenta", "ochenta", "cien"],
    "MIN": ["diez", "quince", "veinte", "cinco"],
    "HORA": ["las ocho de la mañana", "las dos de la tarde", "las diez y media",
             "las cuatro"],
    "DIA": ["lunes", "martes", "miércoles", "jueves", "viernes"],
    "PREMIO": ["moto cero kilómetros", "nevera", "televisor de setenta pulgadas",
               "viaje a San Andrés"],
    "TEMA": ["servicios públicos", "transporte en la ciudad", "hábitos de consumo",
             "las próximas elecciones"],
}

MULETILLAS = ["", "", "", "mire, ", "oiga, ", "pues ", "eh, ", "bueno, "]

GUIONES: dict[str, list[list[str]]] = {
    "estafa": [
        ["Buenas tardes, le habla {NOMBRE} del área de seguridad de {BANCO}.",
         "Detectamos un movimiento sospechoso en su tarjeta por {MONTO} pesos.",
         "Para bloquearlo necesito que me confirme el número de la tarjeta y la clave que le llega por mensaje.",
         "Es urgente, en {MIN} minutos la transacción se hace efectiva."],
        ["Felicitaciones, le habla {NOMBRE} de Promociones Fortuna.",
         "Usted se ganó una {PREMIO} en nuestro sorteo de aniversario.",
         "Para reclamarla solo tiene que consignar {MONTO} pesos de impuestos hoy mismo.",
         "Le doy el número de cuenta, pero tiene que ser antes de las cinco."],
        ["Hola, ¿sabe quién le habla? Soy yo, su sobrino.",
         "Estoy en un problema muy grande, me detuvo la policía.",
         "Necesito que me mande {MONTO} por transferencia ya mismo.",
         "Por favor no le diga a nadie de la familia."],
        ["Le habla el agente {NOMBRE} de la Fiscalía.",
         "Su número de cédula aparece vinculado a un proceso penal.",
         "Para evitar la orden de captura debe pagar una multa de {MONTO} pesos hoy.",
         "Si cuelga se activa el proceso de inmediato."],
        ["Hola, soy {NOMBRE} del soporte técnico de {OPERADOR}.",
         "Su línea va a ser suspendida por actividad irregular.",
         "Dígame el código de seis dígitos que le acaba de llegar por mensaje para verificar.",
         "Tiene que ser ahora mismo o pierde el número."],
        ["Buenos días, le hablo de {BANCO}, usted tiene un reembolso pendiente.",
         "Le vamos a devolver {MONTO} pesos de un cobro mal hecho.",
         "Necesito su usuario y contraseña de la banca en línea para hacer la devolución.",
         "Es un trámite rápido, solo por hoy."],
    ],
    "comercial": [
        ["Buenos días, le habla {NOMBRE} de {OPERADOR}.",
         "Lo llamamos porque usted fue seleccionado para un plan de {GB} gigas.",
         "Por solo {PRECIO} pesos mensuales, con minutos ilimitados.",
         "¿Le interesa que le haga el cambio de plan?"],
        ["Buenas tardes, le habla {NOMBRE} de {BANCO}.",
         "Usted tiene una tarjeta de crédito preaprobada sin cuota de manejo.",
         "Solo tenemos que agendar una cita para que firme los papeles en la oficina.",
         "¿Qué día le queda bien?"],
        ["Hola, mi nombre es {NOMBRE}, le llamo de Seguros Protección Total.",
         "Le estamos ofreciendo un seguro exequial para toda la familia.",
         "La cuota es de {PRECIO} pesos al mes y cubre hasta seis personas.",
         "¿Quiere que le envíe la información por correo?"],
        ["Qué tal, le habla {NOMBRE} de {OPERADOR} hogar.",
         "Tenemos una promoción de internet de trescientas megas para su casa.",
         "La instalación es gratis si contrata este mes.",
         "¿Ya tiene internet en su hogar?"],
        ["Buenas, le habla {NOMBRE} del Club Vacacional Horizonte.",
         "Lo invitamos a una presentación con desayuno gratis este sábado.",
         "Tenemos paquetes a Cartagena y Santa Marta con descuento.",
         "Solo tiene que venir con su pareja."],
    ],
    "cobranza": [
        ["Buenos días, le habla {NOMBRE} de {COBRANZA}.",
         "Lo llamamos por una obligación pendiente con {BANCO} por {MONTO} pesos.",
         "Queremos ofrecerle un acuerdo de pago antes de que lo reporten a centrales de riesgo.",
         "¿Usted puede hacer un abono este mes?"],
        ["Buenas tardes, ¿me comunica con {OTRO}?",
         "Es por una deuda con {TIENDA}.",
         "Si usted lo conoce, dígale que se comunique, tiene una mora de noventa días.",
         "Este número aparece como referencia."],
        ["Le habla {NOMBRE} del área de cartera de {OPERADOR}.",
         "Su factura del mes pasado está vencida.",
         "Puede pagar en cualquier punto autorizado o por la página web.",
         "Si ya pagó, por favor ignore este mensaje."],
        ["Buenas, habla {NOMBRE} de la oficina de abogados Restrepo y Asociados.",
         "Tenemos a cargo el cobro jurídico de un crédito a su nombre.",
         "Le pedimos comunicarse con nosotros para normalizar su crédito.",
         "Así evitamos iniciar el proceso de embargo."],
    ],
    "encuesta": [
        ["Buenos días, le habla {NOMBRE} de {ENCUESTADORA}.",
         "Estamos haciendo una encuesta sobre {TEMA}.",
         "Son solo tres preguntas, le toma dos minutos.",
         "¿Me regala un momento?"],
        ["Hola, le llamamos de {OPERADOR} para calificar la atención que recibió.",
         "En una escala del uno al cinco, ¿qué tan satisfecho quedó?",
         "Su opinión nos ayuda a mejorar el servicio.",
         "Gracias por su tiempo."],
        ["Buenas tardes, mi nombre es {NOMBRE}, somos estudiantes de la universidad.",
         "Estamos haciendo un estudio de mercado sobre {TEMA}.",
         "La encuesta es anónima y no le vamos a vender nada.",
         "¿Podría responder unas preguntas?"],
        ["Buenas, hablo de {ENCUESTADORA}, estamos midiendo intención de voto.",
         "Solo queremos saber su opinión sobre {TEMA}.",
         "Es un estudio de opinión, no necesitamos sus datos.",
         "Son cinco preguntas cortas."],
    ],
    "legitima": [
        ["Hola, soy {NOMBRE}, el domiciliario de {TIENDA}.",
         "Estoy afuera con su pedido.",
         "No encuentro el número de la casa, ¿me puede abrir?",
         "Estoy frente a la portería."],
        ["Buenos días, le hablo del consultorio del doctor {NOMBRE}, de {CLINICA}.",
         "Lo llamamos para confirmar su cita de mañana a {HORA}.",
         "Recuerde llegar quince minutos antes con su documento.",
         "Si no puede asistir, avísenos para reprogramarla."],
        ["Hola, buenas tardes, soy {NOMBRE} de recursos humanos de {EMPRESA}.",
         "Revisamos su hoja de vida para la vacante que publicamos.",
         "Queremos invitarlo a una entrevista el {DIA}.",
         "Le envío los detalles al correo."],
        ["Quiubo, soy {NOMBRE}, el compañero de la universidad.",
         "Cambié de número, guárdelo.",
         "Lo llamaba por lo del trabajo en grupo del {DIA}.",
         "Hablamos más tarde."],
        ["Hola mijo, soy su tía, este es mi número nuevo.",
         "Lo llamo para lo del almuerzo del domingo en la casa.",
         "Dígale a su mamá que lleve el postre.",
         "Bueno, nos vemos."],
        ["Buenas tardes, le habla {NOMBRE} del taller.",
         "Su carro ya está listo, le cambiamos las pastillas de freno.",
         "Puede pasar a recogerlo hoy hasta las seis.",
         "Cualquier cosa me escribe."],
        ["Hola, soy {NOMBRE}, la vecina del apartamento de abajo.",
         "Le pedí el número a la administración.",
         "Es que hay una gotera que viene de su baño.",
         "¿Puede revisar cuando llegue?"],
    ],
    "equivocada": [
        ["¿Aló? ¿Hablo con {OTRO}?",
         "Ah, ¿no? Perdón, me equivoqué de número.",
         "Qué pena con usted."],
        ["Buenas, ¿es la panadería La Espiga?",
         "Quería encargar unos pandebonos.",
         "Ay, disculpe, marqué mal."],
        ["¿{OTRO}? Ah, no, entonces me dieron mal el número.",
         "Disculpe la molestia, que esté bien."],
        ["Buenas, llamo por el apartamento en arriendo que publicaron.",
         "¿No es este número? Qué pena, debí copiarlo mal.",
         "Gracias, chao."],
    ],
    "no_identificable": [
        ["Aló, aló.", "No se escucha.", "Aló."],
        ["Eh.", "Sí.", "Bueno."],
        ["¿Quién es?", "No, nada.", "Ya llamo después."],
        ["Por favor espere en línea.", "Su llamada es importante para nosotros."],
        ["...", "Aló.", "Se cortó."],
    ],
}


def _llenar(texto: str, rng: random.Random) -> str:
    return re.sub(r"\{(\w+)\}", lambda m: rng.choice(HUECOS[m.group(1)]), texto)


def _variacion(turnos: list[str], rng: random.Random) -> list[str]:
    salida = []
    for i, turno in enumerate(turnos):
        # A veces quien llama no dice la última frase.
        if i == len(turnos) - 1 and len(turnos) > 2 and rng.random() < 0.3:
            continue
        texto = _llenar(turno, rng)
        muletilla = rng.choice(MULETILLAS)
        if muletilla:
            texto = muletilla + texto[0].lower() + texto[1:]
        salida.append(texto)
    return salida


def generar(variaciones_por_guion: int = 10, semilla: int = 7) -> list[dict]:
    """Devuelve una lista de {'guion_id', 'categoria', 'turnos'}."""
    rng = random.Random(semilla)
    ejemplos = []
    for categoria, guiones in GUIONES.items():
        for g, turnos in enumerate(guiones):
            for _ in range(variaciones_por_guion):
                ejemplos.append({
                    "guion_id": f"{categoria}-{g}",
                    "categoria": categoria,
                    "turnos": _variacion(turnos, rng),
                })
    return ejemplos

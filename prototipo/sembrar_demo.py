"""Llena la base de datos con llamadas de ejemplo para que el panel no arranque vacío.

Uso:  .venv/bin/python sembrar_demo.py
"""

import random
import uuid
from datetime import datetime, timedelta

from rita import db
from rita.agente import AgenteFormulario
from rita.clasificador import Clasificador
from rita.datos_sinteticos import generar

rng = random.Random(3)
clasificador = Clasificador()
ejemplos = generar(variaciones_por_guion=1, semilla=11)
rng.shuffle(ejemplos)

# Algunos números repetidos, para que la lista de números tenga historial.
numeros = [f"+57 3{rng.randint(10, 99)} {rng.randint(100, 999)} {rng.randint(1000, 9999)}"
           for _ in range(8)]
inicio = datetime.now() - timedelta(days=3)

for i, ej in enumerate(ejemplos[:14]):
    agente = AgenteFormulario()
    turnos = [{"hablante": "rita", "texto": agente.saludo(), "t": 0.0}]
    t = 0.0
    for frase in ej["turnos"]:
        t += round(rng.uniform(3, 7), 1)
        respuesta = agente.responder(frase)
        turnos += [{"hablante": "llamante", "texto": frase, "t": t},
                   {"hablante": "rita", "texto": respuesta, "t": t}]
        if agente.terminada:
            break
    momento = inicio + timedelta(hours=5 * i, minutes=rng.randint(0, 59))
    llamada = {
        "id": uuid.uuid4().hex[:12],
        "numero": rng.choice(numeros),
        "inicio": momento.isoformat(timespec="seconds"),
        "fin": (momento + timedelta(seconds=t + 4)).isoformat(timespec="seconds"),
        "turnos": turnos,
        "datos": agente.datos,
        "latencias_ms": [rng.randint(900, 1800) for _ in range(len(turnos) // 2)],
        "agente": "formulario (ejemplo)",
    }
    texto = " ".join(x["texto"] for x in turnos if x["hablante"] == "llamante")
    db.guardar(llamada, clasificador.clasificar(texto, llamada["id"]))

print(f"Listo: {len(db.listar())} llamadas en {db.RUTA}")

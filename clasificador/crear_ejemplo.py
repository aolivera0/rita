"""Crea un directorio de datos de EJEMPLO para probar el flujo completo sin datos reales.

Toma los 35 guiones de juguete del prototipo, genera 10 variaciones por guion y simula
dos anotadores (uno copia la categoría del guion; el otro se equivoca en ~10 % de los
casos). NO son datos del proyecto: solo sirven para ver que los scripts funcionan.

Uso:
    python crear_ejemplo.py                       # escribe datos/ejemplo/
    python validar.py --datos datos/ejemplo
    python acuerdo.py --datos datos/ejemplo
    python particionar.py --datos datos/ejemplo --congelar
    python evaluar.py --datos datos/ejemplo
"""

import random
import shutil
import sys
from pathlib import Path

from rita_clasificador.datos import CATEGORIAS, DATOS, escribir_csv, escribir_jsonl

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "prototipo"))
from rita.datos_sinteticos import GUIONES, generar  # noqa: E402

DESTINO = DATOS / "ejemplo"


def main() -> int:
    if DESTINO.exists():
        shutil.rmtree(DESTINO)
    guiones = [{"guion_id": f"{cat}-{i}", "categoria": cat, "autor": "prototipo",
                "referencia": "guion de juguete del prototipo", "turnos": turnos}
               for cat, lista in GUIONES.items() for i, turnos in enumerate(lista)]
    conversaciones = []
    for i, e in enumerate(generar(variaciones_por_guion=10, semilla=5)):
        n = sum(1 for c in conversaciones if c["guion_id"] == e["guion_id"])
        conversaciones.append({"id": f"{e['guion_id']}-v{n:02d}", "guion_id": e["guion_id"],
                               "fuente": "plantilla", "turnos": e["turnos"]})
    escribir_jsonl(DESTINO / "guiones.jsonl", guiones)
    escribir_jsonl(DESTINO / "conversaciones.jsonl", conversaciones)

    rng = random.Random(1)
    cat = {g["guion_id"]: g["categoria"] for g in guiones}
    a = [{"id": c["id"], "etiqueta": cat[c["guion_id"]]} for c in conversaciones]
    b = [{"id": c["id"], "etiqueta": rng.choice(CATEGORIAS) if rng.random() < 0.1 else cat[c["guion_id"]]}
         for c in conversaciones]
    escribir_csv(DESTINO / "etiquetas" / "simulado_a.csv", a, ["id", "etiqueta", "dudosa", "notas"])
    escribir_csv(DESTINO / "etiquetas" / "simulado_b.csv", b, ["id", "etiqueta", "dudosa", "notas"])
    print(f"Ejemplo en {DESTINO}: {len(guiones)} guiones, {len(conversaciones)} conversaciones, 2 anotadores simulados.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

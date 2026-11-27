"""Reparte los GUIONES (no las conversaciones sueltas) en entrenamiento, validación y prueba.

Todas las variaciones de un guion quedan en el mismo conjunto: si quedaran repartidas, el
modelo vería en prueba casi lo mismo que vio al entrenar y las cifras saldrían infladas.

- Las proporciones objetivo son 60 / 20 / 20 dentro de cada categoría.
- Es de solo agregar: los guiones ya asignados no se mueven; cada guion nuevo va al
  conjunto que más lejos esté de su proporción en esa categoría.
- `--congelar` fija el conjunto de prueba: guarda en `particion.lock` una huella SHA-256
  de sus guiones y del texto de sus conversaciones. Desde ahí ningún guion nuevo entra a
  prueba, y `evaluar.py --conjunto prueba` se niega a correr si la huella cambió.

Uso:
    python particionar.py                 # asigna los guiones nuevos
    python particionar.py --congelar      # además congela el conjunto de prueba
"""

import argparse
import hashlib
import json
import random
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

from rita_clasificador.datos import DATOS, leer_jsonl

CONJUNTOS = ["entrenamiento", "validacion", "prueba"]
PROPORCION = {"entrenamiento": 0.6, "validacion": 0.2, "prueba": 0.2}


def huella_prueba(directorio: Path, particion: dict[str, str]) -> str:
    """SHA-256 de los guiones de prueba y del texto de todas sus conversaciones."""
    de_prueba = sorted(g for g, c in particion.items() if c == "prueba")
    conversaciones = sorted(
        (c["id"], c["turnos"]) for c in leer_jsonl(directorio / "conversaciones.jsonl")
        if c["guion_id"] in set(de_prueba)
    )
    contenido = json.dumps({"guiones": de_prueba, "conversaciones": conversaciones}, ensure_ascii=False)
    return hashlib.sha256(contenido.encode()).hexdigest()


def verificar_congelado(directorio: Path, particion: dict[str, str]) -> str | None:
    """Devuelve un mensaje de error si la prueba congelada cambió; None si está bien o no está congelada."""
    ruta = directorio / "particion.lock"
    if not ruta.exists():
        return None
    lock = json.loads(ruta.read_text(encoding="utf-8"))
    if huella_prueba(directorio, particion) != lock["huella"]:
        return ("El conjunto de prueba cambió después de congelarlo (se movieron guiones o se editaron "
                "conversaciones de prueba). Reviertan el cambio en git antes de evaluar.")
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--datos", type=Path, default=DATOS)
    ap.add_argument("--congelar", action="store_true")
    ap.add_argument("--semilla", type=int, default=2026)
    args = ap.parse_args()

    guiones = leer_jsonl(args.datos / "guiones.jsonl")
    ruta = args.datos / "particion.json"
    particion = json.loads(ruta.read_text(encoding="utf-8"))["guiones"] if ruta.exists() else {}
    congelada = (args.datos / "particion.lock").exists()

    error = verificar_congelado(args.datos, particion)
    if error:
        print(error, file=sys.stderr)
        return 1

    nuevos = [g for g in guiones if g["guion_id"] not in particion]
    random.Random(args.semilla + len(particion)).shuffle(nuevos)
    categoria = {g["guion_id"]: g["categoria"] for g in guiones}

    for g in nuevos:
        cat = g["categoria"]
        cuenta = Counter(c for gid, c in particion.items() if categoria.get(gid) == cat)
        total = sum(cuenta.values()) + 1
        opciones = [c for c in CONJUNTOS if not (congelada and c == "prueba")]
        # El conjunto con mayor déficit respecto a su proporción objetivo.
        destino = max(opciones, key=lambda c: (PROPORCION[c] * total - cuenta[c], PROPORCION[c]))
        particion[g["guion_id"]] = destino

    ruta.write_text(json.dumps({"semilla": args.semilla, "guiones": dict(sorted(particion.items()))},
                               ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    if args.congelar and not congelada:
        lock = {"congelado": datetime.now().isoformat(timespec="seconds"),
                "guiones_prueba": sum(1 for c in particion.values() if c == "prueba"),
                "huella": huella_prueba(args.datos, particion)}
        (args.datos / "particion.lock").write_text(json.dumps(lock, indent=1) + "\n", encoding="utf-8")
        congelada = True

    tabla = Counter((categoria.get(g), c) for g, c in particion.items())
    print(f"{len(nuevos)} guiones nuevos asignados. Prueba {'CONGELADA' if congelada else 'sin congelar'}.\n")
    print(f"{'categoría':<18}" + "".join(f"{c:>15}" for c in CONJUNTOS))
    for cat in sorted({categoria.get(g) for g in particion}, key=str):
        print(f"{str(cat):<18}" + "".join(f"{tabla[(cat, c)]:>15}" for c in CONJUNTOS))
    return 0


if __name__ == "__main__":
    sys.exit(main())

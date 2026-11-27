"""Revisa que los archivos de datos tengan el formato acordado.

Uso:  python validar.py [--datos datos/]
"""

import argparse
import sys
from collections import Counter
from pathlib import Path

from rita_clasificador.datos import DATOS, leer_jsonl, validar


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--datos", type=Path, default=DATOS)
    args = ap.parse_args()

    errores = validar(args.datos)
    guiones = leer_jsonl(args.datos / "guiones.jsonl")
    conversaciones = leer_jsonl(args.datos / "conversaciones.jsonl")
    por_cat = Counter(g.get("categoria") for g in guiones)
    cat_de = {g.get("guion_id"): g.get("categoria") for g in guiones}
    conv_cat = Counter(cat_de.get(c.get("guion_id")) for c in conversaciones)

    print(f"{len(guiones)} guiones y {len(conversaciones)} conversaciones en {args.datos}")
    for cat, n in sorted(por_cat.items(), key=lambda kv: str(kv[0])):
        print(f"  {cat:<18} {n:>3} guiones  {conv_cat.get(cat, 0):>4} conversaciones")
    if errores:
        print(f"\n{len(errores)} problema(s):")
        for e in errores:
            print("  -", e)
        return 1
    print("\nFormato correcto.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

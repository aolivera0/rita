"""Prepara la hoja de etiquetado a ciegas de un integrante.

Escribe `datos/etiquetas/<anotador>.csv` con las columnas id, texto, etiqueta, dudosa y
notas. No muestra el guion ni su categoría. Si la hoja ya existe, conserva lo etiquetado y
solo agrega las conversaciones nuevas.

Reparto:
- Sin opciones: el integrante recibe TODAS las conversaciones (etiquetado doble completo).
- Con --parte k/n y --comunes N: recibe las N conversaciones comunes (las mismas para los
  tres, sirven para calcular el kappa) más su parte k de n del resto.

Ejemplos:
    python exportar_etiquetado.py --anotador aolivera0
    python exportar_etiquetado.py --anotador jpastranar --parte 2/3 --comunes 120

Abran el CSV en LibreOffice o Google Sheets, llenen `etiqueta` (estafa, comercial,
cobranza, encuesta, legitima, equivocada, no_identificable o descartar), `dudosa` (si o
vacío) y `notas`, y guárdenlo como CSV con el mismo nombre.
"""

import argparse
import hashlib
import random
import sys
from pathlib import Path

from rita_clasificador.datos import DATOS, escribir_csv, leer_csv, leer_jsonl, texto_llamante

COLUMNAS = ["id", "texto", "etiqueta", "dudosa", "notas"]


def huella(cid: str) -> int:
    return int(hashlib.sha1(cid.encode()).hexdigest(), 16)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--anotador", required=True, help="usuario de GitHub de quien etiqueta")
    ap.add_argument("--datos", type=Path, default=DATOS)
    ap.add_argument("--parte", help="k/n: esta persona recibe la parte k de n del resto")
    ap.add_argument("--comunes", type=int, default=0, help="conversaciones que etiquetan todos")
    args = ap.parse_args()

    conversaciones = leer_jsonl(args.datos / "conversaciones.jsonl")
    if not conversaciones:
        print("No hay conversaciones todavía.", file=sys.stderr)
        return 1

    # Orden estable por huella: las comunes son las mismas para todos.
    ordenadas = sorted(conversaciones, key=lambda c: huella(c["id"]))
    comunes = ordenadas[: args.comunes]
    resto = ordenadas[args.comunes:]
    if args.parte:
        k, n = (int(x) for x in args.parte.split("/"))
        if not 1 <= k <= n:
            print("--parte debe ser k/n con 1 <= k <= n", file=sys.stderr)
            return 2
        resto = [c for c in resto if huella(c["id"]) % n == k - 1]
    asignadas = comunes + resto

    ruta = args.datos / "etiquetas" / f"{args.anotador}.csv"
    existentes = leer_csv(ruta)
    ya = {f["id"] for f in existentes}
    nuevas = [{"id": c["id"], "texto": texto_llamante(c), "etiqueta": "", "dudosa": "", "notas": ""}
              for c in asignadas if c["id"] not in ya]
    # Orden al azar (pero fijo por persona) para que no vengan agrupadas por guion.
    random.Random(f"{args.anotador}").shuffle(nuevas)
    escribir_csv(ruta, existentes + nuevas, COLUMNAS)

    pendientes = sum(1 for f in existentes + nuevas if not f.get("etiqueta"))
    print(f"{ruta}: {len(nuevas)} nuevas, {pendientes} por etiquetar "
          f"({len(comunes)} comunes con el resto del equipo).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

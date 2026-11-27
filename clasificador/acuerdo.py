"""Mide el acuerdo entre anotadores y arma las etiquetas finales.

Lee `datos/etiquetas/*.csv` (una hoja por integrante) y:

1. Calcula el kappa de Cohen de cada par de anotadores sobre las conversaciones que
   etiquetaron los dos, y el porcentaje de acuerdo.
2. Arma `datos/etiquetas_finales.csv`:
   - si todos los que la etiquetaron coinciden, esa etiqueta;
   - si hay desacuerdo, la de `datos/resoluciones.csv` (id, etiqueta, razon), que el
     equipo llena después de discutir cada caso;
   - si hay desacuerdo sin resolver, queda fuera y aparece en `datos/desacuerdos.csv`.
3. Escribe el resumen en `resultados/acuerdo.md`.

Uso:  python acuerdo.py [--datos datos/]
"""

import argparse
import itertools
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from sklearn.metrics import cohen_kappa_score

from rita_clasificador.datos import CATEGORIAS, DATOS, DESCARTAR, RAIZ, escribir_csv, leer_csv, leer_jsonl, texto_llamante


def interpretar(k: float) -> str:
    # Escala de Landis y Koch (1977), la más citada.
    for limite, nombre in [(0.2, "leve"), (0.4, "aceptable"), (0.6, "moderado"), (0.8, "sustancial")]:
        if k <= limite:
            return nombre
    return "casi perfecto"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--datos", type=Path, default=DATOS)
    ap.add_argument("--resultados", type=Path, default=RAIZ / "resultados")
    args = ap.parse_args()

    hojas = {r.stem: leer_csv(r) for r in sorted((args.datos / "etiquetas").glob("*.csv"))}
    if not hojas:
        print("No hay hojas en datos/etiquetas/.", file=sys.stderr)
        return 1

    etiquetas: dict[str, dict[str, str]] = defaultdict(dict)  # id -> anotador -> etiqueta
    for anotador, filas in hojas.items():
        for f in filas:
            if f.get("etiqueta"):
                etiquetas[f["id"]][anotador] = f["etiqueta"]

    lineas = [f"# Acuerdo entre anotadores", "", f"Generado: {datetime.now():%Y-%m-%d %H:%M}", "",
              "| Anotador | Conversaciones etiquetadas |", "|---|---|"]
    for anotador in hojas:
        n = sum(1 for e in etiquetas.values() if anotador in e)
        lineas.append(f"| {anotador} | {n} |")

    lineas += ["", "| Par | En común | Acuerdo | Kappa de Cohen | Interpretación |", "|---|---|---|---|---|"]
    kappas = []
    for a, b in itertools.combinations(hojas, 2):
        comunes = [i for i, e in etiquetas.items() if a in e and b in e]
        if len(comunes) < 2:
            continue
        ya = [etiquetas[i][a] for i in comunes]
        yb = [etiquetas[i][b] for i in comunes]
        acuerdo = sum(x == y for x, y in zip(ya, yb)) / len(comunes)
        k = cohen_kappa_score(ya, yb)
        kappas.append(k)
        lineas.append(f"| {a} / {b} | {len(comunes)} | {acuerdo:.0%} | {k:.3f} | {interpretar(k)} |")
    if not kappas:
        lineas.append("| — | todavía no hay conversaciones etiquetadas por dos personas | | | |")

    # Desacuerdos más frecuentes: dicen qué regla de la guía hay que aclarar.
    pares = Counter()
    for e in etiquetas.values():
        valores = sorted(set(e.values()))
        if len(valores) > 1:
            pares[" vs ".join(valores)] += 1
    if pares:
        lineas += ["", "## Desacuerdos más frecuentes", "", "| Entre | Veces |", "|---|---|"]
        lineas += [f"| {p} | {n} |" for p, n in pares.most_common(10)]

    resoluciones = {r["id"]: r for r in leer_csv(args.datos / "resoluciones.csv")}
    conversaciones = {c["id"]: c for c in leer_jsonl(args.datos / "conversaciones.jsonl")}
    cat_guion = {g["guion_id"]: g["categoria"] for g in leer_jsonl(args.datos / "guiones.jsonl")}

    finales, desacuerdos = [], []
    for cid, e in sorted(etiquetas.items()):
        valores = set(e.values())
        if len(valores) == 1:
            finales.append({"id": cid, "etiqueta": valores.pop(), "origen": "acuerdo" if len(e) > 1 else "una_persona"})
        elif cid in resoluciones and resoluciones[cid].get("etiqueta"):
            finales.append({"id": cid, "etiqueta": resoluciones[cid]["etiqueta"], "origen": "resolucion"})
        else:
            c = conversaciones.get(cid)
            desacuerdos.append({"id": cid, "texto": texto_llamante(c) if c else "",
                                "etiquetas": "; ".join(f"{a}={v}" for a, v in sorted(e.items())),
                                "etiqueta": "", "razon": ""})

    escribir_csv(args.datos / "etiquetas_finales.csv", finales, ["id", "etiqueta", "origen"])
    escribir_csv(args.datos / "desacuerdos.csv", desacuerdos, ["id", "texto", "etiquetas", "etiqueta", "razon"])

    utiles = [f for f in finales if f["etiqueta"] in CATEGORIAS]
    por_cat = Counter(f["etiqueta"] for f in utiles)
    distinta = sum(1 for f in utiles
                   if cat_guion.get(conversaciones.get(f["id"], {}).get("guion_id")) not in (None, f["etiqueta"]))
    lineas += ["", "## Etiquetas finales", "",
               f"- {len(utiles)} conversaciones con etiqueta final, "
               f"{sum(1 for f in finales if f['etiqueta'] == DESCARTAR)} descartadas, "
               f"{len(desacuerdos)} desacuerdos sin resolver (ver `datos/desacuerdos.csv`).",
               f"- {distinta} conversaciones quedaron con una etiqueta distinta a la categoría con la que se "
               "escribió su guion (normal en las variaciones; revisen si son muchas).", "",
               "| Categoría | Conversaciones |", "|---|---|"]
    lineas += [f"| {c} | {por_cat.get(c, 0)} |" for c in CATEGORIAS]

    args.resultados.mkdir(parents=True, exist_ok=True)
    (args.resultados / "acuerdo.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print("\n".join(lineas))
    return 0


if __name__ == "__main__":
    sys.exit(main())

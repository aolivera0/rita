"""Entrena las líneas base y las evalúa con las métricas acordadas.

Por defecto evalúa en VALIDACIÓN: entrena con entrenamiento y mide en validación. Es lo
que se corre todos los días para comparar modelos y elegir umbrales.

El conjunto de PRUEBA se usa una sola vez, al final: entrena con entrenamiento +
validación y mide en prueba. Exige --confirmo-prueba, verifica que la prueba congelada no
haya cambiado y deja constancia en resultados/uso_prueba.log.

Para comparar otro modelo (por ejemplo Kev, que corre en Colab), pásenle sus predicciones
en un CSV con columnas id, etiqueta (o prediccion) y, si las tiene, prob_<categoria>:
    python evaluar.py --predicciones kev_validacion.csv --nombre kev-4b

Ejemplos:
    python evaluar.py
    python evaluar.py --transcripciones datos/transcripciones.jsonl
    python evaluar.py --conjunto prueba --confirmo-prueba
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
from sklearn.pipeline import Pipeline

from particionar import verificar_congelado
from rita_clasificador import metricas, modelos
from rita_clasificador.datos import CATEGORIAS, DATOS, RAIZ, ErrorDatos, cargar_dataset, escribir_csv, leer_csv


def commit_actual() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=RAIZ, capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception:  # noqa: BLE001
        return "sin-git"


def pct(v, ic=None) -> str:
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "—"
    s = f"{v:.0%}" if ic is None else f"{v:.0%} ({ic[0]:.0%}–{ic[1]:.0%})"
    return s


def predicciones_externas(ruta: Path, filas: list[dict]):
    datos = {f["id"]: f for f in leer_csv(ruta)}
    faltan = [f["id"] for f in filas if f["id"] not in datos]
    if faltan:
        raise ErrorDatos(f"{ruta.name} no trae predicción para {len(faltan)} conversaciones (p. ej. {faltan[0]})")
    columna = "etiqueta" if "etiqueta" in next(iter(datos.values())) else "prediccion"
    pred = np.array([datos[f["id"]][columna] for f in filas])
    columnas = [f"prob_{c}" for c in CATEGORIAS]
    probs = None
    if all(c in next(iter(datos.values())) for c in columnas):
        probs = np.array([[float(datos[f["id"]][c] or 0) for c in columnas] for f in filas])
    return pred, probs, CATEGORIAS


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--datos", type=Path, default=DATOS)
    ap.add_argument("--conjunto", choices=["validacion", "prueba"], default="validacion")
    ap.add_argument("--confirmo-prueba", action="store_true")
    ap.add_argument("--transcripciones", type=Path, help="usar el texto de Whisper en vez del guion")
    ap.add_argument("--predicciones", type=Path, help="CSV de predicciones de otro modelo")
    ap.add_argument("--nombre", default="externo", help="nombre del modelo de --predicciones")
    ap.add_argument("--bootstrap", type=int, default=1000)
    ap.add_argument("--resultados", type=Path, default=RAIZ / "resultados")
    args = ap.parse_args()

    try:
        filas = cargar_dataset(args.datos, args.transcripciones)
    except ErrorDatos as e:
        print(e, file=sys.stderr)
        return 1

    if args.conjunto == "prueba":
        if not args.confirmo_prueba:
            print("La prueba se usa una sola vez, al final. Si de verdad es el momento, agreguen "
                  "--confirmo-prueba.", file=sys.stderr)
            return 2
        if not (args.datos / "particion.lock").exists():
            print("Congelen primero la prueba: python particionar.py --congelar", file=sys.stderr)
            return 2
        particion = json.loads((args.datos / "particion.json").read_text(encoding="utf-8"))["guiones"]
        error = verificar_congelado(args.datos, particion)
        if error:
            print(error, file=sys.stderr)
            return 1
        entrenar_con = {"entrenamiento", "validacion"}
    else:
        entrenar_con = {"entrenamiento"}

    entrenamiento = [f for f in filas if f["conjunto"] in entrenar_con]
    evaluacion = [f for f in filas if f["conjunto"] == args.conjunto]
    if not entrenamiento or not evaluacion:
        print(f"Faltan datos: {len(entrenamiento)} para entrenar y {len(evaluacion)} para evaluar.", file=sys.stderr)
        return 1

    x_tr = [f["texto"] for f in entrenamiento]
    y_tr = [f["etiqueta"] for f in entrenamiento]
    g_tr = [f["guion_id"] for f in entrenamiento]
    x_ev = [f["texto"] for f in evaluacion]
    y_ev = [f["etiqueta"] for f in evaluacion]
    g_ev = [f["guion_id"] for f in evaluacion]
    etiquetas = [c for c in CATEGORIAS if c in set(y_tr) | set(y_ev)]

    salida = args.resultados / f"{datetime.now():%Y-%m-%d_%H%M%S}_{args.conjunto}"
    (salida / "predicciones").mkdir(parents=True, exist_ok=True)

    resultados, extras = {}, {}
    candidatos = [] if args.predicciones else modelos.todas()
    for m in candidatos:
        if isinstance(m, Pipeline):
            m.fit(x_tr, y_tr)
        else:
            m.fit(x_tr, y_tr, g_tr)
        pred = np.asarray(m.predict(x_ev))
        probs = m.predict_proba(x_ev) if hasattr(m, "predict_proba") else None
        clases = list(m.classes_) if probs is not None else None
        resultados[m.nombre] = metricas.calcular(y_ev, pred, g_ev, etiquetas, probs, clases, args.bootstrap)
        if hasattr(m, "c_elegido"):
            extras[m.nombre] = {"C": m.c_elegido}
        guardar_predicciones(salida, m.nombre, evaluacion, pred, probs, clases)

    if args.predicciones:
        try:
            pred, probs, clases = predicciones_externas(args.predicciones, evaluacion)
        except ErrorDatos as e:
            print(e, file=sys.stderr)
            return 1
        resultados[args.nombre] = metricas.calcular(y_ev, pred, g_ev, etiquetas, probs, clases, args.bootstrap)
        guardar_predicciones(salida, args.nombre, evaluacion, pred, probs, clases)

    fuente = f"transcripciones ({args.transcripciones.name})" if args.transcripciones else "texto del guion"
    reporte = armar_reporte(resultados, extras, args.conjunto, len(entrenamiento), evaluacion, fuente, etiquetas)
    (salida / "reporte.md").write_text(reporte, encoding="utf-8")
    (salida / "metricas.json").write_text(json.dumps(
        {"conjunto": args.conjunto, "fuente": fuente, "commit": commit_actual(), "entrenamiento": len(entrenamiento),
         "evaluacion": len(evaluacion), "modelos": resultados, "extras": extras},
        ensure_ascii=False, indent=1), encoding="utf-8")

    if args.conjunto == "prueba":
        with (args.resultados / "uso_prueba.log").open("a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat(timespec='seconds')}\tcommit {commit_actual()}\t"
                    f"{', '.join(resultados)}\t{salida.name}\n")

    print(reporte)
    print(f"Guardado en {salida}")
    return 0


def guardar_predicciones(salida: Path, nombre: str, filas, pred, probs, clases) -> None:
    columnas = ["id", "guion_id", "real", "prediccion", "acierto"]
    registros = []
    for i, f in enumerate(filas):
        r = {"id": f["id"], "guion_id": f["guion_id"], "real": f["etiqueta"], "prediccion": pred[i],
             "acierto": int(pred[i] == f["etiqueta"])}
        if probs is not None:
            for j, c in enumerate(clases):
                r[f"prob_{c}"] = f"{probs[i][j]:.6f}"
        registros.append(r)
    if probs is not None:
        columnas += [f"prob_{c}" for c in clases]
    escribir_csv(salida / "predicciones" / f"{nombre}.csv", registros, columnas)


def armar_reporte(resultados, extras, conjunto, n_tr, evaluacion, fuente, etiquetas) -> str:
    n_guiones = len({f["guion_id"] for f in evaluacion})
    l = [f"# Evaluación en {conjunto}", "",
         f"- Entrenamiento: {n_tr} conversaciones. Evaluación: {len(evaluacion)} conversaciones de {n_guiones} guiones.",
         f"- Texto: {fuente}. Commit: {commit_actual()}.",
         "- Intervalos de 95 %: Wilson para proporciones y bootstrap por guion para el F1.", "",
         "| Modelo | F1 macro (IC 95 %) | Exactitud | Legítimas mal marcadas (IC 95 %) | Estafas detectadas (IC 95 %) | ECE |",
         "|---|---|---|---|---|---|"]
    for nombre, r in resultados.items():
        ic = r["f1_macro_ic95"]
        ece = "—" if r["ece"] is None else f"{r['ece']:.3f}"
        l.append(f"| {nombre} | {r['f1_macro']:.3f} ({ic[0]:.3f}–{ic[1]:.3f}) | {r['exactitud']:.0%} | "
                 f"{pct(r['legitimas_mal_marcadas'], r['legitimas_mal_marcadas_ic95'])} de {r['legitimas']} | "
                 f"{pct(r['estafas_detectadas'], r['estafas_detectadas_ic95'])} de {r['estafas']} | {ece} |")
    for nombre, e in extras.items():
        l.append(f"\n{nombre}: C elegido por validación cruzada agrupada = {e['C']}")
    l += ["", "## F1 por clase", "", "| Modelo | " + " | ".join(etiquetas) + " |",
          "|---|" + "---|" * len(etiquetas)]
    for nombre, r in resultados.items():
        l.append(f"| {nombre} | " + " | ".join(f"{r['por_clase'][e]['f1']:.2f}" for e in etiquetas) + " |")
    return "\n".join(l) + "\n"


if __name__ == "__main__":
    sys.exit(main())

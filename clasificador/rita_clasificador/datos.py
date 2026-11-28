"""Formato de los datos, carga y validación.

Archivos de un directorio de datos (por defecto `clasificador/datos/`):

- `guiones.jsonl`: un guion por línea.
    {"guion_id": "estafa-banco-01", "categoria": "estafa", "autor": "aolivera0",
     "referencia": "llamada que recibió mi mamá, oct. 2026", "turnos": ["...", "..."],
     "modalidad": "E1", "dificil": false}
  `modalidad` (código de modalidades_colombia.md) y `dificil` son opcionales.
- `conversaciones.jsonl`: una conversación por línea. Las variaciones de un guion llevan
  su `guion_id`; un guion escrito a mano también puede ser su propia conversación.
    {"id": "estafa-banco-01-v03", "guion_id": "estafa-banco-01", "fuente": "llm:modelo",
     "turnos": ["...", "..."]}
- `etiquetas/<anotador>.csv`: lo que etiquetó cada integrante (id, etiqueta, dudosa, notas).
- `etiquetas_finales.csv`: la etiqueta acordada de cada conversación (id, etiqueta).
- `particion.json` y `particion.lock`: a qué conjunto va cada guion, y la huella del de prueba.
- `transcripciones.jsonl` (opcional): {"id": ..., "texto": ...} con lo que entendió Whisper.

Los turnos son SOLO lo que dice quien llama.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

CATEGORIAS = [
    "estafa", "comercial", "cobranza", "encuesta", "legitima", "equivocada", "no_identificable",
]
DESCARTAR = "descartar"

RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "datos"


class ErrorDatos(ValueError):
    pass


def leer_jsonl(ruta: Path) -> list[dict]:
    if not ruta.exists():
        return []
    filas = []
    with ruta.open(encoding="utf-8") as f:
        for n, linea in enumerate(f, 1):
            linea = linea.strip()
            if not linea:
                continue
            try:
                filas.append(json.loads(linea))
            except json.JSONDecodeError as e:
                raise ErrorDatos(f"{ruta.name}:{n}: JSON inválido ({e.msg})") from e
    return filas


def escribir_jsonl(ruta: Path, filas: list[dict]) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", encoding="utf-8") as f:
        for fila in filas:
            f.write(json.dumps(fila, ensure_ascii=False) + "\n")


def leer_csv(ruta: Path) -> list[dict]:
    if not ruta.exists():
        return []
    with ruta.open(encoding="utf-8", newline="") as f:
        return [{k.strip(): (v or "").strip() for k, v in fila.items() if k} for fila in csv.DictReader(f)]


def escribir_csv(ruta: Path, filas: list[dict], columnas: list[str]) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columnas, extrasaction="ignore")
        w.writeheader()
        w.writerows(filas)


def _turnos_validos(turnos, donde: str) -> list[str]:
    errores = []
    if not isinstance(turnos, list) or not turnos:
        errores.append(f"{donde}: 'turnos' debe ser una lista no vacía de frases")
    elif not all(isinstance(t, str) and t.strip() for t in turnos):
        errores.append(f"{donde}: hay turnos vacíos o que no son texto")
    return errores


def validar(directorio: Path = DATOS) -> list[str]:
    """Devuelve la lista de problemas encontrados (vacía si todo está bien)."""
    errores: list[str] = []
    guiones = leer_jsonl(directorio / "guiones.jsonl")
    conversaciones = leer_jsonl(directorio / "conversaciones.jsonl")

    ids_guion = set()
    for i, g in enumerate(guiones, 1):
        donde = f"guiones.jsonl:{i}"
        gid = g.get("guion_id")
        if not gid:
            errores.append(f"{donde}: falta 'guion_id'")
            continue
        if gid in ids_guion:
            errores.append(f"{donde}: 'guion_id' repetido: {gid}")
        ids_guion.add(gid)
        if g.get("categoria") not in CATEGORIAS:
            errores.append(f"{donde}: categoría desconocida {g.get('categoria')!r}")
        errores += _turnos_validos(g.get("turnos"), donde)

    ids = set()
    for i, c in enumerate(conversaciones, 1):
        donde = f"conversaciones.jsonl:{i}"
        cid = c.get("id")
        if not cid:
            errores.append(f"{donde}: falta 'id'")
            continue
        if cid in ids:
            errores.append(f"{donde}: 'id' repetido: {cid}")
        ids.add(cid)
        if c.get("guion_id") not in ids_guion:
            errores.append(f"{donde}: el guion {c.get('guion_id')!r} no está en guiones.jsonl")
        errores += _turnos_validos(c.get("turnos"), donde)

    for ruta in sorted((directorio / "etiquetas").glob("*.csv")):
        for i, fila in enumerate(leer_csv(ruta), 2):
            if fila.get("id") not in ids:
                errores.append(f"etiquetas/{ruta.name}:{i}: id desconocido {fila.get('id')!r}")
            et = fila.get("etiqueta", "")
            if et and et not in CATEGORIAS and et != DESCARTAR:
                errores.append(f"etiquetas/{ruta.name}:{i}: etiqueta desconocida {et!r}")
    return errores


def texto_llamante(conversacion: dict) -> str:
    return " ".join(t.strip() for t in conversacion["turnos"])


def cargar_dataset(directorio: Path = DATOS, transcripciones: Path | None = None) -> list[dict]:
    """Une conversaciones, etiqueta final y partición en una sola lista lista para evaluar.

    Cada elemento: {id, guion_id, texto, etiqueta, conjunto}. Se dejan fuera las
    conversaciones sin etiqueta final, las descartadas y las de guiones sin partición.
    """
    conversaciones = leer_jsonl(directorio / "conversaciones.jsonl")
    finales = {f["id"]: f["etiqueta"] for f in leer_csv(directorio / "etiquetas_finales.csv")}
    ruta_particion = directorio / "particion.json"
    if not ruta_particion.exists():
        raise ErrorDatos("No hay particion.json: corran primero particionar.py")
    particion = json.loads(ruta_particion.read_text(encoding="utf-8"))["guiones"]

    textos_asr = {}
    if transcripciones is not None:
        textos_asr = {t["id"]: t["texto"] for t in leer_jsonl(transcripciones)}

    filas = []
    for c in conversaciones:
        etiqueta = finales.get(c["id"])
        if etiqueta not in CATEGORIAS or c["guion_id"] not in particion:
            continue
        if transcripciones is not None and c["id"] not in textos_asr:
            continue
        filas.append({
            "id": c["id"],
            "guion_id": c["guion_id"],
            "texto": textos_asr[c["id"]] if transcripciones is not None else texto_llamante(c),
            "etiqueta": etiqueta,
            "conjunto": particion[c["guion_id"]],
        })
    return filas

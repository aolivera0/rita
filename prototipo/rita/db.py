"""Base de datos SQLite: una fila por llamada, con los dos formatos acordados en JSON."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

RUTA = Path(__file__).resolve().parent.parent / "rita.db"

ESQUEMA = """
CREATE TABLE IF NOT EXISTS llamadas (
    id TEXT PRIMARY KEY,
    numero TEXT NOT NULL,
    inicio TEXT NOT NULL,
    llamada TEXT NOT NULL,        -- formato Llamada (JSON)
    clasificacion TEXT NOT NULL,  -- formato Clasificación (JSON)
    etiqueta_usuario TEXT         -- corrección del usuario, si la hay
);
"""


def conectar() -> sqlite3.Connection:
    con = sqlite3.connect(RUTA)
    con.row_factory = sqlite3.Row
    con.executescript(ESQUEMA)
    return con


def guardar(llamada: dict, clasificacion: dict) -> None:
    with conectar() as con:
        con.execute(
            "INSERT OR REPLACE INTO llamadas (id, numero, inicio, llamada, clasificacion) "
            "VALUES (?, ?, ?, ?, ?)",
            (llamada["id"], llamada["numero"], llamada["inicio"],
             json.dumps(llamada, ensure_ascii=False),
             json.dumps(clasificacion, ensure_ascii=False)),
        )


def _fila(f: sqlite3.Row) -> dict:
    return {
        "llamada": json.loads(f["llamada"]),
        "clasificacion": json.loads(f["clasificacion"]),
        "etiqueta_usuario": f["etiqueta_usuario"],
    }


def listar() -> list[dict]:
    with conectar() as con:
        filas = con.execute("SELECT * FROM llamadas ORDER BY inicio DESC").fetchall()
    return [_fila(f) for f in filas]


def obtener(llamada_id: str) -> dict | None:
    with conectar() as con:
        f = con.execute("SELECT * FROM llamadas WHERE id = ?", (llamada_id,)).fetchone()
    return _fila(f) if f else None


def corregir(llamada_id: str, etiqueta: str | None) -> bool:
    with conectar() as con:
        cur = con.execute("UPDATE llamadas SET etiqueta_usuario = ? WHERE id = ?",
                          (etiqueta, llamada_id))
    return cur.rowcount > 0


def borrar(llamada_id: str) -> bool:
    with conectar() as con:
        cur = con.execute("DELETE FROM llamadas WHERE id = ?", (llamada_id,))
    return cur.rowcount > 0

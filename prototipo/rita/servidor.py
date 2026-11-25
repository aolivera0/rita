"""Servidor del prototipo de Rita (FastAPI).

Correr con:  .venv/bin/uvicorn rita.servidor:app --port 8000
"""

from __future__ import annotations

import base64
import csv
import io
import os
import time
import uuid
from collections import Counter
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from . import db, voz
from .agente import AgenteFormulario, nuevo_agente
from .clasificador import NOMBRES_PISTA, Clasificador
from .datos_sinteticos import CATEGORIAS, NOMBRES_CATEGORIA

ESTATICO = Path(__file__).resolve().parent.parent / "web"
USUARIO = os.environ.get("RITA_USUARIO", "Angel")

app = FastAPI(title="Rita · prototipo")
clasificador = Clasificador()
sesiones: dict[str, dict] = {}

RIESGO = {"estafa": 3, "cobranza": 2, "comercial": 2, "encuesta": 1,
          "no_identificable": 1, "equivocada": 0, "legitima": 0}


@app.on_event("startup")
def _precargar() -> None:
    voz.precargar()


def _ahora() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _audio_b64(texto: str) -> tuple[str, int]:
    t = time.perf_counter()
    wav = voz.sintetizar(texto)
    return base64.b64encode(wav).decode(), int((time.perf_counter() - t) * 1000)


# ---------- Llamada en curso ----------

class NuevaLlamada(BaseModel):
    numero: str


@app.post("/api/llamadas")
def iniciar(datos: NuevaLlamada) -> dict:
    agente = nuevo_agente(USUARIO)
    llamada_id = uuid.uuid4().hex[:12]
    saludo = agente.saludo()
    sesiones[llamada_id] = {
        "agente": agente,
        "llamada": {
            "id": llamada_id,
            "numero": datos.numero.strip() or "desconocido",
            "inicio": _ahora(),
            "fin": None,
            "turnos": [{"hablante": "rita", "texto": saludo, "t": 0.0}],
            "datos": agente.datos,
            "latencias_ms": [],
            "agente": agente.tipo,
        },
        "t0": time.time(),
    }
    audio, tts_ms = _audio_b64(saludo)
    return {"id": llamada_id, "respuesta": saludo, "audio": audio, "agente": agente.tipo,
            "tiempos_ms": {"tts": tts_ms}}


@app.post("/api/llamadas/{llamada_id}/turno")
async def turno(llamada_id: str, audio: UploadFile | None = File(None),
                texto: str | None = Form(None)) -> dict:
    s = sesiones.get(llamada_id)
    if not s:
        raise HTTPException(404, "La llamada no existe o ya terminó")
    agente: AgenteFormulario = s["agente"]
    llamada = s["llamada"]

    t = time.perf_counter()
    if audio is not None:
        texto = voz.transcribir(await audio.read())
    texto = (texto or "").strip()
    asr_ms = int((time.perf_counter() - t) * 1000)

    t = time.perf_counter()
    respuesta = agente.responder(texto)
    agente_ms = int((time.perf_counter() - t) * 1000)

    audio_b64, tts_ms = _audio_b64(respuesta)
    total = asr_ms + agente_ms + tts_ms

    momento = round(time.time() - s["t0"], 1)
    llamada["turnos"].append({"hablante": "llamante", "texto": texto, "t": momento})
    llamada["turnos"].append({"hablante": "rita", "texto": respuesta, "t": momento})
    llamada["latencias_ms"].append(total)
    llamada["datos"] = agente.datos

    return {
        "transcripcion": texto,
        "respuesta": respuesta,
        "audio": audio_b64,
        "datos": agente.datos,
        "terminar": agente.terminada,
        "tiempos_ms": {"voz_a_texto": asr_ms, "agente": agente_ms, "texto_a_voz": tts_ms,
                       "total": total},
    }


@app.post("/api/llamadas/{llamada_id}/colgar")
def colgar(llamada_id: str) -> dict:
    s = sesiones.pop(llamada_id, None)
    if not s:
        raise HTTPException(404, "La llamada no existe o ya terminó")
    llamada = s["llamada"]
    llamada["fin"] = _ahora()
    texto = " ".join(t["texto"] for t in llamada["turnos"] if t["hablante"] == "llamante")
    clasif = clasificador.clasificar(texto, llamada_id)
    db.guardar(llamada, clasif)
    return {"llamada": llamada, "clasificacion": clasif}


# ---------- Panel ----------

def _etiqueta(fila: dict) -> str:
    return fila["etiqueta_usuario"] or fila["clasificacion"]["etiqueta"]


@app.get("/api/llamadas")
def listar() -> list[dict]:
    return db.listar()


@app.get("/api/llamadas/{llamada_id}")
def obtener(llamada_id: str) -> dict:
    fila = db.obtener(llamada_id)
    if not fila:
        raise HTTPException(404, "No existe")
    return fila


class Correccion(BaseModel):
    etiqueta: str | None


@app.post("/api/llamadas/{llamada_id}/etiqueta")
def corregir(llamada_id: str, c: Correccion) -> dict:
    if c.etiqueta is not None and c.etiqueta not in CATEGORIAS:
        raise HTTPException(400, "Etiqueta desconocida")
    if not db.corregir(llamada_id, c.etiqueta):
        raise HTTPException(404, "No existe")
    return {"ok": True}


@app.delete("/api/llamadas/{llamada_id}")
def borrar(llamada_id: str) -> dict:
    if not db.borrar(llamada_id):
        raise HTTPException(404, "No existe")
    return {"ok": True}


def _numeros() -> list[dict]:
    por_numero: dict[str, list[dict]] = {}
    for f in db.listar():
        por_numero.setdefault(f["llamada"]["numero"], []).append(f)
    salida = []
    for numero, filas in por_numero.items():
        etiquetas = Counter(_etiqueta(f) for f in filas)
        riesgo = max(RIESGO[e] for e in etiquetas)
        salida.append({
            "numero": numero,
            "llamadas": len(filas),
            "etiquetas": dict(etiquetas),
            "etiqueta_frecuente": etiquetas.most_common(1)[0][0],
            "ultima": max(f["llamada"]["inicio"] for f in filas),
            "riesgo": ["bajo", "bajo", "medio", "alto"][riesgo],
            "orden": riesgo,
        })
    return sorted(salida, key=lambda n: (-n["orden"], -n["llamadas"]))


@app.get("/api/numeros")
def numeros() -> list[dict]:
    return _numeros()


@app.get("/api/numeros.csv")
def exportar() -> StreamingResponse:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["numero", "llamadas", "etiqueta_frecuente", "riesgo", "ultima_llamada"])
    for n in _numeros():
        w.writerow([n["numero"], n["llamadas"], n["etiqueta_frecuente"], n["riesgo"],
                    n["ultima"]])
    buf.seek(0)
    return StreamingResponse(iter([buf.getvalue()]), media_type="text/csv",
                             headers={"Content-Disposition":
                                      "attachment; filename=numeros-rita.csv"})


@app.get("/api/modelo")
def modelo() -> dict:
    return {
        "modelo": clasificador.nombre_modelo,
        "metricas": clasificador.metricas,
        "categorias": NOMBRES_CATEGORIA,
        "pistas": NOMBRES_PISTA,
        "usuario": USUARIO,
    }


class TextoLibre(BaseModel):
    texto: str


@app.post("/api/clasificar")
def clasificar(t: TextoLibre) -> dict:
    return clasificador.clasificar(t.texto)


# ---------- Páginas ----------

@app.get("/")
def pagina_llamada() -> FileResponse:
    return FileResponse(ESTATICO / "llamada.html")


@app.get("/panel")
def pagina_panel() -> FileResponse:
    return FileResponse(ESTATICO / "panel.html")


@app.get("/estilos.css")
def estilos() -> FileResponse:
    return FileResponse(ESTATICO / "estilos.css")


@app.get("/veredicto.js")
def veredicto_js() -> FileResponse:
    return FileResponse(ESTATICO / "veredicto.js", media_type="text/javascript")

"""Crea variaciones de cada guion con un modelo de lenguaje.

Cada guion entra también como su propia conversación (`<guion_id>-v00`). Las variaciones
se agregan a `conversaciones.jsonl` como `<guion_id>-v01`, `-v02`, ... y quedan marcadas
con la fuente. Después TODAS se revisan al etiquetar (etiqueta `descartar` si salió mal).

Dos formas de usarlo:

1. Con una API compatible con OpenAI (por ejemplo el nivel gratuito de Groq o Gemini):
       export LLM_API_KEY=...            # obligatoria
       export LLM_BASE_URL=https://api.groq.com/openai/v1   # opcional
       export LLM_MODEL=llama-3.3-70b-versatile             # revisen el nombre vigente
       python generar_variaciones.py --por-guion 5

2. Sin API, pegando a mano en cualquier chat:
       python generar_variaciones.py --solo-prompts prompts/
   Escribe un archivo .txt por guion. Peguen cada uno en el chat, guarden la respuesta
   (el JSON) como prompts/<guion_id>.json y luego:
       python generar_variaciones.py --importar prompts/ --fuente llm:gemini-web

Solo procesa guiones que todavía no tienen variaciones, salvo que se pase --rehacer.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

from rita_clasificador.datos import DATOS, escribir_jsonl, leer_jsonl

PROMPT = """Eres un guionista que ayuda a crear datos de entrenamiento para un clasificador de \
llamadas telefónicas en Colombia. Te doy una llamada real o realista, de la categoría «{categoria}». \
Escribe {n} variaciones de lo que diría QUIEN LLAMA (no escribas lo que responde la otra persona).

Reglas:
- Mantén la intención y la categoría: una estafa sigue siendo estafa, una legítima sigue siendo legítima.
- Cambia nombres, entidades, montos, orden y forma de decir las cosas. Español de Colombia, con \
muletillas y frases cortadas como se habla por teléfono.
- Varía el largo: al menos una de 2 turnos y una de 6 o más.
- Al menos una variación debe ser menos obvia (más educada, sin palabras típicas de su categoría).
- Nunca inventes números de teléfono, cuentas, cédulas ni nombres completos de personas reales.

Llamada original (un turno por línea):
{turnos}

Responde SOLO con JSON, sin texto antes ni después, con esta forma:
{{"variaciones": [["turno 1", "turno 2"], ["turno 1", "turno 2", "turno 3"]]}}"""


def prompt_de(guion: dict, n: int) -> str:
    turnos = "\n".join(f"- {t}" for t in guion["turnos"])
    return PROMPT.format(categoria=guion["categoria"], n=n, turnos=turnos)


def extraer_variaciones(texto: str) -> list[list[str]]:
    m = re.search(r"\{.*\}", texto, re.S)
    if not m:
        raise ValueError("la respuesta no trae JSON")
    datos = json.loads(m.group(0))
    variaciones = datos.get("variaciones")
    if not isinstance(variaciones, list):
        raise ValueError("falta la lista 'variaciones'")
    limpias = []
    for v in variaciones:
        if isinstance(v, list):
            turnos = [str(t).strip() for t in v if str(t).strip()]
            if turnos:
                limpias.append(turnos)
    if not limpias:
        raise ValueError("no vino ninguna variación válida")
    return limpias


def pedir_api(prompt: str) -> tuple[str, str]:
    import httpx  # solo hace falta en este modo

    url = os.environ.get("LLM_BASE_URL", "https://api.groq.com/openai/v1").rstrip("/")
    modelo = os.environ.get("LLM_MODEL", "llama-3.3-70b-versatile")
    r = httpx.post(
        f"{url}/chat/completions",
        headers={"Authorization": f"Bearer {os.environ['LLM_API_KEY']}"},
        json={"model": modelo, "temperature": 0.9,
              "messages": [{"role": "user", "content": prompt}],
              "response_format": {"type": "json_object"}},
        timeout=90,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"], modelo


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--datos", type=Path, default=DATOS)
    ap.add_argument("--por-guion", type=int, default=5)
    ap.add_argument("--solo-prompts", type=Path, help="escribe los prompts en este directorio y termina")
    ap.add_argument("--importar", type=Path, help="lee las respuestas <guion_id>.json de este directorio")
    ap.add_argument("--fuente", default=None, help="etiqueta de la fuente al importar (p. ej. llm:gemini-web)")
    ap.add_argument("--rehacer", action="store_true", help="procesa también guiones que ya tienen variaciones")
    args = ap.parse_args()

    guiones = leer_jsonl(args.datos / "guiones.jsonl")
    ruta_conv = args.datos / "conversaciones.jsonl"
    conversaciones = leer_jsonl(ruta_conv)
    ids = {c["id"] for c in conversaciones}

    # Cada guion entra como su propia conversación.
    for g in guiones:
        cid = f"{g['guion_id']}-v00"
        if cid not in ids:
            conversaciones.append({"id": cid, "guion_id": g["guion_id"], "fuente": "guion",
                                   "turnos": g["turnos"]})
            ids.add(cid)

    con_variaciones = {c["guion_id"] for c in conversaciones if c["fuente"] != "guion"}
    pendientes = [g for g in guiones if args.rehacer or g["guion_id"] not in con_variaciones]

    if args.solo_prompts:
        args.solo_prompts.mkdir(parents=True, exist_ok=True)
        for g in pendientes:
            (args.solo_prompts / f"{g['guion_id']}.txt").write_text(prompt_de(g, args.por_guion), encoding="utf-8")
        escribir_jsonl(ruta_conv, conversaciones)
        print(f"{len(pendientes)} prompts en {args.solo_prompts}/. Guarden cada respuesta como <guion_id>.json")
        return 0

    if not args.importar and not os.environ.get("LLM_API_KEY"):
        print("Falta LLM_API_KEY. Usen --solo-prompts para el modo sin API.", file=sys.stderr)
        return 2

    agregadas, fallidas = 0, []
    for g in pendientes:
        try:
            if args.importar:
                ruta = args.importar / f"{g['guion_id']}.json"
                if not ruta.exists():
                    continue
                respuesta, fuente = ruta.read_text(encoding="utf-8"), args.fuente or "llm:manual"
            else:
                respuesta, modelo = pedir_api(prompt_de(g, args.por_guion))
                fuente = f"llm:{modelo}"
            variaciones = extraer_variaciones(respuesta)
        except Exception as e:  # noqa: BLE001 - seguimos con los demás guiones
            fallidas.append(f"{g['guion_id']}: {e}")
            continue
        n = max([int(c["id"].rsplit("-v", 1)[1]) for c in conversaciones
                 if c["guion_id"] == g["guion_id"] and "-v" in c["id"]] + [0])
        for turnos in variaciones:
            n += 1
            conversaciones.append({"id": f"{g['guion_id']}-v{n:02d}", "guion_id": g["guion_id"],
                                   "fuente": fuente, "turnos": turnos})
            agregadas += 1
        escribir_jsonl(ruta_conv, conversaciones)  # se guarda tras cada guion por si algo falla

    escribir_jsonl(ruta_conv, conversaciones)
    print(f"{agregadas} variaciones nuevas. Total: {len(conversaciones)} conversaciones.")
    for f in fallidas:
        print("  falló", f)
    return 1 if fallidas else 0


if __name__ == "__main__":
    sys.exit(main())

# Rita · prototipo

Primer prototipo funcionando de punta a punta, todo **local, gratuito y en CPU** (no
necesita GPU ni cuentas):

1. **Llamada desde el navegador.** Hablas por el micrófono como si fueras quien llama
   (o escribes, si no hay micrófono). Un detector de voz en el navegador corta cada frase
   cuando te quedas callado.
2. **Voz a texto** con [faster-whisper](https://github.com/SYSTRAN/faster-whisper).
3. **Agente** que pregunta nombre, entidad y motivo. Por defecto es el *formulario*
   (la línea base de la propuesta, con reglas). Si se configura una API de modelo de
   lenguaje, usa el *agente LLM*.
4. **Texto a voz** con [Piper](https://github.com/rhasspy/piper): Rita contesta en voz alta.
5. **Al colgar**, el clasificador (TF-IDF + regresión logística) da la etiqueta, la
   confianza, las probabilidades y las pistas de sí o no.
6. **Panel** para celular: llamadas, detalle con transcripción, corrección de etiqueta,
   borrado de registros, lista de números con su riesgo, exportación a CSV, métricas
   del modelo y una caja para clasificar cualquier texto.

Los datos que pasan entre piezas usan los dos formatos acordados en el README del
proyecto (*Llamada* y *Clasificación*).

## Cómo correrlo

Requisitos: Python 3.10–3.12, `ffmpeg` y unos 1,5 GB libres. Con [uv](https://docs.astral.sh/uv/):

```bash
cd prototipo
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.txt
```

Sin uv, `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt` también
sirve. Luego se descargan los modelos (una sola vez) y, si quieren, se siembran llamadas
de ejemplo:

```bash
.venv/bin/python descargar_modelos.py
```

```bash
.venv/bin/python sembrar_demo.py
```

Y se arranca el servidor:

```bash
.venv/bin/uvicorn rita.servidor:app --port 8000
```

Abran <http://localhost:8000> en Chrome o Firefox y den permiso al micrófono. El panel
está en <http://localhost:8000/panel>.

Para la demostración: usen audífonos, para que el micrófono no capte la voz de Rita, y
hablen frases completas con una pausa al final. Si el salón tiene mucho ruido, el campo
de texto de abajo hace lo mismo sin micrófono.

## Configuración (variables de entorno)

| Variable | Por defecto | Para qué |
|---|---|---|
| `RITA_USUARIO` | `Angel` | Nombre del usuario al que Rita representa |
| `WHISPER_MODEL` | `base` | `small` entiende mejor, pero tarda ~2 s más por frase en CPU |
| `PIPER_VOICE` | `es_MX-claude-high` | Otra voz de Piper (hay que descargarla con `descargar_modelos.py`) |
| `LLM_API_KEY` | (vacía) | Si se define, usa el agente LLM en vez del formulario |
| `LLM_BASE_URL` | `https://api.groq.com/openai/v1` | Cualquier API compatible con OpenAI |
| `LLM_MODEL` | `llama-3.1-8b-instant` | Revisen el nombre vigente en su proveedor |

El agente LLM no se ha probado con una clave real. Si la API falla, responde el
formulario, así que la llamada no se cae.

## Cifras medidas en un portátil de 4 núcleos sin GPU

| Paso | Tiempo |
|---|---|
| Voz a texto (Whisper base, frase de ~5 s) | 0,9–1,0 s |
| Agente formulario | < 1 ms |
| Texto a voz (Piper) | 0,05–0,6 s |
| **Total desde que quien llama termina de hablar** | **≈ 1,0–1,6 s** más ~0,9 s que espera el detector de voz para confirmar el silencio |

## Qué es de juguete y qué falta

- **El clasificador se entrena con 350 conversaciones generadas de 35 guiones**
  ([`rita/datos_sinteticos.py`](rita/datos_sinteticos.py)), con empresas inventadas.
  Su validación cruzada agrupada por guion da F1 macro ≈ 0,59: muestra el método de
  evaluación de la propuesta, no el resultado.
- **Kev no está.** Necesita GPU; se prueba aparte en Colab o Kaggle y se conecta con una
  función que devuelva el mismo formato *Clasificación*.
- **Las pistas son reglas** (expresiones regulares), no preguntas a Kev.
- **No hay telefonía real** todavía (Twilio) ni voz clonada.
- **El detector de voz es simple** (energía con umbral adaptativo): con ruido de fondo
  fuerte puede cortar mal.

## Estructura

```
prototipo/
├── rita/
│   ├── servidor.py          # API FastAPI y páginas
│   ├── agente.py            # agente formulario y agente LLM
│   ├── voz.py               # Whisper y Piper
│   ├── clasificador.py      # TF-IDF + regresión logística, pistas, validación por guion
│   ├── datos_sinteticos.py  # guiones de juguete
│   └── db.py                # SQLite
├── web/                     # llamada.html, panel.html, estilos.css
├── descargar_modelos.py
├── sembrar_demo.py
└── requirements.txt
```

Cada frente puede seguir desde aquí: el Frente 1 reemplaza `clasificador.py` y los datos,
el Frente 2 `agente.py` y `voz.py` (y el detector de voz de `llamada.html`), y el Frente 3
`servidor.py`, `db.py` y `panel.html`.

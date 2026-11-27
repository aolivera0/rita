# Frente 1 · Datos y clasificador

Todo lo necesario para construir el conjunto de datos de Rita, etiquetarlo entre los tres,
partirlo sin fugas y medir los modelos contra sus líneas base. Responde a dos criterios de
la rúbrica del jurado: **Evidencia** (línea base, métrica justificada, resultados
reproducibles) y **Uso del curso** (qué se escogió y qué se descartó).

## Instalación

```bash
cd clasificador
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.txt
```

Sin uv: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`. Todos los
comandos de abajo se corren desde `clasificador/` con `.venv/bin/python`.

## El flujo, paso a paso

```
guiones.jsonl ──generar_variaciones──► conversaciones.jsonl ──exportar_etiquetado──► etiquetas/<cada uno>.csv
                                                                                              │
resultados/ ◄──evaluar── particion.json (+ .lock) ◄──particionar── etiquetas_finales.csv ◄──acuerdo
```

1. **Escribir guiones** en `datos/guiones.jsonl`, uno por línea, siguiendo la
   [guía de etiquetado](guia_etiquetado.md) (sección «Cómo escribir guiones»):

   ```json
   {"guion_id": "estafa-banco-01", "categoria": "estafa", "autor": "aolivera0", "referencia": "llamada que recibió mi mamá, oct. 2026", "turnos": ["Buenas tardes, le hablo del área de seguridad de su banco.", "Para bloquear la compra necesito el código que le acaba de llegar."]}
   ```

   Meta: ~10 guiones por categoría y ~20 de `legitima`, con al menos un tercio de casos
   difíciles. Revisen el formato con `python validar.py`.

2. **Generar variaciones** (~5 por guion) con un modelo de lenguaje:

   ```bash
   python generar_variaciones.py --solo-prompts prompts/       # sin API: pegar en cualquier chat
   python generar_variaciones.py --importar prompts/ --fuente llm:gemini-web
   ```

   O, con una clave de API gratuita, `LLM_API_KEY=... python generar_variaciones.py`. Cada
   guion entra también como su propia conversación (`-v00`). **Hay que declararlo en el
   informe** (sección de uso de IA).

3. **Etiquetar a ciegas.** Cada uno genera su hoja y la llena en LibreOffice o Google
   Sheets, sin ver la categoría del guion:

   ```bash
   python exportar_etiquetado.py --anotador aolivera0 --parte 1/3 --comunes 120
   python exportar_etiquetado.py --anotador jpastranar --parte 2/3 --comunes 120
   python exportar_etiquetado.py --anotador dromeroo --parte 3/3 --comunes 120
   ```

   Las 120 comunes las etiquetan los tres (con ellas se calcula el kappa); el resto se
   reparte en tercios. Sin `--parte` y `--comunes`, cada uno etiqueta todo (doble
   etiquetado completo, si hay tiempo).

4. **Medir el acuerdo y armar las etiquetas finales:**

   ```bash
   python acuerdo.py
   ```

   Escribe `resultados/acuerdo.md` (kappa por par y desacuerdos más frecuentes) y
   `datos/desacuerdos.csv`. Los desacuerdos se discuten entre los tres y la decisión se
   anota en `datos/resoluciones.csv` (`id,etiqueta,razon`); luego se vuelve a correr.
   Si un desacuerdo se repite mucho, se aclara la regla en la guía.

5. **Partir por guion** y, cuando ya no vayan a cambiar los datos de prueba, **congelar**:

   ```bash
   python particionar.py            # 60/20/20 por categoría; los ya asignados no se mueven
   python particionar.py --congelar # desde aquí ningún guion nuevo entra a prueba
   ```

   Congelen después de generar las variaciones de todos los guiones de prueba: editar o
   agregar una conversación de prueba después de congelar bloquea la evaluación final.

6. **Evaluar** en validación, todas las veces que quieran:

   ```bash
   python evaluar.py
   python evaluar.py --transcripciones datos/transcripciones.jsonl   # texto que entendió Whisper
   python evaluar.py --predicciones kev_validacion.csv --nombre kev-4b
   ```

   Cada corrida queda en `resultados/<fecha>_validacion/` con `reporte.md`,
   `metricas.json` y las predicciones de cada modelo (para analizar errores).

7. **Prueba final, una sola vez,** con todo decidido:

   ```bash
   python evaluar.py --conjunto prueba --confirmo-prueba
   ```

   Entrena con entrenamiento + validación, verifica que la prueba congelada no cambió y
   deja constancia en `resultados/uso_prueba.log`.

## Qué mide `evaluar.py` y por qué

| Métrica | Por qué |
|---|---|
| **Legítimas mal marcadas** (IC Wilson 95 %) | La cifra principal. Marcar como estafa o spam la llamada del médico hace que el usuario la pierda; dejar pasar un spam solo le cuesta revisarlo. |
| **Estafas detectadas** (recall, IC Wilson 95 %) | El segundo error más caro. |
| **F1 macro** (IC bootstrap por guion) | Las clases están desbalanceadas y todas importan; la exactitud premia acertar las frecuentes. |
| **ECE** (error de calibración esperado) | Mostramos la confianza al usuario y elegimos umbrales con ella: si dice 90 %, debe acertar ~90 %. |
| F1 por clase | Para ver dónde falla cada modelo. |

Los intervalos importan porque los conjuntos son pequeños: con 18 legítimas en validación,
un solo error mueve la cifra 5,5 puntos. El bootstrap remuestrea guiones enteros, porque
las variaciones de un guion no son independientes.

## Líneas base (semanas 5 y 6)

| Modelo | Qué es |
|---|---|
| `mayoritaria` | Siempre la clase más frecuente. El piso absoluto. |
| `reglas` | Palabras clave escritas a mano, en el orden de la guía. Lo que haría alguien sin aprendizaje automático. |
| `naive_bayes` | Naïve Bayes multinomial sobre conteos de palabras y pares de palabras. |
| `regresion_logistica` | TF-IDF + regresión logística, con C elegido por validación cruzada agrupada por guion. **La que Kev tiene que superar.** |

Kev corre aparte (Colab o Kaggle, necesita GPU). Su cuaderno solo tiene que escribir un CSV
con `id`, `etiqueta` y `prob_<categoria>` para el conjunto de validación, y `evaluar.py
--predicciones` lo mide con exactamente las mismas métricas.

## Probar el flujo sin datos reales

```bash
python crear_ejemplo.py
python validar.py --datos datos/ejemplo
python acuerdo.py --datos datos/ejemplo --resultados datos/ejemplo/resultados
python particionar.py --datos datos/ejemplo --congelar
python evaluar.py --datos datos/ejemplo --resultados datos/ejemplo/resultados
```

Usa los 35 guiones de juguete del prototipo y dos anotadores simulados. Ahí las `reglas`
ganan por mucho, porque se escribieron con las mismas palabras que esos guiones: es justo
el sesgo que los datos reales (y los casos difíciles de la guía) tienen que evitar.

## Archivos

| Archivo | Qué hace |
|---|---|
| [`guia_etiquetado.md`](guia_etiquetado.md) | Definición de las 7 categorías, reglas de frontera y cómo escribir guiones |
| `validar.py` | Revisa el formato y cuenta guiones y conversaciones por categoría |
| `generar_variaciones.py` | Variaciones con un modelo de lenguaje (API o pegando a mano) |
| `exportar_etiquetado.py` | Hoja de etiquetado a ciegas por integrante |
| `acuerdo.py` | Kappa de Cohen, desacuerdos y etiquetas finales |
| `particionar.py` | Partición por guion, de solo agregar, con congelamiento de la prueba |
| `evaluar.py` | Entrena las líneas base y reporta las métricas con intervalos |
| `rita_clasificador/` | Código compartido: formato de datos, métricas y modelos |
| `crear_ejemplo.py` | Datos de ejemplo para probar el flujo |
